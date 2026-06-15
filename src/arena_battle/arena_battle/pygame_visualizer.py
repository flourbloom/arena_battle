#!/usr/bin/env python3

import sys
import math
import random
import time
import json
import subprocess
import pygame
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import GameState, RobotState, RobotCombatCommand
from std_msgs.msg import String

class PygameVisualizer(Node):
    def __init__(self):
        super().__init__('pygame_visualizer')
        
        # Declare player_id parameter just in case
        self.declare_parameter('player_id', 1)
        self.player_id = self.get_parameter('player_id').get_parameter_value().integer_value
        
        # GUI State
        self.state = "MENU" # MENU, LOBBY_HOST, LOBBY_JOIN, LOBBY_GUEST, GAMEPLAY
        self.player_name = "Player_" + str(random.randint(1000, 9999))
        self.name_input_active = False
        self.is_network = False
        self.host_id = "node_" + str(random.randint(1000, 9999))
        self.active_lobbies = {}
        self.selected_lobby_id = None
        self.lobby_data = {}
        self.server_process = None
        
        # Keyboard Control States (P1)
        self.p1_linear = 0.0
        self.p1_angular = 0.0
        self.p1_turret_angle = 0.0
        self.p1_shoot = False
        self.p1_shield = False
        self.p1_weapon_type = 0
        
        # Keyboard Control States (P2)
        self.p2_linear = 0.0
        self.p2_angular = 0.0
        self.p2_turret_angle = 0.0
        self.p2_shoot = False
        self.p2_shield = False
        self.p2_weapon_type = 0
        
        # Player 1 Game States (received from server)
        self.p1_x = -1.5
        self.p1_y = 0.0
        self.p1_theta = 0.0
        self.p1_turret_angle_received = 0.0
        self.p1_health = 100
        self.p1_shield_active = False
        self.p1_shield_energy = 100.0
        self.p1_score = 0
        self.p1_ammo = 10
        
        # Player 2 Game States (received from server)
        self.p2_x = 1.5
        self.p2_y = 0.0
        self.p2_theta = math.pi
        self.p2_turret_angle_received = 0.0
        self.p2_health = 100
        self.p2_shield_active = False
        self.p2_shield_energy = 100.0
        self.p2_score = 0
        self.p2_ammo = 10

        self.game_over = False
        self.time_elapsed = 0.0
        
        # Particles & projectiles
        self.particles = []
        self.projectiles = []
        self.active_projectile_ids = set()
        
        # ROS 2 Subscriptions and Publishers
        self.state_sub = self.create_subscription(
            GameState,
            '/game_state',
            self.state_callback,
            10
        )
        
        self.lobby_pub = self.create_publisher(String, '/lobby_advertisement', 10)
        self.lobby_sub = self.create_subscription(String, '/lobby_advertisement', self.lobby_ad_callback, 10)
        
        self.join_pub = self.create_publisher(String, '/lobby_join_request', 10)
        self.join_sub = self.create_subscription(String, '/lobby_join_request', self.lobby_join_callback, 10)
        
        self.p1_cmd_pub = self.create_publisher(RobotCombatCommand, '/p1/robot_command', 10)
        self.p2_cmd_pub = self.create_publisher(RobotCombatCommand, '/p2/robot_command', 10)
        
        # Timers
        self.cmd_timer = self.create_timer(0.05, self.publish_commands) # 20Hz
        self.lobby_timer = self.create_timer(1.0, self.publish_lobby_advertisement) # 1Hz
        
        # Initialize Pygame
        pygame.init()
        pygame.font.init()
        
        # Set up display
        self.screen_width = 800
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Arena Battle - Neon Combat")
        
        # Coordinates mapping: 1 meter = 100 pixels
        self.scale = 100.0
        self.cx = self.screen_width // 2
        self.cy = self.screen_height // 2
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            self.font_menu_title = pygame.font.SysFont("Outfit", 38, bold=True)
            self.font_menu_subtitle = pygame.font.SysFont("Outfit", 22, bold=True)
            self.font_menu_button = pygame.font.SysFont("Outfit", 18, bold=True)
            self.font_menu_label = pygame.font.SysFont("Outfit", 15)
            self.font_title = pygame.font.SysFont("Outfit", 18, bold=True)
            self.font_hud = pygame.font.SysFont("Outfit", 14)
            self.font_controls = pygame.font.SysFont("Outfit", 12)
        except Exception:
            self.font_menu_title = pygame.font.Font(None, 46)
            self.font_menu_subtitle = pygame.font.Font(None, 26)
            self.font_menu_button = pygame.font.Font(None, 22)
            self.font_menu_label = pygame.font.Font(None, 18)
            self.font_title = pygame.font.Font(None, 22)
            self.font_hud = pygame.font.Font(None, 18)
            self.font_controls = pygame.font.Font(None, 16)
            
        self.get_logger().info("Pygame Unified Client Initialized!")

    def start_game_server(self):
        self.stop_game_server()
        self.get_logger().info("Spawning Local Game Logic Server...")
        try:
            self.server_process = subprocess.Popen(
                ["ros2", "run", "arena_battle", "game_logic"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            self.get_logger().error(f"Failed to start local server process: {e}")

    def stop_game_server(self):
        if self.server_process is not None:
            self.get_logger().info("Terminating Local Game Logic Server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None

    def publish_lobby_advertisement(self):
        if self.state not in ["LOBBY_HOST", "GAMEPLAY"] or not self.is_network:
            return
            
        lobby_info = {
            "host_id": self.host_id,
            "host_name": f"{self.player_name}'s Arena",
            "player1_name": self.player_name,
            "player2_name": self.lobby_data.get("player2_name", ""),
            "status": "playing" if self.state == "GAMEPLAY" else self.lobby_data.get("status", "waiting")
        }
        
        msg = String()
        msg.data = json.dumps(lobby_info)
        self.lobby_pub.publish(msg)

    def lobby_ad_callback(self, msg):
        try:
            data = json.loads(msg.data)
            hid = data.get("host_id", "")
            if not hid or hid == self.host_id:
                return
                
            self.active_lobbies[hid] = (data, time.time())
            
            if self.state == "LOBBY_GUEST" and self.selected_lobby_id == hid:
                self.lobby_data = data
                if data.get("status") == "playing":
                    self.get_logger().info("Lobby status changed to playing! Entering game...")
                    self.state = "GAMEPLAY"
        except Exception:
            pass

    def lobby_join_callback(self, msg):
        if self.state != "LOBBY_HOST":
            return
            
        try:
            data = json.loads(msg.data)
            target_host_id = data.get("host_id", "")
            if target_host_id == self.host_id:
                guest_name = data.get("guest_name", "")
                guest_id = data.get("guest_id", "")
                
                if guest_name == "":
                    # Leave request
                    if self.lobby_data.get("player2_id") == guest_id:
                        self.lobby_data["player2_name"] = ""
                        self.lobby_data["player2_id"] = ""
                        self.lobby_data["status"] = "waiting"
                        self.get_logger().info("Guest left the lobby.")
                        self.publish_lobby_advertisement()
                else:
                    # Join request
                    self.lobby_data["player2_name"] = guest_name
                    self.lobby_data["player2_id"] = guest_id
                    self.lobby_data["status"] = "ready"
                    self.get_logger().info(f"Guest '{guest_name}' joined.")
                    self.publish_lobby_advertisement()
        except Exception:
            pass

    def request_join_lobby(self, host_id):
        self.selected_lobby_id = host_id
        self.state = "LOBBY_GUEST"
        
        req = {
            "host_id": host_id,
            "guest_name": self.player_name,
            "guest_id": self.host_id
        }
        msg = String()
        msg.data = json.dumps(req)
        self.join_pub.publish(msg)

    def leave_lobby(self):
        if self.selected_lobby_id:
            req = {
                "host_id": self.selected_lobby_id,
                "guest_name": "",
                "guest_id": self.host_id
            }
            msg = String()
            msg.data = json.dumps(req)
            self.join_pub.publish(msg)
            
        self.state = "LOBBY_JOIN"
        self.selected_lobby_id = None
        self.lobby_data = {}

    def publish_commands(self):
        if self.state != "GAMEPLAY":
            return
            
        # P1 / Host local publish
        if not self.is_network or self.player_id == 1:
            msg = RobotCombatCommand()
            msg.linear_velocity = float(self.p1_linear)
            msg.angular_velocity = float(self.p1_angular)
            msg.turret_angle = float(self.p1_turret_angle)
            msg.shoot = bool(self.p1_shoot)
            msg.shield = bool(self.p1_shield)
            msg.weapon_type = int(self.p1_weapon_type)
            self.p1_cmd_pub.publish(msg)
            
            # Reset triggers
            self.p1_shoot = False
            self.p1_shield = False
            self.p1_weapon_type = 0
            
        # P2 / Guest local publish
        if not self.is_network or self.player_id == 2:
            msg = RobotCombatCommand()
            msg.linear_velocity = float(self.p2_linear)
            msg.angular_velocity = float(self.p2_angular)
            msg.turret_angle = float(self.p2_turret_angle)
            msg.shoot = bool(self.p2_shoot)
            msg.shield = bool(self.p2_shield)
            msg.weapon_type = int(self.p2_weapon_type)
            self.p2_cmd_pub.publish(msg)
            
            # Reset triggers
            self.p2_shoot = False
            self.p2_shield = False
            self.p2_weapon_type = 0

    def clean_active_lobbies(self):
        now = time.time()
        for hid in list(self.active_lobbies.keys()):
            if now - self.active_lobbies[hid][1] > 3.0:
                del self.active_lobbies[hid]

    def state_callback(self, msg):
        # Update Player 1 properties
        self.p1_x = msg.player1.x
        self.p1_y = msg.player1.y
        self.p1_theta = msg.player1.theta
        self.p1_turret_angle_received = msg.player1.turret_angle
        self.p1_health = msg.player1.health
        self.p1_shield_active = msg.player1.shield_active
        self.p1_shield_energy = msg.player1.shield_energy
        self.p1_score = msg.player1.score
        self.p1_ammo = msg.player1.ammo
        
        # Update Player 2 properties
        self.p2_x = msg.player2.x
        self.p2_y = msg.player2.y
        self.p2_theta = msg.player2.theta
        self.p2_turret_angle_received = msg.player2.turret_angle
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
        
        new_ids = current_ids - self.active_projectile_ids
        for pid in new_ids:
            p = current_projectiles[pid]
            owner_x = self.p1_x if p.owner == 1 else self.p2_x
            owner_y = self.p1_y if p.owner == 1 else self.p2_y
            dx = p.x - owner_x
            dy = p.y - owner_y
            angle = math.atan2(dy, dx)
            color = (0, 246, 255) if p.owner == 1 else (255, 0, 255)
            self.spawn_flash_particles(p.x, p.y, angle, color)
            
        self.active_projectile_ids = current_ids
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
        mx, my = pygame.mouse.get_pos()
        
        btn_local = pygame.Rect(self.screen_width // 2 - 150, 320, 300, 45)
        btn_host = pygame.Rect(self.screen_width // 2 - 150, 385, 300, 45)
        btn_join = pygame.Rect(self.screen_width // 2 - 150, 450, 300, 45)
        btn_exit = pygame.Rect(self.screen_width // 2 - 150, 515, 300, 45)
        
        self.draw_button("LOCAL MATCH (1 LAPTOP)", btn_local, (10, 45, 80), (15, 70, 120), (255, 255, 255), btn_local.collidepoint(mx, my))
        self.draw_button("HOST LAN LOBBY", btn_host, (10, 80, 45), (15, 120, 70), (255, 255, 255), btn_host.collidepoint(mx, my))
        self.draw_button("JOIN LAN LOBBY", btn_join, (80, 10, 80), (120, 15, 120), (255, 255, 255), btn_join.collidepoint(mx, my))
        self.draw_button("EXIT SIMULATION", btn_exit, (80, 15, 15), (120, 20, 20), (255, 255, 255), btn_exit.collidepoint(mx, my))

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
        mx, my = pygame.mouse.get_pos()
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
                mx, my = pygame.mouse.get_pos()
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
        mx, my = pygame.mouse.get_pos()
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
        mx, my = pygame.mouse.get_pos()
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

    def run(self):
        running = True
        
        while running and rclpy.ok():
            # Process ROS 2 Callbacks
            rclpy.spin_once(self, timeout_sec=0.001)
            
            dt = self.clock.tick(60) / 1000.0
            
            # Subsystem housekeepings
            if self.state == "LOBBY_JOIN":
                self.clean_active_lobbies()
            
            # --- Pygame Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        mx, my = event.pos
                        
                        if self.state == "MENU":
                            # Click name box
                            input_rect = pygame.Rect(self.screen_width // 2 - 150, 240, 300, 45)
                            if input_rect.collidepoint(mx, my):
                                self.name_input_active = True
                            else:
                                self.name_input_active = False
                                
                            # Clicks on menu buttons
                            btn_local = pygame.Rect(self.screen_width // 2 - 150, 320, 300, 45)
                            btn_host = pygame.Rect(self.screen_width // 2 - 150, 385, 300, 45)
                            btn_join = pygame.Rect(self.screen_width // 2 - 150, 450, 300, 45)
                            btn_exit = pygame.Rect(self.screen_width // 2 - 150, 515, 300, 45)
                            
                            if btn_local.collidepoint(mx, my):
                                self.is_network = False
                                self.player_id = 1
                                self.start_game_server()
                                time.sleep(0.5)
                                self.state = "GAMEPLAY"
                            elif btn_host.collidepoint(mx, my):
                                self.is_network = True
                                self.player_id = 1
                                self.host_id = "host_" + str(random.randint(1000, 9999))
                                self.lobby_data = {"player2_name": "", "status": "waiting"}
                                self.start_game_server()
                                self.state = "LOBBY_HOST"
                            elif btn_join.collidepoint(mx, my):
                                self.is_network = True
                                self.player_id = 2
                                self.host_id = "guest_" + str(random.randint(1000, 9999))
                                self.state = "LOBBY_JOIN"
                            elif btn_exit.collidepoint(mx, my):
                                running = False
                                
                        elif self.state == "LOBBY_HOST":
                            btn_start = pygame.Rect(self.screen_width // 2 - 150, 480, 300, 45)
                            btn_back = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
                            
                            if btn_start.collidepoint(mx, my) and self.lobby_data.get("player2_name"):
                                self.lobby_data["status"] = "playing"
                                self.publish_lobby_advertisement()
                                self.state = "GAMEPLAY"
                            elif btn_back.collidepoint(mx, my):
                                self.stop_game_server()
                                self.state = "MENU"
                                
                        elif self.state == "LOBBY_JOIN":
                            btn_back = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
                            if btn_back.collidepoint(mx, my):
                                self.state = "MENU"
                            else:
                                lobbies = list(self.active_lobbies.values())
                                for idx, (lobby, _) in enumerate(lobbies[:5]):
                                    join_btn_rect = pygame.Rect(self.screen_width // 2 + 120, 200 + idx * 60, 90, 34)
                                    if join_btn_rect.collidepoint(mx, my) and lobby['status'] == 'waiting':
                                        self.request_join_lobby(lobby["host_id"])
                                        
                        elif self.state == "LOBBY_GUEST":
                            btn_leave = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
                            if btn_leave.collidepoint(mx, my):
                                self.leave_lobby()
                                
                elif event.type == pygame.KEYDOWN:
                    # Escape behavior context
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "GAMEPLAY":
                            if self.is_network:
                                if self.player_id == 1:
                                    self.state = "LOBBY_HOST"
                                    self.lobby_data["status"] = "ready"
                                    self.publish_lobby_advertisement()
                                else:
                                    self.leave_lobby()
                            else:
                                self.stop_game_server()
                                self.state = "MENU"
                        elif self.state in ["LOBBY_HOST", "LOBBY_JOIN"]:
                            self.stop_game_server()
                            self.state = "MENU"
                        elif self.state == "LOBBY_GUEST":
                            self.leave_lobby()
                            
                    # Name Input text capture
                    if self.state == "MENU" and self.name_input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.key == pygame.K_RETURN:
                            self.name_input_active = False
                        else:
                            if event.unicode and len(self.player_name) < 15 and event.unicode.isprintable():
                                self.player_name += event.unicode
                                
                    # Game combat triggers
                    elif self.state == "GAMEPLAY":
                        # P1 actions
                        if not self.is_network or self.player_id == 1:
                            if event.key == pygame.K_SPACE:
                                self.p1_shoot = True
                            elif event.key == pygame.K_q:
                                self.p1_shield = True
                            elif event.key == pygame.K_e:
                                self.p1_weapon_type = 1
                                
                        # P2 actions
                        if not self.is_network:
                            # 1 Laptop P2
                            if event.key == pygame.K_RETURN:
                                self.p2_shoot = True
                            elif event.key == pygame.K_RCTRL:
                                self.p2_shield = True
                            elif event.key == pygame.K_RSHIFT:
                                self.p2_weapon_type = 1
                        elif self.player_id == 2:
                            # Network P2
                            if event.key == pygame.K_SPACE:
                                self.p2_shoot = True
                            elif event.key == pygame.K_q:
                                self.p2_shield = True
                            elif event.key == pygame.K_e:
                                self.p2_weapon_type = 1

            # --- Continuous Key Polling for movement (only in Gameplay) ---
            if self.state == "GAMEPLAY":
                keys = pygame.key.get_pressed()
                
                # Player 1 Movement (Host / Local P1)
                if not self.is_network or self.player_id == 1:
                    self.p1_linear = 0.0
                    if keys[pygame.K_w]:
                        self.p1_linear = 1.0
                    elif keys[pygame.K_s]:
                        self.p1_linear = -1.0
                        
                    self.p1_angular = 0.0
                    if keys[pygame.K_a]:
                        self.p1_angular = 1.0
                    elif keys[pygame.K_d]:
                        self.p1_angular = -1.0
                        
                    if keys[pygame.K_j]:
                        self.p1_turret_angle = self.normalize_angle(self.p1_turret_angle + 0.05)
                    elif keys[pygame.K_l]:
                        self.p1_turret_angle = self.normalize_angle(self.p1_turret_angle - 0.05)
                        
                # Player 2 Movement
                if not self.is_network:
                    # Same laptop P2
                    self.p2_linear = 0.0
                    if keys[pygame.K_UP]:
                        self.p2_linear = 1.0
                    elif keys[pygame.K_DOWN]:
                        self.p2_linear = -1.0
                        
                    self.p2_angular = 0.0
                    if keys[pygame.K_LEFT]:
                        self.p2_angular = 1.0
                    elif keys[pygame.K_RIGHT]:
                        self.p2_angular = -1.0
                        
                    if keys[pygame.K_LEFTBRACKET] or keys[pygame.K_COMMA]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle + 0.05)
                    elif keys[pygame.K_RIGHTBRACKET] or keys[pygame.K_PERIOD]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle - 0.05)
                elif self.player_id == 2:
                    # Network P2 (WASD)
                    self.p2_linear = 0.0
                    if keys[pygame.K_w]:
                        self.p2_linear = 1.0
                    elif keys[pygame.K_s]:
                        self.p2_linear = -1.0
                        
                    self.p2_angular = 0.0
                    if keys[pygame.K_a]:
                        self.p2_angular = 1.0
                    elif keys[pygame.K_d]:
                        self.p2_angular = -1.0
                        
                    if keys[pygame.K_j]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle + 0.05)
                    elif keys[pygame.K_l]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle - 0.05)

            # --- Update Particles ---
            for p in self.particles[:]:
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['alpha'] -= p['decay'] * dt
                p['radius'] = max(1.0, p['radius'] - p['size_decay'] * dt)
                if p['alpha'] <= 0.0:
                    self.particles.remove(p)
                    
            # --- Projectile Trails ---
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

            # --- Screen Rendering based on state ---
            if self.state == "MENU":
                self.render_menu()
            elif self.state == "LOBBY_HOST":
                self.render_lobby_host()
            elif self.state == "LOBBY_JOIN":
                self.render_lobby_join()
            elif self.state == "LOBBY_GUEST":
                self.render_lobby_guest()
            elif self.state == "GAMEPLAY":
                self.render_gameplay(dt)
                
            pygame.display.flip()
            
        pygame.quit()

    def destroy_node(self):
        self.stop_game_server()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    visualizer = PygameVisualizer()
    try:
        visualizer.run()
    except KeyboardInterrupt:
        pass
    finally:
        visualizer.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass

if __name__ == '__main__':
    main()
