#!/usr/bin/env python3
"""
Pygame client entry point.

Combines:
- NetworkMixin  (networking.py)  -- ROS 2 topics, lobby/matchmaking, server process mgmt
- RenderMixin   (rendering.py)   -- all pygame drawing
into a single Node subclass, and owns the main loop (event polling, key
polling, particle updates, and per-state render dispatch).
"""

import os
import math
import random
import time
import atexit
import pygame
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import signal

from arena_battle.networking import NetworkMixin
from arena_battle.rendering import RenderMixin


class PygameVisualizer(Node, NetworkMixin, RenderMixin):
    def __init__(self):
        import uuid
        node_name = 'pygame_node_' + str(uuid.uuid4())[:8]
        super().__init__(node_name)
        
        # Declare player_id parameter just in case
        self.declare_parameter('player_id', 1)
        self.player_id = self.get_parameter('player_id').get_parameter_value().integer_value
        
        # If run inside a specific namespace containing p1/p2, override player_id to match
        ns = self.get_namespace()
        if 'p2' in ns:
            self.player_id = 2
        elif 'p1' in ns:
            self.player_id = 1
        
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
        self.server_detected = False
        self.server_check_failed_timer = 0.0
        
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
        self.paused = False
        self.pause_modal = False
        
        # Particles & projectiles
        self.particles = []
        self.projectiles = []
        self.active_projectile_ids = set()
        
        # ROS 2 Subscriptions and Publishers (standard QoS depth 10)
        # Lobby topics remain global
        self.state_sub = None

        self.lobby_pub = self.create_publisher(String, '/lobby_advertisement', 10)
        self.lobby_sub = self.create_subscription(String, '/lobby_advertisement', self.lobby_ad_callback, 10)

        self.join_pub = self.create_publisher(String, '/lobby_join_request', 10)
        self.join_sub = self.create_subscription(String, '/lobby_join_request', self.lobby_join_callback, 10)

        # Command publishers will be created per-match when gameplay starts
        self.p1_cmd_pub = None
        self.p2_cmd_pub = None
        self.current_match_id = None
        
        # Timers
        self.cmd_timer = self.create_timer(0.01, self.publish_commands) # 100Hz
        self.lobby_timer = self.create_timer(1.0, self.publish_lobby_advertisement) # 1Hz
        
        # Setup clean exit hooks
        atexit.register(self.stop_game_server)
        
        # Initialize Pygame
        # Set DPI awareness for Windows to prevent blurry/tiny windows on High-DPI screens
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        pygame.init()
        pygame.font.init()
        
        # Set up display
        self.window_width = 800
        self.window_height = 800
        self.window_surface = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption("Arena Battle - Neon Combat")
        self.is_fullscreen = False

        self.screen_width = 800
        self.screen_height = 800
        # self.screen is the virtual canvas we draw onto
        self.screen = pygame.Surface((self.screen_width, self.screen_height))
        
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
        domain_id = os.environ.get('ROS_DOMAIN_ID', '0')
        self.get_logger().info(f"Pygame Unified Client Initialized! (ROS_DOMAIN_ID: {domain_id})")

    def run(self):
        running = True
        while running and rclpy.ok():
            # Periodically check if game server is running (every 1 second)
            now = time.time()
            if not hasattr(self, '_last_server_check') or now - self._last_server_check > 1.0:
                self._last_server_check = now
                try:
                    self.server_detected = any(n == 'game_server' or n.endswith('/game_server') for n in self.get_node_names())
                except Exception:
                    self.server_detected = False

            # Process ROS 2 callbacks in a non-blocking manner
            rclpy.spin_once(self, timeout_sec=0.0)
            dt = self.clock.tick(60) / 1000.0
            
            # Decrement warning timer
            if hasattr(self, 'server_check_failed_timer') and self.server_check_failed_timer > 0.0:
                self.server_check_failed_timer = max(0.0, self.server_check_failed_timer - dt)
            
            # Subsystem housekeepings
            if self.state == "LOBBY_JOIN":
                self.clean_active_lobbies()
            
            # --- Pygame Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    if not self.is_fullscreen:
                        self.window_width, self.window_height = event.size
                        self.window_surface = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        wx, wy = event.pos
                        mx = int(wx * (self.screen_width / self.window_width))
                        my = int(wy * (self.screen_height / self.window_height))
                        
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
                                try:
                                    server_already_running = any(
                                        n == 'game_server' or n.endswith('/game_server')
                                        for n in self.get_node_names()
                                    )
                                except Exception:
                                    server_already_running = False
                                if not server_already_running:
                                    self.start_game_server(force=True)
                                    time.sleep(0.5)
                                self.setup_match_topics(None)
                                self.clean_gameplay_data()
                                self.state = "GAMEPLAY"
                            elif btn_host.collidepoint(mx, my):
                                self.is_network = True
                                self.player_id = 1
                                self.host_id = "host_" + str(random.randint(1000, 9999))
                                self.lobby_data = {"player2_name": "", "status": "waiting"}
                                self.start_game_server()
                                self.state = "LOBBY_HOST"
                            elif btn_join.collidepoint(mx, my):
                                # Synchronously check if server is running
                                try:
                                    self.server_detected = any(n == 'game_server' or n.endswith('/game_server') for n in self.get_node_names())
                                except Exception:
                                    self.server_detected = False
                                    
                                if self.server_detected:
                                    self.is_network = True
                                    self.player_id = 2
                                    self.host_id = "guest_" + str(random.randint(1000, 9999))
                                    self.state = "LOBBY_JOIN"
                                else:
                                    self.server_check_failed_timer = 1.5
                            elif btn_exit.collidepoint(mx, my):
                                running = False
                                
                        elif self.state == "LOBBY_HOST":
                            btn_start = pygame.Rect(self.screen_width // 2 - 150, 480, 300, 45)
                            btn_back = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
                            
                            if btn_start.collidepoint(mx, my) and self.lobby_data.get("player2_name"):
                                    # Ensure a match_id exists so master and clients can coordinate
                                    if not self.current_match_id:
                                        # generate sanitized match id
                                        mid = str(random.randint(1000, 999999))
                                        if mid[0].isdigit():
                                            mid = 'm' + mid
                                        self.current_match_id = mid
                                    self.lobby_data["status"] = "playing"
                                    self.publish_lobby_advertisement()
                                    self.setup_match_topics(self.current_match_id)
                                    self.clean_gameplay_data()
                                    self.state = "GAMEPLAY"
                            elif btn_back.collidepoint(mx, my):
                                if self.is_network:
                                    self.lobby_data['status'] = 'end'
                                    for _ in range(5):
                                        self.publish_lobby_advertisement()
                                        time.sleep(0.02)
                                self.stop_game_server()
                                self.state = "MENU"
                                self.current_match_id = None
                                
                        elif self.state == "LOBBY_JOIN":
                            btn_back = pygame.Rect(self.screen_width // 2 - 150, 545, 300, 45)
                            if btn_back.collidepoint(mx, my):
                                self.state = "MENU"
                                self.current_match_id = None
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
                        elif self.state == "GAMEPLAY" and self.paused:
                            # check modal buttons
                            no_rect = getattr(self, '_pause_btn_no', None)
                            yes_rect = getattr(self, '_pause_btn_yes', None)
                            if no_rect and no_rect.collidepoint(mx, my):
                                # Unpause
                                self.paused = False
                                self.pause_modal = False
                                if self.is_network and self.current_match_id:
                                    self.lobby_data['status'] = 'playing'
                                    self.publish_lobby_advertisement()
                            elif yes_rect and yes_rect.collidepoint(mx, my):
                                # End match for both players
                                if self.is_network and self.current_match_id:
                                    self.lobby_data['status'] = 'end'
                                    for _ in range(5):
                                        self.publish_lobby_advertisement()
                                        time.sleep(0.05)
                                # Clean up local client and leave
                                self.clean_gameplay_data()
                                if not self.is_network:
                                    self.stop_game_server()
                                self.state = 'MENU'
                                self.paused = False
                                self.pause_modal = False
                                self.current_match_id = None
                                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.is_fullscreen = not self.is_fullscreen
                        if self.is_fullscreen:
                            self.window_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            self.window_width, self.window_height = self.window_surface.get_size()
                        else:
                            self.window_width = 800
                            self.window_height = 800
                            self.window_surface = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                    # Escape behavior context
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == "GAMEPLAY":
                            if self.game_over:
                                # Return to menu
                                if self.is_network and self.current_match_id:
                                    self.lobby_data['status'] = 'end'
                                    for _ in range(5):
                                        self.publish_lobby_advertisement()
                                        time.sleep(0.02)
                                self.clean_gameplay_data()
                                if not self.is_network:
                                    self.stop_game_server()
                                self.state = 'MENU'
                                self.paused = False
                                self.pause_modal = False
                                self.current_match_id = None
                            else:
                                if not self.paused:
                                    # Enter paused modal and notify peers
                                    self.paused = True
                                    self.pause_modal = True
                                    if self.is_network and self.current_match_id:
                                        self.lobby_data['status'] = 'paused'
                                        self.publish_lobby_advertisement()
                                else:
                                    # If already paused and we are the pauser, ESC unpauses
                                    if self.pause_modal:
                                        self.paused = False
                                        self.pause_modal = False
                                        if self.is_network and self.current_match_id:
                                            self.lobby_data['status'] = 'playing'
                                            self.publish_lobby_advertisement()
                            
                    # Name Input text capture
                    elif self.state == "MENU" and self.name_input_active:
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
            if self.state == "GAMEPLAY" and not self.paused:
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
                        self.p1_angular = -1.0 if self.p1_linear < 0.0 else 1.0
                    elif keys[pygame.K_d]:
                        self.p1_angular = 1.0 if self.p1_linear < 0.0 else -1.0
                        
                    if keys[pygame.K_j]:
                        self.p1_turret_angle = self.normalize_angle(self.p1_turret_angle + 0.06)
                    elif keys[pygame.K_l]:
                        self.p1_turret_angle = self.normalize_angle(self.p1_turret_angle - 0.06)
                        
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
                        self.p2_angular = -1.0 if self.p2_linear < 0.0 else 1.0
                    elif keys[pygame.K_RIGHT]:
                        self.p2_angular = 1.0 if self.p2_linear < 0.0 else -1.0
                        
                    if keys[pygame.K_LEFTBRACKET] or keys[pygame.K_COMMA]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle + 0.06)
                    elif keys[pygame.K_RIGHTBRACKET] or keys[pygame.K_PERIOD]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle - 0.06)
                elif self.player_id == 2:
                    # Network P2 (WASD)
                    self.p2_linear = 0.0
                    if keys[pygame.K_w]:
                        self.p2_linear = 1.0
                    elif keys[pygame.K_s]:
                        self.p2_linear = -1.0
                        
                    self.p2_angular = 0.0
                    if keys[pygame.K_a]:
                        self.p2_angular = -1.0 if self.p2_linear < 0.0 else 1.0
                    elif keys[pygame.K_d]:
                        self.p2_angular = 1.0 if self.p2_linear < 0.0 else -1.0
                        
                    if keys[pygame.K_j]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle + 0.06)
                    elif keys[pygame.K_l]:
                        self.p2_turret_angle = self.normalize_angle(self.p2_turret_angle - 0.06)

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
                
            if self.window_width == self.screen_width and self.window_height == self.screen_height:
                self.window_surface.blit(self.screen, (0, 0))
            else:
                scaled_surf = pygame.transform.scale(self.screen, (self.window_width, self.window_height))
                self.window_surface.blit(scaled_surf, (0, 0))
            pygame.display.flip()
            
        pygame.quit()

    def get_mouse_pos(self):
        wx, wy = pygame.mouse.get_pos()
        mx = int(wx * (self.screen_width / self.window_width))
        my = int(wy * (self.screen_height / self.window_height))
        return mx, my

    def destroy_node(self):
        if self.is_network and self.current_match_id:
            try:
                self.lobby_data['status'] = 'end'
                for _ in range(5):
                    self.publish_lobby_advertisement()
                    time.sleep(0.02)
            except Exception:
                pass
        self.stop_game_server()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    visualizer = PygameVisualizer()
    # Handle SIGTERM/SIGINT to ensure we clean up rclpy and spawned server
    def _on_signal(signum, frame):
        try:
            visualizer.get_logger().info(f'Received signal {signum}, shutting down...')
        except Exception:
            pass
        try:
            visualizer.destroy_node()
        except Exception:
            pass
        try:
            rclpy.shutdown()
        except Exception:
            pass

    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
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
