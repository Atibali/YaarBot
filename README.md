# YaarBot Full Duplex Voice Assistant (Local Mode)

Real-time friendly voice assistant loop:

Mic -> Whisper (local STT) -> Ollama (local LLM) -> pyttsx3 (local TTS) -> Speaker

## Features

- Fully local model pipeline (no OpenAI API)
- Continuous listening loop
- Barge-in interruption support
- Hinglish-friendly conversation
- Wake-word mode (`hey yaarbot`)

## Prerequisites

- Python 3.10+
- Working microphone + speaker
- [Ollama](https://ollama.com/) installed and running
- One local chat model pulled in Ollama (default used here: `llama3.1:8b`)

## Setup

1. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

2. Start Ollama server (usually auto-runs after install), then pull model:

```powershell
ollama pull llama3.1:8b
```

3. Run bot:

```powershell
python assistant.py
```

## Notes

- Wake word required by default: say `hey yaarbot` before query.
- Press `Ctrl + C` to stop.
- To disable wake word, set `wake_word_enabled=False` in `VoiceConfig`.
- To use another model, change `ollama_model` in `VoiceConfig`.
