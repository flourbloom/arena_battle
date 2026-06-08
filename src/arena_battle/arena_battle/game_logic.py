#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import TransformStamped
from arena_battle_interfaces.msg import RobotCombatCommand
from std_msgs.msg import Float64

class GameLogic(Node):
    def __init__(self):
        super().__init__('game_logic')
        
        # Robot pose
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.turret_angle = 0.0
        
        # Subscribe to robot commands
        self.sub = self.create_subscription(
            RobotCombatCommand, 
            '/robot_command', 
            self.command_callback, 
            10
        )
        
        # Publisher for turret joint
        self.turret_pub = self.create_publisher(
            Float64,
            '/turret_joint/command',
            10
        )
        
        # Publisher for projectile markers (kept for shooting effects)
        self.marker_pub = self.create_publisher(
            Marker, 
            '/projectile_marker', 
            10
        )
        
        # Timer for updates
        self.timer = self.create_timer(0.05, self.update_robot)
        
        self.get_logger().info('Game Logic Ready - Arena Battle Robot')
        self.get_logger().info('Use WASD to move, mouse to aim turret')

    def command_callback(self, msg):
        # Update robot pose
        self.theta += msg.angular_velocity * 0.1
        self.x += msg.linear_velocity * math.cos(self.theta) * 0.2
        self.y += msg.linear_velocity * math.sin(self.theta) * 0.2
        
        # Handle weapons
        if msg.shoot:
            self.shoot_projectile()
        if msg.shield:
            self.get_logger().info('🛡️ Shield Activated!')
        if msg.weapon_type == 1:
            self.get_logger().info('⚡ SPECIAL ATTACK!')
            self.shoot_special()

    def shoot_projectile(self):
        # Create projectile marker
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'projectile'
        marker.id = self.get_clock().now().nanosec  # Unique ID
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        
        # Position from turret
        marker.pose.position.x = self.x + 0.3 * math.cos(self.theta)
        marker.pose.position.y = self.y + 0.3 * math.sin(self.theta)
        marker.pose.position.z = 0.1
        
        marker.scale.x = 0.05
        marker.scale.y = 0.05
        marker.scale.z = 0.05
        
        marker.color.r = 1.0
        marker.color.g = 0.5
        marker.color.b = 0.0
        marker.color.a = 1.0
        
        # Set lifetime
        marker.lifetime.sec = 2  # 2 seconds
        
        self.marker_pub.publish(marker)
        self.get_logger().info('💥 PEW! Projectile fired!')

    def shoot_special(self):
        # Create special attack markers
        for i in range(8):
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'special_attack'
            marker.id = self.get_clock().now().nanosec + i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            
            angle = self.theta + (i * math.pi / 4)
            marker.pose.position.x = self.x + 0.2 * math.cos(angle)
            marker.pose.position.y = self.y + 0.2 * math.sin(angle)
            marker.pose.position.z = 0.15
            
            marker.scale.x = 0.04
            marker.scale.y = 0.04
            marker.scale.z = 0.04
            
            marker.color.r = 0.0
            marker.color.g = 0.8
            marker.color.b = 1.0
            marker.color.a = 1.0
            
            marker.lifetime.sec = 1
            
            self.marker_pub.publish(marker)

    def update_robot(self):
        # Publish turret angle
        turret_msg = Float64()
        turret_msg.data = self.turret_angle
        self.turret_pub.publish(turret_msg)

def main(args=None):
    rclpy.init(args=args)
    node = GameLogic()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
