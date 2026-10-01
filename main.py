import time
import sys
from core.input_reader import InputReader
from core.processor import SignalProcessor
from core.virtual_output import VirtualOutput
from utils.logger import get_logger
from utils.config import POLL_RATE

logger = get_logger("MainPipeline")

def main():
    """
    Sistemi ayağa kaldıran ana orkestrasyon fonksiyonu.
    Veri Hattı (Data Pipeline): Reader -> Processor -> Output
    """
    logger.info("=========================================")
    logger.info("Gamepad Middleware Sistemi Başlatılıyor...")
    logger.info("=========================================")
    
    # 1. Modüllerin Başlatılması
    reader = InputReader()
    processor = SignalProcessor()
    
    try:
        output = VirtualOutput()
    except Exception:
        logger.critical("Sanal Sürücü modülü başlatılamadı. Kapatılıyor.")
        sys.exit(1)

    logger.info(f"Sistem hazır! Veri iletim hızı: {POLL_RATE}s. Çıkış için Ctrl+C tuşlarına basın.")

    try:
        # 2. Asenkron/Sonsuz Veri Döngüsü (Pipeline)
        for raw_state in reader.read_events():
            
            # Aşama A: Veriyi İşle, Filtrele, Normalize Et
            processed_state = processor.process(raw_state)
            
            # Aşama B: Veriyi İşletim Sistemine Enjekte Et
            output.inject_data(processed_state)
            
            # Aşama C: İşlemciyi yormamak adına minik gecikme (Polling Rate)
            time.sleep(POLL_RATE)
            
    except KeyboardInterrupt:
        logger.info("\nKullanıcı komutu ile sistem kapatılıyor. (Zarif Kapatma / Graceful Shutdown)")
    except Exception as e:
        logger.critical(f"Pipeline içinde beklenmeyen hata: {e}")
    finally:
        logger.info("Sistem kapatıldı.")

if __name__ == "__main__":
    main()
