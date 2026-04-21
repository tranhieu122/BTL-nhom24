"""Unit tests for BookingDAO."""
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false
from __future__ import annotations

from typing import Any

from dao.booking_dao import BookingDAO  # type: ignore[import-not-found]
from dao.user_dao import UserDAO  # type: ignore[import-not-found]
from dao.room_dao import RoomDAO  # type: ignore[import-not-found]
from models.booking import Booking  # type: ignore[import-not-found]
from models.room import Room  # type: ignore[import-not-found]
from models.user import User  # type: ignore[import-not-found]


def _seed(dao_u: Any, dao_r: Any) -> None:
    dao_u.save(User("U01", "u1", "User One", "Sinh vien",
                    "u1@x.com", "0901234567", "h", "Hoat dong"))
    dao_r.save(Room("R01", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))


def _make_booking(**ov: Any) -> Any:
    base: dict[str, Any] = dict(booking_id="B001", user_id="U01", user_name="User One",
                                room_id="R01", booking_date="2026-04-20",
                                slot="Ca 1 (07:00-09:00)", purpose="Hoc nhom",
                                status="Cho duyet")
    base.update(ov)
    return Booking(**base)


class TestBookingDAO:
    def test_save_and_find_by_id(self) -> None:
        udao, rdao, bdao = UserDAO(), RoomDAO(), BookingDAO()
        _seed(udao, rdao)
        b = _make_booking()
        bdao.save(b)
        found = bdao.find_by_id("B001")
        assert found is not None
        assert found.purpose == "Hoc nhom"

    def test_find_by_user(self) -> None:
        udao, rdao, bdao = UserDAO(), RoomDAO(), BookingDAO()
        _seed(udao, rdao)
        bdao.save(_make_booking(booking_id="B001"))
        bdao.save(_make_booking(booking_id="B002"))
        results = bdao.find_by_user("U01")
        assert len(results) == 2

    def test_list_all(self) -> None:
        udao, rdao, bdao = UserDAO(), RoomDAO(), BookingDAO()
        _seed(udao, rdao)
        bdao.save(_make_booking(booking_id="B001"))
        bdao.save(_make_booking(booking_id="B002"))
        assert len(bdao.list_all()) == 2

    def test_delete(self) -> None:
        udao, rdao, bdao = UserDAO(), RoomDAO(), BookingDAO()
        _seed(udao, rdao)
        bdao.save(_make_booking())
        bdao.delete("B001")
        assert bdao.find_by_id("B001") is None

    def test_status_update(self) -> None:
        udao, rdao, bdao = UserDAO(), RoomDAO(), BookingDAO()
        _seed(udao, rdao)
        b = _make_booking()
        bdao.save(b)
        b.status = "Da duyet"
        bdao.save(b)
        assert bdao.find_by_id("B001").status == "Da duyet"
