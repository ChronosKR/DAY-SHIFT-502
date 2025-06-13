# Lesson 1 – Industrial Control Fundamentals

Welcome to the PLC SCADA Lab! This lesson introduces you to the fundamentals of industrial control systems and Programmable Logic Controllers (PLCs).

## What is a PLC?

A **Programmable Logic Controller (PLC)** is a ruggedized industrial computer designed to control manufacturing processes, machinery, and automation systems. PLCs are the backbone of modern industrial automation.

### Key Characteristics:
- **Real-time operation** - Responds to inputs within milliseconds
- **Rugged design** - Operates in harsh industrial environments
- **Reliable** - Designed for 24/7 operation with minimal downtime
- **Programmable** - Logic can be modified without hardware changes

## Basic PLC Components

### Digital Inputs
- **Purpose**: Read signals from sensors, switches, and other devices
- **Examples**: Push buttons, limit switches, proximity sensors
- **States**: ON (1) or OFF (0)

### Digital Outputs (Coils)
- **Purpose**: Control external devices like motors, lights, and valves
- **Examples**: Motor starters, indicator lights, solenoid valves
- **States**: ON (1) or OFF (0)

### Analog Values
- **Holding Registers**: Store 16-bit data values (0-65535)
- **Input Registers**: Read analog sensor values
- **Examples**: Temperature, pressure, flow rate measurements

## Try It Now!

Use the control panel to interact with our simulated PLC:

### Exercise 1: Basic Input/Output
1. Click the **Start Button** (Input 0)
2. Observe that the **Motor Running** output activates
3. Click the **Stop Button** (Input 1) 
4. Watch the motor stop

### Exercise 2: Process Control
1. Ensure the motor is running
2. Activate the **Tank Low Level** sensor (Input 3)
3. Notice the **Pump Running** output activates
4. Observe how the pressure increases in the process values

### Exercise 3: Safety Systems
1. While the motor is running, activate **Motor Fault** (Input 2)
2. See how the safety system immediately stops the motor
3. Notice the alarm indicator activates

## Understanding the Display

### Process Values
- **Temperature**: Simulated process temperature with heater control
- **Pressure**: System pressure affected by pump operation  
- **Flow Rate**: Liquid flow rate through the system
- **Alarm Status**: Shows active system alarms

### Raw MODBUS Data
The bottom panel shows the actual MODBUS register values:
- **Coils**: Digital outputs (0 = OFF, 1 = ON)
- **Discrete Inputs**: Digital inputs (0 = OFF, 1 = ON)  
- **Holding Registers**: Process values and setpoints
- **Input Registers**: Sensor readings

## Key Concepts

### Scan Cycle
PLCs operate in a continuous **scan cycle**:
1. **Input Scan**: Read all input values
2. **Program Execution**: Execute ladder logic
3. **Output Update**: Update all outputs
4. **Housekeeping**: System maintenance tasks

Our simulator shows the scan time (typically 10-100ms).

### Ladder Logic
PLCs use **ladder logic** programming, which resembles electrical relay circuits:
- **Rungs**: Individual control circuits
- **Contacts**: Input conditions (normally open/closed)
- **Coils**: Output devices to be controlled

## Industrial Applications

PLCs are used in virtually every industry:
- **Manufacturing**: Assembly lines, packaging machines
- **Process Control**: Chemical plants, water treatment
- **Building Automation**: HVAC, lighting, security
- **Transportation**: Traffic lights, conveyor systems

## Next Steps

In the next lesson, we'll explore MODBUS communication protocol and how PLCs communicate with other industrial devices.

**Remember**: Industrial safety is paramount. Always follow proper lockout/tagout procedures when working with real industrial equipment!