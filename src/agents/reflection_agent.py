import os
import json
from google import genai
from google.genai import types
from PIL import Image
from src.utils.logger import Logger

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'long_term_memory.json')

class ReflectionAgent:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        self.system_instruction = """You are the Self-Reflection Module for a UI Automation Agent.
The agent attempted an action, but the user reported it failed or was incorrect.

Your job is to look at the 'Before' and 'After' screenshots, alongside the attempted action, and deduce exactly WHY it failed.
Then, you must formulate a concise, universal rule to prevent this mistake in the future.

Your output MUST be valid JSON:
{
    "mistake_analysis": "What went wrong",
    "new_rule": "The short, universal rule to add to memory (e.g. 'If a cookie banner is present, close it before clicking login.')"
}"""

    def _load_memory(self) -> list:
        if not os.path.exists(MEMORY_FILE):
            return []
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_memory(self, memory: list):
        try:
            with open(MEMORY_FILE, 'w') as f:
                json.dump(memory, f, indent=4)
            Logger.memory(f"Memory saved to disk. Total rules: {len(memory)}")
        except Exception as e:
            Logger.error(f"Failed to save memory: {e}")

    def get_rules(self) -> list:
        """Returns the current list of learned rules."""
        return self._load_memory()

    def reflect_on_failure(self, before_img_path: str, after_img_path: str, attempted_action: dict, user_complaint: str):
        """
        Analyzes a failure and saves a new rule to memory.
        """
        Logger.agent("Reflection", "Initiating failure analysis...")
        
        try:
            img_before = Image.open(before_img_path)
            img_after = Image.open(after_img_path)
            
            prompt = f"""
Attempted Action: {json.dumps(attempted_action)}
User Complaint: "{user_complaint}"
Image 1: Before Action
Image 2: After Action

Output the JSON analysis and the new rule to learn.
"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[img_before, img_after, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.2,
                    response_mime_type="application/json",
                )
            )
            
            parsed = json.loads(response.text.strip())
            new_rule = parsed.get("new_rule")
            
            if new_rule:
                Logger.success(f"Lesson Learned: {new_rule}")
                
                # Append to memory
                mem = self._load_memory()
                if new_rule not in mem:
                    mem.append(new_rule)
                    self._save_memory(mem)
            else:
                Logger.warn("Reflection failed to extract a reusable rule.")
                
        except Exception as e:
            Logger.error(f"Reflection API call failed: {e}")
