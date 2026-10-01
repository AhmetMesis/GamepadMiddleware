import asyncio
import os
import json
import ctypes
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.input_reader import InputReader
from core.processor import SignalProcessor
from core.virtual_output import VirtualOutput
from utils.logger import get_logger

logger = get_logger("Server")

app = FastAPI()

web_dir = os.path.join(os.path.dirname(__file__), "web")
app.mount("/static", StaticFiles(directory=web_dir), name="static")

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

middleware_config = {
    "deadzone_left": 0.15,
    "deadzone_right": 0.15
}

def load_config():
    global middleware_config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                middleware_config.update(loaded)
        except Exception:
            pass

def save_config():
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(middleware_config, f, indent=4)
    except Exception:
        pass

load_config()

@app.get("/")
async def get():
    with open(os.path.join(web_dir, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()
reader_instance = None 

# --- NATIVE WINDOWS XINPUT RUMBLE (TİTREŞİM) MOTORU ---
class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]

def get_xinput():
    try: return ctypes.windll.xinput1_4
    except: 
        try: return ctypes.windll.xinput1_3
        except:
            try: return ctypes.windll.xinput9_1_0
            except: return None

xinput_dll = get_xinput()

async def trigger_native_rumble(low: float, high: float, duration_ms: int):
    # Windows'un çekirdek XInput sürücüsü üzerinden doğrudan motora voltaj gönder
    if xinput_dll:
        vib = XINPUT_VIBRATION(int(low * 65535), int(high * 65535))
        for i in range(4): # Bağlı olabilecek 4 portu da sars (Böylece kaçıncı portta olursa olsun titrer)
            xinput_dll.XInputSetState(i, ctypes.byref(vib))
        
        await asyncio.sleep(duration_ms / 1000.0)
        
        stop_vib = XINPUT_VIBRATION(0, 0)
        for i in range(4):
            xinput_dll.XInputSetState(i, ctypes.byref(stop_vib))
    else:
        # Eski sistem yedeği
        if reader_instance and reader_instance.joystick:
            try: reader_instance.joystick.rumble(low, high, duration_ms)
            except: pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_json({
        "type": "init_config",
        "data": middleware_config
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "config_update":
                cfg = message.get("data", {})
                if "deadzone_left" in cfg:
                    middleware_config["deadzone_left"] = float(cfg["deadzone_left"])
                if "deadzone_right" in cfg:
                    middleware_config["deadzone_right"] = float(cfg["deadzone_right"])
                save_config()
                
            elif message.get("type") == "test_rumble":
                data = message.get("data", {})
                low = data.get("low", 0.0)
                high = data.get("high", 0.0)
                duration = data.get("duration", 800)
                # Arka planda native titreşimi başlat
                asyncio.create_task(trigger_native_rumble(low, high, duration))
                        
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def gamepad_loop():
    logger.info("Gamepad Veri Motoru Baslatildi.")
    global reader_instance
    reader_instance = InputReader()
    processor = SignalProcessor()
    try:
        output = VirtualOutput()
    except Exception:
        output = None

    async for raw_state in reader_instance.read_events():
        processor.deadzone_left = middleware_config["deadzone_left"]
        processor.deadzone_right = middleware_config["deadzone_right"]
        processed_state = processor.process(raw_state)
        if output:
            output.inject_data(processed_state)
        if manager.active_connections:
            await manager.broadcast({
                "type": "gamepad_data",
                "processed": processed_state
            })
        await asyncio.sleep(0.01)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(gamepad_loop())

if __name__ == "__main__":
    print("\n" + "="*50)
    print("[>] GAMEPAD STUDIO PRO BASLATILDI!")
    print("[>] Arayuzu Gormek Icin Tarayiciyi Acin: http://127.0.0.1:8000")
    print("="*50 + "\n")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False, log_level="error")
