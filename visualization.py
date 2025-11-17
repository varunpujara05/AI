"""
Visualization module for the Planetary Exploration Rover.
Creates visualizations of the environment, rover path, and comparisons.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np
from typing import List, Tuple, Dict
from environment import Environment, TerrainType


class RoverVisualizer:
    """
    Handles visualization of the rover's environment and path.
    """
    
    # Color scheme for different terrain types
    TERRAIN_COLORS = {
        TerrainType.FLAT: '#F5DEB3',          # Wheat (flat terrain)
        TerrainType.SANDY: '#F4A460',         # Sandy brown
        TerrainType.SAND_TRAP: "#A27F65",     # Saddle brown (dark brown for sand trap)
        TerrainType.RADIATION_SPOT: "#E10D0D", # Medium purple (distinct from sand trap)
        TerrainType.CLIFF: '#654321',         # Dark brown (steep cliff)
        TerrainType.ROCKY: '#2F4F4F',         # Dark slate gray (impassable)
        TerrainType.RECHARGE_STATION: '#32CD32' # Lime green
    }
    
    def __init__(self, environment: Environment):
        """
        Initialize visualizer.
        
        Args:
            environment: Environment instance
        """
        self.env = environment
        
    def create_terrain_grid(self) -> np.ndarray:
        """Create a numerical representation of terrain for visualization."""
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
    
    def plot_environment(self, ax=None, show_grid: bool = True):
        """
        Plot the environment with terrain types.
        
        Args:
            ax: Matplotlib axis (creates new if None)
            show_grid: Whether to show grid lines
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        
        grid = self.create_terrain_grid()
        
        # Create custom colormap
        colors = [
            self.TERRAIN_COLORS[TerrainType.FLAT],
            self.TERRAIN_COLORS[TerrainType.SANDY],
            self.TERRAIN_COLORS[TerrainType.SAND_TRAP],
            self.TERRAIN_COLORS[TerrainType.RADIATION_SPOT],
            self.TERRAIN_COLORS[TerrainType.CLIFF],
            self.TERRAIN_COLORS[TerrainType.ROCKY],
            self.TERRAIN_COLORS[TerrainType.RECHARGE_STATION]
        ]
        cmap = ListedColormap(colors)
        
        # Plot terrain
        im = ax.imshow(grid, cmap=cmap, origin='lower', aspect='equal')
        
        if show_grid:
            ax.set_xticks(np.arange(-0.5, self.env.width, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, self.env.height, 1), minor=True)
            ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        
        ax.set_xlim(-0.5, self.env.width - 0.5)
        ax.set_ylim(-0.5, self.env.height - 0.5)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        # Create legend
        legend_elements = [
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.FLAT], label='Flat (cost: 5)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.SANDY], label='Sandy (cost: 10)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.SAND_TRAP], label='Sand Trap (cost: 17)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.RADIATION_SPOT], label='Radiation (cost: 15)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.CLIFF], label='Cliff (cost: 20)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.ROCKY], label='Rocky (impassable)'),
            mpatches.Patch(color=self.TERRAIN_COLORS[TerrainType.RECHARGE_STATION], label='Recharge Station')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))
        
        return ax
    
    def plot_path(self, path: List[Tuple[int, int]], ax=None, 
                  color: str = 'blue', label: str = 'Path', 
                  start_marker: str = 'o', goal_marker: str = '*'):
        """
        Plot a path on the environment.
        
        Args:
            path: List of (x, y) positions
            ax: Matplotlib axis
            color: Path color
            label: Path label for legend
            start_marker: Marker for start position
            goal_marker: Marker for goal position
        """
        if not path or len(path) == 0:
            return ax
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
            self.plot_environment(ax)
        
        # Extract x and y coordinates
        x_coords = [pos[0] for pos in path]
        y_coords = [pos[1] for pos in path]
        
        # Plot path
        ax.plot(x_coords, y_coords, color=color, linewidth=2, 
                label=label, alpha=0.7, marker='.')
        
        # Mark start and goal
        ax.plot(x_coords[0], y_coords[0], marker=start_marker, 
                color='green', markersize=15, label='Start', zorder=5)
        ax.plot(x_coords[-1], y_coords[-1], marker=goal_marker, 
                color='red', markersize=20, label='Goal', zorder=5)
        
        return ax
    
    def plot_battery_history(self, battery_history: List[int], ax=None):
        """
        Plot battery level over time.
        
        Args:
            battery_history: List of battery levels
            ax: Matplotlib axis
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 5))
        
        steps = range(len(battery_history))
        ax.plot(steps, battery_history, linewidth=2, color='blue')
        ax.axhline(y=20, color='red', linestyle='--', label='Critical Level (20%)')
        ax.axhline(y=25, color='orange', linestyle='--', label='Low Level (25%)')
        ax.fill_between(steps, 0, 20, alpha=0.2, color='red')
        ax.fill_between(steps, 20, 25, alpha=0.2, color='orange')
        
        ax.set_xlabel('Step')
        ax.set_ylabel('Battery Level')
        ax.set_title('Battery Level Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def visualize_single_run(self, path: List[Tuple[int, int]], 
                            battery_history: List[int],
                            heuristic_name: str,
                            stats: dict,
                            save_path: str = None):
        """
        Create comprehensive visualization for a single run.
        
        Args:
            path: Rover's path
            battery_history: Battery levels over time
            heuristic_name: Name of heuristic used
            stats: Statistics dictionary
            save_path: Path to save figure (optional)
        """
        fig = plt.figure(figsize=(16, 6))
        
        # Create grid for subplots
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        ax1 = fig.add_subplot(gs[:, 0])  # Environment and path (spans both rows)
        ax2 = fig.add_subplot(gs[0, 1])  # Battery history
        ax3 = fig.add_subplot(gs[1, 1])  # Statistics
        
        # Plot environment and path
        self.plot_environment(ax1)
        self.plot_path(path, ax1, color='blue', label=f'Path ({heuristic_name})')
        ax1.set_title(f'Rover Path - {heuristic_name.replace("_", " ").title()} Heuristic')
        ax1.legend()
        
        # Plot battery history
        self.plot_battery_history(battery_history, ax2)
        
        # Display statistics
        ax3.axis('off')
        stats_text = f"""
        Heuristic: {heuristic_name.replace('_', ' ').title()}
        
        Path Length: {stats.get('path_length', 'N/A')} steps
        Distance Traveled: {stats.get('distance_traveled', 0):.2f} units
        Final Battery: {stats.get('final_battery', 'N/A')}%
        Recharge Count: {stats.get('recharge_count', 0)}
        Nodes Expanded: {stats.get('nodes_expanded', 'N/A')}
        """
        ax3.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax3.set_title('Run Statistics', fontsize=14, fontweight='bold')
        
        plt.suptitle(f'Planetary Rover Exploration - {heuristic_name.replace("_", " ").title()}', 
                     fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  📊 Saved visualization to {save_path}")
        
        return fig
    
    def compare_heuristics_visualization(self, results: Dict, save_path: str = None):
        """
        Create comparison visualization for all heuristics.
        
        Args:
            results: Dictionary containing results for each heuristic
            save_path: Path to save figure (optional)
        """
        heuristics = list(results.keys())
        n_heuristics = len(heuristics)
        
        fig, axes = plt.subplots(2, 2, figsize=(18, 16))
        axes = axes.flatten()
        
        colors = ['blue', 'red', 'green', 'purple']
        
        for idx, (heuristic, color) in enumerate(zip(heuristics, colors)):
            ax = axes[idx]
            result = results[heuristic]
            
            # Plot environment
            self.plot_environment(ax, show_grid=False)
            
            # Plot path if found
            if result['found'] and result['path']:
                self.plot_path(result['path'], ax, color=color, 
                             label=f"{heuristic.replace('_', ' ').title()}")
            
            # Add statistics as text
            stats_text = f"Steps: {result['path_length']}\n"
            stats_text += f"Cost: {result['path_cost']}\n"
            stats_text += f"Nodes: {result['nodes_expanded']}"
            
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax.set_title(f"{heuristic.replace('_', ' ').title()} Heuristic", 
                        fontsize=12, fontweight='bold')
            ax.legend(loc='lower right')
        
        plt.suptitle('Comparison of A* Heuristics for Rover Navigation', 
                     fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  📊 Saved comparison visualization to {save_path}")
        
        return fig
    
    def plot_comparison_metrics(self, results: Dict, save_path: str = None):
        """
        Create bar charts comparing metrics across heuristics.
        
        Args:
            results: Dictionary containing results for each heuristic
            save_path: Path to save figure (optional)
        """
        heuristics = list(results.keys())
        
        # Extract metrics
        path_lengths = [results[h]['path_length'] for h in heuristics]
        path_costs = [results[h]['path_cost'] if results[h]['path_cost'] != float('inf') 
                     else 0 for h in heuristics]
        nodes_expanded = [results[h]['nodes_expanded'] for h in heuristics]
        
        # Create subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        x_pos = np.arange(len(heuristics))
        
        # Plot path lengths
        axes[0].bar(x_pos, path_lengths, color=colors, alpha=0.7)
        axes[0].set_xlabel('Heuristic')
        axes[0].set_ylabel('Path Length (steps)')
        axes[0].set_title('Path Length Comparison')
        axes[0].set_xticks(x_pos)
        axes[0].set_xticklabels([h.replace('_', '\n') for h in heuristics], rotation=0)
        axes[0].grid(axis='y', alpha=0.3)
        
        # Plot path costs
        axes[1].bar(x_pos, path_costs, color=colors, alpha=0.7)
        axes[1].set_xlabel('Heuristic')
        axes[1].set_ylabel('Path Cost (battery units)')
        axes[1].set_title('Path Cost Comparison')
        axes[1].set_xticks(x_pos)
        axes[1].set_xticklabels([h.replace('_', '\n') for h in heuristics], rotation=0)
        axes[1].grid(axis='y', alpha=0.3)
        
        # Plot nodes expanded
        axes[2].bar(x_pos, nodes_expanded, color=colors, alpha=0.7)
        axes[2].set_xlabel('Heuristic')
        axes[2].set_ylabel('Nodes Expanded')
        axes[2].set_title('Computational Efficiency Comparison')
        axes[2].set_xticks(x_pos)
        axes[2].set_xticklabels([h.replace('_', '\n') for h in heuristics], rotation=0)
        axes[2].grid(axis='y', alpha=0.3)
        
        plt.suptitle('Performance Metrics Comparison Across Heuristics', 
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  📊 Saved metrics comparison to {save_path}")
        
        return fig
