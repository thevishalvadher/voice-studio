"""Tests for core/audio_utils.py (cleaning samples, joining, MP3)."""

import shutil
import subprocess
import unittest

import numpy as np
import soundfile as sf

from core import StudioError, audio_utils
from tests.helpers import StudioTestCase, make_tone

HAS_FFMPEG = shutil.which("ffmpeg") is not None


class CleanSampleTest(StudioTestCase):

    def test_good_sample_becomes_mono_24k_trimmed_and_normalized(self):
        src = make_tone(self.tmp / "in.wav", seconds=15, sample_rate=44100, channels=2, silence=2)
        out = self.tmp / "clean.wav"
        length = audio_utils.clean_sample(src, out)

        info = sf.info(str(out))
        self.assertEqual(info.channels, 1)
        self.assertEqual(info.samplerate, 24000)
        # 2 s of silence on each side was trimmed (only ~0.1 s padding kept).
        self.assertAlmostEqual(length, 15.2, delta=0.15)
        audio, _ = sf.read(str(out))
        self.assertLessEqual(np.max(np.abs(audio)), 0.951)

    def test_too_short_message(self):
        src = make_tone(self.tmp / "short.wav", seconds=6)
        with self.assertRaises(StudioError) as caught:
            audio_utils.clean_sample(src, self.tmp / "out.wav")
        self.assertEqual(str(caught.exception), "Sample too short (6 s). Need at least 10 s.")

    def test_silence_does_not_count_towards_length(self):
        src = make_tone(self.tmp / "padded.wav", seconds=6, silence=5)  # 16 s file, 6 s voice
        with self.assertRaises(StudioError) as caught:
            audio_utils.clean_sample(src, self.tmp / "out.wav")
        self.assertIn("Sample too short", str(caught.exception))

    def test_too_long_message(self):
        src = make_tone(self.tmp / "long.wav", seconds=40, sample_rate=16000, channels=1)
        with self.assertRaises(StudioError) as caught:
            audio_utils.clean_sample(src, self.tmp / "out.wav")
        self.assertEqual(str(caught.exception), "Sample too long (40 s). Please use 30 s or less.")

    def test_silent_sample(self):
        audio_utils.save_wav(self.tmp / "silent.wav", np.zeros(24000 * 15), 24000)
        with self.assertRaises(StudioError) as caught:
            audio_utils.clean_sample(self.tmp / "silent.wav", self.tmp / "out.wav")
        self.assertIn("could not hear any voice", str(caught.exception))

    def test_unreadable_file(self):
        bad = self.tmp / "notes.wav"
        bad.write_text("this is not audio")
        with self.assertRaises(StudioError) as caught:
            audio_utils.clean_sample(bad, self.tmp / "out.wav")
        self.assertIn("Could not read this audio file", str(caught.exception))

    @unittest.skipUnless(HAS_FFMPEG, "needs ffmpeg")
    def test_browser_recording_format_webm(self):
        wav = make_tone(self.tmp / "rec.wav", seconds=12)
        webm = self.tmp / "recording.webm"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), str(webm)], check=True)
        self.assertAlmostEqual(audio_utils.clean_sample(webm, self.tmp / "out.wav"), 12, delta=0.3)


class SmallHelpersTest(StudioTestCase):

    def test_format_seconds(self):
        self.assertEqual(audio_utils.format_seconds(6.0), "6")
        self.assertEqual(audio_utils.format_seconds(9.64), "9.6")

    def test_join_chunks_adds_150ms_gaps(self):
        a = np.ones(1000, dtype=np.float32)
        joined = audio_utils.join_chunks([a, a, a], 24000, gap_ms=150)
        self.assertEqual(len(joined), 3000 + 2 * 3600)  # 150 ms at 24 kHz = 3600 samples
        self.assertTrue(np.all(joined[1000:4600] == 0))

    def test_join_nothing(self):
        self.assertEqual(len(audio_utils.join_chunks([], 24000)), 0)

    @unittest.skipUnless(HAS_FFMPEG, "needs ffmpeg")
    def test_mp3_is_192kbps(self):
        wav = self.tmp / "a.wav"
        audio_utils.save_wav(wav, 0.2 * np.sin(np.arange(24000 * 5) / 7), 24000)
        mp3 = self.tmp / "a.mp3"
        audio_utils.wav_to_mp3(wav, mp3)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=bit_rate", "-of", "csv=p=0", str(mp3)],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(probe.stdout.strip(), "192000")


if __name__ == "__main__":
    unittest.main()
