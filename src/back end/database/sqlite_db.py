"""SQLite database — singleton connection + schema bootstrap.

The database file is stored at:
    <project>/src/back end/database/classroom_booking.db
"""
from __future__ import annotations
import sqlite3
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
"""

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
    
    # 1. Seed Users
    seed_users = [
        ("AD001", "admin", "Nguyen Van A", "Admin",      "admin@btl.local", "0901234567", sha256_hash("admin123"), "Hoat dong"),
        ("GV001", "gv01",  "Tran Thi B",  "Giang vien", "gv01@btl.local",  "0912345678", sha256_hash("gv123"),    "Hoat dong"),
        ("GV002", "gv02",  "Nguyen Van C", "Giang vien", "gv02@btl.local",  "0923456789", sha256_hash("gv123"),    "Hoat dong"),
        ("SV001", "sv01",  "Le Van D",    "Sinh vien",  "sv01@btl.local",  "0934567890", sha256_hash("sv123"),    "Hoat dong"),
        ("SV002", "sv02",  "Pham Van E",  "Sinh vien",  "sv02@btl.local",  "0945678901", sha256_hash("sv123"),    "Hoat dong"),
        ("SV003", "sv03",  "Hoang Van F", "Sinh vien",  "sv03@btl.local",  "0956789012", sha256_hash("sv123"),    "Hoat dong"),
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

    # 3. Seed Equipment
    seed_equipment = [
        ("TB001", "May chieu Epson", "Thiet bi chieu", "P101", "Hoat dong", "01/01/2023"),
        ("TB002", "Dieu hoa Daikin", "Dieu hoa",       "P101", "Hoat dong", "15/03/2022"),
        ("TB003", "iMac 24 inch",    "May tinh",       "L101", "Hoat dong", "10/05/2023"),
        ("TB004", "Loa JBL",         "Am thanh",       "H101", "Hoat dong", "20/08/2022"),
        ("TB005", "Tivi Samsung 65", "Man hinh",       "S101", "Hoat dong", "01/09/2023"),
    ]
    conn.executemany(
        "INSERT INTO equipment (id,name,equipment_type,room_id,status,purchase_date) VALUES (?,?,?,?,?,?)",
        seed_equipment,
    )

    # 4. Seed Bookings
    seed_bookings = [
        ("DPH001", "GV001", "Tran Thi B",   "P101", "2026-04-20", "Ca 1", "Giang day Lap trinh", "Da duyet"),
        ("DPH002", "GV002", "Nguyen Van C", "P202", "2026-04-20", "Ca 2", "Thuc hanh CSDL",       "Cho duyet"),
        ("DPH003", "SV001", "Le Van D",     "L101", "2026-04-21", "Ca 3", "Lam bai tap lon",      "Da duyet"),
        ("DPH004", "SV002", "Pham Van E",    "S101", "2026-04-21", "Ca 4", "Hop co cau thanh nien", "Tu choi"),
    ]
    conn.executemany(
        "INSERT INTO bookings (id,user_id,user_name,room_id,booking_date,slot,purpose,status) VALUES (?,?,?,?,?,?,?,?)",
        seed_bookings,
    )

    # 5. Seed Schedules (Some recurring classes)
    seed_schedules = [
        ("P101", "Thu 2", "Ca 1", "Lap trinh Python", "Da dat"),
        ("P101", "Thu 3", "Ca 2", "Co so du lieu",    "Da dat"),
        ("P202", "Thu 4", "Ca 1", "Thuc hanh mang",   "Da dat"),
    ]
    conn.executemany(
        "INSERT INTO schedules (room_id,weekday,slot,label,status) VALUES (?,?,?,?,?)",
        seed_schedules,
    )

    conn.commit()
