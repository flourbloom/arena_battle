#!/usr/bin/env python3

import sys
import tty
import termios
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import RobotCombatCommand

class KeyboardController(Node):
    def __init__(self):
        super().__init__('keyboard_controller')
        self.publisher = self.create_publisher(RobotCombatCommand, '/robot_command', 10)
        self.get_logger().info('Controls: WASD | Space=Shoot | Q=Shield | E=Special')
        self.get_logger().info('Press Ctrl+C to exit')

    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def run(self):
        while rclpy.ok():
            key = self.get_key()
            
            # Create and publish command message
            msg = RobotCombatCommand()
            msg.turret_angle = 0.0
            
            # Handle movement
            if key == 'w':
                msg.linear_velocity = 1.0
                self.get_logger().info('Moving Forward', throttle_duration_sec=0.5)
            elif key == 's':
                msg.linear_velocity = -1.0
                self.get_logger().info('Moving Backward', throttle_duration_sec=0.5)
            elif key == 'a':
                msg.angular_velocity = 1.0
                self.get_logger().info('Rotating Left', throttle_duration_sec=0.5)
            elif key == 'd':
                msg.angular_velocity = -1.0
                self.get_logger().info('Rotating Right', throttle_duration_sec=0.5)
            elif key == ' ':
                msg.shoot = True
                self.get_logger().info('PEW!')
            elif key == 'q':
                msg.shield = True
                self.get_logger().info('Shield Activated!')
            elif key == 'e':
                msg.weapon_type = 1
                self.get_logger().info('SPECIAL ATTACK!')
            elif key == '\x03':  # Ctrl+C
                break
            else:
                # Ignore other keys
                continue
            
            # Publish the command
            self.publisher.publish(msg)
            
            # Small delay to prevent overwhelming the system
            rclpy.spin_once(self, timeout_sec=0.05)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardController()
    
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
