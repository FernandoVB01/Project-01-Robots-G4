"""Track one closed course using Gazebo's rear-axle pose over the ROS bridge."""

import csv
import json
from math import atan2, hypot, isfinite, sqrt
from pathlib import Path as FilePath

from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry, Path
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile

from .geometry import CORNER_RADIUS, SIDE_LENGTH, Course, Motion, pursuit


class Tracker(Node):
    def __init__(self):
        super().__init__('trajectory_tracker')
        self.declare_parameter('speed', 0.55)
        self.declare_parameter('lookahead', 0.32)
        self.declare_parameter('start_delay', 2.0)
        self.declare_parameter('output_dir', 'results')
        self.speed = self.get_parameter('speed').value
        self.lookahead = self.get_parameter('lookahead').value
        self.start_delay = self.get_parameter('start_delay').value
        if not 0.1 <= self.speed <= 1.0 or not 0.12 <= self.lookahead <= 0.8:
            raise ValueError('speed must be 0.1–1.0 m/s and lookahead 0.12–0.8 m')
        if not isfinite(self.start_delay) or self.start_delay < 0:
            raise ValueError('start_delay must be finite and nonnegative')

        self.output = FilePath(self.get_parameter('output_dir').value).expanduser()
        self.output.mkdir(parents=True, exist_ok=True)
        self.log_file = (self.output / 'tracking.csv').open('w', newline='')
        self.log = csv.writer(self.log_file, lineterminator='\n')
        self.log.writerow(['time_s', 'x_m', 'y_m', 'yaw_rad', 'station_m',
                           'reference_x_m', 'reference_y_m', 'error_m', 'speed_mps',
                           'command_yaw_radps', 'command_steering_rad'])
        summary = self.output / 'summary.json'
        summary.unlink(missing_ok=True)

        self.course = Course()
        self.station = 0.0
        self.pose = None
        self.started_at = None
        self.ready_at = None
        self.last_sample = None
        self.sample_count = 0
        self.squared_error = 0.0
        self.maximum_error = 0.0
        self.terminal = False
        self.command = self.create_publisher(Twist, '/challenger/cmd_vel', 10)
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.reference = self.create_publisher(Path, '/challenger/reference_path', latched)
        self.create_subscription(Odometry, '/challenger/ground_truth', self.on_odometry, 10)
        self.create_timer(0.05, self.tick)
        self.get_logger().info('Waiting for Gazebo ground truth and simulation clock.')

    def on_odometry(self, message):
        point = message.pose.pose.position
        q = message.pose.pose.orientation
        yaw = atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        stamp = message.header.stamp
        if all(map(isfinite, (point.x, point.y, yaw))):
            self.pose = point.x, point.y, yaw, stamp.sec + stamp.nanosec * 1e-9

    def publish_reference(self):
        path = Path()
        path.header.frame_id = 'odom'
        path.header.stamp = self.get_clock().now().to_msg()
        for x, y in self.course.points:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self.reference.publish(path)

    def send(self, speed=0.0, yaw_rate=0.0):
        message = Twist()
        message.linear.x = float(speed)
        message.angular.z = float(yaw_rate)
        self.command.publish(message)

    def tick(self):
        if self.terminal or self.pose is None:
            self.send()
            return

        now = self.get_clock().now().nanoseconds * 1e-9
        x, y, yaw, stamp = self.pose
        if now <= 0 or abs(now - stamp) > 0.35:
            self.send()
            return
        if self.ready_at is None:
            self.ready_at = now + self.start_delay
            self.publish_reference()
        if now < self.ready_at or stamp == self.last_sample:
            return
        if self.started_at is None:
            self.started_at = stamp
            self.get_logger().info('Tracking one rounded-hexagon lap.')
        self.last_sample = stamp

        error, station, rx, ry = self.course.project(x, y, self.station)
        self.station = max(self.station, station)
        remaining = self.course.length - self.station
        endpoint_error = hypot(x, y)
        elapsed = stamp - self.started_at
        if error > 0.65:
            state = 'off_course'
        elif remaining <= 0.07 and endpoint_error <= 0.09:
            state = 'completed'
        elif elapsed > 2 * self.course.length / self.speed + 10:
            state = 'timeout'
        else:
            state = 'tracking'

        if state == 'tracking':
            speed = min(self.speed, max(0.12, 1.2 * remaining))
            target = self.course.point_at(self.station + self.lookahead)
            motion = pursuit(x, y, yaw, target, speed)
        else:
            motion = Motion(0.0, 0.0, 0.0)
        self.send(motion.speed, motion.yaw_rate)
        self.log.writerow([elapsed, x, y, yaw, self.station, rx, ry, error,
                           motion.speed, motion.yaw_rate, motion.steering])
        self.sample_count += 1
        self.squared_error += error ** 2
        self.maximum_error = max(self.maximum_error, error)
        if state != 'tracking':
            self.finish(state, elapsed, endpoint_error)

    def finish(self, state, elapsed, endpoint_error):
        self.terminal = True
        self.log_file.close()
        summary = {
            'course': 'rounded_hexagon',
            'nominal_side_length_m': SIDE_LENGTH,
            'corner_radius_m': CORNER_RADIUS,
            'status': state,
            'simulated_duration_s': elapsed,
            'reference_length_m': self.course.length,
            'station_m': self.station,
            'samples': self.sample_count,
            'rmse_m': sqrt(self.squared_error / self.sample_count),
            'max_error_m': self.maximum_error,
            'endpoint_error_m': endpoint_error,
            'speed_mps': self.speed,
            'lookahead_m': self.lookahead,
        }
        temporary = self.output / 'summary.json.tmp'
        temporary.write_text(json.dumps(summary, indent=2) + '\n')
        temporary.replace(self.output / 'summary.json')
        self.get_logger().info(f'{state}: RMSE {summary["rmse_m"]:.3f} m. Results in {self.output}.')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = Tracker()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            if rclpy.ok():
                node.send()
            node.log_file.close()
            node.destroy_node()
        rclpy.try_shutdown()
