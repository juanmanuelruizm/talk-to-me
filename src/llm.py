import json
from typing import Iterator

import requests

from config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT


def chat(messages: list[dict]) -> str:
    """Envía mensajes a Ollama y devuelve la respuesta completa del asistente."""
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
        },
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


def chat_stream(messages: list[dict]) -> Iterator[str]:
    """Igual que chat() pero devuelve la respuesta token a token (streaming).

    Permite mostrar la respuesta en tiempo real mientras el modelo la genera.
    """
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": True,
        },
        timeout=OLLAMA_TIMEOUT,
        stream=True,
    )
    response.raise_for_status()

    for line in response.iter_lines():
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        chunk = data.get("message", {}).get("content", "")
        if chunk:
            yield chunk
        if data.get("done"):
            break


def check_connection() -> bool:
    """Verifica que Ollama está corriendo y el modelo está disponible."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        # Ollama puede devolver el nombre con o sin tag (:latest)
        return any(OLLAMA_MODEL in m for m in models)
    except (requests.ConnectionError, requests.Timeout):
        return False


if __name__ == "__main__":
    # Test standalone
    if check_connection():
        print("Ollama connected")
        print("LLM: ", end="", flush=True)
        for token in chat_stream([
            {"role": "system", "content": "You are a helpful English tutor."},
            {"role": "user", "content": "Hello! How are you?"},
        ]):
            print(token, end="", flush=True)
        print()
    else:
        print("Ollama not reachable or model not found")
