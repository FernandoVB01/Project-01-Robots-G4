from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


def generate_launch_description():
    share = Path(get_package_share_directory('ackermann_challenger_description'))
    urdf = xacro.process_file(str(share / 'urdf' / 'Ackermann_Challenger.xacro')).toxml()
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': ParameterValue(urdf, value_type=str)}],
        ),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui'),
        Node(package='rviz2', executable='rviz2',
             arguments=['-d', str(share / 'config' / 'display.rviz')]),
    ])
