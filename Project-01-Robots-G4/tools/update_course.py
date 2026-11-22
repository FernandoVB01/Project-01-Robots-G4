#!/usr/bin/env python3
"""Regenerate the visual centerline in the Gazebo world from the ROS reference."""

from math import atan2, hypot
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ackermann_challenger_control'))
from ackermann_challenger_control.geometry import Course  # noqa: E402


def main():
    world = ROOT / 'ackermann_challenger_description/worlds/challenger_course.sdf'
    before, remainder = world.read_text().split('      <!-- BEGIN GENERATED CENTERLINE -->\n')
    _, after = remainder.split('      <!-- END GENERATED CENTERLINE -->\n')
    course = Course()
    marks = []
    intervals = 112
    for i in range(intervals):
        x0, y0 = course.point_at(i * course.length / intervals)
        x1, y1 = course.point_at((i + 1) * course.length / intervals)
        length = hypot(x1 - x0, y1 - y0)
        marks.append(
            f'      <visual name="segment_{i:03d}">\n'
            f'        <pose>{(x0 + x1) / 2:.5f} {(y0 + y1) / 2:.5f} 0.001 '
            f'0 0 {atan2(y1 - y0, x1 - x0):.5f}</pose>\n'
            f'        <geometry><box><size>{length + 0.008:.5f} 0.032 0.001</size></box></geometry>\n'
            '        <material><ambient>0.03 0.39 0.40 1</ambient>'
            '<diffuse>0.03 0.48 0.50 1</diffuse></material>\n'
            '        <cast_shadows>false</cast_shadows>\n'
            '      </visual>\n'
        )
    world.write_text(before + '      <!-- BEGIN GENERATED CENTERLINE -->\n'
                     + ''.join(marks) + '      <!-- END GENERATED CENTERLINE -->\n' + after)


if __name__ == '__main__':
    main()
