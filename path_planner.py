"""
A* Path Planning module with multiple heuristics.
Implements A* algorithm with 5 different heuristic functions for comparison.
"""

import heapq
import math
from typing import Tuple, List, Optional, Callable
from environment import Environment


class AStarPlanner:
    """
    A* path planner with multiple heuristic options.
    """
    
    def __init__(self, environment: Environment):
        """
        Initialize A* planner.
        
        Args:
            environment: Environment instance
        """
        self.env = environment
        self.nodes_expanded = 0
        
    def euclidean_heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Heuristic 1: Euclidean distance.
        Straight-line distance between two points.
        """
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
    
    def manhattan_heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Heuristic 2: Manhattan distance.
        Sum of absolute differences in coordinates (4-directional movement).
        """
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    def weighted_euclidean_heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Heuristic 3: Weighted Euclidean distance.
        Euclidean distance with a weight factor to make search more aggressive.
        Weight = 1.5 (can be adjusted for different behaviors)
        """
        return 1.5 * math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
    
    def risk_aware_heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Heuristic 4: Risk-Aware distance.
        Adds a safety penalty based on proximity to hazardous cells (radiation spots).
        Prefers routes that keep distance from hazards.
        """
        from environment import TerrainType
        
        # Base Euclidean distance
        base_dist = math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
        
        # Risk parameters
        alpha = 5.0  # Risk penalty weight
        decay = 2.0  # Decay rate for distance from hazards
        radius = 2   # Search radius for nearby hazards
        
        # Calculate hazard penalty
        x0, y0 = pos
        hazard_score = 0.0
        hazardous_types = {TerrainType.RADIATION_SPOT}
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < self.env.width and 0 <= y < self.env.height:
                    terrain = self.env.get_terrain(x, y)
                    if terrain in hazardous_types:
                        dist_to_hazard = math.sqrt(dx*dx + dy*dy)
                        hazard_score += math.exp(-dist_to_hazard / decay)
        
        return base_dist + alpha * hazard_score
    
    def terrain_cost_aware_heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Heuristic 5: Terrain-Cost-Aware distance.
        Scales heuristic by local terrain difficulty to prefer low-cost regions.
        Estimates expected terrain multiplier based on nearby cells.
        """
        # Base Euclidean distance
        base_dist = math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
        
        # Sample local terrain costs
        sample_radius = 2
        x0, y0 = pos
        total_cost = 0.0
        count = 0
        
        for dx in range(-sample_radius, sample_radius + 1):
            for dy in range(-sample_radius, sample_radius + 1):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < self.env.width and 0 <= y < self.env.height:
                    total_cost += self.env.get_movement_cost(x, y)
                    count += 1
        
        # Calculate average local terrain cost multiplier
        avg_cost = total_cost / max(1, count)
        
        # Scale base distance by terrain difficulty
        return base_dist * avg_cost
    
    def get_heuristic_function(self, heuristic_name: str) -> Callable:
        """
        Get heuristic function by name.
        
        Args:
            heuristic_name: Name of the heuristic
            
        Returns:
            Heuristic function
        """
        heuristics = {
            'euclidean': self.euclidean_heuristic,
            'manhattan': self.manhattan_heuristic,
            'weighted_euclidean': self.weighted_euclidean_heuristic,
            'risk_aware': self.risk_aware_heuristic,
            'terrain_cost_aware': self.terrain_cost_aware_heuristic
        }
        return heuristics.get(heuristic_name, self.euclidean_heuristic)
    
    def reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Reconstruct path from start to goal using came_from mapping.
        
        Args:
            came_from: Dictionary mapping positions to their predecessors
            current: Goal position
            
        Returns:
            List of positions from start to goal
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
    def plan_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  heuristic_name: str = 'euclidean') -> Optional[List[Tuple[int, int]]]:
        """
        Plan a path from start to goal using A* algorithm.
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            heuristic_name: Name of heuristic to use
            
        Returns:
            List of positions representing the path, or None if no path exists
        """
        self.nodes_expanded = 0
        
        # Get heuristic function
        heuristic = self.get_heuristic_function(heuristic_name)
        
        # Priority queue: (f_score, counter, position)
        # Counter is used to break ties consistently
        counter = 0
        open_set = [(heuristic(start, goal), counter, start)]
        heapq.heapify(open_set)
        
        # Track which positions we've visited
        closed_set = set()
        
        # Maps position to its predecessor
        came_from = {}
        
        # Cost from start to each position
        g_score = {start: 0}
        
        # Estimated total cost from start to goal through each position
        f_score = {start: heuristic(start, goal)}
        
        while open_set:
            # Get position with lowest f_score
            _, _, current = heapq.heappop(open_set)
            
            # Skip if already processed
            if current in closed_set:
                continue
            
            self.nodes_expanded += 1
            
            # Goal reached
            if current == goal:
                return self.reconstruct_path(came_from, current)
            
            closed_set.add(current)
            
            # Explore neighbors
            for neighbor in self.env.get_neighbors(current[0], current[1]):
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative g_score
                movement_cost = self.env.get_movement_cost(neighbor[0], neighbor[1])
                tentative_g = g_score[current] + movement_cost
                
                # If this path to neighbor is better than any previous one
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal)
                    f_score[neighbor] = f
                    
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))
        
        # No path found
        return None
    
    def get_stats(self) -> dict:
        """Get statistics from the last path planning operation."""
        return {
            'nodes_expanded': self.nodes_expanded
        }


def compare_heuristics(environment: Environment, start: Tuple[int, int], 
                       goal: Tuple[int, int]) -> dict:
    """
    Compare all 5 heuristics on the same problem.
    
    Args:
        environment: Environment instance
        start: Starting position
        goal: Goal position
        
    Returns:
        Dictionary containing comparison results
    """
    heuristics = ['euclidean', 'manhattan', 'weighted_euclidean', 'risk_aware', 'terrain_cost_aware']
    results = {}
    
    planner = AStarPlanner(environment)
    
    for heuristic_name in heuristics:
        path = planner.plan_path(start, goal, heuristic_name)
        stats = planner.get_stats()
        
        if path:
            # Calculate path cost
            path_cost = sum(
                environment.get_movement_cost(pos[0], pos[1]) 
                for pos in path[1:]  # Skip start position
            )
            
            results[heuristic_name] = {
                'path': path,
                'path_length': len(path),
                'path_cost': path_cost,
                'nodes_expanded': stats['nodes_expanded'],
                'found': True
            }
        else:
            results[heuristic_name] = {
                'path': None,
                'path_length': 0,
                'path_cost': float('inf'),
                'nodes_expanded': stats['nodes_expanded'],
                'found': False
            }
    
    return results
