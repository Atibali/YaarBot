# YaarBot Full Duplex Voice Assistant (Local Mode)

Real-time friendly voice assistant loop:

Mic -> Whisper (local STT) -> Ollama (local LLM) -> pyttsx3 (local TTS) -> Speaker

## Features

- ✨ **Emotionally Intelligent**: Detects user emotions (joy, sadness, anger, etc.) and responds with empathy
- 🎭 **Personality with Humor**: Good humor, dark humor when contextually appropriate
- 🔊 Fully local model pipeline (no OpenAI API)
- 🎙️ Continuous listening loop with barge-in interruption support
- 🌐 English-primary conversation (was Hinglish-friendly)
- 💬 Wake-word mode (`hey yaarbot`)
- 📊 Real-time emotion tracking for conversation context

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

## How It Works

### Emotion Detection

YaarBot uses VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis to detect your emotional state from your speech/text. It recognizes:

- **Joy**: Upbeat responses, encouragement, matching positive energy
- **Sadness**: Empathetic, supportive tone, gentle humor
- **Anger**: Acknowledgment of frustration, understanding, dark humor if appropriate
- **Curiosity**: Informative, encouraging questions
- **Neutral**: Balanced, natural conversation

### Personality & Humor

- **Light Humor (Always)**: Puns, wit, gentle self-deprecation to keep conversation engaging
- **Dark Humor (Context-Dependent)**: Sarcasm and cynical observations when user is frustrated or angry
- **Empathy-First on Crisis**: Disables humor if you mention harm or serious distress

### Real-Time Response

YaarBot listens continuously and responds in <50ms for emotion detection, preserving the natural feel of real-time conversation.

## Configuration

Edit `assistant.py` or `VoiceConfig` dataclass to customize:

- `wake_word`: Custom wake phrase (default: "hey yaarbot")
- `wake_word_enabled`: Toggle wake-word mode
- `whisper_model`: STT model size ("base", "small", "medium")
- `ollama_model`: LLM to use (default: "llama3.1:8b")
- `ollama_url`: Ollama server URL
- `tts_rate`: Speech speed (185 default)

## Usage Notes

- **Wake Word Mode**: Say `hey yaarbot` before your query
- **Disable Wake Word**: Set `wake_word_enabled=False` in `VoiceConfig`
- **Stop Bot**: Press `Ctrl + C`
- **Change Model**: Edit `ollama_model` in `VoiceConfig`
- **Test Emotions**: Run `python test_emotions.py` to test emotion detection

## Project Structure

```
YaarBot/
├── assistant.py              # Main voice assistant with emotion integration
├── emotion_detector.py        # Emotion detection using VADER sentiment analysis
├── personality_manager.py     # Dynamic personality & humor rules
├── test_emotions.py          # Emotion detection test suite
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Dependencies

- **sounddevice**: Audio input/output
- **openai-whisper**: Speech-to-text
- **pyttsx3**: Text-to-speech
- **ollama**: Local LLM integration
- **nltk/vader**: Emotion & sentiment analysis (NEW)
- **textblob**: NLP utilities (NEW)

## Architecture

YaarBot's emotional intelligence pipeline:

```
User Speech
    ↓
Whisper (STT) → "I'm feeling down"
    ↓
Emotion Detection (VADER) → Emotion: Sadness
    ↓
Personality Manager → "Be empathetic, supportive"
    ↓
System Prompt Update → "You are YaarBot... The user seems down..."
    ↓
Ollama LLM → Generates empathetic response
    ↓
pyttsx3 (TTS) → Speaks response with care
```

## Performance

- Emotion detection: <50ms
- System prompt generation: <5ms
- Ollama response: ~2-5 seconds
- TTS playback: <2 seconds
- Total latency: <100ms overhead from emotion features

## Future Enhancements

- Multi-turn emotion trend detection
- Context-aware humor density
- User personality learning (remember what humor works for you)
- Hinglish-specific emotion lexicon
- Advanced transformer models for higher accuracy

## Notes

- YaarBot is a companion for conversation and entertainment
- All processing is local—no data sent to cloud services
- Dark humor is used thoughtfully and contextually, not to mock
- For serious mental health concerns, please consult a professional

Press `Ctrl + C` to stop.

