#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ Thống Quản Lý Đặt Phòng Học – Nhóm 24
Thành viên: Trần Trung Hiếu · Nguyễn Huy Hải · Nguyễn Tuấn Minh
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# ─── PALETTE ──────────────────────────────────────────────────────────────────
C_DARK      = "#1a2f5e"   # sidebar / dark header
C_PRIMARY   = "#2255a4"   # primary blue (topbar, table headers, buttons)
C_LIGHT     = "#4a8ecb"   # lighter blue (sidebar hover/active)
C_BG        = "#f4f6fb"   # page background
C_WHITE     = "#ffffff"
C_GRAY      = "#e8ecf1"   # alternating row / border
C_TEXT      = "#222222"

C_CARD1     = "#cce5ff"   # stat card – blue
C_CARD2     = "#d4edda"   # stat card – green
C_CARD3     = "#fff3cd"   # stat card – yellow
C_CARD4     = "#f8d7da"   # stat card – pink/red

C_GREEN     = "#28a745"
C_ORANGE    = "#fd7e14"
C_RED       = "#dc3545"
C_YELLOW    = "#ffc107"

SIDEBAR_W   = 200
TOPBAR_H    = 48

FONT_PAGE   = ("Arial", 15, "bold")
FONT_HDR    = ("Arial", 10, "bold")
FONT_NORMAL = ("Arial", 10)
FONT_SMALL  = ("Arial", 9)

# ─── MOCK DATA ────────────────────────────────────────────────────────────────
MOCK_ACCOUNTS = [
    {"id": "U001", "ten": "Nguyễn Văn A",  "vaitro": "Admin",       "email": "admin@uni.edu.vn",   "sdt": "0901234567", "tt": "Hoạt động"},
    {"id": "U002", "ten": "Trần Thị B",    "vaitro": "Giảng viên",  "email": "b@uni.edu.vn",       "sdt": "0912345678", "tt": "Hoạt động"},
    {"id": "U003", "ten": "Nguyễn Văn C",  "vaitro": "Giảng viên",  "email": "c@uni.edu.vn",       "sdt": "0923456789", "tt": "Hoạt động"},
    {"id": "U004", "ten": "Lê Thị D",      "vaitro": "Sinh viên",   "email": "d@sv.uni.edu.vn",    "sdt": "0934567890", "tt": "Hoạt động"},
    {"id": "U005", "ten": "Phạm Văn E",    "vaitro": "Sinh viên",   "email": "e@sv.uni.edu.vn",    "sdt": "0945678901", "tt": "Hoạt động"},
    {"id": "U006", "ten": "Hoàng Văn F",   "vaitro": "Sinh viên",   "email": "f@sv.uni.edu.vn",    "sdt": "0956789012", "tt": "Khóa"},
]

MOCK_ROOMS = [
    {"id": "P101", "ten": "Phòng 101",  "sc": 50,  "loai": "Phòng học",    "tb": "Máy chiếu, Điều hòa",                "tt": "Hoạt động"},
    {"id": "P202", "ten": "Phòng 202",  "sc": 40,  "loai": "Phòng máy",    "tb": "Máy tính, Máy chiếu",                "tt": "Hoạt động"},
    {"id": "P305", "ten": "Phòng 305",  "sc": 60,  "loai": "Hội trường",   "tb": "Micro, Âm thanh, Máy chiếu",         "tt": "Bảo trì"},
    {"id": "P306", "ten": "Phòng 306",  "sc": 20,  "loai": "Phòng seminar","tb": "TV 65\", Bảng trắng",                "tt": "Hoạt động"},
    {"id": "P401", "ten": "Phòng 401",  "sc": 45,  "loai": "Phòng học",    "tb": "Máy chiếu, Điều hòa, Bảng tương tác","tt": "Hoạt động"},
    {"id": "P402", "ten": "Phòng 402",  "sc": 30,  "loai": "Phòng máy",    "tb": "30 máy tính, Điều hòa",              "tt": "Hoạt động"},
]

MOCK_BOOKINGS = [
    {"id": "DPH001", "nguoidat": "Trần Thị B",   "phong": "P101", "ngay": "14/04/2026", "ca": "Ca 1", "mucdich": "Dạy học – Lập trình",    "tt": "Đã duyệt"},
    {"id": "DPH002", "nguoidat": "Nguyễn Văn C",  "phong": "P202", "ngay": "14/04/2026", "ca": "Ca 2", "mucdich": "Thực hành CSDL",          "tt": "Chờ duyệt"},
    {"id": "DPH003", "nguoidat": "Lê Thị D",      "phong": "P305", "ngay": "15/04/2026", "ca": "Ca 3", "mucdich": "Hội thảo chuyên đề",      "tt": "Từ chối"},
    {"id": "DPH004", "nguoidat": "Phạm Văn E",    "phong": "P101", "ngay": "15/04/2026", "ca": "Ca 1", "mucdich": "Học nhóm",                "tt": "Đã duyệt"},
    {"id": "DPH005", "nguoidat": "Trần Thị B",    "phong": "P401", "ngay": "16/04/2026", "ca": "Ca 2", "mucdich": "Giảng dạy",               "tt": "Đã duyệt"},
    {"id": "DPH006", "nguoidat": "Nguyễn Văn C",  "phong": "P306", "ngay": "16/04/2026", "ca": "Ca 4", "mucdich": "Họp nhóm dự án",          "tt": "Chờ duyệt"},
    {"id": "DPH007", "nguoidat": "Hoàng Văn F",   "phong": "P402", "ngay": "17/04/2026", "ca": "Ca 3", "mucdich": "Thực hành lập trình",      "tt": "Đã duyệt"},
    {"id": "DPH008", "nguoidat": "Lê Thị D",      "phong": "P306", "ngay": "17/04/2026", "ca": "Ca 2", "mucdich": "Seminar sinh viên",        "tt": "Từ chối"},
]

MOCK_EQUIPMENT = [
    {"id": "TB001", "ten": "Máy chiếu Epson EB-X51", "loai": "Thiết bị chiếu",   "phong": "P101", "tt": "Hoạt động", "ngaymua": "01/01/2022"},
    {"id": "TB002", "ten": "Điều hòa Daikin 2HP",    "loai": "Điều hòa",          "phong": "P101", "tt": "Hoạt động", "ngaymua": "15/03/2021"},
    {"id": "TB003", "ten": "Máy chiếu Sony VPL-DX271","loai": "Thiết bị chiếu",   "phong": "P202", "tt": "Hoạt động", "ngaymua": "10/05/2022"},
    {"id": "TB004", "ten": "Bảng tương tác Smart",    "loai": "TB giảng dạy",      "phong": "P401", "tt": "Hoạt động", "ngaymua": "20/08/2023"},
    {"id": "TB005", "ten": "Máy tính Dell OptiPlex",  "loai": "Máy tính",          "phong": "P202", "tt": "Hoạt động", "ngaymua": "01/09/2020"},
    {"id": "TB006", "ten": "Hệ thống âm thanh JBL",   "loai": "Âm thanh",          "phong": "P305", "tt": "Bảo trì",   "ngaymua": "01/06/2019"},
    {"id": "TB007", "ten": "Micro không dây Shure",   "loai": "Âm thanh",          "phong": "P305", "tt": "Hoạt động", "ngaymua": "12/12/2020"},
    {"id": "TB008", "ten": "TV Samsung 65\"",         "loai": "Màn hình",          "phong": "P306", "tt": "Hoạt động", "ngaymua": "05/07/2021"},
]

CA_HOC = [
    "Ca 1 (7:00–9:00)",
    "Ca 2 (9:15–11:15)",
    "Ca 3 (13:00–15:00)",
    "Ca 4 (15:15–17:15)",
    "Ca 5 (17:30–19:30)",
]

# ─── HELPER WIDGETS ───────────────────────────────────────────────────────────

def _style_treeview():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TV.Treeview.Heading",
                background=C_PRIMARY, foreground="white",
                font=("Arial", 10, "bold"), relief="flat", padding=6)
    s.map("TV.Treeview.Heading", background=[("active", C_LIGHT)])
    s.configure("TV.Treeview",
                rowheight=30, font=("Arial", 10),
                fieldbackground=C_WHITE, background=C_WHITE)
    s.map("TV.Treeview", background=[("selected", "#bbdefb")],
          foreground=[("selected", C_TEXT)])


def build_treeview(parent, columns, col_widths, heights=10):
    frame = tk.Frame(parent, bg=C_BG)
    tv = ttk.Treeview(frame, columns=columns, show="headings",
                      height=heights, style="TV.Treeview")
    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tv.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
    tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tv.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    for col, w in zip(columns, col_widths):
        tv.heading(col, text=col)
        tv.column(col, width=w, anchor="center", minwidth=40)
    tv.tag_configure("even", background=C_WHITE)
    tv.tag_configure("odd",  background="#f0f4fa")
    return frame, tv


def action_btn(parent, text, color, cmd):
    return tk.Button(parent, text=text, bg=color, fg="white",
                     font=("Arial", 9, "bold"), relief="flat",
                     padx=10, pady=5, cursor="hand2", command=cmd)


def labeled_entry(parent, label, var, readonly=False, width=28):
    f = tk.Frame(parent, bg=C_WHITE)
    tk.Label(f, text=label, bg=C_WHITE, fg=C_TEXT,
             font=FONT_NORMAL, anchor="w").pack(anchor="w", pady=(0, 2))
    state = "readonly" if readonly else "normal"
    e = tk.Entry(f, textvariable=var, font=FONT_NORMAL, width=width,
                 relief="solid", bd=1, state=state,
                 readonlybackground="#e9ecef")
    e.pack(fill="x", ipady=5)
    return f


def labeled_combo(parent, label, var, values, width=28):
    f = tk.Frame(parent, bg=C_WHITE)
    tk.Label(f, text=label, bg=C_WHITE, fg=C_TEXT,
             font=FONT_NORMAL, anchor="w").pack(anchor="w", pady=(0, 2))
    cb = ttk.Combobox(f, textvariable=var, values=values,
                      state="readonly", font=FONT_NORMAL, width=width)
    cb.pack(fill="x", ipady=3)
    return f


def labeled_text(parent, label, height=4, width=35):
    f = tk.Frame(parent, bg=C_WHITE)
    tk.Label(f, text=label, bg=C_WHITE, fg=C_TEXT,
             font=FONT_NORMAL, anchor="w").pack(anchor="w", pady=(0, 2))
    t = tk.Text(f, font=FONT_NORMAL, width=width, height=height,
                relief="solid", bd=1, wrap="word")
    t.pack(fill="x")
    return f, t


def separator(parent, color=C_GRAY):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", pady=8)


# ─── APPLICATION ROOT ─────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Đặt Phòng Học")
        self.geometry("1200x760")
        self.minsize(900, 600)
        self.configure(bg=C_BG)
        _style_treeview()
        self._center()
        self.current_user = None
        self._show_login()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - 1200) // 2
        y = (sh - 760)  // 2
        self.geometry(f"1200x760+{x}+{y}")

    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        LoginFrame(self).pack(fill="both", expand=True)

    def login(self, username, password):
        creds = {
            "admin":  {"name": "Nguyễn Văn A", "role": "Admin",      "code": "AD001"},
            "gv01":   {"name": "Trần Thị B",   "role": "Giảng viên", "code": "GV2001"},
            "sv01":   {"name": "Lê Thị D",     "role": "Sinh viên",  "code": "SV2001"},
        }
        passwords = {"admin": "admin123", "gv01": "gv123", "sv01": "sv123"}
        if username not in creds or passwords.get(username) != password:
            messagebox.showerror("Lỗi đăng nhập",
                                 "Sai tên đăng nhập hoặc mật khẩu!\n\n"
                                 "Demo:\n  admin / admin123\n  gv01 / gv123\n  sv01 / sv123")
            return
        self.current_user = creds[username]
        for w in self.winfo_children():
            w.destroy()
        MainShell(self).pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        self._show_login()


# ─── LOGIN ────────────────────────────────────────────────────────────────────

class LoginFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="white")
        self.app = app
        self._build()

    def _build(self):
        # ── Header bar ──────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C_CARD1, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Hệ Thống Quản Lý Đặt Phòng Học",
                 bg=C_CARD1, fg=C_DARK,
                 font=("Arial", 17, "bold")).pack(expand=True)

        # ── Center card ─────────────────────────────────────────────────────
        outer = tk.Frame(self, bg="white")
        outer.pack(expand=True)

        card = tk.Frame(outer, bg="#ebebeb", padx=45, pady=40,
                        relief="groove", bd=1)
        card.pack(padx=100, pady=60)

        tk.Label(card, text="ĐĂNG NHẬP", bg="#ebebeb", fg=C_DARK,
                 font=("Arial", 19, "bold")).pack(pady=(0, 28))

        # Username
        self.v_user = tk.StringVar()
        tk.Label(card, text="Tên đăng nhập:", bg="#ebebeb",
                 font=FONT_NORMAL).pack(anchor="w")
        tk.Entry(card, textvariable=self.v_user, font=("Arial", 11),
                 width=34, relief="solid", bd=1).pack(pady=(4, 14), ipady=6)

        # Password
        self.v_pass = tk.StringVar()
        tk.Label(card, text="Mật khẩu:", bg="#ebebeb",
                 font=FONT_NORMAL).pack(anchor="w")
        tk.Entry(card, textvariable=self.v_pass, font=("Arial", 11),
                 width=34, relief="solid", bd=1, show="*").pack(pady=(4, 14), ipady=6)

        # Role
        self.v_role = tk.StringVar(value="Admin / Giảng viên / Sinh viên")
        tk.Label(card, text="Vai trò:", bg="#ebebeb",
                 font=FONT_NORMAL).pack(anchor="w")
        ttk.Combobox(card, textvariable=self.v_role,
                     values=["Admin", "Giảng viên", "Sinh viên"],
                     state="readonly", font=("Arial", 11),
                     width=32).pack(pady=(4, 22), ipady=4)

        # Login button
        tk.Button(card, text="ĐĂNG NHẬP",
                  bg=C_PRIMARY, fg="white", font=("Arial", 12, "bold"),
                  width=30, pady=9, relief="flat", cursor="hand2",
                  command=self._login).pack()

        tk.Label(card,
                 text="Tài khoản demo:  admin / admin123   ·   gv01 / gv123   ·   sv01 / sv123",
                 bg="#ebebeb", fg="#777", font=("Arial", 8)).pack(pady=(14, 0))

        self.bind_all("<Return>", lambda _e: self._login())

    def _login(self):
        self.app.login(self.v_user.get().strip(), self.v_pass.get().strip())


# ─── MAIN SHELL ───────────────────────────────────────────────────────────────

class MainShell(tk.Frame):

    # Nav items per role  (label, icon, page_key)
    NAV_ADMIN = [
        ("Trang chủ",          "🏠", "home"),
        ("Quản lý phòng",      "🏫", "rooms"),
        ("Đặt phòng",          "📅", "book"),
        ("Danh sách đặt phòng","📋", "bookings"),
        ("Quản lý tài khoản",  "👤", "users"),
        ("Quản lý thiết bị",   "🔧", "equipment"),
        ("Báo cáo thống kê",   "📊", "stats"),
        ("Lịch biểu phòng",    "🗓", "schedule"),
    ]
    NAV_GV = [
        ("Trang chủ",     "🏠", "home"),
        ("Đặt phòng",     "📅", "book"),
        ("Lịch đặt của tôi","📋","bookings"),
        ("Thông báo",     "🔔", "notify"),
    ]
    NAV_SV = [
        ("Trang chủ",     "🏠", "home"),
        ("Đặt phòng",     "📅", "book"),
        ("Lịch đặt của tôi","📋","bookings"),
        ("Thông báo",     "🔔", "notify"),
    ]

    def __init__(self, app):
        super().__init__(app, bg=C_BG)
        self.app = app
        role = app.current_user["role"]
        self.nav = (self.NAV_ADMIN if role == "Admin"
                    else self.NAV_GV if role == "Giảng viên"
                    else self.NAV_SV)
        self.active_key = "home"
        self._nav_btns: dict[str, tk.Button] = {}
        self._build()
        self._show_page("home")

    # ── Layout ──────────────────────────────────────────────────────────────

    def _build(self):
        # Top bar
        tb = tk.Frame(self, bg=C_PRIMARY, height=TOPBAR_H)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)
        self._build_topbar(tb)

        # Body
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True)

        sb = tk.Frame(body, bg=C_DARK, width=SIDEBAR_W)
        sb.pack(fill="y", side="left")
        sb.pack_propagate(False)
        self._build_sidebar(sb)

        self.content = tk.Frame(body, bg=C_BG)
        self.content.pack(fill="both", expand=True)

    def _build_topbar(self, tb):
        tk.Label(tb, text="HỆ THỐNG QUẢN LÝ ĐẶT PHÒNG HỌC",
                 bg=C_PRIMARY, fg="white",
                 font=("Arial", 13, "bold")).pack(side="left", padx=20)
        u = self.app.current_user
        tk.Label(tb, text=f"{u['role']}: {u['name']}",
                 bg=C_PRIMARY, fg="white",
                 font=("Arial", 10)).pack(side="right", padx=(0, 8))
        tk.Label(tb, text="|", bg=C_PRIMARY, fg="white",
                 font=("Arial", 10)).pack(side="right")
        tk.Button(tb, text="Đăng xuất",
                  bg=C_RED, fg="white", font=("Arial", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2",
                  command=self.app.logout).pack(side="right", padx=8)

    def _build_sidebar(self, sb):
        tk.Frame(sb, bg=C_DARK, height=10).pack()
        for label, icon, key in self.nav:
            text = f"  {icon}  {label}"
            btn = tk.Button(sb, text=text,
                            bg=C_DARK, fg="white",
                            font=("Arial", 10), anchor="w",
                            relief="flat", bd=0,
                            padx=10, pady=11,
                            cursor="hand2",
                            command=lambda k=key: self._show_page(k))
            btn.pack(fill="x")
            btn.bind("<Enter>",
                     lambda e, b=btn, k=key: b.config(bg=C_PRIMARY)
                     if self.active_key != k else None)
            btn.bind("<Leave>",
                     lambda e, b=btn, k=key: b.config(
                         bg=C_LIGHT if self.active_key == k else C_DARK))
            self._nav_btns[key] = btn

    def _show_page(self, key):
        self.active_key = key
        for k, b in self._nav_btns.items():
            b.config(bg=C_LIGHT if k == key else C_DARK)
        for w in self.content.winfo_children():
            w.destroy()
        mapping = {
            "home":      HomePage,
            "rooms":     RoomManagementPage,
            "book":      BookingFormPage,
            "bookings":  BookingListPage,
            "users":     UserManagementPage,
            "equipment": EquipmentPage,
            "stats":     StatisticsPage,
            "schedule":  SchedulePage,
            "notify":    NotifyPage,
        }
        cls = mapping.get(key, HomePage)
        cls(self.content, self.app).pack(fill="both", expand=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════════

class _BasePage(tk.Frame):
    """Scrollable base page."""
    def __init__(self, parent, app, padx=28, pady=20):
        super().__init__(parent, bg=C_BG)
        self.app = app
        canvas = tk.Canvas(self, bg=C_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._inner = tk.Frame(canvas, bg=C_BG, padx=padx, pady=pady)
        self._inner.bind("<Configure>",
                         lambda _e: canvas.configure(
                             scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

    def page_title(self, text):
        tk.Label(self._inner, text=text, bg=C_BG, fg=C_DARK,
                 font=FONT_PAGE).pack(anchor="w", pady=(0, 14))


# ─── HOME ─────────────────────────────────────────────────────────────────────

class HomePage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("TRANG CHỦ")
        self._build()

    def _build(self):
        p = self._inner

        # Stat cards
        card_row = tk.Frame(p, bg=C_BG)
        card_row.pack(fill="x", pady=(0, 20))
        cards = [
            ("Tổng số phòng", "42",  C_CARD1),
            ("Đặt phòng hôm nay", "15", C_CARD2),
            ("Chờ duyệt", "3",       C_CARD3),
            ("Từ chối", "2",         C_CARD4),
        ]
        for title, val, bg in cards:
            f = tk.Frame(card_row, bg=bg, width=170, height=105,
                         padx=18, pady=16)
            f.pack_propagate(False)
            f.pack(side="left", padx=(0, 12))
            tk.Label(f, text=title, bg=bg, fg=C_DARK,
                     font=("Arial", 10, "bold"),
                     wraplength=150, justify="center").pack()
            tk.Label(f, text=val, bg=bg, fg=C_DARK,
                     font=("Arial", 24, "bold")).pack(pady=(6, 0))

        # Recent bookings
        tk.Label(p, text="Đặt phòng gần đây", bg=C_BG, fg=C_DARK,
                 font=FONT_HDR).pack(anchor="w", pady=(0, 6))
        cols   = ("Mã đặt", "Phòng", "Người đặt", "Ngày", "Ca học", "Trạng thái")
        widths = [90, 70, 160, 110, 80, 120]
        tv_f, tv = build_treeview(p, cols, widths, heights=len(MOCK_BOOKINGS))
        for i, b in enumerate(MOCK_BOOKINGS):
            icon = {"Đã duyệt": "✅", "Chờ duyệt": "⏳", "Từ chối": "❌"}.get(b["tt"], "")
            tv.insert("", "end",
                      values=(b["id"], b["phong"], b["nguoidat"],
                              b["ngay"], b["ca"],
                              f"{icon} {b['tt']}"),
                      tags=("even" if i % 2 == 0 else "odd",))
        tv_f.pack(fill="x")


# ─── ROOM MANAGEMENT ──────────────────────────────────────────────────────────

class RoomManagementPage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("QUẢN LÝ PHÒNG HỌC")
        self._selected_room = None
        self._build()

    def _build(self):
        p = self._inner

        # Action bar
        ab = tk.Frame(p, bg=C_BG)
        ab.pack(fill="x", pady=(0, 12))
        action_btn(ab, "+ Thêm phòng", C_PRIMARY, self._add).pack(side="left", padx=(0, 8))
        action_btn(ab, "→ Sửa phòng",  C_ORANGE,  self._edit).pack(side="left", padx=(0, 8))
        action_btn(ab, "🗑 Xóa phòng", C_RED,     self._delete).pack(side="left")

        # Search
        self.v_search = tk.StringVar()
        sf = tk.Frame(ab, bg=C_BG)
        sf.pack(side="right")
        tk.Entry(sf, textvariable=self.v_search, font=FONT_NORMAL,
                 width=28, relief="solid", bd=1,
                 fg="#888").pack(side="left", ipady=5)
        self.v_search.set("🔍  Tìm kiếm phòng...")
        self.v_search.trace_add("write", lambda *_: self._load())

        # Table
        cols   = ("Mã phòng", "Tên phòng", "Sức chứa", "Loại phòng", "Trang thiết bị", "Trạng thái")
        widths = [90, 110, 90, 130, 260, 110]
        self.tv_f, self.tv = build_treeview(p, cols, widths, heights=12)
        self.tv_f.pack(fill="x", pady=(0, 14))
        self.tv.bind("<<TreeviewSelect>>", self._on_select)

        self._load()

        # Inline dialog area (hidden until add/edit)
        self.dialog_outer = tk.Frame(p, bg=C_BG)
        self.dialog_outer.pack(fill="x")

    def _load(self):
        self.tv.delete(*self.tv.get_children())
        q = self.v_search.get().strip().lower()
        skip = q in ("", "🔍  tìm kiếm phòng...")
        for i, r in enumerate(MOCK_ROOMS):
            if not skip and q not in r["id"].lower() and q not in r["ten"].lower():
                continue
            dot = "🟢" if r["tt"] == "Hoạt động" else "🔴"
            self.tv.insert("", "end",
                           values=(r["id"], r["ten"], r["sc"],
                                   r["loai"], r["tb"], f"{dot} {r['tt']}"),
                           tags=("even" if i % 2 == 0 else "odd",))

    def _on_select(self, _event):
        sel = self.tv.focus()
        if sel:
            self._selected_room = self.tv.item(sel, "values")[0]

    def _get_room(self):
        if not self._selected_room:
            return None
        return next((r for r in MOCK_ROOMS if r["id"] == self._selected_room), None)

    def _add(self):
        self._open_dialog(None)

    def _edit(self):
        r = self._get_room()
        if not r:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một phòng để sửa.")
            return
        self._open_dialog(r)

    def _delete(self):
        r = self._get_room()
        if not r:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một phòng để xóa.")
            return
        if messagebox.askyesno("Xác nhận", f"Xóa phòng {r['id']} – {r['ten']}?"):
            messagebox.showinfo("Đã xóa", f"Đã xóa phòng {r['id']}.")

    def _open_dialog(self, room):
        # Clear previous dialog
        for w in self.dialog_outer.winfo_children():
            w.destroy()

        title = "Dialog: Thêm / Sửa Phòng"
        dlg_header = tk.Frame(self.dialog_outer, bg="#fff3cd", pady=6)
        dlg_header.pack(fill="x")
        tk.Label(dlg_header, text=title, bg="#fff3cd", fg="#856404",
                 font=("Arial", 9, "italic")).pack()

        form = tk.Frame(self.dialog_outer, bg="#fffde7",
                        padx=20, pady=14, relief="solid", bd=1)
        form.pack(fill="x")

        v_id    = tk.StringVar(value=room["id"]   if room else "")
        v_ten   = tk.StringVar(value=room["ten"]  if room else "")
        v_sc    = tk.StringVar(value=str(room["sc"]) if room else "")
        v_loai  = tk.StringVar(value=room["loai"] if room else "Phòng học")
        v_tb    = tk.StringVar(value=room["tb"]   if room else "")

        fields = tk.Frame(form, bg="#fffde7")
        fields.pack(fill="x", pady=(0, 10))
        pairs = [
            ("Mã phòng:", v_id, False),
            ("Tên phòng:", v_ten, False),
            ("Sức chứa:", v_sc, False),
        ]
        for col_idx, (lbl, var, ro) in enumerate(pairs):
            fc = tk.Frame(fields, bg="#fffde7")
            fc.grid(row=0, column=col_idx, padx=(0, 20), sticky="w")
            tk.Label(fc, text=lbl, bg="#fffde7", font=FONT_SMALL).pack(anchor="w")
            tk.Entry(fc, textvariable=var, font=FONT_NORMAL, width=18,
                     relief="solid", bd=1,
                     state="readonly" if ro else "normal").pack(ipady=4)

        fc_loai = tk.Frame(fields, bg="#fffde7")
        fc_loai.grid(row=0, column=3, padx=(0, 20), sticky="w")
        tk.Label(fc_loai, text="Loại:", bg="#fffde7", font=FONT_SMALL).pack(anchor="w")
        ttk.Combobox(fc_loai, textvariable=v_loai,
                     values=["Phòng học", "Phòng máy", "Hội trường", "Phòng seminar"],
                     state="readonly", font=FONT_NORMAL, width=16).pack(ipady=3)

        fc_tb = tk.Frame(fields, bg="#fffde7")
        fc_tb.grid(row=0, column=4, padx=(0, 20), sticky="w")
        tk.Label(fc_tb, text="Thiết bị:", bg="#fffde7", font=FONT_SMALL).pack(anchor="w")
        tk.Entry(fc_tb, textvariable=v_tb, font=FONT_NORMAL, width=28,
                 relief="solid", bd=1).pack(ipady=4)

        def _save():
            messagebox.showinfo("Thành công",
                                f"Đã lưu phòng [{v_id.get()}] – {v_ten.get()}.")
            for w in self.dialog_outer.winfo_children():
                w.destroy()
            self._load()

        btns = tk.Frame(form, bg="#fffde7")
        btns.pack()
        action_btn(btns, "Lưu", C_PRIMARY, _save).pack(side="left", padx=(0, 8))
        action_btn(btns, "Hủy", "#6c757d",
                   lambda: [w.destroy()
                            for w in self.dialog_outer.winfo_children()]).pack(side="left")


# ─── BOOKING FORM ─────────────────────────────────────────────────────────────

class BookingFormPage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._build()

    def _build(self):
        p = self._inner

        # Outer card
        card = tk.Frame(p, bg="#f0f0f0", padx=40, pady=35,
                        relief="groove", bd=1)
        card.pack(fill="x", padx=20, pady=10)

        tk.Label(card, text="FORM ĐẶT PHÒNG HỌC",
                 bg="#f0f0f0", fg=C_DARK,
                 font=("Arial", 15, "bold")).pack(pady=(0, 20))

        # Two-column layout
        cols = tk.Frame(card, bg="#f0f0f0")
        cols.pack(fill="both", expand=True)
        left  = tk.Frame(cols, bg=C_WHITE, padx=20, pady=16,
                         relief="flat", bd=1,
                         highlightbackground=C_GRAY, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(cols, bg=C_WHITE, padx=20, pady=16,
                         relief="flat", bd=1,
                         highlightbackground=C_GRAY, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)

        # ── LEFT ────────────────────────────────────────────────────────────
        u = self.app.current_user
        self.v_name  = tk.StringVar(value=u["name"])
        self.v_code  = tk.StringVar(value=u.get("code", "GV2001"))
        self.v_room  = tk.StringVar(value="")
        self.v_date  = tk.StringVar(value=datetime.date.today().strftime("%d/%m/%Y"))

        labeled_entry(left, "Họ tên người đặt:", self.v_name,
                      readonly=True).pack(fill="x", pady=(0, 10))
        labeled_entry(left, "Mã số (MSSV / mã GV):", self.v_code,
                      readonly=True).pack(fill="x", pady=(0, 10))
        labeled_combo(left, "Chọn phòng:",
                      self.v_room,
                      [r["id"] + " – " + r["ten"] for r in MOCK_ROOMS
                       if r["tt"] == "Hoạt động"]).pack(fill="x", pady=(0, 10))
        labeled_entry(left, "Ngày đặt phòng:", self.v_date).pack(fill="x", pady=(0, 10))

        # Calendar placeholder
        cal_ph = tk.Frame(left, bg="#fff8e1", relief="solid", bd=1, height=100)
        cal_ph.pack(fill="x", pady=(4, 0))
        cal_ph.pack_propagate(False)
        tk.Label(cal_ph, text="[Lịch chọn ngày – tkcalendar]",
                 bg="#fff8e1", fg="#aaa", font=("Arial", 9, "italic")).pack(expand=True)

        # ── RIGHT ───────────────────────────────────────────────────────────
        self.v_shift = tk.StringVar(value=CA_HOC[0])
        labeled_combo(right, "Ca học:", self.v_shift, CA_HOC).pack(fill="x", pady=(0, 10))

        tk.Label(right, text="Các ca còn trống trong ngày:",
                 bg=C_WHITE, font=FONT_NORMAL).pack(anchor="w", pady=(0, 4))
        avail_box = tk.Frame(right, bg="#e8f4fd", relief="solid", bd=1,
                             padx=8, pady=8)
        avail_box.pack(fill="x", pady=(0, 10))
        shifts_info = [
            ("✅ Ca 1 (7:00–9:00)",    True),
            ("✅ Ca 2 (9:15–11:15)",   True),
            ("❌ Ca 3 (13:00–15:00) — Đã đặt", False),
            ("✅ Ca 4 (15:15–17:15)",  True),
            ("✅ Ca 5 (17:30–19:30)",  True),
        ]
        for lbl, avail in shifts_info:
            fg = C_GREEN if avail else C_RED
            tk.Label(avail_box, text=lbl, bg="#e8f4fd", fg=fg,
                     font=FONT_SMALL).pack(anchor="w")

        _, self.t_mucdich = labeled_text(right, "Mục đích sử dụng:", height=4)
        self.t_mucdich.pack_configure(pady=(0, 10))
        _, self.t_ghichu  = labeled_text(right, "Ghi chú thêm:", height=3)

        # ── Buttons ─────────────────────────────────────────────────────────
        btn_row = tk.Frame(card, bg="#f0f0f0")
        btn_row.pack(pady=(22, 0))
        tk.Button(btn_row, text="  GỬI YÊU CẦU ĐẶT PHÒNG  ",
                  bg=C_PRIMARY, fg="white", font=("Arial", 11, "bold"),
                  relief="flat", padx=20, pady=10, cursor="hand2",
                  command=self._submit).pack(side="left", padx=(0, 16))
        tk.Button(btn_row, text="  HỦY  ",
                  bg=C_RED, fg="white", font=("Arial", 11, "bold"),
                  relief="flat", padx=20, pady=10, cursor="hand2",
                  command=self._cancel).pack(side="left")

    def _submit(self):
        room = self.v_room.get()
        if not room:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn phòng học.")
            return
        messagebox.showinfo("Thành công",
                            f"Yêu cầu đặt phòng đã được gửi!\n"
                            f"Phòng: {room}\n"
                            f"Ngày: {self.v_date.get()}\n"
                            f"Ca: {self.v_shift.get()}\n\n"
                            "Vui lòng chờ quản trị viên duyệt.")

    def _cancel(self):
        self.v_room.set("")
        self.t_mucdich.delete("1.0", "end")
        self.t_ghichu.delete("1.0", "end")


# ─── BOOKING LIST ─────────────────────────────────────────────────────────────

class BookingListPage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("DANH SÁCH ĐẶT PHÒNG")
        self._build()

    def _build(self):
        p = self._inner

        # Filter bar
        fb = tk.Frame(p, bg=C_BG)
        fb.pack(fill="x", pady=(0, 12))

        self.v_date   = tk.StringVar(value="14/04/2026")
        self.v_froom  = tk.StringVar(value="Tất cả")
        self.v_status = tk.StringVar(value="Tất cả")

        f1 = tk.Frame(fb, bg=C_BG)
        f1.pack(side="left", padx=(0, 8))
        tk.Label(f1, text="Lọc theo ngày:", bg=C_BG, font=FONT_SMALL).pack(anchor="w")
        tk.Entry(f1, textvariable=self.v_date, font=FONT_NORMAL,
                 width=14, relief="solid", bd=1).pack(ipady=4)

        f2 = tk.Frame(fb, bg=C_BG)
        f2.pack(side="left", padx=(0, 8))
        tk.Label(f2, text="Lọc theo phòng:", bg=C_BG, font=FONT_SMALL).pack(anchor="w")
        ttk.Combobox(f2, textvariable=self.v_froom,
                     values=["Tất cả"] + [r["id"] for r in MOCK_ROOMS],
                     state="readonly", font=FONT_NORMAL, width=12).pack(ipady=3)

        f3 = tk.Frame(fb, bg=C_BG)
        f3.pack(side="left", padx=(0, 8))
        tk.Label(f3, text="Trạng thái:", bg=C_BG, font=FONT_SMALL).pack(anchor="w")
        ttk.Combobox(f3, textvariable=self.v_status,
                     values=["Tất cả", "Đã duyệt", "Chờ duyệt", "Từ chối"],
                     state="readonly", font=FONT_NORMAL, width=12).pack(ipady=3)

        btn_f = tk.Frame(fb, bg=C_BG)
        btn_f.pack(side="left", padx=(0, 8))
        tk.Label(btn_f, text=" ", bg=C_BG, font=FONT_SMALL).pack()
        action_btn(btn_f, "🔍 Tìm kiếm", C_PRIMARY, self._load).pack(ipady=2)

        btn_x = tk.Frame(fb, bg=C_BG)
        btn_x.pack(side="left")
        tk.Label(btn_x, text=" ", bg=C_BG, font=FONT_SMALL).pack()
        action_btn(btn_x, "📥 Xuất Excel", C_GREEN,
                   lambda: messagebox.showinfo("Xuất file",
                                               "Đã xuất báo cáo danh sách đặt phòng.xlsx")).pack(ipady=2)

        # Table
        cols   = ("Mã đặt", "Người đặt", "Phòng", "Ngày", "Ca học", "Mục đích", "Trạng thái", "Thao tác")
        widths = [88, 140, 70, 100, 80, 170, 110, 100]
        self.tv_f, self.tv = build_treeview(p, cols, widths, heights=12)
        self.tv_f.pack(fill="x")
        self._load()

        # Pagination
        pg = tk.Frame(p, bg=C_BG)
        pg.pack(pady=10)
        for t, cmd in [("< Trước", None), ("Trang 1 / 3", None), ("Tiếp >", None)]:
            tk.Button(pg, text=t, bg=C_GRAY, fg=C_TEXT,
                      font=FONT_SMALL, relief="flat", padx=8, pady=3,
                      cursor="hand2" if t != "Trang 1 / 3" else "arrow",
                      state="normal" if t != "Trang 1 / 3" else "disabled"
                      ).pack(side="left", padx=2)

    def _load(self):
        self.tv.delete(*self.tv.get_children())
        st_filter = self.v_status.get()
        rm_filter = self.v_froom.get()
        for i, b in enumerate(MOCK_BOOKINGS):
            if st_filter != "Tất cả" and b["tt"] != st_filter:
                continue
            if rm_filter != "Tất cả" and b["phong"] != rm_filter:
                continue
            icon = {"Đã duyệt": "✅", "Chờ duyệt": "⏳", "Từ chối": "❌"}.get(b["tt"], "")
            action = "[Duyệt][Từ chối]" if b["tt"] == "Chờ duyệt" else "[Xem]"
            self.tv.insert("", "end",
                           values=(b["id"], b["nguoidat"], b["phong"],
                                   b["ngay"], b["ca"], b["mucdich"],
                                   f"{icon} {b['tt']}", action),
                           tags=("even" if i % 2 == 0 else "odd",))


# ─── USER MANAGEMENT ──────────────────────────────────────────────────────────

class UserManagementPage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("QUẢN LÝ TÀI KHOẢN")
        self._build()

    def _build(self):
        p = self._inner

        ab = tk.Frame(p, bg=C_BG)
        ab.pack(fill="x", pady=(0, 12))
        action_btn(ab, "+ Thêm tài khoản", C_PRIMARY,
                   lambda: UserDialog(p, None)).pack(side="left", padx=(0, 8))

        cols   = ("Mã", "Họ tên", "Vai trò", "Email", "Số điện thoại", "Trạng thái", "Thao tác")
        widths = [70, 160, 110, 210, 120, 100, 100]
        tv_f, tv = build_treeview(p, cols, widths, heights=12)
        tv_f.pack(fill="x")
        for i, u in enumerate(MOCK_ACCOUNTS):
            dot = "🟢" if u["tt"] == "Hoạt động" else "🔴"
            tv.insert("", "end",
                      values=(u["id"], u["ten"], u["vaitro"],
                              u["email"], u["sdt"],
                              f"{dot} {u['tt']}", "Sửa | Xóa"),
                      tags=("even" if i % 2 == 0 else "odd",))


class UserDialog(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.title("Thêm tài khoản" if not user else "Sửa tài khoản")
        self.geometry("420x380")
        self.resizable(False, False)
        self.grab_set()
        self._build(user)

    def _build(self, user):
        self.configure(bg=C_WHITE)
        pad = {"fill": "x", "padx": 24, "pady": 6}
        v_ten   = tk.StringVar(value=user["ten"]   if user else "")
        v_email = tk.StringVar(value=user["email"] if user else "")
        v_sdt   = tk.StringVar(value=user["sdt"]   if user else "")
        v_role  = tk.StringVar(value=user["vaitro"] if user else "Sinh viên")

        for lbl, var in [("Họ tên:", v_ten), ("Email:", v_email), ("Số điện thoại:", v_sdt)]:
            f = tk.Frame(self, bg=C_WHITE)
            f.pack(**pad)
            tk.Label(f, text=lbl, bg=C_WHITE, width=16, anchor="w",
                     font=FONT_NORMAL).pack(side="left")
            tk.Entry(f, textvariable=var, font=FONT_NORMAL, width=24,
                     relief="solid", bd=1).pack(side="left", ipady=4)

        f_r = tk.Frame(self, bg=C_WHITE)
        f_r.pack(**pad)
        tk.Label(f_r, text="Vai trò:", bg=C_WHITE, width=16, anchor="w",
                 font=FONT_NORMAL).pack(side="left")
        ttk.Combobox(f_r, textvariable=v_role,
                     values=["Admin", "Giảng viên", "Sinh viên"],
                     state="readonly", font=FONT_NORMAL, width=22).pack(side="left", ipady=3)

        btns = tk.Frame(self, bg=C_WHITE)
        btns.pack(pady=20)
        action_btn(btns, "Lưu", C_PRIMARY,
                   lambda: [messagebox.showinfo("OK", "Đã lưu tài khoản."),
                            self.destroy()]).pack(side="left", padx=6)
        action_btn(btns, "Hủy", "#6c757d", self.destroy).pack(side="left", padx=6)


# ─── EQUIPMENT ────────────────────────────────────────────────────────────────

class EquipmentPage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("QUẢN LÝ THIẾT BỊ")
        self._build()

    def _build(self):
        p = self._inner

        ab = tk.Frame(p, bg=C_BG)
        ab.pack(fill="x", pady=(0, 12))
        action_btn(ab, "+ Thêm thiết bị", C_PRIMARY,
                   lambda: messagebox.showinfo("Thêm", "Form thêm thiết bị")).pack(side="left", padx=(0, 8))
        action_btn(ab, "Sửa", C_ORANGE,
                   lambda: messagebox.showinfo("Sửa", "Form sửa thiết bị")).pack(side="left", padx=(0, 8))
        action_btn(ab, "Xóa", C_RED,
                   lambda: messagebox.showinfo("Xóa", "Xác nhận xóa thiết bị")).pack(side="left")

        # Filter
        sf = tk.Frame(p, bg=C_BG)
        sf.pack(fill="x", pady=(0, 8))
        v_phong = tk.StringVar(value="Tất cả")
        tk.Label(sf, text="Lọc theo phòng:", bg=C_BG, font=FONT_NORMAL).pack(side="left")
        ttk.Combobox(sf, textvariable=v_phong,
                     values=["Tất cả"] + [r["id"] for r in MOCK_ROOMS],
                     state="readonly", font=FONT_NORMAL, width=12).pack(side="left", padx=8)
        action_btn(sf, "Lọc", C_PRIMARY,
                   lambda: None).pack(side="left")

        cols   = ("Mã TB", "Tên thiết bị", "Loại", "Phòng", "Trạng thái", "Ngày mua", "Thao tác")
        widths = [80, 220, 140, 70, 110, 100, 100]
        tv_f, tv = build_treeview(p, cols, widths, heights=12)
        tv_f.pack(fill="x")
        for i, e in enumerate(MOCK_EQUIPMENT):
            dot = "🟢" if e["tt"] == "Hoạt động" else "🔴"
            tv.insert("", "end",
                      values=(e["id"], e["ten"], e["loai"],
                              e["phong"], f"{dot} {e['tt']}",
                              e["ngaymua"], "Sửa | Xóa"),
                      tags=("even" if i % 2 == 0 else "odd",))


# ─── STATISTICS ───────────────────────────────────────────────────────────────

class StatisticsPage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("BÁO CÁO THỐNG KÊ")
        self._build()

    def _build(self):
        p = self._inner

        # Filter bar
        fb = tk.Frame(p, bg=C_BG)
        fb.pack(fill="x", pady=(0, 14))
        v_month = tk.StringVar(value="Tháng 4")
        v_year  = tk.StringVar(value="2026")
        for lbl, var, vals, w in [
            ("Tháng:", v_month, [f"Tháng {i}" for i in range(1, 13)], 10),
            ("Năm:",   v_year,  ["2024", "2025", "2026"], 8),
        ]:
            tk.Label(fb, text=lbl, bg=C_BG, font=FONT_NORMAL).pack(side="left", padx=(0, 4))
            ttk.Combobox(fb, textvariable=var, values=vals,
                         state="readonly", font=FONT_NORMAL, width=w).pack(side="left", padx=(0, 10))
        action_btn(fb, "Xem báo cáo", C_PRIMARY, lambda: None).pack(side="left", padx=(0, 8))
        action_btn(fb, "📥 Xuất Excel", C_GREEN,
                   lambda: messagebox.showinfo("Xuất", "Đã xuất file bao_cao.xlsx")).pack(side="left")

        # Two columns
        body = tk.Frame(p, bg=C_BG)
        body.pack(fill="both", expand=True)

        # Summary table
        left = tk.Frame(body, bg=C_BG)
        left.pack(side="left", fill="y", padx=(0, 20))
        tk.Label(left, text="Tổng hợp theo phòng", bg=C_BG, fg=C_DARK,
                 font=FONT_HDR).pack(anchor="w", pady=(0, 6))
        data = [("P101", 12, 10, 2, "83%"), ("P202", 9, 7, 2, "72%"),
                ("P305", 4,  2,  2, "48%"), ("P306", 8, 7, 1, "76%"),
                ("P401", 11, 10, 1, "85%"), ("P402", 7, 6, 1, "70%")]
        cols   = ("Phòng", "Tổng đặt", "Đã duyệt", "Từ chối", "Tỷ lệ SD")
        widths = [70, 80, 80, 80, 90]
        tv_f, tv = build_treeview(left, cols, widths, heights=8)
        tv_f.pack()
        for i, row in enumerate(data):
            tv.insert("", "end", values=row,
                      tags=("even" if i % 2 == 0 else "odd",))

        # Bar chart
        right = tk.Frame(body, bg=C_WHITE, padx=15, pady=15,
                         relief="flat", bd=1,
                         highlightbackground=C_GRAY, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Biểu đồ tỷ lệ sử dụng phòng (%)",
                 bg=C_WHITE, fg=C_DARK, font=FONT_HDR).pack(anchor="w", pady=(0, 8))
        self._canvas = tk.Canvas(right, bg=C_WHITE, height=230, highlightthickness=0)
        self._canvas.pack(fill="x", expand=True)
        right.after(50, lambda: self._draw_chart(data))

    def _draw_chart(self, data):
        c = self._canvas
        c.update_idletasks()
        W = c.winfo_width() or 380
        H = 210
        ml, mr, mb, mt = 38, 12, 36, 16
        bar_area_w = W - ml - mr
        n = len(data)
        gap = 10
        bar_w = max(20, (bar_area_w - gap * (n + 1)) // n)
        colors = [C_PRIMARY, C_LIGHT, C_GREEN, C_ORANGE, "#9b59b6", "#17a2b8"]
        for idx, row in enumerate(data):
            label = row[0]
            pct   = int(row[4].replace("%", ""))
            x0 = ml + gap + idx * (bar_w + gap)
            bh = int((H - mt - mb) * pct / 100)
            y0, y1 = H - mb - bh, H - mb
            c.create_rectangle(x0, y0, x0 + bar_w, y1,
                                fill=colors[idx % len(colors)], outline="")
            c.create_text(x0 + bar_w // 2, y0 - 8,
                          text=f"{pct}%", font=("Arial", 8), fill=C_TEXT)
            c.create_text(x0 + bar_w // 2, H - mb + 14,
                          text=label, font=("Arial", 8), fill=C_TEXT)
        # Axes
        c.create_line(ml, mt, ml, H - mb, fill="#ccc")
        c.create_line(ml, H - mb, W - mr, H - mb, fill="#ccc")
        for v in range(0, 101, 25):
            y = H - mb - int((H - mt - mb) * v / 100)
            c.create_line(ml - 4, y, W - mr, y, fill="#eee", dash=(3, 3))
            c.create_text(ml - 6, y, text=str(v),
                          font=("Arial", 7), fill="#999", anchor="e")


# ─── SCHEDULE ─────────────────────────────────────────────────────────────────

class SchedulePage(_BasePage):
    DAYS   = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    SHIFTS = ["Ca 1\n7:00–9:00", "Ca 2\n9:15–11:15",
              "Ca 3\n13:00–15:00", "Ca 4\n15:15–17:15", "Ca 5\n17:30–19:30"]
    # (day_idx, shift_idx): (room, person)
    SAMPLE = {
        (0, 0): ("P101", "Trần Thị B"),
        (0, 2): ("P202", "Nguyễn Văn C"),
        (1, 1): ("P305", "Lê Thị D"),
        (2, 0): ("P101", "Phạm Văn E"),
        (3, 3): ("P401", "Trần Thị B"),
        (4, 0): ("P306", "Nguyễn Văn C"),
        (4, 4): ("P402", "Hoàng Văn F"),
    }

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("LỊCH BIỂU PHÒNG HỌC")
        self._build()

    def _build(self):
        p = self._inner

        # Week nav
        nav = tk.Frame(p, bg=C_BG)
        nav.pack(fill="x", pady=(0, 12))
        self.v_week = tk.StringVar(value="Tuần 14/04/2026 – 20/04/2026")
        tk.Button(nav, text="◀", bg=C_PRIMARY, fg="white",
                  font=FONT_HDR, relief="flat", padx=10,
                  cursor="hand2").pack(side="left")
        tk.Label(nav, textvariable=self.v_week, bg=C_BG, fg=C_DARK,
                 font=FONT_HDR).pack(side="left", padx=12)
        tk.Button(nav, text="▶", bg=C_PRIMARY, fg="white",
                  font=FONT_HDR, relief="flat", padx=10,
                  cursor="hand2").pack(side="left")

        # Room filter
        rf = tk.Frame(p, bg=C_BG)
        rf.pack(fill="x", pady=(0, 10))
        v_r = tk.StringVar(value="Tất cả phòng")
        tk.Label(rf, text="Phòng:", bg=C_BG, font=FONT_NORMAL).pack(side="left")
        ttk.Combobox(rf, textvariable=v_r,
                     values=["Tất cả phòng"] + [r["id"] for r in MOCK_ROOMS],
                     state="readonly", font=FONT_NORMAL, width=14).pack(side="left", padx=8)

        # Grid
        grid_f = tk.Frame(p, bg=C_BG)
        grid_f.pack(fill="both", expand=True)

        CELL_W, CELL_H = 120, 58
        HDR_W = 90

        # Corner
        tk.Frame(grid_f, bg=C_PRIMARY, width=HDR_W, height=38,
                 relief="flat").grid(row=0, column=0, padx=1, pady=1)
        # Day headers
        for ci, day in enumerate(self.DAYS):
            tk.Label(grid_f, text=day, bg=C_PRIMARY, fg="white",
                     font=FONT_HDR, width=14, height=2,
                     relief="flat").grid(row=0, column=ci + 1, padx=1, pady=1)
        # Shift rows
        for ri, shift in enumerate(self.SHIFTS):
            tk.Label(grid_f, text=shift, bg=C_DARK, fg="white",
                     font=("Arial", 8, "bold"),
                     width=11, height=3,
                     justify="center", relief="flat").grid(
                         row=ri + 1, column=0, padx=1, pady=1)
            for ci in range(len(self.DAYS)):
                booking = self.SAMPLE.get((ci, ri))
                if booking:
                    cell_bg = C_CARD2
                    cell_text = f"{booking[0]}\n{booking[1]}"
                    fg = "#155724"
                else:
                    cell_bg = C_WHITE
                    cell_text = "Trống"
                    fg = "#888"
                tk.Label(grid_f, text=cell_text, bg=cell_bg, fg=fg,
                         font=("Arial", 8),
                         width=14, height=3,
                         relief="solid", bd=1,
                         justify="center").grid(
                             row=ri + 1, column=ci + 1, padx=1, pady=1)


# ─── NOTIFICATIONS ────────────────────────────────────────────────────────────

class NotifyPage(_BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_title("THÔNG BÁO")
        self._build()

    def _build(self):
        p = self._inner
        notices = [
            ("✅", "Yêu cầu đặt phòng DPH001 của bạn đã được duyệt.",  "14/04/2026 08:30", C_CARD2),
            ("⏳", "Yêu cầu đặt phòng DPH002 đang chờ xét duyệt.",     "14/04/2026 09:00", C_CARD3),
            ("❌", "Yêu cầu đặt phòng DPH003 đã bị từ chối.\nLý do: Phòng đang bảo trì.", "15/04/2026 10:15", C_CARD4),
            ("✅", "Yêu cầu đặt phòng DPH004 của bạn đã được duyệt.",  "15/04/2026 11:00", C_CARD2),
        ]
        for icon, msg, time, bg in notices:
            card = tk.Frame(p, bg=bg, padx=16, pady=12,
                            relief="flat", bd=1,
                            highlightbackground=C_GRAY, highlightthickness=1)
            card.pack(fill="x", pady=(0, 10))
            top = tk.Frame(card, bg=bg)
            top.pack(fill="x")
            tk.Label(top, text=f"{icon}  {msg}", bg=bg, fg=C_TEXT,
                     font=FONT_NORMAL, anchor="w",
                     justify="left", wraplength=700).pack(side="left")
            tk.Label(top, text=time, bg=bg, fg="#777",
                     font=FONT_SMALL).pack(side="right")


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
