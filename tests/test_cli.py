import numpy as np
import pytest

from talk_to_me import cli
from talk_to_me.llm import ConnectionStatus, LLMError


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "SESSIONS_DIR", tmp_path)
    return cli.App(level="intermediate", language="en", model="m", input_fn=lambda _: "")


def stream_of(*tokens):
    def fake(messages, model=None):
        fake.calls.append((messages, model))
        yield from tokens

    fake.calls = []
    return fake


def test_help_and_unknown_command(app, capsys):
    app.handle_input("/help")
    assert "/language" in capsys.readouterr().out
    app.handle_input("/levels")
    assert "Unknown command: /levels" in capsys.readouterr().out
    app.handle_input("/LEVEL beginner")  # case-insensitive command name
    assert app.level == "beginner"


def test_level_and_language_change_reset_conversation(app, capsys):
    app.conversation.add_user("hi")
    app.handle_input("/level advanced")
    assert app.level == "advanced" and app.conversation.is_empty
    app.conversation.add_user("hi")
    app.handle_input("/language es")
    assert app.language == "es" and app.conversation.is_empty
    assert "Spanish" in capsys.readouterr().out
    app.handle_input("/level expert")
    assert "Usage: /level" in capsys.readouterr().out and app.level == "advanced"
    app.handle_input("/language klingon")
    assert "Usage: /language" in capsys.readouterr().out and app.language == "es"


def test_chat_turn_streams_and_records_history(app, monkeypatch, capsys):
    fake = stream_of("Hel", "lo!")
    monkeypatch.setattr(cli, "chat_stream", fake)
    app.handle_input("Hi there")
    out = capsys.readouterr().out
    assert "Tutor: Hello!" in out
    assert [m["content"] for m in app.conversation.turns] == ["Hi there", "Hello!"]
    messages, model = fake.calls[0]
    assert model == "m"
    assert messages[0]["role"] == "system"
    assert messages[-1]["content"] == "Hi there"


def test_chat_turn_drops_user_message_on_llm_error(app, monkeypatch, capsys):
    def boom(messages, model=None):
        raise LLMError("down")
        yield  # pragma: no cover

    monkeypatch.setattr(cli, "chat_stream", boom)
    app.handle_input("Hi")
    assert "LLM error: down" in capsys.readouterr().out
    assert app.conversation.is_empty


def test_chat_turn_drops_user_message_on_empty_reply(app, monkeypatch, capsys):
    monkeypatch.setattr(cli, "chat_stream", stream_of("  "))
    app.handle_input("Hi")
    assert "empty reply" in capsys.readouterr().out
    assert app.conversation.is_empty


def test_chat_turn_cancelled_with_ctrl_c(app, monkeypatch, capsys):
    def interrupted(messages, model=None):
        yield "Hel"
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "chat_stream", interrupted)
    app.handle_input("Hi")
    assert "(cancelled)" in capsys.readouterr().out
    assert app.conversation.is_empty


def test_history_and_save(app, monkeypatch, capsys, tmp_path):
    app.handle_input("/history")
    assert "(no messages yet)" in capsys.readouterr().out
    app.handle_input("/save")
    assert "(nothing to save yet)" in capsys.readouterr().out

    monkeypatch.setattr(cli, "chat_stream", stream_of("Hello!"))
    app.handle_input("Hi")
    capsys.readouterr()
    app.handle_input("/history")
    out = capsys.readouterr().out
    assert "You: Hi" in out and "Tutor: Hello!" in out
    app.handle_input("/save")
    assert "Conversation saved to" in capsys.readouterr().out
    assert list(tmp_path.glob("session_*.md"))
    assert not app.conversation.unsaved


def test_text_command_uses_args_or_prompt(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cli, "SESSIONS_DIR", tmp_path)
    monkeypatch.setattr(cli, "chat_stream", stream_of("ok"))
    app = cli.App(model="m", input_fn=lambda _: "typed message")
    app.handle_input("/text inline message")
    assert app.conversation.turns[0]["content"] == "inline message"
    app.handle_input("/text")
    assert app.conversation.turns[2]["content"] == "typed message"
    app = cli.App(model="m", input_fn=lambda _: "   ")
    app.handle_input("/text")
    assert "empty message" in capsys.readouterr().out


def test_voice_turn_no_speech_and_transcription(app, monkeypatch, capsys):
    monkeypatch.setattr(cli.stt, "ensure_loaded", lambda: None)
    monkeypatch.setattr(cli, "record_until_silence", lambda stop_requested=None: np.array([]))
    app.handle_input("")
    assert "no speech detected" in capsys.readouterr().out

    monkeypatch.setattr(
        cli, "record_until_silence", lambda stop_requested=None: np.ones(16000, dtype=np.float32)
    )
    seen = {}
    monkeypatch.setattr(
        cli.stt, "transcribe", lambda audio, language=None: seen.update(lang=language) or "I go"
    )
    monkeypatch.setattr(cli, "chat_stream", stream_of("You went."))
    app.handle_input("/language es")
    app.handle_input("")
    out = capsys.readouterr().out
    assert 'You said: "I go"' in out and "Tutor: You went." in out
    assert seen["lang"] == "es"


def test_voice_turn_audio_error_is_reported(app, monkeypatch, capsys):
    monkeypatch.setattr(cli.stt, "ensure_loaded", lambda: None)

    def boom(stop_requested=None):
        raise RuntimeError("no input device")

    monkeypatch.setattr(cli, "record_until_silence", boom)
    app.handle_input("")
    out = capsys.readouterr().out
    assert "Audio error: no input device" in out and "/text" in out


def test_run_quits_and_asks_to_save(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cli, "SESSIONS_DIR", tmp_path)
    monkeypatch.setattr(cli, "chat_stream", stream_of("Hello!"))
    answers = iter(["Hi", "/quit", "y"])
    prompts = []

    def input_fn(prompt):
        prompts.append(prompt)
        return next(answers)

    app = cli.App(model="m", input_fn=input_fn)
    app.run()
    out = capsys.readouterr().out
    assert "Save the conversation before leaving?" in prompts[-1]
    assert "Conversation saved to" in out and "Bye!" in out
    assert list(tmp_path.glob("session_*.md"))


def test_run_auto_saves_on_eof(monkeypatch, capsys, tmp_path, cfg):
    monkeypatch.setattr(cli, "SESSIONS_DIR", tmp_path)
    monkeypatch.setattr(cli, "chat_stream", stream_of("Hello!"))
    cfg("AUTO_SAVE_ON_EXIT", True)
    answers = iter(["Hi"])

    def input_fn(_):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    cli.App(model="m", input_fn=input_fn).run()
    assert "Conversation saved to" in capsys.readouterr().out
    assert list(tmp_path.glob("session_*.md"))


def test_main_exits_when_model_missing(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "check_connection",
        lambda model: ConnectionStatus(True, False, ["llama3.1:latest"]),
    )
    with pytest.raises(SystemExit) as exc:
        cli.main(["--model", "nope"])
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "ollama pull nope" in out and "llama3.1:latest" in out


def test_main_exits_when_ollama_down(monkeypatch, capsys):
    monkeypatch.setattr(
        cli, "check_connection", lambda model: ConnectionStatus(False, False, error="refused")
    )
    with pytest.raises(SystemExit):
        cli.main([])
    assert "Could not connect to Ollama" in capsys.readouterr().out
