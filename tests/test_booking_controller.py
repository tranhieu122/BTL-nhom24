"""Unit tests for BookingController."""
from __future__ import annotations

import pytest
from controllers.auth_controller import AuthController
from controllers.booking_controller import BookingController
from controllers.room_controller import RoomController
from dao.room_dao import RoomDAO
from models.room import Room
from models.user import User


def _setup() -> tuple[BookingController, RoomController, User]:
    """Create controllers and a test user + room."""
    auth = AuthController()
    user = auth.register("Test User", "testbc", "bc@test.com",
                         "0901234567", "pass123")
    RoomDAO().save(Room("R01", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))
    return BookingController(), RoomController(), user


class TestBookingController:
    def test_create_booking(self):
        bc, rc, user = _setup()
        b = bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Hoc nhom")
        assert b.room_id == "R01"
        assert b.status == "Cho duyet"

    def test_create_booking_admin_auto_approved(self):
        auth = AuthController()
        admin = auth.register("Admin", "adminbc", "adminbc@test.com",
                              "0901234568", "pass123", role="Admin")
        admin.role = "Admin"
        auth.user_dao.save(admin)
        RoomDAO().save(Room("R01", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))
        bc = BookingController()
        b = bc.create_booking(admin, "R01", "2026-05-01", "Ca 1", "Admin test")
        assert b.status == "Da duyet"

    def test_create_booking_invalid_date(self):
        bc, rc, user = _setup()
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            bc.create_booking(user, "R01", "not-a-date", "Ca 1", "Test")

    def test_create_booking_empty_purpose(self):
        bc, rc, user = _setup()
        with pytest.raises(ValueError, match="Muc dich"):
            bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "  ")

    def test_create_booking_invalid_slot(self):
        bc, rc, user = _setup()
        with pytest.raises(ValueError, match="Ca hoc"):
            bc.create_booking(user, "R01", "2026-05-01", "Ca 99", "Test")

    def test_create_booking_no_room(self):
        bc, rc, user = _setup()
        with pytest.raises(ValueError, match="chon phong"):
            bc.create_booking(user, "", "2026-05-01", "Ca 1", "Test")

    def test_conflict_detection(self):
        bc, rc, user = _setup()
        bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "First")
        with pytest.raises(ValueError, match="da co lich"):
            bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Second")

    def test_available_slots(self):
        bc, rc, user = _setup()
        bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Test")
        avail = bc.available_slots("R01", "2026-05-01")
        assert "Ca 1" not in avail
        assert "Ca 2" in avail

    def test_update_status(self):
        bc, rc, user = _setup()
        b = bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Test")
        updated = bc.update_status(b.booking_id, "Da duyet")
        assert updated.status == "Da duyet"

    def test_update_status_invalid(self):
        bc, rc, user = _setup()
        b = bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Test")
        with pytest.raises(ValueError, match="khong hop le"):
            bc.update_status(b.booking_id, "Trang thai la")

    def test_delete_booking_owner(self):
        bc, rc, user = _setup()
        b = bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Test")
        bc.delete_booking(b.booking_id, user)
        assert bc.booking_dao.find_by_id(b.booking_id) is None

    def test_delete_booking_other_user_denied(self):
        bc, rc, user = _setup()
        b = bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Test")
        other = User("U99", "other", "Other", "Sinh vien",
                     "o@x.com", "0900000000", "h", "Hoat dong")
        with pytest.raises(PermissionError):
            bc.delete_booking(b.booking_id, other)

    def test_suggest_alternatives(self):
        bc, rc, user = _setup()
        RoomDAO().save(Room("R02", "Phong 202", 30, "Phong hoc", "", "Hoat dong"))
        bc.create_booking(user, "R01", "2026-05-01", "Ca 1", "Test")
        suggestions = bc.suggest_alternatives("R01", "2026-05-01", "Ca 1",
                                              ["R01", "R02"])
        assert len(suggestions["other_rooms"]) >= 1
        assert any(r[0] == "R02" for r in suggestions["other_rooms"])
