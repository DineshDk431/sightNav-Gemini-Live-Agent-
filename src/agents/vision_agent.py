"""
SightNav — Vision Agent
=======================
Upgraded to use Set-of-Mark (SoM) OpenCV overlays.
Receives the ID-tagged screenshot, outputs an ARRAY of 
actions, and translates the chosen IDs back to absolute (x,y).
"""

import os
import json
from google import genai
from google.genai import types
from PIL import Image
import io
import base64
from src.utils.logger import Logger

class VisionAgent:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"

        self.system_instruction = """You are an Autonomous UI Navigation Agent.
Your job is to look at a screenshot, understand the user's goal, and output the EXACT sequences of physical actions needed to achieve that goal.

CRITICAL RULES:
1. YOU DO NOT HAVE ACCESS TO THE HTML DOM.
2. The user has pre-processed the screenshot to draw RED BOUNDING BOXES over clickable elements. Each box has a numerical ID in white text (e.g., [12]).
3. You must output an ARRAY of actions to execute sequentially.
4. Instead of guessing X/Y coordinates, you must specify the 'id' of the bounding box you want to target.
5. Your output MUST be a valid JSON Array and nothing else.

OUTPUT FORMAT:
[
    {
        "action": "click" | "type" | "scroll" | "wait",
        "id": <integer ID of the target red box, omit if scrolling/waiting>,
        "text": "<optional text to type>",
        "reasoning": "<brief explanation of why this action is next>"
    }
]

Before answering, review the "Long Term Memory Rules" provided by the user. If a rule applies (e.g., 'always close popups first'), you must follow it."""

    def analyze_screen(self, base64_image: str, coordinate_map: dict, user_intent: str, memory_rules: list) -> list:
        """
        Sends the SoM image to Gemini.
        Parses the JSON array, and replaces 'id' with actual 'x' and 'y' from coordinate_map.
        """
        Logger.agent("Vision", f"Analyzing intent: '{user_intent}'")
        
        try:
            # Decode base64 back to PIL Image for the GenAI SDK
            image_data = base64.b64decode(base64_image)
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Format memory rules
            rules_str = "\n".join([f"- {rule}" for rule in memory_rules]) if memory_rules else "None"
            
            prompt = f"""
USER INTENT: {user_intent}

LONG TERM MEMORY RULES:
{rules_str}

Analyze the annotated screenshot and return the JSON ARRAY of actions to execute the user intent.
"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[pil_image, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.1,
                    response_mime_type="application/json",
                )
            )

            response_text = response.text.strip()
            
            try:
                # Expecting a list of dicts now
                action_plan = json.loads(response_text)
                if not isinstance(action_plan, list):
                    action_plan = [action_plan] # Force array if model slipped up
                    
                Logger.success(f"Vision Agent returned {len(action_plan)} step plan.")
                
                # IMPORTANT: Map the 'id' back to 'x', 'y' for the Executor
                compiled_plan = []
                for step in action_plan:
                    step_id = step.get("id")
                    if step_id is not None:
                        # Convert string "12" to int 12 just in case
                        try:
                            step_id = int(step_id)
                        except ValueError:
                            pass
                            
                        # Lookup the mapped coordinates from OpenCV
                        coords = coordinate_map.get(step_id)
                        if coords:
                            step["x"] = coords[0]
                            step["y"] = coords[1]
                        else:
                            Logger.warn(f"Gemini returned ID {step_id} which does not exist in the coordinate map!")
                            
                    compiled_plan.append(step)
                    Logger.info(f"Targeting: {step}")
                    
                return compiled_plan
                
            except json.JSONDecodeError:
                Logger.error(f"Failed to parse JSON array from Vision Agent. Raw: {response_text}")
                return []
                
        except Exception as e:
            Logger.error(f"Vision API call failed: {e}")
            return []
