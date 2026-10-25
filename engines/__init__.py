"""
engines - a small registry that turns a name from languages.json
(e.g. "chatterbox_mtl") into a ready-to-use engine object.

To add a new engine later:
  1. create engines/my_engine.py with a class that follows engines/base.py
  2. add one line to ENGINE_CLASSES below
  3. point a language at it in languages.json
"""

import importlib

# name in languages.json  ->  "python.module:ClassName"
# (Imported only when needed, so tests can run without a GPU or torch.)
ENGINE_CLASSES = {
    "chatterbox_mtl": "engines.chatterbox_mtl:ChatterboxMtlEngine",
}

# Engines that are already created. Each model is loaded ONCE and reused.
_loaded = {}


def register_engine(name, engine):
    """Use a ready-made engine object for this name (tests use a fake engine)."""
    _loaded[name] = engine


def get_engine(name):
    """Return the engine for this name, creating it the first time."""
    if name in _loaded:
        return _loaded[name]
    if name not in ENGINE_CLASSES:
        from core import StudioError
        raise StudioError(f"Unknown engine '{name}'. Check languages.json.")
    module_name, class_name = ENGINE_CLASSES[name].split(":")
    module = importlib.import_module(module_name)
    engine = getattr(module, class_name)()
    _loaded[name] = engine
    return engine
