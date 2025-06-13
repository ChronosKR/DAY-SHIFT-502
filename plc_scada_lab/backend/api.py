import json
import pathlib
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from plc_scada_lab.backend.modbus_core import (
        start_modbus, get_plc_state, set_discrete_input, set_holding_register
    )
    from plc_scada_lab.backend.lessons import list_lessons, load_md
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Module import failed: {e}")
    MODULES_AVAILABLE = False

# FastAPI app setup
app = FastAPI(title="PLC SCADA Lab", version="1.0.0")

# Mount static files - serve frontend files at /static
FRONTEND_DIR = pathlib.Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    logger.info(f"Mounted static files from {FRONTEND_DIR}")
else:
    logger.warning(f"Frontend directory not found: {FRONTEND_DIR}")

# Data models
class ActionRequest(BaseModel):
    action_type: str
    address: int
    value: Any = None

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if self.active_connections:
            message_str = json.dumps(message)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.append(connection)
                    
            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection)

# Global connection manager
manager = ConnectionManager()

# Initialize PLC system with error handling
context, plc = None, None
if MODULES_AVAILABLE:
    try:
        context, plc = start_modbus()
        logger.info("PLC SCADA system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PLC system: {e}")
        context, plc = None, None

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main application page"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        content = index_path.read_text()
        return HTMLResponse(content=content, status_code=200)
    else:
        # Return a basic HTML page if frontend not found
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PLC SCADA Lab</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .error { color: red; }
                .info { color: blue; }
            </style>
        </head>
        <body>
            <h1>PLC SCADA Lab</h1>
            <p class="error">Frontend files not found. Please check the installation.</p>
            <p class="info">Expected location: plc_scada_lab/frontend/index.html</p>
        </body>
        </html>
        """, status_code=200)

@app.get("/api/lessons")
async def get_lessons():
    """Get list of available lessons"""
    if MODULES_AVAILABLE:
        try:
            return {"lessons": list_lessons()}
        except Exception as e:
            logger.error(f"Error loading lessons: {e}")
    
    # Return mock lessons if modules not available
    return {"lessons": ["01_intro", "02_modbus", "03_ladder_logic"]}

@app.get("/api/lesson/{lesson_name}")
async def get_lesson(lesson_name: str):
    """Get specific lesson content"""
    if MODULES_AVAILABLE:
        try:
            content = load_md(lesson_name)
            return {"name": lesson_name, "content": content}
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Lesson not found")
        except Exception as e:
            logger.error(f"Error loading lesson {lesson_name}: {e}")
    
    # Return mock content if modules not available
    return {
        "name": lesson_name,
        "content": f"# {lesson_name}\n\nLesson content would be loaded here."
    }

@app.get("/api/state")
async def get_state():
    """Get current PLC state"""
    if plc is not None and MODULES_AVAILABLE:
        try:
            return get_plc_state()
        except Exception as e:
            logger.error(f"Error getting PLC state: {e}")
    
    # Return mock state if PLC system not available
    return {
        'coils': [False] * 8,
        'discrete_inputs': [False] * 8,
        'holding_registers': [800, 0, 0, 0, 800, 0, 0, 0],
        'input_registers': [800, 0, 0, 0, 0, 0, 0, 0],
        'motor_running': False,
        'pump_running': False,
        'scan_time': 0.1
    }

@app.post("/api/action")
async def perform_action(action: ActionRequest):
    """Perform PLC action"""
    if plc is None or not MODULES_AVAILABLE:
        # Mock response if PLC system not available
        await manager.broadcast({
            "kind": "state",
            "payload": {
                'coils': [False] * 8,
                'discrete_inputs': [False] * 8,
                'holding_registers': [800, 0, 0, 0, 800, 0, 0, 0],
                'input_registers': [800, 0, 0, 0, 0, 0, 0, 0],
                'motor_running': False,
                'pump_running': False,
                'scan_time': 0.1
            }
        })
        return {"success": True, "message": "Action performed (simulation mode)"}
        
    success = False
    
    try:
        if action.action_type == "set_input":
            success = set_discrete_input(action.address, bool(action.value))
        elif action.action_type == "set_register":
            success = set_holding_register(action.address, int(action.value))
        else:
            raise HTTPException(status_code=400, detail="Invalid action type")
            
        if success:
            # Broadcast state update to all clients
            await manager.broadcast({
                "kind": "state",
                "payload": get_plc_state()
            })
            return {"success": True, "message": "Action performed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Action failed")
    except Exception as e:
        logger.error(f"Error performing action: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        if MODULES_AVAILABLE:
            try:
                lessons = list_lessons()
            except:
                lessons = ["01_intro", "02_modbus", "03_ladder_logic"]
        else:
            lessons = ["01_intro", "02_modbus", "03_ladder_logic"]
            
        await websocket.send_text(json.dumps({
            "kind": "lessons",
            "payload": lessons
        }))
        
        # Send initial state
        if plc is not None and MODULES_AVAILABLE:
            try:
                initial_state = get_plc_state()
            except:
                initial_state = {
                    'coils': [False] * 8,
                    'discrete_inputs': [False] * 8,
                    'holding_registers': [800, 0, 0, 0, 800, 0, 0, 0],
                    'input_registers': [800, 0, 0, 0, 0, 0, 0, 0],
                    'motor_running': False,
                    'pump_running': False,
                    'scan_time': 0.1
                }
        else:
            initial_state = {
                'coils': [False] * 8,
                'discrete_inputs': [False] * 8,
                'holding_registers': [800, 0, 0, 0, 800, 0, 0, 0],
                'input_registers': [800, 0, 0, 0, 0, 0, 0, 0],
                'motor_running': False,
                'pump_running': False,
                'scan_time': 0.1
            }
        
        await websocket.send_text(json.dumps({
            "kind": "state",
            "payload": initial_state
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["kind"] == "action":
                    payload = message["payload"]
                    success = False
                    
                    if plc is not None and MODULES_AVAILABLE:
                        try:
                            if payload.get("action_type") == "toggle_input":
                                address = int(payload["address"])
                                current_state = get_plc_state()
                                new_value = not current_state["discrete_inputs"][address]
                                success = set_discrete_input(address, new_value)
                                
                            elif payload.get("action_type") == "set_register":
                                address = int(payload["address"])
                                value = int(payload["value"])
                                success = set_holding_register(address, value)
                                
                            elif payload.get("flip") is not None:  # Legacy support
                                address = int(payload["flip"])
                                current_state = get_plc_state()
                                new_value = not current_state["discrete_inputs"][address]
                                success = set_discrete_input(address, new_value)
                        except Exception as e:
                            logger.error(f"Error processing action: {e}")
                    else:
                        # Mock success in simulation mode
                        success = True
                    
                    if success:
                        # Broadcast updated state to all clients
                        if plc is not None and MODULES_AVAILABLE:
                            try:
                                state_payload = get_plc_state()
                            except:
                                state_payload = initial_state
                        else:
                            # Mock state update
                            state_payload = initial_state
                        
                        await manager.broadcast({
                            "kind": "state",
                            "payload": state_payload
                        })
                        
                elif message["kind"] == "lesson":
                    lesson_name = message["payload"]
                    try:
                        if MODULES_AVAILABLE:
                            content = load_md(lesson_name)
                        else:
                            content = f"# {lesson_name}\n\nLesson content would be loaded here."
                        await websocket.send_text(json.dumps({
                            "kind": "lesson",
                            "payload": content
                        }))
                    except FileNotFoundError:
                        await websocket.send_text(json.dumps({
                            "kind": "error",
                            "payload": f"Lesson '{lesson_name}' not found"
                        }))
                    except Exception as e:
                        logger.error(f"Error loading lesson: {e}")
                        await websocket.send_text(json.dumps({
                            "kind": "error",
                            "payload": f"Error loading lesson: {str(e)}"
                        }))
                        
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "kind": "error",
                    "payload": "Invalid JSON message"
                }))
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Background task to broadcast state updates (only if PLC available)
async def state_broadcaster():
    """Periodically broadcast state updates"""
    while True:
        try:
            if plc is not None and manager.active_connections and MODULES_AVAILABLE:
                try:
                    await manager.broadcast({
                        "kind": "state",
                        "payload": get_plc_state()
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting state: {e}")
            await asyncio.sleep(1)  # Broadcast every second
        except Exception as e:
            logger.error(f"State broadcaster error: {e}")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    if plc is not None and MODULES_AVAILABLE:
        asyncio.create_task(state_broadcaster())
    logger.info("PLC SCADA Lab API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if plc is not None:
        try:
            plc.stop_simulation()
        except:
            pass
    logger.info("PLC SCADA Lab API stopped")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "modules_available": MODULES_AVAILABLE,
        "plc_available": plc is not None,
        "frontend_available": FRONTEND_DIR.exists()
    }