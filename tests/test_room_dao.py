"""Unit tests for RoomDAO."""
from __future__ import annotations

import pytest
from dao.room_dao import RoomDAO
from models.room import Room


def _room(**ov) -> Room:
    base = dict(room_id="R01", name="Phong 101", capacity=40,
                room_type="Phong hoc", equipment="May chieu", status="Hoat dong")
    base.update(ov)
    return Room(**base)


class TestRoomDAO:
    def test_save_and_find(self):
        dao = RoomDAO()
        dao.save(_room())
        r = dao.find_by_id("R01")
        assert r is not None
        assert r.name == "Phong 101"

    def test_find_nonexistent(self):
        dao = RoomDAO()
        assert dao.find_by_id("NOPE") is None

    def test_list_all(self):
        dao = RoomDAO()
        dao.save(_room(room_id="R01", name="P1"))
        dao.save(_room(room_id="R02", name="P2"))
        assert len(dao.list_all()) == 2

    def test_update(self):
        dao = RoomDAO()
        r = _room()
        dao.save(r)
        r.capacity = 99
        dao.save(r)
        assert dao.find_by_id("R01").capacity == 99

    def test_delete(self):
        dao = RoomDAO()
        dao.save(_room())
        dao.delete("R01")
        assert dao.find_by_id("R01") is None
