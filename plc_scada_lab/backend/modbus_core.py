import threading
import time
import logging

logger = logging.getLogger(__name__)

class PLCSimulator:
    """Simplified PLC simulation for WebContainer compatibility"""
    
    def __init__(self):
        self.running = False
        self.scan_time = 0.1  # 100ms scan cycle
        self.coils = [False] * 64
        self.discrete_inputs = [False] * 64
        self.holding_registers = [0] * 64
        self.input_registers = [0] * 64
        
        # Initialize some realistic values
        self.holding_registers[0] = 800   # Process temperature
        self.holding_registers[1] = 0     # Process pressure
        self.holding_registers[2] = 0     # Flow rate
        self.holding_registers[3] = 0     # Alarm status
        self.holding_registers[4] = 800   # Temperature setpoint
        
        # Simulation variables
        self.motor_running = False
        self.pump_running = False
        
    def start_simulation(self):
        """Start the PLC simulation loop"""
        self.running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        logger.info("PLC Simulation started")
        
    def stop_simulation(self):
        """Stop the PLC simulation"""
        self.running = False
        logger.info("PLC Simulation stopped")
        
    def _simulation_loop(self):
        """Main simulation loop - executes ladder logic"""
        while self.running:
            try:
                self._execute_ladder_logic()
                self._update_process_values()
                time.sleep(self.scan_time)
            except Exception as e:
                logger.error(f"Simulation error: {e}")
                
    def _execute_ladder_logic(self):
        """Execute ladder logic - simplified for WebContainer"""
        
        # Rung 1: Motor control
        start_button = self.discrete_inputs[0]
        stop_button = self.discrete_inputs[1]
        motor_fault = self.discrete_inputs[2]
        
        if start_button and not stop_button and not motor_fault:
            self.motor_running = True
        elif stop_button or motor_fault:
            self.motor_running = False
            
        self.coils[0] = self.motor_running
        
        # Rung 2: Pump control (depends on motor)
        tank_level_low = self.discrete_inputs[3]
        
        if self.motor_running and tank_level_low:
            self.pump_running = True
        elif not self.motor_running:
            self.pump_running = False
            
        self.coils[1] = self.pump_running
        
        # Rung 3: Temperature control
        current_temp = self.holding_registers[0]
        temp_setpoint = self.holding_registers[4]
        
        # Heater control with hysteresis
        if current_temp < (temp_setpoint - 20):
            self.coils[2] = True  # Heater ON
        elif current_temp > (temp_setpoint + 10):
            self.coils[2] = False  # Heater OFF
            
        # Rung 4: Alarm logic
        alarm_status = 0
        if current_temp > 1200:  # Over-temperature
            alarm_status |= 0x01
        if self.holding_registers[1] > 1000:  # Over-pressure
            alarm_status |= 0x02
        if motor_fault:  # Motor fault
            alarm_status |= 0x04
            
        self.holding_registers[3] = alarm_status
        self.coils[3] = alarm_status > 0  # Alarm indicator
        
    def _update_process_values(self):
        """Simulate realistic process values"""
        
        # Temperature simulation
        current_temp = self.holding_registers[0]
        heater_on = self.coils[2]
        
        if heater_on:
            # Heat up with some inertia
            self.holding_registers[0] = min(1500, current_temp + 2)
        else:
            # Cool down naturally
            self.holding_registers[0] = max(200, current_temp - 1)
            
        # Pressure simulation (depends on pump)
        current_pressure = self.holding_registers[1]
        if self.pump_running:
            self.holding_registers[1] = min(1200, current_pressure + 5)
        else:
            self.holding_registers[1] = max(0, current_pressure - 3)
            
        # Flow rate (depends on pump and pressure)
        if self.pump_running and current_pressure > 100:
            self.holding_registers[2] = min(100, self.holding_registers[2] + 2)
        else:
            self.holding_registers[2] = max(0, self.holding_registers[2] - 1)
            
        # Update input registers with sensor readings
        self.input_registers[0] = self.holding_registers[0]  # Temperature sensor
        self.input_registers[1] = self.holding_registers[1]  # Pressure sensor
        self.input_registers[2] = self.holding_registers[2]  # Flow sensor

# Global instances
plc_simulator = None

def start_modbus(port: int = 1502):
    """Start the simplified PLC system for WebContainer"""
    global plc_simulator
    try:
        # Create and start PLC simulation
        plc_simulator = PLCSimulator()
        plc_simulator.start_simulation()
        
        logger.info("Simplified PLC system started (WebContainer mode)")
        return None, plc_simulator
        
    except Exception as e:
        logger.error(f"Failed to start PLC system: {e}")
        return None, None

def get_plc_state():
    """Get current PLC state"""
    if plc_simulator is None:
        return {
            'coils': [False] * 8,
            'discrete_inputs': [False] * 8,
            'holding_registers': [800, 0, 0, 0, 800, 0, 0, 0],
            'input_registers': [800, 0, 0, 0, 0, 0, 0, 0],
            'motor_running': False,
            'pump_running': False,
            'scan_time': 0.1
        }
    
    return {
        'coils': plc_simulator.coils[:8],
        'discrete_inputs': plc_simulator.discrete_inputs[:8],
        'holding_registers': plc_simulator.holding_registers[:8],
        'input_registers': plc_simulator.input_registers[:8],
        'motor_running': plc_simulator.motor_running,
        'pump_running': plc_simulator.pump_running,
        'scan_time': plc_simulator.scan_time
    }

def set_discrete_input(address: int, value: bool):
    """Set discrete input value"""
    if plc_simulator is None:
        return True  # Mock success
        
    if 0 <= address < len(plc_simulator.discrete_inputs):
        plc_simulator.discrete_inputs[address] = value
        return True
    return False

def set_holding_register(address: int, value: int):
    """Set holding register value"""
    if plc_simulator is None:
        return True  # Mock success
        
    if 0 <= address < len(plc_simulator.holding_registers):
        plc_simulator.holding_registers[address] = max(0, min(65535, value))
        return True
    return False