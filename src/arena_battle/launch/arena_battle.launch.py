import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Get package share directory
    pkg_share = get_package_share_directory('arena_battle')
    
    # Path to URDF file
    urdf_file = os.path.join(pkg_share, 'urdf', 'arena_robot.urdf')
    
    # Read URDF file
    with open(urdf_file, 'r') as file:
        robot_description = file.read()
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }]
    )
    
    # Joint state publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{
            'use_sim_time': False,
            'rate': 50
        }]
    )
    
    # Game logic node
    game_logic = Node(
        package='arena_battle',
        executable='game_logic',
        name='game_logic',
        output='screen'
    )
    
    # RViz2 node with config
    rviz_config = os.path.join(pkg_share, 'rviz', 'arena_battle.rviz')
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )
    
    # TF broadcaster for robot pose
    robot_pose_tf = Node(
        package='arena_battle',
        executable='robot_pose_tf',
        name='robot_pose_tf',
        output='screen'
    )
    
    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        robot_pose_tf,
        game_logic,
        # Delay RViz start to ensure TF tree is ready
        TimerAction(
            period=2.0,
            actions=[rviz2]
        ),
    ])
