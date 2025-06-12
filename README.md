
# PLC/MODBUS Trainer

A web-based interactive training application for learning PLC (Programmable Logic Controller) and MODBUS protocol concepts. This educational tool provides hands-on experience with industrial control systems in a safe, simulated environment.

## Features

- **Interactive PLC Simulation**: Real-time coil and register manipulation
- **MODBUS Protocol**: Built-in MODBUS TCP server for authentic industrial communication
- **Educational Content**: Structured lessons covering industrial control fundamentals
- **Live State Monitoring**: Real-time visualization of PLC state changes
- **Web-Based Interface**: No special software required - runs in any modern browser

## Architecture

- **Backend**: FastAPI with Python
- **Frontend**: Vanilla JavaScript with WebSocket communication
- **MODBUS Server**: PyModbus library providing TCP server functionality
- **Real-time Updates**: WebSocket connection for live state synchronization

## Project Structure

```
├── backend/
│   ├── api.py          # FastAPI application and WebSocket endpoints
│   ├── modbus_core.py  # MODBUS server implementation
│   └── lessons.py      # Lesson management system
├── frontend/
│   ├── index.html      # Main web interface
│   ├── app.js          # Client-side JavaScript application
│   └── styles.css      # Application styling
├── docs/
│   └── 01_intro.md     # Educational lesson content
├── requirements.txt    # Python dependencies
└── run.py             # Application entry point
```

## Getting Started

### Prerequisites

- Python 3.9+
- Modern web browser

### Installation & Running

1. **Clone or fork this repository in Replit**

2. **Install dependencies** (handled automatically):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Click the "Run" button in Replit, or execute:
   ```bash
   python run.py
   ```

4. **Access the trainer**:
   Open the web preview in Replit to start learning!

## How to Use

1. **Select a Lesson**: Choose from available lessons in the sidebar
2. **Read the Content**: Study the educational material in the main panel
3. **Interact with Controls**: Use the toggle buttons to manipulate PLC coils
4. **Monitor State**: Watch real-time updates in the state panel
5. **Experiment**: Try different combinations and observe the results

## Educational Content

The trainer includes structured lessons covering:

- Industrial Control Basics
- PLC Fundamentals
- MODBUS Protocol
- Coils vs Registers
- Real-world Applications

## Technical Details

### MODBUS Implementation

- **Protocol**: MODBUS TCP
- **Port**: 1502 (internal)
- **Address Space**: 
  - Coils: 64 boolean outputs
  - Registers: 64 16-bit data values
  - Discrete Inputs: 64 boolean inputs
  - Input Registers: 64 16-bit input values

### API Endpoints

- `GET /`: Main application interface
- `WebSocket /ws`: Real-time communication for state updates and lesson content

### Dependencies

- **FastAPI**: Modern web framework for Python APIs
- **Uvicorn**: ASGI server implementation
- **PyModbus**: MODBUS protocol implementation
- **Jinja2**: Template engine for dynamic content
- **markdown-it-py**: Markdown processing for lessons

## Development

### Adding New Lessons

1. Create a new `.md` file in the `docs/` directory
2. Follow the naming convention: `##_title.md`
3. Write educational content using Markdown syntax
4. Restart the application to load the new lesson

### Extending Functionality

- **Backend**: Modify `backend/api.py` for new endpoints
- **Frontend**: Update `frontend/app.js` for UI enhancements
- **MODBUS**: Extend `backend/modbus_core.py` for protocol features

## Deployment

This application is designed to run on Replit's platform:

1. Ensure all dependencies are in `requirements.txt`
2. The application automatically binds to `0.0.0.0:8000`
3. Use Replit's deployment features for sharing your trainer

## Educational Goals

This trainer helps students understand:

- **Industrial Automation**: Core concepts of factory automation
- **PLC Programming**: Logic controller fundamentals
- **MODBUS Communication**: Industrial protocol standards
- **Real-time Systems**: Immediate response in control systems
- **Safety Concepts**: Understanding industrial safety principles

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is designed for educational purposes. Feel free to use and modify for learning and teaching industrial automation concepts.

## Support

For questions or issues:
- Check the lesson content for guidance
- Review the code comments for implementation details
- Experiment with different configurations to understand behavior

---

**Happy Learning!** 🏭⚡
