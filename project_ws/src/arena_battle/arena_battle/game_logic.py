#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from arena_battle_interfaces.msg import RobotCombatCommand

class GameLogic(Node):
    def __init__(self):
        super().__init__('game_logic')
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.sub = self.create_subscription(RobotCombatCommand, '/robot_command', self.command_callback, 10)
        self.marker_pub = self.create_publisher(Marker, '/robot_marker', 10)
        self.timer = self.create_timer(0.05, self.update_visualization)
        self.get_logger().info('Game Logic Ready')

    def command_callback(self, msg):
        self.theta += msg.angular_velocity * 0.1
        self.x += msg.linear_velocity * math.cos(self.theta) * 0.2
        self.y += msg.linear_velocity * math.sin(self.theta) * 0.2
        if msg.shoot:
            self.get_logger().info('PEW!')
        if msg.shield:
            self.get_logger().info('Shield Activated!')
        if msg.weapon_type == 1:
            self.get_logger().info('SPECIAL ATTACK!')

    def update_visualization(self):
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'robot'
        marker.id = 0
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.pose.position.x = self.x
        marker.pose.position.y = self.y
        marker.pose.position.z = 0.0
        marker.pose.orientation.z = math.sin(self.theta / 2)
        marker.pose.orientation.w = math.cos(self.theta / 2)
        marker.scale.x = 0.5
        marker.scale.y = 0.2
        marker.scale.z = 0.2
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0
        self.marker_pub.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = GameLogic()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
