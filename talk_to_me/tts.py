"""Text-to-Speech opcional para que el tutor responda también con voz.

Backends:
  - `say`: el comando nativo de macOS. Sin dependencias y fiable.
  - `pyttsx3`: multiplataforma y offline (usa el motor de voz del sistema).
    Requiere `pip install pyttsx3` (o `pip install -e .[tts]`).

Con TTS_BACKEND=auto se usa `say` en macOS y `pyttsx3` en el resto.
Todo es opcional: si no hay backend disponible, las funciones no fallan.
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
        import pyttsx3  # import perezoso: solo si se usa TTS

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
        # pyttsx3 no instalado o sin motor de voz en el sistema
        _backend = None
    return _backend


def is_available() -> bool:
    """True si hay algún backend de voz utilizable."""
    return _get_backend() is not None


def backend_name() -> str:
    backend = _get_backend()
    return backend.name if backend else "none"


_INLINE_CORRECTION = re.compile(rf"\(\s*{CORRECTION_MARKER}[^)]*\)")
_TRAILING_CORRECTION = re.compile(rf"(?:^|\n)\s*\(?{CORRECTION_MARKER}")
_MARKDOWN = re.compile(r"[*_`#>]+")


def clean_for_speech(text: str) -> str:
    """Deja solo la parte conversacional: quita correcciones, markdown y flechas."""
    cleaned = _INLINE_CORRECTION.sub("", text)
    cleaned = _TRAILING_CORRECTION.split(cleaned, maxsplit=1)[0]
    cleaned = cleaned.replace("→", " to ").replace("->", " to ")
    cleaned = _MARKDOWN.sub("", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned).strip()
    return cleaned or text.strip()


def speak(text: str) -> None:
    """Lee el texto en voz alta (bloqueante). No-op si TTS no está disponible."""
    backend = _get_backend()
    if backend is None or not text.strip():
        return
    try:
        backend.speak(clean_for_speech(text))
    except KeyboardInterrupt:
        backend.stop()
        raise
    except Exception:
        # Si algo falla en pleno uso, no rompemos la conversación.
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
        print(f"TTS disponible (backend: {backend_name()}). Probando voz...")
        speak("Hello! This is your tutor speaking. (Correction: this part is not read.) Bye!")
    else:
        print("TTS no disponible. Instala pyttsx3: pip install pyttsx3")
