"""Text-to-Speech opcional para que el tutor responda también con voz.

Usa `pyttsx3`, que funciona offline y es multiplataforma (usa el motor de voz
del sistema operativo). Es totalmente opcional: si la librería no está
instalada, las funciones no fallan, simplemente no hacen nada.

Para activarlo:
    pip install pyttsx3
    # y poner TTS_ENABLED=true en .env o el comando /tts dentro de la app
"""

import re

from config import TTS_RATE

_engine = None
_init_failed = False


def is_available() -> bool:
    """Devuelve True si pyttsx3 está instalado y se pudo inicializar."""
    return _get_engine() is not None


def _get_engine():
    global _engine, _init_failed
    if _engine is not None or _init_failed:
        return _engine
    try:
        import pyttsx3  # import perezoso: solo si se usa TTS

        _engine = pyttsx3.init()
        _engine.setProperty("rate", TTS_RATE)
    except Exception:
        # No instalado o sin motor de voz disponible en el sistema
        _init_failed = True
        _engine = None
    return _engine


def _clean_for_speech(text: str) -> str:
    """Quita la sección de correcciones para no leerla en voz alta."""
    # Cortamos a partir de "Correction:" o "(Correction:" para que la voz
    # suene natural y solo lea la parte conversacional.
    cut = re.split(r"\n*\(?Correction:", text, maxsplit=1)[0]
    return cut.strip() or text.strip()


def speak(text: str) -> None:
    """Lee el texto en voz alta (bloqueante). No-op si TTS no está disponible."""
    engine = _get_engine()
    if engine is None or not text.strip():
        return
    try:
        engine.say(_clean_for_speech(text))
        engine.runAndWait()
    except Exception:
        # Si algo falla en pleno uso, no rompemos la conversación.
        pass


if __name__ == "__main__":
    if is_available():
        print("TTS disponible. Probando voz...")
        speak("Hello! This is your English tutor speaking.")
    else:
        print("TTS no disponible. Instala pyttsx3: pip install pyttsx3")
