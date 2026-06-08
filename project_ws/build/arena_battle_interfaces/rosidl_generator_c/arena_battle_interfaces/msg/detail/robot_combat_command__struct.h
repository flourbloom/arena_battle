// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice

#ifndef ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__STRUCT_H_
#define ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/RobotCombatCommand in the package arena_battle_interfaces.
typedef struct arena_battle_interfaces__msg__RobotCombatCommand
{
  float linear_velocity;
  float angular_velocity;
  bool shoot;
  bool shield;
  uint8_t weapon_type;
} arena_battle_interfaces__msg__RobotCombatCommand;

// Struct for a sequence of arena_battle_interfaces__msg__RobotCombatCommand.
typedef struct arena_battle_interfaces__msg__RobotCombatCommand__Sequence
{
  arena_battle_interfaces__msg__RobotCombatCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arena_battle_interfaces__msg__RobotCombatCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__STRUCT_H_
