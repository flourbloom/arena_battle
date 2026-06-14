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
    
    # Pygame visualizer for Player 1
    pygame_visualizer_p1 = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_visualizer_p1',
        parameters=[{'player_id': 1}],
        output='screen'
    )
    
    # Pygame visualizer for Player 2
    pygame_visualizer_p2 = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_visualizer_p2',
        parameters=[{'player_id': 2}],
        output='screen'
    )
    
    return LaunchDescription([
        game_logic,
        pygame_visualizer_p1,
        pygame_visualizer_p2,
    ])
