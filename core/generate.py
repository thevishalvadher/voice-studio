"""
core/generate.py - turn text into audio files.
"""

from pathlib import Path

import config
import engines
from core import StudioError
from core import audio_utils

# The two lines used by the engine test (Milestone 2).
TEST_LINES = {
    "hi": "भोला काका ने खेत से लौटकर कहा, आज बारिश ज़रूर होगी।",
    "en": "Bhola Kaka smiled and said, the rain will come today, mark my words.",
}


def generate_test_lines(sample_path=None):
    """Speak the Hindi and English test lines and save them to outputs/test/.

    Uses the model's built-in demo voice, or sample_path if you give one.
    Returns a list of saved WAV paths.
    """
    if sample_path and not Path(sample_path).exists():
        raise StudioError(f"Demo sample not found: {sample_path}")
    out_dir = config.outputs_dir() / "test"
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for code, line in TEST_LINES.items():
        engine, info = engines.for_language(code)
        audio = engine.synthesize(line, info["language_id"], config.DEFAULT_SETTINGS,
                                  sample_path=sample_path or None)
        path = out_dir / f"{code}_test.wav"
        audio_utils.save_wav(path, audio, engine.sample_rate)
        saved.append(path)
    return saved
