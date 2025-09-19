from __future__ import annotations

import sys
from pathlib import Path

from alembic.config import main as alembic_main

EXTRA_ARGS_THRESHOLD = 2
ERROR_MISSING_MESSAGE = 2

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def _run(*args: str) -> int:
    argv = ["-c", str(ALEMBIC_INI), *args]
    return alembic_main(argv=argv)


def upgrade_main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 else "head"
    extra = (
        sys.argv[EXTRA_ARGS_THRESHOLD:] if len(sys.argv) > EXTRA_ARGS_THRESHOLD else []
    )
    return _run("upgrade", rev, *extra)


def downgrade_main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 else "-1"
    extra = (
        sys.argv[EXTRA_ARGS_THRESHOLD:] if len(sys.argv) > EXTRA_ARGS_THRESHOLD else []
    )
    return _run("downgrade", rev, *extra)


def current_main() -> int:
    extra = (
        sys.argv[EXTRA_ARGS_THRESHOLD:] if len(sys.argv) > EXTRA_ARGS_THRESHOLD else []
    )
    return _run("current", *extra)


def history_main() -> int:
    return _run("history")


def revision_main() -> int:
    # Usage: db-revision -m "message" [--autogenerate]
    args = sys.argv[1:]
    if "-m" not in args:
        return ERROR_MISSING_MESSAGE
    return _run("revision", *args)
