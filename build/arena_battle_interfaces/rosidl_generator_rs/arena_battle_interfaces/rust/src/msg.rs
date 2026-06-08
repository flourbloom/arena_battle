#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to arena_battle_interfaces__msg__RobotCombatCommand

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::RobotCombatCommand::default())
  }
}

impl rosidl_runtime_rs::Message for RobotCombatCommand {
  type RmwMsg = super::msg::rmw::RobotCombatCommand;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        linear_velocity: msg.linear_velocity,
        angular_velocity: msg.angular_velocity,
        shoot: msg.shoot,
        shield: msg.shield,
        weapon_type: msg.weapon_type,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      linear_velocity: msg.linear_velocity,
      angular_velocity: msg.angular_velocity,
      shoot: msg.shoot,
      shield: msg.shield,
      weapon_type: msg.weapon_type,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      linear_velocity: msg.linear_velocity,
      angular_velocity: msg.angular_velocity,
      shoot: msg.shoot,
      shield: msg.shield,
      weapon_type: msg.weapon_type,
    }
  }
}


