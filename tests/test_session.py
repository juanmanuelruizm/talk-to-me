from datetime import datetime

from talk_to_me.session import Conversation


def filled(n_pairs: int, **kw) -> Conversation:
    conv = Conversation("intermediate", "en", **kw)
    for i in range(n_pairs):
        conv.add_user(f"u{i}")
        conv.add_assistant(f"a{i}")
    return conv


def test_for_llm_starts_with_system_prompt_and_all_turns_by_default():
    conv = filled(3)
    msgs = conv.for_llm()
    assert msgs[0]["role"] == "system"
    assert "English" in msgs[0]["content"]
    assert [m["content"] for m in msgs[1:]] == ["u0", "a0", "u1", "a1", "u2", "a2"]


def test_for_llm_trims_to_last_pairs():
    conv = filled(3)
    msgs = conv.for_llm(max_turns=2)
    assert [m["content"] for m in msgs[1:]] == ["u1", "a1", "u2", "a2"]


def test_for_llm_trim_keeps_pending_user_message_and_never_starts_with_assistant():
    conv = filled(2)
    conv.add_user("u2")  # pending, no reply yet
    msgs = conv.for_llm(max_turns=1)
    assert [m["content"] for m in msgs[1:]] == ["u2"]
    msgs = conv.for_llm(max_turns=2)
    assert [m["content"] for m in msgs[1:]] == ["u1", "a1", "u2"]


def test_system_prompt_follows_level_and_language():
    conv = Conversation("beginner", "es")
    assert "Spanish" in conv.system_prompt and "beginner" in conv.system_prompt
    conv.language = "fr"
    assert "French" in conv.for_llm()[0]["content"]
    assert conv.language_name == "French"


def test_unsaved_flag_and_reset(tmp_path):
    conv = Conversation("intermediate", "en")
    assert conv.is_empty and not conv.unsaved
    conv.add_user("hi")
    assert conv.unsaved
    conv.save(tmp_path)
    assert not conv.unsaved
    conv.add_assistant("hello")
    assert conv.unsaved
    conv.reset()
    assert conv.is_empty and not conv.unsaved


def test_drop_last_user_only_drops_user_messages():
    conv = filled(1)
    conv.drop_last_user()  # last is assistant → untouched
    assert len(conv.turns) == 2
    conv.add_user("pending")
    conv.drop_last_user()
    assert [m["content"] for m in conv.turns] == ["u0", "a0"]
    empty = Conversation("intermediate", "en")
    empty.add_user("x")
    empty.drop_last_user()
    assert empty.is_empty and not empty.unsaved


def test_save_writes_markdown(tmp_path):
    conv = filled(1, model="llama3.1")
    now = datetime(2026, 9, 11, 10, 30, 5)
    path = conv.save(tmp_path, now=now)
    assert path == tmp_path / "session_20260911_103005.md"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# English practice session — 2026-09-11 10:30")
    assert "- Level: intermediate" in text
    assert "- Model: llama3.1" in text
    assert "**You:** u0" in text and "**Tutor:** a0" in text
