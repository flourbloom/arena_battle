from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='arena_battle', executable='keyboard_controller', output='screen'),
        Node(package='arena_battle', executable='game_logic', output='screen'),
    ])
