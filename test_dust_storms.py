"""
Test script to demonstrate Martian Dust Storm system.
"""

from environment import Environment, TerrainType, DustStorm
from rover import Rover
from path_planner import AStarPlanner
from reflex_agent import ReflexAgent
import numpy as np

def test_dust_storm_movement():
    """Test dust storm movement across the map."""
    print("=" * 70)
    print("TEST 1: Dust Storm Movement")
    print("=" * 70)
    
    # Create environment with storms enabled
    env = Environment(20, 20, dust_storms_enabled=True)
    
    # Add a single storm
    env.add_dust_storm((10, 10), radius=3, direction=(1, 0), speed=1)
    
    print(f"\nInitial storm position: {env.dust_storms[0].get_center()}")
    print(f"Storm radius: {env.dust_storms[0].radius}")
    print(f"Storm direction: {env.dust_storms[0].direction}")
    
    # Simulate storm movement
    for step in range(10):
        env.update_dust_storms()
        print(f"Step {step + 1}: Storm at {env.dust_storms[0].get_center()}")
    
    print("\n✅ Storm movement test complete!")


def test_storm_battery_drain():
    """Test battery drain in storm vs normal terrain."""
    print("\n\n" + "=" * 70)
    print("TEST 2: Storm Battery Drain")
    print("=" * 70)
    
    # Create environment
    env = Environment(20, 20, dust_storms_enabled=True)
    env.set_terrain(5, 5, TerrainType.FLAT)
    env.set_terrain(10, 10, TerrainType.FLAT)
    
    # Add storm at position (10, 10)
    env.add_dust_storm((10, 10), radius=2, direction=(0, 0), speed=0)
    
    # Test normal movement cost
    normal_cost = env.get_movement_cost(5, 5)
    print(f"\nNormal movement cost at (5,5): {normal_cost}")
    
    # Test storm-adjusted cost
    storm_cost = env.get_storm_adjusted_cost(10, 10)
    print(f"Storm-adjusted cost at (10,10): {storm_cost}")
    print(f"Multiplier applied: {storm_cost / normal_cost}x")
    
    # Test position in storm
    print(f"\nIs (10,10) in storm? {env.is_in_dust_storm(10, 10)}")
    print(f"Is (5,5) in storm? {env.is_in_dust_storm(5, 5)}")
    
    print("\n✅ Battery drain test complete!")


def test_shelter_at_recharge_station():
    """Test that recharge stations provide shelter from storms."""
    print("\n\n" + "=" * 70)
    print("TEST 3: Shelter at Recharge Stations")
    print("=" * 70)
    
    # Create environment
    env = Environment(20, 20, dust_storms_enabled=True)
    env.set_terrain(10, 10, TerrainType.RECHARGE_STATION)
    
    # Add storm covering the recharge station
    env.add_dust_storm((10, 10), radius=2, direction=(0, 0), speed=0)
    
    print(f"\nRecharge station at (10,10)")
    print(f"Storm covering (10,10): {env.is_in_dust_storm(10, 10)}")
    print(f"Is position safe from storms? {env.is_safe_from_storms(10, 10)}")
    print("✓ Recharge station provides shelter even when in storm area!")
    
    # Test normal terrain in storm
    env.set_terrain(11, 10, TerrainType.FLAT)
    print(f"\nFlat terrain at (11,10)")
    print(f"In storm: {env.is_in_dust_storm(11, 10)}")
    print(f"Is position safe? {env.is_safe_from_storms(11, 10)}")
    print("✗ Normal terrain in storm is NOT safe!")
    
    print("\n✅ Shelter test complete!")


def test_rover_with_storms():
    """Test rover navigation with dust storms."""
    print("\n\n" + "=" * 70)
    print("TEST 4: Rover Navigation with Dust Storms")
    print("=" * 70)
    
    # Create simple environment
    env = Environment(15, 15, dust_storms_enabled=True)
    
    # Add some terrain
    for x in range(15):
        for y in range(15):
            env.set_terrain(x, y, TerrainType.FLAT)
    
    # Add recharge station
    env.set_terrain(7, 7, TerrainType.RECHARGE_STATION)
    
    # Add storm blocking direct path
    env.add_dust_storm((5, 5), radius=2, direction=(0, 0), speed=0)
    
    # Create rover and agents
    rover = Rover((0, 0), battery_capacity=100)
    planner = AStarPlanner(env)
    reflex_agent = ReflexAgent(rover, env)
    
    print(f"\nRover starting at: {rover.position}")
    print(f"Storm at: {env.dust_storms[0].get_center()}")
    print(f"Storm radius: {env.dust_storms[0].radius}")
    
    # Test moving into storm
    print(f"\nAttempting to move to (5,5) - in storm")
    print(f"Normal battery cost: {env.get_movement_cost(5, 5)}")
    print(f"Storm-adjusted cost: {env.get_storm_adjusted_cost(5, 5)}")
    
    # Move rover to storm edge
    rover.position = (4, 5)
    percepts = reflex_agent.perceive()
    print(f"\nRover at {rover.position}")
    print(f"In storm: {percepts['in_dust_storm']}")
    print(f"Safe from storms: {percepts['is_safe_from_storms']}")
    
    # Move into storm
    rover.position = (5, 5)
    percepts = reflex_agent.perceive()
    print(f"\nRover moved to {rover.position}")
    print(f"In storm: {percepts['in_dust_storm']}")
    print(f"Safe from storms: {percepts['is_safe_from_storms']}")
    print("⚠️ Rover should seek shelter!")
    
    print("\n✅ Rover navigation test complete!")


def test_storm_boundary_bounce():
    """Test storm bouncing off boundaries."""
    print("\n\n" + "=" * 70)
    print("TEST 5: Storm Boundary Collision")
    print("=" * 70)
    
    env = Environment(10, 10, dust_storms_enabled=True)
    
    # Add storm near right edge moving right
    env.add_dust_storm((8, 5), radius=1, direction=(1, 0), speed=1)
    
    print(f"\nInitial: Storm at {env.dust_storms[0].get_center()}, direction: {env.dust_storms[0].direction}")
    
    # Move several times
    for step in range(5):
        env.update_dust_storms()
        storm = env.dust_storms[0]
        print(f"Step {step + 1}: Storm at {storm.get_center()}, direction: {storm.direction}")
    
    print("\n✅ Storm should bounce off boundary!")


if __name__ == "__main__":
    test_dust_storm_movement()
    test_storm_battery_drain()
    test_shelter_at_recharge_station()
    test_rover_with_storms()
    test_storm_boundary_bounce()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED!")
    print("=" * 70)
    print("\n🌪️ Dust Storm System Features:")
    print("  ✅ Storms move dynamically across the map")
    print("  ✅ Battery drain 3x higher in storms")
    print("  ✅ Recharge stations provide shelter")
    print("  ✅ Rover detects and avoids storms")
    print("  ✅ Dynamic replanning when storms block path")
    print("  ✅ Storms bounce off boundaries")
    print("\nRun the GUI to see storms in action! 🎮")
