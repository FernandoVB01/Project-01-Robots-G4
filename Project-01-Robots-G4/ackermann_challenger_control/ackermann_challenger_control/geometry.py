"""Reference curve and rear-axle Pure Pursuit geometry, independent of ROS."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import atan, atan2, cos, hypot, pi, sin


WHEELBASE = 0.300
CURVATURE_LIMIT = 1.8
A = 2.7
B = 1.15
ALIGNMENT = atan2(2 * B, A)


def reference_point(u):
    """Rotate the Gerono curve so the start tangent faces Gazebo +X."""
    e, n = A * sin(u), B * sin(2 * u)
    return (e * cos(ALIGNMENT) + n * sin(ALIGNMENT),
            -e * sin(ALIGNMENT) + n * cos(ALIGNMENT))


def reference_curvature(u):
    dx, dy = A * cos(u), 2 * B * cos(2 * u)
    ddx, ddy = -A * sin(u), -4 * B * sin(2 * u)
    return (dx * ddy - dy * ddx) / hypot(dx, dy) ** 3


class Course:
    """One continuous lap, sampled at 720 intervals in the curve parameter."""

    def __init__(self):
        self.points = [reference_point(2 * pi * i / 720) for i in range(721)]
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
        # At the intersection, only the local branch is eligible.
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
