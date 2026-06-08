#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from arena_battle_interfaces.msg import RobotCombatCommand

import os
import threading
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from ament_index_python.packages import get_package_share_directory

class GameWebServer(BaseHTTPRequestHandler):
    game_node = None

    def log_message(self, format, *args):
        # Suppress logging to stdout to keep console clean
        pass

    def get_html_content(self):
        try:
            share_dir = get_package_share_directory('arena_battle')
            html_path = os.path.join(share_dir, 'html', 'index.html')
            if os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass

        # Development fallback relative to the source file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, 'index.html'),
            os.path.join(current_dir, 'html', 'index.html'),
            os.path.join(current_dir, '..', 'html', 'index.html'),
            os.path.join(current_dir, '..', '..', 'html', 'index.html'),
            'index.html'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception:
                    pass

        return "<html><body><h1>Error: index.html not found. Check installation/build.</h1></body></html>"

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html_content().encode('utf-8'))
        elif self.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with self.game_node.state_lock:
                state = {
                    'x': self.game_node.x,
                    'y': self.game_node.y,
                    'theta': self.game_node.theta,
                    'shoot': self.game_node.shoot_active,
                    'shield': self.game_node.shield_active,
                    'weapon_type': self.game_node.weapon_type,
                    'linear_velocity': self.game_node.linear_velocity,
                    'angular_velocity': self.game_node.angular_velocity
                }
                
                # Reset transient events so they fire once per trigger
                if self.game_node.shoot_active:
                    self.game_node.shoot_active = False
                if self.game_node.shield_active:
                    self.game_node.shield_active = False
                if self.game_node.weapon_type != 0:
                    self.game_node.weapon_type = 0
            
            self.wfile.write(json.dumps(state).encode('utf-8'))
            
        elif self.path == '/api/sse':
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # SSE push stream
            while self.game_node.server_running:
                with self.game_node.state_lock:
                    state = {
                        'x': self.game_node.x,
                        'y': self.game_node.y,
                        'theta': self.game_node.theta,
                        'shoot': self.game_node.shoot_active,
                        'shield': self.game_node.shield_active,
                        'weapon_type': self.game_node.weapon_type,
                        'linear_velocity': self.game_node.linear_velocity,
                        'angular_velocity': self.game_node.angular_velocity
                    }
                    
                    # Reset transient states
                    if self.game_node.shoot_active:
                        self.game_node.shoot_active = False
                    if self.game_node.shield_active:
                        self.game_node.shield_active = False
                    if self.game_node.weapon_type != 0:
                        self.game_node.weapon_type = 0
                
                try:
                    data_str = f"data: {json.dumps(state)}\n\n"
                    self.wfile.write(data_str.encode('utf-8'))
                    self.wfile.flush()
                except (ConnectionResetError, BrokenPipeError):
                    # Client disconnected
                    break
                time.sleep(0.05)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                cmd_data = json.loads(post_data.decode('utf-8'))
                
                # Map browser request payload into ROS 2 custom message
                msg = RobotCombatCommand()
                msg.linear_velocity = float(cmd_data.get('linear_velocity', 0.0))
                msg.angular_velocity = float(cmd_data.get('angular_velocity', 0.0))
                msg.shoot = bool(cmd_data.get('shoot', False))
                msg.shield = bool(cmd_data.get('shield', False))
                msg.weapon_type = int(cmd_data.get('weapon_type', 0))
                
                # Publish browser command on the ROS topic
                self.game_node.web_command_pub.publish(msg)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

class GameLogic(Node):
    def __init__(self):
        super().__init__('game_logic')
        
        # State locks
        self.state_lock = threading.Lock()
        
        # Robot physical state variables
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        
        # Transient status flags for combat animations
        self.shoot_active = False
        self.shield_active = False
        self.weapon_type = 0
        
        # ROS 2 Pubs & Subs
        self.sub = self.create_subscription(
            RobotCombatCommand, 
            '/robot_command', 
            self.command_callback, 
            10
        )
        
        # Publisher to allow web controls to feed back into /robot_command
        self.web_command_pub = self.create_publisher(
            RobotCombatCommand, 
            '/robot_command', 
            10
        )
        
        # Keep RViz markers active just in case
        self.marker_pub = self.create_publisher(Marker, '/robot_marker', 10)
        self.timer = self.create_timer(0.05, self.update_visualization)
        
        # Start Web Server on port 8080
        self.server_running = True
        GameWebServer.game_node = self
        self.server = HTTPServer(('0.0.0.0', 8080), GameWebServer)
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        
        self.get_logger().info('Game Logic node ready.')
        self.get_logger().info('Serving top-down game view on http://localhost:8080')

    def run_server(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            self.get_logger().error(f'Web server error: {e}')

    def command_callback(self, msg):
        with self.state_lock:
            # Update state with incoming velocity changes
            self.linear_velocity = msg.linear_velocity
            self.angular_velocity = msg.angular_velocity
            
            # Kinematic integration
            self.theta += msg.angular_velocity * 0.1
            self.x += msg.linear_velocity * math.cos(self.theta) * 0.2
            self.y += msg.linear_velocity * math.sin(self.theta) * 0.2
            
            # Record events for web streaming
            if msg.shoot:
                self.shoot_active = True
                self.get_logger().info('Combat Event: Laser Fired!')
            if msg.shield:
                self.shield_active = True
                self.get_logger().info('Combat Event: Energy Shield deployed!')
            if msg.weapon_type != 0:
                self.weapon_type = msg.weapon_type
                self.get_logger().info(f'Combat Event: Special shockwave detonated (weapon type {msg.weapon_type})!')

    def update_visualization(self):
        # Continue to publish markers to /robot_marker for RViz compatibility
        with self.state_lock:
            x, y, theta = self.x, self.y, self.theta
            
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'robot'
        marker.id = 0
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = 0.0
        marker.pose.orientation.z = math.sin(theta / 2.0)
        marker.pose.orientation.w = math.cos(theta / 2.0)
        marker.scale.x = 0.5
        marker.scale.y = 0.2
        marker.scale.z = 0.2
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0
        self.marker_pub.publish(marker)

    def destroy_node(self):
        self.get_logger().info('Stopping game server...')
        self.server_running = False
        self.server.shutdown()
        self.server.server_close()
        super().destroy_node()

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
