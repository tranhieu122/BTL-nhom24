"""pytest configuration: inject an isolated in-memory SQLite DB for every test.

This replaces the singleton connection so tests never touch the real
classroom_booking.db file and can run without any installed dependencies
beyond pytest itself.
"""
from __future__ import annotations

import sqlite3
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

# ── Make src/back end importable ─────────────────────────────────────────────
BACKEND = Path(__file__).resolve().parents[1] / "src" / "back end"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


# ── Patch sqlite_db before any DAO/controller is imported ────────────────────

@pytest.fixture(autouse=True)
def isolated_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[sqlite3.Connection]:
    """Each test gets a fresh in-memory SQLite database."""
    import database.sqlite_db as db_mod  # type: ignore[import-not-found]
    db_module: Any = db_mod

    # Re-use the same schema SQL already defined in the module
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(str(getattr(db_module, "_SCHEMA", "")))
    conn.commit()

    # Apply all migrations against the in-memory db
    from database.migrations import run_migrations  # type: ignore[import-not-found]
    run_migrations(conn)

    # Reset singleton so next call to get_connection() returns our fresh db
    monkeypatch.setattr(db_module, "_conn", conn)

    yield conn

    conn.close()
    monkeypatch.setattr(db_module, "_conn", None)
