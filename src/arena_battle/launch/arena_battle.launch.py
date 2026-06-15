from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Pygame visualizer (which starts in Main Menu mode)
    client = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_visualizer',
        output='screen'
    )
    
    return LaunchDescription([
        client,
    ])
