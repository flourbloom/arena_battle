#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from arena_battle_interfaces.msg import RobotCombatCommand

class RobotPoseTF(Node):
    def __init__(self):
        super().__init__('robot_pose_tf')
        
        # Initialize robot pose
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        # Subscribe to robot commands
        self.subscription = self.create_subscription(
            RobotCombatCommand,
            '/robot_command',
            self.command_callback,
            10
        )
        
        # Create TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Create timer for TF publishing
        self.timer = self.create_timer(0.05, self.publish_transform)
        
        self.get_logger().info('Robot Pose TF Broadcaster ready')
    
    def command_callback(self, msg):
        # Update robot pose based on commands (matching game_logic)
        self.theta += msg.angular_velocity * 0.1
        self.x += msg.linear_velocity * math.cos(self.theta) * 0.2
        self.y += msg.linear_velocity * math.sin(self.theta) * 0.2
    
    def publish_transform(self):
        # Create transform from map to base_link
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'map'
        t.child_frame_id = 'base_link'
        
        # Set translation
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.05  # Slight elevation
        
        # Set rotation (yaw only)
        t.transform.rotation.z = math.sin(self.theta / 2.0)
        t.transform.rotation.w = math.cos(self.theta / 2.0)
        
        # Broadcast transform
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = RobotPoseTF()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
