"""
Reflex Agent module for the Planetary Exploration Rover.
Handles decision-making based on percepts (battery, terrain, proximity to recharge stations).
"""

from typing import Tuple, Optional, List
from rover import Rover
from environment import Environment, TerrainType


class ReflexAgent:
    """
    Reflex agent that makes decisions based on current percepts.
    
    Rules:
    1. Initiate recharge when battery < 20%
    2. Avoid impassable obstacles (rocks)
    3. If terrain is hazardous at current cell, stop and backtrack
    4. If battery 20-25% and recharge station within 2 moves, go to recharge
    """
    
    def __init__(self, rover: Rover, environment: Environment):
        """
        Initialize reflex agent.
        
        Args:
            rover: Rover instance
            environment: Environment instance
        """
        self.rover = rover
        self.env = environment
        
    def perceive(self) -> dict:
        """
        Gather percepts from the current state.
        
        Returns:
            Dictionary containing current percepts
        """
        x, y = self.rover.position
        
        percepts = {
            'position': (x, y),
            'battery_level': self.rover.battery,
            'battery_percentage': self.rover.get_battery_percentage(),
            'terrain': self.env.get_terrain(x, y),
            'is_hazardous': self.env.is_hazardous(x, y),
            'nearest_recharge': self.env.find_nearest_recharge_station(x, y),
            'recharge_distance': None,
            'in_dust_storm': self.env.is_in_dust_storm(x, y) if hasattr(self.env, 'is_in_dust_storm') else False,
            'is_safe_from_storms': self.env.is_safe_from_storms(x, y) if hasattr(self.env, 'is_safe_from_storms') else True
        }
        
        # Calculate distance to nearest recharge station
        if percepts['nearest_recharge']:
            percepts['recharge_distance'] = self.env.euclidean_distance(
                (x, y), percepts['nearest_recharge']
            )
        
        return percepts
    
    def should_override_for_recharge(self, percepts: dict) -> bool:
        """
        Check if rover should override exploration to seek recharge.
        
        Rule: Battery 20-25% and recharge station within 2 moves (Euclidean distance ≤ 2)
        """
        battery_pct = percepts['battery_percentage']
        recharge_dist = percepts['recharge_distance']
        
        if recharge_dist is not None and 20 <= battery_pct <= 25 and recharge_dist <= 2:
            return True
        return False
    
    def decide_action(self, planned_next_move):
        """
        Decide what action to take based on current percepts.
        
        NOTE: Hazard detection happens AFTER move in execute_action,
        so this primarily handles battery and movement decisions.
        
        Args:
            planned_next_move: The next position from A* planner
            
        Returns:
            Tuple of (action, target_position)
        """
        percepts = self.perceive()
        
        # STORM RULE: If in dust storm and not at shelter, seek nearest recharge station
        if percepts['in_dust_storm'] and not percepts['is_safe_from_storms']:
            print("🌪️ DUST STORM! Seeking shelter at recharge station...")
            nearest_station = percepts['nearest_recharge']
            if nearest_station:
                return ('storm_shelter', nearest_station)
        
        # Rule 1: Critical battery (< 20%) - highest priority
        if self.rover.needs_immediate_recharge():
            nearest_station = percepts['nearest_recharge']
            if nearest_station:
                return ('recharge_override', nearest_station)
            else:
                print("⚠️ Critical battery but no recharge station available!")
                return ('stop', None)
        
        # Rule 4: Low battery (20-25%) and recharge station within 2 moves
        if self.should_override_for_recharge(percepts):
            return ('recharge_override', percepts['nearest_recharge'])
        
        # Check if planned next move is in a storm - avoid it if possible
        if planned_next_move and hasattr(self.env, 'is_in_dust_storm'):
            if self.env.is_in_dust_storm(planned_next_move[0], planned_next_move[1]):
                # Check if it's a shelter location
                if self.env.get_terrain(planned_next_move[0], planned_next_move[1]) != TerrainType.RECHARGE_STATION:
                    print(f"⚠️ Storm detected at planned move {planned_next_move}, attempting to avoid...")
                    return ('storm_avoid', planned_next_move)
        
        # Normal movement (Rule 2 handled by A* planner)
        if planned_next_move:
            # Check if next move is passable
            if self.env.is_passable(planned_next_move[0], planned_next_move[1]):
                return ('move', planned_next_move)
            else:
                print(f"⚠️ Planned move to {planned_next_move} is impassable!")
                return ('stop', None)
        
        return ('stop', None)
    
    def execute_action(self, action: str, target) -> bool:
        """
        Execute the decided action.
        
        RULE 3 is checked HERE - after the move is executed.
        
        Args:
            action: Action to execute
            target: Target position or None
            
        Returns:
            True if action was successful
        """
        if action == 'move':
            if target:
                # Execute the move
                success = self.rover.move_to(target, self.env)
                
                if success:
                    # RULE 3: Check if current position is hazardous (AFTER entering)
                    current_x, current_y = self.rover.position
                    if self.env.is_hazardous(current_x, current_y):
                        terrain = self.env.get_terrain(current_x, current_y)
                        print(f"\n   🔴 RULE 3 TRIGGERED!")
                        print(f"   Hazard detected at {self.rover.position}!")
                        print(f"   Terrain: {terrain.name}")
                        print(f"   Executing: STOP and BACKTRACK")
                        
                        # Backtrack immediately
                        self.rover.backtrack()
                        print(f"   ✅ Backtracked to safe position: {self.rover.position}")
                        
                        # Return False to signal need for replanning
                        return False
                    
                return success
            return False
        
        elif action == 'backtrack':
            self.rover.backtrack()
            return True
        
        elif action == 'stop':
            return False
        
        return False
