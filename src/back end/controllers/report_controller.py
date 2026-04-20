"""Reporting and statistics logic."""
from __future__ import annotations
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.booking_controller import BookingController
    from controllers.room_controller import RoomController
    from controllers.user_controller import UserController
    from controllers.equipment_controller import EquipmentController


class ReportController:
    def __init__(
        self,
        room_controller: RoomController,
        booking_controller: BookingController,
        user_controller: UserController,
        equipment_controller: EquipmentController,
    ) -> None:
        self.room_ctrl = room_controller
        self.booking_ctrl = booking_controller
        self.user_ctrl = user_controller
        self.equip_ctrl = equipment_controller

    def build_dashboard(self) -> dict[str, int]:
        bookings = self.booking_ctrl.list_bookings(from_today=False)
        return {
            "Tong phong":     len(self.room_ctrl.list_rooms()),
            "Tong dat phong": len(bookings),
            "Cho duyet":      sum(1 for b in bookings if b.status == "Cho duyet"),
            "Tu choi":        sum(1 for b in bookings if b.status == "Tu choi"),
            "Nguoi dung":     len(self.user_ctrl.list_users()),
            "Thiet bi":       len(self.equip_ctrl.list_equipment()),
        }

    def room_usage_rows(self) -> list[tuple[str, int]]:
        counter = Counter(b.room_id for b in self.booking_ctrl.list_bookings(from_today=False))
        return [(r.room_id, counter.get(r.room_id, 0))
                for r in self.room_ctrl.list_rooms()]

    def room_stats_table(self) -> list[tuple[str, int, int, int, str]]:
        """Return per-room stats: (room_id, total, approved, rejected, rate_pct)."""
        from collections import defaultdict
        stats: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
        for b in self.booking_ctrl.list_bookings(from_today=False):
            stats[b.room_id][0] += 1
            if b.status == "Da duyet":
                stats[b.room_id][1] += 1
            elif b.status == "Tu choi":
                stats[b.room_id][2] += 1
        result: list[tuple[str, int, int, int, str]] = []
        for r in self.room_ctrl.list_rooms():
            s = stats.get(r.room_id, [0, 0, 0])
            total, approved, rejected = s
            rate = f"{int(approved / total * 100)}%" if total > 0 else "0%"
            result.append((r.room_id, total, approved, rejected, rate))
        return [row for row in result if row[1] > 0]

