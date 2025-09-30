"""Actions package: imports built-ins to ensure registration on import."""

from __future__ import annotations

import logging

# Trigger registration of built-in actions (side effects)
from . import builtin_actions as _builtin_actions  # noqa: F401
from .registry import known_actions

# Optional: log available actions once at import time
logging.getLogger(__name__).info("Registered actions: %s", known_actions())
