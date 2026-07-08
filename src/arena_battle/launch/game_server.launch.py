from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    # Keep the same domain as the client launch file so they can see each other
    domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '67')

    # Game Logic Server (headless physics/match master)
    server = Node(
        package='arena_battle',
        executable='game_logic',
        name='game_server',
        output='screen'
    )

    return LaunchDescription([
        domain_id,
        server,
    ])
