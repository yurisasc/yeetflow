"""Helpers for working with Passlib while suppressing deprecation noise."""

from __future__ import annotations

import warnings
from functools import lru_cache


def configure_passlib_warnings() -> None:
    """Apply warning filters required when importing passlib."""

    warnings.filterwarnings(
        "ignore",
        message="'crypt' is deprecated and slated for removal in Python 3.13",
        category=DeprecationWarning,
    )


@lru_cache(maxsize=1)
def get_passlib_context():
    """Return a configured ``CryptContext`` instance."""
    configure_passlib_warnings()
    from passlib.context import CryptContext  # noqa: PLC0415, RUF100

    return CryptContext(schemes=["bcrypt"], deprecated="auto")
