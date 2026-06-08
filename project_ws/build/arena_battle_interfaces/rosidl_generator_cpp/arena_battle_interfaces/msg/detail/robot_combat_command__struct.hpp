// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice

#ifndef ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__STRUCT_HPP_
#define ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__arena_battle_interfaces__msg__RobotCombatCommand __attribute__((deprecated))
#else
# define DEPRECATED__arena_battle_interfaces__msg__RobotCombatCommand __declspec(deprecated)
#endif

namespace arena_battle_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RobotCombatCommand_
{
  using Type = RobotCombatCommand_<ContainerAllocator>;

  explicit RobotCombatCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->linear_velocity = 0.0f;
      this->angular_velocity = 0.0f;
      this->shoot = false;
      this->shield = false;
      this->weapon_type = 0;
    }
  }

  explicit RobotCombatCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->linear_velocity = 0.0f;
      this->angular_velocity = 0.0f;
      this->shoot = false;
      this->shield = false;
      this->weapon_type = 0;
    }
  }

  // field types and members
  using _linear_velocity_type =
    float;
  _linear_velocity_type linear_velocity;
  using _angular_velocity_type =
    float;
  _angular_velocity_type angular_velocity;
  using _shoot_type =
    bool;
  _shoot_type shoot;
  using _shield_type =
    bool;
  _shield_type shield;
  using _weapon_type_type =
    uint8_t;
  _weapon_type_type weapon_type;

  // setters for named parameter idiom
  Type & set__linear_velocity(
    const float & _arg)
  {
    this->linear_velocity = _arg;
    return *this;
  }
  Type & set__angular_velocity(
    const float & _arg)
  {
    this->angular_velocity = _arg;
    return *this;
  }
  Type & set__shoot(
    const bool & _arg)
  {
    this->shoot = _arg;
    return *this;
  }
  Type & set__shield(
    const bool & _arg)
  {
    this->shield = _arg;
    return *this;
  }
  Type & set__weapon_type(
    const uint8_t & _arg)
  {
    this->weapon_type = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arena_battle_interfaces__msg__RobotCombatCommand
    std::shared_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arena_battle_interfaces__msg__RobotCombatCommand
    std::shared_ptr<arena_battle_interfaces::msg::RobotCombatCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RobotCombatCommand_ & other) const
  {
    if (this->linear_velocity != other.linear_velocity) {
      return false;
    }
    if (this->angular_velocity != other.angular_velocity) {
      return false;
    }
    if (this->shoot != other.shoot) {
      return false;
    }
    if (this->shield != other.shield) {
      return false;
    }
    if (this->weapon_type != other.weapon_type) {
      return false;
    }
    return true;
  }
  bool operator!=(const RobotCombatCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RobotCombatCommand_

// alias to use template instance with default allocator
using RobotCombatCommand =
  arena_battle_interfaces::msg::RobotCombatCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace arena_battle_interfaces

#endif  // ARENA_BATTLE_INTERFACES__MSG__DETAIL__ROBOT_COMBAT_COMMAND__STRUCT_HPP_
