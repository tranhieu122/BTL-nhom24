"""Business logic for weekly recurring schedule rules."""
from __future__ import annotations
import datetime as dt
from dao.schedule_rule_dao import ScheduleRuleDAO
from models.schedule_rule import ScheduleRule, ScheduleOccurrence
from utils.logger import get_logger

_log = get_logger(__name__)

# ISO weekday labels (1=Mon … 7=Sun)
WEEKDAY_LABELS: dict[int, str] = {
    1: "Thu 2", 2: "Thu 3", 3: "Thu 4",
    4: "Thu 5", 5: "Thu 6", 6: "Thu 7", 7: "Chu nhat",
}

SLOT_TIME_RANGES = [
    ("07:00", "09:00"),
    ("09:15", "11:15"),
    ("13:00", "15:00"),
    ("15:15", "17:15"),
    ("17:30", "19:30"),
]

VALID_STATUSES = {"Hoat dong", "Da xong", "Huy"}


class ScheduleRuleController:
    def __init__(self) -> None:
        self.dao = ScheduleRuleDAO()

    # ── Queries ───────────────────────────────────────────────────────────────

    def list_rules(self, status: str = "") -> list[ScheduleRule]:
        rules = self.dao.list_all()
        if status:
            rules = [r for r in rules if r.status == status]
        return rules

    def get_rule(self, rule_id: int) -> ScheduleRule | None:
        return self.dao.find_by_id(rule_id)

    def list_occurrences(self, rule_id: int) -> list[ScheduleOccurrence]:
        return self.dao.list_occurrences(rule_id)

    def count_occurrences(self, rule_id: int) -> int:
        return self.dao.count_occurrences(rule_id)

    def list_occurrences_in_range(
        self, date_from: str, date_to: str
    ) -> list[ScheduleOccurrence]:
        return self.dao.list_occurrences_by_date_range(date_from, date_to)

    # ── Create ────────────────────────────────────────────────────────────────

    def create_rule(self, payload: dict) -> ScheduleRule: # type: ignore
        """Validate, save a ScheduleRule, then auto-generate all occurrences."""
        subject = payload.get("subject", "").strip() # type: ignore
        if not subject:
            raise ValueError("Ten mon hoc / ten buoi day khong duoc de trong.")

        days_of_week: list[int] = list(payload.get("days_of_week", [])) # type: ignore
        if not days_of_week:
            raise ValueError("Phai chon it nhat mot thu trong tuan.")
        invalid = [d for d in days_of_week if d not in range(1, 8)]
        if invalid:
            raise ValueError(f"Gia tri thu khong hop le: {invalid}")

        start_time: str = payload.get("start_time", "").strip() # type: ignore
        end_time: str   = payload.get("end_time", "").strip() # type: ignore
        if not start_time or not end_time:
            raise ValueError("Phai nhap gio bat dau va gio ket thuc.")
        try:
            t_start = dt.time.fromisoformat(start_time) # type: ignore
            t_end   = dt.time.fromisoformat(end_time) # type: ignore
        except ValueError:
            raise ValueError("Dinh dang gio phai la HH:MM.")
        if t_start >= t_end:
            raise ValueError("Gio bat dau phai truoc gio ket thuc.")

        start_date: str = payload.get("start_date", "").strip() # type: ignore
        end_date:   str = payload.get("end_date", "").strip() # type: ignore
        try:
            d_start = dt.date.fromisoformat(start_date) # type: ignore
            d_end   = dt.date.fromisoformat(end_date) # type: ignore
        except ValueError:
            raise ValueError("Ngay bat dau / ket thuc phai theo dinh dang YYYY-MM-DD.")
        if d_start > d_end:
            raise ValueError("Ngay bat dau phai truoc hoac bang ngay ket thuc.")
        if (d_end - d_start).days > 365 * 3:
            raise ValueError("Khoang thoi gian khong duoc vuot qua 3 nam.")

        room_id: str      = payload.get("room_id", "").strip() # type: ignore
        lecturer_id: str  = payload.get("lecturer_id", "").strip() # type: ignore
        if not room_id:
            raise ValueError("Phai chon phong hoc.")
        if not lecturer_id:
            raise ValueError("Phai nhap ma giang vien.")

        lecturer_name: str = payload.get("lecturer_name", "").strip() # type: ignore

        rule = ScheduleRule(
            subject=subject, # type: ignore
            days_of_week=sorted(days_of_week),
            start_time=start_time, # type: ignore
            end_time=end_time, # type: ignore
            start_date=start_date, # type: ignore
            end_date=end_date, # type: ignore
            room_id=room_id, # type: ignore
            lecturer_id=lecturer_id, # type: ignore
            lecturer_name=lecturer_name, # type: ignore
            status="Hoat dong",
        )
        rule = self.dao.save(rule)
        occurrences = self._generate_occurrences(rule)
        self.dao.insert_occurrences(occurrences)
        _log.info(
            "ScheduleRule #%d created — %d occurrences generated",
            rule.rule_id, len(occurrences),
        )
        return rule

    # ── Update status ─────────────────────────────────────────────────────────

    def update_rule_status(self, rule_id: int, status: str) -> None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Trang thai khong hop le: {status}")
        self.dao.update_status(rule_id, status)

    def update_occurrence_status(self, occ_id: int, status: str) -> None:
        valid = {"Du kien", "Da dien ra", "Huy"}
        if status not in valid:
            raise ValueError(f"Trang thai buoi hoc khong hop le: {status}")
        self.dao.update_occurrence_status(occ_id, status)

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete_rule(self, rule_id: int) -> None:
        self.dao.delete(rule_id)
        _log.info("ScheduleRule #%d deleted (with all occurrences)", rule_id)

    # ── Occurrence generation ─────────────────────────────────────────────────

    @staticmethod
    def _generate_occurrences(rule: ScheduleRule) -> list[ScheduleOccurrence]:
        """Expand a ScheduleRule into concrete daily occurrences."""
        d_start = dt.date.fromisoformat(rule.start_date)
        d_end   = dt.date.fromisoformat(rule.end_date)
        target_days = set(rule.days_of_week)
        occurrences: list[ScheduleOccurrence] = []

        current = d_start
        while current <= d_end:
            iso_wd = current.isoweekday()  # 1=Mon … 7=Sun
            if iso_wd in target_days:
                occurrences.append(ScheduleOccurrence(
                    rule_id=rule.rule_id,
                    occurrence_date=current.isoformat(),
                    day_of_week=iso_wd,
                    subject=rule.subject,
                    start_time=rule.start_time,
                    end_time=rule.end_time,
                    room_id=rule.room_id,
                    lecturer_name=rule.lecturer_name,
                    status="Du kien",
                ))
            current += dt.timedelta(days=1)
        return occurrences

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def days_label(days_of_week: list[int]) -> str:
        """Return human-readable day list, e.g. 'T2, T4, T6'."""
        short = {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}
        return ", ".join(short.get(d, str(d)) for d in sorted(days_of_week))
