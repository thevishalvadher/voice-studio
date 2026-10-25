"""Tests for core/text_utils.py (splitting text into pieces)."""

import unittest

from core import text_utils


class SplitSentencesTest(unittest.TestCase):

    def test_hindi_danda_and_english_marks(self):
        text = "भोला काका आए। उन्होंने कहा, चलो! Are you ready? Yes."
        self.assertEqual(
            text_utils.split_sentences(text),
            ["भोला काका आए।", "उन्होंने कहा, चलो!", "Are you ready?", "Yes."],
        )

    def test_closing_quote_stays_with_sentence(self):
        text = 'उन्होंने कहा, "आज बारिश होगी।" फिर वे चले गए।'
        self.assertEqual(
            text_utils.split_sentences(text),
            ['उन्होंने कहा, "आज बारिश होगी।"', "फिर वे चले गए।"],
        )

    def test_decimal_number_is_not_a_sentence_end(self):
        self.assertEqual(text_utils.split_sentences("It costs 3.5 rupees. Ok."),
                         ["It costs 3.5 rupees.", "Ok."])

    def test_text_without_end_mark(self):
        self.assertEqual(text_utils.split_sentences("  hello   there  "), ["hello there"])

    def test_empty(self):
        self.assertEqual(text_utils.split_sentences(""), [])
        self.assertEqual(text_utils.split_text("   "), [])


class SplitTextTest(unittest.TestCase):

    def test_short_text_is_one_chunk(self):
        self.assertEqual(text_utils.split_text("Hello. How are you?"), ["Hello. How are you?"])

    def test_long_paragraph_chunks_fit_and_end_at_sentences(self):
        sentence = "हमारे गाँव में एक बहुत पुराना बरगद का पेड़ था, जिसके नीचे सब बच्चे कहानियाँ सुनते थे।"
        text = " ".join([sentence] * 8)  # about 730 characters
        chunks = text_utils.split_text(text, max_chars=250)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 250)
            self.assertTrue(chunk.endswith("।"))
        # Nothing lost, nothing added.
        self.assertEqual(" ".join(chunks), text)

    def test_one_very_long_sentence_is_cut_at_commas_then_spaces(self):
        text = "one two three, " * 40 + "end."
        chunks = text_utils.split_text(text, max_chars=100)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 100)
        self.assertEqual(" ".join(chunks).split(), text.split())

    def test_giant_word_is_cut_by_force(self):
        chunks = text_utils.split_text("a" * 260, max_chars=100)
        self.assertEqual([len(c) for c in chunks], [100, 100, 60])


if __name__ == "__main__":
    unittest.main()
