from talk_to_me.prompts import CORRECTION_MARKER, LANGUAGES, LEVELS, get_system_prompt


def test_every_level_and_language_renders():
    for level in LEVELS:
        for code, name in LANGUAGES.items():
            prompt = get_system_prompt(level, code)
            assert f"{name} tutor" in prompt
            assert f"Speak only in {name}" in prompt
            assert prompt.count(CORRECTION_MARKER) >= 2  # rule + example
            assert CORRECTION_MARKER in prompt


def test_levels_differ():
    assert get_system_prompt("beginner") != get_system_prompt("advanced")
    assert "beginner" in get_system_prompt("beginner")
    assert "advanced" in get_system_prompt("advanced")


def test_unknown_values_fall_back():
    assert get_system_prompt("expert", "xx") == get_system_prompt("intermediate", "en")
