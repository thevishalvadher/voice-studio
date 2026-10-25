"""
core/text_utils.py - cut long text into small pieces the model can speak well.

The model is best with short inputs, so we cut at sentence ends
(। . ? !) and pack sentences into pieces of about 250 characters.
"""

import re

import config

SENTENCE_ENDS = "।॥.?!"          # Hindi danda, double danda, full stop, ?, !
CLOSING_MARKS = "\"'”’)]»"       # quotes/brackets that can follow a sentence end


def clean_text(text):
    """Turn runs of spaces/new lines into single spaces."""
    return " ".join((text or "").split())


def split_sentences(text):
    """"Hello. How are you?" -> ["Hello.", "How are you?"]

    A full stop only ends a sentence when a space follows, so "3.5" stays whole.
    The Hindi danda (।) always ends a sentence.
    """
    text = clean_text(text)
    sentences, current, i = [], "", 0
    while i < len(text):
        char = text[i]
        current += char
        i += 1
        if char in SENTENCE_ENDS:
            # Keep extra marks and closing quotes with this sentence: "Wow!!" / "होगी।"
            while i < len(text) and (text[i] in SENTENCE_ENDS or text[i] in CLOSING_MARKS):
                current += text[i]
                i += 1
            if char in "।॥" or i >= len(text) or text[i] == " ":
                sentences.append(current.strip())
                current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences


def _pack(pieces, max_chars, joiner=" "):
    """Join small pieces together while they fit under max_chars."""
    chunks, current = [], ""
    for piece in pieces:
        candidate = f"{current}{joiner}{piece}" if current else piece
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = piece
    if current:
        chunks.append(current)
    return chunks


def _split_long_sentence(sentence, max_chars):
    """A single sentence that is too long: cut at commas, then at spaces."""
    parts = [p.strip() for p in re.split(r"(?<=[,،;:])\s+", sentence) if p.strip()]
    pieces = []
    for part in parts:
        if len(part) <= max_chars:
            pieces.append(part)
        else:
            words = part.split(" ")
            # A "word" longer than max_chars (very rare) is cut by force.
            for word in words:
                while len(word) > max_chars:
                    pieces.append(word[:max_chars])
                    word = word[max_chars:]
                if word:
                    pieces.append(word)
    return _pack(pieces, max_chars)


def split_text(text, max_chars=config.CHUNK_CHARS):
    """Split text into chunks of at most max_chars, cutting at sentence ends."""
    pieces = []
    for sentence in split_sentences(text):
        if len(sentence) <= max_chars:
            pieces.append(sentence)
        else:
            pieces.extend(_split_long_sentence(sentence, max_chars))
    return _pack(pieces, max_chars)
