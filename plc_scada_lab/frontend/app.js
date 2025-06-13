// PLC SCADA Lab Frontend Application
class PLCSCADAApp {
    constructor() {
        this.ws = null;
        this.md = window.markdownit();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.currentLesson = null;
        
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.updateConnectionStatus('connecting');
    }
    
    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.handleConnectionError();
        }
    }
    
    setupWebSocketHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };
        
        this.ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.updateConnectionStatus('disconnected');
            this.handleReconnection();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.handleConnectionError();
        };
    }
    
    handleMessage(message) {
        switch (message.kind) {
            case 'lessons':
                this.renderLessons(message.payload);
                break;
            case 'lesson':
                this.renderLesson(message.payload);
                break;
            case 'state':
                this.updatePLCState(message.payload);
                break;
            case 'error':
                this.showError(message.payload);
                break;
            default:
                console.warn('Unknown message type:', message.kind);
        }
    }
    
    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateConnectionStatus('connecting');
            
            setTimeout(() => {
                console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                this.setupWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            this.updateConnectionStatus('failed');
            this.showError('Connection failed. Please refresh the page.');
        }
    }
    
    handleConnectionError() {
        this.updateConnectionStatus('disconnected');
        setTimeout(() => this.handleReconnection(), 1000);
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        const statusText = statusElement.querySelector('span');
        
        statusElement.className = `connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                statusText.textContent = 'Connected';
                break;
            case 'connecting':
                statusText.textContent = 'Connecting...';
                break;
            case 'disconnected':
                statusText.textContent = 'Disconnected';
                break;
            case 'failed':
                statusText.textContent = 'Connection Failed';
                break;
        }
    }
    
    setupEventListeners() {
        // Digital input buttons
        document.querySelectorAll('[data-input]').forEach(button => {
            button.addEventListener('click', (e) => {
                const address = parseInt(e.currentTarget.dataset.input);
                this.toggleDigitalInput(address);
            });
        });
        
        // Temperature setpoint slider
        const tempSlider = document.getElementById('tempSetpoint');
        const tempValue = document.getElementById('tempSetpointValue');
        
        if (tempSlider && tempValue) {
            tempSlider.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                tempValue.textContent = value;
                this.setHoldingRegister(4, value); // Register 4 is temperature setpoint
            });
        }
        
        // Legacy coil buttons (for backward compatibility)
        document.querySelectorAll('[data-coil]').forEach(button => {
            button.addEventListener('click', (e) => {
                const address = parseInt(e.currentTarget.dataset.coil);
                this.toggleDigitalInput(address);
            });
        });
    }
    
    renderLessons(lessons) {
        const navElement = document.getElementById('nav');
        if (!navElement) return;
        
        navElement.innerHTML = lessons.map(lesson => 
            `<button data-lesson="${lesson}" class="lesson-btn">${this.formatLessonName(lesson)}</button>`
        ).join('');
        
        // Add click handlers
        navElement.querySelectorAll('[data-lesson]').forEach(button => {
            button.addEventListener('click', (e) => {
                const lessonName = e.currentTarget.dataset.lesson;
                this.loadLesson(lessonName);
                
                // Update active state
                navElement.querySelectorAll('.lesson-btn').forEach(btn => btn.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });
    }
    
    formatLessonName(lessonName) {
        // Convert "01_intro" to "01 - Introduction"
        return lessonName
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase())
            .replace(/(\d+)\s+/, '$1 - ');
    }
    
    loadLesson(lessonName) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.currentLesson = lessonName;
            this.ws.send(JSON.stringify({
                kind: 'lesson',
                payload: lessonName
            }));
        }
    }
    
    renderLesson(content) {
        const lessonElement = document.getElementById('lesson');
        if (!lessonElement) return;
        
        lessonElement.innerHTML = this.md.render(content);
        lessonElement.classList.add('fade-in');
        
        // Scroll to top of lesson
        lessonElement.scrollTop = 0;
    }
    
    updatePLCState(state) {
        // Update scan time
        const scanTimeElement = document.getElementById('scanTime');
        if (scanTimeElement && state.scan_time) {
            scanTimeElement.textContent = `Scan: ${(state.scan_time * 1000).toFixed(0)}ms`;
        }
        
        // Update digital inputs
        if (state.discrete_inputs) {
            state.discrete_inputs.forEach((value, index) => {
                const inputElement = document.getElementById(`input${index}`);
                if (inputElement) {
                    inputElement.classList.toggle('active', value);
                }
            });
        }
        
        // Update digital outputs (coils)
        if (state.coils) {
            state.coils.forEach((value, index) => {
                const outputElement = document.getElementById(`output${index}`);
                if (outputElement) {
                    outputElement.classList.toggle('active', value);
                }
            });
        }
        
        // Update process values
        if (state.holding_registers) {
            const tempElement = document.getElementById('temperature');
            const pressureElement = document.getElementById('pressure');
            const flowElement = document.getElementById('flowRate');
            const alarmElement = document.getElementById('alarmStatus');
            
            if (tempElement) tempElement.textContent = `${state.holding_registers[0]}°C`;
            if (pressureElement) pressureElement.textContent = `${state.holding_registers[1]} kPa`;
            if (flowElement) flowElement.textContent = `${state.holding_registers[2]} L/min`;
            
            if (alarmElement) {
                const alarmStatus = state.holding_registers[3];
                let alarmText = 'Normal';
                
                if (alarmStatus > 0) {
                    const alarms = [];
                    if (alarmStatus & 0x01) alarms.push('Over-Temp');
                    if (alarmStatus & 0x02) alarms.push('Over-Pressure');
                    if (alarmStatus & 0x04) alarms.push('Motor Fault');
                    alarmText = alarms.join(', ');
                }
                
                alarmElement.textContent = alarmText;
                alarmElement.classList.toggle('alarm-active', alarmStatus > 0);
            }
        }
        
        // Update raw data display
        this.updateRawData(state);
    }
    
    updateRawData(state) {
        const coilsElement = document.getElementById('coilsData');
        const inputsElement = document.getElementById('inputsData');
        const holdingElement = document.getElementById('holdingData');
        const inputRegsElement = document.getElementById('inputRegsData');
        
        if (coilsElement && state.coils) {
            coilsElement.textContent = state.coils.map(v => v ? '1' : '0').join(' ');
        }
        
        if (inputsElement && state.discrete_inputs) {
            inputsElement.textContent = state.discrete_inputs.map(v => v ? '1' : '0').join(' ');
        }
        
        if (holdingElement && state.holding_registers) {
            holdingElement.textContent = state.holding_registers.join(' ');
        }
        
        if (inputRegsElement && state.input_registers) {
            inputRegsElement.textContent = state.input_registers.join(' ');
        }
    }
    
    toggleDigitalInput(address) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                kind: 'action',
                payload: {
                    action_type: 'toggle_input',
                    address: address
                }
            }));
        }
    }
    
    setHoldingRegister(address, value) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                kind: 'action',
                payload: {
                    action_type: 'set_register',
                    address: address,
                    value: value
                }
            }));
        }
    }
    
    showError(message) {
        console.error('Application error:', message);
        
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to page
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.plcApp = new PLCSCADAApp();
});

// Add error notification styles
const errorStyles = `
.error-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    z-index: 1000;
    max-width: 400px;
    animation: slideIn 0.3s ease-out;
}

.error-notification button {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    margin-left: auto;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;

// Inject error styles
const styleSheet = document.createElement('style');
styleSheet.textContent = errorStyles;
document.head.appendChild(styleSheet);