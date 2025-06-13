# Lesson 3 – Ladder Logic Programming

Ladder Logic is the most common programming language for PLCs, designed to resemble electrical relay circuits that industrial electricians already understood.

## What is Ladder Logic?

**Ladder Logic** is a graphical programming language that represents control logic using symbols that look like electrical ladder diagrams. It was designed to make PLC programming familiar to electricians and technicians.

### Key Concepts:
- **Rungs**: Horizontal lines representing individual control circuits
- **Rails**: Vertical power lines (left = power, right = neutral)
- **Contacts**: Input conditions (switches, sensors)
- **Coils**: Output devices (motors, lights, valves)
- **Logic Flow**: Power flows from left to right when conditions are met

## Basic Ladder Logic Elements

### Contacts (Inputs)
- **Normally Open (NO)**: `] [` - Passes power when input is ON
- **Normally Closed (NC)**: `]/[` - Passes power when input is OFF
- **Rising Edge**: `]P[` - Triggers once when input turns ON
- **Falling Edge**: `]N[` - Triggers once when input turns OFF

### Coils (Outputs)
- **Output Coil**: `( )` - Turns ON when rung has power
- **Negated Coil**: `(/)` - Turns OFF when rung has power  
- **Set Coil**: `(S)` - Latches ON, stays ON until reset
- **Reset Coil**: `(R)` - Turns OFF the corresponding set coil

### Logic Operations
- **AND**: Contacts in series - ALL must be true
- **OR**: Contacts in parallel - ANY can be true
- **NOT**: Normally closed contacts - inverts logic

## Our Simulator's Ladder Logic

Let's examine the actual ladder logic running in our PLC simulator:

### Rung 1: Motor Control
```
Start_Button    Stop_Button    Motor_Fault         Motor_Run
    ] [      AND    ]/[     AND    ]/[        =      ( )
```

**Logic**: Motor runs IF Start button is pressed AND Stop button is NOT pressed AND there's NO motor fault.

### Rung 2: Pump Control  
```
Motor_Running   Tank_Level_Low                      Pump_Run
    ] [       AND     ] [                    =       ( )
```

**Logic**: Pump runs IF Motor is running AND Tank level is low.

### Rung 3: Temperature Control (with Hysteresis)
```
Current_Temp < (Setpoint - 20)                     Heater_ON
           ] [                              =        ( )

Current_Temp > (Setpoint + 10)                     Heater_OFF  
           ] [                              =        (/)
```

**Logic**: Heater turns ON when temperature is 20° below setpoint, turns OFF when 10° above setpoint.

### Rung 4: Alarm Logic
```
Over_Temp    Over_Pressure    Motor_Fault          Alarm_Active
   ] [    OR     ] [      OR     ] [         =        ( )
```

**Logic**: Alarm activates if ANY alarm condition is present.

## Try It Now!

Let's trace through the ladder logic execution:

### Exercise 1: Motor Start Sequence
1. **Initial State**: All inputs OFF, motor stopped
2. **Press Start Button**: 
   - Input 0 becomes TRUE
   - Rung 1 evaluates: TRUE AND TRUE AND TRUE = TRUE
   - Motor_Run coil (Output 0) turns ON
3. **Release Start Button**:
   - Input 0 becomes FALSE  
   - Rung 1 evaluates: FALSE AND TRUE AND TRUE = FALSE
   - Motor stops (no latching in this simple example)

### Exercise 2: Motor Latching (Self-Hold)
Real industrial systems use **latching** to keep motors running:

```
Start_Button    Motor_Run     Stop_Button    Motor_Fault    Motor_Run
    ] [    OR     ] [     AND    ]/[     AND    ]/[    =     ( )
```

This creates a "self-hold" - once started, the motor contact keeps itself running until stopped or faulted.

### Exercise 3: Pump Interlock
1. **Start the motor** (Input 0)
2. **Activate tank low level** (Input 3)
3. **Observe**: Pump only runs when BOTH conditions are met
4. **Stop the motor**: Pump immediately stops (safety interlock)

### Exercise 4: Temperature Control
1. **Watch the temperature value** in process display
2. **Adjust the setpoint slider** to different values
3. **Observe heater behavior**:
   - Below setpoint: Heater ON, temperature rises
   - Above setpoint: Heater OFF, temperature falls
   - **Hysteresis**: Prevents rapid on/off cycling

## Advanced Ladder Logic Concepts

### Timers
- **TON (Timer On-Delay)**: Delays turning ON an output
- **TOF (Timer Off-Delay)**: Delays turning OFF an output  
- **RTO (Retentive Timer)**: Accumulates time across power cycles

### Counters
- **CTU (Count Up)**: Increments on rising edge
- **CTD (Count Down)**: Decrements on rising edge
- **RES (Reset)**: Resets timer/counter values

### Math Operations
- **ADD, SUB, MUL, DIV**: Basic arithmetic
- **MOV (Move)**: Copy values between registers
- **CMP (Compare)**: Compare values (>, <, =, ≠)

### Data Manipulation
- **Shift Registers**: Move data through arrays
- **FIFO/LIFO**: First-in-first-out / Last-in-first-out
- **Scaling**: Convert raw values to engineering units

## Programming Best Practices

### Organization
- **Document**: Comment every rung with clear descriptions
- **Group**: Organize related rungs together
- **Number**: Use consistent addressing schemes
- **Modular**: Break complex logic into smaller functions

### Safety Considerations
- **Fail-Safe**: Design logic to fail in a safe state
- **Emergency Stops**: Always wire hardware E-stops
- **Interlocks**: Prevent unsafe equipment combinations
- **Monitoring**: Include diagnostic and status indicators

### Performance Optimization
- **Scan Time**: Keep logic efficient for fast scan cycles
- **Memory**: Use appropriate data types
- **Network**: Minimize communication overhead
- **Testing**: Thoroughly test all logic paths

## Common Ladder Logic Patterns

### Start/Stop Station
```
Start    Stop    Run                Run
 ] [  AND ]/[ AND ] [         =     ( )
```

### Alternating Outputs
```
Input    Output1                    Output2
 ]P[  AND  ]/[              =       ( )

Input    Output2                    Output1  
 ]P[  AND  ]/[              =       ( )
```

### Sequence Control
```
Step1    Condition1                 Step2
 ] [  AND    ] [            =       (S)

Step2    Condition2                 Step3
 ] [  AND    ] [            =       (S)

Step3    Reset_Condition            Step1
 ] [  AND      ] [          =       (R)
```

## Troubleshooting Ladder Logic

### Common Issues
1. **Logic Never True**: Check AND conditions - all must be satisfied
2. **Logic Always True**: Check for missing interlocks or conditions
3. **Oscillation**: Usually caused by missing hysteresis or delays
4. **Race Conditions**: Multiple rungs affecting same output

### Debugging Techniques
- **Force I/O**: Manually set inputs/outputs for testing
- **Online Monitoring**: Watch logic execution in real-time
- **Data Tables**: Monitor register values during operation
- **Trend Analysis**: Graph values over time to spot patterns

## Real-World Applications

### Manufacturing
- **Conveyor Control**: Start/stop sequences with sensors
- **Assembly Stations**: Step-by-step automated assembly
- **Quality Control**: Reject parts based on measurements
- **Packaging**: Count, fill, seal, and label operations

### Process Control
- **Batch Processing**: Recipe-based control sequences
- **Temperature Control**: Heating/cooling with PID loops
- **Level Control**: Pump control based on tank levels
- **Flow Control**: Valve positioning for flow rates

## Next Steps

In Lesson 4, we'll explore Human Machine Interfaces (HMIs) and how operators interact with PLC-controlled systems through graphical displays and touch screens.

Understanding ladder logic is essential for anyone working with industrial automation - it's the language that brings machines to life!