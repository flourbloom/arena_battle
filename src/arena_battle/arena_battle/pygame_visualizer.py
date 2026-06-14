#!/usr/bin/env python3

import sys
import math
import random
import pygame
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import RobotCombatCommand, RobotState

class PygameVisualizer(Node):
    def __init__(self):
        super().__init__('pygame_visualizer')
        
        # Robot position and orientation from state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.turret_angle = 0.0
        
        # Gameplay status
        self.health = 100
        self.shield_active = False
        self.shield_energy = 100.0
        self.score = 0
        self.ammo = 10
        self.game_over = False
        self.time_elapsed = 0.0
        
        # Visual particles
        self.particles = []
        
        # Track active projectiles for rendering and spawning particles
        self.projectiles = []
        self.active_projectile_ids = set()
        self.prev_projectiles_pos = {} # maps pid -> (x, y, type)
        
        # Command publishing states (Controller part)
        self.last_linear = 0.0
        self.last_angular = 0.0
        self.last_command_time = self.get_clock().now()
        self.command_publish_interval = 0.05 # 20 Hz
        
        # Subscription to game state (View part)
        self.state_sub = self.create_subscription(
            RobotState,
            '/robot_state',
            self.state_callback,
            10
        )
        
        # Publisher for inputs (Controller part)
        self.cmd_pub = self.create_publisher(
            RobotCombatCommand,
            '/robot_command',
            10
        )
        
        # Initialize Pygame
        pygame.init()
        pygame.font.init()
        
        # Set up display
        self.screen_width = 800
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Arena Battle - Robot Visualizer")
        
        # Coordinates mapping: 1 meter = 100 pixels
        self.scale = 100.0
        self.cx = self.screen_width // 2
        self.cy = self.screen_height // 2
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            self.font_title = pygame.font.SysFont("Outfit", 18, bold=True)
            self.font_hud = pygame.font.SysFont("Outfit", 14)
            self.font_controls = pygame.font.SysFont("Outfit", 12)
        except Exception:
            self.font_title = pygame.font.Font(None, 22)
            self.font_hud = pygame.font.Font(None, 18)
            self.font_controls = pygame.font.Font(None, 16)
            
        self.get_logger().info("Pygame Visualizer (View/Controller Node) Initialized!")

    def state_callback(self, msg):
        # Trigger exhaust particles if robot is moving
        if msg.x != self.x or msg.y != self.y or msg.theta != self.theta:
            self.spawn_exhaust_particles()
            
        # Update pose
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta
        self.turret_angle = msg.turret_angle
        
        # Update HUD state
        self.health = msg.health
        self.shield_active = msg.shield_active
        self.shield_energy = msg.shield_energy
        self.score = msg.score
        self.ammo = msg.ammo
        self.game_over = msg.game_over
        self.time_elapsed = msg.time_elapsed
        
        # Process projectiles & spawn particles
        current_projectiles = {p.id: p for p in msg.projectiles}
        current_ids = set(current_projectiles.keys())
        
        # Spawn flash particles for newly created projectiles
        new_ids = current_ids - self.active_projectile_ids
        for pid in new_ids:
            p = current_projectiles[pid]
            # Calculate spawning direction relative to robot heading
            dx = p.x - self.x
            dy = p.y - self.y
            angle = math.atan2(dy, dx)
            color = (255, 100, 0) if p.type == 0 else (0, 204, 255)
            self.spawn_flash_particles(p.x, p.y, angle, color)
            
        # Spawn impact particles for dead projectiles
        dead_ids = self.active_projectile_ids - current_ids
        for pid in dead_ids:
            if pid in self.prev_projectiles_pos:
                last_x, last_y, last_type = self.prev_projectiles_pos[pid]
                dist = math.sqrt(last_x**2 + last_y**2)
                if dist >= 3.4: # near boundary
                    impact_angle = math.atan2(last_y, last_x)
                    ix = 3.5 * math.cos(impact_angle)
                    iy = 3.5 * math.sin(impact_angle)
                    color = (255, 100, 0) if last_type == 0 else (0, 204, 255)
                    self.spawn_impact_particles(ix, iy, color)
                    
        # Update local states for next callback
        self.active_projectile_ids = current_ids
        self.prev_projectiles_pos = {p.id: (p.x, p.y, p.type) for p in msg.projectiles}
        
        # Store current active projectiles
        self.projectiles = [
            {
                'x': p.x,
                'y': p.y,
                'type': p.type,
                'vx': p.vx,
                'vy': p.vy,
                'color': (255, 100, 0) if p.type == 0 else (0, 204, 255),
                'radius': 5 if p.type == 0 else 4
            }
            for p in msg.projectiles
        ]

    def spawn_exhaust_particles(self):
        rear_x = self.x - 0.2 * math.cos(self.theta)
        rear_y = self.y - 0.2 * math.sin(self.theta)
        
        for _ in range(2):
            vx = -0.5 * math.cos(self.theta) + random.uniform(-0.2, 0.2)
            vy = -0.5 * math.sin(self.theta) + random.uniform(-0.2, 0.2)
            self.particles.append({
                'x': rear_x,
                'y': rear_y,
                'vx': vx,
                'vy': vy,
                'radius': random.randint(4, 8),
                'color': (80 + random.randint(0, 30), 120 + random.randint(0, 30), 200 + random.randint(0, 50)),
                'alpha': 180.0,
                'decay': 350.0,
                'size_decay': 4.0
            })

    def spawn_flash_particles(self, px, py, angle, color):
        for _ in range(8):
            spread = angle + random.uniform(-0.4, 0.4)
            speed = random.uniform(1.0, 3.0)
            self.particles.append({
                'x': px,
                'y': py,
                'vx': speed * math.cos(spread),
                'vy': speed * math.sin(spread),
                'radius': random.randint(3, 6),
                'color': color,
                'alpha': 255.0,
                'decay': 1200.0,
                'size_decay': 15.0
            })

    def spawn_impact_particles(self, px, py, color):
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.0)
            self.particles.append({
                'x': px,
                'y': py,
                'vx': speed * math.cos(angle),
                'vy': speed * math.sin(angle),
                'radius': random.randint(2, 5),
                'color': color,
                'alpha': 255.0,
                'decay': 800.0,
                'size_decay': 8.0
            })

    def to_screen(self, x, y):
        px = self.cx + int(x * self.scale)
        py = self.cy - int(y * self.scale)
        return px, py

    def to_world(self, px, py):
        x = (px - self.cx) / self.scale
        y = (self.cy - py) / self.scale
        return x, y

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def publish_combat_command(self, linear=0.0, angular=0.0, shoot=False, shield=False, weapon_type=0):
        msg = RobotCombatCommand()
        msg.linear_velocity = linear
        msg.angular_velocity = angular
        msg.shoot = shoot
        msg.shield = shield
        msg.weapon_type = weapon_type
        msg.turret_angle = self.turret_angle
        self.cmd_pub.publish(msg)

    def run(self):
        running = True
        
        while running and rclpy.ok():
            # Process ROS callbacks
            rclpy.spin_once(self, timeout_sec=0.001)
            
            dt = self.clock.tick(60) / 1000.0
            
            # --- Pygame Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.publish_combat_command(shoot=True)
                    elif event.key == pygame.K_q:
                        self.publish_combat_command(shield=True)
                    elif event.key == pygame.K_e:
                        self.publish_combat_command(weapon_type=1)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left Click
                        self.publish_combat_command(shoot=True)
                        
            # --- Continuous Key Press Tracking (Movement) ---
            keys = pygame.key.get_pressed()
            linear = 0.0
            angular = 0.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                linear += 1.0
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                linear -= 1.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                angular += 1.0
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                angular -= 1.0
                
            # --- Mouse Aiming Update ---
            mx, my = pygame.mouse.get_pos()
            world_mx, world_my = self.to_world(mx, my)
            dx = world_mx - self.x
            dy = world_my - self.y
            target_abs = math.atan2(dy, dx)
            self.turret_angle = self.normalize_angle(target_abs - self.theta)
            
            # Publish movement commands periodically
            now = self.get_clock().now()
            time_since_last_cmd = (now - self.last_command_time).nanoseconds / 1e9
            
            if (linear != self.last_linear or angular != self.last_angular or 
                time_since_last_cmd >= self.command_publish_interval):
                self.publish_combat_command(linear=linear, angular=angular)
                self.last_linear = linear
                self.last_angular = angular
                self.last_command_time = now

            # --- Update Particles ---
            for p in self.particles[:]:
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['alpha'] -= p['decay'] * dt
                p['radius'] = max(1.0, p['radius'] - p['size_decay'] * dt)
                if p['alpha'] <= 0.0:
                    self.particles.remove(p)
                    
            # --- Draw trail particles on active projectiles ---
            for p in self.projectiles:
                # Add trail particle occasionally
                if random.random() < 0.3:
                    self.particles.append({
                        'x': p['x'],
                        'y': p['y'],
                        'vx': -0.2 * p['vx'] + random.uniform(-0.1, 0.1),
                        'vy': -0.2 * p['vy'] + random.uniform(-0.1, 0.1),
                        'radius': int(p['radius'] * 0.7),
                        'color': p['color'],
                        'alpha': 150.0,
                        'decay': 600.0,
                        'size_decay': 2.0
                    })

            # --- Rendering Phase ---
            self.screen.fill((8, 8, 16)) # Cyber dark blue background
            
            alpha_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            
            # 1. Draw Grid Lines
            grid_interval = 0.5
            for i in range(-7, 8):
                gx = i * grid_interval
                sp_x, sp_y_top = self.to_screen(gx, 3.5)
                _, sp_y_bot = self.to_screen(gx, -3.5)
                pygame.draw.line(alpha_surface, (24, 24, 48, 120), (sp_x, sp_y_top), (sp_x, sp_y_bot), 1)
                
                gy = i * grid_interval
                sp_x_left, sp_y = self.to_screen(-3.5, gy)
                sp_x_right, _ = self.to_screen(3.5, gy)
                pygame.draw.line(alpha_surface, (24, 24, 48, 120), (sp_x_left, sp_y), (sp_x_right, sp_y), 1)
                
            # 2. Draw Arena Boundary
            apx, apy = self.to_screen(0, 0)
            arena_pixel_radius = int(3.5 * self.scale)
            pygame.draw.circle(alpha_surface, (255, 60, 0, 50), (apx, apy), arena_pixel_radius + 5, 4)
            pygame.draw.circle(self.screen, (255, 50, 0), (apx, apy), arena_pixel_radius, 4)
            
            self.screen.blit(alpha_surface, (0, 0))
            
            # 3. Draw Particles
            particle_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            for p in self.particles:
                px, py = self.to_screen(p['x'], p['y'])
                color = (p['color'][0], p['color'][1], p['color'][2], max(0, min(255, int(p['alpha']))))
                pygame.draw.circle(particle_surface, color, (px, py), int(p['radius']))
            self.screen.blit(particle_surface, (0, 0))
            
            # 4. Draw Projectiles
            for p in self.projectiles:
                px, py = self.to_screen(p['x'], p['y'])
                pygame.draw.circle(self.screen, (min(255, p['color'][0] + 50), min(255, p['color'][1] + 50), min(255, p['color'][2] + 50)), (px, py), p['radius'] + 2)
                pygame.draw.circle(self.screen, p['color'], (px, py), p['radius'])
                
            # 5. Draw Robot Chassis & Turret
            robot_px, robot_py = self.to_screen(self.x, self.y)
            
            # Base/Chassis
            chassis_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            # Wheels
            pygame.draw.rect(chassis_surf, (40, 40, 40), (22, 10, 16, 4))
            pygame.draw.rect(chassis_surf, (0, 0, 0), (22, 10, 16, 4), 1)
            pygame.draw.rect(chassis_surf, (40, 40, 40), (22, 66, 16, 4))
            pygame.draw.rect(chassis_surf, (0, 0, 0), (22, 66, 16, 4), 1)
            # Casters
            pygame.draw.circle(chassis_surf, (120, 120, 120), (58, 40), 3)
            pygame.draw.circle(chassis_surf, (120, 120, 120), (22, 40), 3)
            # Chassis Box
            pygame.draw.rect(chassis_surf, (0, 102, 204), (20, 25, 40, 30))
            pygame.draw.rect(chassis_surf, (0, 246, 255), (20, 25, 40, 30), 2)
            # Cover plate
            pygame.draw.rect(chassis_surf, (70, 70, 70), (22, 27, 36, 26))
            pygame.draw.rect(chassis_surf, (150, 150, 150), (22, 27, 36, 26), 1)
            
            rotated_chassis = pygame.transform.rotate(chassis_surf, math.degrees(self.theta))
            chassis_rect = rotated_chassis.get_rect(center=(robot_px, robot_py))
            self.screen.blit(rotated_chassis, chassis_rect)
            
            # Turret
            turret_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.rect(turret_surf, (60, 60, 60), (40, 38, 15, 4))
            pygame.draw.rect(turret_surf, (0, 0, 0), (40, 38, 15, 4), 1)
            pygame.draw.circle(turret_surf, (204, 0, 0), (40, 40), 10)
            pygame.draw.circle(turret_surf, (255, 51, 51), (40, 40), 10, 2)
            
            absolute_turret_angle = self.theta + self.turret_angle
            rotated_turret = pygame.transform.rotate(turret_surf, math.degrees(absolute_turret_angle))
            turret_rect = rotated_turret.get_rect(center=(robot_px, robot_py))
            self.screen.blit(rotated_turret, turret_rect)
            
            # 6. Draw Robot Shield
            if self.shield_active:
                shield_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                pulse_val = abs(math.sin(pygame.time.get_ticks() * 0.01))
                alpha = int(80 + pulse_val * 60)
                pygame.draw.circle(shield_surface, (0, 255, 255, alpha), (robot_px, robot_py), 35, 3)
                pygame.draw.circle(shield_surface, (0, 255, 255, alpha // 4), (robot_px, robot_py), 32)
                self.screen.blit(shield_surface, (0, 0))
                
            # 7. Draw HUD (Glassmorphism Dashboard)
            hud_surface = pygame.Surface((230, 130), pygame.SRCALPHA)
            pygame.draw.rect(hud_surface, (0, 0, 10, 180), (0, 0, 230, 130), border_radius=8)
            pygame.draw.rect(hud_surface, (0, 246, 255, 120), (0, 0, 230, 130), 2, border_radius=8)
            
            label_title = self.font_title.render("COMBAT ROBOT HUD", True, (0, 246, 255))
            hud_surface.blit(label_title, (15, 8))
            
            txt_pos = f"Pos: X: {self.x:.2f}m | Y: {self.y:.2f}m"
            txt_head = f"Heading: {math.degrees(self.theta):.1f}°"
            txt_turret = f"Turret Joint: {math.degrees(self.turret_angle):.1f}°"
            txt_time = f"Time: {self.time_elapsed:.1f}s"
            
            hud_surface.blit(self.font_hud.render(txt_pos, True, (220, 220, 220)), (15, 30))
            hud_surface.blit(self.font_hud.render(txt_head, True, (220, 220, 220)), (15, 50))
            hud_surface.blit(self.font_hud.render(txt_turret, True, (220, 220, 220)), (15, 70))
            hud_surface.blit(self.font_hud.render(txt_time, True, (220, 220, 220)), (15, 90))
            
            # Health display
            label_hp = self.font_hud.render("HP:", True, (255, 50, 50))
            hud_surface.blit(label_hp, (15, 110))
            pygame.draw.rect(hud_surface, (100, 20, 20), (45, 112, 100, 10))
            pygame.draw.rect(hud_surface, (255, 50, 50), (45, 112, self.health, 10))
            
            self.screen.blit(hud_surface, (20, 20))
            
            # 8. Draw System Status HUD (Right panel)
            status_hud = pygame.Surface((230, 115), pygame.SRCALPHA)
            pygame.draw.rect(status_hud, (0, 0, 10, 180), (0, 0, 230, 115), border_radius=8)
            pygame.draw.rect(status_hud, (255, 100, 0, 120), (0, 0, 230, 115), 2, border_radius=8)
            
            label_s_title = self.font_title.render("SYSTEM STATUS", True, (255, 120, 0))
            status_hud.blit(label_s_title, (15, 8))
            
            shield_status = "ONLINE" if self.shield_active else "READY"
            shield_color = (0, 255, 255) if self.shield_active else (0, 255, 100)
            status_hud.blit(self.font_hud.render("Shield Matrix: ", True, (220, 220, 220)), (15, 30))
            status_hud.blit(self.font_hud.render(shield_status, True, shield_color), (120, 30))
            
            # Ammo display
            status_hud.blit(self.font_hud.render(f"Ammo: {self.ammo}/10", True, (220, 220, 220)), (15, 50))
            # Score display
            status_hud.blit(self.font_hud.render(f"Score: {self.score}", True, (220, 220, 220)), (15, 70))
            
            # Controls notice
            label_ctrl = self.font_controls.render("WASD: Move | Q: Shield | E: Special", True, (150, 150, 150))
            status_hud.blit(label_ctrl, (15, 95))
            
            self.screen.blit(status_hud, (self.screen_width - 250, 20))
            
            pygame.display.flip()
            
        pygame.quit()

def main(args=None):
    rclpy.init(args=args)
    visualizer = PygameVisualizer()
    try:
        visualizer.run()
    except KeyboardInterrupt:
        pass
    finally:
        visualizer.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
