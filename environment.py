"""
Environment module for the Planetary Exploration Rover.
Defines terrain types, grid world, and environment dynamics.
"""

import numpy as np
from enum import Enum
from typing import Tuple, List, Optional, Set
import random

class TerrainType(Enum):
    """Enumeration of terrain types with their associated battery costs."""
    FLAT = 5
    SANDY = 10
    SAND_TRAP = 17  # Difficult terrain, high battery cost
    RADIATION_SPOT = 15
    CLIFF = 20  # Very dangerous, highest battery cost
    ROCKY = 1000  # Impassable
    RECHARGE_STATION = 0  # No cost, recharges battery


class DustStorm:
    """Represents a moving Martian dust storm."""
    
    def __init__(self, center: Tuple[int, int], radius: int, direction: Tuple[int, int], speed: int = 1):
        """
        Initialize a dust storm.
        
        Args:
            center: Center position (x, y) of the storm
            radius: Radius of the storm effect
            direction: Movement direction (dx, dy) per step
            speed: Movement speed (cells per update)
        """
        self.center = list(center)  # Mutable for movement
        self.radius = radius
        self.direction = list(direction)
        self.speed = speed
        self.battery_drain_multiplier = 1.25  # 1.25x normal battery drain in storm
        self.affected_cells: Set[Tuple[int, int]] = set()
        self.update_affected_cells()
    
    def update_affected_cells(self):
        """Calculate all cells affected by the storm."""
        self.affected_cells.clear()
        cx, cy = int(self.center[0]), int(self.center[1])
        for dx in range(-self.radius, self.radius + 1):
            for dy in range(-self.radius, self.radius + 1):
                if dx*dx + dy*dy <= self.radius*self.radius:
                    self.affected_cells.add((cx + dx, cy + dy))
    
    def move(self, width: int, height: int):
        """Move the storm and bounce off boundaries."""
        # Update position
        self.center[0] += self.direction[0] * self.speed
        self.center[1] += self.direction[1] * self.speed
        
        # Bounce off boundaries and add some randomness
        if self.center[0] <= self.radius or self.center[0] >= width - self.radius:
            self.direction[0] = -self.direction[0]
            # Add slight vertical drift
            if random.random() > 0.7:
                self.direction[1] += random.choice([-1, 0, 1])
                self.direction[1] = max(-1, min(1, self.direction[1]))
        
        if self.center[1] <= self.radius or self.center[1] >= height - self.radius:
            self.direction[1] = -self.direction[1]
            # Add slight horizontal drift
            if random.random() > 0.7:
                self.direction[0] += random.choice([-1, 0, 1])
                self.direction[0] = max(-1, min(1, self.direction[0]))
        
        # Clamp to boundaries
        self.center[0] = max(self.radius, min(width - self.radius - 1, self.center[0]))
        self.center[1] = max(self.radius, min(height - self.radius - 1, self.center[1]))
        
        self.update_affected_cells()
    
    def is_in_storm(self, x: int, y: int) -> bool:
        """Check if a position is affected by the storm."""
        return (x, y) in self.affected_cells
    
    def get_center(self) -> Tuple[int, int]:
        """Get the current center position."""
        return (int(self.center[0]), int(self.center[1]))


class Environment:
    """
    Represents the Mars environment as a 2D grid with different terrain types.
    """
    
    def __init__(self, width: int = 20, height: int = 20, dust_storms_enabled: bool = True):
        """
        Initialize the environment.
        
        Args:
            width: Grid width
            height: Grid height
            dust_storms_enabled: Enable dynamic dust storms
        """
        self.width = width
        self.height = height
        self.grid = np.full((height, width), TerrainType.FLAT, dtype=object)
        self.recharge_stations = []
        
        # Dust storm system
        self.dust_storms_enabled = dust_storms_enabled
        self.dust_storms: List[DustStorm] = []
        self.storm_update_interval = 5  # Update storm positions every N steps
        self.step_counter = 0
        
    def set_terrain(self, x: int, y: int, terrain: TerrainType):
        """Set terrain type at a specific position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = terrain
            if terrain == TerrainType.RECHARGE_STATION:
                self.recharge_stations.append((x, y))
    
    def get_terrain(self, x: int, y: int) -> Optional[TerrainType]:
        """Get terrain type at a specific position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x]
        return None
    
    def is_passable(self, x: int, y: int) -> bool:
        """Check if a position is passable (not rocky or out of bounds)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        terrain = self.grid[y, x]
        return terrain != TerrainType.ROCKY
    
    def is_hazardous(self, x: int, y: int) -> bool:
        """
        Check if terrain at position is hazardous.
        
        HAZARDOUS (triggers RULE 3 backtrack):
        - RADIATION_SPOT, SAND_TRAP, CLIFF
        
        NOT hazardous (safe to traverse):
        - FLAT, SANDY, RECHARGE_STATION
        """
        terrain = self.get_terrain(x, y)
        return terrain in (TerrainType.RADIATION_SPOT, TerrainType.SAND_TRAP, TerrainType.CLIFF)
    
    def get_movement_cost(self, x: int, y: int) -> int:
        """Get battery cost for moving to a position."""
        terrain = self.get_terrain(x, y)
        if terrain is None:
            return float('inf')
        return terrain.value
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get all valid neighbors (4-directional movement only - no diagonals).
        Returns list of (x, y) tuples for horizontal and vertical movements.
        """
        neighbors = []
        # Only horizontal and vertical movements (no diagonals)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_passable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def create_sample_environment(self):
        """Create a sample Mars environment with various terrain types."""
        # Set random rocky obstacles
        np.random.seed(42)
        for _ in range(30):
            x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.set_terrain(x, y, TerrainType.ROCKY)
        
        # Set sandy areas
        for _ in range(25):
            x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.set_terrain(x, y, TerrainType.SANDY)
        
        # Set sand traps
        for _ in range(12):
            x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.set_terrain(x, y, TerrainType.SAND_TRAP)
        
        # Set radiation spots
        for _ in range(15):
            x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.set_terrain(x, y, TerrainType.RADIATION_SPOT)
        
        # Set cliffs (dangerous terrain)
        for _ in range(8):
            x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.set_terrain(x, y, TerrainType.CLIFF)
        
        # Place recharge stations strategically
        recharge_positions = [(5, 5), (15, 5), (10, 15), (5, 15)]
        for x, y in recharge_positions:
            self.set_terrain(x, y, TerrainType.RECHARGE_STATION)
        
        # Ensure start and goal are flat
        self.set_terrain(0, 0, TerrainType.FLAT)
        self.set_terrain(self.width - 1, self.height - 1, TerrainType.FLAT)
    
    def euclidean_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions."""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def find_nearest_recharge_station(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Find the nearest recharge station to a given position."""
        if not self.recharge_stations:
            return None
        
        nearest = min(self.recharge_stations, 
                     key=lambda station: self.euclidean_distance((x, y), station))
        return nearest
    
    def add_dust_storm(self, center: Tuple[int, int], radius: int = 3, 
                      direction: Tuple[int, int] = None, speed: int = 1):
        """Add a new dust storm to the environment."""
        if direction is None:
            # Random initial direction
            direction = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
            if direction == (0, 0):
                direction = (1, 0)
        
        storm = DustStorm(center, radius, direction, speed)
        self.dust_storms.append(storm)
    
    def update_dust_storms(self):
        """Update all dust storm positions."""
        if not self.dust_storms_enabled:
            return
        
        self.step_counter += 1
        if self.step_counter >= self.storm_update_interval:
            self.step_counter = 0
            for storm in self.dust_storms:
                storm.move(self.width, self.height)
    
    def is_in_dust_storm(self, x: int, y: int) -> bool:
        """Check if a position is currently in any dust storm."""
        if not self.dust_storms_enabled:
            return False
        
        for storm in self.dust_storms:
            if storm.is_in_storm(x, y):
                return True
        return False
    
    def is_safe_from_storms(self, x: int, y: int) -> bool:
        """Check if position is safe from storms (shelter at recharge station or not in storm)."""
        # Recharge stations provide shelter
        if self.get_terrain(x, y) == TerrainType.RECHARGE_STATION:
            return True
        return not self.is_in_dust_storm(x, y)
    
    def get_storm_adjusted_cost(self, x: int, y: int) -> int:
        """Get movement cost adjusted for dust storm effects."""
        base_cost = self.get_movement_cost(x, y)
        if base_cost == float('inf'):
            return base_cost
        
        # Apply storm multiplier if in storm and not at shelter
        if self.is_in_dust_storm(x, y) and self.get_terrain(x, y) != TerrainType.RECHARGE_STATION:
            for storm in self.dust_storms:
                if storm.is_in_storm(x, y):
                    return int(base_cost * storm.battery_drain_multiplier)
        
        return base_cost
    
    def get_active_storms(self) -> List[DustStorm]:
        """Get list of all active dust storms."""
        return self.dust_storms if self.dust_storms_enabled else []
    
    def clear_dust_storms(self):
        """Remove all dust storms."""
        self.dust_storms.clear()
        self.step_counter = 0
