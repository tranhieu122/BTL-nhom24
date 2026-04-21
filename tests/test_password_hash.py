"""Unit tests for password hashing (PBKDF2 + legacy SHA-256)."""
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false
from __future__ import annotations

from utils.password_hash import hash_password, verify_password, sha256_hash  # type: ignore[import-not-found]


class TestPasswordHash:
    def test_hash_produces_pbkdf2_format(self):
        h = hash_password("secret")
        assert h.startswith("pbkdf2:")
        parts = h.split(":")
        assert len(parts) == 4

    def test_verify_pbkdf2_correct(self):
        h = hash_password("my_password")
        assert verify_password("my_password", h) is True

    def test_verify_pbkdf2_wrong(self):
        h = hash_password("correct")
        assert verify_password("wrong", h) is False

    def test_different_hashes_each_time(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # different salts

    def test_verify_legacy_sha256(self):
        legacy = sha256_hash("legacy_pass")
        assert verify_password("legacy_pass", legacy) is True
        assert verify_password("wrong", legacy) is False

    def test_sha256_hash_deterministic(self):
        assert sha256_hash("abc") == sha256_hash("abc")
        assert sha256_hash("abc") != sha256_hash("xyz")
