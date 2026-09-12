"""Conversation state: turns, history trimming, and Markdown export."""

from datetime import datetime
from pathlib import Path

from talk_to_me.prompts import LANGUAGES, get_system_prompt

Message = dict[str, str]

SESSIONS_DIR = Path(__file__).resolve().parent.parent / "sessions"


class Conversation:
    """History of a practice session (the system prompt is not part of `turns`)."""

    def __init__(self, level: str, language: str, model: str = "") -> None:
        self.level = level
        self.language = language
        self.model = model
        self.turns: list[Message] = []
        self.unsaved = False

    # --- State ---
    @property
    def system_prompt(self) -> str:
        return get_system_prompt(self.level, self.language)

    @property
    def language_name(self) -> str:
        return LANGUAGES.get(self.language, self.language)

    @property
    def is_empty(self) -> bool:
        return not self.turns

    def reset(self) -> None:
        self.turns = []
        self.unsaved = False

    # --- Turns ---
    def add_user(self, text: str) -> None:
        self.turns.append({"role": "user", "content": text})
        self.unsaved = True

    def add_assistant(self, text: str) -> None:
        self.turns.append({"role": "assistant", "content": text})
        self.unsaved = True

    def drop_last_user(self) -> None:
        """Removes the last message if it is from the user (e.g. when the LLM fails)."""
        if self.turns and self.turns[-1]["role"] == "user":
            self.turns.pop()
            self.unsaved = bool(self.turns)

    def for_llm(self, max_turns: int = 0) -> list[Message]:
        """Messages to send to the LLM: system prompt + the last `max_turns` pairs.

        `max_turns=0` sends the full history. Trimming prevents Ollama from
        truncating from the top (and dropping the system prompt) in long sessions.
        """
        turns = self.turns
        if max_turns > 0:
            turns = turns[-(2 * max_turns) :]
            # Never start with an assistant reply without its question.
            if turns and turns[0]["role"] == "assistant":
                turns = turns[1:]
        return [{"role": "system", "content": self.system_prompt}, *turns]

    # --- Export ---
    def to_markdown(self, now: datetime | None = None) -> str:
        now = now or datetime.now()
        lines = [
            f"# {self.language_name} practice session — {now:%Y-%m-%d %H:%M}",
            "",
            f"- Level: {self.level}",
            f"- Language: {self.language_name}",
        ]
        if self.model:
            lines.append(f"- Model: {self.model}")
        lines.append("")
        for m in self.turns:
            speaker = "You" if m["role"] == "user" else "Tutor"
            lines.append(f"**{speaker}:** {m['content']}")
            lines.append("")
        return "\n".join(lines)

    def save(self, sessions_dir: Path = SESSIONS_DIR, now: datetime | None = None) -> Path:
        """Saves the conversation as Markdown and returns the file path."""
        now = now or datetime.now()
        sessions_dir.mkdir(parents=True, exist_ok=True)
        path = sessions_dir / f"session_{now:%Y%m%d_%H%M%S}.md"
        path.write_text(self.to_markdown(now), encoding="utf-8")
        self.unsaved = False
        return path
