// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "arena_battle_interfaces/msg/detail/robot_combat_command__rosidl_typesupport_introspection_c.h"
#include "arena_battle_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "arena_battle_interfaces/msg/detail/robot_combat_command__functions.h"
#include "arena_battle_interfaces/msg/detail/robot_combat_command__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  arena_battle_interfaces__msg__RobotCombatCommand__init(message_memory);
}

void arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_fini_function(void * message_memory)
{
  arena_battle_interfaces__msg__RobotCombatCommand__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_member_array[5] = {
  {
    "linear_velocity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arena_battle_interfaces__msg__RobotCombatCommand, linear_velocity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "angular_velocity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arena_battle_interfaces__msg__RobotCombatCommand, angular_velocity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "shoot",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arena_battle_interfaces__msg__RobotCombatCommand, shoot),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "shield",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arena_battle_interfaces__msg__RobotCombatCommand, shield),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "weapon_type",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arena_battle_interfaces__msg__RobotCombatCommand, weapon_type),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_members = {
  "arena_battle_interfaces__msg",  // message namespace
  "RobotCombatCommand",  // message name
  5,  // number of fields
  sizeof(arena_battle_interfaces__msg__RobotCombatCommand),
  arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_member_array,  // message members
  arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_init_function,  // function to initialize message memory (memory has to be allocated)
  arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_type_support_handle = {
  0,
  &arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_arena_battle_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arena_battle_interfaces, msg, RobotCombatCommand)() {
  if (!arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_type_support_handle.typesupport_identifier) {
    arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &arena_battle_interfaces__msg__RobotCombatCommand__rosidl_typesupport_introspection_c__RobotCombatCommand_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
