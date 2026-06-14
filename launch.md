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
   Install it within your project virtual environment (or system python if you are not using one):
   ```bash
   pip install pygame
   ```

---

## 🛠️ Building the Workspace

Always navigate to the root directory of your workspace (`~/arena_battle`) to clean and build the packages:

1. **Clean previous builds** (recommended for fresh compiles):
   ```bash
   cd ~/arena_battle
   rm -rf build install log
   ```

2. **Build the packages**:
   ```bash
   colcon build --symlink-install
   ```

---

## 🚀 Sourcing and Launching

To run ROS 2 commands, the build environment must be sourced in **every new terminal** you use.

### Step 1: Source the Build Environment
```bash
source ~/arena_battle/install/setup.bash
```

### Step 2: Launch the Simulator
Launch the game client (`pygame_visualizer`) and game server (`game_logic`) nodes:
```bash
ros2 launch arena_battle arena_battle.launch.py
```

A Pygame window will open, showing the cyber dark-blue circular arena, your blue robot chassis, red weapon turret, and HUD panels.

---

## 🎮 Controls (Pygame Window)

When the Pygame visualizer window is selected and active, use the following controls:

| Control | Action | Description |
| :--- | :--- | :--- |
| **`W` / `S`** or **Up / Down Arrows** | Move Forward / Backward | Moves the robot body inside the arena boundary |
| **`A` / `D`** or **Left / Right Arrows** | Rotate Chassis Left / Right | Turns the robot heading |
| **Mouse Motion** | Aim Turret | Rotates the turret barrel toward your cursor |
| **Left Click** or **`Space`** | Shoot | Fires a orange projectile (costs 1 ammo; gains 10 score on wall hit) |
| **`Q`** | Activate Shield | Triggers a protective cyan energy bubble (costs 30 shield energy) |
| **`E`** | Radial Special | Fires an 8-way special cyan projectile attack (costs 5 ammo) |
| **`ESC`** | Exit Simulator | Safely closes the visualizer window and shuts down the node |

---

## ⌨️ Alternative Controller (Terminal-based)

If you prefer to input commands from a terminal window rather than Pygame directly:

1. Leave the main launch running in your first terminal.
2. Open a **new terminal**.
3. Source the workspace:
   ```bash
   source ~/arena_battle/install/setup.bash
   ```
4. Run the keyboard controller node:
   ```bash
   ros2 run arena_battle keyboard_controller
   ```
   *Note: Press `W`/`A`/`S`/`D` to move, `Space` to shoot, `Q` for shield, and `E` for special attack. Focus must be on this terminal window for keys to register.*
