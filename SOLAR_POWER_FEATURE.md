# ☀️🌙 Solar Power Management System

## Overview
A unique and realistic feature that simulates Martian day/night cycles and their impact on solar-powered rover operations.

## Feature Details

### Day/Night Cycle
- **Cycle Length**: 10 steps per period (10 day, 10 night, repeating)
- **Starting Time**: Day (step 0-9 is daytime)
- **Visual Feedback**: 
  - **DAY** ☀️: Light background (#FFF8DC - Cornsilk)
  - **NIGHT** 🌙: Dark background (#1a1a2e - Navy Blue)

### Recharge Behavior

#### Daytime Recharging ☀️
- **Full Solar Power Available**
- Recharge to: **100%** battery
- Symbol: ☀️ DAY
- Color: Golden/Yellow indicators

#### Nighttime Recharging 🌙
- **Limited Stored Battery Power**
- Recharge amount: **+50%** (not to full capacity)
- Maximum: 100% (if current battery + 50 exceeds 100)
- Symbol: 🌙 NIGHT
- Color: Blue indicators

## Implementation

### Rover Class (`rover.py`)
Added tracking for:
- `step_count`: Current step number
- `day_night_cycle_length`: Steps per cycle (10)
- `is_daytime`: Current time state
- `day_night_history`: Historical day/night record

Methods:
- `is_day()`: Checks if current step is daytime
- `get_time_of_day()`: Returns "DAY" or "NIGHT"
- `recharge()`: Solar-aware recharging

### GUI (`rover_gui.py`)
Visual changes:
- **Map Background**: Changes between light (day) and dark (night)
- **Title**: Shows current time of day
- **Step Info Box**: Color-coded (yellow for day, gray for night)
- **Battery Graph**: Day/night cycle shading
- **Statistics**: Separate counts for day vs night recharges

### Animation (`animation.py`)
- Dynamic background changes during animation
- Day/night cycle visualization in battery graph
- Time-specific recharge event messages

## Strategic Impact

### Planning Considerations
1. **Battery Management**: Night recharges are less efficient
2. **Timing**: Reaching charging stations during day is optimal
3. **Emergency Planning**: Need more battery buffer at night
4. **Route Optimization**: Consider time of day when planning

### Gameplay Dynamics
- Adds temporal dimension to path planning
- Creates urgency during night periods
- Rewards efficient daytime navigation
- Increases realism of Mars rover operations

## Visual Indicators Summary

| Element | Day ☀️ | Night 🌙 |
|---------|--------|----------|
| Background | Light Cornsilk | Dark Navy |
| Recharge | 100% | +50% |
| Step Box | Light Yellow | Light Gray |
| Battery Box | Light Yellow | Light Blue |
| Graph Shade | Yellow (10%) | Navy (15%) |

## Usage Example

```python
rover = Rover(start_pos=(0, 0), battery_capacity=100)

# Rover automatically tracks day/night
rover.move_to((1, 0), env)  # Step 1 - DAY
rover.move_to((2, 0), env)  # Step 2 - DAY
# ... (steps 3-10 are still DAY)

rover.move_to((0, 1), env)  # Step 11 - NIGHT begins!
# Recharges during night only give +50%

# Check current time
is_day = rover.is_daytime
time_str = rover.get_time_of_day()  # "DAY" or "NIGHT"
```

## Benefits

✅ **Unique Feature**: Not commonly found in similar projects
✅ **Realistic**: Based on actual Mars rover operations
✅ **Visual Impact**: Clear day/night feedback
✅ **Strategic Depth**: Adds complexity to decision-making
✅ **Educational**: Teaches about solar power constraints
✅ **Impressive**: Shows advanced system integration

---

**This feature makes your project stand out from peers by adding a unique, realistic, and visually striking element that demonstrates understanding of autonomous systems, resource management, and real-world constraints!** 🚀
