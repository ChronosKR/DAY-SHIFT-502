import json, pathlib
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from backend.modbus_core import start_modbus
from backend.lessons import list_lessons, load_md

UI = pathlib.Path(__file__).parent.parent / "frontend"
app = FastAPI()
app.mount("/", StaticFiles(directory=UI, html=True), name="static")

plc = start_modbus()

def snap():
    return dict(
        coils=plc[0].getValues(1, 0, 8),
        registers=plc[0].getValues(3, 0, 8)
    )

@app.websocket("/ws")
async def socket(ws: WebSocket):
    await ws.accept()
    await ws.send_text(json.dumps({"kind":"lessons", "payload": list_lessons()}))
    await ws.send_text(json.dumps({"kind":"state",   "payload": snap()}))
    while True:
        msg = json.loads(await ws.receive_text())
        if msg["kind"] == "action":
            idx = int(msg["payload"]["flip"])
            cur = plc[0].getValues(1, idx, 1)[0]
            plc[0].setValues(1, idx, [not cur])
            await ws.send_text(json.dumps({"kind":"state","payload":snap()}))
        elif msg["kind"] == "lesson":
            await ws.send_text(json.dumps(
                {"kind":"lesson","payload": load_md(msg["payload"])}
            ))
