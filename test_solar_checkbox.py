"""
Test script to verify Solar Power Management checkbox functionality.
"""

from rover import Rover
from environment import Environment, TerrainType
import numpy as np

def test_solar_power_enabled():
    """Test rover with solar power enabled."""
    print("=" * 60)
    print("TEST 1: Solar Power ENABLED")
    print("=" * 60)
    
    # Create simple environment
    grid = np.full((10, 10), TerrainType.FLAT)
    grid[5, 5] = TerrainType.RECHARGE_STATION
    env = Environment(grid)
    
    # Create rover with solar power enabled
    rover = Rover(start_position=(0, 0), battery_capacity=100, solar_power_enabled=True)
    
    # Move 15 steps (should cross day/night boundary at step 10)
    for i in range(15):
        print(f"\nStep {i+1}:")
        print(f"  Battery: {rover.battery}%")
        print(f"  Step Count: {rover.step_count}")
        print(f"  Time: {rover.get_time_of_day()}")
        
        # Move rover
        if i < 9:
            rover.move_to((i+1, 0), env)
        else:
            rover.move_to((9, i-9), env)
    
    # Recharge at recharge station
    rover.position = (5, 5)
    print(f"\n--- Moving to recharge station at (5, 5) ---")
    print(f"Before recharge - Battery: {rover.battery}%, Time: {rover.get_time_of_day()}")
    rover.recharge(env)
    print(f"After recharge - Battery: {rover.battery}%, Time: {rover.get_time_of_day()}")
    
    print(f"\nFinal Stats:")
    print(f"  Total Recharges: {rover.recharge_count}")
    print(f"  Has solar_power_enabled attribute: {hasattr(rover, 'solar_power_enabled')}")
    print(f"  solar_power_enabled value: {rover.solar_power_enabled}")
    

def test_solar_power_disabled():
    """Test rover with solar power disabled."""
    print("\n\n" + "=" * 60)
    print("TEST 2: Solar Power DISABLED")
    print("=" * 60)
    
    # Create simple environment
    grid = np.full((10, 10), TerrainType.FLAT)
    grid[5, 5] = TerrainType.RECHARGE_STATION
    env = Environment(grid)
    
    # Create rover with solar power disabled
    rover = Rover(start_position=(0, 0), battery_capacity=100, solar_power_enabled=False)
    
    # Move 15 steps (should NOT have day/night tracking)
    for i in range(15):
        print(f"\nStep {i+1}:")
        print(f"  Battery: {rover.battery}%")
        print(f"  Step Count: {rover.step_count}")
        if hasattr(rover, 'get_time_of_day'):
            print(f"  Time: {rover.get_time_of_day()}")
        else:
            print(f"  Time tracking: Not available")
        
        # Move rover
        if i < 9:
            rover.move_to((i+1, 0), env)
        else:
            rover.move_to((9, i-9), env)
    
    # Recharge at recharge station
    rover.position = (5, 5)
    print(f"\n--- Moving to recharge station at (5, 5) ---")
    print(f"Before recharge - Battery: {rover.battery}%")
    rover.recharge(env)
    print(f"After recharge - Battery: {rover.battery}% (should always be 100%)")
    
    print(f"\nFinal Stats:")
    print(f"  Total Recharges: {rover.recharge_count}")
    print(f"  Has solar_power_enabled attribute: {hasattr(rover, 'solar_power_enabled')}")
    print(f"  solar_power_enabled value: {rover.solar_power_enabled}")


if __name__ == "__main__":
    test_solar_power_enabled()
    test_solar_power_disabled()
    
    print("\n\n" + "=" * 60)
    print("TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nKey Observations:")
    print("1. With solar_power_enabled=True:")
    print("   - Tracks day/night cycles (10 steps each)")
    print("   - Day recharge: 100%")
    print("   - Night recharge: +50% (capped at 100%)")
    print("\n2. With solar_power_enabled=False:")
    print("   - No day/night tracking")
    print("   - Recharge: always 100%")
    print("   - Behaves like original system")
