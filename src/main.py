import sys

from audio import record_until_silence
from stt import transcribe
from llm import chat, check_connection
from prompts import get_system_prompt
from config import DEFAULT_LEVEL, OLLAMA_MODEL


HELP_TEXT = """
Available commands:
  /quit, /exit    — Exit the app
  /reset          — Reset conversation history
  /level <level>  — Change level (beginner, intermediate, advanced)
  /text           — Type your message instead of speaking
  /help           — Show this help
"""


def main():
    print("=" * 60)
    print("  🗣️  English Practice — Conversational AI Tutor")
    print("=" * 60)

    # Check Ollama connection
    print(f"\n⏳  Checking Ollama connection ({OLLAMA_MODEL})...")
    if not check_connection():
        print(f"\n❌  Could not connect to Ollama or model '{OLLAMA_MODEL}' not found.")
        print("    Make sure Ollama is running: ollama serve")
        print(f"    And the model is pulled: ollama pull {OLLAMA_MODEL}")
        sys.exit(1)
    print("✅  Ollama connected\n")

    level = DEFAULT_LEVEL
    messages: list[dict] = [
        {"role": "system", "content": get_system_prompt(level)}
    ]

    print(f"Level: {level}")
    print("Press ENTER to start speaking, or type a command.")
    print("Type /help for available commands.\n")

    while True:
        try:
            user_input = input("\n[ENTER to speak | /text to type | /help] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nBye! Keep practicing! 👋")
            break

        # --- Commands ---
        if user_input.lower() in ("/quit", "/exit"):
            print("\nBye! Keep practicing! 👋")
            break

        if user_input.lower() == "/help":
            print(HELP_TEXT)
            continue

        if user_input.lower() == "/reset":
            messages = [{"role": "system", "content": get_system_prompt(level)}]
            print("🔄  Conversation reset.")
            continue

        if user_input.lower().startswith("/level"):
            parts = user_input.split()
            if len(parts) >= 2 and parts[1] in ("beginner", "intermediate", "advanced"):
                level = parts[1]
                messages = [{"role": "system", "content": get_system_prompt(level)}]
                print(f"🔄  Level changed to '{level}'. Conversation reset.")
            else:
                print("Usage: /level <beginner|intermediate|advanced>")
            continue

        # --- Get user message ---
        if user_input.lower() == "/text":
            user_text = input("📝  Type your message: ").strip()
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
                print("⏳  Transcribing...")
                user_text = transcribe(audio)
                if not user_text:
                    print("(could not understand audio, try again)")
                    continue
                print(f"\n🗣️  You said: \"{user_text}\"")
            except Exception as e:
                print(f"❌  Audio error: {e}")
                print("    Try /text to type your message instead.")
                continue
        else:
            # Treat raw text as direct input (convenience)
            user_text = user_input

        # --- Send to LLM ---
        messages.append({"role": "user", "content": user_text})

        print("⏳  Thinking...")
        try:
            response = chat(messages)
        except Exception as e:
            print(f"❌  LLM error: {e}")
            messages.pop()  # Remove failed user message
            continue

        messages.append({"role": "assistant", "content": response})
        print(f"\n🤖  Tutor: {response}")


if __name__ == "__main__":
    main()
