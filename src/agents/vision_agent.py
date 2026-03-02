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
Your job is to look at a screenshot, understand the user's goal, and output the EXACT sequences of physical actions needed.

CRITICAL RULES:
1. YOU DO NOT HAVE ACCESS TO THE HTML DOM.
2. The user has pre-processed the screenshot to draw RED BOUNDING BOXES over clickable elements. Each box has a numerical ID in white text (e.g., [12]).
3. Instead of guessing X/Y coordinates, you must specify the 'id' of the bounding box you want to target.
4. You must employ the Triple-Check Consensus Protocol to prevent hallucinations before outputting the final array.
5. Your output MUST strictly match the exact JSON schema provided.

TRIPLE-CHECK SCHEMA:
{
    "final_action_plan": [
        {
            "action": "click" | "type" | "scroll" | "wait",
            "id": <integer ID of the target red box, omit if scrolling/waiting>,
            "text": "<optional text to type>"
        }
    ]
}

Before answering, review the "Long Term Memory Rules". If a rule exists, adhere to it over your own logic. Do not output any reasoning text, only output the final JSON array."""

    def analyze_screen(self, base64_image: str, coordinate_map: dict, user_intent: str, memory_rules: list) -> list:
        Logger.agent("Vision", f"Analyzing intent via Triple-Check Consensus: '{user_intent}'")
        
        try:
            image_data = base64.b64decode(base64_image)
            pil_image = Image.open(io.BytesIO(image_data))
            
            rules_str = "\n".join([f"- {rule}" for rule in memory_rules]) if memory_rules else "None"
            
            prompt = f"""
USER INTENT: {user_intent}

LONG TERM MEMORY RULES:
{rules_str}

Evaluate the annotated screenshot using the Triple-Check Schema and output the JSON result.
"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[pil_image, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.2, # Slight variance for creative critique
                    response_mime_type="application/json",
                )
            )

            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
                
                action_plan = result.get("final_action_plan", [])
                
                if not isinstance(action_plan, list):
                    action_plan = [action_plan]
                    
                Logger.success(f"Vision Agent finalized a {len(action_plan)} step execution plan.")
                
                compiled_plan = []
                for step in action_plan:
                    step_id = step.get("id")
                    if step_id is not None:
                        try:
                            step_id = int(step_id)
                        except ValueError:
                            pass
                            
                        coords = coordinate_map.get(step_id)
                        if coords:
                            step["x"] = coords[0]
                            step["y"] = coords[1]
                        else:
                            Logger.error(f"Judge hallucinated ID {step_id} which does not exist in OpenCV map!")
                            
                    compiled_plan.append(step)
                    
                return compiled_plan
                
            except json.JSONDecodeError:
                Logger.error(f"Failed to parse Tri-Reasoning JSON. Raw: {response_text}")
                return []
                
        except Exception as e:
            Logger.error(f"Vision API Tri-Check call failed: {e}")
            return []
