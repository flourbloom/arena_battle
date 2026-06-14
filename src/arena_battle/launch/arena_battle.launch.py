from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Game logic node (Model/State node)
    game_logic = Node(
        package='arena_battle',
        executable='game_logic',
        name='game_logic',
        output='screen'
    )
    
    # Pygame visualizer node (View/Controller node)
    pygame_visualizer = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_visualizer',
        output='screen'
    )
    
    return LaunchDescription([
        game_logic,
        pygame_visualizer,
    ])
