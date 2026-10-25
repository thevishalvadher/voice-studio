"""
config.py - all the settings for Muskaanpur Voice Studio in one place.

Think of this like a CSS variables file: change a number here and the
whole app uses the new value.
"""

import json
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Where things live
# ---------------------------------------------------------------------------

# Folder that holds this code (the cloned GitHub repo).
CODE_DIR = Path(__file__).resolve().parent

# Folder in Google Drive that holds your voices and audio outputs.
# (Tests change this to a temporary folder, so they never touch Drive.)
DATA_ROOT = Path("/content/drive/MyDrive/MuskaanpurVoiceStudio")

# Temporary folder for uploads/recordings before they are saved as a voice.
TEMP_DIR = Path("/content/mvs_temp")

LANGUAGES_FILE = CODE_DIR / "languages.json"


def voices_dir():
    """Drive folder with one sub-folder per voice: voices/<id>/"""
    return Path(DATA_ROOT) / "voices"


def voices_json():
    """The list of saved voices: voices/voices.json"""
    return voices_dir() / "voices.json"


def outputs_dir():
    """Drive folder for generated audio: outputs/<date>/"""
    return Path(DATA_ROOT) / "outputs"


# ---------------------------------------------------------------------------
# Voice sample rules
# ---------------------------------------------------------------------------

MIN_SAMPLE_SECONDS = 10   # shorter samples clone badly
MAX_SAMPLE_SECONDS = 30   # longer samples do not help and slow things down
SAMPLE_RATE = 24000       # Chatterbox works at 24,000 samples per second

# Settings every new voice starts with (saved into voices.json).
DEFAULT_SETTINGS = {
    "exaggeration": 0.5,  # "expression": 0.5 = normal, higher = more dramatic
    "cfg_weight": 0.5,    # how closely to follow the voice sample
    "temperature": 0.8,   # randomness; lower = flatter, higher = livelier
    "seed": 1234,         # fixed seed = the same line sounds the same every time
}

# ---------------------------------------------------------------------------
# Generation rules
# ---------------------------------------------------------------------------

CHUNK_CHARS = 250         # long text is cut into pieces of about this size
GAP_MS = 150              # silence between pieces, in milliseconds
MP3_BITRATE = "192k"      # MP3 quality
MAX_TEXT_CHARS = 3000     # keeps one job short enough for free Colab

# Dates in folder names use Indian time.
TIMEZONE = "Asia/Kolkata"


def now():
    """Current date and time in Indian time (falls back to the computer's clock)."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(TIMEZONE))
    except Exception:
        return datetime.now().astimezone()


# ---------------------------------------------------------------------------
# Languages (read from languages.json)
# ---------------------------------------------------------------------------

def load_languages():
    """Return the whole languages.json as a dict, e.g. {"hi": {...}, "en": {...}}."""
    with open(LANGUAGES_FILE, encoding="utf-8") as f:
        return json.load(f)


def enabled_languages():
    """Only the languages you can use right now (enabled = true)."""
    return {code: info for code, info in load_languages().items() if info.get("enabled")}


def disabled_languages():
    """Languages that exist but are switched off (e.g. Gujarati)."""
    return {code: info for code, info in load_languages().items() if not info.get("enabled")}
