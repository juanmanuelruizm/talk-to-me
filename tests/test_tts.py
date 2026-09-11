import pytest

from talk_to_me.tts import clean_for_speech


@pytest.mark.parametrize(
    "text,expected",
    [
        # Trailing correction section is dropped.
        (
            'That sounds fun! What did you buy?\n\nCorrection: "I have went" -> "I went" (past).',
            "That sounds fun! What did you buy?",
        ),
        # Inline (beginner-style) correction is removed but the rest is kept.
        (
            'Nice! (Correction: you said "I go" → "I went") What did you do next?',
            "Nice! What did you do next?",
        ),
        # Markdown and arrows are cleaned.
        ("**Great** job! Say *hello* -> hi `now`", "Great job! Say hello to hi now"),
        # Nothing to clean.
        ("Hello, how are you today?", "Hello, how are you today?"),
        # Parenthesised trailing section on its own line.
        ("Good.\n(Correction: x -> y)", "Good."),
    ],
)
def test_clean_for_speech(text, expected):
    assert clean_for_speech(text) == expected


def test_only_correction_falls_back_to_original():
    text = 'Correction: "a" -> "b"'
    assert clean_for_speech(text) == text
