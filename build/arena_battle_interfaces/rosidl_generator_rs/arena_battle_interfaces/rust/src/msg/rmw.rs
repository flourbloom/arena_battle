#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "arena_battle_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__arena_battle_interfaces__msg__RobotCombatCommand() -> *const std::ffi::c_void;
}

#[link(name = "arena_battle_interfaces__rosidl_generator_c")]
extern "C" {
    fn arena_battle_interfaces__msg__RobotCombatCommand__init(msg: *mut RobotCombatCommand) -> bool;
    fn arena_battle_interfaces__msg__RobotCombatCommand__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RobotCombatCommand>, size: usize) -> bool;
    fn arena_battle_interfaces__msg__RobotCombatCommand__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RobotCombatCommand>);
    fn arena_battle_interfaces__msg__RobotCombatCommand__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RobotCombatCommand>, out_seq: *mut rosidl_runtime_rs::Sequence<RobotCombatCommand>) -> bool;
}

// Corresponds to arena_battle_interfaces__msg__RobotCombatCommand
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RobotCombatCommand {

    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_velocity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angular_velocity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub shoot: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub shield: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub weapon_type: u8,

}



impl Default for RobotCombatCommand {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !arena_battle_interfaces__msg__RobotCombatCommand__init(&mut msg as *mut _) {
        panic!("Call to arena_battle_interfaces__msg__RobotCombatCommand__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RobotCombatCommand {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { arena_battle_interfaces__msg__RobotCombatCommand__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { arena_battle_interfaces__msg__RobotCombatCommand__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { arena_battle_interfaces__msg__RobotCombatCommand__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RobotCombatCommand {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RobotCombatCommand where Self: Sized {
  const TYPE_NAME: &'static str = "arena_battle_interfaces/msg/RobotCombatCommand";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__arena_battle_interfaces__msg__RobotCombatCommand() }
  }
}


