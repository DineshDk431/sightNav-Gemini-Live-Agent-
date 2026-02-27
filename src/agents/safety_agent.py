"""
SightNav — Security Gatekeeper (Safety Agent)
==============================================
Acts as a pre-computation bouncer. Intercepts the user's intent 
before any screenshots or tool calls happen. Guards against 
malicious actions and flags medium-risk activities for HITL approval.
"""

import json
from google import genai
from google.genai import types
from src.utils.logger import Logger

class SafetyAgent:
    def __init__(self):
        self.client = genai.Client()
        # Text-only fast model for pre-processing
        self.model_name = "gemini-2.5-flash"
        
        self.system_instruction = """You are the Security Gatekeeper for an Autonomous Computer Control Agent.
The user is about to give a command that will be executed on their local desktop.

Your job is to classify the risk and block dangerous commands BEFORE they happen.

RULES:
1. HIGH RISK (BLOCK IMMEDIATELY): Commands asking to format drives, delete system files (like System32 or OS folders), disable antivirus, execute ransomware, or make unauthorized financial cryptocurrency/bank transfers.
2. MEDIUM RISK (FLAG FOR HUMAN IN THE LOOP): Commands asking to submit forms, send emails, delete user documents, purchase items, or click "Checkout/Pay".
3. SAFE (ALLOW): General navigation, reading, parsing, scrolling, clicking harmless tabs.

Your output MUST be valid JSON:
{
    "risk_level": "high" | "medium" | "safe",
    "is_safe": true | false,
    "violation_reason": "<Why it was blocked or why it needs 'Confirm' verification, else empty string>"
}
Note: For medium risk, set is_safe to false but format the reason as 'Requires HITL: <reason>'
"""

    def check_intent(self, user_intent: str) -> dict:
        """
        Evaluates the raw text intent for safety.
        Returns the JSON dictionary.
        """
        Logger.agent("Safety", f"Scanning intent for security risks: '{user_intent}'")
        
        try:
            prompt = f"USER INTENT TO SCAN: {user_intent}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.0, # Zero variance for security
                    response_mime_type="application/json",
                )
            )

            result = json.loads(response.text.strip())
            risk = result.get("risk_level", "unknown")
            is_safe = result.get("is_safe", False)
            
            if risk == "high":
                Logger.error(f"SECURITY BLOCK (HIGH RISK): {result.get('violation_reason')}")
            elif risk == "medium":
                Logger.warn(f"SECURITY HOLD (HITL REQUIRED): {result.get('violation_reason')}")
            else:
                Logger.success("Security Check Passed. Intent is Safe.")
                
            return result
            
        except Exception as e:
            # Fail-safe closed: If the safety system goes down, block everything.
            Logger.error(f"Safety Agent offline or failed to parse. Blocking action. Error: {e}")
            return {"is_safe": False, "risk_level": "high", "violation_reason": "Safety system offline."}
