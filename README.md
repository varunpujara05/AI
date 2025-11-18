# 🚀 Planetary Exploration Rover - AI Path Planning Simulator

A comprehensive Mars rover navigation simulation system that implements intelligent path planning using A* algorithm with multiple heuristics, reflex agent decision-making, and dynamic environment challenges including dust storms and battery management with day/night cycles.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Heuristics](#heuristics)
- [Terrain Types](#terrain-types)
- [Project Structure](#project-structure)
- [Output](#output)
- [Requirements](#requirements)

## 🌟 Overview

This project simulates an autonomous Mars rover navigating through challenging Martian terrain. The rover must find optimal paths from start to goal positions while managing battery constraints, avoiding hazards, responding to dust storms, and adapting to solar power availability during day/night cycles.

The system demonstrates key AI concepts:
- **A* Path Planning** with 5 different heuristic functions
- **Reflex Agent** for reactive decision-making based on percepts
- **Solar Power Management** with day/night cycle simulation
- **Dynamic Environment** with moving dust storms
- **Battery Management** with strategic recharging

## ✨ Features

### Path Planning
- **Multiple Heuristics**: Compare 5 different A* heuristics for optimal pathfinding
  - Euclidean Distance
  - Manhattan Distance
  - Weighted Euclidean
  - Risk-Aware (avoids radiation zones)
  - Terrain-Cost-Aware (prefers low-cost terrain)

### Environment Dynamics
- **7 Terrain Types**: Each with different battery consumption rates
- **Dust Storms**: Moving hazards that increase battery drain by 25%
- **Recharge Stations**: Strategic power replenishment points
- **Impassable Obstacles**: Rocky terrain requiring path replanning

### Rover Intelligence
- **Reflex Agent Rules**:
  - Initiates recharge when battery < 20%
  - Proactively seeks recharge at 20-25% if station within 2 moves
  - Backtracks when encountering hazards
  - Avoids impassable terrain
  - Responds to dust storm threats

### Solar Power System
- **Day/Night Cycles**: 10 steps per phase (day or night)
- **Daytime**: Normal recharge rates at stations
- **Nighttime**: Reduced recharge efficiency (50% rate)
- Visual indicators throughout simulation

### Visualization & Analysis
- **Interactive GUI**: Real-time simulation with tkinter interface
- **Animated GIFs**: Export simulations as animations
- **Comparative Analysis**: Side-by-side heuristic performance metrics
- **Battery Tracking**: Real-time battery level graphs
- **Jupyter Notebooks**: Detailed heuristics comparison

## 🏗️ System Architecture

### Core Modules

#### 1. `environment.py`
Defines the Martian environment with:
- Terrain types and movement costs
- Dust storm physics and movement
- Grid world representation
- Hazard detection

#### 2. `rover.py`
Rover entity with:
- Position and battery state tracking
- Solar power management (day/night cycles)
- Movement history logging
- Battery consumption calculation

#### 3. `path_planner.py`
A* algorithm implementation with:
- 5 distinct heuristic functions
- Node expansion tracking
- Path cost calculation
- Heuristic comparison utilities

#### 4. `reflex_agent.py`
Reactive agent that:
- Perceives environment state
- Makes decisions based on rules
- Manages recharge strategies
- Handles hazard avoidance

#### 5. `rover_gui.py`
Interactive GUI application featuring:
- Real-time simulation visualization
- Configuration controls
- Animation speed adjustment
- GIF recording capability
- Battery level monitoring

#### 6. `visualization.py`
Creates static visualizations:
- Environment maps
- Path overlays
- Heuristic comparisons
- Performance metrics

#### 7. `animation.py`
Generates animated GIFs showing:
- Rover movement frame-by-frame
- Battery level changes
- Event annotations (recharge, backtrack, etc.)
- Day/night cycle indicators

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Dependencies

Install required packages:

```bash
pip install numpy matplotlib pillow
```

Or install from requirements file:

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `numpy` - Numerical computing and grid operations
- `matplotlib` - Visualization and plotting
- `Pillow (PIL)` - Image processing and GIF generation
- `tkinter` - GUI framework (usually included with Python)

### Setup

1. Clone or download the repository:
```bash
git clone <repository-url>
cd Group15_Planetary_Exploration_Rover
```

2. Verify installation:
```bash
python --version
python -c "import numpy, matplotlib, PIL; print('All dependencies installed!')"
```

## 🚀 Usage

### 1. Interactive GUI Mode

Launch the graphical interface for interactive simulations:

```bash
python rover_gui.py
```

**GUI Features:**
- Configure start/goal positions
- Select heuristic algorithm
- Toggle solar power management
- Adjust animation speed
- Record simulations as GIFs
- Real-time battery monitoring

### 2. Command Line Simulation

Run batch simulations comparing all heuristics:

```bash
python main.py
```

This will:
- Generate environment visualizations
- Run simulations with all 5 heuristics
- Create comparative performance charts
- Save results to `output/` directory

### 3. Generate Animations

Create animated GIFs from simulations:

```bash
python generate_animations.py
```

Outputs saved to `animations/` directory.

### 4. Jupyter Analysis

Explore detailed heuristic comparisons:

```bash
jupyter notebook "Heuristics Comparision.ipynb"
```

## 🧮 Heuristics

### 1. Euclidean Distance
```python
h(n) = √[(x_goal - x_n)² + (y_goal - y_n)²]
```
**Characteristics**: Optimal for unrestricted movement, straight-line distance

### 2. Manhattan Distance
```python
h(n) = |x_goal - x_n| + |y_goal - y_n|
```
**Characteristics**: Best for grid-based 4-directional movement

### 3. Weighted Euclidean (ε = 1.5)
```python
h(n) = 1.5 × √[(x_goal - x_n)² + (y_goal - y_n)²]
```
**Characteristics**: Faster search, potentially suboptimal paths

### 4. Risk-Aware
```python
h(n) = euclidean_distance + α × Σ exp(-dist_to_hazard / β)
```
**Characteristics**: Avoids radiation zones, safer but longer paths

### 5. Terrain-Cost-Aware
```python
h(n) = euclidean_distance × local_terrain_cost_factor
```
**Characteristics**: Prefers low-cost terrain, battery-efficient routes

## 🗺️ Terrain Types

| Terrain | Battery Cost | Description |
|---------|-------------|-------------|
| **FLAT** | 5 | Optimal travel surface |
| **SANDY** | 10 | Moderate resistance |
| **SAND_TRAP** | 17 | Difficult terrain, high cost |
| **RADIATION_SPOT** | 15 | Hazardous zone |
| **CLIFF** | 20 | Very dangerous, steep |
| **ROCKY** | 1000 | Impassable obstacle |
| **RECHARGE_STATION** | 0 | Battery replenishment |

## 📁 Project Structure

```
Group15_Planetary_Exploration_Rover/
│
├── main.py                          # Main simulation runner
├── rover_gui.py                     # Interactive GUI application
├── generate_animations.py           # Animation generator
│
├── environment.py                   # Environment & terrain definitions
├── rover.py                         # Rover entity with battery management
├── path_planner.py                  # A* algorithm with heuristics
├── reflex_agent.py                  # Reactive agent decision-making
│
├── visualization.py                 # Static visualization utilities
├── animation.py                     # GIF animation creator
├── gif_recorder.py                  # GUI frame recorder
│
├── Heuristics Comparision.ipynb     # Jupyter analysis notebook
│
├── output/                          # Simulation results
│   ├── environment.png
│   ├── heuristics_comparison.png
│   ├── metrics_comparison.png
│   └── simulation_*.png
│
├── animations/                      # Generated GIF animations
│   ├── rover_animation.gif
│   └── *.gif
│
├── __pycache__/                     # Python cache files
│
└── README.md                        # This file
```

## 📊 Output

### Static Visualizations (`output/`)
- **environment.png**: Terrain map with start/goal markers
- **simulation_[heuristic].png**: Individual heuristic results
- **heuristics_comparison.png**: Side-by-side comparison
- **metrics_comparison.png**: Performance metrics bar charts

### Animations (`animations/`)
- **rover_[heuristic].gif**: Animated rover navigation
- Step-by-step movement visualization
- Battery level tracking
- Event annotations (recharge, backtrack, dust storm)

### Console Output
Each simulation provides:
- Path planning time
- Total battery consumed
- Distance traveled
- Number of recharges
- Backtrack events
- Success/failure status

## 📋 Requirements

**Minimum Requirements:**
- Python 3.7+
- 4GB RAM
- Display with 1400x900+ resolution (for GUI)

**Python Packages:**
```
numpy>=1.19.0
matplotlib>=3.3.0
Pillow>=8.0.0
```

**Optional:**
- Jupyter Notebook/Lab (for notebook analysis)
- Git (for version control)

## 🎯 Key Algorithms

### A* Pathfinding
```
f(n) = g(n) + h(n)
```
Where:
- `g(n)`: Actual cost from start to node n
- `h(n)`: Heuristic estimated cost from n to goal
- `f(n)`: Total estimated cost

### Reflex Agent Rules
1. **Low Battery**: Battery < 20% → Initiate recharge
2. **Preventive Recharge**: Battery 20-25% AND station within 2 moves → Go to station
3. **Hazard Response**: Current cell hazardous → Backtrack to safe position
4. **Obstacle Avoidance**: Rocky terrain ahead → Replan path
5. **Storm Response**: Dust storm detected → Seek shelter or adjust course

## 🔬 Research Applications

This simulator is useful for:
- **AI Education**: Demonstrating search algorithms and heuristics
- **Path Planning Research**: Testing different optimization strategies
- **Autonomous Systems**: Simulating reactive agent behaviors
- **Resource Management**: Battery optimization strategies
- **Dynamic Environments**: Handling moving obstacles and hazards

## 📝 Notes

- The rover has a maximum battery capacity of 100 units
- Day/night cycles alternate every 10 steps
- Dust storms move dynamically and can be avoided
- Recharge stations provide full battery restoration (time-dependent on day/night)
- All distances are Euclidean unless using Manhattan heuristic

## 🤝 Contributing

This is an educational project. Feel free to:
- Experiment with new heuristics
- Add terrain types
- Implement additional agent behaviors
- Enhance visualizations

## 📄 License

Educational project - Group 15

## 👥 Authors

Group 15 - Planetary Exploration Rover Project

---

**Happy Exploring! 🌌🤖**
