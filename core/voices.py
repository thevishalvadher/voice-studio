"""
core/voices.py - save, list and load voices.

All voices are listed in Drive at voices/voices.json, and each voice has
its own folder voices/<id>/ with its cleaned sample and cached fingerprint.
"""

import json
import re
import shutil
from pathlib import Path

import config
import engines
from core import StudioError
from core import audio_utils

EMPTY_DB = {"version": 1, "voices": []}


def ensure_storage():
    """Create the Drive folders and an empty voices.json if they are missing."""
    config.voices_dir().mkdir(parents=True, exist_ok=True)
    config.outputs_dir().mkdir(parents=True, exist_ok=True)
    if not config.voices_json().exists():
        save_db(EMPTY_DB)


def load_db():
    """Read voices.json into a dict like {"version": 1, "voices": [...]}."""
    path = config.voices_json()
    if not path.exists():
        return {"version": 1, "voices": []}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise StudioError(
            f"voices.json is damaged and cannot be read ({path}). "
            "Open it in Drive and fix it, or delete it to start fresh."
        )


def save_db(db):
    """Write the dict back to voices.json (pretty, and keeps Hindi readable)."""
    path = config.voices_json()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def list_voices():
    """All saved voices (a list of dicts)."""
    return load_db()["voices"]


def get_voice(voice_id):
    """One voice by its id, e.g. "bhola_kaka"."""
    for voice in list_voices():
        if voice["id"] == voice_id:
            return voice
    raise StudioError(f"Voice '{voice_id}' was not found. Add it in the 'Add Voice' section first.")


def data_path(relative_path):
    """Turn a path saved in voices.json ("voices/x/conds.pt") into a full Drive path."""
    return Path(config.DATA_ROOT) / relative_path


def make_voice_id(name, taken_ids):
    """"Bhola Kaka" -> "bhola_kaka". Non-English names become "voice", "voice_2"…"""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "voice"
    voice_id, n = slug, 2
    while voice_id in taken_ids:
        voice_id = f"{slug}_{n}"
        n += 1
    return voice_id


def add_voice(name, language, audio_path, consent, transcript=""):
    """Check, clean and save a new voice. Returns its voices.json entry.

    Steps: check the form -> clean the sample (mono, trim, normalize, 10–30 s)
    -> save it to voices/<id>/ -> build and cache conds.pt -> update voices.json.
    """
    name = (name or "").strip()
    if not name:
        raise StudioError("Please type a name for the voice.")
    if not consent:
        raise StudioError(
            "Please tick the consent box. You need signed consent from this person "
            "before cloning their voice."
        )
    if not audio_path or not Path(audio_path).exists():
        raise StudioError("Please upload or record a voice sample first.")

    engine, language_info = engines.for_language(language)  # also blocks disabled languages

    ensure_storage()
    db = load_db()
    if any(v["name"].lower() == name.lower() for v in db["voices"]):
        raise StudioError(f"A voice called '{name}' already exists. Please use a different name.")

    voice_id = make_voice_id(name, {v["id"] for v in db["voices"]})
    folder = config.voices_dir() / voice_id
    folder.mkdir(parents=True, exist_ok=True)
    settings = dict(config.DEFAULT_SETTINGS)

    try:
        # Keep the original upload too, in case you want to re-clean it later.
        shutil.copy(audio_path, folder / f"sample_original{Path(audio_path).suffix.lower()}")
        sample_seconds = audio_utils.clean_sample(audio_path, folder / "sample_clean.wav")
        # Build the voice "fingerprint" once and cache it (used for every generation).
        engine.prepare_voice(folder / "sample_clean.wav", folder / "conds.pt", settings)
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)  # don't leave half-saved voices behind
        raise

    voice = {
        "id": voice_id,
        "name": name,
        "language": language,
        "engine": language_info["engine"],
        "sample_file": f"voices/{voice_id}/sample_clean.wav",
        "sample_seconds": sample_seconds,
        "transcript": transcript,
        "conds_file": f"voices/{voice_id}/conds.pt",
        "consent_confirmed": True,
        "settings": settings,
        "created_at": config.now().isoformat(timespec="seconds"),
    }
    db["voices"].append(voice)
    save_db(db)
    return voice
