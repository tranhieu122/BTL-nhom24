"""Unit tests for input validators."""
from __future__ import annotations

from utils.validators import is_valid_email, is_valid_phone, is_valid_room_code


class TestEmailValidator:
    def test_valid_emails(self):
        assert is_valid_email("user@example.com")
        assert is_valid_email("a.b+c@domain.co")
        assert is_valid_email("test@sub.domain.org")

    def test_invalid_emails(self):
        assert not is_valid_email("")
        assert not is_valid_email("no-at-sign")
        assert not is_valid_email("@domain.com")
        assert not is_valid_email("user@")
        assert not is_valid_email("user@.com")


class TestPhoneValidator:
    def test_valid_phones(self):
        assert is_valid_phone("0901234567")
        assert is_valid_phone("+84901234567")

    def test_invalid_phones(self):
        assert not is_valid_phone("")
        assert not is_valid_phone("123456")
        assert not is_valid_phone("090123456")  # 9 digits
        assert not is_valid_phone("09012345678")  # 11 digits
        assert not is_valid_phone("abc")


class TestRoomCodeValidator:
    def test_valid_codes(self):
        assert is_valid_room_code("P101")
        assert is_valid_room_code("L202")
        assert is_valid_room_code("H305")

    def test_invalid_codes(self):
        assert not is_valid_room_code("")
        assert not is_valid_room_code("101")
        assert not is_valid_room_code("PP01")
        assert not is_valid_room_code("P10")
