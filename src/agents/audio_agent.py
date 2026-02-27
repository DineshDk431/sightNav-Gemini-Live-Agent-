import sys
import speech_recognition as sr
import pyttsx3
from src.utils.logger import Logger

class AudioAgent:
    def __init__(self):
        Logger.info("Booting Audio Engine...")
        self.recognizer = sr.Recognizer()    
        try:
            self.tts = pyttsx3.init()
            voices = self.tts.getProperty('voices')
            for voice in voices:
                if "Zira" in voice.name or "Female" in voice.name:
                    self.tts.setProperty('voice', voice.id)
                    break
        except Exception as e:
            Logger.error(f"Failed to load pyttsx3 TTS engine: {e}")
            self.tts = None

    def listen(self, timeout=5, phrase_time_limit=10) -> str:
        Logger.divider("Microphone Active")
        Logger.info("Listening for command...")
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
            Logger.error(f"Microphone error: {e}")
            print("\n", end="")
            user_input = input("🗣️ [Mic Failed] Type Command: ")
            return user_input.strip()

    def speak(self, text: str):
        Logger.agent("Audio Out", text)
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                Logger.error(f"TTS Engine skipped: {e}")
        Logger.divider()
