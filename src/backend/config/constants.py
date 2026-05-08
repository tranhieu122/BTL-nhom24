"""
config/constants.py — Central repository for all UI-level constants.

Import from here rather than duplicating values across gui/* and main.py.
"""

from __future__ import annotations

# ── Layout dimensions ─────────────────────────────────────────────────────────
SIDEBAR_W = 240     # sidebar width in pixels
TOPBAR_H  = 56      # top-bar height in pixels

# ── Sidebar palette (Indigo / Slate dark) ────────────────────────────────────
SB_BG     = "#1e1b4b"    # Indigo 950
SB_HOVER  = "#312e81"    # Indigo 900
SB_ACTIVE = "#3730a3"    # Indigo 800
SB_ACCENT = "#818cf8"    # Indigo 400
SB_TEXT   = "#e0e7ff"    # Indigo 100
SB_MUTED  = "#6366f1"    # Indigo 500
SB_SECT   = "#312e81"    # Indigo 900 (divider / section bg)

# ── Top-bar palette ───────────────────────────────────────────────────────────
TP_BG     = "#ffffff"
TP_BORDER = "#e2e8f0"
TP_TEXT   = "#1e293b"
TP_MUTED  = "#64748b"

# ── Content / page background ────────────────────────────────────────────────
C_BG      = "#f8fafc"    # Slate 50

# ── Role-chip colours  {role: (bg, fg)} ──────────────────────────────────────
ROLE_CHIP: dict[str, tuple[str, str]] = {
    "Admin":      ("#eef2ff", "#4f46e5"),   # Indigo tint
    "Giang vien": ("#dcfce7", "#15803d"),   # Green tint
    "Sinh vien":  ("#fef9c3", "#854d0e"),   # Amber tint
}

# ── Role-avatar fill colours ─────────────────────────────────────────────────
ROLE_AVATAR: dict[str, str] = {
    "Admin":      "#4f46e5",   # Indigo 600
    "Giang vien": "#16a34a",   # Green 600
    "Sinh vien":  "#b45309",   # Amber 700
}

# ── Sidebar navigation items ─────────────────────────────────────────────────
# Format: (display_label, route_key, emoji_icon)
# Use key == "---" for section headers (no icon needed).

NAV_ALL = [
    ("Trang chu",       "dashboard",           "🏠"),
    ("Dat phong",       "booking_form",        "📝"),
    ("Danh sach dat",   "booking_list",        "📋"),
    ("Lich bieu",       "schedule",            "📆"),
    ("Lich day chu ky", "recurring_schedule",  "🔁"),
    ("Thong bao",       "notifications",       "🔔"),
    ("QUAN TRI",        "---",                 None),
    ("Quan ly phong",   "rooms",               "🏫"),
    ("So do phong 2D",  "room_map",            "🗺️"),
    ("Nguoi dung",      "users",               "👥"),
    ("Thiet bi",        "equipment",           "🔧"),
    ("Bao cao",         "report",              "📊"),
    ("Bao loi phong",   "room_issues",         "🚨"),
    ("CAI DAT",         "---",                 None),
    ("Cai dat",         "settings",            "⚙️"),
    ("Gioi thieu",      "about",               "ℹ️"),
]

NAV_GV_SV = [
    ("Trang chu",       "dashboard",           "🏠"),
    ("Dat phong",       "booking_form",        "📝"),
    ("Lich su dat",     "booking_list",        "📋"),
    ("Lich bieu",       "schedule",            "📆"),
    ("Lich day chu ky", "recurring_schedule",  "🔁"),
    ("Thong bao",       "notifications",       "🔔"),
    ("Phong hoc",       "rooms",               "🏫"),
    ("So do phong 2D",  "room_map",            "🗺️"),
    ("CAI DAT",         "---",                 None),
    ("Cai dat",         "settings",            "⚙️"),
    ("Gioi thieu",      "about",               "ℹ️"),
]

# ── Page breadcrumb titles {route_key: Vietnamese title} ─────────────────────
PAGE_TITLES: dict[str, str] = {
    "dashboard":           "Trang chu",
    "rooms":               "Quan ly phong hoc",
    "room_map":            "So do phong hoc 2D",
    "booking_form":        "Dat phong hoc",
    "booking_list":        "Danh sach dat phong",
    "lich_su_dat":         "Lich su dat phong",
    "users":               "Quan ly nguoi dung",
    "equipment":           "Quan ly thiet bi",
    "report":              "Bao cao thong ke",
    "schedule":            "Lich bieu phong hoc",
    "lich_bieu":           "Lich bieu phong hoc",
    "recurring_schedule":  "Lich day theo chu ky tuan",
    "room_issues":         "Bao cao su co phong",
    "notifications":       "Thong bao noi bo",
    "settings":            "Cai dat",
    "about":               "Gioi thieu",
}
