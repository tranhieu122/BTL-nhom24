"""Booking business logic and conflict checks."""
from __future__ import annotations
import datetime as dt
import threading
import uuid
from dao.booking_dao import BookingDAO
from dao.user_dao import UserDAO
from models.booking import Booking
from models.schedule import Schedule
from models.user import User
from utils.email_notifier import send_booking_notification
from utils.logger import get_logger

_log = get_logger(__name__)


class BookingController:
    SLOT_OPTIONS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]
    WEEKDAY_LABELS = {0: "Thu 2", 1: "Thu 3", 2: "Thu 4",
                      3: "Thu 5", 4: "Thu 6", 5: "Thu 7", 6: "Chu nhat"}

    def __init__(self) -> None:
        self.booking_dao = BookingDAO()

    VALID_STATUSES = {"Cho duyet", "Da duyet", "Tu choi"}

    def list_bookings(self, current_user: User | None = None,
                      status: str = "", room_id: str = "", date_text: str = "",
                      from_today: bool = True) -> list[Booking]:
        bookings = self.booking_dao.list_all()
        if from_today:
            today = dt.date.today().isoformat()
            bookings = [b for b in bookings if b.booking_date >= today]
        if current_user is not None and current_user.role != "Admin":
            bookings = [b for b in bookings if b.user_id == current_user.user_id]
        if status:
            bookings = [b for b in bookings if b.status == status]
        if room_id:
            bookings = [b for b in bookings if b.room_id == room_id]
        if date_text:
            bookings = [b for b in bookings if b.booking_date == date_text]
        return bookings

    def available_slots(self, room_id: str, booking_date: str) -> list[str]:
        used = {b.slot for b in self.booking_dao.list_all()
                if b.room_id == room_id and b.booking_date == booking_date
                and b.status != "Tu choi"}
        return [s for s in self.SLOT_OPTIONS if s not in used]

    def create_booking(self, user: User, room_id: str, booking_date: str,
                       slot: str, purpose: str) -> Booking:
        try:
            dt.date.fromisoformat(booking_date)
        except ValueError:
            raise ValueError("Ngay dat phong phai theo dinh dang YYYY-MM-DD.")
        if not room_id:
            raise ValueError("Hay chon phong hoc.")
        if slot not in self.SLOT_OPTIONS:
            raise ValueError("Ca hoc khong hop le.")
        if not purpose.strip():
            raise ValueError("Muc dich dat phong khong duoc de trong.")
        if slot not in self.available_slots(room_id, booking_date):
            raise ValueError("Phong da co lich trong ca hoc nay.")
        new_id = "B" + uuid.uuid4().hex[:8].upper()
        booking = Booking(
            booking_id=new_id, user_id=user.user_id, user_name=user.full_name,
            room_id=room_id, booking_date=booking_date, slot=slot,
            purpose=purpose.strip(),
            status="Da duyet" if user.role == "Admin" else "Cho duyet",
        )
        _log.info("Booking created: %s by %s for room %s on %s %s",
                  new_id, user.username, room_id, booking_date, slot)
        return self.booking_dao.save(booking)

    def update_status(self, booking_id: str, new_status: str) -> Booking:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Trang thai '{new_status}' khong hop le.")
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        booking.status = new_status
        saved = self.booking_dao.save(booking)
        _log.info("Booking %s status changed to '%s'", booking_id, new_status)

        # Fire-and-forget email notification (non-blocking)
        if new_status in ("Da duyet", "Tu choi"):
            try:
                user = UserDAO().find_by_id(booking.user_id)
                email = getattr(user, "email", "") if user else ""
            except Exception:
                email = ""
            if email:
                threading.Thread(
                    target=send_booking_notification,
                    args=(email, booking.user_name, booking.booking_id,
                          booking.room_id, booking.booking_date,
                          booking.slot, new_status),
                    daemon=True,
                ).start()
        return saved

    def update_booking(self, booking_id: str, current_user: User, room_id: str,
                       booking_date: str, slot: str, purpose: str) -> Booking:
        """Edit booking fields. Owner or Admin only."""
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        if current_user.role != "Admin" and booking.user_id != current_user.user_id:
            raise PermissionError("Ban khong co quyen sua lich nay.")
        try:
            dt.date.fromisoformat(booking_date)
        except ValueError:
            raise ValueError("Ngay dat phong phai theo dinh dang YYYY-MM-DD.")
        if slot not in self.SLOT_OPTIONS:
            raise ValueError("Ca hoc khong hop le.")
        if not purpose.strip():
            raise ValueError("Muc dich dat phong khong duoc de trong.")
        # Check conflict, excluding current booking
        used = {b.slot for b in self.booking_dao.list_all()
                if b.room_id == room_id and b.booking_date == booking_date
                and b.status != "Tu choi" and b.booking_id != booking_id}
        if slot in used:
            raise ValueError("Phong da co lich trong ca hoc nay.")
        booking.room_id = room_id
        booking.booking_date = booking_date
        booking.slot = slot
        booking.purpose = purpose.strip()
        # Reset status to pending if not admin
        if current_user.role != "Admin":
            booking.status = "Cho duyet"
        return self.booking_dao.save(booking)

    def delete_booking(self, booking_id: str, current_user: User) -> None:
        """Delete a booking. Owner or Admin only."""
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        if current_user.role != "Admin" and booking.user_id != current_user.user_id:
            raise PermissionError("Ban khong co quyen xoa lich nay.")
        self.booking_dao.delete(booking_id)
        _log.info("Booking %s deleted by user %s", booking_id, current_user.user_id)

    def suggest_alternatives(
        self,
        room_id: str,
        booking_date: str,
        slot: str,
        all_room_ids: list[str],
        days_ahead: int = 7,
    ) -> dict[str, list[tuple[str, str]]]:
        """Return two suggestion groups:

        'other_rooms'   – [(room_id, slot)] rooms free on the same date+slot
        'other_slots'   – [(date_str, slot)] free combos for the same room
                           in the next `days_ahead` days (incl. today)
        """
        try:
            base_date = dt.date.fromisoformat(booking_date)
        except ValueError:
            return {"other_rooms": [], "other_slots": []}

        # ── 1. Other rooms free on same date + slot ───────────────────────────
        other_rooms: list[tuple[str, str]] = []
        for rid in all_room_ids:
            if rid == room_id:
                continue
            if slot in self.available_slots(rid, booking_date):
                other_rooms.append((rid, slot))

        # ── 2. Other date+slot combos for the same room ───────────────────────
        other_slots: list[tuple[str, str]] = []
        for delta in range(0, days_ahead + 1):
            d = base_date + dt.timedelta(days=delta)
            date_str = d.isoformat()
            free = self.available_slots(room_id, date_str)
            for s in free:
                # Skip the current (room, date, slot) — that's already shown
                if date_str == booking_date and s == slot:
                    continue
                other_slots.append((date_str, s))

        return {"other_rooms": other_rooms, "other_slots": other_slots}

    def build_schedule(self) -> list[Schedule]:
        rows: list[Schedule] = []
        today = dt.date.today().isoformat()
        for b in self.booking_dao.list_all():
            if b.booking_date < today:
                continue
            try:
                d = dt.date.fromisoformat(b.booking_date)
                weekday = self.WEEKDAY_LABELS[d.weekday()]
            except Exception:
                weekday = b.booking_date
            rows.append(Schedule(room_id=b.room_id, weekday=weekday,
                                 slot=b.slot, label=f"{b.room_id} - {b.user_name}",
                                 status=b.status))
        return rows
