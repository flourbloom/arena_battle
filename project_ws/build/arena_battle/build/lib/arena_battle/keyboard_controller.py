#!/usr/bin/env python3

import sys
import tty
import termios
import select
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import RobotCombatCommand

class KeyboardController(Node):
    def __init__(self):
        super().__init__('keyboard_controller')
        self.publisher = self.create_publisher(RobotCombatCommand, '/robot_command', 10)
        self.get_logger().info('Controls: WASD | Space=Shoot | Q=Shield | E=Special')

    def get_key(self):
        dr, _, _ = select.select([sys.stdin], [], [], 0.02)
        if dr:
            return sys.stdin.read(1)
        return None

    def run(self):
        while rclpy.ok():
            key = self.get_key()
            if key is None:
                continue
            msg = RobotCombatCommand()
            key = key.lower()
            if key == 'w':
                msg.linear_velocity = 1.0
            elif key == 's':
                msg.linear_velocity = -1.0
            elif key == 'a':
                msg.angular_velocity = 1.0
            elif key == 'd':
                msg.angular_velocity = -1.0
            elif key == ' ':
                msg.shoot = True
            elif key == 'q':
                msg.shield = True
            elif key == 'e':
                msg.weapon_type = 1
            else:
                continue
            self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardController()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
