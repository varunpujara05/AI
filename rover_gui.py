"""
Mars Rover Path Planning GUI
Interactive application with visualization, configuration, and animation export.

GIF Recording:
- Captures exact UI frames during simulation
- Ensures pixel-perfect match between live display and saved GIF
- Records at the same frame rate as the simulation
- No recreation or regeneration - what you see is what you get
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np
import threading
import os

from environment import Environment, TerrainType
from rover import Rover
from reflex_agent import ReflexAgent
from path_planner import AStarPlanner
from animation import RoverAnimator
from visualization import RoverVisualizer
from gif_recorder import GIFRecorder


class MarsRoverGUI:
    """Main GUI application for Mars Rover path planning."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mars Rover Path Planning Simulator")
        self.root.geometry("1400x900")
        
        # Initialize variables
        self.env = None
        self.rover = None
        self.result = None
        self.start_pos = (1, 1)
        self.goal_pos = (18, 18)
        self.is_simulating = False
        self.animation_delay = 500  # Milliseconds between steps (500ms = 0.5 seconds)
        self.max_steps_estimate = 50  # Fixed x-axis limit for stable battery graph
        
        # Solar Power Management toggle
        self.solar_power_enabled = tk.BooleanVar(value=True)  # Enabled by default
        
        # GIF Recorder
        self.gif_recorder = GIFRecorder()
        
        # Terrain editing mode
        self.edit_mode_enabled = tk.BooleanVar(value=False)
        self.selected_terrain = tk.StringVar(value="FLAT")
        
        # Terrain colors
        self.terrain_colors = {
            TerrainType.FLAT: '#F5DEB3',
            TerrainType.SANDY: '#F4A460',
            TerrainType.SAND_TRAP: '#8B4513',
            TerrainType.RADIATION_SPOT: '#9370DB',
            TerrainType.CLIFF: '#654321',
            TerrainType.ROCKY: '#2F4F4F',
            TerrainType.RECHARGE_STATION: '#32CD32'
        }
        
        self.setup_ui()
        self.create_default_environment()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_container, width=350)
        main_container.add(left_panel, weight=0)
        
        # Right panel - Visualization
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        self.setup_control_panel(left_panel)
        self.setup_visualization_panel(right_panel)
        
    def setup_control_panel(self, parent):
        """Setup the control panel."""
        # Title
        title = ttk.Label(parent, text="🚀 Mars Rover Control", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(parent, width=340)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === Environment Settings ===
        env_frame = ttk.LabelFrame(scrollable_frame, text="Environment Settings", padding=10)
        env_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Grid size
        ttk.Label(env_frame, text="Grid Size:").grid(row=0, column=0, sticky=tk.W)
        self.grid_size_var = tk.IntVar(value=20)
        grid_size_spin = ttk.Spinbox(env_frame, from_=10, to=30, textvariable=self.grid_size_var, width=10)
        grid_size_spin.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Environment preset
        ttk.Label(env_frame, text="Preset:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.preset_var = tk.StringVar(value="Random")
        preset_combo = ttk.Combobox(env_frame, textvariable=self.preset_var, width=15,
                                     values=["Random", "Sparse", "Dense Obstacles"])
        preset_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Button(env_frame, text="Generate Environment", 
                  command=self.generate_environment).grid(row=2, column=0, columnspan=2, pady=10)
        
        # === Terrain Editor ===
        editor_frame = ttk.LabelFrame(scrollable_frame, text="🖌️ Terrain Editor", padding=10)
        editor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Enable/Disable editing mode
        edit_checkbox = ttk.Checkbutton(editor_frame, text="Enable Editing Mode (Click on map to paint)",
                                        variable=self.edit_mode_enabled,
                                        command=self.toggle_edit_mode)
        edit_checkbox.pack(anchor=tk.W, pady=5)
        
        # Terrain type selector
        ttk.Label(editor_frame, text="Paint Terrain:").pack(anchor=tk.W, pady=(5,2))
        
        terrain_options = [
            ("FLAT", "Flat (5)"),
            ("SANDY", "Sandy (10)"),
            ("SAND_TRAP", "Sand Trap (17)"),
            ("RADIATION_SPOT", "Radiation (15)"),
            ("CLIFF", "Cliff (20)"),
            ("ROCKY", "Rocky (∞)"),
            ("RECHARGE_STATION", "Recharge (0)")
        ]
        
        for terrain_key, terrain_label in terrain_options:
            rb = ttk.Radiobutton(editor_frame, text=terrain_label, 
                                variable=self.selected_terrain, value=terrain_key)
            rb.pack(anchor=tk.W, padx=20)
        
        # Clear/Reset button
        ttk.Button(editor_frame, text="🗑️ Clear All to Flat", 
                  command=self.clear_to_flat).pack(fill=tk.X, pady=10)
        
        # === Position Settings ===
        pos_frame = ttk.LabelFrame(scrollable_frame, text="Start & Goal Positions", padding=10)
        pos_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start position
        ttk.Label(pos_frame, text="Start X:").grid(row=0, column=0, sticky=tk.W)
        self.start_x_var = tk.IntVar(value=1)
        ttk.Spinbox(pos_frame, from_=0, to=19, textvariable=self.start_x_var, width=8).grid(row=0, column=1, padx=2)
        
        ttk.Label(pos_frame, text="Y:").grid(row=0, column=2, sticky=tk.W, padx=(5,0))
        self.start_y_var = tk.IntVar(value=1)
        ttk.Spinbox(pos_frame, from_=0, to=19, textvariable=self.start_y_var, width=8).grid(row=0, column=3, padx=2)
        
        # Goal position
        ttk.Label(pos_frame, text="Goal X:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.goal_x_var = tk.IntVar(value=18)
        ttk.Spinbox(pos_frame, from_=0, to=19, textvariable=self.goal_x_var, width=8).grid(row=1, column=1, padx=2)
        
        ttk.Label(pos_frame, text="Y:").grid(row=1, column=2, sticky=tk.W, padx=(5,0))
        self.goal_y_var = tk.IntVar(value=18)
        ttk.Spinbox(pos_frame, from_=0, to=19, textvariable=self.goal_y_var, width=8).grid(row=1, column=3, padx=2)
        
        # === Rover Settings ===
        rover_frame = ttk.LabelFrame(scrollable_frame, text="Rover Configuration", padding=10)
        rover_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(rover_frame, text="Battery Capacity:").grid(row=0, column=0, sticky=tk.W)
        self.battery_var = tk.IntVar(value=100)
        ttk.Spinbox(rover_frame, from_=50, to=200, textvariable=self.battery_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(rover_frame, text="Heuristic:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.heuristic_var = tk.StringVar(value="euclidean")
        heuristic_combo = ttk.Combobox(rover_frame, textvariable=self.heuristic_var, width=15,
                                       values=["euclidean", "manhattan", "weighted_euclidean", "risk_aware", "terrain_cost_aware"])
        heuristic_combo.grid(row=1, column=1, padx=5)
        
        ttk.Label(rover_frame, text="Animation Speed:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.speed_var = tk.StringVar(value="Medium")
        speed_combo = ttk.Combobox(rover_frame, textvariable=self.speed_var, width=15,
                                   values=["Very Slow", "Slow", "Medium", "Fast", "Very Fast"],
                                   state="readonly")
        speed_combo.grid(row=2, column=1, padx=5)
        speed_combo.bind('<<ComboboxSelected>>', self.update_animation_speed)
        
        # Solar Power Management checkbox
        solar_checkbox = ttk.Checkbutton(rover_frame, text="☀️🌙 Enable Solar Power Management",
                                         variable=self.solar_power_enabled)
        solar_checkbox.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Dust Storm checkbox
        self.dust_storms_enabled = tk.BooleanVar(value=True)
        storm_checkbox = ttk.Checkbutton(rover_frame, text="🌪️ Enable Dust Storms",
                                         variable=self.dust_storms_enabled)
        storm_checkbox.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Number of storms
        ttk.Label(rover_frame, text="Number of Storms:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.num_storms_var = tk.IntVar(value=2)
        storm_spinbox = ttk.Spinbox(rover_frame, from_=0, to=5, textvariable=self.num_storms_var, width=13)
        storm_spinbox.grid(row=5, column=1, padx=5)
        
        # === Simulation Controls ===
        sim_frame = ttk.LabelFrame(scrollable_frame, text="Simulation", padding=10)
        sim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.run_button = ttk.Button(sim_frame, text="▶ Run Simulation", 
                                     command=self.run_simulation, style='Accent.TButton')
        self.run_button.pack(fill=tk.X, pady=5)
        
        self.stop_button = ttk.Button(sim_frame, text="⏹ Stop", 
                                      command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=5)
        
        # === Export Options ===
        export_frame = ttk.LabelFrame(scrollable_frame, text="Export Options", padding=10)
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(export_frame, text="💾 Save Static Image", 
                  command=self.save_static_image).pack(fill=tk.X, pady=2)
        
        ttk.Button(export_frame, text="🎬 Generate & Save GIF", 
                  command=self.save_animation_gif).pack(fill=tk.X, pady=2)
        
        ttk.Button(export_frame, text="📊 Export Path Data", 
                  command=self.export_path_data).pack(fill=tk.X, pady=2)
        
        # === Statistics ===
        stats_frame = ttk.LabelFrame(scrollable_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=10, width=35, font=('Courier', 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.update_stats("No simulation run yet")
        
        # === Legend ===
        legend_frame = ttk.LabelFrame(scrollable_frame, text="Terrain Legend", padding=10)
        legend_frame.pack(fill=tk.X, padx=5, pady=5)
        
        legends = [
            ("🟤", "Flat (Cost: 5)"),
            ("🟡", "Sandy (Cost: 10)"),
            ("☢️", "Radiation (Cost: 15)"),
            ("🪨", "Rocky (Impassable)"),
            ("🔋", "Recharge Station")
        ]
        
        for i, (icon, text) in enumerate(legends):
            ttk.Label(legend_frame, text=f"{icon} {text}").pack(anchor=tk.W)
        
    def setup_visualization_panel(self, parent):
        """Setup the visualization panel with dual-panel layout like GIF animations."""
        # Store parent for background changes
        self.viz_parent = parent
        
        # Title
        title = ttk.Label(parent, text="Environment Visualization", font=('Arial', 12, 'bold'))
        title.pack(pady=5)
        
        # Create matplotlib figure with dual-panel layout (same as GIF animations)
        self.fig = Figure(figsize=(14, 6), dpi=100, facecolor='white')
        self.ax_map = self.fig.add_subplot(121)  # Left panel - Map
        self.ax_battery = self.fig.add_subplot(122)  # Right panel - Battery graph
        
        # Canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Connect mouse click event for terrain editing
        self.canvas.mpl_connect('button_press_event', self.on_map_click)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize battery data
        self.battery_data = []
        self.current_step = 0
        
    def update_animation_speed(self, event=None):
        """Update animation delay based on speed selection."""
        speed_map = {
            "Very Slow": 1000,   # 1 second per step
            "Slow": 700,         # 0.7 seconds per step
            "Medium": 500,       # 0.5 seconds per step
            "Fast": 300,         # 0.3 seconds per step
            "Very Fast": 100     # 0.1 seconds per step
        }
        self.animation_delay = speed_map.get(self.speed_var.get(), 500)
    
    def create_default_environment(self):
        """Create a default environment."""
        self.generate_environment()
        
    def generate_environment(self):
        """Generate environment based on selected preset."""
        size = self.grid_size_var.get()
        # Pass dust_storms_enabled to Environment
        dust_storms_enabled = self.dust_storms_enabled.get()
        self.env = Environment(size, size, dust_storms_enabled=dust_storms_enabled)
        preset = self.preset_var.get()
        
        self.status_var.set(f"Generating {preset} environment...")
        self.root.update()
        
        if preset == "Random":
            self.create_random_environment()
        elif preset == "Sparse":
            self.create_sparse_environment()
        elif preset == "Dense Obstacles":
            self.create_dense_obstacles_environment()
        
        # Add dust storms if enabled
        if dust_storms_enabled:
            self.add_dust_storms()
        
        self.visualize_environment()
        self.status_var.set(f"{preset} environment generated")
        
    def create_random_environment(self):
        """Create random environment."""
        np.random.seed()
        size = self.env.width
        
        # Rocky obstacles
        for _ in range(size * 2):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            if (x, y) != (self.start_x_var.get(), self.start_y_var.get()) and \
               (x, y) != (self.goal_x_var.get(), self.goal_y_var.get()):
                self.env.set_terrain(x, y, TerrainType.ROCKY)
        
        # Sandy areas
        for _ in range(size):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.SANDY)
        
        # Sand traps
        for _ in range(size // 3):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.SAND_TRAP)
        
        # Radiation spots
        for _ in range(size // 2):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.RADIATION_SPOT)
        
        # Cliffs
        for _ in range(size // 4):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.CLIFF)
        
        # Recharge stations
        stations = [(size//4, size//4), (3*size//4, size//4), 
                   (size//2, size//2), (3*size//4, 3*size//4)]
        for x, y in stations:
            if 0 <= x < size and 0 <= y < size:
                self.env.set_terrain(x, y, TerrainType.RECHARGE_STATION)
    
    def create_radiation_hazards_environment(self):
        """Create environment with radiation hazards."""
        size = self.env.width
        
        # Rocky obstacles
        rocks = [(5, 5), (6, 5), (7, 5), (size-5, size-5), (size-4, size-5)]
        for x, y in rocks:
            if 0 <= x < size and 0 <= y < size:
                self.env.set_terrain(x, y, TerrainType.ROCKY)
        
        # Sand traps scattered
        for _ in range(size // 4):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.SAND_TRAP)
        
        # Radiation clusters
        rad_centers = [(size//3, size//3), (2*size//3, size//2), (size//2, 2*size//3)]
        for cx, cy in rad_centers:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < size and 0 <= y < size:
                        self.env.set_terrain(x, y, TerrainType.RADIATION_SPOT)
        
        # Cliffs near edges
        for _ in range(size // 5):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.CLIFF)
        
        # Recharge stations
        stations = [(3, 3), (size-4, 3), (size//2, size//2)]
        for x, y in stations:
            if 0 <= x < size and 0 <= y < size:
                self.env.set_terrain(x, y, TerrainType.RECHARGE_STATION)
    
    def create_radiation_corridor_environment(self):
        """Create corridor environment with radiation."""
        size = self.env.width
        
        # Vertical walls
        for y in range(size):
            if y not in [size//3, size//3+1]:
                if 0 <= size//3 < size:
                    self.env.set_terrain(size//3, y, TerrainType.ROCKY)
        
        # Radiation in passages
        for x in [size//3-1, size//3, size//3+1]:
            for y in [size//3, size//3+1]:
                if 0 <= x < size and 0 <= y < size:
                    self.env.set_terrain(x, y, TerrainType.RADIATION_SPOT)
        
        # Recharge stations
        stations = [(2, 2), (size//2, size//2)]
        for x, y in stations:
            if 0 <= x < size and 0 <= y < size:
                self.env.set_terrain(x, y, TerrainType.RECHARGE_STATION)
    
    def create_sparse_environment(self):
        """Create sparse environment."""
        size = self.env.width
        
        # Few obstacles
        for _ in range(size // 2):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.ROCKY)
        
        # Sandy patches
        for _ in range(size // 3):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.SANDY)
        
        # Few sand traps
        for _ in range(2):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.SAND_TRAP)
        
        # Few radiation
        for _ in range(3):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.RADIATION_SPOT)
        
        # Few cliffs
        for _ in range(2):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.CLIFF)
        
        # Recharge station
        self.env.set_terrain(size//2, size//2, TerrainType.RECHARGE_STATION)
    
    def create_dense_obstacles_environment(self):
        """Create dense obstacles environment."""
        size = self.env.width
        
        # Many obstacles
        for _ in range(size * 3):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            if (x, y) != (self.start_x_var.get(), self.start_y_var.get()) and \
               (x, y) != (self.goal_x_var.get(), self.goal_y_var.get()):
                self.env.set_terrain(x, y, TerrainType.ROCKY)
        
        # Sand traps
        for _ in range(size // 2):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.SAND_TRAP)
        
        # Radiation zones
        for _ in range(size):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.RADIATION_SPOT)
        
        # Cliffs
        for _ in range(size // 3):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.CLIFF)
        
        # Multiple recharge stations
        for _ in range(4):
            x, y = np.random.randint(0, size), np.random.randint(0, size)
            self.env.set_terrain(x, y, TerrainType.RECHARGE_STATION)
    
    def add_dust_storms(self):
        """Add dust storms to the environment."""
        num_storms = self.num_storms_var.get()
        size = self.env.width
        
        for _ in range(num_storms):
            # Random position avoiding start/goal
            while True:
                cx = np.random.randint(4, size - 4)
                cy = np.random.randint(4, size - 4)
                # Ensure storm doesn't start on start/goal positions
                if (cx, cy) != (self.start_x_var.get(), self.start_y_var.get()) and \
                   (cx, cy) != (self.goal_x_var.get(), self.goal_y_var.get()):
                    break
            
            # Random initial direction
            direction = (np.random.choice([-1, 0, 1]), np.random.choice([-1, 0, 1]))
            if direction == (0, 0):
                direction = (1, 0)
            
            # Storm radius 2-4
            radius = np.random.randint(2, 4)
            
            self.env.add_dust_storm((cx, cy), radius, direction, speed=1)
        
        print(f"🌪️ Added {num_storms} dust storm(s) to environment")
    
    def toggle_edit_mode(self):
        """Toggle terrain editing mode."""
        if self.edit_mode_enabled.get():
            self.status_var.set("🖌️ Editing Mode: Click on map to paint terrain")
            messagebox.showinfo("Terrain Editor", 
                              "Editing Mode Enabled!\n\n"
                              "• Click on any cell to change its terrain\n"
                              "• Select terrain type from the editor panel\n"
                              "• Changes are applied instantly\n"
                              "• Click 'Clear All to Flat' to reset")
        else:
            self.status_var.set("Ready")
    
    def on_map_click(self, event):
        """Handle mouse clicks on the map for terrain editing."""
        # Only process clicks if in edit mode and not simulating
        if not self.edit_mode_enabled.get() or self.is_simulating:
            return
        
        # Only process clicks on the left panel (map)
        if event.inaxes != self.ax_map:
            return
        
        if self.env is None:
            return
        
        # Get click coordinates
        x, y = int(round(event.xdata)), int(round(event.ydata))
        
        # Validate coordinates
        if not (0 <= x < self.env.width and 0 <= y < self.env.height):
            return
        
        # Get selected terrain type
        terrain_name = self.selected_terrain.get()
        terrain_type = getattr(TerrainType, terrain_name)
        
        # Update terrain
        old_terrain = self.env.get_terrain(x, y)
        self.env.set_terrain(x, y, terrain_type)
        
        # Update visualization
        self.visualize_environment()
        
        # Update status
        self.status_var.set(f"🖌️ Changed ({x}, {y}) from {old_terrain.name} to {terrain_type.name}")
    
    def clear_to_flat(self):
        """Clear entire environment to flat terrain."""
        if self.env is None:
            messagebox.showwarning("Warning", "No environment to clear!")
            return
        
        result = messagebox.askyesno("Confirm Clear", 
                                     "Clear all terrain to FLAT?\n\n"
                                     "This will reset the entire map.")
        if not result:
            return
        
        # Clear all to flat
        for x in range(self.env.width):
            for y in range(self.env.height):
                self.env.set_terrain(x, y, TerrainType.FLAT)
        
        # Keep start and goal as flat
        start_x, start_y = self.start_x_var.get(), self.start_y_var.get()
        goal_x, goal_y = self.goal_x_var.get(), self.goal_y_var.get()
        self.env.set_terrain(start_x, start_y, TerrainType.FLAT)
        self.env.set_terrain(goal_x, goal_y, TerrainType.FLAT)
        
        # Update visualization
        self.visualize_environment()
        
        self.status_var.set("✅ Environment cleared to flat terrain")
    
    def visualize_environment(self, path=None, battery_history=None):
        """Visualize the current environment with dual-panel layout (same as GIF animations)."""
        # Clear both panels
        self.ax_map.clear()
        self.ax_battery.clear()
        
        # Check if solar power management is enabled
        solar_enabled = self.solar_power_enabled.get()
        
        # Determine if it's day or night based on path length (steps taken)
        is_daytime = True
        current_step = 0
        
        if solar_enabled:
            if path and len(path) > 1:
                current_step = len(path) - 1  # Current step count
                # Calculate day/night (10 steps day, 10 steps night)
                cycle_position = current_step % 20
                is_daytime = cycle_position < 10
            elif hasattr(self, 'result') and self.result and 'rover' in self.result:
                rover = self.result['rover']
                if hasattr(rover, 'is_daytime'):
                    is_daytime = rover.is_daytime
                    current_step = rover.step_count if hasattr(rover, 'step_count') else 0
        
        # Set colors based on day/night (only if solar power enabled)
        if solar_enabled and not is_daytime:
            # Night mode colors
            map_bg_color = '#0f0f1e'  # Very dark blue - nighttime background
            fig_bg_color = '#1a1a2e'
            axes_bg_color = '#16213e'
            time_indicator = "🌙 NIGHT"
            time_color = 'cyan'
            # Dark theme for entire GUI
            self.root.configure(bg='#0a0a0a')
            self.fig.patch.set_facecolor('#1a1a2e')
            self.canvas.get_tk_widget().configure(bg='#1a1a2e')
        else:
            # Day mode colors (default, also used when solar power disabled)
            map_bg_color = '#FFF8DC'  # Cornsilk - light daytime background
            fig_bg_color = 'white'
            axes_bg_color = 'white'
            time_indicator = "☀️ DAY" if solar_enabled else ""
            time_color = 'gold'
            # Light theme for entire GUI
            self.root.configure(bg='white')
            self.fig.patch.set_facecolor('white')
            self.canvas.get_tk_widget().configure(bg='white')
        
        # Set map background
        self.ax_map.set_facecolor(map_bg_color)
        self.ax_battery.set_facecolor(axes_bg_color)
        
        # ===== LEFT PANEL: MAP VISUALIZATION =====
        # Create terrain grid
        terrain_map = {
            TerrainType.FLAT: 0,
            TerrainType.SANDY: 1,
            TerrainType.SAND_TRAP: 2,
            TerrainType.RADIATION_SPOT: 3,
            TerrainType.CLIFF: 4,
            TerrainType.ROCKY: 5,
            TerrainType.RECHARGE_STATION: 6
        }
        
        grid = np.zeros((self.env.height, self.env.width))
        for y in range(self.env.height):
            for x in range(self.env.width):
                terrain = self.env.grid[y, x]
                grid[y, x] = terrain_map[terrain]
        
        # Color map
        colors = [
            self.terrain_colors[TerrainType.FLAT],
            self.terrain_colors[TerrainType.SANDY],
            self.terrain_colors[TerrainType.SAND_TRAP],
            self.terrain_colors[TerrainType.RADIATION_SPOT],
            self.terrain_colors[TerrainType.CLIFF],
            self.terrain_colors[TerrainType.ROCKY],
            self.terrain_colors[TerrainType.RECHARGE_STATION]
        ]
        cmap = ListedColormap(colors)
        
        # Plot terrain
        self.ax_map.imshow(grid, cmap=cmap, origin='lower', aspect='equal')
        
        # Plot dust storms if enabled
        if hasattr(self.env, 'dust_storms_enabled') and self.env.dust_storms_enabled:
            for storm in self.env.get_active_storms():
                center = storm.get_center()
                # Draw storm as semi-transparent circle
                circle = plt.Circle(center, storm.radius, color='orange', alpha=0.35, zorder=3)
                self.ax_map.add_patch(circle)
                # Draw storm center
                self.ax_map.plot(center[0], center[1], 'o', color='darkorange', 
                               markersize=10, markeredgecolor='red', markeredgewidth=2, zorder=3)
                # Add storm icon/label
                self.ax_map.text(center[0], center[1] + storm.radius + 0.5, '🌪️', 
                               fontsize=16, ha='center', va='bottom', zorder=3)
        
        # Plot start and goal
        start = (self.start_x_var.get(), self.start_y_var.get())
        goal = (self.goal_x_var.get(), self.goal_y_var.get())
        
        self.ax_map.plot(start[0], start[1], 'go', markersize=15, label='Start',
                    markeredgecolor='darkgreen', markeredgewidth=2, zorder=5)
        self.ax_map.plot(goal[0], goal[1], 'r*', markersize=25, label='Goal',
                    markeredgecolor='darkred', markeredgewidth=2, zorder=5)
        
        # Plot path if available
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            # Path trail (cyan line like in GIF animations)
            self.ax_map.plot(path_x, path_y, '-', color='cyan', linewidth=3, 
                           alpha=0.6, zorder=4, label='Path Trail')
            # Current rover position (blue circle like in GIF animations)
            if len(path) > 0:
                current_pos = path[-1]
                self.ax_map.plot(current_pos[0], current_pos[1], 'o', color='#1E90FF', 
                               markersize=18, markeredgecolor='navy', 
                               markeredgewidth=2, zorder=10, label='Rover')
                
                # Add step information text box with day/night indicator (like in GIF animations) - bottom left
                current_terrain = self.env.get_terrain(current_pos[0], current_pos[1])
                terrain_name = current_terrain.name.replace('_', ' ').title()
                step_info = ""
                if solar_enabled and time_indicator:
                    step_info = f"{time_indicator}\n"
                step_info += f"Step: {len(path) - 1}\nPosition: {current_pos}\nTerrain: {terrain_name}"
                
                if is_daytime:
                    box_color = 'lightyellow'
                    text_color = 'black'
                    edge_color = 'orange'
                else:
                    box_color = '#2a2a4e'
                    text_color = 'white'
                    edge_color = 'cyan'
                
                self.ax_map.text(0.02, 0.02, step_info, transform=self.ax_map.transAxes,
                               fontsize=10, verticalalignment='bottom', color=text_color,
                               bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.9, 
                                       edgecolor=edge_color, linewidth=2))
        
        self.ax_map.set_xlim(-0.5, self.env.width - 0.5)
        self.ax_map.set_ylim(-0.5, self.env.height - 0.5)
        
        # Set axis colors based on day/night - always visible
        if is_daytime:
            # Day: dark colors for visibility on light background
            axis_color = 'black'
            spine_color = 'darkgray'
            self.ax_map.tick_params(colors=axis_color)
            self.ax_map.spines['bottom'].set_color(spine_color)
            self.ax_map.spines['top'].set_color(spine_color)
            self.ax_map.spines['left'].set_color(spine_color)
            self.ax_map.spines['right'].set_color(spine_color)
            self.ax_map.xaxis.label.set_color(axis_color)
            self.ax_map.yaxis.label.set_color(axis_color)
            
            self.ax_battery.tick_params(colors=axis_color)
            self.ax_battery.spines['bottom'].set_color(spine_color)
            self.ax_battery.spines['top'].set_color(spine_color)
            self.ax_battery.spines['left'].set_color(spine_color)
            self.ax_battery.spines['right'].set_color(spine_color)
            self.ax_battery.xaxis.label.set_color(axis_color)
            self.ax_battery.yaxis.label.set_color(axis_color)
        else:
            # Night: light colors for visibility on dark background
            axis_color = 'white'
            spine_color = 'cyan'
            self.ax_map.tick_params(colors=axis_color)
            self.ax_map.spines['bottom'].set_color(spine_color)
            self.ax_map.spines['top'].set_color(spine_color)
            self.ax_map.spines['left'].set_color(spine_color)
            self.ax_map.spines['right'].set_color(spine_color)
            self.ax_map.xaxis.label.set_color(axis_color)
            self.ax_map.yaxis.label.set_color(axis_color)
            
            self.ax_battery.tick_params(colors=axis_color)
            self.ax_battery.spines['bottom'].set_color(spine_color)
            self.ax_battery.spines['top'].set_color(spine_color)
            self.ax_battery.spines['left'].set_color(spine_color)
            self.ax_battery.spines['right'].set_color(spine_color)
            self.ax_battery.xaxis.label.set_color(axis_color)
            self.ax_battery.yaxis.label.set_color(axis_color)
        
        self.ax_map.set_xlabel('X Coordinate', fontsize=12)
        self.ax_map.set_ylabel('Y Coordinate', fontsize=12)
        
        # Title with large day/night indicator (only if solar enabled)
        heuristic_name = self.heuristic_var.get().replace("_", " ").title()
        
        # Add edit mode indicator
        edit_mode_text = "🖌️ EDIT MODE - " if self.edit_mode_enabled.get() else ""
        
        if solar_enabled and time_indicator:
            title_text = f'{edit_mode_text}{time_indicator}\nRover Navigation - {heuristic_name}'
        else:
            title_text = f'{edit_mode_text}Rover Navigation - {heuristic_name}'
        title_color = 'black' if is_daytime else 'white'
        self.ax_map.set_title(title_text, fontsize=14, fontweight='bold', color=title_color, pad=15)
        
        # Legend with terrain types (like in GIF animations)
        legend_elements = [
            mpatches.Patch(color=self.terrain_colors[TerrainType.FLAT], label='Flat (5)'),
            mpatches.Patch(color=self.terrain_colors[TerrainType.SANDY], label='Sandy (10)'),
            mpatches.Patch(color=self.terrain_colors[TerrainType.SAND_TRAP], label='Sand Trap (17)'),
            mpatches.Patch(color=self.terrain_colors[TerrainType.RADIATION_SPOT], label='Radiation (15)'),
            mpatches.Patch(color=self.terrain_colors[TerrainType.CLIFF], label='Cliff (20)'),
            mpatches.Patch(color=self.terrain_colors[TerrainType.ROCKY], label='Rocky (∞)'),
            mpatches.Patch(color=self.terrain_colors[TerrainType.RECHARGE_STATION], label='Recharge'),
        ]
        legend = self.ax_map.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        # Style legend based on day/night
        if is_daytime:
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_edgecolor('darkgray')
            legend.get_frame().set_alpha(0.9)
            for text in legend.get_texts():
                text.set_color('black')
        else:
            legend.get_frame().set_facecolor('#2a2a4e')
            legend.get_frame().set_edgecolor('cyan')
            legend.get_frame().set_alpha(0.9)
            for text in legend.get_texts():
                text.set_color('white')
        
        # ===== RIGHT PANEL: BATTERY GRAPH =====
        if battery_history and len(battery_history) > 0:
            steps = list(range(len(battery_history)))
            
            # Set up battery graph with FIXED x-axis limit to prevent shifting
            self.ax_battery.set_xlim(0, self.max_steps_estimate)
            self.ax_battery.set_ylim(0, 105)
            
            # Add day/night cycle background shading (only if solar enabled)
            if solar_enabled and hasattr(self, 'result') and self.result and 'rover' in self.result:
                rover = self.result['rover']
                if hasattr(rover, 'day_night_cycle_length'):
                    cycle_length = rover.day_night_cycle_length
                    # Shade night periods
                    for i in range(0, self.max_steps_estimate, cycle_length * 2):
                        night_start = i + cycle_length
                        night_end = i + cycle_length * 2
                        self.ax_battery.axvspan(night_start, night_end, alpha=0.15, color='navy', label='Night' if i == 0 else '')
                        if i == 0:
                            self.ax_battery.axvspan(i, i + cycle_length, alpha=0.1, color='yellow', label='Day')
            
            # Critical and low battery zones (like in GIF animations) - use fixed width
            self.ax_battery.axhline(y=20, color='red', linestyle='--', linewidth=2, label='Critical (20%)')
            self.ax_battery.axhline(y=25, color='orange', linestyle='--', linewidth=2, label='Low (25%)')
            self.ax_battery.fill_between([0, self.max_steps_estimate], 0, 20, alpha=0.2, color='red')
            self.ax_battery.fill_between([0, self.max_steps_estimate], 20, 25, alpha=0.2, color='orange')
            
            # Plot battery line
            self.ax_battery.plot(steps, battery_history, 'b-', linewidth=3, label='Battery')
            self.ax_battery.plot(steps[-1], battery_history[-1], 'bo', markersize=10)
            
            self.ax_battery.set_xlabel('Step', fontsize=12)
            self.ax_battery.set_ylabel('Battery Level (%)', fontsize=12)
            title_color = 'black' if is_daytime else 'white'
            self.ax_battery.set_title('Battery Level Over Time', fontsize=14, fontweight='bold', color=title_color)
            self.ax_battery.grid(True, alpha=0.3, color='gray' if is_daytime else 'lightgray')
            legend = self.ax_battery.legend(loc='lower left', fontsize=10)
            
            # Style legend based on day/night
            if is_daytime:
                legend.get_frame().set_facecolor('white')
                legend.get_frame().set_edgecolor('darkgray')
                legend.get_frame().set_alpha(0.9)
                for text in legend.get_texts():
                    text.set_color('black')
            else:
                legend.get_frame().set_facecolor('#2a2a4e')
                legend.get_frame().set_edgecolor('cyan')
                legend.get_frame().set_alpha(0.9)
                for text in legend.get_texts():
                    text.set_color('white')
            
            # Add battery status text box with day/night info (like in GIF animations) - right side
            current_battery = battery_history[-1]
            time_status = "☀️ DAY" if is_daytime else "🌙 NIGHT"
            battery_info = f"{time_status}\nStep: {len(battery_history)-1}\nBattery: {current_battery}%"
            if current_battery < 20:
                battery_info += "\n⚠️ CRITICAL!"
            elif current_battery <= 25:
                battery_info += "\n⚡ LOW"
            
            if is_daytime:
                box_color = 'lightyellow'
                text_color = 'black'
                edge_color = 'orange'
            else:
                box_color = '#2a2a4e'
                text_color = 'white'
                edge_color = 'cyan'
            
            self.ax_battery.text(0.98, 0.50, battery_info, transform=self.ax_battery.transAxes,
                               fontsize=10, verticalalignment='center', horizontalalignment='right',
                               color=text_color,
                               bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.9, 
                                       edgecolor=edge_color, linewidth=2))
        else:
            # No battery data yet - show empty graph with fixed x-axis
            self.ax_battery.set_xlim(0, self.max_steps_estimate)
            self.ax_battery.set_ylim(0, 105)
            self.ax_battery.axhline(y=20, color='red', linestyle='--', linewidth=2, label='Critical (20%)')
            self.ax_battery.axhline(y=25, color='orange', linestyle='--', linewidth=2, label='Low (25%)')
            self.ax_battery.fill_between([0, self.max_steps_estimate], 0, 20, alpha=0.2, color='red')
            self.ax_battery.fill_between([0, self.max_steps_estimate], 20, 25, alpha=0.2, color='orange')
            self.ax_battery.set_xlabel('Step', fontsize=12)
            self.ax_battery.set_ylabel('Battery Level (%)', fontsize=12)
            title_color = 'black' if is_daytime else 'white'
            self.ax_battery.set_title('Battery Level Over Time', fontsize=14, fontweight='bold', color=title_color)
            self.ax_battery.grid(True, alpha=0.3, color='gray' if is_daytime else 'lightgray')
            legend = self.ax_battery.legend(loc='lower left', fontsize=10)
            
            # Style legend based on day/night
            if is_daytime:
                legend.get_frame().set_facecolor('white')
                legend.get_frame().set_edgecolor('darkgray')
                legend.get_frame().set_alpha(0.9)
                for text in legend.get_texts():
                    text.set_color('black')
            else:
                legend.get_frame().set_facecolor('#2a2a4e')
                legend.get_frame().set_edgecolor('cyan')
                legend.get_frame().set_alpha(0.9)
                for text in legend.get_texts():
                    text.set_color('white')
            
            # Empty state message with appropriate color
            text_color = 'gray' if is_daytime else 'lightgray'
            self.ax_battery.text(0.5, 0.5, 'Run simulation to see battery data', 
                               transform=self.ax_battery.transAxes,
                               ha='center', va='center', fontsize=12, style='italic', 
                               alpha=0.5, color=text_color)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Capture frame for GIF recording if simulation is running
        if self.is_simulating and self.gif_recorder.is_recording:
            self.gif_recorder.capture_frame(self.fig)
    
    def run_simulation(self):
        """Run the rover simulation."""
        if self.is_simulating:
            messagebox.showwarning("Simulation Running", "A simulation is already in progress!")
            return
        
        # Update positions
        self.start_pos = (self.start_x_var.get(), self.start_y_var.get())
        self.goal_pos = (self.goal_x_var.get(), self.goal_y_var.get())
        
        # Validate positions
        if not self.env.is_passable(self.start_pos[0], self.start_pos[1]):
            messagebox.showerror("Invalid Start", "Start position is not passable!")
            return
        
        if not self.env.is_passable(self.goal_pos[0], self.goal_pos[1]):
            messagebox.showerror("Invalid Goal", "Goal position is not passable!")
            return
        
        self.is_simulating = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running simulation...")
        
        # Start GIF recording
        self.gif_recorder.start_recording()
        
        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self._run_simulation_thread)
        thread.daemon = True
        thread.start()
    
    def _run_simulation_thread(self):
        """Run simulation in background thread."""
        try:
            # Initialize rover and planner with solar power setting
            solar_enabled = self.solar_power_enabled.get()
            rover = Rover(self.start_pos, self.battery_var.get(), solar_power_enabled=solar_enabled)
            planner = AStarPlanner(self.env)
            reflex_agent = ReflexAgent(rover, self.env)
            
            # Plan path
            heuristic = self.heuristic_var.get()
            planned_path = planner.plan_path(self.start_pos, self.goal_pos, heuristic)
            
            if not planned_path:
                self.root.after(0, lambda: messagebox.showerror("No Path", "No path found to goal!"))
                self.root.after(0, self.simulation_complete)
                return
            
            # Capture initial state (starting position)
            self.root.after(0, lambda: self.visualize_environment([self.start_pos], [rover.get_battery_percentage()]))
            import time
            time.sleep(self.animation_delay / 1000.0)  # Pause to show start
            
            # Execute path
            events = []
            current_idx = 1
            step = 0
            max_steps = 200
            
            while rover.position != self.goal_pos and step < max_steps and self.is_simulating:
                step += 1
                
                # Always update dust storms even if rover doesn't move
                if hasattr(self.env, 'update_dust_storms'):
                    self.env.update_dust_storms()
                
                if current_idx >= len(planned_path):
                    planned_path = planner.plan_path(rover.position, self.goal_pos, heuristic)
                    if not planned_path:
                        break
                    current_idx = 1
                    events.append({'step': len(rover.path_history), 'type': 'replan', 'position': rover.position})
                    continue
                
                next_move = planned_path[current_idx]
                action, override_target = reflex_agent.decide_action(next_move)
                
                if action == 'move':
                    battery_before = rover.battery
                    success = reflex_agent.execute_action(action, next_move)
                    if success:
                        current_idx += 1
                        
                        # Check if recharged (battery jumped significantly)
                        if rover.battery == rover.max_battery and battery_before < rover.max_battery:
                            events.append({
                                'step': len(rover.path_history) - 1,
                                'type': 'recharge',
                                'position': rover.position
                            })
                        
                        # Update visualization with battery history
                        self.root.after(0, lambda p=rover.path_history.copy(), b=rover.battery_history.copy(): 
                                      self.visualize_environment(p, b))
                        
                        # Add delay for animation effect (slower speed)
                        import time
                        time.sleep(self.animation_delay / 1000.0)
                    else:
                        # Move failed - check if backtracking occurred
                        if rover.position != next_move:
                            events.append({
                                'step': len(rover.path_history) - 1,
                                'type': 'backtrack',
                                'position': rover.position
                            })
                        
                        planned_path = planner.plan_path(rover.position, self.goal_pos, heuristic)
                        if not planned_path:
                            break
                        current_idx = 1
                
                elif action == 'recharge_override':
                    # Check battery level for event type
                    battery_pct = rover.get_battery_percentage()
                    if battery_pct < 20:
                        events.append({
                            'step': len(rover.path_history),
                            'type': 'critical_battery',
                            'position': rover.position
                        })
                    else:
                        events.append({
                            'step': len(rover.path_history),
                            'type': 'low_battery',
                            'position': rover.position
                        })
                    
                    recharge_path = planner.plan_path(rover.position, override_target, heuristic)
                    if recharge_path:
                        # Execute path to recharge station step-by-step - CHECK FOR BATTERY DEPLETION
                        recharge_failed = False
                        for i in range(1, len(recharge_path)):
                            move_success = rover.move_to(recharge_path[i], self.env)
                            
                            if not move_success:
                                # BATTERY DEPLETED - Rover is STRANDED
                                recharge_failed = True
                                break
                            
                            # Check for hazard even on recharge path
                            if self.env.is_hazardous(rover.position[0], rover.position[1]):
                                rover.backtrack()
                                recharge_failed = True
                                break
                            
                            # Update visualization during recharge journey
                            self.root.after(0, lambda p=rover.path_history.copy(), b=rover.battery_history.copy(): 
                                          self.visualize_environment(p, b))
                            
                            import time
                            time.sleep(self.animation_delay / 1000.0)
                        
                        if recharge_failed:
                            # Could not reach recharge station - mission fails
                            break
                        
                        # Successfully reached recharge station
                        if rover.position == override_target:
                            # Add recharge event
                            events.append({
                                'step': len(rover.path_history) - 1,
                                'type': 'recharge',
                                'position': rover.position
                            })
                        
                        planned_path = planner.plan_path(rover.position, self.goal_pos, heuristic)
                        if not planned_path:
                            break
                        current_idx = 1
                    else:
                        # Cannot find path to recharge station
                        break
                
                elif action == 'storm_shelter':
                    # Seek shelter from dust storm
                    events.append({
                        'step': len(rover.path_history),
                        'type': 'storm_detected',
                        'position': rover.position
                    })
                    
                    recharge_path = planner.plan_path(rover.position, override_target, heuristic)
                    if recharge_path:
                        # Execute path to shelter - CHECK FOR BATTERY DEPLETION
                        recharge_failed = False
                        for i in range(1, len(recharge_path)):
                            move_success = rover.move_to(recharge_path[i], self.env)
                            
                            if not move_success:
                                # BATTERY DEPLETED - Rover is STRANDED
                                recharge_failed = True
                                break
                            
                            # Check for hazard even on shelter path
                            if self.env.is_hazardous(rover.position[0], rover.position[1]):
                                rover.backtrack()
                                recharge_failed = True
                                break
                            
                            # Update visualization during shelter journey
                            self.root.after(0, lambda p=rover.path_history.copy(), b=rover.battery_history.copy(): 
                                          self.visualize_environment(p, b))
                            
                            import time
                            time.sleep(self.animation_delay / 1000.0)
                        
                        if recharge_failed:
                            # Could not reach shelter - mission fails
                            break
                        
                        # Successfully reached shelter
                        if rover.position == override_target:
                            # Add recharge event
                            events.append({
                                'step': len(rover.path_history) - 1,
                                'type': 'recharge',
                                'position': rover.position
                            })
                        
                        planned_path = planner.plan_path(rover.position, self.goal_pos, heuristic)
                        if not planned_path:
                            break
                        current_idx = 1
                    else:
                        # Cannot find path to shelter
                        break
                
                elif action == 'storm_avoid':
                    # Storm blocking path - replan to avoid
                    events.append({
                        'step': len(rover.path_history),
                        'type': 'storm_avoid',
                        'position': rover.position
                    })
                    
                    # Wait a moment for storm to potentially move
                    import time
                    time.sleep(self.animation_delay / 1000.0 * 2)
                    
                    # Update visualization to show storm has moved
                    self.root.after(0, lambda p=rover.path_history.copy(), b=rover.battery_history.copy(): 
                                  self.visualize_environment(p, b))
                    
                    planned_path = planner.plan_path(rover.position, self.goal_pos, heuristic)
                    if not planned_path:
                        break
                    current_idx = 1
                
                elif action == 'backtrack':
                    events.append({
                        'step': len(rover.path_history),
                        'type': 'backtrack',
                        'position': rover.position
                    })
                    reflex_agent.execute_action(action, None)
                    planned_path = planner.plan_path(rover.position, self.goal_pos, heuristic)
                    if not planned_path:
                        break
                    current_idx = 1
                else:
                    break
            
            # Store result
            self.result = {
                'success': rover.position == self.goal_pos,
                'rover': rover,
                'events': events,
                'heuristic': heuristic,
                'steps': len(rover.path_history),
                'storm_states': []  # Store storm positions at each step
            }
            
            # Capture final storm positions if storms are enabled
            if hasattr(self.env, 'dust_storms_enabled') and self.env.dust_storms_enabled:
                for storm in self.env.get_active_storms():
                    self.result['storm_states'].append({
                        'final_center': storm.get_center(),
                        'radius': storm.radius,
                        'direction': storm.direction.copy(),
                        'speed': storm.speed
                    })
            
            # Update UI with final visualization including battery history
            self.root.after(0, lambda: self.visualize_environment(rover.path_history, rover.battery_history))
            self.root.after(0, self.update_stats_from_result)
            self.root.after(0, self.simulation_complete)
            
            if self.result['success']:
                self.root.after(0, lambda: self.status_var.set("Simulation completed successfully!"))
            else:
                self.root.after(0, lambda: self.status_var.set("Simulation incomplete - no path found"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Simulation Error", f"Error: {str(e)}"))
            self.root.after(0, self.simulation_complete)
    
    def stop_simulation(self):
        """Stop the current simulation."""
        self.is_simulating = False
        self.status_var.set("Simulation stopped")
    
    def simulation_complete(self):
        """Called when simulation is complete."""
        self.is_simulating = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Stop GIF recording
        self.gif_recorder.stop_recording()
    
    def update_stats(self, message):
        """Update statistics display."""
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, message)
    
    def update_stats_from_result(self):
        """Update statistics from simulation result."""
        if not self.result:
            return
        
        rover = self.result['rover']
        
        # Check if solar power management was enabled
        solar_enabled = hasattr(rover, 'solar_power_enabled') and rover.solar_power_enabled
        
        # Calculate day/night recharges if solar power is enabled
        day_recharges = 0
        night_recharges = 0
        solar_stats = ""
        
        if solar_enabled and hasattr(rover, 'day_night_history'):
            for i, event in enumerate(self.result['events']):
                if event['type'] == 'recharge' and i < len(rover.day_night_history):
                    if rover.day_night_history[i]:
                        day_recharges += 1
                    else:
                        night_recharges += 1
            
            solar_stats = f"""
Solar Power Management:
  • Final Time: {rover.get_time_of_day() if hasattr(rover, 'get_time_of_day') else 'N/A'}
  • Day Recharges (☀️ 100%): {day_recharges}
  • Night Recharges (🌙 +50%): {night_recharges}
  • Total Recharges: {rover.recharge_count}
"""
        else:
            solar_stats = f"""
Battery Management:
  • Total Recharges: {rover.recharge_count}
"""
        
        stats = f"""
╔══════════════════════════════════╗
║      SIMULATION RESULTS          ║
╚══════════════════════════════════╝

Status: {'✅ SUCCESS' if self.result['success'] else '❌ INCOMPLETE'}

Path Statistics:
  • Steps Taken: {self.result['steps']}
  • Distance: {rover.total_distance_traveled:.2f} units
{solar_stats}  • Battery Remaining: {rover.get_battery_percentage():.1f}%

Heuristic Used:
  • {self.result['heuristic'].replace('_', ' ').title()}

Events:
  • Replans: {sum(1 for e in self.result['events'] if e['type'] == 'replan')}
  • Backtracks: {sum(1 for e in self.result['events'] if e['type'] == 'backtrack')}
  • Recharge Seeks: {sum(1 for e in self.result['events'] if e['type'] == 'recharge_seek')}
"""
        self.update_stats(stats)
    
    def save_static_image(self):
        """Save current visualization as image."""
        if not self.result:
            messagebox.showwarning("No Data", "Run a simulation first!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="rover_path.png"
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=150, bbox_inches='tight')
                messagebox.showinfo("Success", f"Image saved to:\n{filename}")
                self.status_var.set(f"Image saved: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving image:\n{str(e)}")
    
    def save_animation_gif(self):
        """Save recorded frames as GIF."""
        if not self.gif_recorder.frames:
            messagebox.showwarning("No Recording", "Run a simulation first to record frames!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
            initialfile="rover_animation.gif"
        )
        
        if filename:
            try:
                self.status_var.set("Saving GIF... Please wait...")
                self.root.update()
                
                # Save the recorded frames as GIF
                success = self.gif_recorder.save_gif(
                    filepath=filename,
                    duration=self.animation_delay,  # Use same delay as simulation
                    loop=0  # Infinite loop
                )
                
                if success:
                    messagebox.showinfo("Success", f"GIF saved to:\n{filename}\n\nFrames: {len(self.gif_recorder.frames)}")
                    self.status_var.set(f"GIF saved: {os.path.basename(filename)}")
                else:
                    messagebox.showerror("Save Error", "Error saving GIF")
                    self.status_var.set("Error saving GIF")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving GIF:\n{str(e)}")
                self.status_var.set("Error saving GIF")
    
    def export_path_data(self):
        """Export path data to CSV file."""
        if not self.result:
            messagebox.showwarning("No Data", "Run a simulation first!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="rover_path_data.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Step,X,Y,Battery,Terrain\n")
                    rover = self.result['rover']
                    for i, (x, y) in enumerate(rover.path_history):
                        battery = rover.battery_history[i] if i < len(rover.battery_history) else 0
                        terrain = self.env.get_terrain(x, y).name if self.env.get_terrain(x, y) else "UNKNOWN"
                        f.write(f"{i},{x},{y},{battery},{terrain}\n")
                
                messagebox.showinfo("Success", f"Path data exported to:\n{filename}")
                self.status_var.set(f"Data exported: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting data:\n{str(e)}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = MarsRoverGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
