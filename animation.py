"""
Animation module for the Planetary Exploration Rover.
Creates animated GIF showing rover movement with rule triggers.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap
import numpy as np
from typing import List, Tuple, Dict
from environment import Environment, TerrainType


class RoverAnimator:
    """
    Creates animated visualization of rover navigation.
    """
    
    # Color scheme
    TERRAIN_COLORS = {
        TerrainType.FLAT: '#F5DEB3',
        TerrainType.SANDY: '#F4A460',
        TerrainType.SAND_TRAP: '#8B4513',
        TerrainType.RADIATION_SPOT: '#9370DB',
        TerrainType.CLIFF: '#654321',
        TerrainType.ROCKY: '#2F4F4F',
        TerrainType.RECHARGE_STATION: '#32CD32'
    }
    
    def __init__(self, environment: Environment):
        """Initialize animator with environment."""
        self.env = environment
        
    def create_terrain_grid(self) -> np.ndarray:
        """Create numerical representation of terrain."""
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
        
        return grid
    
    def animate_rover_journey(self, path: List[Tuple[int, int]], 
                              battery_history: List[int],
                              events: List[Dict],
                              start: Tuple[int, int],
                              goal: Tuple[int, int],
                              heuristic_name: str,
                              save_path: str = "rover_animation.gif",
                              rover=None):
        """
        Create animated GIF of rover's journey.
        
        Args:
            path: List of (x, y) positions rover visited
            battery_history: Battery level at each step
            events: List of special events (recharge, backtrack, etc.)
            start: Start position
            goal: Goal position
            heuristic_name: Name of heuristic used
            save_path: Path to save GIF
            rover: Rover object (to check if solar power is enabled)
        """
        # Check if solar power management is enabled
        solar_enabled = rover and hasattr(rover, 'solar_power_enabled') and rover.solar_power_enabled
        
        # Setup figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Prepare terrain grid
        grid = self.create_terrain_grid()
        colors = [
            '#F5DEB3',  # FLAT
            '#F4A460',  # SANDY
            '#8B4513',  # SAND_TRAP
            '#9370DB',  # RADIATION_SPOT
            '#654321',  # CLIFF
            '#2F4F4F',  # ROCKY
            '#32CD32'   # RECHARGE_STATION
        ]
        cmap = ListedColormap(colors)
        
        # Plot terrain on left axis
        ax1.imshow(grid, cmap=cmap, origin='lower', aspect='equal')
        ax1.set_xlim(-0.5, self.env.width - 0.5)
        ax1.set_ylim(-0.5, self.env.height - 0.5)
        ax1.set_xlabel('X Coordinate', fontsize=12)
        ax1.set_ylabel('Y Coordinate', fontsize=12)
        ax1.set_title(f'Rover Navigation - {heuristic_name.replace("_", " ").title()}', 
                     fontsize=14, fontweight='bold')
        
        # Plot dust storms if enabled
        storm_patches = []
        storm_centers = []
        storm_labels = []
        if hasattr(self.env, 'dust_storms_enabled') and self.env.dust_storms_enabled:
            for storm in self.env.get_active_storms():
                center = storm.get_center()
                # Draw storm as semi-transparent circle
                circle = plt.Circle(center, storm.radius, color='orange', alpha=0.35, zorder=3)
                ax1.add_patch(circle)
                storm_patches.append(circle)
                # Draw storm center
                storm_center, = ax1.plot(center[0], center[1], 'o', color='darkorange', 
                               markersize=10, markeredgecolor='red', markeredgewidth=2, zorder=3)
                storm_centers.append(storm_center)
                # Add storm icon/label
                storm_label = ax1.text(center[0], center[1] + storm.radius + 0.5, '🌪️', 
                               fontsize=16, ha='center', va='bottom', zorder=3)
                storm_labels.append(storm_label)
        
        # Mark start and goal
        ax1.plot(start[0], start[1], 'go', markersize=15, 
                label='Start', zorder=5, markeredgecolor='darkgreen', markeredgewidth=2)
        ax1.plot(goal[0], goal[1], 'r*', markersize=25, 
                label='Goal', zorder=5, markeredgecolor='darkred', markeredgewidth=2)
        
        # Initialize rover marker (blue circle)
        rover_marker, = ax1.plot([], [], 'o', color='#1E90FF', markersize=18, 
                                label='Rover', zorder=10, markeredgecolor='navy', markeredgewidth=2)
        
        # Initialize path trail (cyan line)
        path_trail, = ax1.plot([], [], '-', color='cyan', linewidth=3, 
                              alpha=0.6, zorder=4, label='Path Trail')
        
        # Legend for left plot
        legend_elements = [
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.FLAT], label='Flat (5)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.SANDY], label='Sandy (10)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.SAND_TRAP], label='Sand Trap (17)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.RADIATION_SPOT], label='Radiation (15)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.CLIFF], label='Cliff (20)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.ROCKY], label='Rocky (∞)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.RECHARGE_STATION], label='Recharge'),
        ]
        legend_ax1 = ax1.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        # Setup battery plot on right axis
        ax2.set_xlim(0, len(battery_history))
        ax2.set_ylim(0, 105)
        
        # Add day/night cycle background only if solar power is enabled
        if solar_enabled:
            day_night_cycle = 10
            for i in range(0, len(battery_history), day_night_cycle * 2):
                # Night shading
                night_start = i + day_night_cycle
                night_end = min(i + day_night_cycle * 2, len(battery_history))
                ax2.axvspan(night_start, night_end, alpha=0.15, color='navy', label='Night' if i == 0 else '')
                # Day shading
                if i == 0:
                    ax2.axvspan(i, min(i + day_night_cycle, len(battery_history)), alpha=0.1, color='yellow', label='Day')
        
        ax2.axhline(y=20, color='red', linestyle='--', linewidth=2, label='Critical (20%)')
        ax2.axhline(y=25, color='orange', linestyle='--', linewidth=2, label='Low (25%)')
        ax2.fill_between([0, len(battery_history)], 0, 20, alpha=0.2, color='red')
        ax2.fill_between([0, len(battery_history)], 20, 25, alpha=0.2, color='orange')
        ax2.set_xlabel('Step', fontsize=12)
        ax2.set_ylabel('Battery Level (%)', fontsize=12)
        ax2.set_title('Battery Level Over Time', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        legend_ax2 = ax2.legend(loc='lower left', fontsize=10)
        
        # Initialize battery line
        battery_line, = ax2.plot([], [], 'b-', linewidth=3, label='Battery')
        battery_point, = ax2.plot([], [], 'bo', markersize=10)
        
        # Text annotations - positioned to avoid overlap with legends and axes
        # Step info: bottom left of map
        step_text = ax1.text(0.02, 0.02, '', transform=ax1.transAxes,
                           fontsize=10, verticalalignment='bottom',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))
        
        # Event info: bottom right of map
        event_text = ax1.text(0.98, 0.02, '', transform=ax1.transAxes,
                            fontsize=10, verticalalignment='bottom', horizontalalignment='right',
                            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9, edgecolor='orange', linewidth=2))
        
        # Battery info: top right of battery graph (away from legend)
        battery_text = ax2.text(0.98, 0.50, '', transform=ax2.transAxes,
                               fontsize=10, verticalalignment='center', horizontalalignment='right',
                               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9, edgecolor='blue'))
        
        # Animation function
        def init():
            """Initialize animation."""
            rover_marker.set_data([], [])
            path_trail.set_data([], [])
            battery_line.set_data([], [])
            battery_point.set_data([], [])
            step_text.set_text('')
            event_text.set_text('')
            battery_text.set_text('')
            # Initialize storm elements
            if hasattr(self.env, 'dust_storms_enabled') and self.env.dust_storms_enabled:
                for storm_center in storm_centers:
                    storm_center.set_data([], [])
            return_list = [rover_marker, path_trail, battery_line, battery_point, step_text, event_text, battery_text]
            return_list.extend(storm_centers)
            return tuple(return_list)
        
        def animate(frame):
            """Update animation for each frame."""
            if frame >= len(path):
                frame = len(path) - 1
            
            # Update dust storms if enabled (move storms every 5 frames to match simulation)
            if hasattr(self.env, 'dust_storms_enabled') and self.env.dust_storms_enabled:
                if frame % 5 == 0 and frame > 0:  # Update every 5 steps
                    self.env.update_dust_storms()
                    # Update storm visualizations
                    for i, storm in enumerate(self.env.get_active_storms()):
                        if i < len(storm_patches):
                            center = storm.get_center()
                            storm_patches[i].set_center(center)
                            storm_centers[i].set_data([center[0]], [center[1]])
                            storm_labels[i].set_position((center[0], center[1] + storm.radius + 0.5))
            
            # Current position
            current_pos = path[frame]
            current_battery = battery_history[frame]
            
            # Update rover position
            rover_marker.set_data([current_pos[0]], [current_pos[1]])
            
            # Update path trail
            trail_x = [pos[0] for pos in path[:frame+1]]
            trail_y = [pos[1] for pos in path[:frame+1]]
            path_trail.set_data(trail_x, trail_y)
            
            # Update battery plot
            battery_line.set_data(range(frame+1), battery_history[:frame+1])
            battery_point.set_data([frame], [current_battery])
            
            # Get current terrain
            terrain = self.env.get_terrain(current_pos[0], current_pos[1])
            terrain_name = terrain.name.replace('_', ' ').title()
            
            # Determine day or night only if solar power is enabled
            time_of_day = ""
            is_day = True  # Default to day mode for visuals
            
            if solar_enabled:
                day_night_cycle = 10
                cycle_position = frame % (day_night_cycle * 2)
                is_day = cycle_position < day_night_cycle
                time_of_day = "☀️ DAY" if is_day else "🌙 NIGHT"
            
            # Update map background based on day/night (only if solar enabled)
            if solar_enabled:
                if is_day:
                    ax1.set_facecolor('#FFF8DC')  # Light daytime (matches GUI)
                    fig.patch.set_facecolor('white')  # Figure background day
                    ax2.set_facecolor('white')  # Battery panel background day
                    # Day: dark colors for visibility on light background
                    axis_color = 'black'
                    spine_color = 'darkgray'
                    title_color = 'black'
                else:
                    ax1.set_facecolor('#0f0f1e')  # Dark nighttime (matches GUI)
                    fig.patch.set_facecolor('#1a1a2e')  # Figure background night
                    ax2.set_facecolor('#16213e')  # Battery panel background night
                    # Night: light colors for visibility on dark background
                    axis_color = 'white'
                    spine_color = 'cyan'
                    title_color = 'white'
                
                # Apply axis colors to both panels
                for ax in [ax1, ax2]:
                    ax.tick_params(colors=axis_color)
                    ax.spines['bottom'].set_color(spine_color)
                    ax.spines['top'].set_color(spine_color)
                    ax.spines['left'].set_color(spine_color)
                    ax.spines['right'].set_color(spine_color)
                    ax.xaxis.label.set_color(axis_color)
                    ax.yaxis.label.set_color(axis_color)
                # Update grid color for ax2 (battery graph has grid)
                grid_color = 'gray' if is_day else 'lightgray'
                for line in ax2.get_xgridlines() + ax2.get_ygridlines():
                    line.set_color(grid_color)
            else:
                ax1.set_facecolor('#FFF8DC')  # Always light mode when solar disabled
                fig.patch.set_facecolor('white')
                ax2.set_facecolor('white')
                axis_color = 'black'
                spine_color = 'darkgray'
                title_color = 'black'
                # Apply default light colors
                for ax in [ax1, ax2]:
                    ax.tick_params(colors=axis_color)
                    ax.spines['bottom'].set_color(spine_color)
                    ax.spines['top'].set_color(spine_color)
                    ax.spines['left'].set_color(spine_color)
                    ax.spines['right'].set_color(spine_color)
                    ax.xaxis.label.set_color(axis_color)
                    ax.yaxis.label.set_color(axis_color)
                # Update grid color for ax2 (battery graph has grid)
                for line in ax2.get_xgridlines() + ax2.get_ygridlines():
                    line.set_color('gray')
            
            # Update step text with day/night info (only if solar enabled)
            step_info = ""
            if solar_enabled:
                step_info = f"{time_of_day}\n"
            step_info += f"Step: {frame}\n"
            step_info += f"Position: {current_pos}\n"
            step_info += f"Terrain: {terrain_name}"
            
            # Dynamic text box colors based on day/night (matches GUI)
            if solar_enabled and not is_day:
                step_box_color = '#2a2a4e'
                step_text_color = 'white'
                step_edge_color = 'cyan'
            else:
                step_box_color = 'lightyellow'
                step_text_color = 'black'
                step_edge_color = 'orange'
            
            step_text.set_text(step_info)
            step_text.set_color(step_text_color)
            step_text.set_bbox(dict(boxstyle='round', facecolor=step_box_color, alpha=0.9, 
                                   edgecolor=step_edge_color, linewidth=2))
            
            # Update battery text with day/night info (only if solar enabled)
            battery_info = ""
            if solar_enabled:
                battery_info = f"{time_of_day}\n"
            battery_info += f"Battery: {current_battery}%"
            if current_battery < 20:
                battery_info += "\n⚠️ CRITICAL!"
            elif current_battery <= 25:
                battery_info += "\n⚡ LOW"
            
            # Dynamic text box colors based on day/night (matches GUI)
            if solar_enabled and not is_day:
                battery_box_color = '#2a2a4e'
                battery_text_color = 'white'
                battery_edge_color = 'cyan'
            else:
                battery_box_color = 'lightyellow'
                battery_text_color = 'black'
                battery_edge_color = 'orange'
            
            battery_text.set_text(battery_info)
            battery_text.set_color(battery_text_color)
            battery_text.set_bbox(dict(boxstyle='round', facecolor=battery_box_color, alpha=0.9, 
                                      edgecolor=battery_edge_color, linewidth=2))
            
            # Update titles with day/night indicator and color (matches GUI)
            heuristic_name_formatted = heuristic_name.replace("_", " ").title()
            if solar_enabled and time_of_day:
                title_text = f'{time_of_day}\nRover Navigation - {heuristic_name_formatted}'
            else:
                title_text = f'Rover Navigation - {heuristic_name_formatted}'
            ax1.set_title(title_text, fontsize=14, fontweight='bold', color=title_color, pad=15)
            ax2.set_title('Battery Level Over Time', fontsize=14, fontweight='bold', color=title_color)
            
            # Update legend styling based on day/night (matches GUI)
            if solar_enabled and not is_day:
                # Night mode legend
                legend_ax1.get_frame().set_facecolor('#2a2a4e')
                legend_ax1.get_frame().set_edgecolor('cyan')
                legend_ax1.get_frame().set_alpha(0.9)
                for text in legend_ax1.get_texts():
                    text.set_color('white')
                    
                legend_ax2.get_frame().set_facecolor('#2a2a4e')
                legend_ax2.get_frame().set_edgecolor('cyan')
                legend_ax2.get_frame().set_alpha(0.9)
                for text in legend_ax2.get_texts():
                    text.set_color('white')
            else:
                # Day mode legend
                legend_ax1.get_frame().set_facecolor('white')
                legend_ax1.get_frame().set_edgecolor('darkgray')
                legend_ax1.get_frame().set_alpha(0.9)
                for text in legend_ax1.get_texts():
                    text.set_color('black')
                    
                legend_ax2.get_frame().set_facecolor('white')
                legend_ax2.get_frame().set_edgecolor('darkgray')
                legend_ax2.get_frame().set_alpha(0.9)
                for text in legend_ax2.get_texts():
                    text.set_color('black')
            
            # Check for events at this step
            event_info = ""
            for event in events:
                if event['step'] == frame:
                    event_type = event['type']
                    if event_type == 'recharge':
                        if solar_enabled:
                            recharge_msg = "☀️ SOLAR RECHARGE!\nBattery: 100%" if is_day else "🌙 NIGHT RECHARGE!\nBattery +50%"
                        else:
                            recharge_msg = "⚡ RECHARGE!\nBattery: 100%"
                        event_info = recharge_msg
                        # Flash effect for recharge
                        rover_marker.set_color('lime')
                        rover_marker.set_markersize(22)
                    elif event_type == 'backtrack':
                        event_info = "⚠️ BACKTRACK!\nHazard Detected"
                        rover_marker.set_color('red')
                        rover_marker.set_markersize(22)
                    elif event_type == 'critical_battery':
                        event_info = "🔋 OVERRIDE!\nSeeking Recharge"
                        rover_marker.set_color('orange')
                        rover_marker.set_markersize(22)
                    elif event_type == 'low_battery':
                        event_info = "⚡ LOW BATTERY!\nNearby Station"
                        rover_marker.set_color('yellow')
                        rover_marker.set_markersize(22)
                    elif event_type == 'storm_detected':
                        event_info = "🌪️ STORM!\nSeeking Shelter"
                        rover_marker.set_color('darkorange')
                        rover_marker.set_markersize(22)
                    elif event_type == 'storm_avoid':
                        event_info = "🌪️ AVOIDING STORM\nReplanning Path"
                        rover_marker.set_color('orange')
                        rover_marker.set_markersize(20)
                    break
            
            # Reset rover color if no event
            if not event_info:
                rover_marker.set_color('#1E90FF')
                rover_marker.set_markersize(18)
            
            event_text.set_text(event_info)
            
            # Build return list with all animated elements
            return_list = [rover_marker, path_trail, battery_line, battery_point, step_text, event_text, battery_text]
            if hasattr(self.env, 'dust_storms_enabled') and self.env.dust_storms_enabled:
                return_list.extend(storm_centers)
            return tuple(return_list)
        
        # Create animation
        print(f"\n🎬 Creating animation with {len(path)} frames...")
        anim = FuncAnimation(fig, animate, init_func=init,
                           frames=len(path), interval=500,  # 500ms per frame
                           blit=True, repeat=True)
        
        # Save as GIF
        print(f"💾 Saving animation to {save_path}...")
        writer = PillowWriter(fps=2)  # 2 frames per second
        anim.save(save_path, writer=writer, dpi=100)
        
        plt.close()
        print(f"✅ Animation saved successfully!")
        
        return save_path


def create_animation_with_events(env: Environment, 
                                 rover_path: List[Tuple[int, int]],
                                 battery_history: List[int],
                                 start: Tuple[int, int],
                                 goal: Tuple[int, int],
                                 heuristic_name: str,
                                 save_path: str = "rover_animation.gif") -> str:
    """
    Helper function to create animation with automatic event detection.
    
    Args:
        env: Environment instance
        rover_path: Complete path rover took
        battery_history: Battery levels at each step
        start: Start position
        goal: Goal position
        heuristic_name: Heuristic used
        save_path: Output file path
        
    Returns:
        Path to saved animation
    """
    # Detect events from path and battery history
    events = []
    
    for i in range(len(rover_path)):
        pos = rover_path[i]
        battery = battery_history[i]
        
        # Check for recharge
        if i > 0 and battery_history[i] > battery_history[i-1] + 50:
            events.append({
                'step': i,
                'type': 'recharge',
                'position': pos
            })
        
        # Check for critical battery
        elif battery < 20 and i > 0:
            events.append({
                'step': i,
                'type': 'critical_battery',
                'position': pos
            })
        
        # Check for low battery
        elif 20 <= battery <= 25 and i > 0:
            # Check if near recharge station
            nearest_station = env.find_nearest_recharge_station(pos[0], pos[1])
            if nearest_station:
                dist = env.euclidean_distance(pos, nearest_station)
                if dist <= 2:
                    events.append({
                        'step': i,
                        'type': 'low_battery',
                        'position': pos
                    })
        
        # Check for backtrack (position repeats)
        if i > 1 and rover_path[i] == rover_path[i-2]:
            events.append({
                'step': i,
                'type': 'backtrack',
                'position': pos
            })
    
    # Create animator and generate GIF
    animator = RoverAnimator(env)
    return animator.animate_rover_journey(
        rover_path, battery_history, events,
        start, goal, heuristic_name, save_path
    )
