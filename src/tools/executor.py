import time
import pyautogui
import platform
from src.utils.logger import Logger

pyautogui.FAILSAFE = True  
pyautogui.PAUSE = 0.5      

_scale_factor = None

def get_windows_scaling():
    global _scale_factor
    if _scale_factor is not None:
        return _scale_factor
        
    if platform.system() == "Windows":
        try:
            import ctypes
            # Get physical DPI of primary monitor
            hDC = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hDC, 88) # LOGPIXELSX = 88
            ctypes.windll.user32.ReleaseDC(0, hDC)
            # Standard DPI is 96 (which is 100%)
            _scale_factor = dpi / 96.0
            Logger.info(f"Windows Desktop scaling detected: {int(_scale_factor * 100)}%")
            return _scale_factor
        except Exception as e:
            Logger.warn(f"Failed to detect Windows scaling: {e}. Assuming 100%.")
            _scale_factor = 1.0
            return 1.0
    _scale_factor = 1.0
    return 1.0


def execute_plan(plan_array: list) -> bool:
    """
    Example format expected:
    [
      { "action": "click", "x": 500, "y": 600, "clicks": 1 }
    ]
    """
    if not plan_array:
        Logger.error("Empty execution plan received.")
        return False
        
    scale = get_windows_scaling()
    success_count = 0

    try:
        for step_num, action_data in enumerate(plan_array, 1):
            action_type = action_data.get("action", "").lower()
            Logger.action(f"Step {step_num}/{len(plan_array)} Executing: {action_type}")

            if not action_type:
                continue

            # 1. CLICK
            if action_type == "click":
                raw_x = action_data.get("x")
                raw_y = action_data.get("y")
                clicks = action_data.get("clicks", 1)
                
                if raw_x is None or raw_y is None:
                    Logger.error("Click missing coordinates.")
                    continue
                    
                # APPLY WINDOWS DOT-PITCH SCALING FIX
                x = int(raw_x / scale)
                y = int(raw_y / scale)
                
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click(clicks=clicks)
                Logger.success(f"Clicked at OS coords ({x}, {y}) [Scaled from raw {raw_x}, {raw_y}]")
                success_count += 1

            # 2. TYPE
            elif action_type == "type":
                text = action_data.get("text")
                if not text:
                    continue
                    
                raw_x = action_data.get("x")
                raw_y = action_data.get("y")
                
                if raw_x is not None and raw_y is not None:
                    x = int(raw_x / scale)
                    y = int(raw_y / scale)
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    time.sleep(0.2)
                    
                pyautogui.write(text, interval=0.05)
                if action_data.get("press_enter", True):
                    pyautogui.press("enter")
                Logger.success(f"Typed text: '{text}'")
                success_count += 1

            # 3. SCROLL
            elif action_type == "scroll":
                amount = action_data.get("amount", -500) 
                pyautogui.scroll(amount)
                Logger.success(f"Scrolled by {amount}")
                success_count += 1

            # 4. WAIT
            elif action_type == "wait":
                duration = action_data.get("duration", 2.0)
                Logger.info(f"Waiting for {duration} seconds...")
                time.sleep(duration)
                success_count += 1
                
        # If we executed at least one step successfully, return True
        return success_count > 0

    except pyautogui.FailSafeException:
        Logger.error("FailSafe triggered! Mouse was moved to a screen corner.")
        return False
    except Exception as e:
        Logger.error(f"Execution failed on step {step_num}: {e}")
        return False
