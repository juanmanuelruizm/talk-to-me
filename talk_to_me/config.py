"""Configuración central de la app.

Todos los valores tienen un default razonable y pueden sobreescribirse con
variables de entorno o con un archivo `.env` (se busca primero en el directorio
actual y después en la raíz del proyecto), sin tener que tocar este archivo.

Ejemplo de `.env`:
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


# --- Carga opcional de un archivo .env (sin dependencias externas) ---
def parse_env_file(text: str) -> dict[str, str]:
    """Convierte el contenido de un .env en un dict (ignora comentarios y líneas vacías)."""
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
            # Permite comentarios al final de la línea: KEY=value  # comentario
            value = value.split("#", 1)[0].strip()
        values[key] = value
    return values


def load_dotenv(candidates: Iterable[Path] | None = None) -> Path | None:
    """Carga el primer .env que exista, sin pisar variables ya definidas en el entorno.

    Devuelve la ruta cargada o None si no había ninguno.
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


# --- Helpers de lectura tipada ---
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
    """Lee una variable que debe estar dentro de `choices`; si no, avisa y usa el default."""
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
# Pares user/tutor enviados al LLM en cada petición (0 = todo el historial)
MAX_HISTORY_TURNS = _get_int("MAX_HISTORY_TURNS", 20)
AUTO_SAVE_ON_EXIT = _get_bool("AUTO_SAVE_ON_EXIT", False)

# --- Whisper (STT) ---
WHISPER_MODEL = _get_str("WHISPER_MODEL", "base")  # tiny, base, small, medium, large-v3
WHISPER_COMPUTE_TYPE = _get_str("WHISPER_COMPUTE_TYPE", "int8")  # int8 (CPU), float16 (GPU)
WHISPER_DEVICE = _get_str("WHISPER_DEVICE", "auto")  # auto, cpu, cuda
WHISPER_LANGUAGE = _get_str("WHISPER_LANGUAGE", "")  # vacío = sigue a TARGET_LANGUAGE

# --- Ollama (LLM) ---
OLLAMA_URL = _get_str("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = _get_str("OLLAMA_MODEL", "llama3.1")
OLLAMA_TIMEOUT = _get_int("OLLAMA_TIMEOUT", 120)
OLLAMA_NUM_CTX = _get_int("OLLAMA_NUM_CTX", 0)  # 0 = default de Ollama
OLLAMA_TEMPERATURE = _get_float("OLLAMA_TEMPERATURE", 0.3)  # <0 = default de Ollama

# --- Audio ---
SAMPLE_RATE = _get_int("SAMPLE_RATE", 16000)  # Hz — Whisper espera 16kHz
CHANNELS = _get_int("CHANNELS", 1)  # Mono
SILENCE_THRESHOLD = _get_float("SILENCE_THRESHOLD", 0.01)  # Umbral RMS de silencio
SILENCE_DURATION = _get_float("SILENCE_DURATION", 1.5)  # Seg. de silencio para cortar
NO_SPEECH_TIMEOUT = _get_float("NO_SPEECH_TIMEOUT", 6.0)  # Seg. sin voz antes de abortar
MAX_RECORD_SECONDS = _get_int("MAX_RECORD_SECONDS", 30)  # Máximo de grabación

# --- Text-to-Speech (opcional) ---
TTS_ENABLED = _get_bool("TTS_ENABLED", False)  # El tutor responde también con voz
TTS_BACKEND = _get_choice("TTS_BACKEND", "auto", ("auto", "say", "pyttsx3"))
TTS_RATE = _get_int("TTS_RATE", 170)  # Palabras por minuto
