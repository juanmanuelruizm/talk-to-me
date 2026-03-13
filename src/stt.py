import numpy as np
from faster_whisper import WhisperModel

from config import WHISPER_MODEL, WHISPER_COMPUTE_TYPE, WHISPER_LANGUAGE, SAMPLE_RATE


_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        print(f"Loading Whisper model '{WHISPER_MODEL}' (first time may download)...")
        _model = WhisperModel(WHISPER_MODEL, compute_type=WHISPER_COMPUTE_TYPE)
        print("Whisper model loaded")
    return _model


def transcribe(audio: np.ndarray) -> str:
    """Transcribe un array de audio float32 (16kHz mono) a texto."""
    if len(audio) == 0:
        return ""

    model = _get_model()
    segments, info = model.transcribe(
        audio,
        language=WHISPER_LANGUAGE,
        beam_size=5,
        vad_filter=True,
    )

    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()


if __name__ == "__main__":
    # Test standalone: transcribir audio grabado
    from audio import record_until_silence

    print("Test de STT. Habla algo en inglés:")
    audio = record_until_silence()
    text = transcribe(audio)
    print(f"Transcripción: '{text}'")
