# dashboard_gui.py  –  home / dashboard screen  (v2.0 pro-max)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
from typing import Any
from gui.theme import (C_BG, C_DARK, C_PRIMARY, C_SURFACE, C_BORDER,
                       C_MUTED,
                       F_SECTION,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, MiniProgressBar, btn, toast,
                       animate_count)

# Card colour palette: (bg, accent_fg, icon, label)
CARD_PALETTE = [
    ("#eef2ff", "#4f46e5", "🏫", "Tong phong"),         # Indigo
    ("#dcfce7", "#15803d", "📅", "Tong dat phong"),     # Green
    ("#fef3c7", "#b45309", "⏳", "Cho duyet"),         # Amber
    ("#fdf2f8", "#db2777", "🚫", "Tu choi"),           # Red
    ("#e0f2fe", "#0369a1", "👥", "Nguoi dung"),        # Sky
    ("#ede9fe", "#6d28d9", "🔧", "Thiet bi"),          # Violet
]

STATUS_COLOR = {
    "Da duyet":  "#16a34a",
    "Cho duyet": "#f59e0b",
    "Tu choi":   "#ec4899",
}


class DashboardFrame(tk.Frame):
    def __init__(self, master: tk.Misc, report_controller: Any,
                 booking_controller: Any,
                 booking_ctrl_approve: Any = None,
                 current_user: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.report_ctrl   = report_controller
        self.booking_ctrl  = booking_controller
        self.current_user  = current_user
        self._build()

    # ─────────────────────────────────────────────────────────────────────────
    def _build(self) -> None:
        page_header(self, "Tong quan he thong", "🏠").pack(fill="x")

        # Scrollable body
        canvas = tk.Canvas(self, bg=C_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)  # type: ignore[arg-type]
        body = tk.Frame(canvas, bg=C_BG)
        body.bind("<Configure>",
                  lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._body = body
        self._draw_cards(body)
        self._draw_quick_actions(body)
        self._draw_today_panel(body)
        self._draw_main_area(body)

    # ── Stat cards ────────────────────────────────────────────────────────────
    def _draw_cards(self, body: tk.Frame) -> None:
        grid = tk.Frame(body, bg=C_BG)
        grid.pack(fill="x", padx=20, pady=(6, 12))

        summary_values = list(self.report_ctrl.build_dashboard().values())
        bookings = self.booking_ctrl.list_bookings(from_today=False)
        total_b  = len(bookings) or 1

        # Nav targets for each card (click to navigate)
        CARD_NAV = ["rooms", "booking_list", "booking_list",
                    "booking_list", "users", "equipment"]

        for idx in range(6):
            bg, fg, icon, _ = CARD_PALETTE[idx]
            value = summary_values[idx] if idx < len(summary_values) else 0

            # Indigo-tinted shadow
            shadow = tk.Frame(grid, bg="#c7d2fe")
            shadow.grid(row=idx // 3, column=idx % 3,
                        sticky="nsew", padx=6, pady=6)

            card = tk.Frame(shadow, bg=bg, padx=18, pady=16, cursor="hand2")
            card.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

            # Hover effect
            def _on_enter(e: Any, c: Any = card, b: Any = bg) -> None:
                _darken = {"#eef2ff": "#e0e7ff", "#dcfce7": "#bbf7d0",
                           "#fef3c7": "#fde68a", "#fdf2f8": "#fbcfe8",
                           "#e0f2fe": "#bae6fd", "#ede9fe": "#ddd6fe"}
                c.config(bg=_darken.get(b, b))
            def _on_leave(e: Any, c: Any = card, b: Any = bg) -> None:
                c.config(bg=b)

            nav_key = CARD_NAV[idx] if idx < len(CARD_NAV) else "dashboard"

            def _on_click(e: Any, k: str = nav_key) -> None:
                w: Any = self.master
                while w is not None:
                    if hasattr(w, "_navigate"):
                        w._navigate(k)
                        return
                    w = getattr(w, "master", None)

            for widget in [card]:
                widget.bind("<Enter>",    _on_enter)
                widget.bind("<Leave>",    _on_leave)
                widget.bind("<Button-1>", _on_click)

            # Top row: icon circle + value
            top = tk.Frame(card, bg=bg)
            top.pack(fill="x")
            top.bind("<Button-1>", _on_click)

            # Colored icon circle
            ic = tk.Canvas(top, width=46, height=46, bg=bg,
                           highlightthickness=0, cursor="hand2")
            ic.pack(side="left")
            ic.create_oval(2, 2, 44, 44, fill=fg, outline="")
            ic.create_text(23, 23, text=icon, font=("Segoe UI", 18),
                           fill="white")
            ic.bind("<Button-1>", _on_click)

            val_lbl = tk.Label(top, text="0", bg=bg, fg=fg,
                               font=("Segoe UI", 32, "bold"),
                               cursor="hand2")
            val_lbl.pack(side="right", anchor="s", pady=(0, 2))
            val_lbl.bind("<Button-1>", _on_click)
            animate_count(val_lbl, int(value))

            _, lbl = CARD_PALETTE[idx][:2], CARD_PALETTE[idx][3]
            tk.Label(card, text=lbl, bg=bg, fg="#475569",
                     font=("Segoe UI", 9, "bold"), cursor="hand2").pack(
                anchor="w", pady=(8, 4))

            # Mini progress bar (% of total bookings for booking-related cards)
            if idx in (1, 2, 3):   # total bookings, pending, rejected
                pbar = MiniProgressBar(card, value, total_b,
                                       color=fg, height=4, width=160)
                pbar.configure(bg=bg)
                pbar.pack(anchor="w")

            # Percentage hint for booking cards
            if idx in (2, 3) and total_b > 1:
                pct = int(value / total_b * 100)
                tk.Label(card, text=f"{pct}% tong so",
                         bg=bg, fg=fg,
                         font=("Segoe UI", 8)).pack(anchor="w")

        for col in range(3):
            grid.grid_columnconfigure(col, weight=1)

    # ── Quick Actions ─────────────────────────────────────────────────────────
    def _draw_quick_actions(self, body: tk.Frame) -> None:
        from gui.theme import tooltip as _tooltip
        shadow = tk.Frame(body, bg="#c7d2fe")
        shadow.pack(fill="x", padx=20, pady=(0, 12))
        card = tk.Frame(shadow, bg=C_SURFACE, padx=16, pady=14)
        card.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        hdr = tk.Frame(card, bg=C_SURFACE)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Label(hdr, text="⚡  Thao tac nhanh",
                 bg=C_SURFACE, fg=C_DARK, font=F_SECTION).pack(side="left")

        def _nav(key: str) -> None:
            w: Any = self.master
            while w is not None:
                if hasattr(w, "_navigate"):
                    w._navigate(key)
                    return
                w = getattr(w, "master", None)

        # Refresh button
        def _refresh_all() -> None:
            toast(self, "Da lam moi du lieu!", kind="success")

        refresh_b = btn(hdr, "Lam moi", _refresh_all, variant="ghost", icon="🔄")
        refresh_b.pack(side="right")
        _tooltip(refresh_b, "Lam moi trang (F5)")

        actions_row = tk.Frame(card, bg=C_SURFACE)
        actions_row.pack(fill="x")

        ACTIONS = [
            ("📝  Dat phong",    "primary", "booking_form", "Dat phong hoc moi (Ctrl+B)"),
            ("📋  Danh sach dat", "outline", "booking_list", "Xem tat ca lich dat (Ctrl+L)"),
            ("📆  Lich bieu",    "outline",  "schedule",     "Xem lich theo tuan"),
            ("📊  Bao cao",      "outline",  "report",       "Thong ke va bao cao"),
            ("🏫  Phong hoc",   "outline",  "rooms",        "Quan ly phong hoc"),
        ]

        for label, variant, key, tip in ACTIONS:
            b = btn(actions_row, label, lambda k=key: _nav(k), variant=variant)
            b.pack(side="left", padx=(0, 8))
            _tooltip(b, tip)

    # ── Today's bookings mini-panel ───────────────────────────────────────────
    def _draw_today_panel(self, body: tk.Frame) -> None:
        today_str = dt.date.today().isoformat()
        today_bookings = [ # type: ignore
            b for b in (self.booking_ctrl.list_bookings(from_today=False) or []) # type: ignore
            if b.booking_date == today_str # type: ignore
        ]

        shadow = tk.Frame(body, bg="#c7d2fe")
        shadow.pack(fill="x", padx=20, pady=(0, 12))
        card = tk.Frame(shadow, bg=C_SURFACE, padx=16, pady=14)
        card.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        hdr = tk.Frame(card, bg=C_SURFACE)
        hdr.pack(fill="x", pady=(0, 10))
        today_disp = dt.date.today().strftime("%A, %d/%m/%Y")
        tk.Label(hdr, text=f"📅  Lich hom nay  —  {today_disp}",
                 bg=C_SURFACE, fg=C_DARK, font=F_SECTION).pack(side="left")
        count_bg = "#dcfce7" if today_bookings else "#f1f5f9"
        count_fg = "#15803d" if today_bookings else C_MUTED
        tk.Label(hdr, text=f"  {len(today_bookings)} lich  ", # type: ignore
                 bg=count_bg, fg=count_fg,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=8)

        if not today_bookings:
            empty = tk.Frame(card, bg="#f8fafc", highlightthickness=1,
                             highlightbackground=C_BORDER)
            empty.pack(fill="x", pady=(0, 4))
            tk.Label(empty,
                     text="Khong co lich dat phong nao hom nay 🎉",
                     bg="#f8fafc", fg=C_MUTED,
                     font=("Segoe UI", 10, "italic")).pack(pady=14)
            return

        # Slot-based compact chip row
        SLOT_TIMES = {
            "Ca 1": "7:00-9:00",  "Ca 2": "9:15-11:15",
            "Ca 3": "13:00-15:00","Ca 4": "15:15-17:15",
            "Ca 5": "17:30-19:30",
        }
        STATUS_CHIP: dict[str, tuple[str, str]] = {
            "Da duyet":  ("#dcfce7", "#15803d"),
            "Cho duyet": ("#fef3c7", "#b45309"),
            "Tu choi":   ("#fdf2f8", "#db2777"),
        }
        slots_wrap = tk.Frame(card, bg=C_SURFACE)
        slots_wrap.pack(fill="x")
        for b in today_bookings[:8]: # type: ignore
            chip_bg, chip_fg = STATUS_CHIP.get(b.status, ("#f1f5f9", C_MUTED)) # type: ignore
            slot_time: str = SLOT_TIMES.get(b.slot, b.slot) or b.slot # type: ignore
            row = tk.Frame(slots_wrap, bg=C_SURFACE,
                           highlightthickness=1, highlightbackground=C_BORDER)
            row.pack(fill="x", pady=3)
            # Slot pill
            slot_pill = tk.Frame(row, bg=C_PRIMARY, padx=10, pady=6)
            slot_pill.pack(side="left")
            tk.Label(slot_pill, text=b.slot, # type: ignore
                     bg=C_PRIMARY, fg="white",
                     font=("Segoe UI", 9, "bold")).pack()
            tk.Label(slot_pill, text=slot_time, # type: ignore
                     bg=C_PRIMARY, fg="#c7d2fe",
                     font=("Segoe UI", 7)).pack()
            # Room chip
            room_chip = tk.Frame(row, bg="#eef2ff", padx=8, pady=6)
            room_chip.pack(side="left", padx=(0, 1))
            tk.Label(room_chip, text=f"🏫 {b.room_id}", # type: ignore
                     bg="#eef2ff", fg="#4f46e5",
                     font=("Segoe UI", 9, "bold")).pack()
            # User name
            tk.Label(row, text=f"👤 {b.user_name}", # type: ignore
                     bg=C_SURFACE, fg=C_DARK,
                     font=("Segoe UI", 9)).pack(side="left", padx=10)
            # Status
            status_chip = tk.Frame(row, bg=chip_bg, padx=8, pady=4)
            status_chip.pack(side="right", padx=8)
            tk.Label(status_chip, text=b.status, # type: ignore
                     bg=chip_bg, fg=chip_fg,
                     font=("Segoe UI", 8, "bold")).pack()
        if len(today_bookings) > 8: # type: ignore
            tk.Label(card, text=f"  + {len(today_bookings) - 8} lich khac...", # type: ignore
                     bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(4, 0))

    # ── Main area: recent bookings + donut chart ──────────────────────────────
    def _draw_main_area(self, body: tk.Frame) -> None:
        area = tk.Frame(body, bg=C_BG)
        area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        area.columnconfigure(0, weight=3)
        area.columnconfigure(1, weight=2)
        area.rowconfigure(0, weight=1)

        # ── Left: recent bookings ─────────────────────────────────────────────
        left_shadow = tk.Frame(area, bg="#c7d2fe")
        left_shadow.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        left = tk.Frame(left_shadow, bg=C_SURFACE, padx=14, pady=14)
        left.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        # Header with refresh button
        lhdr = tk.Frame(left, bg=C_SURFACE)
        lhdr.pack(fill="x", pady=(0, 8))
        tk.Label(lhdr, text="📋  Dat phong gan day",
                 bg=C_SURFACE, fg=C_DARK, font=F_SECTION).pack(side="left")

        cols = ("ma", "nguoi_dat", "phong", "ngay", "ca", "trang_thai")
        hdrs = ("Ma", "Nguoi dat", "Phong", "Ngay", "Ca", "Trang thai")
        wids = (85, 150, 70, 100, 65, 105)
        tree = make_tree(left, cols, hdrs, wids, height=10)
        with_scrollbar(left, tree)

        rows = [(b.booking_id, b.user_name, b.room_id,
                 b.booking_date, b.slot, b.status)
                for b in self.booking_ctrl.list_bookings(from_today=False)[:15]]
        fill_tree(tree, rows)

        # ── Right: donut chart + pending panel ───────────────────────────────
        right_col = tk.Frame(area, bg=C_BG)
        right_col.grid(row=0, column=1, sticky="nsew")

        self._draw_donut_chart(right_col)
        self._draw_pending_panel(right_col)

    # ── Donut chart ───────────────────────────────────────────────────────────
    def _draw_donut_chart(self, parent: tk.Frame) -> None:
        bookings  = self.booking_ctrl.list_bookings(from_today=False)
        da_duyet  = sum(1 for b in bookings if b.status == "Da duyet")
        cho_duyet = sum(1 for b in bookings if b.status == "Cho duyet")
        tu_choi   = sum(1 for b in bookings if b.status == "Tu choi")
        total     = len(bookings)

        shadow = tk.Frame(parent, bg="#c7d2fe")
        shadow.pack(fill="x", pady=(0, 8))

        card = tk.Frame(shadow, bg=C_SURFACE, padx=16, pady=16)
        card.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        tk.Label(card, text="📊  Trang thai dat phong",
                 bg=C_SURFACE, fg=C_DARK, font=F_SECTION).pack(anchor="w",
                                                                pady=(0, 12))

        # Donut + legend side by side
        chart_row = tk.Frame(card, bg=C_SURFACE)
        chart_row.pack(fill="x")

        SIZE, STROKE = 160, 24
        cx = cy = SIZE // 2
        MARGIN = STROKE // 2 + 3

        cv = tk.Canvas(chart_row, width=SIZE, height=SIZE,
                       bg=C_SURFACE, highlightthickness=0)
        cv.pack(side="left")

        def _draw_donut() -> None:
            cv.delete("all")
            segs = [
                (da_duyet,  "#16a34a"),
                (cho_duyet, "#f59e0b"),
                (tu_choi,   "#ec4899"),
            ]
            if total == 0:
                cv.create_arc(MARGIN, MARGIN, SIZE - MARGIN, SIZE - MARGIN,  # type: ignore[no-untyped-call]
                              start=0, extent=359,
                              style="arc", outline="#e5e7eb", width=STROKE)
                cv.create_text(cx, cy, text="0",
                               font=("Segoe UI", 20, "bold"), fill=C_MUTED)
                return

            start = 90.0
            for val, color in segs:
                if val == 0:
                    continue
                extent = -(360.0 * val / total)
                cv.create_arc(MARGIN, MARGIN, SIZE - MARGIN, SIZE - MARGIN,  # type: ignore[no-untyped-call]
                              start=start, extent=extent,
                              style="arc", outline=color, width=STROKE)
                start += extent

            # White center hole
            ellipse_r = (SIZE - 2 * MARGIN) / 2
            hole_r = int(ellipse_r - STROKE // 2 - 3)
            cv.create_oval(cx - hole_r, cy - hole_r,
                           cx + hole_r, cy + hole_r,
                           fill=C_SURFACE, outline="")

            pct = int(da_duyet / total * 100) if total > 0 else 0
            cv.create_text(cx, cy - 10, text=f"{pct}%",
                           font=("Segoe UI", 18, "bold"), fill=C_DARK)
            cv.create_text(cx, cy + 11, text="da duyet",
                           font=("Segoe UI", 8), fill=C_MUTED)

        cv.after(20, _draw_donut)

        # Legend
        legend = tk.Frame(chart_row, bg=C_SURFACE)
        legend.pack(side="left", padx=(14, 0), anchor="center")

        for label, val, color in [
            ("Da duyet",  da_duyet,  "#16a34a"),
            ("Cho duyet", cho_duyet, "#f59e0b"),
            ("Tu choi",   tu_choi,   "#ec4899"),
        ]:
            row = tk.Frame(legend, bg=C_SURFACE)
            row.pack(anchor="w", pady=5)
            dot = tk.Canvas(row, width=12, height=12, bg=C_SURFACE,
                            highlightthickness=0)
            dot.pack(side="left")
            dot.create_oval(0, 0, 12, 12, fill=color, outline="")
            tk.Label(row, text=f"  {label}", bg=C_SURFACE, fg="#374151",
                     font=("Segoe UI", 9)).pack(side="left")
            tk.Label(row, text=f"  {val}", bg=C_SURFACE, fg=color,
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        # Total
        tk.Frame(card, bg=C_BORDER, height=1).pack(fill="x", pady=(10, 6))
        tk.Label(card, text=f"Tong cong: {total} yeu cau",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")

    # ── Pending panel ─────────────────────────────────────────────────────────
    def _draw_pending_panel(self, parent: tk.Frame) -> None:
        pending = [b for b in self.booking_ctrl.list_bookings(from_today=False)
                   if b.status == "Cho duyet"]
        if not pending:
            return

        shadow = tk.Frame(parent, bg="#c7d2fe")
        shadow.pack(fill="x")

        p_card = tk.Frame(shadow, bg="#fffbeb", padx=14, pady=12)
        p_card.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        hdr = tk.Frame(p_card, bg="#fffbeb")
        hdr.pack(fill="x", pady=(0, 8))
        tk.Canvas(hdr, width=8, height=8, bg="#fffbeb",
                  highlightthickness=0).pack(side="left", padx=(0, 6), pady=6)
        # animated dot would go here; for now solid amber circle
        tk.Label(hdr, text=f"⏳  {len(pending)} yeu cau cho duyet",
                 bg="#fffbeb", fg="#92400e",
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        for b in pending[:3]:
            row = tk.Frame(p_card, bg="#fef3c7",
                           highlightthickness=1,
                           highlightbackground="#fde68a")
            row.pack(fill="x", pady=(0, 4))
            tk.Label(row,
                     text=f"  {b.booking_id}  •  {b.room_id}  •  {b.booking_date}",
                     bg="#fef3c7", fg="#78350f",
                     font=("Segoe UI", 8), anchor="w").pack(
                side="left", fill="x", expand=True, padx=4, pady=5)
            tk.Label(row, text=b.user_name, bg="#fef3c7", fg="#b45309",
                     font=("Segoe UI", 8, "bold")).pack(
                side="right", padx=8, pady=5)

        if len(pending) > 3:
            tk.Label(p_card, text=f"  ...va {len(pending) - 3} yeu cau khac",
                     bg="#fffbeb", fg="#b45309",
                     font=("Segoe UI", 8, "italic")).pack(anchor="w")

