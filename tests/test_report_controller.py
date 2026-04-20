"""Unit tests for ReportController."""
from __future__ import annotations

from controllers.auth_controller import AuthController
from controllers.booking_controller import BookingController
from controllers.equipment_controller import EquipmentController
from controllers.report_controller import ReportController
from controllers.room_controller import RoomController
from controllers.user_controller import UserController
from dao.room_dao import RoomDAO
from models.room import Room


def _setup() -> tuple[ReportController, BookingController]:
    rc = RoomController()
    bc = BookingController()
    uc = UserController()
    ec = EquipmentController()
    report = ReportController(rc, bc, uc, ec)

    # Seed data
    RoomDAO().save(Room("P101", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))
    auth = AuthController()
    user = auth.register("Report User", "rptuser", "rpt@test.com",
                         "0901234567", "pass123")
    bc.create_booking(user, "P101", "2026-05-01", "Ca 1", "Test booking 1")
    bc.create_booking(user, "P101", "2026-05-01", "Ca 2", "Test booking 2")
    return report, bc


class TestReportController:
    def test_dashboard_counts(self):
        report, bc = _setup()
        dash = report.build_dashboard()
        assert dash["Tong phong"] >= 1
        assert dash["Tong dat phong"] >= 2
        assert dash["Nguoi dung"] >= 1

    def test_room_usage_rows(self):
        report, bc = _setup()
        rows = report.room_usage_rows()
        assert len(rows) >= 1
        # P101 should have 2 bookings
        p101_row = next(r for r in rows if r[0] == "P101")
        assert p101_row[1] >= 2

    def test_room_stats_table(self):
        report, bc = _setup()
        stats = report.room_stats_table()
        assert len(stats) >= 1
        # Each row: (room_id, total, approved, rejected, rate_pct)
        for row in stats:
            assert len(row) == 5
