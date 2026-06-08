// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice

#ifndef ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__TRAITS_HPP_
#define ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "arena_battle_interfaces/msg/detail/robot_combat_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace arena_battle_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const RobotCombatCommand & msg,
  std::ostream & out)
{
  out << "{";
  // member: linear_velocity
  {
    out << "linear_velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.linear_velocity, out);
    out << ", ";
  }

  // member: angular_velocity
  {
    out << "angular_velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.angular_velocity, out);
    out << ", ";
  }

  // member: shoot
  {
    out << "shoot: ";
    rosidl_generator_traits::value_to_yaml(msg.shoot, out);
    out << ", ";
  }

  // member: shield
  {
    out << "shield: ";
    rosidl_generator_traits::value_to_yaml(msg.shield, out);
    out << ", ";
  }

  // member: weapon_type
  {
    out << "weapon_type: ";
    rosidl_generator_traits::value_to_yaml(msg.weapon_type, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RobotCombatCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: linear_velocity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "linear_velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.linear_velocity, out);
    out << "\n";
  }

  // member: angular_velocity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "angular_velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.angular_velocity, out);
    out << "\n";
  }

  // member: shoot
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "shoot: ";
    rosidl_generator_traits::value_to_yaml(msg.shoot, out);
    out << "\n";
  }

  // member: shield
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "shield: ";
    rosidl_generator_traits::value_to_yaml(msg.shield, out);
    out << "\n";
  }

  // member: weapon_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "weapon_type: ";
    rosidl_generator_traits::value_to_yaml(msg.weapon_type, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RobotCombatCommand & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace arena_battle_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use arena_battle_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const arena_battle_interfaces::msg::RobotCombatCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  arena_battle_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arena_battle_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const arena_battle_interfaces::msg::RobotCombatCommand & msg)
{
  return arena_battle_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<arena_battle_interfaces::msg::RobotCombatCommand>()
{
  return "arena_battle_interfaces::msg::RobotCombatCommand";
}

template<>
inline const char * name<arena_battle_interfaces::msg::RobotCombatCommand>()
{
  return "arena_battle_interfaces/msg/RobotCombatCommand";
}

template<>
struct has_fixed_size<arena_battle_interfaces::msg::RobotCombatCommand>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<arena_battle_interfaces::msg::RobotCombatCommand>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<arena_battle_interfaces::msg::RobotCombatCommand>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__TRAITS_HPP_
