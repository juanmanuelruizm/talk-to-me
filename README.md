# talk-to-me — AI Language Tutor (CLI)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-black?style=flat)
![CI](https://github.com/juanmanuelruizm/talk-to-me/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

Practice a language by having real conversations with an AI tutor, powered by voice recognition and a local LLM.

You speak into your microphone, the app transcribes your voice, and a local LLM acts as your tutor: it keeps the conversation going, corrects your mistakes, and helps you improve. Built for practicing English, but it also works with Spanish, French, German, Italian, and Portuguese.

> First time here? Follow the **[step-by-step Quick Start Guide (GUIDE.md)](GUIDE.md)** — designed to get you talking in 5 minutes, even if you have never used Ollama.

### Features

- 🎙️ **Speak or type** — practice with your voice, or type if you have no microphone
- 🧠 **100% local and private** — everything runs on your machine (Ollama + Whisper); your voice never leaves it
- ⚡ **Streaming replies** — the tutor answers in real time, word by word
- 📊 **3 levels** — beginner, intermediate, and advanced, switchable on the fly
- 🌍 **Multi-language** — English, Spanish, French, German, Italian, or Portuguese (`/language`)
- 🔊 **Optional voice (TTS)** — the tutor can also talk back (`say` on macOS, `pyttsx3` elsewhere)
- 💾 **Save your sessions** — export the conversation to Markdown (`/save`, or when you quit)
- 🛠️ **Configurable without touching code** — environment variables or a `.env` file
- ✅ **Tests and CI** — a `pytest` suite that needs no microphone or network, plus `ruff` linting

## How it works

```
Microphone → faster-whisper (STT) → Prompt + history → Ollama (LLM) → Reply in the terminal (+ voice)
     ↑                                                                          |
     └──────────────────── You read/listen to the reply and speak again ←───────┘
```

1. **You speak** into the microphone (or type a message)
2. **faster-whisper** transcribes your audio to text
3. The text is sent to **Ollama** together with the recent history and a tutor system prompt
4. The LLM replies as a tutor: it answers you, corrects mistakes in a final `Correction:` line, and keeps the conversation going
5. Repeat — the conversation keeps its context

## Prerequisites

- **Python 3.10+**
- **Ollama** installed and running ([ollama.com](https://ollama.com))
- **A working microphone** (for voice mode)
- **Windows**: PortAudio (usually installed automatically with `sounddevice`; if you hit problems, install [PortAudio](http://www.portaudio.com/) manually)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/juanmanuelruizm/talk-to-me.git
cd talk-to-me
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Alternatively, install the package (this gives you the `talk-to-me` command):

```bash
pip install -e .            # runtime only
pip install -e ".[tts]"     # + tutor voice via pyttsx3 (not needed on macOS)
pip install -e ".[dev]"     # + pytest and ruff
```

### 3. Install Ollama and pull the model

```bash
# Install Ollama from https://ollama.com

# Pull the model (once)
ollama pull llama3.1
```

### 4. Make sure Ollama is running

```bash
ollama serve   # if it is not already running as a service
ollama list    # check that llama3.1 shows up
```

## Usage

From the project root, any of these three is equivalent:

```bash
python run.py
python -m talk_to_me
talk-to-me                  # if you ran pip install -e .
```

Command-line options (all optional; they can also be set in `.env`):

```bash
talk-to-me --level beginner --language es --model qwen2.5:7b
talk-to-me --help
```

### App flow

1. The app checks the connection to Ollama (if the model is missing, it lists the ones you do have)
2. It shows the prompt and waits for input
3. **Press ENTER** to speak — talk, then stay silent so it detects the end, or **press ENTER again** to stop early
4. The transcription is shown on screen
5. The tutor replies with corrections and continues the conversation

### Available commands

| Command | Description |
|---|---|
| `ENTER` | Record from the microphone (ENTER again to stop) |
| `/text [message]` | Type a message manually |
| `/level <level>` | Change level: `beginner`, `intermediate`, `advanced` |
| `/language <code>` | Change language: `en`, `es`, `fr`, `de`, `it`, `pt` |
| `/history` | Show the conversation so far |
| `/save` | Save the conversation to `sessions/` as Markdown |
| `/tts` | Toggle the tutor's voice |
| `/reset` | Reset the conversation (clear history) |
| `/help` | Show help |
| `/quit`, `/exit` | Exit (if there are unsaved turns, it asks whether to save them) |

You can also type text directly without `/text` — any input that is not a command is treated as a message. `Ctrl+C` during a recording or a reply cancels only that turn.

### Example session

```
============================================================
  English Practice — Conversational AI Tutor
============================================================

Checking Ollama connection (llama3.1)...
Ollama connected

Level: intermediate  |  Language: English  |  Model: llama3.1  |  TTS: off
Press ENTER to start speaking, or type a message or a command.
Type /help for available commands.

[ENTER to speak | /text to type | /help] >
Listening... (speak, stay silent to finish, or press ENTER to stop)
Recorded 3.2s of audio
Transcribing...

You said: "I have went to the store yesterday"

Tutor: That sounds like a productive day! What did you buy at the store?

Correction: "I have went" -> "I went" (use simple past for completed
actions with a specific time like "yesterday", not present perfect).
```

## Configuration

No code changes needed. You can configure everything with **environment variables** or, more conveniently, by copying [`.env.example`](.env.example) to `.env` and editing it:

```bash
cp .env.example .env
# edit .env with your favorite editor
```

| Setting | Default | Description |
|---|---|---|
| `DEFAULT_LEVEL` | `intermediate` | Default tutor level |
| `TARGET_LANGUAGE` | `en` | Language you practice: `en`, `es`, `fr`, `de`, `it`, `pt` |
| `MAX_HISTORY_TURNS` | `20` | Question/answer pairs sent to the LLM (0 = full history) |
| `AUTO_SAVE_ON_EXIT` | `false` | Save automatically on exit (otherwise it asks) |
| `WHISPER_MODEL` | `base` | Whisper model: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_COMPUTE_TYPE` | `int8` | `int8` for CPU, `float16` for GPU |
| `WHISPER_DEVICE` | `auto` | `auto`, `cpu`, `cuda` |
| `WHISPER_LANGUAGE` | *(empty)* | Force the transcription language; empty = follows `TARGET_LANGUAGE` |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1` | Ollama model to use |
| `OLLAMA_TIMEOUT` | `120` | Timeout (s) for the LLM reply |
| `OLLAMA_NUM_CTX` | `0` | Context size in tokens (0 = Ollama default) |
| `OLLAMA_TEMPERATURE` | `0.3` | Model creativity; low = more consistent at following the correction format (`-1` = Ollama default) |
| `SILENCE_THRESHOLD` | `0.01` | RMS threshold for detecting silence |
| `SILENCE_DURATION` | `1.5` | Seconds of silence to stop recording |
| `NO_SPEECH_TIMEOUT` | `6` | Seconds without speech before cancelling the recording |
| `MAX_RECORD_SECONDS` | `30` | Maximum seconds per recording |
| `TTS_ENABLED` | `false` | Have the tutor reply with voice as well |
| `TTS_BACKEND` | `auto` | `auto` (`say` on macOS, `pyttsx3` elsewhere), `say`, `pyttsx3` |
| `TTS_RATE` | `170` | Voice speed (words per minute) |

The defaults live in [`talk_to_me/config.py`](talk_to_me/config.py); any environment variable or `.env` entry overrides them.

**Whisper models**: `tiny` and `base` are faster but less accurate; `large-v3` is the most accurate but needs more RAM and a GPU to feel smooth.

**History**: Ollama truncates the context from the top when it fills up, which in long sessions used to drop the system prompt (and the tutor stopped correcting). That is why only the last `MAX_HISTORY_TURNS` pairs are sent; the full history is kept for `/history` and `/save`. If you want more memory, raise `OLLAMA_NUM_CTX` (e.g. `8192`).

### Tutor voice (optional TTS)

- **macOS**: nothing to install, the system `say` command is used.
- **Linux / Windows**: install `pyttsx3` (`pip install pyttsx3` or `pip install -e ".[tts]"`). On Linux you may also need a system voice engine such as `espeak`.

Enable it with `TTS_ENABLED=true` in your `.env`, or at any time inside the app with `/tts`. The `Correction:` line is not read aloud, only the conversational part.

## Development

```bash
pip install -e ".[dev]"
pytest              # unit tests (no microphone, Ollama, or model download needed)
ruff check .        # lint
ruff format .       # format
```

Each module can be tried on its own: `python -m talk_to_me.audio`, `python -m talk_to_me.stt`, `python -m talk_to_me.llm`, `python -m talk_to_me.tts`.

## Project structure

```
talk-to-me/
├── talk_to_me/
│   ├── cli.py        # Main CLI loop: commands, voice/text turns, exit
│   ├── audio.py      # Microphone capture + silence detection (SilenceDetector)
│   ├── stt.py        # Transcription with faster-whisper
│   ├── llm.py        # Ollama API client (streaming, errors, model check)
│   ├── tts.py        # Optional text-to-speech (say / pyttsx3)
│   ├── prompts.py    # Tutor system prompt (per level and language)
│   ├── session.py    # Conversation history, trimming, and Markdown export
│   ├── config.py     # Configuration (environment variables / .env)
│   └── __main__.py   # python -m talk_to_me
├── tests/            # pytest
├── sessions/         # Saved conversations (ignored by git)
├── run.py            # Launcher from the root (python run.py)
├── pyproject.toml    # Package, [tts] [dev] extras, ruff/pytest config
├── requirements.txt
├── .env.example      # Configuration template
├── GUIDE.md          # Step-by-step quick start guide
├── LICENSE
└── README.md
```

## Roadmap

- [x] **Text-to-Speech (TTS)** — Let the tutor reply with voice too
- [x] **Streaming replies** — Show the LLM reply token by token in real time
- [x] **Session persistence** — Save conversation history (`/save`)
- [x] **Multi-language support** — Spanish, French, German, Italian, Portuguese (`/language`)
- [ ] **Web UI** — FastAPI backend + browser frontend with in-browser audio recording
- [ ] **Progress metrics** — Track common mistakes, vocabulary learned, etc.

## License

This project is under the MIT license. Use it, modify it, and share it freely.

## Author

**Juan Manuel Ruiz Muñoz**

- LinkedIn: [Juan Manuel Ruiz Muñoz](https://www.linkedin.com/in/juan-manuel-ruiz-mu%C3%B1oz/)
- GitHub: [@juanmanuelruizm](https://github.com/juanmanuelruizm)
