"""Equipment management business logic."""
from __future__ import annotations
from dao.equipment_dao import EquipmentDAO
from models.equipment import Equipment
from utils.logger import get_logger

_log = get_logger(__name__)


class EquipmentController:
    def __init__(self) -> None:
        self.equipment_dao = EquipmentDAO()

    def list_equipment(self, room_id: str = "") -> list[Equipment]:
        items = self.equipment_dao.list_all()
        if room_id:
            items = [e for e in items if e.room_id == room_id]
        return items

    def save_equipment(self, payload: dict[str, str]) -> Equipment:
        equipment_id = payload["equipment_id"].strip().upper()
        name         = payload["name"].strip()
        room_id      = payload["room_id"].strip()
        if not equipment_id:
            raise ValueError("Ma thiet bi khong duoc de trong.")
        if not name:
            raise ValueError("Ten thiet bi khong duoc de trong.")
        if not room_id:
            raise ValueError("Hay chon phong chua thiet bi.")
        equip = Equipment(
            equipment_id=equipment_id,
            name=name,
            equipment_type=payload["equipment_type"].strip(),
            room_id=room_id,
            status=payload["status"].strip(),
            purchase_date=payload["purchase_date"].strip(),
        )
        return self.equipment_dao.save(equip)

    def delete_equipment(self, equipment_id: str) -> None:
        self.equipment_dao.delete(equipment_id)
