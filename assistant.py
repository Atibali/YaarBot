import io
import json
import os
import queue
import threading
import time
import wave
from dataclasses import dataclass
from typing import Any

import numpy as np
import requests
import sounddevice as sd
import webrtcvad

from emotion_detector import EmotionDetector
from personality_manager import PersonalityManager

try:
    import whisper
except ImportError:
    whisper = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
BYTES_PER_SAMPLE = 2


@dataclass
class VoiceConfig:
    wake_word: str = "hey yaarbot"
    wake_word_enabled: bool = True
    whisper_model: str = "small"
    ollama_model: str = "llama3.1:8b"
    ollama_url: str = "http://127.0.0.1:11434/api/chat"
    tts_rate: int = 185


class FullDuplexAssistant:
    def __init__(self, config: VoiceConfig):
        self.config = config

        if whisper is None:
            raise RuntimeError("Missing dependency: whisper. Install from requirements.txt")
        if pyttsx3 is None:
            raise RuntimeError("Missing dependency: pyttsx3. Install from requirements.txt")

        self.offline_whisper = whisper.load_model(self.config.whisper_model)
        self.offline_tts = pyttsx3.init()
        self.offline_tts.setProperty("rate", self.config.tts_rate)

        self.audio_queue: queue.Queue[bytes] = queue.Queue()
        self.speaking_event = threading.Event()
        self.interrupt_event = threading.Event()
        self.shutdown_event = threading.Event()

        self.vad = webrtcvad.Vad(2)

        self.emotion_detector = EmotionDetector()
        self.personality_manager = PersonalityManager()
        self.last_emotion = None

        self.history: list[dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are YaarBot, a friendly real-time voice assistant. "
                    "Reply conversationally and briefly. Be helpful, witty when asked, and safe. "
                    "You have good humor and sometimes dark humor—use it wisely based on context."
                ),
            }
        ]

    def mic_callback(self, indata, _frames, _time_info, status):
        if status:
            print(f"[mic] {status}")
        chunk = (indata[:, 0] * 32767).astype(np.int16).tobytes()
        self.audio_queue.put(chunk)

    def capture_utterance(self) -> bytes | None:
        silence_frames = int(450 / FRAME_MS)
        max_frames = int(10_000 / FRAME_MS)
        pre_roll = int(240 / FRAME_MS)

        ring: list[bytes] = []
        voiced: list[bytes] = []

        in_speech = False
        silent_count = 0
        seen_speech = 0

        while not self.shutdown_event.is_set():
            try:
                frame = self.audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if len(frame) != FRAME_SIZE * BYTES_PER_SAMPLE:
                continue

            is_speech = self.vad.is_speech(frame, SAMPLE_RATE)

            if not in_speech:
                ring.append(frame)
                if len(ring) > pre_roll:
                    ring.pop(0)

                if is_speech:
                    in_speech = True
                    voiced.extend(ring)
                    voiced.append(frame)
                    seen_speech += 1
                    ring.clear()

                    if self.speaking_event.is_set():
                        self.interrupt_event.set()
            else:
                voiced.append(frame)
                if is_speech:
                    silent_count = 0
                    seen_speech += 1
                else:
                    silent_count += 1

                if silent_count >= silence_frames or len(voiced) >= max_frames:
                    break

        if seen_speech < 3 or not voiced:
            return None

        return b"".join(voiced)

    @staticmethod
    def pcm_to_wav_bytes(pcm: bytes) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(BYTES_PER_SAMPLE)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm)
        buffer.seek(0)
        return buffer.read()

    def transcribe(self, pcm: bytes) -> str:
        wav_data = self.pcm_to_wav_bytes(pcm)
        tmp = "_tmp_utterance.wav"
        with open(tmp, "wb") as f:
            f.write(wav_data)

        try:
            out = self.offline_whisper.transcribe(tmp, fp16=False, language="en")
            return (out.get("text") or "").strip()
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass

    def ask_brain(self, user_text: str) -> str:
        emotion_data = self.emotion_detector.detect(user_text)
        self.last_emotion = emotion_data

        emotion_instruction = self.personality_manager.get_emotion_context_instruction(emotion_data)
        dynamic_system = self.personality_manager.get_system_prompt_with_emotion(emotion_data)

        if self.history[0]["role"] == "system":
            self.history[0]["content"] = dynamic_system

        self.history.append({"role": "user", "content": user_text})

        payload: dict[str, Any] = {
            "model": self.config.ollama_model,
            "messages": self.history,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 120,
            },
        }

        try:
            response = requests.post(self.config.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {})
            answer = (message.get("content") or "").strip()
        except Exception as exc:
            print(f"[brain] local model failed: {exc}")
            answer = f"Maine suna: {user_text}. Local model issue aa gaya."

        if not answer:
            answer = "Sorry, mujhe dubara bolna padega."

        self.history.append({"role": "assistant", "content": answer})
        if len(self.history) > 14:
            self.history = [self.history[0]] + self.history[-13:]

        return answer

    def speak_offline_interruptible(self, text: str):
        self.speaking_event.set()
        self.interrupt_event.clear()

        try:
            self.offline_tts.say(text)
            self.offline_tts.runAndWait()
        except Exception as e:
            print(f"[TTS Error] {e}")
        finally:
            self.speaking_event.clear()
            self.interrupt_event.clear()

    def run(self):
        print("YaarBot local mode started. Ctrl+C to stop.")
        if self.config.wake_word_enabled:
            print(f"Wake word mode ON. Say '{self.config.wake_word}' to activate.")
        else:
            print("Wake word mode OFF. Listening continuously.")

        greeting = "Hey! I'm YaarBot. What's on your mind?"
        print(f"Bot: {greeting}")
        self.speak_offline_interruptible(greeting)

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize=FRAME_SIZE,
            callback=self.mic_callback,
        ):
            while not self.shutdown_event.is_set():
                try:
                    pcm = self.capture_utterance()
                    if not pcm:
                        continue

                    text = self.transcribe(pcm)
                    if not text:
                        continue

                    print(f"\nYou: {text}")

                    if self.config.wake_word_enabled:
                        lowered = text.lower()
                        if self.config.wake_word not in lowered:
                            continue

                        text = lowered.replace(self.config.wake_word, "", 1).strip()
                        if not text:
                            prompt = "Haan, bolo?"
                            print(f"Bot: {prompt}")
                            self.speak_offline_interruptible(prompt)
                            continue

                    reply = self.ask_brain(text)
                    print(f"Bot: {reply}")
                    self.speak_offline_interruptible(reply)

                except KeyboardInterrupt:
                    self.shutdown_event.set()
                    break
                except Exception as exc:
                    print(f"[error] {exc}")
                    time.sleep(0.6)


if __name__ == "__main__":
    bot = FullDuplexAssistant(VoiceConfig(wake_word_enabled=False))
    bot.run()
