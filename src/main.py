import sys
from datetime import datetime
from pathlib import Path

from audio import record_until_silence
from stt import transcribe
from llm import chat_stream, check_connection
from prompts import get_system_prompt
import tts
from config import DEFAULT_LEVEL, OLLAMA_MODEL, TTS_ENABLED


HELP_TEXT = """
Available commands:
  ENTER           — Record audio from the microphone and speak
  /text           — Type your message instead of speaking
  /level <level>  — Change level (beginner, intermediate, advanced)
  /save           — Save the conversation to a file
  /tts            — Toggle text-to-speech (tutor speaks the reply)
  /reset          — Reset conversation history
  /help           — Show this help
  /quit, /exit    — Exit the app
"""

LEVELS = ("beginner", "intermediate", "advanced")
SESSIONS_DIR = Path(__file__).resolve().parent.parent / "sessions"


def save_conversation(messages: list[dict]) -> Path | None:
    """Guarda la conversación (sin el system prompt) en sessions/ como Markdown."""
    turns = [m for m in messages if m["role"] != "system"]
    if not turns:
        print("(nothing to save yet)")
        return None

    SESSIONS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SESSIONS_DIR / f"session_{timestamp}.md"

    lines = [f"# English practice session — {timestamp}", ""]
    for m in turns:
        speaker = "You" if m["role"] == "user" else "Tutor"
        lines.append(f"**{speaker}:** {m['content']}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def get_tutor_reply(messages: list[dict]) -> str:
    """Pide la respuesta al LLM en streaming y la imprime token a token."""
    print("\nTutor: ", end="", flush=True)
    parts: list[str] = []
    for token in chat_stream(messages):
        print(token, end="", flush=True)
        parts.append(token)
    print()
    return "".join(parts).strip()


def main():
    print("=" * 60)
    print("  English Practice — Conversational AI Tutor")
    print("=" * 60)

    # Check Ollama connection
    print(f"\nChecking Ollama connection ({OLLAMA_MODEL})...")
    if not check_connection():
        print(f"\nError: Could not connect to Ollama or model '{OLLAMA_MODEL}' not found.")
        print("    Make sure Ollama is running: ollama serve")
        print(f"    And the model is pulled: ollama pull {OLLAMA_MODEL}")
        sys.exit(1)
    print("Ollama connected")

    tts_on = TTS_ENABLED and tts.is_available()
    if TTS_ENABLED and not tts.is_available():
        print("Note: TTS is enabled but pyttsx3 is not installed. Run: pip install pyttsx3")

    level = DEFAULT_LEVEL
    messages: list[dict] = [
        {"role": "system", "content": get_system_prompt(level)}
    ]

    print(f"\nLevel: {level}  |  TTS: {'on' if tts_on else 'off'}")
    print("Press ENTER to start speaking, or type a command.")
    print("Type /help for available commands.")

    while True:
        try:
            user_input = input("\n[ENTER to speak | /text to type | /help] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nBye! Keep practicing!")
            break

        # --- Commands ---
        if user_input.lower() in ("/quit", "/exit"):
            print("\nBye! Keep practicing!")
            break

        if user_input.lower() == "/help":
            print(HELP_TEXT)
            continue

        if user_input.lower() == "/reset":
            messages = [{"role": "system", "content": get_system_prompt(level)}]
            print("Conversation reset.")
            continue

        if user_input.lower() == "/save":
            path = save_conversation(messages)
            if path:
                print(f"Conversation saved to {path}")
            continue

        if user_input.lower() == "/tts":
            if not tts.is_available():
                print("TTS not available. Install it with: pip install pyttsx3")
            else:
                tts_on = not tts_on
                print(f"TTS {'enabled' if tts_on else 'disabled'}.")
            continue

        if user_input.lower().startswith("/level"):
            parts = user_input.split()
            if len(parts) >= 2 and parts[1] in LEVELS:
                level = parts[1]
                messages = [{"role": "system", "content": get_system_prompt(level)}]
                print(f"Level changed to '{level}'. Conversation reset.")
            else:
                print(f"Usage: /level <{'|'.join(LEVELS)}>")
            continue

        # --- Get user message ---
        if user_input.lower() == "/text":
            user_text = input("Type your message: ").strip()
            if not user_text:
                print("(empty message, skipping)")
                continue
        elif user_input == "":
            # Record audio
            try:
                audio = record_until_silence()
                if len(audio) == 0:
                    print("(no audio captured, try again)")
                    continue
                print("Transcribing...")
                user_text = transcribe(audio)
                if not user_text:
                    print("(could not understand audio, try again)")
                    continue
                print(f"\nYou said: \"{user_text}\"")
            except Exception as e:
                print(f"Audio error: {e}")
                print("    No microphone? Use /text to type your message instead.")
                continue
        elif user_input.startswith("/"):
            print(f"Unknown command: {user_input}. Type /help for available commands.")
            continue
        else:
            # Treat raw text as direct input (convenience)
            user_text = user_input

        # --- Send to LLM (streaming) ---
        messages.append({"role": "user", "content": user_text})

        try:
            response = get_tutor_reply(messages)
        except Exception as e:
            print(f"\nLLM error: {e}")
            messages.pop()  # Remove failed user message
            continue

        messages.append({"role": "assistant", "content": response})

        if tts_on:
            tts.speak(response)


if __name__ == "__main__":
    main()
