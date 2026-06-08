// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice
#include "arena_battle_interfaces/msg/detail/robot_combat_command__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "arena_battle_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "arena_battle_interfaces/msg/detail/robot_combat_command__struct.h"
#include "arena_battle_interfaces/msg/detail/robot_combat_command__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _RobotCombatCommand__ros_msg_type = arena_battle_interfaces__msg__RobotCombatCommand;

static bool _RobotCombatCommand__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _RobotCombatCommand__ros_msg_type * ros_message = static_cast<const _RobotCombatCommand__ros_msg_type *>(untyped_ros_message);
  // Field name: linear_velocity
  {
    cdr << ros_message->linear_velocity;
  }

  // Field name: angular_velocity
  {
    cdr << ros_message->angular_velocity;
  }

  // Field name: shoot
  {
    cdr << (ros_message->shoot ? true : false);
  }

  // Field name: shield
  {
    cdr << (ros_message->shield ? true : false);
  }

  // Field name: weapon_type
  {
    cdr << ros_message->weapon_type;
  }

  return true;
}

static bool _RobotCombatCommand__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _RobotCombatCommand__ros_msg_type * ros_message = static_cast<_RobotCombatCommand__ros_msg_type *>(untyped_ros_message);
  // Field name: linear_velocity
  {
    cdr >> ros_message->linear_velocity;
  }

  // Field name: angular_velocity
  {
    cdr >> ros_message->angular_velocity;
  }

  // Field name: shoot
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->shoot = tmp ? true : false;
  }

  // Field name: shield
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->shield = tmp ? true : false;
  }

  // Field name: weapon_type
  {
    cdr >> ros_message->weapon_type;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_arena_battle_interfaces
size_t get_serialized_size_arena_battle_interfaces__msg__RobotCombatCommand(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _RobotCombatCommand__ros_msg_type * ros_message = static_cast<const _RobotCombatCommand__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name linear_velocity
  {
    size_t item_size = sizeof(ros_message->linear_velocity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name angular_velocity
  {
    size_t item_size = sizeof(ros_message->angular_velocity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name shoot
  {
    size_t item_size = sizeof(ros_message->shoot);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name shield
  {
    size_t item_size = sizeof(ros_message->shield);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name weapon_type
  {
    size_t item_size = sizeof(ros_message->weapon_type);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _RobotCombatCommand__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_arena_battle_interfaces__msg__RobotCombatCommand(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_arena_battle_interfaces
size_t max_serialized_size_arena_battle_interfaces__msg__RobotCombatCommand(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: linear_velocity
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: angular_velocity
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: shoot
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: shield
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: weapon_type
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = arena_battle_interfaces__msg__RobotCombatCommand;
    is_plain =
      (
      offsetof(DataType, weapon_type) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _RobotCombatCommand__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_arena_battle_interfaces__msg__RobotCombatCommand(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_RobotCombatCommand = {
  "arena_battle_interfaces::msg",
  "RobotCombatCommand",
  _RobotCombatCommand__cdr_serialize,
  _RobotCombatCommand__cdr_deserialize,
  _RobotCombatCommand__get_serialized_size,
  _RobotCombatCommand__max_serialized_size
};

static rosidl_message_type_support_t _RobotCombatCommand__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_RobotCombatCommand,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, arena_battle_interfaces, msg, RobotCombatCommand)() {
  return &_RobotCombatCommand__type_support;
}

#if defined(__cplusplus)
}
#endif
