"""SQLite database — singleton connection + schema bootstrap.

The database file is stored at:
    <project>/src/back end/database/classroom_booking.db
"""
from __future__ import annotations
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

_log = get_logger(__name__)
_DB_PATH = Path(__file__).parent / "classroom_booking.db"

_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    full_name     TEXT NOT NULL,
    role          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone         TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'Hoat dong'
);

CREATE TABLE IF NOT EXISTS rooms (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    capacity   INTEGER NOT NULL,
    room_type  TEXT NOT NULL,
    equipment  TEXT NOT NULL DEFAULT '',
    status     TEXT NOT NULL DEFAULT 'Hoat dong'
);

CREATE TABLE IF NOT EXISTS bookings (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL,
    user_name    TEXT NOT NULL,
    room_id      TEXT NOT NULL,
    booking_date TEXT NOT NULL,
    slot         TEXT NOT NULL,
    purpose      TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'Cho duyet',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

CREATE TABLE IF NOT EXISTS equipment (
    id             TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    room_id        TEXT NOT NULL,
    status         TEXT NOT NULL,
    purchase_date  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedules (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id  TEXT NOT NULL,
    weekday  TEXT NOT NULL,
    slot     TEXT NOT NULL,
    label    TEXT NOT NULL DEFAULT '',
    status   TEXT NOT NULL DEFAULT 'Trong',
    UNIQUE (room_id, weekday, slot)
);

CREATE TABLE IF NOT EXISTS room_ratings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id    TEXT NOT NULL,
    user_id    TEXT NOT NULL,
    user_name  TEXT NOT NULL,
    stars      INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5),
    comment    TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS room_issues (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id     TEXT NOT NULL,
    user_id     TEXT NOT NULL,
    user_name   TEXT NOT NULL,
    description TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'Chua xu ly',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS schedule_rules (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    subject       TEXT NOT NULL,
    days_of_week  TEXT NOT NULL,  -- comma-separated ISO weekdays, e.g. "1,3,5"
    start_time    TEXT NOT NULL,  -- "HH:MM"
    end_time      TEXT NOT NULL,  -- "HH:MM"
    start_date    TEXT NOT NULL,  -- "YYYY-MM-DD"
    end_date      TEXT NOT NULL,  -- "YYYY-MM-DD"
    room_id       TEXT NOT NULL,
    lecturer_id   TEXT NOT NULL,
    lecturer_name TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL DEFAULT 'Hoat dong',
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

CREATE TABLE IF NOT EXISTS schedule_occurrences (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id         INTEGER NOT NULL,
    occurrence_date TEXT NOT NULL,  -- "YYYY-MM-DD"
    day_of_week     INTEGER NOT NULL,  -- 1=Mon..7=Sun
    subject         TEXT NOT NULL,
    start_time      TEXT NOT NULL,
    end_time        TEXT NOT NULL,
    room_id         TEXT NOT NULL,
    lecturer_name   TEXT NOT NULL DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'Du kien',
    FOREIGN KEY (rule_id) REFERENCES schedule_rules(id) ON DELETE CASCADE
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_bookings_user_id    ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_room_id    ON bookings(room_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date       ON bookings(booking_date);
CREATE INDEX IF NOT EXISTS idx_bookings_status     ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_equipment_room_id   ON equipment(room_id);
CREATE INDEX IF NOT EXISTS idx_equipment_status    ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_room_ratings_room   ON room_ratings(room_id);
CREATE INDEX IF NOT EXISTS idx_room_issues_room    ON room_issues(room_id);
CREATE INDEX IF NOT EXISTS idx_occ_rule_id         ON schedule_occurrences(rule_id);
CREATE INDEX IF NOT EXISTS idx_occ_date            ON schedule_occurrences(occurrence_date);
"""

# ── auto-backup ──────────────────────────────────────────────────────────────

_BACKUP_KEEP = 7  # number of backups to retain


def backup_database() -> None:
    """Copy DB file to <db_dir>/backups/ with a timestamp.  Keep last N copies."""
    if not _DB_PATH.exists():
        return
    backup_dir = _DB_PATH.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"classroom_booking_{ts}.db"
    shutil.copy2(str(_DB_PATH), str(dest))
    _log.info("Database backed up → %s", dest)
    # Prune old backups
    all_backups = sorted(backup_dir.glob("classroom_booking_*.db"))
    for old in all_backups[:-_BACKUP_KEEP]:
        try:
            old.unlink()
        except OSError:
            pass


# ── singleton connection ──────────────────────────────────────────────────────

_conn: sqlite3.Connection | None = None


def bootstrap() -> None:
    """Ensure database file, schema, and seed data are initialized."""
    get_connection()


def get_connection() -> sqlite3.Connection:
    """Return the open SQLite connection, creating it on first call."""
    global _conn
    if _conn is None:
        _log.info("Opening SQLite database at %s", _DB_PATH)
        try:
            _conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
            _conn.row_factory = sqlite3.Row
            _conn.executescript(_SCHEMA)
            _conn.commit()
            _bootstrap_seed(_conn)
            # Apply any pending schema migrations
            from database.migrations import run_migrations
            run_migrations(_conn)
            _log.info("Database initialised successfully")
        except Exception:
            _log.critical("Failed to initialise database", exc_info=True)
            raise
    return _conn


def _bootstrap_seed(conn: sqlite3.Connection) -> None:
    """Insert comprehensive seed data when tables are empty."""
    # Check if we already have data
    cur = conn.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] > 0:
        return

    from utils.password_hash import sha256_hash
    
    # 1. Seed Essential Users (Admin only for clean start)
    seed_users = [
        ("AD001", "admin", "Nguyen Van A", "Admin", "admin@btl.local", "0901234567", sha256_hash("admin123"), "Hoat dong"),
    ]
    conn.executemany(
        "INSERT INTO users (id,username,full_name,role,email,phone,password_hash,status) VALUES (?,?,?,?,?,?,?,?)",
        seed_users,
    )

    # 2. Seed Rooms
    seed_rooms = [
        ("P101", "Phong 101", 50, "Phong hoc",    "May chieu, Dieu hoa",                "Hoat dong"),
        ("P202", "Phong 202", 40, "Phong may",    "May tinh (30), May chieu",           "Hoat dong"),
        ("P305", "Phong 305", 60, "Hoi truong",   "Micro, Am thanh, May chieu",         "Bao tri"),
        ("L101", "Lab 101",   30, "Phong may",    "30 iMac, May chieu",                 "Hoat dong"),
        ("S101", "Seminar 1", 20, "Phong seminar", "TV 65\", Bang trang",                "Hoat dong"),
        ("H101", "Hoi truong A", 150, "Hoi truong", "Am thanh khung, 2 May chieu",        "Hoat dong"),
    ]
    conn.executemany(
        "INSERT INTO rooms (id,name,capacity,room_type,equipment,status) VALUES (?,?,?,?,?,?)",
        seed_rooms,
    )

    # No mock bookings, equipment or schedules for clean start.

    conn.commit()
