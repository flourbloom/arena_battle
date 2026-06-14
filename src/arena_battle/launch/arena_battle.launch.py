import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Declare visualizer launch argument
    visualizer_arg = DeclareLaunchArgument(
        'visualizer',
        default_value='pygame',
        description='Visualization to use: pygame or rviz'
    )
    
    visualizer = LaunchConfiguration('visualizer')
    
    # Get package share directory
    pkg_share = get_package_share_directory('arena_battle')
    
    # Path to URDF file
    urdf_file = os.path.join(pkg_share, 'urdf', 'arena_robot.urdf')
    
    # Read URDF file
    with open(urdf_file, 'r') as file:
        robot_description = file.read()
    
    # Robot state publisher (only for RViz)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }],
        condition=IfCondition(PythonExpression(["'", visualizer, "' == 'rviz'"]))
    )
    
    # Joint state publisher (only for RViz)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{
            'use_sim_time': False,
            'rate': 50
        }],
        condition=IfCondition(PythonExpression(["'", visualizer, "' == 'rviz'"]))
    )
    
    # Game logic node (always runs)
    game_logic = Node(
        package='arena_battle',
        executable='game_logic',
        name='game_logic',
        output='screen'
    )
    
    # RViz2 node with config (only for RViz)
    rviz_config = os.path.join(pkg_share, 'rviz', 'arena_battle.rviz')
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        condition=IfCondition(PythonExpression(["'", visualizer, "' == 'rviz'"]))
    )
    
    # TF broadcaster for robot pose (only for RViz)
    robot_pose_tf = Node(
        package='arena_battle',
        executable='robot_pose_tf',
        name='robot_pose_tf',
        output='screen',
        condition=IfCondition(PythonExpression(["'", visualizer, "' == 'rviz'"]))
    )
    
    # Pygame visualizer node (only for Pygame)
    pygame_visualizer = Node(
        package='arena_battle',
        executable='pygame_visualizer',
        name='pygame_visualizer',
        output='screen',
        condition=IfCondition(PythonExpression(["'", visualizer, "' == 'pygame'"]))
    )
    
    return LaunchDescription([
        visualizer_arg,
        robot_state_publisher,
        joint_state_publisher,
        robot_pose_tf,
        game_logic,
        pygame_visualizer,
        # Delay RViz start to ensure TF tree is ready (only active if visualizer is rviz)
        TimerAction(
            period=2.0,
            actions=[rviz2]
        ),
    ])
