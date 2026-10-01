from typing import Dict, Any, Tuple
from utils.logger import get_logger

logger = get_logger("SignalProcessor")

class SignalProcessor:
    def __init__(self) -> None:
        # Ayarlar artık dinamik olarak arayüzden gelecek
        self.deadzone_left = 0.15
        self.deadzone_right = 0.15

    def _apply_radial_deadzone(self, x: float, y: float, deadzone: float) -> Tuple[float, float]:
        magnitude = (x**2 + y**2)**0.5
        if magnitude <= deadzone or magnitude == 0.0:
            return 0.0, 0.0
        normalized_mag = (magnitude - deadzone) / (1.0 - deadzone)
        ratio = normalized_mag / magnitude
        return x * ratio, y * ratio

    def process(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        axes = raw_state.get("axes", [])
        buttons = raw_state.get("buttons", [])
        hats = raw_state.get("hats", [])

        processed = {}

        lx = axes[0] if len(axes) > 0 else 0.0
        ly = axes[1] if len(axes) > 1 else 0.0
        rx = axes[2] if len(axes) > 2 else 0.0
        ry = axes[3] if len(axes) > 3 else 0.0

        lx, ly = self._apply_radial_deadzone(lx, ly, self.deadzone_left)
        rx, ry = self._apply_radial_deadzone(rx, ry, self.deadzone_right)
        
        processed["left_joystick"] = (lx, ly)
        processed["right_joystick"] = (rx, ry)
        
        # Jenerik gamepad'lerde tetik tuşlarının axis eşleştirmeleri
        l2_raw = axes[4] if len(axes) > 4 else -1.0
        r2_raw = axes[5] if len(axes) > 5 else -1.0
        
        processed["left_trigger"] = (l2_raw + 1.0) / 2.0
        processed["right_trigger"] = (r2_raw + 1.0) / 2.0

        processed["button_a"] = buttons[0] if len(buttons) > 0 else 0
        processed["button_b"] = buttons[1] if len(buttons) > 1 else 0
        processed["button_x"] = buttons[2] if len(buttons) > 2 else 0
        processed["button_y"] = buttons[3] if len(buttons) > 3 else 0
        processed["button_lb"] = buttons[4] if len(buttons) > 4 else 0
        processed["button_rb"] = buttons[5] if len(buttons) > 5 else 0
        processed["button_back"] = buttons[6] if len(buttons) > 6 else 0
        processed["button_start"] = buttons[7] if len(buttons) > 7 else 0
        processed["button_l3"] = buttons[8] if len(buttons) > 8 else 0
        processed["button_r3"] = buttons[9] if len(buttons) > 9 else 0

        processed["dpad"] = hats[0] if len(hats) > 0 else (0, 0)

        return processed
