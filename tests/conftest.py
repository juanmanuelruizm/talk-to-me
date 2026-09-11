import pytest

from talk_to_me import config


@pytest.fixture
def cfg(monkeypatch):
    """Permite cambiar valores de config en un test: cfg("MAX_HISTORY_TURNS", 2)."""

    def _set(name, value):
        monkeypatch.setattr(config, name, value)

    return _set
