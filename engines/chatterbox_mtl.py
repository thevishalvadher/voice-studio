"""
engines/chatterbox_mtl.py - Resemble AI "Chatterbox Multilingual" engine (MIT licence).

Speaks 23 languages, including Hindi ("hi") and English ("en").
Every output carries Resemble's invisible PerTh watermark. That happens
inside model.generate() and we NEVER remove or disable it.
"""

import random

import numpy as np

from engines.base import Engine


def set_seed(seed):
    """Fix all random number generators so the same input gives the same voice."""
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class ChatterboxMtlEngine(Engine):
    name = "chatterbox_mtl"
    needs_transcript = False  # Chatterbox clones from audio alone

    def __init__(self):
        self.model = None         # loaded once, then reused
        self.device = None        # "cuda" (GPU) or "cpu"
        self._demo_conds = None   # the model's built-in demo voice
        self._conds_cache = {}    # voice fingerprints already read from Drive

    @property
    def sample_rate(self):
        return self.model.sr if self.model is not None else 24000

    def load(self):
        """Download (first time) and load the model. Only runs once."""
        if self.model is not None:
            return
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
        # The model comes with a built-in voice. Keep it for the engine test.
        self._demo_conds = self.model.conds

    def prepare_voice(self, sample_path, conds_path, settings):
        """Build the voice fingerprint from a clean sample and save it as conds.pt."""
        self.load()
        self.model.prepare_conditionals(str(sample_path), exaggeration=settings["exaggeration"])
        self.model.conds.save(str(conds_path))
        self._conds_cache.pop(str(conds_path), None)

    def _load_conds(self, conds_path):
        """Read a saved conds.pt (cached in memory, refreshed if the file changes)."""
        from pathlib import Path
        from chatterbox.mtl_tts import Conditionals

        key = str(conds_path)
        mtime = Path(conds_path).stat().st_mtime
        cached = self._conds_cache.get(key)
        if cached is None or cached[0] != mtime:
            conds = Conditionals.load(key, map_location=self.device).to(self.device)
            self._conds_cache[key] = (mtime, conds)
        return self._conds_cache[key][1]

    def synthesize(self, text, language_id, settings, conds_path=None, sample_path=None):
        """Speak one short piece of text. Returns a numpy float32 array."""
        self.load()
        options = {
            "language_id": language_id,
            "exaggeration": settings["exaggeration"],
            "cfg_weight": settings["cfg_weight"],
            "temperature": settings["temperature"],
        }
        if conds_path:
            self.model.conds = self._load_conds(conds_path)   # saved voice (normal use)
        elif sample_path:
            options["audio_prompt_path"] = str(sample_path)   # raw clip (tests)
        else:
            self.model.conds = self._demo_conds               # built-in demo voice

        set_seed(settings["seed"])  # same seed + same text = same audio
        wav = self.model.generate(text, **options)  # watermark is added in here
        return wav.squeeze(0).detach().cpu().numpy().astype(np.float32)
