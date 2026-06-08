// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice

#ifndef ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__BUILDER_HPP_
#define ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "arena_battle_interfaces/msg/detail/robot_combat_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace arena_battle_interfaces
{

namespace msg
{

namespace builder
{

class Init_RobotCombatCommand_weapon_type
{
public:
  explicit Init_RobotCombatCommand_weapon_type(::arena_battle_interfaces::msg::RobotCombatCommand & msg)
  : msg_(msg)
  {}
  ::arena_battle_interfaces::msg::RobotCombatCommand weapon_type(::arena_battle_interfaces::msg::RobotCombatCommand::_weapon_type_type arg)
  {
    msg_.weapon_type = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arena_battle_interfaces::msg::RobotCombatCommand msg_;
};

class Init_RobotCombatCommand_shield
{
public:
  explicit Init_RobotCombatCommand_shield(::arena_battle_interfaces::msg::RobotCombatCommand & msg)
  : msg_(msg)
  {}
  Init_RobotCombatCommand_weapon_type shield(::arena_battle_interfaces::msg::RobotCombatCommand::_shield_type arg)
  {
    msg_.shield = std::move(arg);
    return Init_RobotCombatCommand_weapon_type(msg_);
  }

private:
  ::arena_battle_interfaces::msg::RobotCombatCommand msg_;
};

class Init_RobotCombatCommand_shoot
{
public:
  explicit Init_RobotCombatCommand_shoot(::arena_battle_interfaces::msg::RobotCombatCommand & msg)
  : msg_(msg)
  {}
  Init_RobotCombatCommand_shield shoot(::arena_battle_interfaces::msg::RobotCombatCommand::_shoot_type arg)
  {
    msg_.shoot = std::move(arg);
    return Init_RobotCombatCommand_shield(msg_);
  }

private:
  ::arena_battle_interfaces::msg::RobotCombatCommand msg_;
};

class Init_RobotCombatCommand_angular_velocity
{
public:
  explicit Init_RobotCombatCommand_angular_velocity(::arena_battle_interfaces::msg::RobotCombatCommand & msg)
  : msg_(msg)
  {}
  Init_RobotCombatCommand_shoot angular_velocity(::arena_battle_interfaces::msg::RobotCombatCommand::_angular_velocity_type arg)
  {
    msg_.angular_velocity = std::move(arg);
    return Init_RobotCombatCommand_shoot(msg_);
  }

private:
  ::arena_battle_interfaces::msg::RobotCombatCommand msg_;
};

class Init_RobotCombatCommand_linear_velocity
{
public:
  Init_RobotCombatCommand_linear_velocity()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RobotCombatCommand_angular_velocity linear_velocity(::arena_battle_interfaces::msg::RobotCombatCommand::_linear_velocity_type arg)
  {
    msg_.linear_velocity = std::move(arg);
    return Init_RobotCombatCommand_angular_velocity(msg_);
  }

private:
  ::arena_battle_interfaces::msg::RobotCombatCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::arena_battle_interfaces::msg::RobotCombatCommand>()
{
  return arena_battle_interfaces::msg::builder::Init_RobotCombatCommand_linear_velocity();
}

}  // namespace arena_battle_interfaces

#endif  // ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__BUILDER_HPP_
