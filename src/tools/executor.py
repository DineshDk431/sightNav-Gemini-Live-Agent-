"""
SightNav — Executor Tool
========================
Interprets the JSON output from the Vision agent and executes the safe
keyboard and mouse actions via PyAutoGUI.
"""

import time
import pyautogui
from src.utils.logger import Logger

# Global safety settings
pyautogui.FAILSAFE = True  # Moving mouse to a corner aborts the program
pyautogui.PAUSE = 0.5      # 0.5s pause after every PyAutoGUI call


def execute_action(action_data: dict) -> bool:
    """
    Executes a parsed JSON action from the Vision Agent.
    
    Format expected:
    {
        "action": "click" | "type" | "scroll" | "wait",
        "x": int (optional),
        "y": int (optional),
        "text": str (optional),
        "clicks": int (optional, default 1),
        "amount": int (optional, for scrolling)
    }
    
    Returns:
        bool: True if execution succeeded, False otherwise
    """
    try:
        action_type = action_data.get("action", "").lower()
        Logger.action(f"Executing: {action_data}")

        if not action_type:
            Logger.error("Action dictionary missing 'action' key.")
            return False

        # 1. CLICK
        if action_type == "click":
            x = action_data.get("x")
            y = action_data.get("y")
            clicks = action_data.get("clicks", 1)
            
            if x is None or y is None:
                Logger.error("Click action requires 'x' and 'y' coordinates.")
                return False
                
            # PyAutoGUI handles the movement automatically in click() if x and y are provided
            # A 0.5s movement duration as per instructions makes it look human
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click(clicks=clicks)
            Logger.success(f"Clicked at ({x}, {y})")

        # 2. TYPE
        elif action_type == "type":
            text = action_data.get("text")
            if not text:
                Logger.error("Type action requires 'text'.")
                return False
                
            # Optional: Move & click before typing if coords are provided
            x = action_data.get("x")
            y = action_data.get("y")
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                time.sleep(0.2)
                
            pyautogui.write(text, interval=0.05)
            # Standard behaviour is to press enter after typing in forms
            if action_data.get("press_enter", True):
                pyautogui.press("enter")
            Logger.success(f"Typed text: '{text}'")

        # 3. SCROLL
        elif action_type == "scroll":
            amount = action_data.get("amount", -500) # Negative often means scroll down
            pyautogui.scroll(amount)
            Logger.success(f"Scrolled by {amount}")

        # 4. WAIT
        elif action_type == "wait":
            duration = action_data.get("duration", 2.0)
            Logger.info(f"Waiting for {duration} seconds...")
            time.sleep(duration)

        else:
            Logger.error(f"Unknown action type: {action_type}")
            return False

        return True

    except pyautogui.FailSafeException:
        Logger.error("FailSafe triggered! Mouse was moved to a screen corner.")
        return False
    except Exception as e:
        Logger.error(f"Execution failed: {e}")
        return False
