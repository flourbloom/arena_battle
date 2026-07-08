#!/usr/bin/env python3
"""
ROS 2 networking / lobby / match-state concerns for the Pygame client.

This is a mixin: `NetworkMixin` expects to be combined with a class that is
also an `rclpy.node.Node` (see pygame_visualizer.py), so it can freely call
self.create_subscription/create_publisher/get_logger/etc.
"""

import os
import math
import random
import time
import json
import subprocess
import signal

from arena_battle_interfaces.msg import GameState, RobotCombatCommand
from std_msgs.msg import String


class NetworkMixin:
    def start_game_server(self, force=False):
        # Only spawn a local server if explicitly allowed by the launcher or forced (e.g. local match)
        allow = os.environ.get('ARENA_ALLOW_LOCAL_SERVER', '0')
        if not force and allow != '1':
            self.get_logger().info("Local server auto-start disabled by launcher; not spawning server.")
            return

        self.stop_game_server()
        self.get_logger().info("Spawning Local Game Logic Server...")
        try:
            self.server_process = subprocess.Popen(
                ["ros2", "run", "arena_battle", "game_logic"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
        except Exception as e:
            self.get_logger().error(f"Failed to start local server process: {e}")

    def stop_game_server(self):
        if self.server_process is not None:
            self.get_logger().info("Terminating Local Game Logic Server...")
            try:
                pgid = os.getpgid(self.server_process.pid)
                os.killpg(pgid, signal.SIGTERM)
                self.server_process.wait(timeout=1.0)
            except Exception as e:
                self.get_logger().error(f"Error terminating local server process group: {e}")
                try:
                    self.server_process.terminate()
                    self.server_process.wait(timeout=0.5)
                except Exception:
                    try:
                        self.server_process.kill()
                    except Exception:
                        pass
            self.server_process = None

    def clean_gameplay_data(self):
        self.particles.clear()
        self.projectiles.clear()
        self.active_projectile_ids.clear()
        
        # Reset poses and combat stats to defaults
        self.p1_x = -1.5
        self.p1_y = 0.0
        self.p1_theta = 0.0
        self.p1_turret_angle = 0.0
        self.p1_turret_angle_received = 0.0
        self.p1_health = 100
        self.p1_shield_active = False
        self.p1_shield_energy = 100.0
        self.p1_score = 0
        self.p1_ammo = 10
        
        self.p2_x = 1.5
        self.p2_y = 0.0
        self.p2_theta = math.pi
        self.p2_turret_angle = 0.0
        self.p2_turret_angle_received = 0.0
        self.p2_health = 100
        self.p2_shield_active = False
        self.p2_shield_energy = 100.0
        self.p2_score = 0
        self.p2_ammo = 10
        
        self.game_over = False
        self.time_elapsed = 0.0

    def publish_lobby_advertisement(self):
        if self.state not in ["LOBBY_HOST", "GAMEPLAY"] or not self.is_network:
            return
            
        if self.state == "GAMEPLAY":
            if self.lobby_data.get("status") == "end":
                status_val = "end"
            elif self.game_over:
                status_val = "game_over"
            elif self.paused:
                status_val = "paused"
            else:
                status_val = "playing"
        else:
            status_val = self.lobby_data.get("status", "waiting")

        # Guest (player_id != 1) is only allowed to advertise if it is signaling match termination ('end')
        if self.player_id != 1 and status_val != "end":
            return

        lobby_info = {
            "host_id": self.host_id,
            "host_name": f"{self.player_name}'s Arena",
            "player1_name": self.player_name,
            "player2_name": self.lobby_data.get("player2_name", ""),
            "status": status_val,
            "match_id": (('m' + str(self.current_match_id)) if (self.current_match_id and str(self.current_match_id)[0].isdigit()) else self.current_match_id)
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
            
            # If currently in gameplay and this advert is for our match, handle pause/unpause/end
            status = data.get('status')
            mid = data.get('match_id')
            if self.state == 'GAMEPLAY' and mid and self.current_match_id and mid == self.current_match_id:
                if status == 'paused':
                    self.get_logger().info("Match paused by remote player.")
                    self.paused = True
                    self.pause_modal = True
                elif status == 'playing':
                    self.get_logger().info("Match resumed by remote player.")
                    self.paused = False
                    self.pause_modal = False
                elif status == 'end':
                    self.get_logger().info("Match ended by remote player.")
                    self.clean_gameplay_data()
                    if not self.is_network:
                        self.stop_game_server()
                    self.state = 'MENU'
                    self.paused = False
                    self.pause_modal = False
                    self.current_match_id = None

            if self.state == "LOBBY_GUEST" and self.selected_lobby_id == hid:
                self.lobby_data = data
                status = data.get('status')
                mid = data.get('match_id')
                if status == 'playing':
                    self.get_logger().info("Lobby status changed to playing! Entering game...")
                    if mid:
                        self.current_match_id = mid
                    self.setup_match_topics(self.current_match_id or ("local_" + str(random.randint(1000,9999))))
                    self.clean_gameplay_data()
                    self.state = "GAMEPLAY"
                    self.paused = False
                    self.pause_modal = False
                elif status == 'paused':
                    self.get_logger().info("Lobby status changed to paused! Entering game...")
                    if mid:
                        self.current_match_id = mid
                    self.setup_match_topics(self.current_match_id or ("local_" + str(random.randint(1000,9999))))
                    self.clean_gameplay_data()
                    self.state = "GAMEPLAY"
                    self.paused = True
                    self.pause_modal = True
                elif status in ['waiting', 'ready']:
                    # lobby update, keep state
                    pass
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

    def setup_match_topics(self, matchid):
        # Tear down existing game topics
        try:
            if self.state_sub is not None:
                try:
                    self.destroy_subscription(self.state_sub)
                except Exception:
                    pass
                self.state_sub = None
        except Exception:
            pass

        try:
            if self.p1_cmd_pub is not None:
                try:
                    self.destroy_publisher(self.p1_cmd_pub)
                except Exception:
                    pass
                self.p1_cmd_pub = None
        except Exception:
            pass

        try:
            if self.p2_cmd_pub is not None:
                try:
                    self.destroy_publisher(self.p2_cmd_pub)
                except Exception:
                    pass
                self.p2_cmd_pub = None
        except Exception:
            pass

        # Create namespaced topics for this match
        self.current_match_id = matchid
        if matchid is None:
            state_topic = '/global_game_state'
            p1_cmd_topic = '/p1/command'
            p2_cmd_topic = '/p2/command'
        else:
            state_topic = f'/match/{matchid}/game_state'
            p1_cmd_topic = f'/match/{matchid}/p1/command'
            p2_cmd_topic = f'/match/{matchid}/p2/command'

        self.state_sub = self.create_subscription(GameState, state_topic, self.state_callback, 10)
        self.p1_cmd_pub = self.create_publisher(RobotCombatCommand, p1_cmd_topic, 10)
        self.p2_cmd_pub = self.create_publisher(RobotCombatCommand, p2_cmd_topic, 10)

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
        self.current_match_id = None

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
            if self.p1_cmd_pub:
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
            if self.p2_cmd_pub:
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

