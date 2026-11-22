from pathlib import Path
from shlex import quote

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


def generate_launch_description():
    share = Path(get_package_share_directory('ackermann_challenger_description'))
    gazebo_share = Path(get_package_share_directory('ros_gz_sim'))
    urdf = xacro.process_file(str(share / 'urdf' / 'Ackermann_Challenger.xacro')).toxml()

    world = quote(str(share / 'worlds' / 'challenger_course.sdf'))
    gz_args = PythonExpression([
        repr(f'-r -v 3 {world}'), " + (' -s' if '",
        LaunchConfiguration('gui'), "'.lower() == 'false' else '')",
    ])

    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true', choices=['true', 'false']),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(gazebo_share / 'launch' / 'gz_sim.launch.py')),
            launch_arguments={'gz_args': gz_args, 'on_exit_shutdown': 'true'}.items(),
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': ParameterValue(urdf, value_type=str),
                         'use_sim_time': True}],
            output='screen',
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-world', 'challenger_course', '-name', 'challenger',
                       '-topic', '/robot_description', '-x', '0.150', '-z', '0.003'],
            output='screen',
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            parameters=[{'config_file': str(share / 'config' / 'bridge.yaml')}],
            output='screen',
        ),
    ])
