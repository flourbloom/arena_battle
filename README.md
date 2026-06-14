# Arena Battle Robot Game

A ROS 2 combat robot simulation package featuring interactive keyboard controls, game logic state publishing, and a custom **Pygame-based 2D visualizer** alongside an **RViz-based 3D visualization** option.

---

## Package Structure

The workspace consists of two ROS 2 packages:
*   **`arena_battle_interfaces`**: Custom message definitions for robot combat commands (`RobotCombatCommand`).
*   **`arena_battle`**: The main Python application, nodes, launch configurations, and URDF/RViz/Pygame resources.

---

## Prerequisites

Before building, make sure you have ROS 2 (e.g., Humble) installed, along with the visualizer dependencies:

```bash
# Standard ROS 2 visualization tools
sudo apt update
sudo apt install ros-humble-desktop ros-humble-joint-state-publisher ros-humble-robot-state-publisher ros-humble-rviz2

# Pygame library
pip install pygame
```

---

## 🛠️ Building the Project

Navigate to the project root directory and build the packages:

1. **(Optional) Clean previous build artifacts** to ensure a fresh build:
   ```bash
   cd ~/arena_battle
   rm -rf build install log
   ```

2. **Build the packages** using `colcon`:
   ```bash
   colcon build --symlink-install
   ```

---

## 🚀 Sourcing and Launching

To run the application, you must source the build environment in every terminal you use.

### 1. Sourcing the Workspace

**In your active terminal:**
```bash
source ~/arena_battle/install/setup.bash
```

**(Recommended) To source automatically in all future terminals:**
```bash
echo "source ~/arena_battle/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

### 2. Launching the Simulator

The package supports two visualization options: an interactive top-down **Pygame window** (default) or **RViz**.

#### Option A: Launching Pygame Visualizer (Default)
This starts the game logic node and opens the Pygame interactive arena. All keyboard/mouse inputs are captured directly in the Pygame window.
```bash
ros2 launch arena_battle arena_battle.launch.py
```

#### Option B: Launching RViz Visualizer
This starts the URDF publishers, TF broadcasters, game logic, and RViz window.
```bash
ros2 launch arena_battle arena_battle.launch.py visualizer:=rviz
```

---

### 3. Launching the Keyboard Controller (Optional)

If running in **RViz mode** or if you prefer a separate terminal for input:

1. Open a new terminal.
2. Source the environment:
   ```bash
   source ~/arena_battle/install/setup.bash
   ```
3. Run the controller node:
   ```bash
   ros2 run arena_battle keyboard_controller
   ```

---

## 🎮 Game Controls

### Pygame Window Controls (Recommended)
When the Pygame window is active, use the following interactive inputs:

| Control | Action | Description |
| :--- | :--- | :--- |
| **`W` / `S`** or **Up/Down Arrows** | Move Forward / Backward | Moves the robot inside the circular boundary |
| **`A` / `D`** or **Left/Right Arrows** | Rotate Chassis Left / Right | Rotates the robot's heading |
| **Mouse Motion** | Aim Turret | Point the cursor to rotate the weapon turret |
| **Left Mouse Click** or **`Space`** | Shoot Projectile | Fires a projectile with trail & muzzle flash effects |
| **`Q`** | Activate Shield | Triggers a cyan protective energy bubble (1.5s duration) |
| **`E`** | Special Weapon | Fires an 8-way radial projectile attack |
| **`ESC`** | Exit Visualizer | Safely closes the Pygame window |

### Terminal Keyboard Controller Controls
If using the `keyboard_controller` node:

| Key | Action | Output / Description |
| :--- | :--- | :--- |
| **`W`** | Move Forward | Moves the robot forward in the arena |
| **`S`** | Move Backward | Moves the robot backward |
| **`A`** | Rotate Left | Rotates the robot counter-clockwise |
| **`D`** | Rotate Right | Rotates the robot clockwise |
| **`Space`** | Shoot | Fires a standard projectile (along the turret heading) |
| **`Q`** | Activate Shield | Triggers shield logic / log output |
| **`E`** | Special Weapon | Fires a radial 8-directional projectile attack |
| **`Ctrl + C`** | Exit | Safely terminates the keyboard controller node |
