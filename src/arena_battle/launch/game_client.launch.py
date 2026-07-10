from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Keep the same domain as the server launch file so they can see each other
    domain_id = SetEnvironmentVariable('ROS_DOMAIN_ID', '67')
    
    # Declare the namespace argument
    ns_arg = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace for the pygame client (e.g. p1, p2)'
    )
    ns = LaunchConfiguration('namespace')

    # Pygame visualizer (which starts in Main Menu mode)
    client = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_node',
        namespace=ns,
        output='screen'
    )

    return LaunchDescription([
        domain_id,
        ns_arg,
        client,
    ])
