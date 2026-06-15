# Launch and Operation Guide

Follow these steps to build, source, launch, and control the Arena Battle Robot simulation.

---

## 📋 Prerequisites

Ensure you have ROS 2 Humble installed, along with the visualizer dependencies:

1. **ROS 2 Humble Desktop Install**:
   ```bash
   sudo apt update
   sudo apt install ros-humble-desktop
   ```
2. **Pygame library**:
   Install it within your project:
   ```bash
   pip install pygame
   ```

---

## 🛠️ Building the Workspace

Always navigate to the root directory of your workspace (`/home/ken/Desktop/github/arena_battle`) to build the packages:

1. **Clean previous builds** (recommended for fresh compiles):
   ```bash
   cd /home/ken/Desktop/github/arena_battle
   rm -rf build install log
   ```

2. **Build the packages**:
   ```bash
   colcon build --symlink-install
   ```

---

## 🚀 Sourcing and Launching

To run ROS 2 commands, the build environment must be sourced in **every new terminal** you use:
```bash
source /home/ken/Desktop/github/arena_battle/install/setup.bash
```

### Option A: Using Convenience Scripts (Recommended)
You can launch the game server and client quickly using the scripts in the workspace root:

1. **Start the Game Server**:
   ```bash
   ./runserver
   ```
2. **Start the Game Client (Pygame Window)**:
   ```bash
   ./rungame
   ```

### Option B: Launching via ROS 2 Commands
1. **Start the game logic server**:
   ```bash
   ros2 run arena_battle game_logic
   ```
2. **Start the Pygame client**:
   ```bash
   ros2 run arena_battle pygame_visualizer
   ```

---

## 🎮 Playing the Game (GUI Focused Controls)

Unlike standard ROS systems where inputs are split, the **`pygame_visualizer` GUI window captures keyboard inputs directly** when it is the focused window. There is no need to run separate command-line teleop nodes.

### Keyboard Mappings (Active when GUI Window is Focused)

#### 1. Single Laptop / Local Mode
Both players can play on the same machine using a shared keyboard:

| Key Binding | Player 1 (Cyan Robot) | Player 2 (Magenta Robot) |
| :--- | :--- | :--- |
| **Move Forward / Backward** | `W` / `S` | `Up Arrow` / `Down Arrow` |
| **Rotate Base Left / Right** | `A` / `D` | `Left Arrow` / `Right Arrow` |
| **Rotate Turret Left / Right** | `J` / `L` | `[` / `]` |
| **Shoot Normal Projectile** | `Space` | `Enter` |
| **Activate Shield Bubble** | `Q` | `Right Ctrl` |
| **Special 8-Way Attack** | `E` | `Right Shift` |

#### 2. LAN Multiplayer Mode
When hosting or joining a match over a network, each player uses their own laptop:

| Action | Control Key | Description |
| :--- | :--- | :--- |
| **Move Forward / Backward** | `W` / `S` | Controls robot chassis speed. |
| **Rotate Base Left / Right** | `A` / `D` | Turns the robot chassis direction. |
| **Rotate Turret Left / Right** | `J` / `L` | Rotates the turret barrel independently to aim. |
| **Shoot Normal Projectile** | `Space` | Fires a standard projectile (costs 1 ammo). |
| **Activate Shield Bubble** | `Q` | Deploys a temporary protective shield (costs 30 shield energy). |
| **Special 8-Way Attack** | `E` | Fires an 8-way special radial projectile attack (costs 5 ammo). |
| **Exit Game** | `ESC` or `Ctrl+C` | Returns to the Lobby/Main Menu. |

---

## 🛠️ Alternative: Using the Console Teleop Node (CLI Only)

If you prefer to drive a robot using a separate terminal window instead of the Pygame GUI focus, you can optionally run the alternative CLI teleop node:

1. **Player 1 CLI Teleop**:
   ```bash
   ros2 run arena_battle teleop_control --ros-args -r __ns:=/p1
   ```
2. **Player 2 CLI Teleop**:
   ```bash
   ros2 run arena_battle teleop_control --ros-args -r __ns:=/p2
   ```
*(Make sure to keep your cursor focused inside the terminal windows to send keys. Movement keys must be held down to move).*
