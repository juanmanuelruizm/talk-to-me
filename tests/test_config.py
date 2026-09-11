import os
from pathlib import Path

import pytest

from talk_to_me import config


def test_parse_env_file_ignores_comments_and_quotes():
    text = """
    # comentario
    WHISPER_MODEL=small
    OLLAMA_MODEL = "llama3.1"   
    TTS_ENABLED='true'
    SILENCE_DURATION=2.0  # inline comment
    INVALID LINE
    =novalue
    """
    assert config.parse_env_file(text) == {
        "WHISPER_MODEL": "small",
        "OLLAMA_MODEL": "llama3.1",
        "TTS_ENABLED": "true",
        "SILENCE_DURATION": "2.0",
    }


def test_load_dotenv_does_not_override_existing_env(tmp_path: Path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("TTM_TEST_A=from_file\nTTM_TEST_B=from_file\n")
    monkeypatch.setenv("TTM_TEST_A", "from_env")
    monkeypatch.delenv("TTM_TEST_B", raising=False)

    loaded = config.load_dotenv([tmp_path / "missing.env", env])

    assert loaded == env
    assert os.environ["TTM_TEST_A"] == "from_env"
    assert os.environ["TTM_TEST_B"] == "from_file"


def test_load_dotenv_returns_none_when_no_file(tmp_path: Path):
    assert config.load_dotenv([tmp_path / ".env"]) is None


@pytest.mark.parametrize(
    "raw,expected",
    [("1", True), ("true", True), ("YES", True), ("on", True), ("0", False), ("nope", False)],
)
def test_get_bool(monkeypatch, raw, expected):
    monkeypatch.setenv("TTM_BOOL", raw)
    assert config._get_bool("TTM_BOOL", not expected) is expected


def test_typed_getters_fall_back_on_garbage(monkeypatch):
    monkeypatch.setenv("TTM_INT", "abc")
    monkeypatch.setenv("TTM_FLOAT", "x.y")
    assert config._get_int("TTM_INT", 7) == 7
    assert config._get_float("TTM_FLOAT", 1.5) == 1.5
    monkeypatch.setenv("TTM_INT", "42")
    assert config._get_int("TTM_INT", 7) == 42


def test_get_choice_validates_and_warns(monkeypatch, capsys):
    monkeypatch.setenv("TTM_LEVEL", "expert")
    assert config._get_choice("TTM_LEVEL", "intermediate", ("beginner", "intermediate")) == (
        "intermediate"
    )
    assert "not valid" in capsys.readouterr().err
    monkeypatch.setenv("TTM_LEVEL", "Beginner")
    assert config._get_choice("TTM_LEVEL", "intermediate", ("beginner", "intermediate")) == (
        "beginner"
    )
