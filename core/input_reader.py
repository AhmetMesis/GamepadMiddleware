import asyncio
import os
import pygame
from typing import AsyncGenerator, Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger("InputReader")

class InputReader:
    def __init__(self) -> None:
        # ÇOK ÖNEMLİ: Pygame (SDL2), uygulama penceresi odakta (focus) değilken
        # güvenlik sebebiyle gamepad verisi okumayı durdurur. 
        # Bunu aşmak ve sistemin arka planda akıcı çalışmasını sağlamak için bu ayar şarttır:
        os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
        
        pygame.init()
        pygame.display.init()
        try:
            # Görev çubuğunda bile çıkmayan gizli pencere
            pygame.display.set_mode((1, 1), pygame.HIDDEN | pygame.NOFRAME)
        except Exception as e:
            logger.warning(f"Gizli pencere açılamadı: {e}")
            
        pygame.joystick.init()
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self._connect_joystick()

    def _connect_joystick(self) -> bool:
        count = pygame.joystick.get_count()
        if count > 0:
            # Sisteme bağlanan ilk oyun kolunu her zaman ana fiziksel kol olarak kabul et
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            logger.info(f"[>] Fiziksel Oyun Kolu Aktif: {self.joystick.get_name()}")
            return True
        return False

    async def read_events(self) -> AsyncGenerator[Dict[str, Any], None]:
        while True:
            # Pygame event kuyruğunu tüket (Bu döngü, arka plan verilerinin akmasını sağlar)
            for event in pygame.event.get():
                pass 
            
            if self.joystick is None or pygame.joystick.get_count() == 0:
                if not self._connect_joystick():
                    await asyncio.sleep(1.0)
                    continue
            
            try:
                state = {
                    "axes": [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())],
                    "buttons": [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())],
                    "hats": [self.joystick.get_hat(i) for i in range(self.joystick.get_numhats())]
                }
                yield state
            except pygame.error as e:
                logger.warning(f"Bağlantı koptu, yeniden aranıyor... Hata: {e}")
                self.joystick = None
                pygame.joystick.quit()
                pygame.joystick.init()
                await asyncio.sleep(1.0)
