"""Optional text-to-speech so the tutor can also reply with voice.

Backends:
  - `say`: the native macOS command. No dependencies and reliable.
  - `pyttsx3`: cross-platform and offline (uses the system voice engine).
    Requires `pip install pyttsx3` (or `pip install -e .[tts]`).

With TTS_BACKEND=auto, `say` is used on macOS and `pyttsx3` elsewhere.
Everything is optional: if no backend is available, the functions do nothing.
"""

import platform
import re
import shutil
import subprocess

from talk_to_me import config
from talk_to_me.prompts import CORRECTION_MARKER


class _SayBackend:
    name = "say"

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None

    @staticmethod
    def available() -> bool:
        return platform.system() == "Darwin" and shutil.which("say") is not None

    def speak(self, text: str) -> None:
        self._proc = subprocess.Popen(["say", "-r", str(config.TTS_RATE), text])
        try:
            self._proc.wait()
        finally:
            self._proc = None

    def stop(self) -> None:
        if self._proc is not None:
            self._proc.kill()


class _Pyttsx3Backend:
    name = "pyttsx3"

    def __init__(self) -> None:
        import pyttsx3  # lazy import: only if TTS is used

        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", config.TTS_RATE)

    def speak(self, text: str) -> None:
        self._engine.say(text)
        self._engine.runAndWait()

    def stop(self) -> None:
        self._engine.stop()


_backend = None
_resolved = False


def _get_backend():
    global _backend, _resolved
    if _resolved:
        return _backend
    _resolved = True
    choice = config.TTS_BACKEND
    try:
        if choice in ("auto", "say") and _SayBackend.available():
            _backend = _SayBackend()
        elif choice in ("auto", "pyttsx3"):
            _backend = _Pyttsx3Backend()
    except Exception:
        # pyttsx3 not installed or no voice engine on the system
        _backend = None
    return _backend


def is_available() -> bool:
    """True if a usable voice backend exists."""
    return _get_backend() is not None


def backend_name() -> str:
    backend = _get_backend()
    return backend.name if backend else "none"


_INLINE_CORRECTION = re.compile(rf"\(\s*{CORRECTION_MARKER}[^)]*\)")
_TRAILING_CORRECTION = re.compile(rf"(?:^|\n)\s*\(?{CORRECTION_MARKER}")
_MARKDOWN = re.compile(r"[*_`#>]+")


def clean_for_speech(text: str) -> str:
    """Keeps only the conversational part: strips corrections, markdown, and arrows."""
    cleaned = _INLINE_CORRECTION.sub("", text)
    cleaned = _TRAILING_CORRECTION.split(cleaned, maxsplit=1)[0]
    cleaned = cleaned.replace("→", " to ").replace("->", " to ")
    cleaned = _MARKDOWN.sub("", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned).strip()
    return cleaned or text.strip()


def speak(text: str) -> None:
    """Reads the text aloud (blocking). No-op if TTS is not available."""
    backend = _get_backend()
    if backend is None or not text.strip():
        return
    try:
        backend.speak(clean_for_speech(text))
    except KeyboardInterrupt:
        backend.stop()
        raise
    except Exception:
        # If something fails mid-use, do not break the conversation.
        pass


def stop() -> None:
    backend = _get_backend()
    if backend is not None:
        try:
            backend.stop()
        except Exception:
            pass


if __name__ == "__main__":
    if is_available():
        print(f"TTS available (backend: {backend_name()}). Testing voice...")
        speak("Hello! This is your tutor speaking. (Correction: this part is not read.) Bye!")
    else:
        print("TTS not available. Install pyttsx3: pip install pyttsx3")
