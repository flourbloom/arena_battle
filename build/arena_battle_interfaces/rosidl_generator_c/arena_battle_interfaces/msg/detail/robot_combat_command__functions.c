// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice
#include "arena_battle_interfaces/msg/detail/robot_combat_command__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
arena_battle_interfaces__msg__RobotCombatCommand__init(arena_battle_interfaces__msg__RobotCombatCommand * msg)
{
  if (!msg) {
    return false;
  }
  // linear_velocity
  // angular_velocity
  // shoot
  // shield
  // weapon_type
  return true;
}

void
arena_battle_interfaces__msg__RobotCombatCommand__fini(arena_battle_interfaces__msg__RobotCombatCommand * msg)
{
  if (!msg) {
    return;
  }
  // linear_velocity
  // angular_velocity
  // shoot
  // shield
  // weapon_type
}

bool
arena_battle_interfaces__msg__RobotCombatCommand__are_equal(const arena_battle_interfaces__msg__RobotCombatCommand * lhs, const arena_battle_interfaces__msg__RobotCombatCommand * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // linear_velocity
  if (lhs->linear_velocity != rhs->linear_velocity) {
    return false;
  }
  // angular_velocity
  if (lhs->angular_velocity != rhs->angular_velocity) {
    return false;
  }
  // shoot
  if (lhs->shoot != rhs->shoot) {
    return false;
  }
  // shield
  if (lhs->shield != rhs->shield) {
    return false;
  }
  // weapon_type
  if (lhs->weapon_type != rhs->weapon_type) {
    return false;
  }
  return true;
}

bool
arena_battle_interfaces__msg__RobotCombatCommand__copy(
  const arena_battle_interfaces__msg__RobotCombatCommand * input,
  arena_battle_interfaces__msg__RobotCombatCommand * output)
{
  if (!input || !output) {
    return false;
  }
  // linear_velocity
  output->linear_velocity = input->linear_velocity;
  // angular_velocity
  output->angular_velocity = input->angular_velocity;
  // shoot
  output->shoot = input->shoot;
  // shield
  output->shield = input->shield;
  // weapon_type
  output->weapon_type = input->weapon_type;
  return true;
}

arena_battle_interfaces__msg__RobotCombatCommand *
arena_battle_interfaces__msg__RobotCombatCommand__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arena_battle_interfaces__msg__RobotCombatCommand * msg = (arena_battle_interfaces__msg__RobotCombatCommand *)allocator.allocate(sizeof(arena_battle_interfaces__msg__RobotCombatCommand), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(arena_battle_interfaces__msg__RobotCombatCommand));
  bool success = arena_battle_interfaces__msg__RobotCombatCommand__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
arena_battle_interfaces__msg__RobotCombatCommand__destroy(arena_battle_interfaces__msg__RobotCombatCommand * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    arena_battle_interfaces__msg__RobotCombatCommand__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
arena_battle_interfaces__msg__RobotCombatCommand__Sequence__init(arena_battle_interfaces__msg__RobotCombatCommand__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arena_battle_interfaces__msg__RobotCombatCommand * data = NULL;

  if (size) {
    data = (arena_battle_interfaces__msg__RobotCombatCommand *)allocator.zero_allocate(size, sizeof(arena_battle_interfaces__msg__RobotCombatCommand), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = arena_battle_interfaces__msg__RobotCombatCommand__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        arena_battle_interfaces__msg__RobotCombatCommand__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
arena_battle_interfaces__msg__RobotCombatCommand__Sequence__fini(arena_battle_interfaces__msg__RobotCombatCommand__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      arena_battle_interfaces__msg__RobotCombatCommand__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

arena_battle_interfaces__msg__RobotCombatCommand__Sequence *
arena_battle_interfaces__msg__RobotCombatCommand__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arena_battle_interfaces__msg__RobotCombatCommand__Sequence * array = (arena_battle_interfaces__msg__RobotCombatCommand__Sequence *)allocator.allocate(sizeof(arena_battle_interfaces__msg__RobotCombatCommand__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = arena_battle_interfaces__msg__RobotCombatCommand__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
arena_battle_interfaces__msg__RobotCombatCommand__Sequence__destroy(arena_battle_interfaces__msg__RobotCombatCommand__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    arena_battle_interfaces__msg__RobotCombatCommand__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
arena_battle_interfaces__msg__RobotCombatCommand__Sequence__are_equal(const arena_battle_interfaces__msg__RobotCombatCommand__Sequence * lhs, const arena_battle_interfaces__msg__RobotCombatCommand__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!arena_battle_interfaces__msg__RobotCombatCommand__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
arena_battle_interfaces__msg__RobotCombatCommand__Sequence__copy(
  const arena_battle_interfaces__msg__RobotCombatCommand__Sequence * input,
  arena_battle_interfaces__msg__RobotCombatCommand__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(arena_battle_interfaces__msg__RobotCombatCommand);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    arena_battle_interfaces__msg__RobotCombatCommand * data =
      (arena_battle_interfaces__msg__RobotCombatCommand *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!arena_battle_interfaces__msg__RobotCombatCommand__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          arena_battle_interfaces__msg__RobotCombatCommand__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!arena_battle_interfaces__msg__RobotCombatCommand__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
