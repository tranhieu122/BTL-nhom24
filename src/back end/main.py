#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
He Thong Quan Ly Phong Hoc - Nhom 24
Thanh vien: Tran Trung Hieu · Nguyen Huy Hai · Nguyen Tuan Minh
Entry point: khoi dong ung dung va day du toan bo module.
"""

from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# ── Load .env file (python-dotenv) ─────────────────────────────────────────
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_ENV_FILE, override=False)
except ImportError:
    pass   # python-dotenv not installed → fall back to os.environ / defaults

# Make `src/font-end` importable so `gui.*` modules can be loaded.
ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "font-end"
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from controllers.auth_controller import AuthController
from controllers.booking_controller import BookingController
from controllers.equipment_controller import EquipmentController
from controllers.notification_controller import NotificationController
from controllers.report_controller import ReportController
from controllers.room_controller import RoomController
from controllers.room_feedback_controller import RoomFeedbackController
from controllers.schedule_rule_controller import ScheduleRuleController
from controllers.user_controller import UserController

from gui.theme import apply_theme
from gui.profile_gui import ProfileDialog
from gui.booking_form_gui import BookingFormFrame
from gui.booking_list_gui import BookingListFrame
from gui.dashboard_gui import DashboardFrame
from gui.equipment_gui import EquipmentManagementFrame
from gui.login_gui import LoginFrame
from gui.notification_gui import NotificationFrame
from gui.report_gui import ReportFrame
from gui.room_feedback_gui import RoomIssueManagementFrame
from gui.room_gui import RoomManagementFrame
from gui.schedule_gui import ScheduleFrame
from gui.recurring_schedule_gui import RecurringScheduleFrame
from gui.user_gui import UserManagementFrame

# ── Layout ───────────────────────────────────────────────────────────────────
SIDEBAR_W = 240
TOPBAR_H  = 56

# ── Sidebar palette — Indigo/Slate ────────────────────────────────────────
SB_BG     = "#1e1b4b"    # Indigo 950
SB_HOVER  = "#312e81"    # Indigo 900
SB_ACTIVE = "#3730a3"    # Indigo 800
SB_ACCENT = "#818cf8"    # Indigo 400
SB_TEXT   = "#e0e7ff"    # Indigo 100
SB_MUTED  = "#6366f1"    # Indigo 500
SB_SECT   = "#312e81"    # Indigo 900 (dividers/section bg)

# ── Top-bar palette ───────────────────────────────────────────────────────────
TP_BG     = "#ffffff"
TP_BORDER = "#e2e8f0"
TP_TEXT   = "#1e293b"
TP_MUTED  = "#64748b"
C_BG      = "#f8fafc"    # Slate 50

# ── Role colours ─────────────────────────────────────────────────────────────
ROLE_CHIP = {
    "Admin":      ("#eef2ff", "#4f46e5"),   # Indigo chip
    "Giang vien": ("#dcfce7", "#15803d"),
    "Sinh vien":  ("#fef9c3", "#854d0e"),
}
ROLE_AVATAR = {
    "Admin":      "#4f46e5",   # Indigo 600
    "Giang vien": "#16a34a",
    "Sinh vien":  "#b45309",
}

# ── Nav: (label, key, icon).  key=="---" → section header ────────────────────
NAV_ALL = [
    ("Trang chu",       "dashboard",           "🏠"),
    ("Dat phong",       "booking_form",        "📝"),
    ("Danh sach dat",   "booking_list",        "📋"),
    ("Lich bieu",       "schedule",            "📆"),
    ("Lich day chu ky", "recurring_schedule",  "🔁"),
    ("Thong bao",       "notifications",       "🔔"),
    ("QUAN TRI",        "---",                 None),
    ("Quan ly phong",   "rooms",               "🏫"),
    ("Nguoi dung",      "users",               "👥"),
    ("Thiet bi",        "equipment",           "🔧"),
    ("Bao cao",         "report",              "📊"),
    ("Bao loi phong",   "room_issues",         "🚨"),
]

NAV_GV_SV = [
    ("Trang chu",       "dashboard",           "🏠"),
    ("Dat phong",       "booking_form",        "📝"),
    ("Lich su dat",     "booking_list",        "📋"),
    ("Lich bieu",       "schedule",            "📆"),
    ("Lich day chu ky", "recurring_schedule",  "🔁"),
    ("Thong bao",       "notifications",       "🔔"),
    ("Phong hoc",       "rooms",               "🏫"),
]

PAGE_TITLES = {
    "dashboard":           "Trang chu",
    "rooms":               "Quan ly phong hoc",
    "booking_form":        "Dat phong hoc",
    "booking_list":        "Danh sach dat phong",
    "users":               "Quan ly nguoi dung",
    "equipment":           "Quan ly thiet bi",
    "report":              "Bao cao thong ke",
    "schedule":            "Lich bieu phong hoc",
    "recurring_schedule":  "Lich day theo chu ky tuan",
    "room_issues":         "Bao cao su co phong",
    "notifications":       "Thong bao noi bo",
}


def _initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"


# ── App root ──────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("He Thong Quan Ly Phong Hoc")
        self.geometry("1280x780")
        self.minsize(960, 600)
        self.configure(bg=C_BG)
        apply_theme(ttk.Style())
        self._center()

        # ── Controllers (shared singletons) ───────────────────────────────────
        self.auth_ctrl   = AuthController()
        self.room_ctrl   = RoomController()
        self.booking_ctrl = BookingController()
        self.user_ctrl   = UserController()
        self.equip_ctrl  = EquipmentController()
        self.feedback_ctrl = RoomFeedbackController()
        self.report_ctrl = ReportController(
            self.room_ctrl, self.booking_ctrl,
            self.user_ctrl, self.equip_ctrl)
        self.schedule_rule_ctrl = ScheduleRuleController()
        self.notif_ctrl = NotificationController()
        try:
            from database.sqlite_db import backup_database
            backup_database()
        except Exception:
            pass

        self.current_user = None
        self._show_login()

    def _center(self) -> None:
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"1280x780+{(sw-1280)//2}+{(sh-780)//2}")

    def _show_login(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        LoginFrame(self, on_login=self._do_login,
                   auth_controller=self.auth_ctrl).pack(fill="both", expand=True)

    def _do_login(self, username: str, password: str) -> None:
        user = self.auth_ctrl.authenticate(username, password)
        if user is None:
            # LoginFrame._submit detects failure by checking if it still exists
            return
        self.current_user = user
        for w in self.winfo_children():
            w.destroy()
        MainShell(self).pack(fill="both", expand=True)

    def logout(self) -> None:
        self.current_user = None
        self._show_login()


# ── Main shell (TopBar + Sidebar + Content) ───────────────────────────────────

class MainShell(tk.Frame):
    def __init__(self, app: App) -> None:
        super().__init__(app, bg=C_BG)
        self.app = app
        self._nav_parts: dict[str, dict] = {}
        self._active_key = ""
        self._page_lbl: tk.Label | None = None
        self._badge_host: tk.Label | None = None
        self._badge_lbl: tk.Label | None = None
        self._notif_badge_host: tk.Label | None = None
        self._notif_badge_lbl: tk.Label | None = None
        self._content: tk.Frame | None = None
        self._content_frame: tk.Frame | None = None
        self._sb_collapsed: bool = False
        self._sb_frame: tk.Frame | None = None
        self._sb_toggle_btn: tk.Button | None = None
        self._build()
        self._bind_shortcuts()
        self._navigate("dashboard")

    # ── Build ──────────────────────────────────────────────────────────────────
    def _build(self) -> None:
        self._build_topbar()
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        self._content_frame = tk.Frame(body, bg=C_BG)
        self._content_frame.pack(fill="both", expand=True)

    # ── TopBar ─────────────────────────────────────────────────────────────────
    def _build_topbar(self) -> None:
        # Outer wrapper with bottom shadow line
        tb_wrap = tk.Frame(self, bg=TP_BG)
        tb_wrap.pack(fill="x")
        tk.Frame(tb_wrap, bg="#e2e8f0", height=1).pack(fill="x", side="bottom")

        tb = tk.Frame(tb_wrap, bg=TP_BG, height=TOPBAR_H)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Left: logo + breadcrumb
        left = tk.Frame(tb, bg=TP_BG)
        left.pack(side="left", fill="y", padx=(16, 0))

        # Sidebar toggle button (≡ hamburger)
        self._sb_toggle_btn = tk.Button(
            left, text="☰", bg=TP_BG, fg="#4f46e5",
            font=("Segoe UI", 14), relief="flat", bd=0, cursor="hand2",
            activebackground="#eef2ff", activeforeground="#3730a3",
            command=self._toggle_sidebar)
        self._sb_toggle_btn.pack(side="left", pady=12, padx=(0, 8))
        self._sb_toggle_btn.bind("<Enter>",
            lambda _: self._sb_toggle_btn.config(bg="#eef2ff"))  # type: ignore
        self._sb_toggle_btn.bind("<Leave>",
            lambda _: self._sb_toggle_btn.config(bg=TP_BG))  # type: ignore

        # Logo badge with Indigo gradient
        logo_cv = tk.Canvas(left, width=36, height=36, bg=TP_BG,
                            highlightthickness=0)
        logo_cv.pack(side="left", pady=10)
        logo_cv.create_oval(1, 1, 35, 35, fill="#4f46e5", outline="#818cf8", width=1)
        logo_cv.create_text(18, 18, text="🏫", font=("Segoe UI", 14),
                            fill="white")

        tk.Label(left, text="  QLPH", bg=TP_BG, fg="#4f46e5",
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Frame(left, bg=TP_BORDER, width=1, height=24).pack(
            side="left", padx=14, fill="y", pady=16)

        # Breadcrumb: indigo chevron + page name
        tk.Label(left, text="›", bg=TP_BG, fg="#818cf8",
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=(0, 4))
        self._page_lbl = tk.Label(left, text="", bg=TP_BG, fg=TP_TEXT,
                                  font=("Segoe UI", 11, "bold"))
        self._page_lbl.pack(side="left")

        # Right: avatar + name + role chip + logout + clock
        right = tk.Frame(tb, bg=TP_BG)
        right.pack(side="right", fill="y", padx=16)

        # Live clock
        self._clock_lbl = tk.Label(right, text="", bg=TP_BG, fg=TP_MUTED,
                                    font=("Segoe UI", 9))
        self._clock_lbl.pack(side="right", padx=(0, 16), pady=18)
        self._tick_clock()

        lo = tk.Button(right, text="  Dang xuat  ", bg="#f8fafc", fg="#4f46e5",
                       font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                       bd=0, padx=10, pady=5,
                       activebackground="#eef2ff", activeforeground="#3730a3",
                       highlightthickness=1, highlightbackground="#c7d2fe",
                       command=self.app.logout)
        lo.pack(side="right", pady=14)
        lo.bind("<Enter>", lambda _: lo.config(bg="#eef2ff"))
        lo.bind("<Leave>", lambda _: lo.config(bg="#f8fafc"))

        tk.Frame(right, bg=TP_BORDER, width=1, height=24).pack(
            side="right", padx=12, fill="y", pady=16)

        user = self.app.current_user  # type: ignore
        chip_bg, chip_fg = ROLE_CHIP.get(user.role, ("#f1f5f9", "#475569")) # type: ignore
        av_color = ROLE_AVATAR.get(user.role, "#64748b") # type: ignore

        # Notification badge (admin only: pending bookings count)
        if user.role == "Admin":  # type: ignore
            badge_wrap = tk.Frame(right, bg=TP_BG)
            badge_wrap.pack(side="right", padx=(0, 4))
            bell = tk.Label(badge_wrap, text="🔔", bg=TP_BG,
                            font=("Segoe UI", 14), cursor="hand2")
            bell.pack()
            self._badge_host = bell
            self._refresh_pending_badge()
            bell.bind("<Button-1>", lambda _: self._navigate("booking_list"))

        # Internal notifications bell (all users)
        notif_wrap = tk.Frame(right, bg=TP_BG)
        notif_wrap.pack(side="right", padx=(0, 4))
        self._notif_badge_host = tk.Label(notif_wrap, text="📩", bg=TP_BG,
                                           font=("Segoe UI", 14), cursor="hand2")
        self._notif_badge_host.pack()
        self._refresh_notif_badge()
        self._notif_badge_host.bind("<Button-1>",
                                    lambda _: self._navigate("notifications"))

        tk.Label(right, text=f"  {user.role}  ", # type: ignore
                 bg=chip_bg, fg=chip_fg,
                 font=("Segoe UI", 8, "bold")).pack(side="right", pady=18)
        tk.Label(right, text=user.full_name, bg=TP_BG, fg=TP_TEXT, # pyright: ignore[reportOptionalMemberAccess]
                 font=("Segoe UI", 10, "bold")).pack(
            side="right", padx=(0, 8), pady=18)

        av = tk.Canvas(right, width=32, height=32, bg=TP_BG,
                       highlightthickness=0, cursor="hand2")
        av.pack(side="right", pady=12, padx=(0, 4))
        av.create_oval(1, 1, 31, 31, fill=av_color, outline="")
        av.create_text(16, 16, text=_initials(user.full_name), # type: ignore
                       fill="white", font=("Segoe UI", 10, "bold"))
        av.bind("<Button-1>", lambda _: ProfileDialog(
            self, self.app.current_user, self.app.auth_ctrl))
        # Tooltip hint
        av.bind("<Enter>", lambda _: av.config(highlightthickness=2,
                                                highlightbackground=SB_ACCENT))
        av.bind("<Leave>", lambda _: av.config(highlightthickness=0))

        # Indigo accent underline on topbar
        tk.Frame(tb_wrap, bg="#4f46e5", height=2).pack(fill="x", side="bottom")

    def _tick_clock(self) -> None:
        """Update the live clock label every second."""
        import datetime as _dt
        if not self.winfo_exists():
            return
        now = _dt.datetime.now()
        self._clock_lbl.config(
            text=now.strftime("%H:%M:%S  |  %d/%m/%Y"))
        self.after(1000, self._tick_clock)

    def _pending_count(self) -> int:
        try:
            return len([
                b for b in self.app.booking_ctrl.list_bookings(from_today=False)
                if getattr(b, "status", "") == "Cho duyet"
            ])
        except Exception:
            return 0

    def _refresh_pending_badge(self) -> None:
        if self._badge_host is None:
            return
        pending_count = self._pending_count()

        if pending_count <= 0:
            if self._badge_lbl is not None:
                self._badge_lbl.destroy()
                self._badge_lbl = None
            return

        if self._badge_lbl is None:
            self._badge_lbl = tk.Label(
                self._badge_host.master,
                bg="#dc2626",
                fg="white",
                font=("Segoe UI", 7, "bold"),
                width=2,
            )
            self._badge_lbl.place(
                in_=self._badge_host,
                relx=1.0,
                rely=0.0,
                anchor="ne",
                x=4,
                y=-2,
            )

        self._badge_lbl.config(text=str(pending_count))

    def _refresh_notif_badge(self) -> None:
        """Update the 📩 bell badge with unread notification count."""
        if self._notif_badge_host is None or not self.app.current_user:
            return
        try:
            count = self.app.notif_ctrl.count_unread(
                self.app.current_user.user_id)
        except Exception:
            count = 0

        if count <= 0:
            if self._notif_badge_lbl is not None:
                self._notif_badge_lbl.destroy()
                self._notif_badge_lbl = None
            return

        if self._notif_badge_lbl is None:
            self._notif_badge_lbl = tk.Label(
                self._notif_badge_host.master,
                bg="#4f46e5", fg="white",
                font=("Segoe UI", 7, "bold"), width=2,
            )
            self._notif_badge_lbl.place(
                in_=self._notif_badge_host,
                relx=1.0, rely=0.0, anchor="ne", x=4, y=-2,
            )
        self._notif_badge_lbl.config(text=str(count))

    # ── Sidebar ────────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent: tk.Frame) -> None:
        sb = tk.Frame(parent, bg=SB_BG, width=SIDEBAR_W)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        self._sb_frame = sb  # save reference for collapse/expand

        # ── Logo strip with gradient canvas ──────────────────────────────────
        logo_bg = tk.Canvas(sb, width=SIDEBAR_W, height=72,
                            bg=SB_BG, highlightthickness=0)
        logo_bg.pack(fill="x")

        def _draw_logo_bg(e=None):
            logo_bg.delete("all")
            w = logo_bg.winfo_width() or SIDEBAR_W
            # Gradient: Indigo 950 → Indigo 900
            steps = 16
            for i in range(steps):
                y0 = i * 72 // steps
                y1 = (i + 1) * 72 // steps
                # #1e1b4b → #312e81
                r = 0x1e + i * (0x31 - 0x1e) // steps
                g = 0x1b + i * (0x2e - 0x1b) // steps
                b = 0x4b + i * (0x81 - 0x4b) // steps
                logo_bg.create_rectangle(0, y0, w, y1,
                                         fill=f"#{r:02x}{g:02x}{b:02x}",
                                         outline="")
            # Icon circle with Indigo 600 bg
            logo_bg.create_oval(16, 16, 48, 48, fill="#4f46e5",
                                outline="#818cf8", width=1)
            logo_bg.create_text(32, 32, text="🏫", font=("Segoe UI", 16),
                                fill="white")
            logo_bg.create_text(58, 29, text="HT Quan Ly Phong Hoc",
                                font=("Segoe UI", 10, "bold"),
                                fill="#e0e7ff", anchor="w")
            logo_bg.create_text(58, 48, text="v2.0  •  Nhom 24",
                                font=("Segoe UI", 7),
                                fill="#6366f1", anchor="w")

        logo_bg.bind("<Configure>", _draw_logo_bg)
        logo_bg.after(20, _draw_logo_bg)

        tk.Frame(sb, bg="#312e81", height=1).pack(fill="x", padx=0)

        tk.Label(sb, text="MENU", bg=SB_BG, fg="#6366f1",
                 font=("Segoe UI", 8, "bold"), anchor="w",
                 padx=20, pady=8).pack(fill="x")

        # Nav items
        user = self.app.current_user  # type: ignore
        nav_items = NAV_ALL if user.role == "Admin" else NAV_GV_SV # type: ignore
        for label, key, icon in nav_items:
            if key == "---":
                self._section_header(sb, label)
            else:
                self._nav_item(sb, label, key, icon or "\u2022")

        # Spacer
        tk.Frame(sb, bg=SB_BG).pack(fill="both", expand=True)

        # Bottom user card
        self._bottom_user_card(sb)

    def _section_header(self, parent: tk.Frame, text: str) -> None:
        f = tk.Frame(parent, bg=SB_BG)
        f.pack(fill="x", pady=(14, 2))
        tk.Frame(f, bg=SB_SECT, height=1).pack(fill="x", padx=18, pady=(0, 8))
        tk.Label(f, text=text, bg=SB_BG, fg="#6366f1",
                 font=("Segoe UI", 8, "bold"),
                 anchor="w", padx=20, pady=2).pack(fill="x")

    def _nav_item(self, parent: tk.Frame, label: str,
                  key: str, icon: str) -> None:
        row = tk.Frame(parent, bg=SB_BG, cursor="hand2")
        row.pack(fill="x")

        # Left accent bar (4px, colored when active)
        accent = tk.Frame(row, bg=SB_BG, width=4)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(row, bg=SB_BG, padx=12, pady=9)
        inner.pack(side="left", fill="x", expand=True)

        # Icon chip canvas
        icon_cv = tk.Canvas(inner, width=28, height=28, bg=SB_BG,
                            highlightthickness=0)
        icon_cv.pack(side="left", padx=(0, 10))
        icon_cv.create_text(14, 14, text=icon, font=("Segoe UI", 13),
                            fill="#818cf8", tags="ico")

        text_lbl = tk.Label(inner, text=label, bg=SB_BG, fg=SB_TEXT,
                            font=("Segoe UI", 10), anchor="w")
        text_lbl.pack(side="left", fill="x")

        self._nav_parts[key] = {
            "row": row, "inner": inner,
            "icon_cv": icon_cv, "text": text_lbl, "accent": accent,
        }

        def on_enter(_e, k=key):
            if k != self._active_key:
                p = self._nav_parts[k]
                for w in (p["row"], p["inner"]):
                    w.config(bg=SB_HOVER)
                p["icon_cv"].config(bg=SB_HOVER)
                p["text"].config(bg=SB_HOVER)

        def on_leave(_e, k=key):
            if k != self._active_key:
                p = self._nav_parts[k]
                for w in (p["row"], p["inner"]):
                    w.config(bg=SB_BG)
                p["icon_cv"].config(bg=SB_BG)
                p["text"].config(bg=SB_BG)

        def on_click(_e, k=key):
            self._navigate(k)

        for w in (row, inner, icon_cv, text_lbl):
            w.bind("<Enter>",    on_enter)
            w.bind("<Leave>",    on_leave)
            w.bind("<Button-1>", on_click)

    def _bottom_user_card(self, parent: tk.Frame) -> None:
        tk.Frame(parent, bg="#312e81", height=1).pack(fill="x")
        card = tk.Frame(parent, bg="#272165", padx=16, pady=12)
        card.pack(fill="x")

        user = self.app.current_user  # type: ignore
        av_color = ROLE_AVATAR.get(user.role, "#4f46e5") # type: ignore

        av = tk.Canvas(card, width=36, height=36,
                       bg="#272165", highlightthickness=0)
        av.pack(side="left", padx=(0, 10))
        av.create_oval(2, 2, 34, 34, fill=av_color, outline="#818cf8", width=1)
        av.create_text(18, 18, text=_initials(user.full_name),  # type: ignore
                       fill="white", font=("Segoe UI", 10, "bold"))

        info = tk.Frame(card, bg="#272165")
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=user.full_name, bg="#272165", fg="#e0e7ff",# type: ignore
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
        tk.Label(info, text=user.role, bg="#272165", fg="#818cf8",# type: ignore
                 font=("Segoe UI", 8), anchor="w").pack(fill="x")

    # ── Sidebar toggle ────────────────────────────────────────────────────────
    def _toggle_sidebar(self) -> None:
        if self._sb_frame is None:
            return
        self._sb_collapsed = not self._sb_collapsed
        if self._sb_collapsed:
            self._sb_frame.pack_forget()
        else:
            if self._content_frame is not None:
                self._sb_frame.pack(side="left", fill="y",
                                    before=self._content_frame)
            else:
                self._sb_frame.pack(side="left", fill="y")

    # ── Navigation ─────────────────────────────────────────────────────────────
    def _navigate(self, key: str) -> None:
        self._refresh_pending_badge()
        self._refresh_notif_badge()

        # Deactivate old
        if self._active_key in self._nav_parts:
            p = self._nav_parts[self._active_key]
            for w in (p["row"], p["inner"]):
                w.config(bg=SB_BG)
            p["icon_cv"].config(bg=SB_BG)
            p["icon_cv"].itemconfigure("ico", fill="#7fa8d4")
            p["text"].config(bg=SB_BG, fg=SB_TEXT, font=("Segoe UI", 10))
            p["accent"].config(bg=SB_BG)

        self._active_key = key

        # Activate new with glow effect
        if key in self._nav_parts:
            p = self._nav_parts[key]
            for w in (p["row"], p["inner"]):
                w.config(bg=SB_ACTIVE)
            p["icon_cv"].config(bg=SB_ACTIVE)
            # Draw icon inside filled Indigo 400 circle
            p["icon_cv"].delete("all")
            p["icon_cv"].create_oval(1, 1, 27, 27,
                                     fill="#818cf8", outline="",
                                     tags="bg_circle")
            icon_char = next(
                (ic for lbl, k, ic in
                 (NAV_ALL if getattr(self.app.current_user, 'role', '') == 'Admin'
                  else NAV_GV_SV)
                 if k == key), "•")
            p["icon_cv"].create_text(14, 14, text=icon_char,
                                     font=("Segoe UI", 12),
                                     fill="white", tags="ico")
            p["text"].config(bg=SB_ACTIVE, fg="white",
                             font=("Segoe UI", 10, "bold"))
            p["accent"].config(bg=SB_ACCENT)

        # Update topbar breadcrumb
        if self._page_lbl:
            self._page_lbl.config(text=PAGE_TITLES.get(key, ""))

        # Swap content
        if self._content is not None:
            self._content.destroy()

        app = self.app
        if key == "dashboard":
            frame = DashboardFrame(self._content_frame,
                                   app.report_ctrl, app.booking_ctrl,
                                   current_user=app.current_user)
        elif key == "rooms":
            frame = RoomManagementFrame(self._content_frame, app.room_ctrl,
                                        app.booking_ctrl, app.feedback_ctrl, app.current_user)
        elif key == "booking_form":
            frame = BookingFormFrame(
                self._content_frame, app.booking_ctrl, app.room_ctrl,
                app.current_user,
                on_booking_created=lambda: self._navigate("booking_list"),
                equipment_controller=app.equip_ctrl)
        elif key in ("booking_list", "lich_su_dat"):
            frame = BookingListFrame(self._content_frame,
                                     app.booking_ctrl, app.current_user,
                                     room_controller=app.room_ctrl)
        elif key == "users":
            frame = UserManagementFrame(self._content_frame, app.user_ctrl)
        elif key == "equipment":
            frame = EquipmentManagementFrame(self._content_frame,
                                             app.equip_ctrl, app.room_ctrl)
        elif key == "report":
            frame = ReportFrame(self._content_frame, app.report_ctrl)
        elif key == "room_issues":
            frame = RoomIssueManagementFrame(self._content_frame, app.feedback_ctrl)
        elif key == "notifications":
            frame = NotificationFrame(self._content_frame, app.notif_ctrl,
                                      app.current_user,
                                      user_controller=app.user_ctrl)
        elif key in ("schedule", "lich_bieu"):
            frame = ScheduleFrame(self._content_frame,
                                  app.booking_ctrl, app.room_ctrl)
        elif key == "recurring_schedule":
            frame = RecurringScheduleFrame(
                self._content_frame,
                app.schedule_rule_ctrl,
                app.room_ctrl,
                app.user_ctrl,
                current_user=app.current_user,
            )
        else:
            frame = tk.Frame(self._content_frame, bg=C_BG)
            tk.Label(frame, text=f"Trang '{key}' dang phat trien.",
                     bg=C_BG, fg="#94a3b8",
                     font=("Segoe UI", 14)).pack(expand=True)

        frame.pack(fill="both", expand=True)
        self._content = frame

    # ── Keyboard shortcuts ────────────────────────────────────────────────────
    def _bind_shortcuts(self) -> None:
        app = self.app
        app.bind_all("<Control-Home>",  lambda _: self._navigate("dashboard"))
        app.bind_all("<F5>",            lambda _: self._navigate(self._active_key))
        app.bind_all("<Control-d>",     lambda _: self._navigate("dashboard"))
        app.bind_all("<Control-b>",     lambda _: self._navigate("booking_form"))
        app.bind_all("<Control-l>",     lambda _: self._navigate("booking_list"))
        app.bind_all("<Control-backslash>", lambda _: self._toggle_sidebar())
        app.bind_all("<F11>",
            lambda _: app.attributes("-fullscreen",
                                      not app.attributes("-fullscreen")))
        app.bind_all("<Escape>",
            lambda _: app.attributes("-fullscreen", False) \
                       if app.attributes("-fullscreen") else None)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from utils.logger import get_logger as _gl
    _log = _gl("main")
    _log.info("Application starting")
    try:
        App().mainloop()
        _log.info("Application exited normally")
    except Exception:
        _log.critical("Unhandled exception — application crashed", exc_info=True)
        messagebox.showerror(
            "Loi khong mong muon",
            "Ung dung gap su co nghiem trong.\n"
            "Chi tiet da duoc luu vao file logs/app.log."
        )
        sys.exit(1)
