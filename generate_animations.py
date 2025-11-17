"""
Generate animated GIFs for rover navigation.
Run this after main.py to create animations from simulation results.
"""

from environment import Environment
from rover import Rover
from reflex_agent import ReflexAgent
from path_planner import AStarPlanner
from animation import create_animation_with_events
import os


def simulate_with_animation(env: Environment, start, goal, heuristic_name: str):
    """Run simulation and capture data for animation."""
    print(f"\n{'='*70}")
    print(f"🚀 Simulating with {heuristic_name.upper()} heuristic for animation")
    print(f"{'='*70}")
    
    # Initialize rover and agents
    rover = Rover(start_pos=start, battery_capacity=100)
    planner = AStarPlanner(env)
    reflex_agent = ReflexAgent(rover, env)
    
    # Track special events
    events = []
    backtrack_count = 0
    
    # Plan initial path
    print(f"📍 Planning initial path...")
    planned_path = planner.plan_path(start, goal, heuristic_name)
    
    if not planned_path:
        print("❌ No path found!")
        return None
    
    print(f"✅ Path found! Length: {len(planned_path)} steps")
    
    # Execute path with reflex agent
    current_path_index = 1
    step_count = 0
    replan_count = 0
    
    while rover.position != goal and step_count < 1000:
        step_count += 1
        
        # Get next move
        if current_path_index < len(planned_path):
            next_move = planned_path[current_path_index]
        else:
            planned_path = planner.plan_path(rover.position, goal, heuristic_name)
            if not planned_path or len(planned_path) < 2:
                break
            current_path_index = 1
            replan_count += 1
            continue
        
        battery_before = rover.battery
        position_before = rover.position
        
        # Reflex agent decision
        action, override_target = reflex_agent.decide_action(next_move)
        
        # Execute action
        if action == 'move':
            success = reflex_agent.execute_action(action, next_move)
            
            if success:
                current_path_index += 1
                
                # Check if recharged
                if rover.battery == rover.max_battery and battery_before < rover.max_battery:
                    events.append({
                        'step': len(rover.path_history) - 1,
                        'type': 'recharge',
                        'position': rover.position
                    })
            else:
                # Check if this was a backtrack
                if rover.position != position_before:
                    backtrack_count += 1
                    events.append({
                        'step': len(rover.path_history) - 1,
                        'type': 'backtrack',
                        'position': rover.position
                    })
                    
                    # Replan
                    planned_path = planner.plan_path(rover.position, goal, heuristic_name)
                    if not planned_path:
                        break
                    current_path_index = 1
                    replan_count += 1
                else:
                    break
        
        elif action == 'recharge_override':
            battery_pct = rover.get_battery_percentage()
            
            if battery_pct < 20:
                events.append({
                    'step': len(rover.path_history) - 1,
                    'type': 'critical_battery',
                    'position': rover.position
                })
            else:
                events.append({
                    'step': len(rover.path_history) - 1,
                    'type': 'low_battery',
                    'position': rover.position
                })
            
            # Navigate to station
            recharge_path = planner.plan_path(rover.position, override_target, heuristic_name)
            if recharge_path:
                for i in range(1, len(recharge_path)):
                    if not rover.move_to(recharge_path[i], env):
                        break
                
                events.append({
                    'step': len(rover.path_history) - 1,
                    'type': 'recharge',
                    'position': rover.position
                })
                
                planned_path = planner.plan_path(rover.position, goal, heuristic_name)
                if not planned_path:
                    break
                current_path_index = 1
                replan_count += 1
            else:
                break
        
        else:
            break
    
    success = (rover.position == goal)
    
    if success:
        print(f"✅ Goal reached! Backtracks: {backtrack_count}")
        return {
            'path': rover.path_history,
            'battery_history': rover.battery_history,
            'events': events,
            'backtrack_count': backtrack_count
        }
    else:
        print(f"❌ Failed to reach goal")
        return None


def main():
    """Generate animations for all heuristics."""
    print("="*70)
    print("ROVER ANIMATION GENERATOR")
    print("="*70)
    
    # Create output directory
    output_dir = "animations"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create environment
    print("\n🌍 Creating Mars environment...")
    env = Environment(width=20, height=20)
    env.create_sample_environment()
    
    # Define start and goal
    start = (1, 1)
    goal = (18, 18)
    
    # Heuristics to animate
    heuristics = ['euclidean', 'manhattan', 'weighted_euclidean', 'risk_aware', 'terrain_cost_aware']
    
    print(f"\n📹 Generating animations for {len(heuristics)} heuristics...")
    print(f"   Start: {start}")
    print(f"   Goal: {goal}")
    print(f"   Output: {output_dir}/")
    
    # Generate animation for each heuristic
    for heuristic in heuristics:
        print(f"\n{'-'*70}")
        
        # Run simulation
        result = simulate_with_animation(env, start, goal, heuristic)
        
        if result and result['success']:
            # Create animation
            output_file = f"{output_dir}/rover_{heuristic}.gif"
            
            try:
                create_animation_with_events(
                    env,
                    result['path'],
                    result['battery_history'],
                    start,
                    goal,
                    heuristic,
                    output_file
                )
                print(f"✅ Animation saved: {output_file}")
            except Exception as e:
                print(f"❌ Error creating animation: {e}")
        else:
            print(f"⚠️ Skipping animation (simulation failed)")
    
    print(f"\n{'='*70}")
    print(f"✅ Animation generation complete!")
    print(f"📁 Check '{output_dir}/' directory for GIF files")
    print(f"{'='*70}")
    
    # Print summary
    print("\n📊 Generated Animations:")
    for heuristic in heuristics:
        gif_path = f"{output_dir}/rover_{heuristic}.gif"
        if os.path.exists(gif_path):
            size_mb = os.path.getsize(gif_path) / (1024 * 1024)
            print(f"   ✅ {gif_path} ({size_mb:.2f} MB)")
        else:
            print(f"   ❌ {gif_path} (not created)")


if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    main()
