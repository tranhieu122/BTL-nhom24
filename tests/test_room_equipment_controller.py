"""Unit tests for RoomController and EquipmentController."""
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false
from __future__ import annotations

import pytest
from controllers.room_controller import RoomController  # type: ignore[import-not-found]
from controllers.equipment_controller import EquipmentController  # type: ignore[import-not-found]
from controllers.booking_controller import BookingController  # type: ignore[import-not-found]
from dao.room_dao import RoomDAO  # type: ignore[import-not-found]
from models.room import Room  # type: ignore[import-not-found]


class TestRoomController:
    def test_save_and_list(self):
        ctrl = RoomController()
        ctrl.save_room({"room_id": "P101", "name": "Phong 101",
                        "capacity": "40", "room_type": "Phong hoc",
                        "equipment": "May chieu", "status": "Hoat dong"})
        rooms = ctrl.list_rooms()
        assert len(rooms) == 1
        assert rooms[0].name == "Phong 101"

    def test_save_invalid_room_code(self):
        ctrl = RoomController()
        with pytest.raises(ValueError, match="dinh dang"):
            ctrl.save_room({"room_id": "xyz", "name": "Test",
                            "capacity": "10", "room_type": "Phong hoc",
                            "equipment": "", "status": "Hoat dong"})

    def test_save_invalid_capacity(self):
        ctrl = RoomController()
        with pytest.raises(ValueError, match="so nguyen duong"):
            ctrl.save_room({"room_id": "P101", "name": "Test",
                            "capacity": "-5", "room_type": "Phong hoc",
                            "equipment": "", "status": "Hoat dong"})

    def test_search_rooms(self):
        ctrl = RoomController()
        ctrl.save_room({"room_id": "P101", "name": "Phong 101",
                        "capacity": "40", "room_type": "Phong hoc",
                        "equipment": "", "status": "Hoat dong"})
        ctrl.save_room({"room_id": "L101", "name": "Lab 101",
                        "capacity": "30", "room_type": "Phong may",
                        "equipment": "", "status": "Hoat dong"})
        assert len(ctrl.list_rooms("lab")) == 1
        assert len(ctrl.list_rooms("101")) == 2

    def test_get_available_rooms(self):
        ctrl = RoomController()
        bc = BookingController()
        ctrl.save_room({"room_id": "P101", "name": "Phong 101",
                        "capacity": "40", "room_type": "Phong hoc",
                        "equipment": "", "status": "Hoat dong"})
        ctrl.save_room({"room_id": "P202", "name": "Phong 202",
                        "capacity": "30", "room_type": "Phong hoc",
                        "equipment": "", "status": "Bao tri"})
        available = ctrl.get_available_rooms(bc, "2026-05-01", "Ca 1")
        assert len(available) == 1
        assert available[0].room_id == "P101"

    def test_delete_room(self):
        ctrl = RoomController()
        ctrl.save_room({"room_id": "P101", "name": "Phong 101",
                        "capacity": "40", "room_type": "Phong hoc",
                        "equipment": "", "status": "Hoat dong"})
        ctrl.delete_room("P101")
        assert ctrl.get_room("P101") is None


class TestEquipmentController:
    def test_save_and_list(self):
        RoomDAO().save(Room("P101", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))
        ctrl = EquipmentController()
        ctrl.save_equipment({
            "equipment_id": "TB01", "name": "May chieu",
            "equipment_type": "Thiet bi chieu", "room_id": "P101",
            "status": "Hoat dong", "purchase_date": "2024-01-01",
        })
        items = ctrl.list_equipment()
        assert len(items) == 1

    def test_save_missing_name(self):
        ctrl = EquipmentController()
        with pytest.raises(ValueError, match="Ten thiet bi"):
            ctrl.save_equipment({
                "equipment_id": "TB01", "name": "",
                "equipment_type": "X", "room_id": "P101",
                "status": "Hoat dong", "purchase_date": "2024-01-01",
            })

    def test_filter_by_room(self):
        RoomDAO().save(Room("P101", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))
        RoomDAO().save(Room("P202", "Phong 202", 30, "Phong hoc", "", "Hoat dong"))
        ctrl = EquipmentController()
        ctrl.save_equipment({
            "equipment_id": "TB01", "name": "May chieu",
            "equipment_type": "X", "room_id": "P101",
            "status": "Hoat dong", "purchase_date": "2024-01-01",
        })
        ctrl.save_equipment({
            "equipment_id": "TB02", "name": "Dieu hoa",
            "equipment_type": "Y", "room_id": "P202",
            "status": "Hoat dong", "purchase_date": "2024-01-01",
        })
        assert len(ctrl.list_equipment("P101")) == 1
        assert len(ctrl.list_equipment()) == 2

    def test_delete_equipment(self):
        RoomDAO().save(Room("P101", "Phong 101", 40, "Phong hoc", "", "Hoat dong"))
        ctrl = EquipmentController()
        ctrl.save_equipment({
            "equipment_id": "TB01", "name": "Test",
            "equipment_type": "X", "room_id": "P101",
            "status": "Hoat dong", "purchase_date": "2024-01-01",
        })
        ctrl.delete_equipment("TB01")
        assert ctrl.equipment_dao.find_by_id("TB01") is None
