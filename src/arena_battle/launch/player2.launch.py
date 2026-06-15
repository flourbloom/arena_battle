from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable

def generate_launch_description():
    # Hardcode domain ID
    set_domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '67')

    # Pygame visualizer for Player 2
    pygame_visualizer_p2 = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_visualizer_p2',
        parameters=[{'player_id': 2}],
        output='screen'
    )
    
    return LaunchDescription([
        set_domain_id,
        pygame_visualizer_p2,
    ])
