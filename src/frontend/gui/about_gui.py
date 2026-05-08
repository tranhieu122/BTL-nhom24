# about_gui.py — About / Info page for the Classroom Booking System
from __future__ import annotations
import tkinter as tk

from gui.theme import (
    F_TITLE, F_SECTION, F_BODY, F_BODY_B, F_SMALL,
    page_header, make_card, _get_c,
)


_VERSION      = "2.0.0"
_RELEASE_DATE = "2026-05"
_TEAM         = [
    ("Tran Trung Hieu",   "MSSV: 20210xxx", "Team lead · Backend"),
    ("Nguyen Huy Hai",    "MSSV: 20210yyy", "Frontend · UI/UX"),
    ("Nguyen Tuan Minh",  "MSSV: 20210zzz", "Database · Testing"),
]
_FEATURES = [
    ("🏫", "Quan ly phong",    "Them / sua / xoa phong, theo doi trang thai thiet bi."),
    ("📝", "Dat phong",        "Dat phong theo ca, kiem tra xung dot tu dong."),
    ("📆", "Lich bieu",        "Xem lich dat phong theo tuan / thang."),
    ("🔁", "Lich chu ky",      "Tao lich day lap lai hang tuan tu dong."),
    ("🔔", "Thong bao",        "Thong bao noi bo khi dat phong duoc duyet / tu choi."),
    ("📊", "Bao cao",          "Xuat bao cao PDF / Excel, thong ke su dung phong."),
    ("🔒", "Bao mat",          "Ma hoa mat khau BCrypt, ghi log, backup tu dong."),
    ("📅", "Xuat ICS",         "Xuat lich dat phong sang dinh dang ICS (Google Calendar)."),
]
_SHORTCUTS = [
    ("Ctrl + D",       "Trang chu"),
    ("Ctrl + B",       "Dat phong"),
    ("Ctrl + L",       "Danh sach dat"),
    ("Ctrl + ,",       "Cai dat"),
    ("Ctrl + \\",      "An / hien Sidebar"),
    ("F5",             "Tai lai trang hien tai"),
    ("F11",            "Toan man hinh"),
    ("Escape",         "Thoat toan man hinh"),
]


class AboutFrame(tk.Frame):
    """About page — project info, team, features and keyboard shortcuts."""

    def __init__(self, master) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self._build()

    def _build(self) -> None:
        page_header(self, "Gioi thieu he thong", "ℹ️").pack(fill="x")

        # Scrollable body
        canvas = tk.Canvas(self, bg=_get_c("BG"), highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=_get_c("BG"))
        win_id = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e=None: canvas.itemconfig(win_id, width=e.width))
        body.bind("<Configure>",
                  lambda e=None: canvas.config(scrollregion=canvas.bbox("all")))

        # ── Hero banner ────────────────────────────────────────────────────
        banner = tk.Frame(body, bg=_get_c("ACCENT"), pady=32)
        banner.pack(fill="x", padx=24, pady=(8, 0))
        tk.Label(banner, text="🏫", bg=_get_c("ACCENT"),
                 font=("Segoe UI", 48)).pack()
        tk.Label(banner, text="He Thong Quan Ly Dat Phong Hoc",
                 bg=_get_c("ACCENT"), fg="white", font=F_TITLE).pack()
        tk.Label(banner,
                 text=f"Phien ban {_VERSION}  •  Phat hanh {_RELEASE_DATE}",
                 bg=_get_c("ACCENT"), fg="#c7d2fe", font=F_SMALL).pack(pady=(4, 0))
        tk.Label(banner, text="Nhom 24 — Bai Tap Lon",
                 bg=_get_c("ACCENT"), fg=_get_c("LIGHT"), font=F_SMALL).pack()

        # Two-column layout
        cols = tk.Frame(body, bg=_get_c("BG"))
        cols.pack(fill="both", expand=True, padx=24, pady=16)

        left  = tk.Frame(cols, bg=_get_c("BG"))
        right = tk.Frame(cols, bg=_get_c("BG"))
        left.pack(side="left",  fill="both", expand=True, padx=(0, 8))
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self._build_team_card(left)
        self._build_features_card(left)
        self._build_shortcuts_card(right)
        self._build_tech_card(right)

    # ── Team card ─────────────────────────────────────────────────────────────

    def _build_team_card(self, parent: tk.Frame) -> None:
        outer, card = make_card(parent)
        outer.pack(fill="x", pady=(0, 12))
        tk.Label(card, text="👥  Thanh vien nhom",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_SECTION).pack(anchor="w", pady=(0, 10))
        tk.Frame(card, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=(0, 12))
        for name, student_id, role in _TEAM:
            row = tk.Frame(card, bg=_get_c("SURFACE"))
            row.pack(fill="x", pady=5)
            av = tk.Canvas(row, width=38, height=38, bg=_get_c("INFO_BG"),
                           highlightthickness=0)
            av.pack(side="left", padx=(0, 12))
            av.create_oval(2, 2, 36, 36, fill=_get_c("ACCENT"), outline="")
            initials = "".join(p[0] for p in name.split()[-2:]).upper()
            av.create_text(19, 19, text=initials, fill="white",
                           font=("Segoe UI", 11, "bold"))
            info = tk.Frame(row, bg=_get_c("SURFACE"))
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=name, bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                     font=F_BODY_B, anchor="w").pack(fill="x")
            tk.Label(info, text=f"{student_id}  ·  {role}",
                     bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                     font=F_SMALL, anchor="w").pack(fill="x")

    # ── Features card ─────────────────────────────────────────────────────────

    def _build_features_card(self, parent: tk.Frame) -> None:
        outer, card = make_card(parent)
        outer.pack(fill="x", pady=(0, 12))
        tk.Label(card, text="✨  Tinh nang chinh",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_SECTION).pack(anchor="w", pady=(0, 10))
        tk.Frame(card, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=(0, 12))
        for icon, title, desc in _FEATURES:
            row = tk.Frame(card, bg=_get_c("SUCCESS_BG"),
                           highlightthickness=1,
                           highlightbackground=_get_c("SUCCESS"))
            row.pack(fill="x", pady=3, ipady=6, ipadx=8)
            tk.Label(row, text=icon, bg=_get_c("SUCCESS_BG"),
                     font=("Segoe UI", 14)).pack(side="left", padx=(6, 8))
            right = tk.Frame(row, bg=_get_c("SUCCESS_BG"))
            right.pack(side="left", fill="x", expand=True)
            tk.Label(right, text=title, bg=_get_c("SUCCESS_BG"), fg=_get_c("SUCCESS"),
                     font=F_BODY_B, anchor="w").pack(fill="x")
            tk.Label(right, text=desc, bg=_get_c("SUCCESS_BG"), fg=_get_c("TEXT"),
                     font=F_SMALL, anchor="w", wraplength=340,
                     justify="left").pack(fill="x")

    # ── Keyboard shortcuts card ───────────────────────────────────────────────

    def _build_shortcuts_card(self, parent: tk.Frame) -> None:
        outer, card = make_card(parent)
        outer.pack(fill="x", pady=(0, 12))
        tk.Label(card, text="⌨️  Phim tat",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_SECTION).pack(anchor="w", pady=(0, 10))
        tk.Frame(card, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=(0, 12))
        for keys, action in _SHORTCUTS:
            row = tk.Frame(card, bg=_get_c("SURFACE"))
            row.pack(fill="x", pady=3)
            key_badge = tk.Label(
                row, text=keys,
                bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"),
                font=("Consolas", 9, "bold"),
                padx=8, pady=3,
                relief="flat")
            key_badge.pack(side="left", padx=(0, 12))
            tk.Label(row, text=action, bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                     font=F_BODY, anchor="w").pack(side="left")

    # ── Tech stack card ───────────────────────────────────────────────────────

    def _build_tech_card(self, parent: tk.Frame) -> None:
        outer, card = make_card(parent)
        outer.pack(fill="x", pady=(0, 12))
        tk.Label(card, text="🛠️  Cong nghe su dung",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_SECTION).pack(anchor="w", pady=(0, 10))
        tk.Frame(card, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=(0, 12))
        techs = [
            ("Python 3.12+",  "Ngon ngu lap trinh chinh"),
            ("Tkinter",       "GUI framework"),
            ("SQLite 3",      "Co so du lieu noi bo"),
            ("BCrypt",        "Ma hoa mat khau"),
            ("tkcalendar",    "Widget chon ngay"),
            ("openpyxl",      "Xuat bao cao Excel"),
            ("ReportLab",     "Xuat bao cao PDF"),
            ("icalendar",     "Xuat lich ICS"),
            ("pytest",        "Kiem thu tu dong"),
        ]
        for tech, desc in techs:
            row = tk.Frame(card, bg=_get_c("SURFACE"))
            row.pack(fill="x", pady=3)
            tk.Label(row, text="▸", bg=_get_c("SURFACE"), fg=_get_c("ACCENT"),
                     font=F_BODY_B).pack(side="left", padx=(0, 6))
            tk.Label(row, text=tech, bg=_get_c("SURFACE"), fg=_get_c("ACCENT"),
                     font=F_BODY_B, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=desc, bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                     font=F_BODY, anchor="w").pack(side="left")
