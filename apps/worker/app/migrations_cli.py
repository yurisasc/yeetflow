from __future__ import annotations

import sys
from pathlib import Path

from alembic.config import main as alembic_main

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def _run(*args: str) -> int:
    argv = ["-c", str(ALEMBIC_INI), *args]
    return alembic_main(argv=argv)


def upgrade_main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 else "head"
    return _run("upgrade", rev)


def downgrade_main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 else "-1"
    return _run("downgrade", rev)


def current_main() -> int:
    return _run("current")


def history_main() -> int:
    return _run("history")


def revision_main() -> int:
    # Usage: db-revision -m "message" [--autogenerate]
    args = sys.argv[1:]
    if "-m" not in args:
        return 2
    return _run("revision", *args)
