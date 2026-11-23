"""Reference curve and rear-axle Pure Pursuit geometry, independent of ROS."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import atan, ceil, cos, hypot, pi, sin, tan


WHEELBASE = 0.300
CURVATURE_LIMIT = 1.8
SIDE_LENGTH = 2.55
CORNER_RADIUS = 0.95
CORNER_ANGLE = pi / 3
STRAIGHT_LENGTH = SIDE_LENGTH - 2 * CORNER_RADIUS * tan(CORNER_ANGLE / 2)
SAMPLE_SPACING = 0.02


def _append_straight(points, heading, length):
    x, y = points[-1]
    count = ceil(length / SAMPLE_SPACING)
    for index in range(1, count + 1):
        distance = length * index / count
        points.append((x + distance * cos(heading), y + distance * sin(heading)))


def _append_corner(points, heading):
    x, y = points[-1]
    count = ceil(CORNER_RADIUS * CORNER_ANGLE / SAMPLE_SPACING)
    for index in range(1, count + 1):
        angle = heading + CORNER_ANGLE * index / count
        points.append((
            x + CORNER_RADIUS * (sin(angle) - sin(heading)),
            y + CORNER_RADIUS * (cos(heading) - cos(angle)),
        ))


class Course:
    """A rounded hexagon with tangent straight-to-arc joins."""

    def __init__(self):
        # The start splits the first side. Its tangent matches Gazebo's +X axis.
        self.points = [(0.0, 0.0)]
        _append_straight(self.points, 0.0, STRAIGHT_LENGTH / 2)
        for corner in range(6):
            _append_corner(self.points, corner * CORNER_ANGLE)
            length = STRAIGHT_LENGTH / 2 if corner == 5 else STRAIGHT_LENGTH
            _append_straight(self.points, (corner + 1) * CORNER_ANGLE, length)
        self.points[-1] = self.points[0]
        self.stations = [0.0]
        for (x0, y0), (x1, y1) in zip(self.points, self.points[1:]):
            self.stations.append(self.stations[-1] + hypot(x1 - x0, y1 - y0))
        self.length = self.stations[-1]

    def point_at(self, station):
        station = min(self.length, max(0.0, station))
        segment = min(len(self.points) - 2, bisect_right(self.stations, station) - 1)
        x0, y0 = self.points[segment]
        x1, y1 = self.points[segment + 1]
        fraction = ((station - self.stations[segment])
                    / (self.stations[segment + 1] - self.stations[segment]))
        return x0 + fraction * (x1 - x0), y0 + fraction * (y1 - y0)

    def project(self, x, y, previous):
        # Keep the projection on the active portion even at the shared endpoint.
        lower = max(0.0, previous - 0.12)
        upper = min(self.length, previous + 0.45)
        first = bisect_right(self.stations, lower) - 1
        last = bisect_left(self.stations, upper)
        best = (float('inf'), previous, 0.0, 0.0)
        for i in range(first, last):
            start = self.stations[i]
            length = self.stations[i + 1] - start
            x0, y0 = self.points[i]
            x1, y1 = self.points[i + 1]
            dx, dy = x1 - x0, y1 - y0
            projected = start + ((x - x0) * dx + (y - y0) * dy) / length
            station = min(start + length, upper, max(start, lower, projected))
            fraction = (station - start) / length
            rx, ry = x0 + fraction * dx, y0 + fraction * dy
            error = hypot(x - rx, y - ry)
            if error < best[0]:
                best = (error, station, rx, ry)
        return best


@dataclass(frozen=True)
class Motion:
    speed: float
    yaw_rate: float
    steering: float


def pursuit(x, y, yaw, target, desired_speed):
    dx, dy = target[0] - x, target[1] - y
    distance_squared = dx * dx + dy * dy
    if distance_squared < 1e-8:
        return Motion(0.0, 0.0, 0.0)
    lateral = -sin(yaw) * dx + cos(yaw) * dy
    curvature = max(-CURVATURE_LIMIT, min(CURVATURE_LIMIT, 2 * lateral / distance_squared))
    return Motion(desired_speed, desired_speed * curvature, atan(WHEELBASE * curvature))
