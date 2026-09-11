import numpy as np

from talk_to_me.audio import Decision, SilenceDetector, rms


def make(**kw):
    defaults = dict(
        threshold=0.01,
        silence_duration=1.0,
        no_speech_timeout=3.0,
        max_seconds=10.0,
        block_duration=0.5,
    )
    defaults.update(kw)
    return SilenceDetector(**defaults)


def run(detector, levels):
    decision = Decision.CONTINUE
    for level in levels:
        decision = detector.feed(level)
        if decision is not Decision.CONTINUE:
            break
    return decision


def test_stops_after_silence_following_speech():
    d = make()  # 1.0s silence = 2 blocks
    assert run(d, [0.5, 0.5, 0.0]) is Decision.CONTINUE
    assert d.feed(0.0) is Decision.STOP_SILENCE
    assert d.has_speech


def test_speech_resets_silence_counter():
    d = make()
    assert run(d, [0.5, 0.0, 0.5, 0.0]) is Decision.CONTINUE
    assert d.feed(0.0) is Decision.STOP_SILENCE


def test_stops_when_no_speech_at_all():
    d = make()  # 3.0s no-speech = 6 blocks
    assert run(d, [0.0] * 5) is Decision.CONTINUE
    assert d.feed(0.0) is Decision.STOP_NO_SPEECH
    assert not d.has_speech


def test_no_speech_timeout_can_be_disabled():
    d = make(no_speech_timeout=0, max_seconds=2.0)  # 4 blocks max
    assert run(d, [0.0] * 3) is Decision.CONTINUE
    assert d.feed(0.0) is Decision.STOP_MAX


def test_stops_at_max_duration_while_speaking():
    d = make(max_seconds=2.0)
    assert run(d, [0.5] * 3) is Decision.CONTINUE
    assert d.feed(0.5) is Decision.STOP_MAX


def test_rms():
    assert rms(np.zeros(100, dtype=np.float32)) == 0.0
    assert abs(rms(np.full(100, 0.5, dtype=np.float32)) - 0.5) < 1e-6
    assert rms(np.array([], dtype=np.float32)) == 0.0
