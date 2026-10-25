"""
engines/base.py - the "shape" every TTS engine must have.

Like an interface in TypeScript: any engine (Chatterbox today, maybe a
Gujarati model later) must provide these methods. The rest of the app only
talks to this shape, so swapping engines never touches the UI.
"""


class Engine:
    # Short name used in languages.json, e.g. "chatterbox_mtl".
    name = "base"

    # Does this engine need a written transcript of the voice sample?
    needs_transcript = False

    # Audio sample rate this engine produces (samples per second).
    sample_rate = 24000

    def load(self):
        """Load the model into memory. Must be safe to call many times
        (only the first call does real work)."""
        raise NotImplementedError

    def prepare_voice(self, sample_path, conds_path, settings):
        """Study a clean voice sample once and save the result
        (the voice "fingerprint") to conds_path, e.g. voices/<id>/conds.pt."""
        raise NotImplementedError

    def synthesize(self, text, language_id, settings, conds_path=None, sample_path=None):
        """Speak one short piece of text.

        - conds_path: a saved voice fingerprint (normal use).
        - sample_path: a raw audio file instead (quick tests).
        - neither: the engine's built-in demo voice.

        Returns a 1-D numpy float32 array of audio at self.sample_rate.
        """
        raise NotImplementedError
