import sys
import numpy as np
import speech_recognition as sr
import pyttsx3
from faster_whisper import WhisperModel
from src.utils.logger import Logger

class AudioAgent:
    def __init__(self):
        Logger.info("Booting Audio Engine...")
        self.recognizer = sr.Recognizer()    
        
        # Initialize Faster Whisper Local Model
        Logger.info("Loading Faster-Whisper (tiny.en) for Local Transcription...")
        try:
            # Using CPU and int8 for maximum compatibility, 'tiny.en' provides near real-time blazing speeds.
            self.model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            Logger.success("Local Whisper Model Loaded.")
        except Exception as e:
            Logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
            
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
                
            Logger.info("Processing audio locally via Whisper...")
            
            # Convert raw 16-bit PCM Audio to float32 NumPy array normalized to [-1.0, 1.0] for Whisper
            raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
            audio_array = np.frombuffer(raw_data, np.int16).astype(np.float32) / 32768.0
            
            if self.model:
                segments, info = self.model.transcribe(audio_array, beam_size=5, language="en")
                text = "".join([segment.text for segment in segments]).strip()
            else:
                # Fallback if model failed to load
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
            return "ERROR_MIC_FAIL"

    def speak(self, text: str):
        Logger.agent("Audio Out", text)
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                Logger.error(f"TTS Engine skipped: {e}")
        Logger.divider()
