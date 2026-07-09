#!/usr/bin/env python3
"""
Pygame drawing/rendering concerns for the client.

This is a mixin: `RenderMixin` expects `self.screen`, `self.font_*`, and the
various game-state attributes to already exist on the combined object (see
pygame_visualizer.py), so it can freely reference them.
"""

import math
import random

import pygame


class RenderMixin:
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

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def draw_button(self, text, rect, color, hover_color, text_color, is_hovered, enabled=True):
        shadow_rect = rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(self.screen, (5, 5, 12, 120), shadow_rect, border_radius=8)
        
        c = hover_color if is_hovered and enabled else color
        if not enabled:
            c = (60, 60, 70)
            
        pygame.draw.rect(self.screen, c, rect, border_radius=8)
        border_c = (min(255, c[0] + 50), min(255, c[1] + 50), min(255, c[2] + 50))
        pygame.draw.rect(self.screen, border_c, rect, width=2, border_radius=8)
        
        txt_surf = self.font_menu_button.render(text, True, text_color if enabled else (140, 140, 145))
        txt_rect = txt_surf.get_rect(center=rect.center)
        self.screen.blit(txt_surf, txt_rect)

    def draw_input_box(self, label, value, rect, is_active):
        lbl_surf = self.font_menu_label.render(label, True, (0, 246, 255))
        self.screen.blit(lbl_surf, (rect.x, rect.y - 22))
        
        bg_color = (16, 16, 36) if is_active else (10, 10, 22)
        border_color = (0, 246, 255) if is_active else (80, 80, 100)
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=6)
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=6)
        
        txt_surf = self.font_menu_button.render(value, True, (255, 255, 255))
        self.screen.blit(txt_surf, (rect.x + 12, rect.y + (rect.height - txt_surf.get_height()) // 2))

    def render_menu(self):
        self.screen.fill((8, 8, 16))
        
        # Cyber grid in background
        grid_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for i in range(0, self.screen_width, 40):
            pygame.draw.line(grid_surface, (20, 20, 40, 60), (i, 0), (i, self.screen_height), 1)
            pygame.draw.line(grid_surface, (20, 20, 40, 60), (0, i), (self.screen_width, i), 1)
        self.screen.blit(grid_surface, (0, 0))
        
        # Title text
        lbl_title = self.font_menu_title.render("ARENA BATTLE", True, (0, 246, 255))
        lbl_subtitle = self.font_menu_subtitle.render("NEON COMBAT", True, (255, 0, 255))
        
        self.screen.blit(lbl_title, lbl_title.get_rect(center=(self.screen_width // 2, 90)))
        self.screen.blit(lbl_subtitle, lbl_subtitle.get_rect(center=(self.screen_width // 2, 140)))
        
        # Name input box
        input_rect = pygame.Rect(self.screen_width // 2 - 150, 240, 300, 45)
        self.draw_input_box("ENTER PILOT NAME:", self.player_name, input_rect, self.name_input_active)
        
        # Buttons
        mx, my = self.get_mouse_pos()
        
        btn_local = pygame.Rect(self.screen_width // 2 - 150, 320, 300, 45)
        btn_host = pygame.Rect(self.screen_width // 2 - 150, 385, 300, 45)
        btn_join = pygame.Rect(self.screen_width // 2 - 150, 450, 300, 45)
        btn_exit = pygame.Rect(self.screen_width // 2 - 150, 515, 300, 45)
        
        self.draw_button("LOCAL MATCH (1 LAPTOP)", btn_local, (10, 45, 80), (15, 70, 120), (255, 255, 255), btn_local.collidepoint(mx, my))
        self.draw_button("HOST LAN LOBBY", btn_host, (10, 80, 45), (15, 120, 70), (255, 255, 255), btn_host.collidepoint(mx, my))
        if self.server_check_failed_timer > 0.0:
            self.draw_button("NO SERVER DETECTED!", btn_join, (150, 20, 20), (180, 30, 30), (255, 255, 255), btn_join.collidepoint(mx, my))
        else:
            self.draw_button("JOIN LAN LOBBY", btn_join, (80, 10, 80), (120, 15, 120), (255, 255, 255), btn_join.collidepoint(mx, my))
        self.draw_button("EXIT SIMULATION", btn_exit, (80, 15, 15), (120, 20, 20), (255, 255, 255), btn_exit.collidepoint(mx, my))

        # Active ROS_DOMAIN_ID display
        import os
        domain_id = os.environ.get('ROS_DOMAIN_ID', '0')
        lbl_domain = self.font_menu_label.render(f"Network Domain ID (ROS_DOMAIN_ID): {domain_id}", True, (120, 120, 140))
        self.screen.blit(lbl_domain, lbl_domain.get_rect(center=(self.screen_width // 2, self.screen_height - 30)))

    def render_lobby_host(self):
        self.screen.fill((8, 8, 16))
        
        lbl_title = self.font_menu_title.render("LOBBY INTERFACE", True, (0, 246, 255))
        self.screen.blit(lbl_title, lbl_title.get_rect(center=(self.screen_width // 2, 90)))
        
        # Lobby state card
        card_rect = pygame.Rect(self.screen_width // 2 - 200, 180, 400, 260)
        pygame.draw.rect(self.screen, (15, 15, 32), card_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 246, 255), card_rect, width=2, border_radius=12)
        
        # Render contents inside card
        lbl_host_title = self.font_menu_subtitle.render("HOST", True, (0, 246, 255))
        lbl_host_name = self.font_menu_button.render(self.player_name, True, (255, 255, 255))
        
        lbl_guest_title = self.font_menu_subtitle.render("GUEST", True, (255, 0, 255))
        gname = self.lobby_data.get("player2_name", "")
        if not gname:
            pulse_val = abs(math.sin(pygame.time.get_ticks() * 0.005))
            guest_color = (int(100 + pulse_val * 80), int(100 + pulse_val * 80), int(120 + pulse_val * 80))
            lbl_guest_name = self.font_menu_button.render("WAITING FOR PLAYER...", True, guest_color)
        else:
            lbl_guest_name = self.font_menu_button.render(gname, True, (255, 255, 255))
            
        self.screen.blit(lbl_host_title, (self.screen_width // 2 - 170, 210))
        self.screen.blit(lbl_host_name, (self.screen_width // 2 - 170, 245))
        
        pygame.draw.line(self.screen, (30, 30, 60), (self.screen_width // 2 - 170, 300), (self.screen_width // 2 + 170, 300), 1)
        
        self.screen.blit(lbl_guest_title, (self.screen_width // 2 - 170, 320))
        self.screen.blit(lbl_guest_name, (self.screen_width // 2 - 170, 355))
        
        # Buttons
        mx, my = self.get_mouse_pos()
        btn_start = pygame.Rect(self.screen_width // 2 - 150, 480, 300, 45)
        btn_back = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
        
        has_guest = bool(gname)
        self.draw_button("START MATCH", btn_start, (10, 80, 45), (15, 120, 70), (255, 255, 255), btn_start.collidepoint(mx, my), enabled=has_guest)
        self.draw_button("BACK TO MENU", btn_back, (80, 15, 15), (120, 20, 20), (255, 255, 255), btn_back.collidepoint(mx, my))

    def render_lobby_join(self):
        self.screen.fill((8, 8, 16))
        
        lbl_title = self.font_menu_title.render("DISCOVER LOBBIES", True, (255, 0, 255))
        self.screen.blit(lbl_title, lbl_title.get_rect(center=(self.screen_width // 2, 90)))
        
        # Box background
        list_rect = pygame.Rect(self.screen_width // 2 - 250, 180, 500, 320)
        pygame.draw.rect(self.screen, (15, 15, 32), list_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 0, 255), list_rect, width=2, border_radius=12)
        
        lobbies = list(self.active_lobbies.values())
        if not lobbies:
            # Draw Scanning...
            pulse_val = abs(math.sin(pygame.time.get_ticks() * 0.005))
            txt_c = (int(100 + pulse_val * 80), int(100 + pulse_val * 80), int(255))
            lbl = self.font_hud.render("Scanning local network for active lobbies...", True, txt_c)
            self.screen.blit(lbl, lbl.get_rect(center=list_rect.center))
        else:
            for idx, (lobby, _) in enumerate(lobbies[:5]):
                row_y = 200 + idx * 60
                pygame.draw.rect(self.screen, (25, 25, 48), (self.screen_width // 2 - 230, row_y, 460, 50), border_radius=6)
                
                host_lbl = self.font_menu_button.render(lobby["host_name"], True, (255, 255, 255))
                self.screen.blit(host_lbl, (self.screen_width // 2 - 210, row_y + 13))
                
                status_str = "READY" if lobby['status'] == 'ready' else "WAITING"
                status_lbl = self.font_hud.render(f"Status: {status_str}", True, (0, 255, 100) if lobby['status'] == 'waiting' else (255, 255, 100))
                self.screen.blit(status_lbl, (self.screen_width // 2 - 10, row_y + 16))
                
                # Join button
                join_btn_rect = pygame.Rect(self.screen_width // 2 + 120, row_y + 8, 90, 34)
                mx, my = self.get_mouse_pos()
                is_hovered = join_btn_rect.collidepoint(mx, my)
                is_full = (lobby['status'] != 'waiting')
                btn_color = (120, 10, 120) if is_hovered and not is_full else (80, 0, 80)
                if is_full:
                    btn_color = (50, 50, 50)
                pygame.draw.rect(self.screen, btn_color, join_btn_rect, border_radius=6)
                pygame.draw.rect(self.screen, (255, 100, 255), join_btn_rect, width=1, border_radius=6)
                btn_txt = self.font_hud.render("FULL" if is_full else "JOIN", True, (200, 200, 200) if is_full else (255, 255, 255))
                self.screen.blit(btn_txt, btn_txt.get_rect(center=join_btn_rect.center))
                
        # Back button
        mx, my = self.get_mouse_pos()
        btn_back = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
        self.draw_button("BACK TO MENU", btn_back, (80, 15, 15), (120, 20, 20), (255, 255, 255), btn_back.collidepoint(mx, my))

    def render_lobby_guest(self):
        self.screen.fill((8, 8, 16))
        
        lbl_title = self.font_menu_title.render("JOINED LOBBY", True, (255, 0, 255))
        self.screen.blit(lbl_title, lbl_title.get_rect(center=(self.screen_width // 2, 90)))
        
        card_rect = pygame.Rect(self.screen_width // 2 - 200, 180, 400, 260)
        pygame.draw.rect(self.screen, (15, 15, 32), card_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 0, 255), card_rect, width=2, border_radius=12)
        
        hname = self.lobby_data.get("player1_name", "Host")
        lbl_host_title = self.font_menu_subtitle.render("HOST", True, (0, 246, 255))
        lbl_host_name = self.font_menu_button.render(hname, True, (255, 255, 255))
        
        lbl_guest_title = self.font_menu_subtitle.render("GUEST (YOU)", True, (255, 0, 255))
        lbl_guest_name = self.font_menu_button.render(self.player_name, True, (255, 255, 255))
        
        self.screen.blit(lbl_host_title, (self.screen_width // 2 - 170, 210))
        self.screen.blit(lbl_host_name, (self.screen_width // 2 - 170, 245))
        
        pygame.draw.line(self.screen, (30, 30, 60), (self.screen_width // 2 - 170, 300), (self.screen_width // 2 + 170, 300), 1)
        
        self.screen.blit(lbl_guest_title, (self.screen_width // 2 - 170, 320))
        self.screen.blit(lbl_guest_name, (self.screen_width // 2 - 170, 355))
        
        # Pulsing status
        pulse_val = abs(math.sin(pygame.time.get_ticks() * 0.005))
        lbl_status = self.font_menu_subtitle.render("WAITING FOR HOST TO START MATCH...", True, (int(100 + pulse_val * 120), 255, int(100 + pulse_val * 120)))
        self.screen.blit(lbl_status, lbl_status.get_rect(center=(self.screen_width // 2, 480)))
        
        # Button
        mx, my = self.get_mouse_pos()
        btn_leave = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
        self.draw_button("LEAVE LOBBY", btn_leave, (80, 15, 15), (120, 20, 20), (255, 255, 255), btn_leave.collidepoint(mx, my))

    def render_gameplay(self, dt):
        # 1. Background Cyber navy fill
        self.screen.fill((8, 8, 16))
        
        alpha_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw Grid Lines
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
            rturret = self.p1_turret_angle_received if pid == 1 else self.p2_turret_angle_received
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
            
            # Chassis Box
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
        p1_border = (0, 246, 255, 220) if not self.is_network or self.player_id == 1 else (80, 80, 100, 120)
        pygame.draw.rect(hud_p1, (0, 0, 10, 180), (0, 0, 230, 140), border_radius=8)
        pygame.draw.rect(hud_p1, p1_border, (0, 0, 230, 140), 2, border_radius=8)
        
        p1_title_text = "PLAYER 1"
        if not self.is_network:
            p1_title_text += " (LOCAL P1)"
        elif self.player_id == 1:
            p1_title_text += " (LOCAL)"
        else:
            p1_title_text += " (ENEMY)"
            
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
        p2_border = (255, 0, 255, 220) if not self.is_network or self.player_id == 2 else (80, 80, 100, 120)
        pygame.draw.rect(hud_p2, (0, 0, 10, 180), (0, 0, 230, 140), border_radius=8)
        pygame.draw.rect(hud_p2, p2_border, (0, 0, 230, 140), 2, border_radius=8)
        
        p2_title_text = "PLAYER 2"
        if not self.is_network:
            p2_title_text += " (LOCAL P2)"
        elif self.player_id == 2:
            p2_title_text += " (LOCAL)"
        else:
            p2_title_text += " (ENEMY)"
            
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
        # If paused, render pause UI on top
        if self.paused:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            self.screen.blit(overlay, (0,0))

            # Modal with buttons for BOTH players
            modal = pygame.Rect(self.screen_width//2 - 200, self.screen_height//2 - 80, 400, 160)
            pygame.draw.rect(self.screen, (18,18,30), modal, border_radius=8)
            pygame.draw.rect(self.screen, (200,200,200), modal, width=2, border_radius=8)
 
            lbl = self.font_menu_title.render("GAME PAUSED", True, (255,255,255))
            self.screen.blit(lbl, lbl.get_rect(center=(self.screen_width//2, self.screen_height//2 - 30)))
 
            prompt = self.font_menu_button.render("Leaving the match?", True, (200,200,200))
            self.screen.blit(prompt, prompt.get_rect(center=(self.screen_width//2, self.screen_height//2 + 0)))
 
            # Buttons
            btn_no = pygame.Rect(self.screen_width//2 - 140, self.screen_height//2 + 40, 120, 36)
            btn_yes = pygame.Rect(self.screen_width//2 + 20, self.screen_height//2 + 40, 120, 36)
 
            mx, my = self.get_mouse_pos()
            self.draw_button("NO", btn_no, (30,120,60), (40,160,80), (255,255,255), btn_no.collidepoint(mx,my))
            self.draw_button("YES", btn_yes, (120,20,20), (160,40,40), (255,255,255), btn_yes.collidepoint(mx,my))
 
            # Expose modal button rects for main loop click handling
            self._pause_btn_no = btn_no
            self._pause_btn_yes = btn_yes
        ctrl_surf = pygame.Surface((560, 30), pygame.SRCALPHA)
        pygame.draw.rect(ctrl_surf, (0, 0, 10, 180), (0, 0, 560, 30), border_radius=5)
        pygame.draw.rect(ctrl_surf, (150, 150, 150, 100), (0, 0, 560, 30), 1, border_radius=5)
        
        # Generate context-aware description
        if not self.is_network:
            help_str = "P1: WASD, Space (Shoot), Q (Shield), E (Special), J/L (Aim) | P2: Arrows, Enter, R-Ctrl, R-Shift, [ / ]"
        elif self.player_id == 1:
            help_str = "P1 Local Controls: WASD to Move, J/L to Aim Turret, Space to Shoot, Q: Shield, E: Special. ESC: Quit"
        else:
            help_str = "P2 Local Controls: WASD to Move, J/L to Aim Turret, Space to Shoot, Q: Shield, E: Special. ESC: Quit"
            
        label_ctrl = self.font_controls.render(help_str, True, (200, 200, 200))
        ctrl_surf.blit(label_ctrl, (label_ctrl.get_rect(center=(280, 15))))
        self.screen.blit(ctrl_surf, (self.screen_width // 2 - 280, self.screen_height - 50))
        
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
            lbl_sub = self.font_hud.render("Press ESC to return to Menu / Lobby", True, (200, 200, 200))
            
            go_surf.blit(lbl_go, (140, 30))
            go_surf.blit(lbl_win, (110, 80))
            go_surf.blit(lbl_sub, (100, 140))
            
            self.screen.blit(go_surf, (self.screen_width // 2 - 200, self.screen_height // 2 - 100))

