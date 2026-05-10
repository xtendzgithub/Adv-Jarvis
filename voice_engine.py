"""
jarvis/voice_engine.py — Text-to-speech and speech recognition for J.A.R.V.I.S.
"""

import threading
import config

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


class VoiceEngine:
    """Handles TTS (speak) and STT (listen)."""

    def __init__(self):
        self._tts = None
        self._recognizer = None
        self._mic = None
        self._lock = threading.Lock()
        self._init_tts()
        self._init_stt()

    # ── TTS ───────────────────────────────────────────────────────────────────
    def _init_tts(self):
        if not TTS_AVAILABLE:
            print("[Voice] pyttsx3 not installed. TTS disabled.")
            return
        try:
            self._tts = pyttsx3.init()
            voices = self._tts.getProperty('voices')
            if voices:
                # Prefer female voice (index 1) if available
                idx = 1 if config.TTS_VOICE == "female" and len(voices) > 1 else 0
                self._tts.setProperty('voice', voices[idx].id)
            self._tts.setProperty('rate', config.TTS_RATE)
            self._tts.setProperty('volume', config.TTS_VOLUME)
            print("[Voice] TTS engine ready")
        except Exception as e:
            print(f"[Voice] TTS init error: {e}")

    def speak(self, text: str):
        """Speak text aloud (thread-safe)."""
        if not self._tts:
            print(f"[TTS] {text}")
            return
        with self._lock:
            try:
                self._tts.say(text)
                self._tts.runAndWait()
            except Exception as e:
                print(f"[TTS] Speak error: {e}")

    # ── STT ───────────────────────────────────────────────────────────────────
    def _init_stt(self):
        if not SR_AVAILABLE:
            print("[Voice] speech_recognition not installed. STT disabled.")
            return
        try:
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
            self._mic = sr.Microphone()
            print("[Voice] Speech recognition ready")
        except Exception as e:
            print(f"[Voice] STT init error: {e}")

    def listen(self, timeout: int = 10) -> str:
        """Listen for one utterance and return transcribed text."""
        if not SR_AVAILABLE or not self._mic:
            return ""
        try:
            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(source, timeout=timeout,
                                                 phrase_time_limit=15)
            return self._recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[STT] Error: {e}")
            return ""

    @property
    def stt_available(self) -> bool:
        return SR_AVAILABLE and self._mic is not None

    @property
    def tts_available(self) -> bool:
        return TTS_AVAILABLE and self._tts is not None
