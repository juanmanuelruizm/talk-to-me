"""Captura de micrófono con detección de silencio (y parada manual con ENTER)."""

from collections.abc import Callable
from enum import Enum

import numpy as np

from talk_to_me import config

BLOCK_DURATION = 0.1  # segundos por bloque de lectura del micrófono


class Decision(Enum):
    CONTINUE = "continue"
    STOP_SILENCE = "silence"  # hubo voz y después silencio suficiente
    STOP_NO_SPEECH = "no_speech"  # nunca se detectó voz
    STOP_MAX = "max"  # se alcanzó la duración máxima


class SilenceDetector:
    """Decide, bloque a bloque, cuándo parar de grabar. Lógica pura (sin audio real)."""

    def __init__(
        self,
        threshold: float,
        silence_duration: float,
        no_speech_timeout: float,
        max_seconds: float,
        block_duration: float = BLOCK_DURATION,
    ) -> None:
        self.threshold = threshold
        self.silent_blocks_needed = max(1, round(silence_duration / block_duration))
        self.no_speech_blocks = (
            max(1, round(no_speech_timeout / block_duration)) if no_speech_timeout > 0 else 0
        )
        self.max_blocks = max(1, round(max_seconds / block_duration))
        self.blocks = 0
        self.silent_blocks = 0
        self.has_speech = False

    def feed(self, rms: float) -> Decision:
        self.blocks += 1
        if rms >= self.threshold:
            self.has_speech = True
            self.silent_blocks = 0
        else:
            self.silent_blocks += 1

        if self.has_speech and self.silent_blocks >= self.silent_blocks_needed:
            return Decision.STOP_SILENCE
        if not self.has_speech and self.no_speech_blocks and self.blocks >= self.no_speech_blocks:
            return Decision.STOP_NO_SPEECH
        if self.blocks >= self.max_blocks:
            return Decision.STOP_MAX
        return Decision.CONTINUE


def rms(block: np.ndarray) -> float:
    return float(np.sqrt(np.mean(block.astype(np.float32) ** 2))) if block.size else 0.0


def record_until_silence(stop_requested: Callable[[], bool] | None = None) -> np.ndarray:
    """Graba del micrófono hasta detectar silencio, agotar el tiempo o `stop_requested()`.

    Devuelve un array numpy float32 mono a SAMPLE_RATE. Si no se detectó voz,
    devuelve un array vacío.
    """
    import sounddevice as sd  # import perezoso: requiere PortAudio, no hace falta para /text

    block_size = int(config.SAMPLE_RATE * BLOCK_DURATION)
    detector = SilenceDetector(
        threshold=config.SILENCE_THRESHOLD,
        silence_duration=config.SILENCE_DURATION,
        no_speech_timeout=config.NO_SPEECH_TIMEOUT,
        max_seconds=config.MAX_RECORD_SECONDS,
    )
    audio_chunks: list[np.ndarray] = []

    with sd.InputStream(
        samplerate=config.SAMPLE_RATE, channels=config.CHANNELS, dtype="float32"
    ) as stream:
        while True:
            block, _overflowed = stream.read(block_size)
            audio_chunks.append(block.copy())
            decision = detector.feed(rms(block))
            if decision is not Decision.CONTINUE:
                break
            if stop_requested is not None and stop_requested():
                break

    if not detector.has_speech or not audio_chunks:
        return np.array([], dtype=np.float32)

    audio = np.concatenate(audio_chunks, axis=0).flatten()
    print(f"Recorded {len(audio) / config.SAMPLE_RATE:.1f}s of audio")
    return audio


if __name__ == "__main__":
    print("Test de grabación de audio. Habla y luego quédate en silencio.")
    captured = record_until_silence()
    print(f"Audio capturado: {len(captured)} samples, {len(captured) / config.SAMPLE_RATE:.2f}s")
