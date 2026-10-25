"""
core/generate.py - turn text into audio files.
"""

from pathlib import Path

import config
import engines
from core import StudioError
from core import audio_utils, text_utils, voices

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


def _next_output_paths(voice_id):
    """outputs/<date>/<voice>_<n>.wav and .mp3, with n = 0001, 0002, …"""
    day_dir = config.outputs_dir() / config.now().strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    numbers = []
    for existing in day_dir.glob(f"{voice_id}_*.wav"):
        tail = existing.stem[len(voice_id) + 1:]
        if tail.isdigit():
            numbers.append(int(tail))
    stem = f"{voice_id}_{max(numbers, default=0) + 1:04d}"
    return day_dir / f"{stem}.wav", day_dir / f"{stem}.mp3"


def generate(voice_id, text, exaggeration=None, seed=None, on_progress=None):
    """Speak text in a saved voice and save WAV + MP3 to outputs/<date>/.

    exaggeration / seed: optional one-time overrides from the "Advanced" area.
    on_progress(done, total): optional callback to show progress.
    Returns {"wav": path, "mp3": path, "seconds": length, "chunks": count}.
    """
    text = text_utils.clean_text(text)
    if not text:
        raise StudioError("Please type some text first.")
    if len(text) > config.MAX_TEXT_CHARS:
        raise StudioError(
            f"Text too long ({len(text)} characters). "
            f"Please use {config.MAX_TEXT_CHARS} or fewer, or split it into parts."
        )

    voice = voices.get_voice(voice_id)
    engine, language_info = engines.for_language(voice["language"])

    settings = dict(config.DEFAULT_SETTINGS)
    settings.update(voice.get("settings", {}))
    if exaggeration is not None:
        settings["exaggeration"] = float(exaggeration)
    if seed is not None:
        settings["seed"] = int(seed)

    # Consistency (Milestone 5): ALWAYS speak from the cached fingerprint
    # (conds.pt) plus the voice's fixed seed, never from the raw sample. Same
    # fingerprint + same seed = the same line sounds the same, and different
    # lines sound like the same person.
    conds_path = voices.data_path(voice["conds_file"])
    if not conds_path.exists():
        # conds.pt was deleted or never finished: rebuild it once from the clean sample.
        sample_path = voices.data_path(voice["sample_file"])
        if not sample_path.exists():
            raise StudioError(
                f"The files for voice '{voice['name']}' are missing in Drive. "
                "Please add the voice again."
            )
        engine.prepare_voice(sample_path, conds_path, settings)

    chunks = text_utils.split_text(text, config.CHUNK_CHARS)
    pieces = []
    for i, chunk in enumerate(chunks):
        if on_progress:
            on_progress(i, len(chunks))
        pieces.append(engine.synthesize(
            chunk, language_info["language_id"], settings, conds_path=conds_path
        ))
    audio = audio_utils.join_chunks(pieces, engine.sample_rate, config.GAP_MS)

    wav_path, mp3_path = _next_output_paths(voice["id"])
    audio_utils.save_wav(wav_path, audio, engine.sample_rate)
    audio_utils.wav_to_mp3(wav_path, mp3_path, config.MP3_BITRATE)
    return {
        "wav": wav_path,
        "mp3": mp3_path,
        "seconds": round(audio_utils.seconds(audio, engine.sample_rate), 1),
        "chunks": len(chunks),
    }
