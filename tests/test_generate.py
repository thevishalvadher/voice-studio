"""Tests for core/generate.py (text -> WAV + MP3), using the fake engine."""

import shutil
import unittest

import numpy as np
import soundfile as sf

import config
from core import StudioError, generate, voices
from tests.helpers import SAMPLE_RATE, StudioTestCase, make_tone

HAS_FFMPEG = shutil.which("ffmpeg") is not None


@unittest.skipUnless(HAS_FFMPEG, "needs ffmpeg for MP3")
class GenerateTest(StudioTestCase):

    def setUp(self):
        super().setUp()
        self.voice = voices.add_voice("Bhola Kaka", "hi", make_tone(self.tmp / "s.wav", 12), True)
        self.engine.calls.clear()

    def test_files_are_saved_with_date_and_number(self):
        first = generate.generate("bhola_kaka", "नमस्ते।")
        second = generate.generate("bhola_kaka", "फिर मिलेंगे।")
        today = config.now().strftime("%Y-%m-%d")
        self.assertEqual(first["wav"], config.outputs_dir() / today / "bhola_kaka_0001.wav")
        self.assertEqual(first["mp3"], config.outputs_dir() / today / "bhola_kaka_0001.mp3")
        self.assertEqual(second["wav"].name, "bhola_kaka_0002.wav")
        for result in (first, second):
            self.assertTrue(result["wav"].exists())
            self.assertTrue(result["mp3"].exists())

    def test_long_text_is_split_and_joined_with_gaps(self):
        sentence = "मुस्कानपुर गाँव में एक बहुत पुराना बरगद का पेड़ था, जिसके नीचे सब बच्चे कहानियाँ सुनते थे।"
        text = " ".join([sentence] * 7)  # about 640 characters
        result = generate.generate("bhola_kaka", text)

        self.assertEqual(result["chunks"], len(self.engine.calls))
        self.assertGreater(result["chunks"], 1)
        for call in self.engine.calls:
            self.assertLessEqual(len(call["text"]), config.CHUNK_CHARS)
            self.assertEqual(call["language_id"], "hi")

        # Final length = all pieces + one 150 ms gap between each pair.
        expected = sum(int(SAMPLE_RATE * 0.01 * len(c["text"])) for c in self.engine.calls)
        expected += (result["chunks"] - 1) * int(SAMPLE_RATE * 0.150)
        self.assertEqual(sf.info(str(result["wav"])).frames, expected)

    def test_always_uses_cached_conds_and_voice_seed(self):
        generate.generate("bhola_kaka", "One. Two. " + "Three. " * 60)
        conds = voices.data_path(self.voice["conds_file"])
        for call in self.engine.calls:
            self.assertEqual(call["conds_path"], conds)
            self.assertIsNone(call["sample_path"])          # never the raw sample
            self.assertEqual(call["settings"]["seed"], 1234)
        self.assertEqual(len(self.engine.prepared), 1)      # fingerprint built only once

    def test_same_line_twice_gives_identical_audio(self):
        a = generate.generate("bhola_kaka", "आज बारिश ज़रूर होगी।")
        b = generate.generate("bhola_kaka", "आज बारिश ज़रूर होगी।")
        audio_a, _ = sf.read(str(a["wav"]))
        audio_b, _ = sf.read(str(b["wav"]))
        self.assertTrue(np.array_equal(audio_a, audio_b))

    def test_advanced_overrides_are_used_but_not_saved(self):
        generate.generate("bhola_kaka", "Hello.", exaggeration=1.2, seed=99)
        self.assertEqual(self.engine.calls[-1]["settings"]["exaggeration"], 1.2)
        self.assertEqual(self.engine.calls[-1]["settings"]["seed"], 99)
        self.assertEqual(voices.get_voice("bhola_kaka")["settings"]["seed"], 1234)

    def test_missing_conds_is_rebuilt_once(self):
        voices.data_path(self.voice["conds_file"]).unlink()
        generate.generate("bhola_kaka", "Hello.")
        self.assertTrue(voices.data_path(self.voice["conds_file"]).exists())
        self.assertEqual(len(self.engine.prepared), 2)

    def test_friendly_errors(self):
        with self.assertRaises(StudioError) as caught:
            generate.generate("bhola_kaka", "   ")
        self.assertEqual(str(caught.exception), "Please type some text first.")
        with self.assertRaises(StudioError) as caught:
            generate.generate("bhola_kaka", "a" * (config.MAX_TEXT_CHARS + 1))
        self.assertIn("Text too long", str(caught.exception))
        with self.assertRaises(StudioError):
            generate.generate("nobody", "Hello.")


class EngineTestLinesTest(StudioTestCase):

    def test_hindi_and_english_test_lines(self):
        paths = generate.generate_test_lines()
        self.assertEqual([p.name for p in paths], ["hi_test.wav", "en_test.wav"])
        self.assertTrue(all(p.exists() for p in paths))
        self.assertEqual([c["language_id"] for c in self.engine.calls], ["hi", "en"])
        self.assertEqual(self.engine.calls[0]["text"], generate.TEST_LINES["hi"])

    def test_missing_demo_sample(self):
        with self.assertRaises(StudioError):
            generate.generate_test_lines(self.tmp / "nope.wav")


if __name__ == "__main__":
    unittest.main()
