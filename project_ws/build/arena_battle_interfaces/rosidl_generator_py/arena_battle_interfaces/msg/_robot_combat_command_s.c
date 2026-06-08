// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from arena_battle_interfaces:msg/RobotCombatCommand.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "arena_battle_interfaces/msg/detail/robot_combat_command__struct.h"
#include "arena_battle_interfaces/msg/detail/robot_combat_command__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool arena_battle_interfaces__msg__robot_combat_command__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[69];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("arena_battle_interfaces.msg._robot_combat_command.RobotCombatCommand", full_classname_dest, 68) == 0);
  }
  arena_battle_interfaces__msg__RobotCombatCommand * ros_message = _ros_message;
  {  // linear_velocity
    PyObject * field = PyObject_GetAttrString(_pymsg, "linear_velocity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->linear_velocity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // angular_velocity
    PyObject * field = PyObject_GetAttrString(_pymsg, "angular_velocity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->angular_velocity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // shoot
    PyObject * field = PyObject_GetAttrString(_pymsg, "shoot");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->shoot = (Py_True == field);
    Py_DECREF(field);
  }
  {  // shield
    PyObject * field = PyObject_GetAttrString(_pymsg, "shield");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->shield = (Py_True == field);
    Py_DECREF(field);
  }
  {  // weapon_type
    PyObject * field = PyObject_GetAttrString(_pymsg, "weapon_type");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->weapon_type = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * arena_battle_interfaces__msg__robot_combat_command__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of RobotCombatCommand */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("arena_battle_interfaces.msg._robot_combat_command");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "RobotCombatCommand");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  arena_battle_interfaces__msg__RobotCombatCommand * ros_message = (arena_battle_interfaces__msg__RobotCombatCommand *)raw_ros_message;
  {  // linear_velocity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->linear_velocity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "linear_velocity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // angular_velocity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->angular_velocity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "angular_velocity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // shoot
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->shoot ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "shoot", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // shield
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->shield ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "shield", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // weapon_type
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->weapon_type);
    {
      int rc = PyObject_SetAttrString(_pymessage, "weapon_type", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
