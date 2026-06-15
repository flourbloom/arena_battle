from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable

def generate_launch_description():
    # Hardcode domain ID
    set_domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '67')

    # Pygame visualizer for Player 1
    pygame_visualizer_p1 = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_visualizer_p1',
        parameters=[{'player_id': 1}],
        output='screen'
    )
    
    return LaunchDescription([
        set_domain_id,
        pygame_visualizer_p1,
    ])
