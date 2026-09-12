"""Speech-to-text transcription with faster-whisper."""

import numpy as np

from talk_to_me import config

_model = None


def ensure_loaded():
    """Loads the Whisper model (once). Calling it before recording avoids waiting later."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel  # lazy import: it is heavy

        print(f"Loading Whisper model '{config.WHISPER_MODEL}' (first time may download)...")
        _model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
        print("Whisper model loaded")
    return _model


def transcribe(audio: np.ndarray, language: str | None = None) -> str:
    """Transcribes a float32 array (16kHz mono) to text in the given language."""
    if len(audio) == 0:
        return ""
    language = language or config.WHISPER_LANGUAGE or config.TARGET_LANGUAGE
    model = ensure_loaded()
    segments, _info = model.transcribe(audio, language=language, beam_size=5, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()


if __name__ == "__main__":
    from talk_to_me.audio import record_until_silence

    print("STT test. Say something:")
    text = transcribe(record_until_silence())
    print(f"Transcription: '{text}'")
