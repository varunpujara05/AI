"""
Main simulation script for the Planetary Exploration Rover.
Runs simulations with different heuristics and generates visualizations.
"""

import os
from typing import Tuple
from environment import Environment, TerrainType
from rover import Rover
from reflex_agent import ReflexAgent
from path_planner import AStarPlanner, compare_heuristics
from visualization import RoverVisualizer


def simulate_rover(env: Environment, start: Tuple[int, int], goal: Tuple[int, int],
                   heuristic_name: str, verbose: bool = True) -> dict:
    """
    Simulate rover navigation using specified heuristic.
    
    Args:
        env: Environment instance
        start: Starting position
        goal: Goal position
        heuristic_name: Name of heuristic to use
        verbose: Whether to print progress
        
    Returns:
        Dictionary containing simulation results
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"🚀 Starting simulation with {heuristic_name.upper()} heuristic")
        print(f"{'='*70}")
        print(f"Start: {start}, Goal: {goal}")
    
    # Initialize rover and agents
    rover = Rover(start_pos=start, battery_capacity=100)
    planner = AStarPlanner(env)
    reflex_agent = ReflexAgent(rover, env)
    
    # Plan initial path
    if verbose:
        print(f"\n📍 Planning initial path using {heuristic_name} heuristic...")
    
    planned_path = planner.plan_path(start, goal, heuristic_name)
    
    if not planned_path:
        print("❌ No path found to goal!")
        return {
            'success': False,
            'rover': rover,
            'planner_stats': planner.get_stats(),
            'heuristic': heuristic_name
        }
    
    if verbose:
        print(f"✅ Path found! Length: {len(planned_path)} steps")
        print(f"   Nodes expanded: {planner.get_stats()['nodes_expanded']}")
    
    # Execute path with reflex agent
    current_path_index = 1  # Start from index 1 (skip start position)
    replan_count = 0
    
    while rover.position != goal:
        # Get next planned move
        if current_path_index < len(planned_path):
            next_move = planned_path[current_path_index]
        else:
            # Reached end of path but not at goal, need to replan
            if verbose:
                print(f"\n🔄 Replanning from {rover.position} to {goal}")
            planned_path = planner.plan_path(rover.position, goal, heuristic_name)
            if not planned_path:
                if verbose:
                    print("❌ Cannot reach goal from current position!")
                break
            current_path_index = 1
            replan_count += 1
            continue
        
        # Let reflex agent decide action
        action, override_target = reflex_agent.decide_action(next_move)
        
        if action == 'move':
            # Normal movement along planned path
            success = reflex_agent.execute_action(action, next_move)
            if success:
                current_path_index += 1
                if verbose and rover.position == next_move:
                    battery_pct = rover.get_battery_percentage()
                    print(f"  Step {len(rover.path_history)-1}: Moved to {rover.position}, Battery: {battery_pct:.1f}%")
            else:
                if verbose:
                    print(f"  ⚠️ Failed to move to {next_move}")
                break
        
        elif action == 'recharge_override':
            # Need to go to recharge station
            if verbose:
                battery_pct = rover.get_battery_percentage()
                print(f"\n  🔋 Battery {'critical' if battery_pct < 20 else 'low'}! Navigating to recharge station at {override_target}")
            
            # Plan path to recharge station
            recharge_path = planner.plan_path(rover.position, override_target, heuristic_name)
            if recharge_path:
                # Execute path to recharge station step-by-step
                recharge_failed = False
                for i in range(1, len(recharge_path)):
                    move_success = rover.move_to(recharge_path[i], env)
                    
                    if not move_success:
                        if verbose:
                            print("  ❌ Failed to reach recharge station - battery depleted!")
                        recharge_failed = True
                        break
                    
                    if verbose:
                        battery_pct = rover.get_battery_percentage()
                        print(f"     → Moving to recharge station: {rover.position}, Battery: {battery_pct:.1f}%")
                    
                    # Check for hazards even on recharge path
                    if env.is_hazardous(rover.position[0], rover.position[1]):
                        if verbose:
                            print("  ⚠️ Hazard encountered on recharge path! Backtracking...")
                        rover.backtrack()
                        recharge_failed = True
                        break
                
                if recharge_failed:
                    if verbose:
                        print("  ❌ Could not reach recharge station!")
                    break
                
                # After recharging, replan to goal
                if verbose:
                    print(f"  ✅ Recharged! Replanning path to goal from {rover.position}")
                planned_path = planner.plan_path(rover.position, goal, heuristic_name)
                if not planned_path:
                    if verbose:
                        print("  ❌ Cannot reach goal after recharge!")
                    break
                current_path_index = 1
                replan_count += 1
            else:
                if verbose:
                    print("  ❌ Cannot reach recharge station!")
                break
        
        elif action == 'backtrack':
            # Backtracked due to hazard
            reflex_agent.execute_action(action, None)
            # Replan from safe position
            if verbose:
                print(f"  🔄 Replanning from safe position: {rover.position}")
            planned_path = planner.plan_path(rover.position, goal, heuristic_name)
            if not planned_path:
                if verbose:
                    print("  ❌ Cannot reach goal after backtracking!")
                break
            current_path_index = 1
            replan_count += 1
        
        else:  # stop
            if verbose:
                print("  🛑 Rover stopped!")
            break
        
        # Safety check for infinite loops
        if len(rover.path_history) > 1000:
            if verbose:
                print("  ⚠️ Maximum steps exceeded!")
            break
    
    # Check if goal was reached
    success = (rover.position == goal)
    
    if verbose:
        print(f"\n{'='*70}")
        if success:
            print("🎉 GOAL REACHED!")
        else:
            print("❌ GOAL NOT REACHED")
        print(f"{'='*70}")
        
        # Print statistics
        stats = rover.get_stats()
        print(f"\nFinal Statistics:")
        print(f"  Final Position: {stats['final_position']}")
        print(f"  Final Battery: {stats['battery_percentage']:.1f}%")
        print(f"  Total Steps: {stats['path_length']}")
        print(f"  Distance Traveled: {stats['distance_traveled']:.2f}")
        print(f"  Recharge Count: {stats['recharge_count']}")
        print(f"  Replan Count: {replan_count}")
        print(f"  Nodes Expanded (initial): {planner.get_stats()['nodes_expanded']}")
    
    return {
        'success': success,
        'rover': rover,
        'planner_stats': planner.get_stats(),
        'heuristic': heuristic_name,
        'replan_count': replan_count
    }


def run_simulation(rover: Rover, env: Environment, start: Tuple[int, int], 
                   goal: Tuple[int, int], heuristic_name: str = 'euclidean',
                   verbose: bool = True) -> dict:
    """
    Run the rover simulation with reflex agent and path planning.
    
    Args:
        rover: Rover instance
        env: Environment instance
        start: Start position
        goal: Goal position
        heuristic_name: Name of heuristic to use
        verbose: Print detailed output
        
    Returns:
        Dictionary with simulation results
    """
    planner = AStarPlanner(env)
    reflex_agent = ReflexAgent(rover, env)
    
    # Track events for visualization
    events = []
    
    # Plan initial path
    if verbose:
        print(f"\n📍 Planning initial path using {heuristic_name} heuristic...")
    
    planned_path = planner.plan_path(start, goal, heuristic_name)
    
    if not planned_path:
        if verbose:
            print("❌ No path found!")
        return {'success': False, 'reason': 'No path found'}
    
    if verbose:
        print(f"✅ Initial path found! Length: {len(planned_path)} steps")
    
    # Execute path with reflex agent
    current_path_index = 1
    step_count = 0
    replan_count = 0
    backtrack_count = 0
    max_steps = 1000
    
    if verbose:
        print(f"\n🎬 Starting simulation...\n")
    
    while rover.position != goal and step_count < max_steps:
        step_count += 1
        
        # Get next planned move
        if current_path_index < len(planned_path):
            next_move = planned_path[current_path_index]
        else:
            # Need to replan
            if verbose:
                print(f"   ℹ️ Reached end of path, replanning from {rover.position}")
            planned_path = planner.plan_path(rover.position, goal, heuristic_name)
            if not planned_path or len(planned_path) < 2:
                if verbose:
                    print(f"   ❌ Cannot find path from {rover.position}")
                break
            current_path_index = 1
            replan_count += 1
            continue
        
        # Store state before action
        battery_before = rover.battery
        position_before = rover.position
        
        # Reflex agent decides action
        action, override_target = reflex_agent.decide_action(next_move)
        
        # Execute action
        if action == 'move':
            success = reflex_agent.execute_action(action, next_move)
            
            if success:
                # Move successful, continue
                current_path_index += 1
                
                # Check if recharged
                if rover.battery == rover.max_battery and battery_before < rover.max_battery:
                    events.append({
                        'step': len(rover.path_history) - 1,
                        'type': 'recharge',
                        'position': rover.position
                    })
                    if verbose:
                        print(f"   🔋 Step {step_count}: Recharged at {rover.position}")
            else:
                # Move failed - could be hazard backtrack or other issue
                if rover.position != position_before:
                    # Position changed - this was a backtrack from hazard
                    backtrack_count += 1
                    events.append({
                        'step': len(rover.path_history) - 1,
                        'type': 'backtrack',
                        'position': rover.position
                    })
                    
                    # Replan from safe position
                    if verbose:
                        print(f"   🔄 Replanning from safe position {rover.position}")
                    
                    planned_path = planner.plan_path(rover.position, goal, heuristic_name)
                    if not planned_path:
                        if verbose:
                            print(f"   ❌ No alternative path available")
                        break
                    
                    current_path_index = 1
                    replan_count += 1
                    
                    if verbose:
                        print(f"   ✅ New path found! Length: {len(planned_path)} steps\n")
                else:
                    # Move truly failed
                    if verbose:
                        print(f"   ❌ Move failed at step {step_count}")
                    break
        
        elif action == 'recharge_override':
            battery_pct = rover.get_battery_percentage()
            
            if battery_pct < 20:
                if verbose:
                    print(f"   ⚡ Step {step_count}: RULE 1 - Critical battery ({battery_pct:.1f}%)")
                events.append({
                    'step': len(rover.path_history) - 1,
                    'type': 'critical_battery',
                    'position': rover.position
                })
            else:
                if verbose:
                    print(f"   🟡 Step {step_count}: RULE 4 - Low battery + nearby station ({battery_pct:.1f}%)")
                events.append({
                    'step': len(rover.path_history) - 1,
                    'type': 'low_battery',
                    'position': rover.position
                })
            
            # Navigate to recharge station
            if verbose:
                print(f"      → Heading to recharge station at {override_target}")
            
            recharge_path = planner.plan_path(rover.position, override_target, heuristic_name)
            
            if recharge_path:
                # Execute path to station
                for i in range(1, len(recharge_path)):
                    move_success = rover.move_to(recharge_path[i], env)
                    if not move_success:
                        break
                    
                    # Check for hazard even on recharge path
                    if env.is_hazardous(rover.position[0], rover.position[1]):
                        if verbose:
                            print(f"      🔴 Hazard on recharge path! Backtracking...")
                        rover.backtrack()
                        backtrack_count += 1
                        break
                
                # Record recharge
                events.append({
                    'step': len(rover.path_history) - 1,
                    'type': 'recharge',
                    'position': rover.position
                })
                
                if verbose:
                    print(f"      ✅ Recharged! Battery: {rover.battery}%")
                
                # Replan to original goal
                planned_path = planner.plan_path(rover.position, goal, heuristic_name)
                if not planned_path:
                    if verbose:
                        print(f"      ❌ Cannot find path to goal after recharge")
                    break
                
                current_path_index = 1
                replan_count += 1
            else:
                if verbose:
                    print(f"      ❌ Cannot reach recharge station")
                break
        
        else:  # stop
            if verbose:
                print(f"   ⛔ Step {step_count}: Stopped")
            break
    
    # Check success
    success = (rover.position == goal)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"📊 SIMULATION RESULTS")
        print(f"{'='*70}")
        
        if success:
            print(f"✅ Goal reached in {len(rover.path_history)} steps!")
        else:
            print(f"❌ Goal not reached. Final position: {rover.position}")
        
        print(f"\n📈 Statistics:")
        print(f"   Path length:                   {len(rover.path_history)}")
        print(f"   Battery remaining:             {rover.battery}%")
        print(f"   Recharge count:                {rover.recharge_count}")
        print(f"   Backtrack count (RULE 3):      {backtrack_count}")
        print(f"   Replan count:                  {replan_count}")
        print(f"   Distance traveled:             {rover.total_distance_traveled:.2f} units")
        print(f"{'='*70}")
    
    return {
        'success': success,
        'path': rover.path_history,
        'battery_history': rover.battery_history,
        'events': events,
        'path_length': len(rover.path_history),
        'battery_remaining': rover.battery,
        'recharge_count': rover.recharge_count,
        'backtrack_count': backtrack_count,
        'replan_count': replan_count,
        'distance': rover.total_distance_traveled
    }


def main():
    """Main function to run all simulations and generate visualizations."""
    print("="*70)
    print("PLANETARY EXPLORATION ROVER SIMULATION")
    print("="*70)
    
    # Create output directory for visualizations
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize environment
    print("\n🌍 Creating Mars environment...")
    env = Environment(width=20, height=20)
    env.create_sample_environment()
    print(f"   Environment size: {env.width}x{env.height}")
    print(f"   Recharge stations: {len(env.recharge_stations)}")
    
    # Define start and goal
    start = (1, 1)
    goal = (18, 18)
    
    # Visualize environment
    print("\n📊 Creating environment visualization...")
    visualizer = RoverVisualizer(env)
    fig, ax = plt.subplots(figsize=(10, 10))
    visualizer.plot_environment(ax)
    ax.plot(start[0], start[1], 'go', markersize=15, label='Start')
    ax.plot(goal[0], goal[1], 'r*', markersize=20, label='Goal')
    ax.legend()
    ax.set_title('Mars Environment')
    plt.savefig(f"{output_dir}/environment.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved to {output_dir}/environment.png")
    
    # Compare heuristics using path planning only (no reflex agent)
    print("\n" + "="*70)
    print("COMPARING A* HEURISTICS (Path Planning Only)")
    print("="*70)
    
    heuristic_results = compare_heuristics(env, start, goal)
    
    print("\nHeuristic Comparison Results:")
    print("-" * 70)
    for heuristic, result in heuristic_results.items():
        print(f"\n{heuristic.upper()}:")
        print(f"  Path Length: {result['path_length']} steps")
        print(f"  Path Cost: {result['path_cost']} battery units")
        print(f"  Nodes Expanded: {result['nodes_expanded']}")
        print(f"  Path Found: {'✅' if result['found'] else '❌'}")
    
    # Visualize heuristic comparison
    print("\n📊 Creating heuristic comparison visualizations...")
    visualizer.compare_heuristics_visualization(
        heuristic_results, 
        save_path=f"{output_dir}/heuristics_comparison.png"
    )
    
    visualizer.plot_comparison_metrics(
        heuristic_results,
        save_path=f"{output_dir}/metrics_comparison.png"
    )
    
    # Run full simulations with reflex agent for each heuristic
    print("\n" + "="*70)
    print("RUNNING FULL SIMULATIONS WITH REFLEX AGENT")
    print("="*70)
    
    heuristics = ['euclidean', 'manhattan', 'weighted_euclidean', 'risk_aware', 'terrain_cost_aware']
    simulation_results = {}
    
    for heuristic in heuristics:
        result = simulate_rover(env, start, goal, heuristic, verbose=True)
        simulation_results[heuristic] = result
        
        # Create individual visualization
        if result['success']:
            rover = result['rover']
            stats = rover.get_stats()
            stats['nodes_expanded'] = result['planner_stats']['nodes_expanded']
            stats['replan_count'] = result['replan_count']
            
            visualizer.visualize_single_run(
                rover.path_history,
                rover.battery_history,
                heuristic,
                stats,
                save_path=f"{output_dir}/simulation_{heuristic}.png"
            )
    
    # Final summary
    print("\n" + "="*70)
    print("SIMULATION SUMMARY")
    print("="*70)
    
    print("\nFull Simulation Results (with Reflex Agent):")
    print("-" * 70)
    for heuristic, result in simulation_results.items():
        if result['success']:
            rover = result['rover']
            stats = rover.get_stats()
            print(f"\n{heuristic.upper()}:")
            print(f"  Success: ✅")
            print(f"  Total Steps: {stats['path_length']}")
            print(f"  Distance: {stats['distance_traveled']:.2f}")
            print(f"  Recharges: {stats['recharge_count']}")
            print(f"  Replans: {result['replan_count']}")
        else:
            print(f"\n{heuristic.upper()}:")
            print(f"  Success: ❌")
    
    print(f"\n{'='*70}")
    print(f"✅ All visualizations saved to '{output_dir}/' directory")
    print(f"{'='*70}")


if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    main()
