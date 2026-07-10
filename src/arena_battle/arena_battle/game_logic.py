#!/usr/bin/env python3

import os
import math
import time
import json
import rclpy
from rclpy.node import Node
from arena_battle_interfaces.msg import RobotCombatCommand, RobotState, Projectile, GameState
from std_msgs.msg import String
import signal
import threading
import subprocess

class RobotTracker:
    def __init__(self, x, y, theta, name, owner_id):
        self.name = name
        self.owner_id = owner_id
        self.x = x
        self.y = y
        self.theta = theta
        self.turret_angle = 0.0
        
        self.health = 100
        self.shield_active = False
        self.shield_duration = 0.0
        self.shield_energy = 100.0
        self.score = 0
        self.ammo = 10
        self.max_ammo = 10
        self.ammo_regen_timer = 0.0

class GameLogic(Node):
    def __init__(self, matchid=None):
        name = 'game_server' if matchid is None else f'game_server_{matchid}'
        super().__init__(name)
        
        # Two players initialized at opposite sides of the circular arena
        self.player1 = RobotTracker(-1.5, 0.0, 0.0, "Player 1", 1)
        self.player2 = RobotTracker(1.5, 0.0, math.pi, "Player 2", 2)
        
        self.start_time = None
        self.game_over = False
        self.is_playing = True  # Default to True for standalone/backwards compatibility
        
        self.projectiles = []  # list of dicts: {'id': int, 'x': float, 'y': float, 'vx': float, 'vy': float, 'type': int, 'owner': int, 'lifetime': float}
        self.projectile_id_counter = 0
        
        # Subscribe to separate player commands (standard QoS depth 10)
        # If running as a match worker, use match-scoped topics
        if matchid is None:
            self.sub_p1 = self.create_subscription(
                RobotCombatCommand,
                '/p1/command',
                lambda msg: self.command_callback(msg, self.player1),
                10
            )
            self.sub_p2 = self.create_subscription(
                RobotCombatCommand,
                '/p2/command',
                lambda msg: self.command_callback(msg, self.player2),
                10
            )
        else:
            self.sub_p1 = self.create_subscription(
                RobotCombatCommand,
                f'/match/{matchid}/p1/command',
                lambda msg: self.command_callback(msg, self.player1),
                10
            )
            self.sub_p2 = self.create_subscription(
                RobotCombatCommand,
                f'/match/{matchid}/p2/command',
                lambda msg: self.command_callback(msg, self.player2),
                10
            )
        
        # Subscribe to lobby advertisements to manage game state
        # Master listens to lobby to spawn matches; workers listen to control pause/end for their match
        self.lobby_sub = self.create_subscription(
            String,
            '/lobby_advertisement',
            self.lobby_callback,
            10
        )

        # Publisher for game state (namespaced for workers, global for master)
        state_topic = '/global_game_state' if matchid is None else f'/match/{matchid}/game_state'
        self.state_pub = self.create_publisher(
            GameState,
            state_topic,
            10
        )
        
        # Timer for updates (60Hz -> dt = 0.0167s)
        self.dt = 1.0 / 60.0
        self.timer = self.create_timer(self.dt, self.update_game)
        domain_id = os.environ.get('ROS_DOMAIN_ID', '0')
        if matchid is None:
            self.get_logger().info(f'Game Master Ready! (ROS_DOMAIN_ID: {domain_id})')
        else:
            self.get_logger().info(f'Game Worker {matchid} Ready! (ROS_DOMAIN_ID: {domain_id})')
        self._matchid = matchid
        self.last_p1_cmd_time = time.time()
        self.last_p2_cmd_time = time.time()
        self.finished_matches = set()

    def lobby_callback(self, msg):
        try:
            data = json.loads(msg.data)
            status = data.get("status", "")
            matchid = data.get("match_id")
            # If this is a worker, only act on messages for our match
            if self._matchid is not None:
                if matchid != self._matchid:
                    return
                # control messages for this worker
                if status in ["waiting", "ready", "paused"]:
                    if self.is_playing:
                        self.get_logger().info(f"[Match {self._matchid}] Pausing game updates (status={status}).")
                        self.is_playing = False
                elif status == "playing":
                    if not self.is_playing:
                        self.get_logger().info(f"[Match {self._matchid}] Resuming game updates.")
                        self.is_playing = True
                elif status in ["end", "terminate"]:
                    self.get_logger().info(f"[Match {self._matchid}] Received end signal; shutting down.")
                    # schedule immediate shutdown
                    def _end_proc():
                        try:
                            self.destroy_node()
                        except Exception:
                            pass
                        try:
                            rclpy.shutdown()
                        except Exception:
                            pass
                        try:
                            os._exit(0)
                        except Exception:
                            pass
                    t = threading.Timer(0.5, _end_proc)
                    t.daemon = True
                    t.start()
                return
            # Master logic (no matchid):
            if not hasattr(self, 'workers'):
                self.workers = {}
            if not hasattr(self, 'finished_matches'):
                self.finished_matches = set()
                
            # Clean up terminated workers from self.workers dictionary
            for mid in list(self.workers.keys()):
                proc = self.workers[mid]
                if proc.poll() is not None:
                    self.get_logger().info(f"Worker for match {mid} has terminated. Removing tracker.")
                    del self.workers[mid]

            if status == "playing":
                if matchid:
                    mid = str(matchid)
                    if mid[0].isdigit():
                        mid = 'm' + mid
                    if mid not in self.workers and mid not in self.finished_matches:
                        self.get_logger().info(f"Lobby status for match {mid} is playing. Spawning match worker.")
                        self.spawn_worker(mid)
            elif status in ["end", "terminate", "game_over"]:
                if matchid:
                    mid = str(matchid)
                    if mid[0].isdigit():
                        mid = 'm' + mid
                    self.finished_matches.add(mid)
                    if mid in self.workers:
                        proc = self.workers[mid]
                        if proc.poll() is None:
                            self.get_logger().info(f"Master terminating worker process group for match {mid}")
                            try:
                                pgid = os.getpgid(proc.pid)
                                os.killpg(pgid, signal.SIGTERM)
                                proc.wait(timeout=1.0)
                            except Exception:
                                try:
                                    proc.terminate()
                                    proc.wait(timeout=0.5)
                                except Exception:
                                    try:
                                        proc.kill()
                                    except Exception:
                                        pass
                        del self.workers[mid]
        except Exception as e:
            self.get_logger().error(f"Error parsing lobby advertisement: {e}")

    def spawn_worker(self, matchid):
        # Launch a separate python process running this file as a worker
        try:
            self.get_logger().info(f'Spawning worker for match {matchid}')
            # prefer launching via ros2 so environment is correct
            # ensure matchid is safe for topic tokens
            mid = str(matchid)
            if mid and mid[0].isdigit():
                mid = 'm' + mid
            cmd = ["ros2", "run", "arena_battle", "game_logic", "--", "--match-id", str(mid)]
            env = os.environ.copy()
            # don't block; let worker run independently, setsid for process group
            p = subprocess.Popen(cmd, env=env, preexec_fn=os.setsid)
            # store reference so we can manage later
            if not hasattr(self, 'workers'):
                self.workers = {}
            self.workers[matchid] = p
        except Exception as e:
            self.get_logger().error(f'Failed to spawn worker {matchid}: {e}')

    def reset_game(self):
        self.player1.x = -1.5
        self.player1.y = 0.0
        self.player1.theta = 0.0
        self.player1.turret_angle = 0.0
        self.player1.health = 100
        self.player1.shield_active = False
        self.player1.shield_duration = 0.0
        self.player1.shield_energy = 100.0
        self.player1.score = 0
        self.player1.ammo = 10
        self.player1.ammo_regen_timer = 0.0

        self.player2.x = 1.5
        self.player2.y = 0.0
        self.player2.theta = math.pi
        self.player2.turret_angle = 0.0
        self.player2.health = 100
        self.player2.shield_active = False
        self.player2.shield_duration = 0.0
        self.player2.shield_energy = 100.0
        self.player2.score = 0
        self.player2.ammo = 10
        self.player2.ammo_regen_timer = 0.0

        self.projectiles.clear()
        self.start_time = None
        self.game_over = False
        self.get_logger().info('🏆 Game Reset and Started!')

    def command_callback(self, msg, player):
        if player.owner_id == 1:
            self.last_p1_cmd_time = time.time()
        elif player.owner_id == 2:
            self.last_p2_cmd_time = time.time()

        if self.game_over:
            return
            
        # Update turret angle (relative to base)
        player.turret_angle = msg.turret_angle
        
        # Update robot pose (scaled by self.dt to keep speed constant)
        player.theta += msg.angular_velocity * (6.0 * self.dt)
        new_x = player.x + msg.linear_velocity * math.cos(player.theta) * (10.0 * self.dt)
        new_y = player.y + msg.linear_velocity * math.sin(player.theta) * (10.0 * self.dt)
        
        # Circular arena boundary constraint (radius 3.5m, robot radius ~0.25m -> max_r = 3.25m)
        dist = math.sqrt(new_x**2 + new_y**2)
        if dist > 3.25:
            player.x = 3.25 * new_x / dist
            player.y = 3.25 * new_y / dist
        else:
            player.x = new_x
            player.y = new_y
        
        # Handle weapon firing
        if msg.shoot:
            self.shoot_projectile(player)
        if msg.shield:
            self.activate_shield(player)
        if msg.weapon_type == 1:
            self.shoot_special(player)

    def shoot_projectile(self, player):
        if player.ammo > 0:
            player.ammo -= 1
            self.projectile_id_counter = (self.projectile_id_counter + 1) % 2147483647
            
            absolute_turret_angle = player.theta + player.turret_angle
            px = player.x + 0.3 * math.cos(absolute_turret_angle)
            py = player.y + 0.3 * math.sin(absolute_turret_angle)
            vx = 6.0 * math.cos(absolute_turret_angle)
            vy = 6.0 * math.sin(absolute_turret_angle)
            
            self.projectiles.append({
                'id': self.projectile_id_counter,
                'x': px,
                'y': py,
                'vx': vx,
                'vy': vy,
                'type': 0, # Normal
                'owner': player.owner_id,
                'lifetime': 2.0
            })
            self.get_logger().info(f'💥 Player {player.owner_id} standard shot fired!')

    def activate_shield(self, player):
        if not player.shield_active and player.shield_energy >= 30.0:
            player.shield_active = True
            player.shield_duration = 1.5
            player.shield_energy -= 30.0
            self.get_logger().info(f'🛡️ Player {player.owner_id} Shield Matrix Activated!')

    def shoot_special(self, player):
        if player.ammo >= 5:
            player.ammo -= 5
            self.get_logger().info(f'⚡ Player {player.owner_id} SPECIAL RADIAL ATTACK!')
            for i in range(8):
                self.projectile_id_counter = (self.projectile_id_counter + 1) % 2147483647
                angle = player.theta + (i * math.pi / 4)
                px = player.x + 0.2 * math.cos(angle)
                py = player.y + 0.2 * math.sin(angle)
                vx = 4.0 * math.cos(angle)
                vy = 4.0 * math.sin(angle)
                
                self.projectiles.append({
                    'id': self.projectile_id_counter,
                    'x': px,
                    'y': py,
                    'vx': vx,
                    'vy': vy,
                    'type': 1, # Special
                    'owner': player.owner_id,
                    'lifetime': 1.0
                })

    def update_game(self):
        if not self.is_playing:
            return
            
        if self.start_time is None:
            self.start_time = time.time()
            
        time_elapsed = time.time() - self.start_time
        
        # Check client timeout for worker nodes
        if self._matchid is not None and not self.game_over:
            now = time.time()
            # If we haven't received any commands from a player for more than 5.0 seconds, shut down
            if now - self.last_p1_cmd_time > 5.0 or now - self.last_p2_cmd_time > 5.0:
                self.get_logger().warn(
                    f"[Match {self._matchid}] Client timeout detected "
                    f"(P1 last cmd: {now - self.last_p1_cmd_time:.1f}s ago, "
                    f"P2 last cmd: {now - self.last_p2_cmd_time:.1f}s ago). Shutting down worker."
                )
                self.game_over = True
                self._shutdown_scheduled = True
                def _shutdown_proc():
                    try:
                        self.destroy_node()
                    except Exception:
                        pass
                    try:
                        rclpy.shutdown()
                    except Exception:
                        pass
                    try:
                        os._exit(0)
                    except Exception:
                        pass
                t = threading.Timer(0.1, _shutdown_proc)
                t.daemon = True
                t.start()
                return
        
        # Robot-to-robot collision resolution (each has radius ~0.25m -> min_dist = 0.5m)
        dx = self.player2.x - self.player1.x
        dy = self.player2.y - self.player1.y
        dist = math.sqrt(dx**2 + dy**2)
        min_dist = 0.5
        if dist < min_dist:
            if dist == 0.0:
                dx = 0.1
                dy = 0.0
                dist = 0.1
            overlap = min_dist - dist
            push_x = (dx / dist) * (overlap / 2.0)
            push_y = (dy / dist) * (overlap / 2.0)
            
            self.player1.x -= push_x
            self.player1.y -= push_y
            self.player2.x += push_x
            self.player2.y += push_y
            
            # Clamp back inside boundary if pushed out
            for p in [self.player1, self.player2]:
                r = math.sqrt(p.x**2 + p.y**2)
                if r > 3.25:
                    p.x = 3.25 * p.x / r
                    p.y = 3.25 * p.y / r
        
        # Update shield duration, shield energy, and ammo for both players
        for player in [self.player1, self.player2]:
            if player.shield_active:
                player.shield_duration -= self.dt
                if player.shield_duration <= 0.0:
                    player.shield_active = False
                    
            # Regenerate shield energy slowly over time
            if not player.shield_active and player.shield_energy < 100.0:
                player.shield_energy = min(100.0, player.shield_energy + 5.0 * self.dt)
                
            # Regenerate ammo
            if player.ammo < player.max_ammo:
                player.ammo_regen_timer += self.dt
                if player.ammo_regen_timer >= 1.0:
                    player.ammo += 1
                    player.ammo_regen_timer = 0.0
                    
        # Update projectiles and check target hits
        for p in self.projectiles[:]:
            p['x'] += p['vx'] * self.dt
            p['y'] += p['vy'] * self.dt
            p['lifetime'] -= self.dt
            
            # Check boundary
            dist_sq = p['x']**2 + p['y']**2
            if dist_sq >= 3.5**2 or p['lifetime'] <= 0.0:
                if p in self.projectiles:
                    self.projectiles.remove(p)
                continue
                
            # Check hitting opponent
            # owner=1 targets player2, owner=2 targets player1
            target = self.player2 if p['owner'] == 1 else self.player1
            shooter = self.player1 if p['owner'] == 1 else self.player2
            
            target_dist = math.sqrt((p['x'] - target.x)**2 + (p['y'] - target.y)**2)
            if target_dist < 0.25: # target radius ~0.25m
                if p in self.projectiles:
                    self.projectiles.remove(p)
                if not self.game_over:
                    if target.shield_active:
                        self.get_logger().info(f'🛡️ Player {target.owner_id} Shield absorbed projectile!')
                    else:
                        damage = 20 if p['type'] == 1 else 10
                        target.health = max(0, target.health - damage)
                        shooter.score += 10
                        self.get_logger().info(f'💥 Player {target.owner_id} hit! Health: {target.health}')
                        
                        if target.health <= 0:
                            self.game_over = True
                            shooter.score += 100 # win bonus points
                            self.get_logger().info(f'🏆 Player {shooter.owner_id} WINS!')
                    
        # Publish game state
        state_msg = GameState()
        state_msg.game_over = bool(self.game_over)
        state_msg.time_elapsed = float(time_elapsed)
        
        def pack_robot(r):
            msg = RobotState()
            msg.x = float(r.x)
            msg.y = float(r.y)
            msg.theta = float(r.theta)
            msg.turret_angle = float(r.turret_angle)
            msg.health = int(r.health)
            msg.shield_active = bool(r.shield_active)
            msg.shield_energy = float(r.shield_energy)
            msg.score = int(r.score)
            msg.ammo = int(r.ammo)
            return msg
            
        state_msg.player1 = pack_robot(self.player1)
        state_msg.player2 = pack_robot(self.player2)
        
        state_msg.projectiles = []
        for p in self.projectiles:
            p_msg = Projectile()
            p_msg.id = int(p['id'])
            p_msg.x = float(p['x'])
            p_msg.y = float(p['y'])
            p_msg.vx = float(p['vx'])
            p_msg.vy = float(p['vy'])
            p_msg.type = int(p['type'])
            p_msg.owner = int(p['owner'])
            state_msg.projectiles.append(p_msg)
            
        self.state_pub.publish(state_msg)

        # If running as a worker and game ended, schedule shutdown of this server process
        if self._matchid is not None and self.game_over and not getattr(self, '_shutdown_scheduled', False):
            self._shutdown_scheduled = True
            self.get_logger().info('Match finished — scheduling server shutdown in 1s')
            def _shutdown_proc():
                try:
                    self.get_logger().info('Shutting down game server process now')
                except Exception:
                    pass
                try:
                    try:
                        self.destroy_node()
                    except Exception:
                        pass
                    try:
                        rclpy.shutdown()
                    except Exception:
                        pass
                finally:
                    try:
                        os._exit(0)
                    except Exception:
                        pass

            t = threading.Timer(1.0, _shutdown_proc)
            t.daemon = True
            t.start()

def main(args=None):
    rclpy.init(args=args)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--match-id', dest='match_id', default=None)
    parsed, unknown = parser.parse_known_args()
    node = GameLogic(matchid=parsed.match_id)
    # Ensure termination signals cause a clean shutdown
    def _on_signal(signum, frame):
        try:
            node.get_logger().info(f'Received signal {signum}, shutting down...')
        except Exception:
            pass
        try:
            # If master, terminate child workers using process group signals
            if getattr(node, '_matchid', None) is None and hasattr(node, 'workers'):
                for mid, proc in list(node.workers.items()):
                    try:
                        node.get_logger().info(f'Terminating worker {mid}')
                        pgid = os.getpgid(proc.pid)
                        os.killpg(pgid, signal.SIGTERM)
                        proc.wait(timeout=0.5)
                    except Exception:
                        try:
                            proc.terminate()
                        except Exception:
                            pass
            rclpy.shutdown()
        except Exception:
            pass

    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass

if __name__ == '__main__':
    main()
