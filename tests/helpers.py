"""
tests/helpers.py - a fake engine and a test base class.

The fake engine pretends to be Chatterbox: no GPU, no model download.
It makes a short beep whose sound depends on the text and the seed, so we
can check that "same text + same seed = same audio".
"""

import shutil
import tempfile
import unittest
import zlib
from pathlib import Path

import numpy as np

import config
import engines
from core import audio_utils
from engines.base import Engine

SAMPLE_RATE = 24000


class FakeEngine(Engine):
    name = "chatterbox_mtl"
    sample_rate = SAMPLE_RATE

    def __init__(self):
        self.loaded = False
        self.prepared = []    # every prepare_voice call
        self.calls = []       # every synthesize call

    def load(self):
        self.loaded = True

    def prepare_voice(self, sample_path, conds_path, settings):
        self.prepared.append(Path(sample_path))
        Path(conds_path).write_text("fake fingerprint")

    def synthesize(self, text, language_id, settings, conds_path=None, sample_path=None):
        self.calls.append({
            "text": text, "language_id": language_id, "settings": dict(settings),
            "conds_path": conds_path, "sample_path": sample_path,
        })
        # 0.1 s of "speech" per 10 characters, random but repeatable.
        rng = np.random.default_rng(zlib.crc32(text.encode()) + int(settings["seed"]))
        length = int(SAMPLE_RATE * 0.01 * max(len(text), 1))
        return (rng.uniform(-0.5, 0.5, length)).astype(np.float32)


def make_tone(path, seconds, sample_rate=44100, channels=2, silence=0.0):
    """Write a test WAV: a tone of `seconds`, with `silence` seconds before and after."""
    t = np.arange(int(sample_rate * seconds)) / sample_rate
    tone = 0.3 * np.sin(2 * np.pi * 220 * t)
    quiet = np.zeros(int(sample_rate * silence))
    audio = np.concatenate([quiet, tone, quiet])
    if channels == 2:
        audio = np.stack([audio, audio * 0.5], axis=1)
    audio_utils.save_wav(path, audio, sample_rate)
    return Path(path)


class StudioTestCase(unittest.TestCase):
    """Every test gets its own empty "Drive" folder and a fresh fake engine."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._old_root = config.DATA_ROOT
        config.DATA_ROOT = self.tmp / "drive"
        self.engine = FakeEngine()
        engines.register_engine("chatterbox_mtl", self.engine)

    def tearDown(self):
        config.DATA_ROOT = self._old_root
        engines._loaded.clear()
        shutil.rmtree(self.tmp, ignore_errors=True)
