"""Configuración central de la app.

Todos los valores tienen un default razonable y pueden sobreescribirse con
variables de entorno (o un archivo `.env` en la raíz del proyecto), sin tener
que tocar este archivo.

Ejemplo de `.env`:
    WHISPER_MODEL=small
    OLLAMA_MODEL=llama3.1
    TTS_ENABLED=true
"""

import os
from pathlib import Path


# --- Carga opcional de un archivo .env (sin dependencias externas) ---
def _load_dotenv() -> None:
    """Carga variables de un archivo .env si existe, sin pisar las ya definidas."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # No pisamos variables ya definidas en el entorno real
        os.environ.setdefault(key, value)


_load_dotenv()


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


# --- Whisper (STT) ---
WHISPER_MODEL = _get_str("WHISPER_MODEL", "base")          # tiny, base, small, medium, large-v3
WHISPER_COMPUTE_TYPE = _get_str("WHISPER_COMPUTE_TYPE", "int8")  # int8 (CPU), float16 (GPU)
WHISPER_LANGUAGE = _get_str("WHISPER_LANGUAGE", "en")

# --- Ollama (LLM) ---
OLLAMA_URL = _get_str("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = _get_str("OLLAMA_MODEL", "llama3.1")
OLLAMA_TIMEOUT = _get_int("OLLAMA_TIMEOUT", 120)

# --- Audio ---
SAMPLE_RATE = _get_int("SAMPLE_RATE", 16000)        # Hz — Whisper espera 16kHz
CHANNELS = _get_int("CHANNELS", 1)                  # Mono
SILENCE_THRESHOLD = _get_float("SILENCE_THRESHOLD", 0.01)  # Umbral RMS de silencio
SILENCE_DURATION = _get_float("SILENCE_DURATION", 1.5)     # Seg. de silencio para cortar
MAX_RECORD_SECONDS = _get_int("MAX_RECORD_SECONDS", 30)    # Máximo de grabación

# --- Text-to-Speech (opcional) ---
TTS_ENABLED = _get_bool("TTS_ENABLED", False)       # El tutor responde también con voz
TTS_RATE = _get_int("TTS_RATE", 170)                # Palabras por minuto (pyttsx3)

# --- App ---
DEFAULT_LEVEL = _get_str("DEFAULT_LEVEL", "intermediate")  # beginner, intermediate, advanced
