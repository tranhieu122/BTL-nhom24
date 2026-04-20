"""Input validation helpers."""
from __future__ import annotations
import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_PATTERN  = re.compile(r"^(0\d{9}|\+84\d{9})$")
ROOM_PATTERN   = re.compile(r"^[A-Z]\d{3}$")

def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value.strip()))

def is_valid_phone(value: str) -> bool:
    return bool(PHONE_PATTERN.match(value.strip()))

def is_valid_room_code(value: str) -> bool:
    return bool(ROOM_PATTERN.match(value.strip().upper()))
