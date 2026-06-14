cmake_minimum_required(VERSION 3.8)
project(arena_battle_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotCombatCommand.msg"
  "msg/Projectile.msg"
  "msg/RobotState.msg"
  "msg/GameState.msg"
)

ament_package()
