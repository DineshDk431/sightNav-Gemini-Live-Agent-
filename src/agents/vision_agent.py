"""
SightNav — Vision Agent
=======================
Send a screenshot and user goal to Gemini 2.0 Flash Multimodal.
Instructs Gemini to return strict JSON containing (x,y) coordinates
and the physical action to take.
"""

import os
import json
from google import genai
from google.genai import types
from PIL import Image
from src.utils.logger import Logger

class VisionAgent:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            Logger.error("GEMINI_API_KEY missing or invalid in .env")
            
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"

        self.system_instruction = """You are an Autonomous UI Navigation Agent.
Your job is to look at a screenshot, understand the user's goal, and output the EXACT physical mouse/keyboard action needed to achieve that goal.

CRITICAL RULES:
1. YOU DO NOT HAVE ACCESS TO THE DOM.
2. You must estimate the absolute (X, Y) pixel coordinates of the target element based on the screenshot provided.
3. Assume the screenshot covers the entire primary monitor.
4. Your output MUST be valid JSON and nothing else.

OUTPUT FORMAT:
{
    "action": "click" | "type" | "scroll" | "wait",
    "x": <integer X coordinate of the target center>,
    "y": <integer Y coordinate of the target center>,
    "text": "<optional text to type>",
    "reasoning": "<brief explanation of why you chose these coordinates>"
}

Before answering, review the "Long Term Memory Rules" provided by the user. If a rule applies (e.g., 'always close popups first'), you must follow it."""

    def analyze_screen(self, image_path: str, user_intent: str, memory_rules: list) -> dict:
        """
        Sends the image and intent to Gemini and parses the JSON response.
        """
        Logger.agent("Vision", f"Analyzing intent: '{user_intent}'")
        
        try:
            pil_image = Image.open(image_path)
            
            # Format memory rules
            rules_str = "\n".join([f"- {rule}" for rule in memory_rules]) if memory_rules else "None"
            
            prompt = f"""
USER INTENT: {user_intent}

LONG TERM MEMORY RULES:
{rules_str}

Analyze the screenshot and return the JSON action to execute the user intent.
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
                parsed_json = json.loads(response_text)
                Logger.success("Vision Agent returned valid JSON plan")
                Logger.info(f"Reasoning: {parsed_json.get('reasoning', '')}")
                return parsed_json
            except json.JSONDecodeError:
                Logger.error(f"Failed to parse JSON from Vision Agent. Raw: {response_text}")
                return {}
                
        except Exception as e:
            Logger.error(f"Vision API call failed: {e}")
            return {}
