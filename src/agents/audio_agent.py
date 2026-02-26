"""
SightNav — Audio Agent
======================
Uses `SpeechRecognition` backed by `sounddevice` to listen
to the user's voice and convert it to text.
Uses `pyttsx3` for lightning-fast Text-to-Speech feedback.
"""

import sys
import speech_recognition as sr
import pyttsx3
from src.utils.logger import Logger

class AudioAgent:
    def __init__(self):
        Logger.info("Booting Audio Engine...")
        
        # Init Speech Recognition (Using the exact mic backend without PyAudio)
        self.recognizer = sr.Recognizer()
        
        # Init TTS Engine
        try:
            self.tts = pyttsx3.init()
            voices = self.tts.getProperty('voices')
            # Try to grab a nice female voice if available, else default
            for voice in voices:
                if "Zira" in voice.name or "Female" in voice.name:
                    self.tts.setProperty('voice', voice.id)
                    break
        except Exception as e:
            Logger.error(f"Failed to load pyttsx3 TTS engine: {e}")
            self.tts = None

    def listen(self, timeout=5, phrase_time_limit=10) -> str:
        """
        Listens to the default active microphone and transcribes to text.
        Falls back to terminal text input if the mic fails.
        """
        Logger.divider("Microphone Active")
        Logger.info("Listening for command...")
        
        # Some SpeechRecognition versions hardcode PyAudio as the default backend.
        # We catch exceptions and fallback smoothly.
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
            Logger.info("Processing audio...")
            text = self.recognizer.recognize_google(audio)
            Logger.user(f"🎙️ '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            Logger.warn("No speech detected. Timeout.")
            return ""
        except sr.UnknownValueError:
            Logger.warn("Speech was unintelligible.")
            return ""
        except (sr.RequestError, OSError, AttributeError) as e:
            # AttributeError usually means PyAudio is entirely missing from the sr.Microphone backend
            Logger.error(f"Microphone error: {e}")
            print("\n", end="")
            user_input = input("🗣️ [Mic Failed] Type Command: ")
            return user_input.strip()

    def speak(self, text: str):
        """
        Speaks the text out loud using local TTS.
        """
        Logger.agent("Audio Out", text)
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                Logger.error(f"TTS Engine skipped: {e}")
        Logger.divider()
