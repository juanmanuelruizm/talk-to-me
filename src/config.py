# --- Whisper (STT) ---
WHISPER_MODEL = "base"        # Opciones: tiny, base, small, medium, large-v3
WHISPER_COMPUTE_TYPE = "int8"  # int8 para CPU, float16 para GPU
WHISPER_LANGUAGE = "en"

# --- Ollama (LLM) ---
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"

# --- Audio ---
SAMPLE_RATE = 16000            # Hz — Whisper espera 16kHz
CHANNELS = 1                   # Mono
SILENCE_THRESHOLD = 0.01       # Umbral RMS para considerar silencio
SILENCE_DURATION = 1.5         # Segundos de silencio para cortar grabación
MAX_RECORD_SECONDS = 30        # Máximo de segundos de grabación

# --- App ---
DEFAULT_LEVEL = "intermediate"  # beginner, intermediate, advanced
