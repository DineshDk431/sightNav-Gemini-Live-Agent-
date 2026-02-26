"""
SightNav — Audio Agent
======================
Handles communication with the user.

NOTE: PyAudio installation was bypassed due to C++ missing headers on 
this environment. This module currently acts as a text-based 
terminal fallback, meaning you type your 'voice' commands manually.

When PyAudio is resolved, this can be upgraded to the Gemini Live API.
"""

from src.utils.logger import Logger

class AudioAgent:
    def __init__(self):
        Logger.info("Audio Agent initialized in TEXT-ONLY fallback mode.")

    def listen(self) -> str:
        """
        Fakes listening by asking for terminal input.
        """
        Logger.divider("Listening")
        print("\n", end="")
        try:
            user_input = input("🗣️  Your Command: ")
            return user_input.strip()
        except KeyboardInterrupt:
            return "exit"

    def speak(self, text: str):
        """
        Fakes speaking by printing to the terminal.
        """
        Logger.agent("Audio Out", text)
        Logger.divider()
