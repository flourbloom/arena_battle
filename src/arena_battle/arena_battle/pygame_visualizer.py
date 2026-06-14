#!/usr/bin/env python3

import sys
import math
import random
import pygame
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import GameState, RobotState

class PygameVisualizer(Node):
    def __init__(self):
        super().__init__('pygame_visualizer')
        
        # Declare player_id parameter so the visualizer window knows if it represents Player 1 or Player 2 local HUD
        self.declare_parameter('player_id', 1)
        self.player_id = self.get_parameter('player_id').get_parameter_value().integer_value
        
        # Player 1 states
        self.p1_x = -1.5
        self.p1_y = 0.0
        self.p1_theta = 0.0
        self.p1_turret_angle = 0.0
        self.p1_health = 100
        self.p1_shield_active = False
        self.p1_shield_energy = 100.0
        self.p1_score = 0
        self.p1_ammo = 10
        
        # Player 2 states
        self.p2_x = 1.5
        self.p2_y = 0.0
        self.p2_theta = math.pi
        self.p2_turret_angle = 0.0
        self.p2_health = 100
        self.p2_shield_active = False
        self.p2_shield_energy = 100.0
        self.p2_score = 0
        self.p2_ammo = 10

        self.game_over = False
        self.time_elapsed = 0.0
        
        # Visual particles
        self.particles = []
        
        # Track active projectiles for rendering and spawning particles
        self.projectiles = []
        self.active_projectile_ids = set()
        
        # Subscription to game state (View part)
        self.state_sub = self.create_subscription(
            GameState,
            '/game_state',
            self.state_callback,
            10
        )
        
        # Initialize Pygame
        pygame.init()
        pygame.font.init()
        
        # Set up display
        self.screen_width = 800
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(f"Arena Battle - Robot Visualizer (Player {self.player_id})")
        
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
            
        self.get_logger().info(f"Pygame Visualizer Pure View (Player {self.player_id} Node) Initialized!")

    def state_callback(self, msg):
        # Update Player 1 local properties
        self.p1_x = msg.player1.x
        self.p1_y = msg.player1.y
        self.p1_theta = msg.player1.theta
        self.p1_turret_angle = msg.player1.turret_angle
        self.p1_health = msg.player1.health
        self.p1_shield_active = msg.player1.shield_active
        self.p1_shield_energy = msg.player1.shield_energy
        self.p1_score = msg.player1.score
        self.p1_ammo = msg.player1.ammo
        
        # Update Player 2 local properties
        self.p2_x = msg.player2.x
        self.p2_y = msg.player2.y
        self.p2_theta = msg.player2.theta
        self.p2_turret_angle = msg.player2.turret_angle
        self.p2_health = msg.player2.health
        self.p2_shield_active = msg.player2.shield_active
        self.p2_shield_energy = msg.player2.shield_energy
        self.p2_score = msg.player2.score
        self.p2_ammo = msg.player2.ammo
        
        self.game_over = msg.game_over
        self.time_elapsed = msg.time_elapsed
        
        # Process projectiles & spawn particles
        current_projectiles = {p.id: p for p in msg.projectiles}
        current_ids = set(current_projectiles.keys())
        
        # Spawn flash particles for newly created projectiles
        new_ids = current_ids - self.active_projectile_ids
        for pid in new_ids:
            p = current_projectiles[pid]
            # Calculate spawning direction relative to owner robot heading
            owner_x = self.p1_x if p.owner == 1 else self.p2_x
            owner_y = self.p1_y if p.owner == 1 else self.p2_y
            dx = p.x - owner_x
            dy = p.y - owner_y
            angle = math.atan2(dy, dx)
            color = (0, 246, 255) if p.owner == 1 else (255, 0, 255)
            self.spawn_flash_particles(p.x, p.y, angle, color)
            
        # Update local states for next callback
        self.active_projectile_ids = current_ids
        
        # Store current active projectiles
        self.projectiles = [
            {
                'x': p.x,
                'y': p.y,
                'type': p.type,
                'vx': p.vx,
                'vy': p.vy,
                'color': (0, 246, 255) if p.owner == 1 else (255, 0, 255),
                'radius': 5 if p.type == 0 else 4
            }
            for p in msg.projectiles
        ]

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

    def to_screen(self, x, y):
        px = self.cx + int(x * self.scale)
        py = self.cy - int(y * self.scale)
        return px, py

    def to_world(self, px, py):
        x = (px - self.cx) / self.scale
        y = (self.cy - py) / self.scale
        return x, y

    def run(self):
        running = True
        
        while running and rclpy.ok():
            # Process ROS callbacks
            rclpy.spin_once(self, timeout_sec=0.001)
            
            dt = self.clock.tick(60) / 1000.0
            
            # --- Pygame Event Handling (Pure Visualizer only exits) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

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
                
            # 5. Draw Both Robots
            for pid in [1, 2]:
                rx = self.p1_x if pid == 1 else self.p2_x
                ry = self.p1_y if pid == 1 else self.p2_y
                rtheta = self.p1_theta if pid == 1 else self.p2_theta
                rturret = self.p1_turret_angle if pid == 1 else self.p2_turret_angle
                rshield_active = self.p1_shield_active if pid == 1 else self.p2_shield_active
                
                robot_px, robot_py = self.to_screen(rx, ry)
                
                # Base/Chassis Surface
                chassis_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                # Wheels
                pygame.draw.rect(chassis_surf, (40, 40, 40), (22, 10, 16, 4))
                pygame.draw.rect(chassis_surf, (0, 0, 0), (22, 10, 16, 4), 1)
                pygame.draw.rect(chassis_surf, (40, 40, 40), (22, 66, 16, 4))
                pygame.draw.rect(chassis_surf, (0, 0, 0), (22, 66, 16, 4), 1)
                # Casters
                pygame.draw.circle(chassis_surf, (120, 120, 120), (58, 40), 3)
                pygame.draw.circle(chassis_surf, (120, 120, 120), (22, 40), 3)
                
                # Chassis Box (Player 1 has Cyan border, Player 2 has Magenta border)
                box_color = (180, 220, 255) if pid == 1 else (255, 180, 255)
                border_color = (0, 246, 255) if pid == 1 else (255, 0, 255)
                pygame.draw.rect(chassis_surf, box_color, (20, 25, 40, 30))
                pygame.draw.rect(chassis_surf, border_color, (20, 25, 40, 30), 2)
                
                # Cover plate
                pygame.draw.rect(chassis_surf, (220, 235, 250), (22, 27, 36, 26))
                pygame.draw.rect(chassis_surf, (255, 255, 255), (22, 27, 36, 26), 1)
                
                rotated_chassis = pygame.transform.rotate(chassis_surf, math.degrees(rtheta))
                chassis_rect = rotated_chassis.get_rect(center=(robot_px, robot_py))
                self.screen.blit(rotated_chassis, chassis_rect)
                
                # Turret
                turret_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.rect(turret_surf, (60, 60, 60), (40, 38, 15, 4))
                pygame.draw.rect(turret_surf, (0, 0, 0), (40, 38, 15, 4), 1)
                
                # Turret core: Player 1 red, Player 2 purple
                core_color = (204, 0, 0) if pid == 1 else (102, 0, 204)
                core_border = (255, 51, 51) if pid == 1 else (178, 102, 255)
                pygame.draw.circle(turret_surf, core_color, (40, 40), 10)
                pygame.draw.circle(turret_surf, core_border, (40, 40), 10, 2)
                
                absolute_turret_angle = rtheta + rturret
                rotated_turret = pygame.transform.rotate(turret_surf, math.degrees(absolute_turret_angle))
                turret_rect = rotated_turret.get_rect(center=(robot_px, robot_py))
                self.screen.blit(rotated_turret, turret_rect)
                
                # Draw Shield
                if rshield_active:
                    shield_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                    pulse_val = abs(math.sin(pygame.time.get_ticks() * 0.01))
                    alpha = int(80 + pulse_val * 60)
                    shield_color = (0, 255, 255, alpha) if pid == 1 else (255, 0, 255, alpha)
                    pygame.draw.circle(shield_surface, shield_color, (robot_px, robot_py), 35, 3)
                    pygame.draw.circle(shield_surface, (shield_color[0], shield_color[1], shield_color[2], alpha // 4), (robot_px, robot_py), 32)
                    self.screen.blit(shield_surface, (0, 0))
                    
            # 6. Render HUD for Player 1 (Left Dashboard)
            hud_p1 = pygame.Surface((230, 140), pygame.SRCALPHA)
            p1_border = (0, 246, 255, 220) if self.player_id == 1 else (80, 80, 100, 120)
            pygame.draw.rect(hud_p1, (0, 0, 10, 180), (0, 0, 230, 140), border_radius=8)
            pygame.draw.rect(hud_p1, p1_border, (0, 0, 230, 140), 2, border_radius=8)
            
            p1_title_text = "PLAYER 1 (LOCAL)" if self.player_id == 1 else "PLAYER 1 (ENEMY)"
            label_p1_title = self.font_title.render(p1_title_text, True, (0, 246, 255))
            hud_p1.blit(label_p1_title, (15, 8))
            
            txt_p1_pos = f"Pos: X: {self.p1_x:.2f}m | Y: {self.p1_y:.2f}m"
            txt_p1_ammo = f"Ammo: {self.p1_ammo}/10"
            txt_p1_score = f"Score: {self.p1_score}"
            shield_p1_status = "SHIELD ONLINE" if self.p1_shield_active else "SHIELD READY"
            shield_p1_color = (0, 255, 255) if self.p1_shield_active else (0, 255, 100)
            
            hud_p1.blit(self.font_hud.render(txt_p1_pos, True, (220, 220, 220)), (15, 30))
            hud_p1.blit(self.font_hud.render(txt_p1_ammo, True, (220, 220, 220)), (15, 50))
            hud_p1.blit(self.font_hud.render(txt_p1_score, True, (220, 220, 220)), (15, 70))
            hud_p1.blit(self.font_hud.render(shield_p1_status, True, shield_p1_color), (15, 90))
            
            hud_p1.blit(self.font_hud.render("HP:", True, (255, 50, 50)), (15, 115))
            pygame.draw.rect(hud_p1, (100, 20, 20), (45, 117, 100, 10))
            pygame.draw.rect(hud_p1, (255, 50, 50), (45, 117, self.p1_health, 10))
            self.screen.blit(hud_p1, (20, 20))
            
            # 7. Render HUD for Player 2 (Right Dashboard)
            hud_p2 = pygame.Surface((230, 140), pygame.SRCALPHA)
            p2_border = (255, 0, 255, 220) if self.player_id == 2 else (80, 80, 100, 120)
            pygame.draw.rect(hud_p2, (0, 0, 10, 180), (0, 0, 230, 140), border_radius=8)
            pygame.draw.rect(hud_p2, p2_border, (0, 0, 230, 140), 2, border_radius=8)
            
            p2_title_text = "PLAYER 2 (LOCAL)" if self.player_id == 2 else "PLAYER 2 (ENEMY)"
            label_p2_title = self.font_title.render(p2_title_text, True, (255, 0, 255))
            hud_p2.blit(label_p2_title, (15, 8))
            
            txt_p2_pos = f"Pos: X: {self.p2_x:.2f}m | Y: {self.p2_y:.2f}m"
            txt_p2_ammo = f"Ammo: {self.p2_ammo}/10"
            txt_p2_score = f"Score: {self.p2_score}"
            shield_p2_status = "SHIELD ONLINE" if self.p2_shield_active else "SHIELD READY"
            shield_p2_color = (255, 0, 255) if self.p2_shield_active else (0, 255, 100)
            
            hud_p2.blit(self.font_hud.render(txt_p2_pos, True, (220, 220, 220)), (15, 30))
            hud_p2.blit(self.font_hud.render(txt_p2_ammo, True, (220, 220, 220)), (15, 50))
            hud_p2.blit(self.font_hud.render(txt_p2_score, True, (220, 220, 220)), (15, 70))
            hud_p2.blit(self.font_hud.render(shield_p2_status, True, shield_p2_color), (15, 90))
            
            hud_p2.blit(self.font_hud.render("HP:", True, (255, 50, 50)), (15, 115))
            pygame.draw.rect(hud_p2, (100, 20, 20), (45, 117, 100, 10))
            pygame.draw.rect(hud_p2, (255, 50, 50), (45, 117, self.p2_health, 10))
            self.screen.blit(hud_p2, (self.screen_width - 250, 20))
            
            # 8. Render Center Timer
            timer_surf = pygame.Surface((120, 40), pygame.SRCALPHA)
            pygame.draw.rect(timer_surf, (0, 0, 10, 180), (0, 0, 120, 40), border_radius=5)
            pygame.draw.rect(timer_surf, (150, 150, 150, 100), (0, 0, 120, 40), 1, border_radius=5)
            txt_time = f"Time: {self.time_elapsed:.1f}s"
            lbl_time = self.font_hud.render(txt_time, True, (255, 255, 255))
            timer_surf.blit(lbl_time, (15, 10))
            self.screen.blit(timer_surf, (self.screen_width // 2 - 60, 20))
            
            # 9. Render Controls Help notice
            ctrl_surf = pygame.Surface((380, 30), pygame.SRCALPHA)
            pygame.draw.rect(ctrl_surf, (0, 0, 10, 180), (0, 0, 380, 30), border_radius=5)
            pygame.draw.rect(ctrl_surf, (150, 150, 150, 100), (0, 0, 380, 30), 1, border_radius=5)
            label_ctrl = self.font_controls.render("Run teleop_control node in terminal to control your robot", True, (200, 200, 200))
            ctrl_surf.blit(label_ctrl, (20, 8))
            self.screen.blit(ctrl_surf, (self.screen_width // 2 - 190, self.screen_height - 50))
            
            # 10. Render Game Over Screen
            if self.game_over:
                go_surf = pygame.Surface((400, 200), pygame.SRCALPHA)
                pygame.draw.rect(go_surf, (10, 0, 0, 220), (0, 0, 400, 200), border_radius=12)
                pygame.draw.rect(go_surf, (255, 50, 50, 200), (0, 0, 400, 200), 3, border_radius=12)
                
                if self.p1_health <= 0:
                    winner_text = "PLAYER 2 WINS!"
                    winner_color = (255, 0, 255)
                elif self.p2_health <= 0:
                    winner_text = "PLAYER 1 WINS!"
                    winner_color = (0, 246, 255)
                else:
                    winner_text = "GAME OVER"
                    winner_color = (255, 255, 255)
                    
                lbl_go = self.font_title.render("COMBAT OVER", True, (255, 50, 50))
                lbl_win = self.font_title.render(winner_text, True, winner_color)
                lbl_sub = self.font_hud.render("Restart simulation in terminal", True, (200, 200, 200))
                
                go_surf.blit(lbl_go, (140, 30))
                go_surf.blit(lbl_win, (110, 80))
                go_surf.blit(lbl_sub, (120, 140))
                
                self.screen.blit(go_surf, (self.screen_width // 2 - 200, self.screen_height // 2 - 100))
                
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
