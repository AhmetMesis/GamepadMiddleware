# 🎮 Gamepad Middleware & Virtual Driver System

A high-performance Python-based middleware system designed to intercept, process, and output gamepad/joystick signals. It acts as a bridge between your physical controller and your operating system, allowing you to manipulate inputs (e.g., deadzone fixing, macros, rebinding) before passing them to a virtual gamepad.

It also features a built-in **FastAPI / WebSocket** server to broadcast real-time telemetry data of the gamepad inputs over the network.

---

## ✨ Features

- **🕹️ Physical Input Reading:** Utilizes `pygame` to accurately read raw inputs (axes, buttons, hats) from any connected physical gamepad.
- **⚙️ Signal Processing Pipeline:** A modular `SignalProcessor` that can manipulate raw data (e.g., adjust sensitivity, invert axes, apply deadzones) before it hits the game.
- **👾 Virtual Controller Emulation:** Uses `vgamepad` to create a virtual Xbox 360 or DualShock 4 controller at the OS level. Games see this virtual controller instead of your physical one.
- **🌐 WebSockets & API:** Runs a `FastAPI` server to expose real-time gamepad telemetry via WebSockets, allowing you to build web-based dashboards or remote-play setups.
- **📝 High-speed Polling:** Optimized polling loop for near zero-latency input translation.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- `pygame` (Input reading)
- `vgamepad` (Virtual controller emulation)
- `fastapi` & `uvicorn` (REST API & WebSocket Server)
- `websockets`

---

## 🚀 Installation & Setup

### Prerequisites
- **Windows OS** (Recommended) since `vgamepad` utilizes the ViGEmBus driver.
- Ensure [ViGEmBus](https://github.com/nefarius/ViGEmBus) is installed on your Windows machine to allow virtual controller creation.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/GamepadMiddleware.git
cd GamepadMiddleware
```

### 2. Install Dependencies
It is highly recommended to use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Middleware
To start the core pipeline (Reader -> Processor -> Virtual Output):
```bash
python main.py
```
*(Make sure your physical controller is plugged in before starting).*

### 4. Run the Web/Telemetry Server (Optional)
If you want to view the controller data over the network or browser:
```bash
python server.py
```

---

## ⚙️ How It Works (The Pipeline)

1. **InputReader:** Hooks into the physical gamepad using `pygame.joystick` and polls for changes.
2. **SignalProcessor:** Receives the raw dictionary of buttons/axes and applies transformations based on your custom logic.
3. **VirtualOutput:** Pushes the modified states to the OS using `vgamepad` (ViGEmBus API).

---

## 📄 License
This project is open-source under the MIT License.
