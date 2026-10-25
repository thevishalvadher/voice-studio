"""
core/audio_utils.py - small audio helpers.

Audio here is a numpy array of numbers between -1.0 and 1.0
(one number per sample, 24,000 samples per second), always mono.
"""

import numpy as np
import soundfile as sf


def seconds(audio, sample_rate):
    """Length of the audio in seconds."""
    return len(audio) / float(sample_rate)


def save_wav(path, audio, sample_rate):
    """Save audio as a normal 16-bit WAV file."""
    audio = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    sf.write(str(path), audio, sample_rate, subtype="PCM_16")
