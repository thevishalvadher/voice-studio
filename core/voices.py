"""
core/voices.py - save, list and load voices.

All voices are listed in Drive at voices/voices.json, and each voice has
its own folder voices/<id>/ with its cleaned sample and cached fingerprint.
"""

import json

import config
from core import StudioError

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
