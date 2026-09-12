"""Main CLI loop: commands, voice/text turns, and clean exit."""

import argparse
import platform
import sys
from collections.abc import Callable

from talk_to_me import __version__, config, stt, tts
from talk_to_me.audio import record_until_silence
from talk_to_me.llm import LLMError, chat_stream, check_connection
from talk_to_me.prompts import LANGUAGES, LEVELS
from talk_to_me.session import SESSIONS_DIR, Conversation

HELP_TEXT = """
Available commands:
  ENTER            — Record from the microphone (press ENTER again to stop early)
  /text            — Type your message instead of speaking
  /level <level>   — Change level: beginner, intermediate, advanced
  /language <code> — Change target language: {languages}
  /history         — Show the conversation so far
  /save            — Save the conversation to a Markdown file
  /tts             — Toggle text-to-speech (tutor speaks the reply)
  /reset           — Reset conversation history
  /help            — Show this help
  /quit, /exit     — Exit the app

Anything else you type is sent to the tutor as a message.
""".format(languages=", ".join(LANGUAGES))

PROMPT = "\n[ENTER to speak | /text to type | /help] > "


def _enter_pressed() -> bool:
    """True if the user pressed ENTER since the last check (interactive terminals only)."""
    if not sys.stdin.isatty():
        return False
    if platform.system() == "Windows":
        import msvcrt

        pressed = False
        while msvcrt.kbhit():
            if msvcrt.getwch() in ("\r", "\n"):
                pressed = True
        return pressed
    import select

    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if ready:
        sys.stdin.readline()  # consume the line so it does not reach the next input()
        return True
    return False


class App:
    """State and commands of an interactive session."""

    def __init__(
        self,
        level: str = config.LEVEL,
        language: str = config.TARGET_LANGUAGE,
        model: str = config.OLLAMA_MODEL,
        tts_on: bool = False,
        input_fn: Callable[[str], str] = input,
    ) -> None:
        self.conversation = Conversation(level, language, model)
        self.model = model
        self.tts_on = tts_on
        self._input = input_fn
        self.running = True
        self.commands: dict[str, Callable[[list[str]], None]] = {
            "/help": self.cmd_help,
            "/quit": self.cmd_quit,
            "/exit": self.cmd_quit,
            "/reset": self.cmd_reset,
            "/save": self.cmd_save,
            "/tts": self.cmd_tts,
            "/level": self.cmd_level,
            "/language": self.cmd_language,
            "/history": self.cmd_history,
            "/text": self.cmd_text,
        }

    @property
    def level(self) -> str:
        return self.conversation.level

    @property
    def language(self) -> str:
        return self.conversation.language

    # --- Dispatch ---
    def handle_input(self, user_input: str) -> None:
        text = user_input.strip()
        if text == "":
            self.voice_turn()
        elif text.startswith("/"):
            name, *args = text.split()
            handler = self.commands.get(name.lower())
            if handler is None:
                print(f"Unknown command: {name}. Type /help for available commands.")
            else:
                handler(args)
        else:
            self.chat_turn(text)

    # --- Commands ---
    def cmd_help(self, args: list[str]) -> None:
        print(HELP_TEXT)

    def cmd_quit(self, args: list[str]) -> None:
        self.running = False

    def cmd_reset(self, args: list[str]) -> None:
        self.conversation.reset()
        print("Conversation reset.")

    def cmd_save(self, args: list[str]) -> None:
        if self.conversation.is_empty:
            print("(nothing to save yet)")
            return
        path = self.conversation.save(SESSIONS_DIR)
        print(f"Conversation saved to {path}")

    def cmd_tts(self, args: list[str]) -> None:
        if not tts.is_available():
            print("TTS not available. Install it with: pip install pyttsx3")
            return
        self.tts_on = not self.tts_on
        print(f"TTS {'enabled' if self.tts_on else 'disabled'} (backend: {tts.backend_name()}).")

    def cmd_level(self, args: list[str]) -> None:
        if args and args[0].lower() in LEVELS:
            self.conversation.level = args[0].lower()
            self.conversation.reset()
            print(f"Level changed to '{self.level}'. Conversation reset.")
        else:
            print(f"Usage: /level <{'|'.join(LEVELS)}>")

    def cmd_language(self, args: list[str]) -> None:
        if args and args[0].lower() in LANGUAGES:
            self.conversation.language = args[0].lower()
            self.conversation.reset()
            name = self.conversation.language_name
            print(f"Language changed to {name} ({self.language}). Conversation reset.")
        else:
            print(f"Usage: /language <{'|'.join(LANGUAGES)}>")

    def cmd_history(self, args: list[str]) -> None:
        if self.conversation.is_empty:
            print("(no messages yet)")
            return
        print()
        for m in self.conversation.turns:
            speaker = "You" if m["role"] == "user" else "Tutor"
            print(f"{speaker}: {m['content']}\n")

    def cmd_text(self, args: list[str]) -> None:
        text = " ".join(args).strip() or self._input("Type your message: ").strip()
        if not text:
            print("(empty message, skipping)")
            return
        self.chat_turn(text)

    # --- Turns ---
    def voice_turn(self) -> None:
        try:
            stt.ensure_loaded()  # before recording, so the user does not wait afterwards
            print("Listening... (speak, stay silent to finish, or press ENTER to stop)")
            audio = record_until_silence(stop_requested=_enter_pressed)
            if len(audio) == 0:
                print("(no speech detected, try again or use /text)")
                return
            print("Transcribing...")
            text = stt.transcribe(audio, language=config.WHISPER_LANGUAGE or self.language)
        except KeyboardInterrupt:
            print("\n(cancelled)")
            return
        except Exception as e:
            print(f"Audio error: {e}")
            print("    No microphone? Use /text to type your message instead.")
            return
        if not text:
            print("(could not understand audio, try again)")
            return
        print(f'\nYou said: "{text}"')
        self.chat_turn(text)

    def chat_turn(self, text: str) -> None:
        conv = self.conversation
        conv.add_user(text)
        print("\nTutor: ", end="", flush=True)
        parts: list[str] = []
        try:
            for token in chat_stream(conv.for_llm(config.MAX_HISTORY_TURNS), model=self.model):
                print(token, end="", flush=True)
                parts.append(token)
        except KeyboardInterrupt:
            print("\n(cancelled)")
            conv.drop_last_user()
            return
        except LLMError as e:
            print(f"\nLLM error: {e}")
            conv.drop_last_user()
            return
        print()

        reply = "".join(parts).strip()
        if not reply:
            print("(the model returned an empty reply, try again)")
            conv.drop_last_user()
            return
        conv.add_assistant(reply)

        if self.tts_on:
            try:
                tts.speak(reply)
            except KeyboardInterrupt:
                print("(speech stopped)")

    # --- Lifecycle ---
    def maybe_save_on_exit(self) -> None:
        if not self.conversation.unsaved:
            return
        if config.AUTO_SAVE_ON_EXIT:
            print(f"Conversation saved to {self.conversation.save(SESSIONS_DIR)}")
            return
        try:
            answer = self._input("Save the conversation before leaving? [y/N] ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            return
        if answer in ("y", "yes"):
            print(f"Conversation saved to {self.conversation.save(SESSIONS_DIR)}")

    def run(self) -> None:
        print(
            f"\nLevel: {self.level}  |  Language: {self.conversation.language_name}"
            f"  |  Model: {self.model}  |  TTS: {'on' if self.tts_on else 'off'}"
        )
        print("Press ENTER to start speaking, or type a message or a command.")
        print("Type /help for available commands.")
        while self.running:
            try:
                user_input = self._input(PROMPT)
            except (KeyboardInterrupt, EOFError):
                print()
                break
            self.handle_input(user_input)
        self.maybe_save_on_exit()
        print("\nBye! Keep practicing!")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="talk-to-me",
        description="Practice a language by talking to a local AI tutor (Whisper + Ollama).",
    )
    parser.add_argument("--level", choices=LEVELS, default=config.LEVEL, help="tutor level")
    parser.add_argument(
        "--language",
        choices=list(LANGUAGES),
        default=config.TARGET_LANGUAGE,
        help="target language code",
    )
    parser.add_argument("--model", default=config.OLLAMA_MODEL, help="Ollama model name")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    language_name = LANGUAGES[args.language]

    print("=" * 60)
    print(f"  {language_name} Practice — Conversational AI Tutor")
    print("=" * 60)

    print(f"\nChecking Ollama connection ({args.model})...")
    status = check_connection(args.model)
    if not status.reachable:
        print(f"\nError: Could not connect to Ollama at {config.OLLAMA_URL}.")
        print("    Make sure Ollama is running: ollama serve")
        if status.error:
            print(f"    Details: {status.error}")
        sys.exit(1)
    if not status.model_found:
        print(f"\nError: model '{args.model}' is not available in Ollama.")
        print(f"    Pull it with: ollama pull {args.model}")
        if status.available:
            print(f"    Models already available: {', '.join(status.available)}")
            print("    Use one of them with --model <name> or OLLAMA_MODEL=<name>")
        sys.exit(1)
    print("Ollama connected")

    tts_on = config.TTS_ENABLED and tts.is_available()
    if config.TTS_ENABLED and not tts_on:
        print("Note: TTS is enabled but no voice backend is available. Run: pip install pyttsx3")

    App(level=args.level, language=args.language, model=args.model, tts_on=tts_on).run()


if __name__ == "__main__":
    main()
