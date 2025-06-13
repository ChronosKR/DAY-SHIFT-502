# Lesson 2 – MODBUS Communication Protocol

MODBUS is the most widely used industrial communication protocol, enabling PLCs, HMIs, and other devices to exchange data reliably over various networks.

## What is MODBUS?

**MODBUS** is an open-standard, serial communication protocol developed in 1979 by Modicon (now Schneider Electric). It's designed for industrial automation and allows devices to communicate over various physical layers.

### Key Features:
- **Open Standard** - No licensing fees, widely supported
- **Simple** - Easy to implement and troubleshoot
- **Reliable** - Proven in harsh industrial environments
- **Flexible** - Works over serial, Ethernet, and wireless networks

## MODBUS Data Model

MODBUS organizes data into four distinct address spaces:

### 1. Coils (Function Codes 01, 05, 15)
- **Address Range**: 00001 - 09999
- **Data Type**: Single bit (Boolean)
- **Access**: Read/Write
- **Purpose**: Digital outputs, relay states
- **Example**: Motor start/stop commands

### 2. Discrete Inputs (Function Code 02)
- **Address Range**: 10001 - 19999  
- **Data Type**: Single bit (Boolean)
- **Access**: Read Only
- **Purpose**: Digital sensor inputs
- **Example**: Limit switch states, button presses

### 3. Holding Registers (Function Codes 03, 06, 16)
- **Address Range**: 40001 - 49999
- **Data Type**: 16-bit word (0-65535)
- **Access**: Read/Write
- **Purpose**: Configuration data, setpoints, control values
- **Example**: Temperature setpoints, timer values

### 4. Input Registers (Function Code 04)
- **Address Range**: 30001 - 39999
- **Data Type**: 16-bit word (0-65535)
- **Access**: Read Only
- **Purpose**: Sensor readings, measured values
- **Example**: Temperature readings, pressure values

## MODBUS TCP vs RTU

### MODBUS RTU (Remote Terminal Unit)
- **Physical Layer**: RS-232, RS-485 serial
- **Data Format**: Binary, compact
- **Error Checking**: CRC-16
- **Addressing**: 8-bit device addresses (1-247)

### MODBUS TCP
- **Physical Layer**: Ethernet (TCP/IP)
- **Data Format**: Same as RTU but with TCP header
- **Error Checking**: TCP checksums
- **Addressing**: IP addresses + unit identifier

## Try It Now!

Our simulator implements a full MODBUS TCP server. Let's explore the data model:

### Exercise 1: Understanding Coils
1. Toggle various input buttons
2. Watch the **Coils** section in the raw data display
3. Notice how coil states change based on ladder logic execution
4. **Coil 0**: Motor running status
5. **Coil 1**: Pump running status  
6. **Coil 2**: Heater control
7. **Coil 3**: Alarm indicator

### Exercise 2: Discrete Inputs
1. Activate different input buttons
2. Observe the **Discrete Inputs** section
3. See how physical inputs map to MODBUS addresses:
   - **Input 0**: Start button (10001)
   - **Input 1**: Stop button (10002)
   - **Input 2**: Motor fault (10003)
   - **Input 3**: Tank low level (10004)

### Exercise 3: Holding Registers
1. Adjust the temperature setpoint slider
2. Watch **Holding Register 4** change
3. Observe other holding registers:
   - **Register 0**: Current temperature
   - **Register 1**: Current pressure
   - **Register 2**: Flow rate
   - **Register 3**: Alarm status word
   - **Register 4**: Temperature setpoint

### Exercise 4: Input Registers
Input registers mirror sensor readings:
- **Register 0**: Temperature sensor (30001)
- **Register 1**: Pressure sensor (30002)  
- **Register 2**: Flow sensor (30003)

## MODBUS Function Codes

Common MODBUS function codes used in industrial applications:

| Code | Name | Purpose |
|------|------|---------|
| 01 | Read Coils | Read 1-2000 coil states |
| 02 | Read Discrete Inputs | Read 1-2000 input states |
| 03 | Read Holding Registers | Read 1-125 register values |
| 04 | Read Input Registers | Read 1-125 input register values |
| 05 | Write Single Coil | Write one coil state |
| 06 | Write Single Register | Write one register value |
| 15 | Write Multiple Coils | Write multiple coil states |
| 16 | Write Multiple Registers | Write multiple register values |

## Error Handling

MODBUS includes robust error handling:

### Exception Codes
- **01**: Illegal Function Code
- **02**: Illegal Data Address  
- **03**: Illegal Data Value
- **04**: Slave Device Failure
- **05**: Acknowledge (long operation in progress)
- **06**: Slave Device Busy

### Timeout Handling
- **Master**: Waits for response, retries on timeout
- **Slave**: Must respond within specified time
- **Network**: Handles lost packets, connection failures

## Real-World Applications

### SCADA Systems
- **HMI**: Human Machine Interface displays
- **Data Logging**: Historical data collection
- **Alarming**: Real-time alarm management
- **Reporting**: Production and maintenance reports

### Device Integration
- **PLCs**: Primary control logic
- **VFDs**: Variable Frequency Drives for motor control
- **I/O Modules**: Remote input/output expansion
- **Instruments**: Temperature, pressure, flow transmitters

### Network Architectures
- **Star**: Central master with multiple slaves
- **Daisy Chain**: Serial connection of devices
- **Ethernet**: TCP/IP network with multiple masters

## Best Practices

### Addressing Strategy
- **Document**: Maintain address maps and documentation
- **Organize**: Group related data logically
- **Reserve**: Leave gaps for future expansion
- **Standardize**: Use consistent addressing across projects

### Network Design
- **Bandwidth**: Consider data update rates and network capacity
- **Redundancy**: Implement backup communication paths
- **Security**: Use firewalls and VPNs for remote access
- **Monitoring**: Implement network health monitoring

## Troubleshooting Tips

### Common Issues
1. **No Response**: Check physical connections, IP addresses
2. **Timeout Errors**: Verify network latency, device response times
3. **Data Corruption**: Check for electromagnetic interference
4. **Address Errors**: Verify MODBUS address mapping

### Diagnostic Tools
- **MODBUS Scanners**: Test device connectivity
- **Protocol Analyzers**: Capture and analyze MODBUS traffic
- **Network Tools**: Ping, traceroute, packet capture
- **Device Diagnostics**: Built-in device status indicators

## Next Steps

In Lesson 3, we'll explore ladder logic programming and how to create control algorithms that respond to inputs and control outputs through the MODBUS interface.

The combination of MODBUS communication and ladder logic forms the foundation of modern industrial automation systems!