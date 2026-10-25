"""Smoke test: the notebook sections build without errors (outside Colab)."""

import importlib.util
import unittest

from tests.helpers import StudioTestCase

HAS_WIDGETS = importlib.util.find_spec("ipywidgets") is not None


@unittest.skipUnless(HAS_WIDGETS, "needs ipywidgets")
class NotebookUiTest(StudioTestCase):

    def test_sections_build(self):
        from ui import notebook_ui

        notebook_ui.setup()
        self.assertTrue(self.engine.loaded)  # model loaded during Setup
        notebook_ui.show_add_voice()
        notebook_ui.show_generate()

    def test_friendly_error_messages(self):
        from ui.notebook_ui import _friendly_error

        self.assertIn("GPU ran out of memory", _friendly_error(RuntimeError("CUDA out of memory")))
        self.assertIn("Drive got disconnected",
                      _friendly_error(OSError("Transport endpoint is not connected")))


if __name__ == "__main__":
    unittest.main()
