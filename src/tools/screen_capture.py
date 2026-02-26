"""
SightNav — Screen Capture Tool
==============================
Captures the primary monitor and converts it into a Base64 encoded PNG 
string to be sent to the Gemini Vision API.
Also saves debug copies to `data/screenshots/` for the Reflection Agent.
"""

import os
import base64
import time
from io import BytesIO
from PIL import ImageGrab
from src.utils.logger import Logger

# Ensure screenshots directory exists
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def capture_screen(save_debug: bool = True) -> tuple[str, str]:
    """
    Captures the primary screen.
    
    Args:
        save_debug: If True, saves a PNG file to data/screenshots/
        
    Returns:
        tuple[str, str]: (base64_encoded_png_string, file_path_if_saved)
    """
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
