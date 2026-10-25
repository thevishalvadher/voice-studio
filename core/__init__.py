"""core - the "business logic": voices, audio cleaning, text splitting, generation."""


class StudioError(Exception):
    """A problem we can explain in plain English (shown to you in the notebook).

    Example: raise StudioError("Sample too short (6 s). Need at least 10 s.")
    """
