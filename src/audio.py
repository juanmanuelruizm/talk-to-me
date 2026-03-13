import numpy as np
import sounddevice as sd

from config import SAMPLE_RATE, CHANNELS, SILENCE_THRESHOLD, SILENCE_DURATION, MAX_RECORD_SECONDS


def record_until_silence() -> np.ndarray:
    """Graba audio del micrófono hasta detectar silencio prolongado.

    Devuelve un array numpy float32 mono a 16kHz.
    """
    block_duration = 0.1  # segundos por bloque de lectura
    block_size = int(SAMPLE_RATE * block_duration)
    silent_blocks_needed = int(SILENCE_DURATION / block_duration)
    max_blocks = int(MAX_RECORD_SECONDS / block_duration)

    audio_chunks: list[np.ndarray] = []
    silent_blocks = 0
    has_speech = False

    print("🎙️  Listening... (speak now)")

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32") as stream:
        for _ in range(max_blocks):
            block, _ = stream.read(block_size)
            audio_chunks.append(block.copy())

            rms = np.sqrt(np.mean(block ** 2))

            if rms >= SILENCE_THRESHOLD:
                has_speech = True
                silent_blocks = 0
            else:
                silent_blocks += 1

            # Solo cortamos por silencio si ya hubo voz
            if has_speech and silent_blocks >= silent_blocks_needed:
                break

    if not audio_chunks:
        return np.array([], dtype=np.float32)

    audio = np.concatenate(audio_chunks, axis=0).flatten()
    print(f"✅  Recorded {len(audio) / SAMPLE_RATE:.1f}s of audio")
    return audio


if __name__ == "__main__":
    # Test standalone: graba y muestra duración
    print("Test de grabación de audio. Habla y luego quédate en silencio.")
    audio = record_until_silence()
    print(f"Audio capturado: {len(audio)} samples, {len(audio)/SAMPLE_RATE:.2f}s")
