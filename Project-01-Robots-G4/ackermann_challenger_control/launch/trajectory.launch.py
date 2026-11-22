from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = Path(get_package_share_directory('ackermann_challenger_description'))
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('drive', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('speed', default_value='0.55'),
        DeclareLaunchArgument('lookahead', default_value='0.32'),
        DeclareLaunchArgument('start_delay', default_value='2.0'),
        DeclareLaunchArgument('output_dir', default_value='resultados'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(share / 'launch' / 'gazebo.launch.py')),
            launch_arguments={'gui': LaunchConfiguration('gui')}.items(),
        ),
        Node(
            condition=IfCondition(LaunchConfiguration('drive')),
            package='ackermann_challenger_control',
            executable='trajectory_tracker',
            parameters=[{
                'use_sim_time': True,
                'speed': ParameterValue(LaunchConfiguration('speed'), value_type=float),
                'lookahead': ParameterValue(LaunchConfiguration('lookahead'), value_type=float),
                'start_delay': ParameterValue(LaunchConfiguration('start_delay'), value_type=float),
                'output_dir': ParameterValue(LaunchConfiguration('output_dir'), value_type=str),
            }],
            output='screen',
        ),
    ])
