#!/usr/bin/env python3

import sys
import select
import tty
import termios
import math
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import RobotCombatCommand

class TeleopControl(Node):
    def __init__(self):
        super().__init__('teleop_control')
        
        # Publish to the relative topic "command".
        # This will resolve to /p1/command or /p2/command when run in a namespace.
        self.publisher = self.create_publisher(RobotCombatCommand, 'command', 10)
        
        # State variables
        self.linear = 0.0
        self.angular = 0.0
        self.turret_angle = 0.0
        self.shoot = False
        self.shield = False
        self.weapon_type = 0
        
        self.last_key_time = self.get_clock().now()
        self.watchdog_timeout = 0.15 # seconds before resetting velocities if key released
        
        # Save terminal settings to restore them at shutdown
        self.settings = termios.tcgetattr(sys.stdin)
        
        # Publish timer at 20Hz (0.05 seconds interval)
        self.timer = self.create_timer(0.05, self.publish_command)
        
        # Display instructions
        self.get_logger().info('Teleop Control Node Initialized!')
        self.get_logger().info('-----------------------------------------')
        self.get_logger().info('Controls:')
        self.get_logger().info('  W / S : Move Forward / Backward')
        self.get_logger().info('  A / D : Rotate Base Left / Right')
        self.get_logger().info('  J / L : Aim Turret Left / Right')
        self.get_logger().info('  Space : Shoot normal projectile')
        self.get_logger().info('  Q     : Activate shield (costs energy)')
        self.get_logger().info('  E     : Special attack (costs 5 ammo)')
        self.get_logger().info('  Ctrl+C: Exit')
        self.get_logger().info('-----------------------------------------')

    def publish_command(self):
        # Watchdog: check if user released movement keys
        now = self.get_clock().now()
        dt = (now - self.last_key_time).nanoseconds / 1e9
        if dt > self.watchdog_timeout:
            self.linear = 0.0
            self.angular = 0.0
            
        msg = RobotCombatCommand()
        msg.linear_velocity = float(self.linear)
        msg.angular_velocity = float(self.angular)
        msg.turret_angle = float(self.turret_angle)
        msg.shoot = bool(self.shoot)
        msg.shield = bool(self.shield)
        msg.weapon_type = int(self.weapon_type)
        
        self.publisher.publish(msg)
        
        # Reset one-shot trigger states
        self.shoot = False
        self.shield = False
        self.weapon_type = 0

    def get_key(self):
        # Check if stdin has data waiting
        rlist, _, _ = select.select([sys.stdin], [], [], 0.02)
        if rlist:
            key = sys.stdin.read(1)
            return key
        return None

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def run(self):
        try:
            # Put stdin into raw/non-canonical mode
            tty.setraw(sys.stdin.fileno())
            
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.005)
                key = self.get_key()
                
                if key is not None:
                    self.last_key_time = self.get_clock().now()
                    
                    if key == 'w':
                        self.linear = 1.0
                    elif key == 's':
                        self.linear = -1.0
                    elif key == 'a':
                        self.angular = 1.0
                    elif key == 'd':
                        self.angular = -1.0
                    elif key == 'j':
                        # Rotate turret counter-clockwise
                        self.turret_angle = self.normalize_angle(self.turret_angle + 0.15)
                    elif key == 'l':
                        # Rotate turret clockwise
                        self.turret_angle = self.normalize_angle(self.turret_angle - 0.15)
                    elif key == ' ':
                        self.shoot = True
                    elif key == 'q':
                        self.shield = True
                    elif key == 'e':
                        self.weapon_type = 1
                    elif key == '\x03': # Ctrl+C
                        break
        finally:
            # Restore terminal settings to normal
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopControl()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
