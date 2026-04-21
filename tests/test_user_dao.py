"""Unit tests for UserDAO."""
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false
from __future__ import annotations

import pytest
from typing import Any

from dao.user_dao import UserDAO  # type: ignore[import-not-found]
from models.user import User  # type: ignore[import-not-found]


def _make_user(**overrides: Any) -> Any:
    base: dict[str, Any] = dict(
        user_id="T001",
        username="testuser",
        full_name="Test User",
        role="Sinh vien",
        email="test@example.com",
        phone="0901234567",
        password_hash="hashed",
        status="Hoat dong",
    )
    base.update(overrides)
    return User(**base)


class TestUserDAO:
    def test_save_and_find_by_id(self):
        dao = UserDAO()
        u = _make_user()
        dao.save(u)
        found = dao.find_by_id("T001")
        assert found is not None
        assert found.username == "testuser"
        assert found.email == "test@example.com"

    def test_find_by_username(self):
        dao = UserDAO()
        dao.save(_make_user())
        assert dao.find_by_username("testuser") is not None
        assert dao.find_by_username("noexist") is None

    def test_find_by_email_case_insensitive(self):
        dao = UserDAO()
        dao.save(_make_user(email="Test@Example.COM"))
        assert dao.find_by_email("test@example.com") is not None
        assert dao.find_by_email("TEST@EXAMPLE.COM") is not None

    def test_list_all(self):
        dao = UserDAO()
        dao.save(_make_user(user_id="T001", username="u1", email="u1@x.com"))
        dao.save(_make_user(user_id="T002", username="u2", email="u2@x.com"))
        all_users = dao.list_all()
        assert len(all_users) == 2

    def test_delete(self):
        dao = UserDAO()
        dao.save(_make_user())
        dao.delete("T001")
        assert dao.find_by_id("T001") is None

    def test_save_updates_existing(self):
        dao = UserDAO()
        u = _make_user()
        dao.save(u)
        u.full_name = "Updated Name"
        dao.save(u)
        found = dao.find_by_id("T001")
        assert found.full_name == "Updated Name"

    def test_unique_email_constraint(self):
        """DB should reject two users with the same email."""
        import sqlite3
        dao = UserDAO()
        dao.save(_make_user(user_id="T001", username="u1", email="dup@x.com"))
        with pytest.raises(sqlite3.IntegrityError):
            dao.save(_make_user(user_id="T002", username="u2", email="dup@x.com"))
