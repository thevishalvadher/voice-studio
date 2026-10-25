"""
core/audio_utils.py - small audio helpers.

Audio here is a numpy array of numbers between -1.0 and 1.0
(one number per sample, 24,000 samples per second), always mono.
"""

import numpy as np
import soundfile as sf

import config
from core import StudioError


def seconds(audio, sample_rate):
    """Length of the audio in seconds."""
    return len(audio) / float(sample_rate)


def format_seconds(value):
    """6.0 -> "6", 9.64 -> "9.6" (for friendly messages)."""
    return f"{value:.1f}".rstrip("0").rstrip(".")


def save_wav(path, audio, sample_rate):
    """Save audio as a normal 16-bit WAV file."""
    audio = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    sf.write(str(path), audio, sample_rate, subtype="PCM_16")


def load_audio(path, sample_rate=config.SAMPLE_RATE):
    """Read any audio file (WAV, MP3, M4A, OGG, WEBM…) as mono at sample_rate."""
    from pydub import AudioSegment  # uses ffmpeg behind the scenes

    try:
        with open(path, "rb") as f:  # ffmpeg works out the format by itself
            sound = AudioSegment.from_file(f)
    except Exception:
        raise StudioError("Could not read this audio file. Please use WAV, MP3, M4A, OGG or WEBM.")
    sound = sound.set_channels(1).set_frame_rate(sample_rate).set_sample_width(2)
    # 16-bit numbers (-32768..32767) -> floats (-1.0..1.0)
    return np.array(sound.get_array_of_samples(), dtype=np.float32) / 32768.0


def trim_silence(audio, sample_rate, threshold_db=-40, padding_s=0.1):
    """Cut quiet parts from the start and end.

    "Quiet" means 40 dB softer than the loudest moment. A little padding
    (0.1 s) is kept so words are not clipped.
    """
    frame = int(sample_rate * 0.02)  # look at 20 ms at a time
    count = len(audio) // frame
    if count == 0:
        return audio
    frames = audio[: count * frame].reshape(count, frame)
    loudness_db = 20 * np.log10(np.sqrt(np.mean(frames ** 2, axis=1)) + 1e-10)
    loud = np.where(loudness_db > loudness_db.max() + threshold_db)[0]
    pad = int(sample_rate * padding_s)
    start = max(0, loud[0] * frame - pad)
    end = min(len(audio), (loud[-1] + 1) * frame + pad)
    return audio[start:end]


def normalize(audio, target_db=-20.0, max_peak=0.95):
    """Make the audio a standard loudness, without letting peaks clip."""
    rms = float(np.sqrt(np.mean(audio ** 2))) if len(audio) else 0.0
    if rms < 1e-6:
        return audio
    audio = audio * (10 ** (target_db / 20) / rms)
    peak = float(np.max(np.abs(audio)))
    if peak > max_peak:
        audio = audio * (max_peak / peak)
    return audio.astype(np.float32)


def clean_sample(in_path, out_path):
    """Prepare a voice sample: mono, trim silence, normalize, check 10–30 s.

    Saves the result as a WAV at out_path and returns its length in seconds.
    Raises StudioError with a plain-English message if something is wrong.
    """
    sample_rate = config.SAMPLE_RATE
    audio = load_audio(in_path, sample_rate)

    if len(audio) == 0 or np.max(np.abs(audio)) < 0.01:
        raise StudioError("We could not hear any voice in this sample. Check your mic and try again.")

    audio = trim_silence(audio, sample_rate)
    length = seconds(audio, sample_rate)
    if length < config.MIN_SAMPLE_SECONDS:
        raise StudioError(
            f"Sample too short ({format_seconds(length)} s). "
            f"Need at least {config.MIN_SAMPLE_SECONDS} s."
        )
    if length > config.MAX_SAMPLE_SECONDS:
        raise StudioError(
            f"Sample too long ({format_seconds(length)} s). "
            f"Please use {config.MAX_SAMPLE_SECONDS} s or less."
        )

    save_wav(out_path, normalize(audio), sample_rate)
    return round(length, 1)


def join_chunks(chunks, sample_rate, gap_ms=config.GAP_MS):
    """Join audio pieces into one, with a short silence (150 ms) between them."""
    gap = np.zeros(int(sample_rate * gap_ms / 1000), dtype=np.float32)
    parts = []
    for i, chunk in enumerate(chunks):
        if i > 0:
            parts.append(gap)
        parts.append(np.asarray(chunk, dtype=np.float32))
    return np.concatenate(parts) if parts else np.zeros(0, dtype=np.float32)


def wav_to_mp3(wav_path, mp3_path, bitrate=config.MP3_BITRATE):
    """Make an MP3 copy of a WAV file (192 kbps by default).

    The MP3 is saved at 44,100 Hz: MP3s at 24,000 Hz cannot go above 160 kbps,
    and 44.1 kHz also opens cleanly in video editors like CapCut.
    """
    from pydub import AudioSegment

    AudioSegment.from_wav(str(wav_path)).export(
        str(mp3_path), format="mp3", bitrate=bitrate, parameters=["-ar", "44100"]
    )
