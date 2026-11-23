# Group 4 presentation script

**Target duration** 4:45. Keep the assigned speaker on camera while sharing the corresponding slide. Show all three teammates together at the opening and closing. Play about 8 seconds of the Gazebo clip on slide 7.

| Time | Slide | Speaker |
|---|---:|---|
| 0:00–0:20 | 1 | Julian, with everyone on camera |
| 0:20–0:42 | 2 | Julian |
| 0:42–1:10 | 3 | David |
| 1:10–1:35 | 4 | David |
| 1:35–2:00 | 5 | Julian |
| 2:00–2:40 | 6 | Luis |
| 2:40–3:24 | 7 | Luis |
| 3:24–3:50 | 8 | David |
| 3:50–4:13 | 9 | David |
| 4:13–4:45 | 10 | Luis, with everyone on camera for the closing |

## 1 · Introduction

We are David Acosta Lara, Julian Gonzales Chamaidan, and Luis Velez Burgos from Group 4. We designed an Ackermann mobile robot and tested it on a closed course with straight segments and circular turns.

## 2 · Workflow

We started with the Fusion 360 assembly, exported the model and meshes, and brought the URDF/Xacro into Gazebo Harmonic. In ROS 2 Jazzy, a Pure Pursuit node reads the rear-axle pose and controls the robot through a velocity command.

## 3 · Kinematic models

A differential-drive robot can turn in place. A skid-steer robot can pivot, but its fixed wheels scrub in bends. Omnidirectional wheels offer lateral motion, while their rollers are more sensitive to surface conditions. A tricycle needs one steering joint and has a smaller support polygon. Ackermann steering suits routes with room for rolling turns.

## 4 · Mathematical model

We locate the pose at the midpoint of the rear axle. The yaw rate equals speed times curvature, and curvature is the tangent of the virtual steering angle divided by the wheelbase. In a left turn the inner front wheel steers more, while the outer rear wheel travels faster.

## 5 · Design parameters

The wheelbase is 300 millimeters. The track is 190 millimeters, and the front pivots are 120 millimeters apart. The wheels have a 35-millimeter radius. The steering joint limit is 35 degrees, giving a geometric minimum turning radius of 0.488 meters.

## 6 · Rounded-hexagon trajectory and controller

The reference is a 14.69-meter rounded hexagon. It has six straights and six circular arcs. Every arc turns 60 degrees at a radius of 0.95 meters and joins its straight sections tangentially. Pure Pursuit selects a point 0.32 meters ahead on the reference. The controller updates at 20 hertz and slows for the final stop.

## 7 · Simulation results

The robot completed the course in 27.50 seconds of simulation time. RMS path error was 2.0 millimeters, maximum error was 5.6 millimeters, and the stop command came 6.60 centimeters from the endpoint. The dashed reference and measured pose are shown together.

Play a short segment that shows the robot leaving a straight and entering a circular corner.

## 8 · Campus delivery

We propose using Ackermann steering for campus delivery between buildings. Long paved segments and wide bends let the robot move forward continuously. The route needs enough room for the minimum turning radius, especially near the delivery point.

## 9 · Limitations

A small steering offset can accumulate as heading drift. We propose calibrating the steering and comparing encoder odometry and IMU readings. The current simulation uses Gazebo's pose estimate, so a physical test would reveal the effects of slip and sensor error.

## 10 · Conclusion

The robot completed the six straight sections and six rounded turns and then stopped near its start. A future trial can compare curvature-continuous transitions and use encoder and IMU feedback. Thank you.
