from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    # Keep the same domain as the server launch file so they can see each other
    domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '67')

    # Pygame visualizer (which starts in Main Menu mode)
    client = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_node',
        namespace='p1',
        output='screen'
    )

    return LaunchDescription([
        domain_id,
        client,
    ])
