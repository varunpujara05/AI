"""
Rover module with battery management and state tracking.
"""

from typing import Tuple, List, Optional
from environment import Environment, TerrainType


class Rover:
    """
    Represents the Mars Rover with battery management and position tracking.
    """
    
    def __init__(self, start_pos: Tuple[int, int], battery_capacity: int = 100, solar_power_enabled: bool = True):
        """
        Initialize the rover.
        
        Args:
            start_pos: Starting position (x, y)
            battery_capacity: Maximum battery capacity
            solar_power_enabled: Enable solar power management (day/night cycle)
        """
        self.position = start_pos
        self.battery = battery_capacity
        self.max_battery = battery_capacity
        self.path_history = [start_pos]
        self.battery_history = [battery_capacity]
        self.last_safe_position = start_pos
        self.total_distance_traveled = 0
        self.recharge_count = 0
        
        # Solar Power Management - Day/Night Cycle
        self.solar_power_enabled = solar_power_enabled
        self.step_count = 0
        self.day_night_cycle_length = 10  # 10 steps per cycle
        self.is_daytime = True  # Start with day
        self.day_night_history = [True]  # Track day/night for each step
        
    def get_battery_percentage(self) -> float:
        """Get current battery level as a percentage."""
        return (self.battery / self.max_battery) * 100
    
    def is_day(self) -> bool:
        """Check if it's currently daytime based on step count."""
        cycle_position = self.step_count % (self.day_night_cycle_length * 2)
        return cycle_position < self.day_night_cycle_length
    
    def get_time_of_day(self) -> str:
        """Get current time of day as string."""
        return "DAY" if self.is_daytime else "NIGHT"
    
    def needs_immediate_recharge(self) -> bool:
        """Check if battery is critically low (< 20%)."""
        return self.get_battery_percentage() < 20
    
    def should_seek_nearby_recharge(self) -> bool:
        """Check if battery is low (20-25%) and should seek nearby recharge."""
        battery_pct = self.get_battery_percentage()
        return 20 <= battery_pct <= 25
    
    def can_reach(self, target: Tuple[int, int], cost: int) -> bool:
        """Check if rover has enough battery to reach a target."""
        return self.battery >= cost
    
    def move_to(self, new_pos: Tuple[int, int], env: Environment) -> bool:
        """
        Move to a new position and update battery.
        
        Args:
            new_pos: Target position (x, y)
            env: Environment instance
            
        Returns:
            True if move was successful, False otherwise
        """
        # Use storm-adjusted cost if storms are enabled
        if hasattr(env, 'dust_storms_enabled') and env.dust_storms_enabled:
            cost = env.get_storm_adjusted_cost(new_pos[0], new_pos[1])
        else:
            cost = env.get_movement_cost(new_pos[0], new_pos[1])
        
        if cost == float('inf') or not self.can_reach(new_pos, cost):
            return False
        
        # Check if moving to a hazardous terrain
        if env.is_hazardous(new_pos[0], new_pos[1]):
            # Can move but need to track for reflex agent
            pass
        else:
            # Update last safe position if not hazardous
            self.last_safe_position = new_pos
        
        # Update position and battery
        self.position = new_pos
        self.battery -= cost
        
        # Increment step count and update day/night (if solar power enabled)
        self.step_count += 1
        if self.solar_power_enabled:
            self.is_daytime = self.is_day()
        
        # Check if at recharge station
        if env.get_terrain(new_pos[0], new_pos[1]) == TerrainType.RECHARGE_STATION:
            self.recharge()
        
        # Track history
        self.path_history.append(new_pos)
        self.battery_history.append(self.battery)
        if self.solar_power_enabled:
            self.day_night_history.append(self.is_daytime)
        
        # Calculate distance traveled
        if len(self.path_history) > 1:
            prev_pos = self.path_history[-2]
            distance = env.euclidean_distance(prev_pos, new_pos)
            self.total_distance_traveled += distance
        
        return True
    
    def recharge(self):
        """Recharge the battery based on time of day (Solar Power Management)."""
        if self.solar_power_enabled:
            if self.is_daytime:
                # DAY: Full solar charge to 100%
                self.battery = self.max_battery
                self.recharge_count += 1
                print(f"  ☀️ DAY - Full solar recharge! Battery: {self.battery}%")
            else:
                # NIGHT: Limited charge to 50% using stored batteries
                self.battery = min(self.battery + 50, self.max_battery)
                self.recharge_count += 1
                print(f"  🌙 NIGHT - Limited recharge! Battery: {self.battery}%")
        else:
            # Normal recharge - always full
            self.battery = self.max_battery
            self.recharge_count += 1
            print(f"  🔋 Rover recharged! Battery: {self.battery}%")
    
    def backtrack(self):
        """Move back to the last known safe position."""
        print(f"  ⚠️ Hazard detected! Backtracking to safe position: {self.last_safe_position}")
        self.position = self.last_safe_position
        self.step_count += 1
        if self.solar_power_enabled:
            self.is_daytime = self.is_day()
        self.path_history.append(self.last_safe_position)
        self.battery_history.append(self.battery)
        if self.solar_power_enabled:
            self.day_night_history.append(self.is_daytime)
    
    def get_stats(self) -> dict:
        """Get rover statistics."""
        return {
            'final_position': self.position,
            'final_battery': self.battery,
            'battery_percentage': self.get_battery_percentage(),
            'path_length': len(self.path_history),
            'distance_traveled': self.total_distance_traveled,
            'recharge_count': self.recharge_count
        }
    
    def reset(self, start_pos: Tuple[int, int]):
        """Reset rover to initial state."""
        self.position = start_pos
        self.battery = self.max_battery
        self.path_history = [start_pos]
        self.battery_history = [self.max_battery]
        self.last_safe_position = start_pos
        self.total_distance_traveled = 0
        self.recharge_count = 0
        self.step_count = 0
        self.is_daytime = True
        if self.solar_power_enabled:
            self.day_night_history = [True]
        else:
            self.day_night_history = []
