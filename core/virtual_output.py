import vgamepad as vg
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger("VirtualOutput")

class VirtualOutput:
    """
    İşlenmiş gamepad verisini alarak işletim sistemine "Kusursuz çalışan bir 
    Sanal Xbox 360 Kolu" olarak ileten katman.
    """
    def __init__(self) -> None:
        try:
            self.gamepad = vg.VX360Gamepad()
            logger.info("Sanal Xbox 360 Kontrolcüsü OS seviyesinde başarıyla oluşturuldu.")
        except Exception as e:
            logger.error(f"Sanal kontrolcü oluşturulurken kritik hata: {e}")
            raise

    def inject_data(self, state: Dict[str, Any]) -> None:
        """
        Processor'den gelen sanitize edilmiş veriyi sanal sürücüye aktarır.
        """
        # Tetikler (Float: 0.0 to 1.0)
        self.gamepad.left_trigger_float(value_float=state.get("left_trigger", 0.0))
        self.gamepad.right_trigger_float(value_float=state.get("right_trigger", 0.0))

        # Analog Kollar (Float: -1.0 to 1.0)
        # Pygame'de Y ekseni genellikle ters döner (aşağı pozitif, yukarı negatiftir).
        # Bu durumu düzeltmek için Y değerinin önüne '-' ekleyebiliriz (-ly, -ry).
        lx, ly = state.get("left_joystick", (0.0, 0.0))
        rx, ry = state.get("right_joystick", (0.0, 0.0))
        self.gamepad.left_joystick_float(x_value_float=lx, y_value_float=-ly)
        self.gamepad.right_joystick_float(x_value_float=rx, y_value_float=-ry)

        # Basılı tutulan tuşları OS'e bas olarak, çekilenleri bırak olarak iletiyoruz
        button_map = {
            "button_a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            "button_b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "button_x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            "button_y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "button_lb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "button_rb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "button_back": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "button_start": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            "button_l3": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "button_r3": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB
        }

        for btn_key, vg_btn in button_map.items():
            if state.get(btn_key):
                self.gamepad.press_button(button=vg_btn)
            else:
                self.gamepad.release_button(button=vg_btn)

        # D-Pad işlemleri (x ve y düzlemi ayrı değerlendirilir)
        dpad_x, dpad_y = state.get("dpad", (0, 0))
        
        # D-Pad Y (Yukarı/Aşağı)
        if dpad_y == 1:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        elif dpad_y == -1:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        else:
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

        # D-Pad X (Sağ/Sol)
        if dpad_x == 1:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        elif dpad_x == -1:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        else:
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)

        # Sonuç: Update metodunu çağırarak işletim sistemine veriyi gönderiyoruz
        self.gamepad.update()
