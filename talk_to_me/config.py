"""Central app configuration.

Every value has a sensible default and can be overridden with environment
variables or a `.env` file (looked up first in the current directory, then in
the project root), without touching this file.

Example `.env`:
    WHISPER_MODEL=small
    OLLAMA_MODEL=llama3.1
    TTS_ENABLED=true
"""

import os
import sys
from collections.abc import Iterable
from pathlib import Path

from talk_to_me.prompts import DEFAULT_LANGUAGE, DEFAULT_LEVEL, LANGUAGES, LEVELS

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# --- Optional .env loading (no external dependencies) ---
def parse_env_file(text: str) -> dict[str, str]:
    """Parses .env content into a dict (ignores comments and blank lines)."""
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if value[:1] in ("'", '"') and len(value) >= 2 and value[-1] == value[0]:
            value = value[1:-1]
        else:
            # Allow trailing comments: KEY=value  # comment
            value = value.split("#", 1)[0].strip()
        values[key] = value
    return values


def load_dotenv(candidates: Iterable[Path] | None = None) -> Path | None:
    """Loads the first existing .env without overriding variables already set.

    Returns the loaded path, or None if there was none.
    """
    if candidates is None:
        candidates = (Path.cwd() / ".env", PROJECT_ROOT / ".env")
    for env_path in candidates:
        if env_path.is_file():
            for key, value in parse_env_file(env_path.read_text(encoding="utf-8")).items():
                os.environ.setdefault(key, value)
            return env_path
    return None


load_dotenv()


# --- Typed readers ---
def _get_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _get_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on", "y")


def _get_choice(name: str, default: str, choices: Iterable[str]) -> str:
    """Reads a variable that must be one of `choices`; otherwise warns and uses the default."""
    value = os.environ.get(name, default).strip().lower()
    if value in choices:
        return value
    print(
        f"Warning: {name}={value!r} is not valid (choices: {', '.join(choices)}). "
        f"Using {default!r}.",
        file=sys.stderr,
    )
    return default


# --- App ---
LEVEL = _get_choice("DEFAULT_LEVEL", DEFAULT_LEVEL, LEVELS)
TARGET_LANGUAGE = _get_choice("TARGET_LANGUAGE", DEFAULT_LANGUAGE, LANGUAGES)
# User/tutor pairs sent to the LLM on each request (0 = full history)
MAX_HISTORY_TURNS = _get_int("MAX_HISTORY_TURNS", 20)
AUTO_SAVE_ON_EXIT = _get_bool("AUTO_SAVE_ON_EXIT", False)

# --- Whisper (STT) ---
WHISPER_MODEL = _get_str("WHISPER_MODEL", "base")  # tiny, base, small, medium, large-v3
WHISPER_COMPUTE_TYPE = _get_str("WHISPER_COMPUTE_TYPE", "int8")  # int8 (CPU), float16 (GPU)
WHISPER_DEVICE = _get_str("WHISPER_DEVICE", "auto")  # auto, cpu, cuda
WHISPER_LANGUAGE = _get_str("WHISPER_LANGUAGE", "")  # empty = follows TARGET_LANGUAGE

# --- Ollama (LLM) ---
OLLAMA_URL = _get_str("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = _get_str("OLLAMA_MODEL", "llama3.1")
OLLAMA_TIMEOUT = _get_int("OLLAMA_TIMEOUT", 120)
OLLAMA_NUM_CTX = _get_int("OLLAMA_NUM_CTX", 0)  # 0 = Ollama default
OLLAMA_TEMPERATURE = _get_float("OLLAMA_TEMPERATURE", 0.3)  # <0 = Ollama default

# --- Audio ---
SAMPLE_RATE = _get_int("SAMPLE_RATE", 16000)  # Hz — Whisper expects 16kHz
CHANNELS = _get_int("CHANNELS", 1)  # Mono
SILENCE_THRESHOLD = _get_float("SILENCE_THRESHOLD", 0.01)  # RMS silence threshold
SILENCE_DURATION = _get_float("SILENCE_DURATION", 1.5)  # Seconds of silence to stop
NO_SPEECH_TIMEOUT = _get_float("NO_SPEECH_TIMEOUT", 6.0)  # Seconds without speech before aborting
MAX_RECORD_SECONDS = _get_int("MAX_RECORD_SECONDS", 30)  # Maximum recording length

# --- Text-to-Speech (optional) ---
TTS_ENABLED = _get_bool("TTS_ENABLED", False)  # The tutor also replies with voice
TTS_BACKEND = _get_choice("TTS_BACKEND", "auto", ("auto", "say", "pyttsx3"))
TTS_RATE = _get_int("TTS_RATE", 170)  # Words per minute
