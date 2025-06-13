import json
import pathlib
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from plc_scada_lab.backend.modbus_core import (
    start_modbus, get_plc_state, set_discrete_input, set_holding_register
)
from plc_scada_lab.backend.lessons import list_lessons, load_md

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(title="PLC SCADA Lab", version="1.0.0")

# Mount static files - serve frontend files at /static
FRONTEND_DIR = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

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

# Initialize PLC system
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
        return HTMLResponse(content=index_path.read_text(), status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.get("/api/lessons")
async def get_lessons():
    """Get list of available lessons"""
    return {"lessons": list_lessons()}

@app.get("/api/lesson/{lesson_name}")
async def get_lesson(lesson_name: str):
    """Get specific lesson content"""
    try:
        content = load_md(lesson_name)
        return {"name": lesson_name, "content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Lesson not found")

@app.get("/api/state")
async def get_state():
    """Get current PLC state"""
    if plc is None:
        raise HTTPException(status_code=503, detail="PLC system not available")
    return get_plc_state()

@app.post("/api/action")
async def perform_action(action: ActionRequest):
    """Perform PLC action"""
    if plc is None:
        raise HTTPException(status_code=503, detail="PLC system not available")
        
    success = False
    
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            "kind": "lessons",
            "payload": list_lessons()
        }))
        
        if plc is not None:
            await websocket.send_text(json.dumps({
                "kind": "state",
                "payload": get_plc_state()
            }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["kind"] == "action":
                    payload = message["payload"]
                    success = False
                    
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
                    
                    if success and plc is not None:
                        # Broadcast updated state to all clients
                        await manager.broadcast({
                            "kind": "state",
                            "payload": get_plc_state()
                        })
                        
                elif message["kind"] == "lesson":
                    lesson_name = message["payload"]
                    try:
                        content = load_md(lesson_name)
                        await websocket.send_text(json.dumps({
                            "kind": "lesson",
                            "payload": content
                        }))
                    except FileNotFoundError:
                        await websocket.send_text(json.dumps({
                            "kind": "error",
                            "payload": f"Lesson '{lesson_name}' not found"
                        }))
                        
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "kind": "error",
                    "payload": "Invalid JSON message"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Background task to broadcast state updates
import asyncio

async def state_broadcaster():
    """Periodically broadcast state updates"""
    while True:
        try:
            if plc is not None and manager.active_connections:
                await manager.broadcast({
                    "kind": "state",
                    "payload": get_plc_state()
                })
            await asyncio.sleep(1)  # Broadcast every second
        except Exception as e:
            logger.error(f"State broadcaster error: {e}")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(state_broadcaster())
    logger.info("PLC SCADA Lab API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if plc is not None:
        plc.stop_simulation()
    logger.info("PLC SCADA Lab API stopped")