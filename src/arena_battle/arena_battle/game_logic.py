#!/usr/bin/env python3

import math
import time
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import RobotCombatCommand, RobotState, Projectile

class GameLogic(Node):
    def __init__(self):
        super().__init__('game_logic')
        
        # Robot pose and game state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.turret_angle = 0.0
        
        self.health = 100
        self.shield_active = False
        self.shield_duration = 0.0
        self.shield_energy = 100.0
        self.score = 0
        self.ammo = 10
        self.max_ammo = 10
        self.ammo_regen_timer = 0.0
        self.game_over = False
        self.start_time = None
        
        self.projectiles = []  # list of dicts: {'id': int, 'x': float, 'y': float, 'vx': float, 'vy': float, 'type': int, 'lifetime': float}
        self.projectile_id_counter = 0
        
        # Subscribe to robot commands
        self.sub = self.create_subscription(
            RobotCombatCommand, 
            '/robot_command', 
            self.command_callback, 
            10
        )
        
        # Publisher for game/robot state
        self.state_pub = self.create_publisher(
            RobotState,
            '/robot_state',
            10
        )
        
        # Timer for updates (50Hz -> dt = 0.02s)
        self.dt = 0.02
        self.timer = self.create_timer(self.dt, self.update_game)
        
        self.get_logger().info('Game Logic (Model Node) Ready!')

    def command_callback(self, msg):
        if self.game_over:
            return
            
        # Update turret angle (relative to base)
        self.turret_angle = msg.turret_angle
        
        # Update robot pose
        self.theta += msg.angular_velocity * 0.1
        new_x = self.x + msg.linear_velocity * math.cos(self.theta) * 0.2
        new_y = self.y + msg.linear_velocity * math.sin(self.theta) * 0.2
        
        # Circular arena boundary constraint (radius 3.5m, robot radius ~0.25m -> max_r = 3.25m)
        dist = math.sqrt(new_x**2 + new_y**2)
        if dist > 3.25:
            self.x = 3.25 * new_x / dist
            self.y = 3.25 * new_y / dist
        else:
            self.x = new_x
            self.y = new_y
        
        # Handle weapon firing
        if msg.shoot:
            self.shoot_projectile()
        if msg.shield:
            self.activate_shield()
        if msg.weapon_type == 1:
            self.shoot_special()

    def shoot_projectile(self):
        if self.ammo > 0:
            self.ammo -= 1
            self.projectile_id_counter = (self.projectile_id_counter + 1) % 2147483647
            
            absolute_turret_angle = self.theta + self.turret_angle
            px = self.x + 0.3 * math.cos(absolute_turret_angle)
            py = self.y + 0.3 * math.sin(absolute_turret_angle)
            vx = 6.0 * math.cos(absolute_turret_angle)
            vy = 6.0 * math.sin(absolute_turret_angle)
            
            self.projectiles.append({
                'id': self.projectile_id_counter,
                'x': px,
                'y': py,
                'vx': vx,
                'vy': vy,
                'type': 0, # Normal
                'lifetime': 2.0
            })
            self.get_logger().info('💥 PEW! Projectile fired!')

    def activate_shield(self):
        if not self.shield_active and self.shield_energy >= 30.0:
            self.shield_active = True
            self.shield_duration = 1.5
            self.shield_energy -= 30.0
            self.get_logger().info('🛡️ Shield Matrix Activated!')

    def shoot_special(self):
        if self.ammo >= 5:
            self.ammo -= 5
            self.get_logger().info('⚡ SPECIAL RADIAL ATTACK!')
            for i in range(8):
                self.projectile_id_counter = (self.projectile_id_counter + 1) % 2147483647
                angle = self.theta + (i * math.pi / 4)
                px = self.x + 0.2 * math.cos(angle)
                py = self.y + 0.2 * math.sin(angle)
                vx = 4.0 * math.cos(angle)
                vy = 4.0 * math.sin(angle)
                
                self.projectiles.append({
                    'id': self.projectile_id_counter,
                    'x': px,
                    'y': py,
                    'vx': vx,
                    'vy': vy,
                    'type': 1, # Special
                    'lifetime': 1.0
                })

    def update_game(self):
        if self.start_time is None:
            self.start_time = time.time()
            
        time_elapsed = time.time() - self.start_time
        
        # Update shield duration
        if self.shield_active:
            self.shield_duration -= self.dt
            if self.shield_duration <= 0.0:
                self.shield_active = False
                
        # Regenerate shield energy slowly over time
        if not self.shield_active and self.shield_energy < 100.0:
            self.shield_energy = min(100.0, self.shield_energy + 5.0 * self.dt) # 5 units per second
            
        # Regenerate ammo
        if self.ammo < self.max_ammo:
            self.ammo_regen_timer += self.dt
            if self.ammo_regen_timer >= 1.0: # 1 ammo per second
                self.ammo += 1
                self.ammo_regen_timer = 0.0
                
        # Update projectiles
        for p in self.projectiles[:]:
            p['x'] += p['vx'] * self.dt
            p['y'] += p['vy'] * self.dt
            p['lifetime'] -= self.dt
            
            # Check boundary
            dist = math.sqrt(p['x']**2 + p['y']**2)
            if dist >= 3.5 or p['lifetime'] <= 0.0:
                self.projectiles.remove(p)
                # Gain small points for hitting the boundary wall as target practice
                if not self.game_over:
                    self.score += 10
                    
        # Publish state
        state_msg = RobotState()
        state_msg.x = float(self.x)
        state_msg.y = float(self.y)
        state_msg.theta = float(self.theta)
        state_msg.turret_angle = float(self.turret_angle)
        state_msg.health = int(self.health)
        state_msg.shield_active = bool(self.shield_active)
        state_msg.shield_energy = float(self.shield_energy)
        state_msg.score = int(self.score)
        state_msg.ammo = int(self.ammo)
        state_msg.game_over = bool(self.game_over)
        state_msg.time_elapsed = float(time_elapsed)
        
        state_msg.projectiles = []
        for p in self.projectiles:
            p_msg = Projectile()
            p_msg.id = int(p['id'])
            p_msg.x = float(p['x'])
            p_msg.y = float(p['y'])
            p_msg.vx = float(p['vx'])
            p_msg.vy = float(p['vy'])
            p_msg.type = int(p['type'])
            state_msg.projectiles.append(p_msg)
            
        self.state_pub.publish(state_msg)

def main(args=None):
    rclpy.init(args=args)
    node = GameLogic()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
