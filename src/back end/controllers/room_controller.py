"""Room management business logic."""
from __future__ import annotations
from typing import TYPE_CHECKING
from dao.room_dao import RoomDAO
from models.room import Room
from utils.validators import is_valid_room_code
from utils.logger import get_logger

if TYPE_CHECKING:
    from controllers.booking_controller import BookingController

_log = get_logger(__name__)


class RoomController:
    def __init__(self) -> None:
        self.room_dao = RoomDAO()

    # ── Queries ───────────────────────────────────────────────────────────────

    def list_rooms(self, keyword: str = "",
                   room_type: str = "", status: str = "") -> list[Room]:
        """Return rooms filtered by keyword, type and/or status."""
        rooms = self.room_dao.list_all()
        kw = keyword.strip().lower()
        if kw:
            rooms = [r for r in rooms if kw in r.room_id.lower()
                     or kw in r.name.lower() or kw in r.room_type.lower()]
        if room_type:
            rooms = [r for r in rooms if r.room_type == room_type]
        if status:
            rooms = [r for r in rooms if r.status == status]
        return rooms

    def get_room(self, room_id: str) -> Room | None:
        return self.room_dao.find_by_id(room_id)

    def list_room_types(self) -> list[str]:
        """Return a sorted unique list of room types present in the DB."""
        return sorted({r.room_type for r in self.room_dao.list_all() if r.room_type})

    def room_stats(self, booking_ctrl: "BookingController") -> list[dict]:
        """Return per-room dict with booking count for each room.

        Returns list of dicts:
            room_id, name, capacity, room_type, status, booking_count
        """
        all_bookings = booking_ctrl.booking_dao.list_all()
        count_map: dict[str, int] = {}
        for b in all_bookings:
            count_map[b.room_id] = count_map.get(b.room_id, 0) + 1
        result = []
        for r in self.room_dao.list_all():
            result.append({
                "room_id": r.room_id,
                "name": r.name,
                "capacity": r.capacity,
                "room_type": r.room_type,
                "status": r.status,
                "booking_count": count_map.get(r.room_id, 0),
            })
        return result

    # ── Mutations ─────────────────────────────────────────────────────────────

    def save_room(self, payload: dict[str, str]) -> Room:
        room_id = payload["room_id"].strip().upper()
        name    = payload["name"].strip()
        if not room_id or not is_valid_room_code(room_id):
            raise ValueError("Ma phong phai co dinh dang nhu P101.")
        if not name:
            raise ValueError("Ten phong khong duoc de trong.")
        try:
            capacity = int(payload["capacity"])
            if capacity <= 0:
                raise ValueError
        except (ValueError, KeyError):
            raise ValueError("Suc chua phai la so nguyen duong.")
        room = Room(
            room_id=room_id,
            name=name,
            capacity=capacity,
            room_type=payload["room_type"].strip(),
            equipment=payload["equipment"].strip(),
            status=payload["status"].strip(),
        )
        saved = self.room_dao.save(room)
        _log.info("Room %s saved (name=%s)", room_id, name)
        return saved

    def delete_room(self, room_id: str) -> None:
        self.room_dao.delete(room_id)
        _log.info("Room %s soft-deleted", room_id)

    # ── Availability ─────────────────────────────────────────────────────────

    def get_available_rooms(self, booking_ctrl: "BookingController",
                             booking_date: str, slot: str) -> list[Room]:
        """Return active rooms that are free for the given date + slot."""
        available: list[Room] = []
        for room in self.room_dao.list_all():
            if room.status != "Hoat dong":
                continue
            if slot in booking_ctrl.available_slots(room.room_id, booking_date):
                available.append(room)
        return available

    def __init__(self) -> None:
        self.room_dao = RoomDAO()

    def list_rooms(self, keyword: str = "") -> list[Room]:
        rooms = self.room_dao.list_all()
        kw = keyword.strip().lower()
        if not kw:
            return rooms
        return [r for r in rooms if kw in r.room_id.lower()
                or kw in r.name.lower() or kw in r.room_type.lower()]

    def get_room(self, room_id: str) -> Room | None:
        return self.room_dao.find_by_id(room_id)

    def save_room(self, payload: dict[str, str]) -> Room:
        room_id = payload["room_id"].strip().upper()
        name    = payload["name"].strip()
        if not room_id or not is_valid_room_code(room_id):
            raise ValueError("Ma phong phai co dinh dang nhu P101.")
        if not name:
            raise ValueError("Ten phong khong duoc de trong.")
        try:
            capacity = int(payload["capacity"])
            if capacity <= 0:
                raise ValueError
        except (ValueError, KeyError):
            raise ValueError("Suc chua phai la so nguyen duong.")
        room = Room(
            room_id=room_id,
            name=name,
            capacity=capacity,
            room_type=payload["room_type"].strip(),
            equipment=payload["equipment"].strip(),
            status=payload["status"].strip(),
        )
        return self.room_dao.save(room)

    def delete_room(self, room_id: str) -> None:
        self.room_dao.delete(room_id)

    def get_available_rooms(self, booking_ctrl: BookingController, booking_date: str, slot: str) -> list[Room]:
        """Tra ve danh sach phong dang hoat dong con trong tai ngay va ca da chon."""
        available: list[Room] = []
        for room in self.room_dao.list_all():
            if room.status != "Hoat dong":
                continue
            free_slots = booking_ctrl.available_slots(room.room_id, booking_date)
            if slot in free_slots:
                available.append(room)
        return available
