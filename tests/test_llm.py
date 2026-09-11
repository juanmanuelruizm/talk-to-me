import json

import pytest
import requests

from talk_to_me import llm


class FakeResponse:
    def __init__(self, lines=(), status_code=200, payload=None, text=""):
        self._lines = list(lines)
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.closed = False

    def iter_lines(self):
        yield from self._lines

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")

    def close(self):
        self.closed = True


def _stream_lines(*chunks, done=True):
    lines = [json.dumps({"message": {"content": c}, "done": False}).encode() for c in chunks]
    if done:
        lines.append(json.dumps({"message": {"content": ""}, "done": True}).encode())
    return lines


def test_chat_stream_yields_tokens_and_stops_at_done(monkeypatch):
    calls = {}

    def fake_post(url, json, timeout, stream):
        calls["json"] = json
        return FakeResponse(_stream_lines("Hel", "lo") + [b"never reached"])

    monkeypatch.setattr(llm.requests, "post", fake_post)
    assert list(llm.chat_stream([{"role": "user", "content": "hi"}], model="m")) == ["Hel", "lo"]
    assert calls["json"]["model"] == "m"
    assert calls["json"]["stream"] is True
    assert calls["json"]["options"] == {"temperature": 0.3}


def test_chat_stream_omits_options_when_all_disabled(monkeypatch, cfg):
    cfg("OLLAMA_TEMPERATURE", -1)
    captured = {}

    def fake_post(url, json, timeout, stream):
        captured.update(json)
        return FakeResponse()

    monkeypatch.setattr(llm.requests, "post", fake_post)
    list(llm.chat_stream([]))
    assert "options" not in captured


def test_chat_stream_sends_num_ctx_when_configured(monkeypatch, cfg):
    cfg("OLLAMA_NUM_CTX", 8192)
    cfg("OLLAMA_TEMPERATURE", -1)
    captured = {}

    def fake_post(url, json, timeout, stream):
        captured.update(json)
        return FakeResponse()

    monkeypatch.setattr(llm.requests, "post", fake_post)
    list(llm.chat_stream([]))
    assert captured["options"] == {"num_ctx": 8192}


def test_chat_stream_raises_on_error_line(monkeypatch):
    lines = [b"not json", json.dumps({"error": "model not found"}).encode()]
    monkeypatch.setattr(llm.requests, "post", lambda *a, **k: FakeResponse(lines))
    with pytest.raises(llm.LLMError, match="model not found"):
        list(llm.chat_stream([]))


def test_chat_stream_raises_on_http_error(monkeypatch):
    resp = FakeResponse(status_code=404, payload={"error": "no such model"})
    monkeypatch.setattr(llm.requests, "post", lambda *a, **k: resp)
    with pytest.raises(llm.LLMError, match="404.*no such model"):
        list(llm.chat_stream([]))


def test_chat_stream_wraps_connection_errors(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(llm.requests, "post", boom)
    with pytest.raises(llm.LLMError, match="refused"):
        list(llm.chat_stream([]))


def test_chat_returns_full_message(monkeypatch):
    resp = FakeResponse(payload={"message": {"content": "Hi there"}})
    monkeypatch.setattr(llm.requests, "post", lambda *a, **k: resp)
    assert llm.chat([]) == "Hi there"


@pytest.mark.parametrize(
    "wanted,available,expected",
    [
        ("llama3.1", ["llama3.1:latest"], True),
        ("llama3.1:latest", ["llama3.1:latest"], True),
        ("llama3.1:8b", ["llama3.1:latest"], False),
        ("llama3", ["llama3.1:latest"], False),  # substring is not a match
        ("qwen2.5", ["qwen2.5:7b", "llama3.1:latest"], True),
        ("mistral", [], False),
    ],
)
def test_model_matches(wanted, available, expected):
    assert llm._model_matches(wanted, available) is expected


def test_check_connection_found(monkeypatch):
    payload = {"models": [{"name": "llama3.1:latest"}, {"name": "qwen2.5:7b"}]}
    monkeypatch.setattr(llm.requests, "get", lambda *a, **k: FakeResponse(payload=payload))
    status = llm.check_connection("qwen2.5")
    assert status.ok
    assert status.available == ["llama3.1:latest", "qwen2.5:7b"]


def test_check_connection_model_missing(monkeypatch):
    payload = {"models": [{"name": "llama3.1:latest"}]}
    monkeypatch.setattr(llm.requests, "get", lambda *a, **k: FakeResponse(payload=payload))
    status = llm.check_connection("mistral")
    assert status.reachable and not status.model_found and not status.ok


def test_check_connection_down(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(llm.requests, "get", boom)
    status = llm.check_connection("llama3.1")
    assert not status.reachable and not status.ok and "refused" in status.error


def test_check_connection_bad_json(monkeypatch):
    monkeypatch.setattr(llm.requests, "get", lambda *a, **k: FakeResponse(payload=None))
    assert not llm.check_connection("llama3.1").reachable
