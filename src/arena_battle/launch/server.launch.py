from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable

def generate_launch_description():
    # Hardcode domain ID
    set_domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '67')

    # Game logic node (Model/State node)
    game_logic = Node(
        package='arena_battle',
        executable='game_logic',
        name='game_logic',
        output='screen'
    )
    
    return LaunchDescription([
        set_domain_id,
        game_logic,
    ])
