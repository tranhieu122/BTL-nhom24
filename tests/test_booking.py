"""Unit tests for BookingController — validation and filtering."""
from __future__ import annotations
import sys, os
import datetime as dt
import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "backend")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("DB_PATH", ":memory:")

from controllers.booking_controller import BookingController
from controllers.auth_controller import AuthController
from database.sqlite_db import get_connection


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user(role: str = "Sinh vien"):
    ctrl = AuthController()
    import uuid
    uname = "bk_" + uuid.uuid4().hex[:6]
    return ctrl.register("Test User", uname, f"{uname}@test.com",
                         "0901234567", "pass1234", role=role)


def _ensure_room(room_id: str) -> None:
    """Insert a test room if it doesn't already exist."""
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO rooms (id,name,capacity,room_type,equipment,status) VALUES (?,?,?,?,?,?)",
        (room_id, f"Phong {room_id}", 30, "Phong hoc", "", "Hoat dong"),
    )
    conn.commit()


# ── create_booking validation ─────────────────────────────────────────────────

class TestCreateBookingValidation:
    def test_past_date_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        past = (dt.date.today() - dt.timedelta(days=1)).isoformat()
        with pytest.raises(ValueError, match="da qua"):
            ctrl.create_booking(user, "R001", past, "Ca 1", "Hoc nhom")

    def test_too_far_future_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        far = (dt.date.today() + dt.timedelta(days=60)).isoformat()
        with pytest.raises(ValueError, match="trong vong"):
            ctrl.create_booking(user, "R001", far, "Ca 1", "Hoc nhom")

    def test_invalid_slot_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        with pytest.raises(ValueError, match="Ca hoc"):
            ctrl.create_booking(user, "R001", tomorrow, "Ca X", "Hoc nhom")

    def test_empty_purpose_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        with pytest.raises(ValueError):
            ctrl.create_booking(user, "R001", tomorrow, "Ca 1", "   ")

    def test_valid_booking_creates_record(self):
        _ensure_room("R001")
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        booking = ctrl.create_booking(user, "R001", tomorrow, "Ca 1", "Hoc nhom")
        assert booking.room_id == "R001"
        assert booking.status == "Cho duyet"
        assert booking.user_id == user.user_id


# ── list_bookings filter ──────────────────────────────────────────────────────

class TestListBookings:
    def test_non_admin_sees_only_own_bookings(self):
        _ensure_room("R002")
        _ensure_room("R003")
        user1 = _make_user()
        user2 = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        ctrl.create_booking(user1, "R002", tomorrow, "Ca 2", "Giang day")
        ctrl.create_booking(user2, "R003", tomorrow, "Ca 3", "Hoc bai")

        bookings = ctrl.list_bookings(current_user=user1, from_today=False)
        assert all(b.user_id == user1.user_id for b in bookings)

    def test_status_filter(self):
        _ensure_room("R004")
        user = _make_user(role="Admin")  # Admin bookings are auto-approved
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        b = ctrl.create_booking(user, "R004", tomorrow, "Ca 4", "Test")
        assert b.status == "Da duyet"

        approved = ctrl.list_bookings(status="Da duyet", from_today=False)
        assert any(x.booking_id == b.booking_id for x in approved)

    def test_available_slots_excludes_booked(self):
        _ensure_room("R005")
        user = _make_user(role="Admin")
        ctrl = BookingController()
        day = (dt.date.today() + dt.timedelta(days=2)).isoformat()
        ctrl.create_booking(user, "R005", day, "Ca 1", "Hoc")
        ctrl.create_booking(user, "R005", day, "Ca 2", "Hoc")
        slots = ctrl.available_slots("R005", day)
        assert "Ca 1" not in slots
        assert "Ca 2" not in slots
        assert "Ca 3" in slots
