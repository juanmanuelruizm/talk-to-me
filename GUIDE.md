# Quick Start Guide — talk-to-me

This guide takes you from zero to chatting with your language tutor in about
**5 minutes**, even if you have never used Ollama or Python. Follow the steps in order.

---

## ✅ Before you start you need

1. **Python 3.10 or newer** → check with: `python --version`
2. **Ollama** (the tutor's "engine") → we install it in Step 2
3. **A microphone** (optional: you can also type instead of speaking)

---

## Step 1 — Download the project

```bash
git clone https://github.com/juanmanuelruizm/talk-to-me.git
cd talk-to-me
```

---

## Step 2 — Install Ollama and the model

Ollama runs the "brain" (the LLM) on your own computer, with no internet needed.

1. Download and install it from **[ollama.com](https://ollama.com)**.
2. Pull the model (only the first time; it is a few GB):

```bash
ollama pull llama3.1
```

3. Check that it is ready:

```bash
ollama list      # "llama3.1" should appear
```

> 💡 Ollama usually keeps running in the background after installation. If the
> app says it cannot connect, open another terminal and run `ollama serve`.

---

## Step 3 — Install the Python dependencies

Create a "virtual environment" (an isolated box for the project's libraries):

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

Install what is needed:

```bash
pip install -r requirements.txt
```

> ⏳ The first time you press ENTER to speak, the Whisper model (speech
> recognition) is downloaded automatically before recording starts. It is normal for
> that to take a little while.

---

## Step 4 — Start the app

```bash
python run.py
```

If all goes well you will see:

```
============================================================
  English Practice — Conversational AI Tutor
============================================================

Checking Ollama connection (llama3.1)...
Ollama connected

Level: intermediate  |  Language: English  |  Model: llama3.1  |  TTS: off
Press ENTER to start speaking, or type a message or a command.
```

---

## Step 5 — Practice!

| I want to... | I do... |
|---|---|
| **Speak into the microphone** | Press `ENTER`, talk, and stay silent for ~1.5 s (or press `ENTER` again to stop) |
| **Type instead of speaking** | Type `/text` and press Enter |
| **Change the level** | `/level beginner`, `/level intermediate`, or `/level advanced` |
| **Practice another language** | `/language es` (also `fr`, `de`, `it`, `pt`, `en`) |
| **See what we have said so far** | `/history` |
| **Have the tutor talk to me** | `/tts` (works out of the box on macOS; on Linux/Windows: `pip install pyttsx3`) |
| **Save the conversation** | `/save` (saved in the `sessions/` folder; you are also asked when quitting) |
| **Start over** | `/reset` |
| **See the help** | `/help` |
| **Quit** | `/quit` |

> ℹ️ You can also type a sentence directly (without `/text`) and it is sent as a message.

### How a round works

1. You speak (or type) in the target language.
2. The app transcribes your voice and shows: `You said: "..."`.
3. The tutor replies **in real time**, correcting you and keeping the chat going:

```
You said: "I have went to the store yesterday"

Tutor: That sounds productive! What did you buy?

Correction: "I have went" -> "I went" (simple past with "yesterday").
```

> ⌨️ `Ctrl+C` while recording or while the tutor is replying cancels only that turn;
> at the main prompt, it exits the app.

---

## ⚙️ Customize (optional)

Want another model, another voice, or more time before it cuts you off? No code
changes needed: copy the template and edit what you want.

```bash
cp .env.example .env
```

Open `.env` and uncomment what you need, for example:

```env
WHISPER_MODEL=small      # more accurate than "base" (but slower)
OLLAMA_MODEL=llama3.1
TARGET_LANGUAGE=en       # or es, fr, de, it, pt
TTS_ENABLED=true         # the tutor replies with voice
SILENCE_DURATION=2.0     # gives you more silence before it stops recording
```

You can also pass options at startup: `python run.py --level beginner --language fr`.

---

## 🆘 Troubleshooting

**"Could not connect to Ollama..."**
→ Ollama is not running. Open a terminal and run `ollama serve`.

**"model 'llama3.1' is not available in Ollama"**
→ It has not been pulled yet: `ollama pull llama3.1`. The app lists the models you do
have; you can use one of them with `--model <name>` or `OLLAMA_MODEL=<name>` in `.env`.

**"(no speech detected)"**
→ No voice was detected in the first ~6 s. Check your microphone or lower
`SILENCE_THRESHOLD` (e.g. `0.005`) in your `.env`. You can allow more time with
`NO_SPEECH_TIMEOUT=10`.

**"Audio error" or the microphone is not detected**
→ Check that your microphone works and has permissions. In the meantime, use `/text`
to type. On Windows, if it fails, install [PortAudio](http://www.portaudio.com/).

**It cuts me off before I finish speaking**
→ Raise `SILENCE_DURATION` (e.g. `2.0`) in your `.env`. If there is background noise,
also raise `SILENCE_THRESHOLD` (e.g. `0.02`).

**The transcription is poor**
→ Use a bigger Whisper model: `WHISPER_MODEL=small` or `medium` in `.env`.

**It is slow**
→ Use a smaller Whisper model (`tiny`/`base`) and/or a lighter Ollama model. With a
GPU, set `WHISPER_COMPUTE_TYPE=float16`.

**The tutor does not speak with `/tts`**
→ On macOS it should work without installing anything (it uses `say`). On Linux/Windows
install the library: `pip install pyttsx3`; on Linux you may also need a system voice
engine (e.g. `espeak`).

**The tutor stops correcting in long conversations**
→ This should no longer happen: only the last 20 turns are sent to the model
(`MAX_HISTORY_TURNS`). If you want it to remember more, raise `OLLAMA_NUM_CTX=8192`
in your `.env`.

---

Ready? Run `python run.py` and start talking. 🚀
