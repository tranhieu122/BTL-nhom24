"""Shared pytest fixtures and configuration."""
from __future__ import annotations
import os
import sys
import pytest # type: ignore

# Force in-memory SQLite for all tests BEFORE importing any app module
os.environ["DB_PATH"] = ":memory:"

# Make sure back-end code is importable
_backend = os.path.join(os.path.dirname(__file__), "..", "src", "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)


@pytest.fixture(autouse=True) # type: ignore
def _fresh_db(): # type: ignore
    """Reset the DB singleton before every test so each test gets a clean DB."""
    from database import sqlite_db
    sqlite_db._reset_for_testing() # type: ignore
    yield
    sqlite_db._reset_for_testing() # type: ignore
