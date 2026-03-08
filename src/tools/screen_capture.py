import os
import base64
import time
from io import BytesIO
from PIL import ImageGrab
from src.utils.logger import Logger

SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def capture_screen(save_debug: bool = True) -> tuple[str, str]:
    try:
        # Capture current screen
        Logger.info("Capturing primary screen...")
        screenshot = ImageGrab.grab()
        
        # Save to memory buffer
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        
        # Encode to base64
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Save debug copy if requested
        file_path = ""
        if save_debug:
            timestamp = int(time.time() * 1000)
            file_path = os.path.join(SCREENSHOTS_DIR, f"capture_{timestamp}.png")
            screenshot.save(file_path)
            Logger.info(f"Screenshot saved to {file_path}")
            
        return img_str, file_path
        
    except Exception as e:
        Logger.error(f"Failed to capture screen: {e}")
        return "", ""
