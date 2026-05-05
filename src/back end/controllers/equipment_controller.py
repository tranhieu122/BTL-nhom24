"""Equipment management business logic."""
from __future__ import annotations
from dao.equipment_dao import EquipmentDAO
from dao.room_feedback_dao import EquipmentReportDAO, EquipmentReport
from models.equipment import Equipment
from models.user import User
from utils.logger import get_logger

_log = get_logger(__name__)

VALID_STATUSES = {"Hoat dong", "Bao tri", "Hong", "Dang sua", "Da thanh ly"}
VALID_REPORT_STATUSES = {"Cho xu ly", "Dang xu ly", "Da xu ly"}


class EquipmentController:
    def __init__(self) -> None:
        self.equipment_dao = EquipmentDAO()
        self.report_dao = EquipmentReportDAO()

    # ── Queries ───────────────────────────────────────────────────────────────

    def list_equipment(self, room_id: str = "",
                       equipment_type: str = "",
                       status: str = "") -> list[Equipment]:
        """Return equipment filtered by room, type, and/or status."""
        items = self.equipment_dao.list_all()
        if room_id:
            items = [e for e in items if e.room_id == room_id]
        if equipment_type:
            items = [e for e in items if e.equipment_type == equipment_type]
        if status:
            items = [e for e in items if e.status == status]
        return items

    def get_equipment(self, equipment_id: str) -> Equipment | None:
        return self.equipment_dao.find_by_id(equipment_id)

    def list_types(self) -> list[str]:
        """Return sorted unique equipment types."""
        return sorted({e.equipment_type for e in self.equipment_dao.list_all()
                       if e.equipment_type})

    def count_by_status(self) -> dict[str, int]:
        """Return {status: count} across all equipment."""
        result: dict[str, int] = {}
        for e in self.equipment_dao.list_all():
            result[e.status] = result.get(e.status, 0) + 1
        return result

    # ── Mutations ─────────────────────────────────────────────────────────────

    def save_equipment(self, payload: dict[str, str]) -> Equipment:
        equipment_id = payload["equipment_id"].strip().upper()
        name         = payload["name"].strip()
        room_id      = payload["room_id"].strip()
        status       = payload.get("status", "Hoat dong").strip()
        if not equipment_id:
            raise ValueError("Ma thiet bi khong duoc de trong.")
        if not name:
            raise ValueError("Ten thiet bi khong duoc de trong.")
        if not room_id:
            raise ValueError("Hay chon phong chua thiet bi.")
        if status and status not in VALID_STATUSES:
            raise ValueError(f"Trang thai '{status}' khong hop le.")
        equip = Equipment(
            equipment_id=equipment_id,
            name=name,
            equipment_type=payload.get("equipment_type", "").strip(),
            room_id=room_id,
            status=status,
            purchase_date=payload.get("purchase_date", "").strip(),
        )
        saved = self.equipment_dao.save(equip)
        _log.info("Equipment %s saved (name=%s, room=%s)", equipment_id, name, room_id)
        return saved

    def delete_equipment(self, equipment_id: str) -> None:
        self.equipment_dao.delete(equipment_id)
        _log.info("Equipment %s deleted", equipment_id)

    def update_status(self, equipment_id: str, new_status: str) -> Equipment:
        """Update only the status of an existing equipment record."""
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Trang thai '{new_status}' khong hop le.")
        equip = self.equipment_dao.find_by_id(equipment_id)
        if equip is None:
            raise ValueError("Khong tim thay thiet bi.")
        equip.status = new_status
        saved = self.equipment_dao.save(equip)
        _log.info("Equipment %s status → %s", equipment_id, new_status)
        return saved

    # ── Maintenance reports ───────────────────────────────────────────────────

    def report_broken(self, equipment_id: str, user: User,
                      description: str) -> EquipmentReport:
        """Create a maintenance request for a broken/faulty equipment item.

        Also marks the equipment status as 'Bao tri' automatically.
        """
        equip = self.equipment_dao.find_by_id(equipment_id)
        if equip is None:
            raise ValueError("Khong tim thay thiet bi.")
        if not description.strip():
            raise ValueError("Mo ta su co khong duoc de trong.")
        # Auto-update equipment status to "Bao tri"
        if equip.status == "Hoat dong":
            equip.status = "Bao tri"
            self.equipment_dao.save(equip)
        report = self.report_dao.report(
            equipment_id=equipment_id,
            equipment_name=equip.name,
            room_id=equip.room_id,
            user_id=user.user_id,
            user_name=user.full_name,
            description=description.strip(),
        )
        _log.info("Equipment report created for %s by %s", equipment_id, user.username)
        return report

    def list_reports(self, room_id: str = "",
                     status: str = "") -> list[EquipmentReport]:
        return self.report_dao.list_all(room_id=room_id, status=status)

    def resolve_report(self, report_id: int) -> None:
        self.report_dao.update_status(report_id, "Da xu ly")
        _log.info("Equipment report %d resolved", report_id)

