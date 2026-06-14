# Launch and Operation Guide

Follow these steps to build, source, launch, and control the Arena Battle Robot simulation in its decentralized 2-player mode.

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

Always navigate to the root directory of your workspace (`~/arena_battle`) to build the packages:

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

To run ROS 2 commands, the build environment must be sourced in **every new terminal** you use:
```bash
source ~/arena_battle/install/setup.bash
```

### Step 1: Launch the Server & Visualizers
In your first terminal, launch the `game_state_manager` physics engine and both player's visualizer windows:
```bash
ros2 launch arena_battle arena_battle.launch.py
```
*This will open two Pygame GUI windows (Player 1 and Player 2). In this version, these windows are **pure listeners** and only display the battle state. They do not capture mouse/keyboard inputs directly.*

---

## 🎮 Playing the Game (Teleop Terminals)

To control the robots, you must run the teleop input nodes in separate terminal windows (one for each player).

### Control Player 1 (Cyan Robot)
1. Open a **new terminal**.
2. Source the build:
   ```bash
   source ~/arena_battle/install/setup.bash
   ```
3. Run the controller in Player 1's namespace:
   ```bash
   ros2 run arena_battle teleop_control --ros-args -r __ns:=/p1
   ```

### Control Player 2 (Magenta Robot)
1. Open a **second new terminal**.
2. Source the build:
   ```bash
   source ~/arena_battle/install/setup.bash
   ```
3. Run the controller in Player 2's namespace:
   ```bash
   ros2 run arena_battle teleop_control --ros-args -r __ns:=/p2
   ```

---

## ⌨️ Keyboard Mappings (Active in Teleop Terminals)

Keep your keyboard focus inside the respective player's terminal console. The controls are:

| Key | Action | Description |
| :--- | :--- | :--- |
| **`W` / `S`** | Move Forward / Backward | Controls robot chassis speed. Stops moving when you let go of the keys. |
| **`A` / `D`** | Rotate Base Left / Right | Turns the robot chassis direction. |
| **`J` / `L`** | Rotate Turret Left / Right | Rotates the turret barrel independently to aim. |
| **`Space`** | Shoot | Fires a standard projectile (costs 1 ammo). |
| **`Q`** | Activate Shield | Deploys a temporary protective shield bubble (costs 30 shield energy). |
| **`E`** | Special Attack | Fires an 8-way special radial projectile attack (costs 5 ammo). |
| **`Ctrl+C`** | Exit | Safely closes the controller node and restores normal terminal output. |
