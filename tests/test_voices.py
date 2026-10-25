"""Tests for core/voices.py (saving and loading voices) and languages.json."""

import json
import unittest

import config
import engines
from core import StudioError, voices
from tests.helpers import StudioTestCase, make_tone

ENTRY_KEYS = {
    "id", "name", "language", "engine", "sample_file", "sample_seconds", "transcript",
    "conds_file", "consent_confirmed", "settings", "created_at",
}


class StorageTest(StudioTestCase):

    def test_ensure_storage_creates_folders_and_empty_json(self):
        voices.ensure_storage()
        self.assertTrue(config.voices_dir().is_dir())
        self.assertTrue(config.outputs_dir().is_dir())
        self.assertEqual(json.loads(config.voices_json().read_text()), {"version": 1, "voices": []})

    def test_damaged_json_gives_plain_message(self):
        voices.ensure_storage()
        config.voices_json().write_text("{oops")
        with self.assertRaises(StudioError) as caught:
            voices.list_voices()
        self.assertIn("voices.json is damaged", str(caught.exception))

    def test_make_voice_id(self):
        self.assertEqual(voices.make_voice_id("Bhola Kaka", set()), "bhola_kaka")
        self.assertEqual(voices.make_voice_id("Bhola Kaka", {"bhola_kaka"}), "bhola_kaka_2")
        self.assertEqual(voices.make_voice_id("भोला काका", set()), "voice")
        self.assertEqual(voices.make_voice_id("कमला", {"voice"}), "voice_2")


class AddVoiceTest(StudioTestCase):

    def setUp(self):
        super().setUp()
        self.sample = make_tone(self.tmp / "sample.wav", seconds=14)

    def test_add_voice_saves_everything(self):
        voice = voices.add_voice("Bhola Kaka", "hi", self.sample, consent=True)

        self.assertEqual(set(voice), ENTRY_KEYS)
        self.assertEqual(voice["id"], "bhola_kaka")
        self.assertEqual(voice["engine"], "chatterbox_mtl")
        self.assertEqual(voice["sample_file"], "voices/bhola_kaka/sample_clean.wav")
        self.assertEqual(voice["conds_file"], "voices/bhola_kaka/conds.pt")
        self.assertTrue(voice["consent_confirmed"])
        self.assertEqual(voice["settings"], {"exaggeration": 0.5, "cfg_weight": 0.5,
                                             "temperature": 0.8, "seed": 1234})
        self.assertAlmostEqual(voice["sample_seconds"], 14, delta=0.3)

        folder = config.voices_dir() / "bhola_kaka"
        self.assertTrue((folder / "sample_clean.wav").exists())
        self.assertTrue((folder / "sample_original.wav").exists())
        self.assertTrue((folder / "conds.pt").exists())       # fingerprint cached once
        self.assertEqual(len(self.engine.prepared), 1)

    def test_voice_survives_a_restart(self):
        voices.add_voice("Kamla Kaki", "en", self.sample, consent=True)
        # A Colab restart wipes memory but not Drive: read everything fresh from disk.
        db = json.loads(config.voices_json().read_text(encoding="utf-8"))
        self.assertEqual([v["id"] for v in db["voices"]], ["kamla_kaki"])
        self.assertEqual(voices.get_voice("kamla_kaki")["name"], "Kamla Kaki")

    def test_consent_is_required(self):
        with self.assertRaises(StudioError) as caught:
            voices.add_voice("Bhola Kaka", "hi", self.sample, consent=False)
        self.assertIn("consent", str(caught.exception))
        self.assertEqual(voices.list_voices(), [])

    def test_name_is_required(self):
        with self.assertRaises(StudioError):
            voices.add_voice("   ", "hi", self.sample, consent=True)

    def test_sample_is_required(self):
        with self.assertRaises(StudioError) as caught:
            voices.add_voice("Bhola Kaka", "hi", None, consent=True)
        self.assertIn("upload or record", str(caught.exception))

    def test_gujarati_is_coming_soon(self):
        with self.assertRaises(StudioError) as caught:
            voices.add_voice("Bhola Kaka", "gu", self.sample, consent=True)
        self.assertEqual(str(caught.exception), "Gujarati is coming soon (Blocked: licence).")

    def test_duplicate_name(self):
        voices.add_voice("Bhola Kaka", "hi", self.sample, consent=True)
        with self.assertRaises(StudioError):
            voices.add_voice("bhola kaka", "en", self.sample, consent=True)

    def test_bad_sample_leaves_nothing_behind(self):
        short = make_tone(self.tmp / "short.wav", seconds=5)
        with self.assertRaises(StudioError):
            voices.add_voice("Bhola Kaka", "hi", short, consent=True)
        self.assertFalse((config.voices_dir() / "bhola_kaka").exists())
        self.assertEqual(voices.list_voices(), [])

    def test_unknown_voice(self):
        with self.assertRaises(StudioError):
            voices.get_voice("nobody")


class LanguagesFileTest(unittest.TestCase):

    def test_hindi_and_english_enabled_gujarati_blocked(self):
        languages = config.load_languages()
        for code in ("hi", "en"):
            self.assertTrue(languages[code]["enabled"])
            self.assertEqual(languages[code]["engine"], "chatterbox_mtl")
            self.assertEqual(languages[code]["language_id"], code)
        self.assertFalse(languages["gu"]["enabled"])
        self.assertEqual(languages["gu"]["note"], "Blocked: licence")
        self.assertEqual(set(config.enabled_languages()), {"hi", "en"})

    def test_every_enabled_engine_exists(self):
        for info in config.enabled_languages().values():
            self.assertIn(info["engine"], engines.ENGINE_CLASSES)

    def test_test_sentences_file(self):
        with open(config.CODE_DIR / "tests" / "test_sentences.json", encoding="utf-8") as f:
            sentences = json.load(f)
        self.assertEqual(len(sentences["hi"]), 3)
        self.assertEqual(len(sentences["en"]), 3)


if __name__ == "__main__":
    unittest.main()
