import requests

from config import OLLAMA_URL, OLLAMA_MODEL


def chat(messages: list[dict]) -> str:
    """Envía mensajes a Ollama y devuelve la respuesta del asistente."""
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


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
        resp = chat([
            {"role": "system", "content": "You are a helpful English tutor."},
            {"role": "user", "content": "Hello! How are you?"},
        ])
        print(f"LLM: {resp}")
    else:
        print("Ollama not reachable or model not found")
