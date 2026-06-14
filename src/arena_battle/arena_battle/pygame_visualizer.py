#!/usr/bin/env python3

import sys
import math
import random
import pygame
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from visualization_msgs.msg import Marker
from arena_battle_interfaces.msg import RobotCombatCommand

class PygameVisualizer(Node):
    def __init__(self):
        super().__init__('pygame_visualizer')
        
        # Robot position and orientation
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.turret_angle = 0.0  # Relative to chassis (base_link)
        self.shield_timer = 0.0  # Remaining time for shield visualization
        
        # Lists to store local game entities and effects
        self.projectiles = []    # Dicts of active projectiles
        self.particles = []      # Dicts of visual particles
        
        # Last command state to detect changes and throttle publishing
        self.last_linear = 0.0
        self.last_angular = 0.0
        self.last_command_time = self.get_clock().now()
        self.command_publish_interval = 0.05  # 20 Hz publishing rate
        
        # Subscriptions
        self.cmd_sub = self.create_subscription(
            RobotCombatCommand,
            '/robot_command',
            self.command_callback,
            10
        )
        
        self.marker_sub = self.create_subscription(
            Marker,
            '/projectile_marker',
            self.marker_callback,
            10
        )
        
        # Publishers
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
            
        self.get_logger().info("Pygame Visualizer Initialized!")

    def command_callback(self, msg):
        # Update pose based on command messages (keep in sync with game_logic)
        self.theta += msg.angular_velocity * 0.1
        new_x = self.x + msg.linear_velocity * math.cos(self.theta) * 0.2
        new_y = self.y + msg.linear_velocity * math.sin(self.theta) * 0.2
        
        # Enforce circular boundary constraint
        dist = math.sqrt(new_x**2 + new_y**2)
        if dist > 3.25:
            self.x = 3.25 * new_x / dist
            self.y = 3.25 * new_y / dist
        else:
            self.x = new_x
            self.y = new_y
            
        # Update turret angle
        self.turret_angle = msg.turret_angle
        
        # Trigger shield visualization
        if msg.shield:
            self.shield_timer = 1.5
            
        # Add exhaust particles if moving
        if msg.linear_velocity != 0.0 or msg.angular_velocity != 0.0:
            self.spawn_exhaust_particles()

    def marker_callback(self, msg):
        # Spawn particles and projectiles based on incoming marker commands
        # Calculate angle of projectile based on spawn position relative to robot
        dx = msg.pose.position.x - self.x
        dy = msg.pose.position.y - self.y
        angle = math.atan2(dy, dx)
        
        # If it is a special attack, speed and colors are slightly different
        is_special = (msg.ns == 'special_attack')
        speed = 6.0 if not is_special else 4.0
        
        color = (
            int(msg.color.r * 255),
            int(msg.color.g * 255),
            int(msg.color.b * 255)
        )
        
        self.projectiles.append({
            'id': msg.id,
            'x': msg.pose.position.x,
            'y': msg.pose.position.y,
            'vx': speed * math.cos(angle),
            'vy': speed * math.sin(angle),
            'color': color,
            'lifetime': float(msg.lifetime.sec) if msg.lifetime.sec > 0 else 2.0,
            'radius': int(msg.scale.x * 100.0) if msg.scale.x > 0 else 5,
            'trail_timer': 0.0
        })
        
        # Spawn flash particles at the tip of the barrel / spawn position
        self.spawn_flash_particles(msg.pose.position.x, msg.pose.position.y, angle, color)

    def spawn_exhaust_particles(self):
        # Position of exhaust at rear of robot
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
                'decay': 350.0,  # Alpha decay per second
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
        # Convert world coordinates (meters) to screen coordinates (pixels)
        # In ROS, Y is up, but in Pygame Y is down.
        px = self.cx + int(x * self.scale)
        py = self.cy - int(y * self.scale)
        return px, py

    def to_world(self, px, py):
        # Convert screen coordinates to world coordinates
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
        # Construct and publish RobotCombatCommand message
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
            # Process ROS 2 node events
            rclpy.spin_once(self, timeout_sec=0.001)
            
            # Delta time in seconds
            dt = self.clock.tick(60) / 1000.0
            
            # Update timers
            if self.shield_timer > 0.0:
                self.shield_timer = max(0.0, self.shield_timer - dt)
            
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
                    if event.button == 1:  # Left Click to Shoot
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
            
            # Publish movement command periodically
            now = self.get_clock().now()
            time_since_last_cmd = (now - self.last_command_time).nanoseconds / 1e9
            
            if (linear != self.last_linear or angular != self.last_angular or 
                time_since_last_cmd >= self.command_publish_interval):
                self.publish_combat_command(linear=linear, angular=angular)
                self.last_linear = linear
                self.last_angular = angular
                self.last_command_time = now

            # --- Update Projectiles ---
            for p in self.projectiles[:]:
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['lifetime'] -= dt
                p['trail_timer'] += dt
                
                # Check for boundary collision
                dist = math.sqrt(p['x']**2 + p['y']**2)
                if dist >= 3.5 or p['lifetime'] <= 0.0:
                    # Spawn impact sparks at the boundary edge
                    impact_angle = math.atan2(p['y'], p['x'])
                    ix = 3.5 * math.cos(impact_angle)
                    iy = 3.5 * math.sin(impact_angle)
                    self.spawn_impact_particles(ix, iy, p['color'])
                    self.projectiles.remove(p)
                    continue
                
                # Projectile particles (trail effect)
                if p['trail_timer'] >= 0.04:
                    p['trail_timer'] = 0.0
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

            # --- Update Particles ---
            for p in self.particles[:]:
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['alpha'] -= p['decay'] * dt
                p['radius'] = max(1.0, p['radius'] - p['size_decay'] * dt)
                if p['alpha'] <= 0.0:
                    self.particles.remove(p)

            # --- Rendering Phase ---
            self.screen.fill((8, 8, 16))  # Cyber dark blue background
            
            # Create alpha surfaces for transparency effects
            alpha_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            
            # 1. Draw Grid Lines inside the Arena
            grid_interval = 0.5  # 0.5 meters
            for i in range(-7, 8):
                # Vertical grid lines
                gx = i * grid_interval
                sp_x, sp_y_top = self.to_screen(gx, 3.5)
                _, sp_y_bot = self.to_screen(gx, -3.5)
                # Clip lines to the circular boundary
                pygame.draw.line(alpha_surface, (24, 24, 48, 120), (sp_x, sp_y_top), (sp_x, sp_y_bot), 1)
                
                # Horizontal grid lines
                gy = i * grid_interval
                sp_x_left, sp_y = self.to_screen(-3.5, gy)
                sp_x_right, _ = self.to_screen(3.5, gy)
                pygame.draw.line(alpha_surface, (24, 24, 48, 120), (sp_x_left, sp_y), (sp_x_right, sp_y), 1)
            
            # 2. Draw Arena Boundary
            apx, apy = self.to_screen(0, 0)
            arena_pixel_radius = int(3.5 * self.scale)
            # Glowing outer ring
            pygame.draw.circle(alpha_surface, (255, 60, 0, 50), (apx, apy), arena_pixel_radius + 5, 4)
            pygame.draw.circle(self.screen, (255, 50, 0), (apx, apy), arena_pixel_radius, 4)
            
            # Blit early alpha elements (grid lines, glows)
            self.screen.blit(alpha_surface, (0, 0))
            
            # 3. Draw Particles
            particle_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            for p in self.particles:
                px, py = self.to_screen(p['x'], p['y'])
                # Safe clamp colors and alpha
                color = (p['color'][0], p['color'][1], p['color'][2], max(0, min(255, int(p['alpha']))))
                pygame.draw.circle(particle_surface, color, (px, py), int(p['radius']))
            self.screen.blit(particle_surface, (0, 0))

            # 4. Draw Projectiles
            for p in self.projectiles:
                px, py = self.to_screen(p['x'], p['y'])
                # Glow effect
                pygame.draw.circle(self.screen, (min(255, p['color'][0] + 50), min(255, p['color'][1] + 50), min(255, p['color'][2] + 50)), (px, py), p['radius'] + 2)
                pygame.draw.circle(self.screen, p['color'], (px, py), p['radius'])

            # 5. Draw Robot Chassis & Turret
            robot_px, robot_py = self.to_screen(self.x, self.y)
            
            # --- Base/Chassis Drawing Surface ---
            # Dimensions: 0.4 x 0.3 meters -> 40 x 30 pixels. Surface needs padding for rotation: 80x80.
            chassis_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            
            # Left Wheel (Dark Grey rect)
            pygame.draw.rect(chassis_surf, (40, 40, 40), (22, 10, 16, 4))
            pygame.draw.rect(chassis_surf, (0, 0, 0), (22, 10, 16, 4), 1)
            # Right Wheel
            pygame.draw.rect(chassis_surf, (40, 40, 40), (22, 66, 16, 4))
            pygame.draw.rect(chassis_surf, (0, 0, 0), (22, 66, 16, 4), 1)
            
            # Casters
            pygame.draw.circle(chassis_surf, (120, 120, 120), (58, 40), 3) # Front
            pygame.draw.circle(chassis_surf, (120, 120, 120), (22, 40), 3) # Rear
            
            # Chassis Box (0.4m x 0.3m -> 40px x 30px)
            pygame.draw.rect(chassis_surf, (0, 102, 204), (20, 25, 40, 30)) # Main body
            pygame.draw.rect(chassis_surf, (0, 246, 255), (20, 25, 40, 30), 2) # Neon border
            
            # Top Cover plate
            pygame.draw.rect(chassis_surf, (70, 70, 70), (22, 27, 36, 26))
            pygame.draw.rect(chassis_surf, (150, 150, 150), (22, 27, 36, 26), 1)
            
            # Rotate chassis surface.
            # Convert theta to degrees. In ROS, CCW is positive, in Pygame CCW is positive,
            # but because Y screen coordinate is inverted, a positive rotation in ROS coordinates
            # corresponds to a counter-clockwise screen rotation.
            rotated_chassis = pygame.transform.rotate(chassis_surf, math.degrees(self.theta))
            chassis_rect = rotated_chassis.get_rect(center=(robot_px, robot_py))
            self.screen.blit(rotated_chassis, chassis_rect)

            # --- Turret & Gun Surface ---
            turret_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            # Barrel: 0.15m -> 15px long. Starts from center (40, 40)
            pygame.draw.rect(turret_surf, (60, 60, 60), (40, 38, 15, 4))
            pygame.draw.rect(turret_surf, (0, 0, 0), (40, 38, 15, 4), 1)
            # Turret core: radius 0.06m -> 6px, let's use 10px for look
            pygame.draw.circle(turret_surf, (204, 0, 0), (40, 40), 10)
            pygame.draw.circle(turret_surf, (255, 51, 51), (40, 40), 10, 2)
            
            # Rotate turret absolute: theta + turret_angle
            absolute_turret_angle = self.theta + self.turret_angle
            rotated_turret = pygame.transform.rotate(turret_surf, math.degrees(absolute_turret_angle))
            turret_rect = rotated_turret.get_rect(center=(robot_px, robot_py))
            self.screen.blit(rotated_turret, turret_rect)

            # 6. Draw Robot Shield (Semi-transparent pulsing Cyan circle)
            if self.shield_timer > 0.0:
                shield_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                pulse_val = abs(math.sin(pygame.time.get_ticks() * 0.01))
                alpha = int(80 + pulse_val * 60)
                # Shield bubble radius 0.35m -> 35px
                pygame.draw.circle(shield_surface, (0, 255, 255, alpha), (robot_px, robot_py), 35, 3)
                pygame.draw.circle(shield_surface, (0, 255, 255, alpha // 4), (robot_px, robot_py), 32)
                self.screen.blit(shield_surface, (0, 0))

            # 7. Draw HUD (Glassmorphism dashboard style)
            hud_surface = pygame.Surface((230, 110), pygame.SRCALPHA)
            # Glass body
            pygame.draw.rect(hud_surface, (0, 0, 10, 180), (0, 0, 230, 110), border_radius=8)
            pygame.draw.rect(hud_surface, (0, 246, 255, 120), (0, 0, 230, 110), 2, border_radius=8)
            
            # Render labels
            label_title = self.font_title.render("COMBAT ROBOT HUD", True, (0, 246, 255))
            hud_surface.blit(label_title, (15, 10))
            
            txt_pos = f"Pos: X: {self.x:.2f}m | Y: {self.y:.2f}m"
            txt_head = f"Heading: {math.degrees(self.theta):.1f}°"
            txt_turret = f"Turret Joint: {math.degrees(self.turret_angle):.1f}°"
            
            label_pos = self.font_hud.render(txt_pos, True, (220, 220, 220))
            label_head = self.font_hud.render(txt_head, True, (220, 220, 220))
            label_turret = self.font_hud.render(txt_turret, True, (220, 220, 220))
            
            hud_surface.blit(label_pos, (15, 35))
            hud_surface.blit(label_head, (15, 55))
            hud_surface.blit(label_turret, (15, 75))
            
            self.screen.blit(hud_surface, (20, 20))
            
            # 8. Draw Keybinds and Weapons status HUD
            weapon_hud = pygame.Surface((230, 95), pygame.SRCALPHA)
            pygame.draw.rect(weapon_hud, (0, 0, 10, 180), (0, 0, 230, 95), border_radius=8)
            pygame.draw.rect(weapon_hud, (255, 100, 0, 120), (0, 0, 230, 95), 2, border_radius=8)
            
            label_w_title = self.font_title.render("SYSTEM STATUS", True, (255, 120, 0))
            weapon_hud.blit(label_w_title, (15, 10))
            
            shield_status = "ONLINE" if self.shield_timer > 0.0 else "READY"
            shield_color = (0, 255, 255) if self.shield_timer > 0.0 else (0, 255, 100)
            
            label_shield = self.font_hud.render(f"Shield Matrix: ", True, (220, 220, 220))
            label_shield_val = self.font_hud.render(shield_status, True, shield_color)
            weapon_hud.blit(label_shield, (15, 35))
            weapon_hud.blit(label_shield_val, (120, 35))
            
            label_ctrl = self.font_controls.render("ESC: Exit | Space/Click: Fire", True, (150, 150, 150))
            label_ctrl2 = self.font_controls.render("Q: Shield Matrix | E: Radial Special", True, (150, 150, 150))
            weapon_hud.blit(label_ctrl, (15, 58))
            weapon_hud.blit(label_ctrl2, (15, 75))
            
            self.screen.blit(weapon_hud, (self.screen_width - 250, 20))
            
            # Refresh screen
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
