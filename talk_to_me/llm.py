"""Cliente mínimo de la API de chat de Ollama (con y sin streaming)."""

import json
from collections.abc import Iterator
from dataclasses import dataclass, field

import requests

from talk_to_me import config


class LLMError(Exception):
    """Error al hablar con Ollama (conexión, HTTP o error devuelto por el modelo)."""


def _options() -> dict:
    opts: dict = {}
    if config.OLLAMA_NUM_CTX > 0:
        opts["num_ctx"] = config.OLLAMA_NUM_CTX
    if config.OLLAMA_TEMPERATURE >= 0:
        opts["temperature"] = config.OLLAMA_TEMPERATURE
    return opts


def _payload(messages: list[dict], model: str | None, stream: bool) -> dict:
    payload = {"model": model or config.OLLAMA_MODEL, "messages": messages, "stream": stream}
    options = _options()
    if options:
        payload["options"] = options
    return payload


def _raise_for_http_error(response: requests.Response) -> None:
    if response.status_code < 400:
        return
    try:
        detail = response.json().get("error", response.text)
    except ValueError:
        detail = response.text
    raise LLMError(f"Ollama returned HTTP {response.status_code}: {detail}")


def chat(messages: list[dict], model: str | None = None) -> str:
    """Envía mensajes a Ollama y devuelve la respuesta completa del asistente."""
    try:
        response = requests.post(
            f"{config.OLLAMA_URL}/api/chat",
            json=_payload(messages, model, stream=False),
            timeout=config.OLLAMA_TIMEOUT,
        )
    except requests.RequestException as e:
        raise LLMError(f"Could not reach Ollama at {config.OLLAMA_URL}: {e}") from e
    _raise_for_http_error(response)
    data = response.json()
    if "error" in data:
        raise LLMError(data["error"])
    return data.get("message", {}).get("content", "")


def chat_stream(messages: list[dict], model: str | None = None) -> Iterator[str]:
    """Igual que chat() pero devuelve la respuesta token a token (streaming)."""
    try:
        response = requests.post(
            f"{config.OLLAMA_URL}/api/chat",
            json=_payload(messages, model, stream=True),
            timeout=config.OLLAMA_TIMEOUT,
            stream=True,
        )
    except requests.RequestException as e:
        raise LLMError(f"Could not reach Ollama at {config.OLLAMA_URL}: {e}") from e
    _raise_for_http_error(response)

    try:
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "error" in data:
                raise LLMError(data["error"])
            chunk = data.get("message", {}).get("content", "")
            if chunk:
                yield chunk
            if data.get("done"):
                break
    except requests.RequestException as e:
        raise LLMError(f"Connection lost while streaming: {e}") from e
    finally:
        response.close()


def _strip_tag(name: str) -> str:
    return name.split(":", 1)[0]


def _model_matches(wanted: str, available: list[str]) -> bool:
    """`wanted` sin tag equivale a cualquier tag; con tag debe coincidir exactamente."""
    if wanted in available:
        return True
    if ":" in wanted:
        return False
    return any(_strip_tag(name) == wanted for name in available)


@dataclass
class ConnectionStatus:
    reachable: bool
    model_found: bool
    available: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.reachable and self.model_found


def check_connection(model: str | None = None) -> ConnectionStatus:
    """Verifica que Ollama está corriendo y que el modelo está descargado."""
    model = model or config.OLLAMA_MODEL
    try:
        resp = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        available = [m["name"] for m in resp.json().get("models", [])]
    except (requests.RequestException, ValueError, KeyError, TypeError) as e:
        return ConnectionStatus(reachable=False, model_found=False, error=str(e))
    return ConnectionStatus(
        reachable=True, model_found=_model_matches(model, available), available=available
    )


if __name__ == "__main__":
    status = check_connection()
    if status.ok:
        print("Ollama connected")
        print("LLM: ", end="", flush=True)
        for token in chat_stream(
            [
                {"role": "system", "content": "You are a helpful English tutor."},
                {"role": "user", "content": "Hello! How are you?"},
            ]
        ):
            print(token, end="", flush=True)
        print()
    else:
        print("Ollama not reachable or model not found:", status)
