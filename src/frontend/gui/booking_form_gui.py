# booking_form_gui.py  –  room booking form  (v3.0 - capacity filter + equipment report)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any
from gui.theme import (page_header, btn, _get_c, C_SURFACE, C_MUTED, C_PRIMARY, C_BORDER)

from tkcalendar import DateEntry  # type: ignore[import-untyped]


class BookingFormFrame(tk.Frame):
    def __init__(self, master: tk.Misc, booking_controller: Any,
                 room_controller: Any, current_user: Any,
                 on_booking_created: Any = None,
                 equipment_controller: Any = None) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.booking_ctrl = booking_controller
        self.room_ctrl    = room_controller
        self.current_user = current_user
        self.on_booking_created = on_booking_created
        self.equip_ctrl   = equipment_controller
        self.room_var     = tk.StringVar()
        self.date_var     = tk.StringVar(value=dt.date.today().isoformat())
        self.slot_var     = tk.StringVar(value="Ca 1")
        self.avail_var    = tk.StringVar()
        self.capacity_var = tk.StringVar(value="0")
        self._build()
        self._refresh_slots()

    def _build(self) -> None:
        page_header(self, "Dat phong hoc", "📝").pack(fill="x")

        # User info banner
        info = tk.Frame(self, bg=_get_c("INFO_BG"), highlightthickness=1,
                        highlightbackground=_get_c("BORDER"))
        info.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(info, text=f"👤  {self.current_user.full_name}",
                 bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"),
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(info, text=f"  │  Vai tro: {self.current_user.role}",
                 bg=_get_c("INFO_BG"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Label(info, text="📌 Dat phong se duoc admin duyet truoc khi co hieu luc",
                 bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"),
                 font=("Segoe UI", 9)).pack(side="right", padx=16)

        # Main form + room info card side by side
        body = tk.Frame(self, bg=_get_c("BG"))
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # ── Left: form ────────────────────────────────────────────────────────
        card = tk.Frame(body, bg=_get_c("SURFACE"), highlightthickness=1,
                        highlightbackground=_get_c("BORDER"), padx=24, pady=20)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1, minsize=200)

        def lbl(row: int, col: int, text: str) -> None:
            tk.Label(card, text=text, bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                     font=("Segoe UI", 9, "bold")).grid(
                row=row, column=col, sticky="w", pady=(14, 2))

        lbl(0, 0, "PHONG HOC")
        lbl(0, 1, "NGAY DAT")

        room_values = [f"{r.room_id} – {r.name} (SC: {r.capacity})"
                       for r in self.room_ctrl.list_rooms()
                       if r.status == "Hoat dong"]
        self._room_display_map: dict[str, Any] = {}
        for r in self.room_ctrl.list_rooms():
            key = f"{r.room_id} – {r.name} (SC: {r.capacity})"
            self._room_display_map[key] = r.room_id

        room_cb = ttk.Combobox(card, textvariable=self.room_var,
                               values=room_values, state="readonly", width=28)
        room_cb.grid(row=1, column=0, sticky="w")
        room_cb.bind("<<ComboboxSelected>>", self._on_room_selected)  # type: ignore[arg-type]

        # Date picker
        date_frame = tk.Frame(card, bg=_get_c("SURFACE"))
        date_frame.grid(row=1, column=1, sticky="ew", padx=(12, 0))
        de = DateEntry(date_frame,  # type: ignore[possibly-unbound]
                       width=28, date_pattern="yyyy-mm-dd",
                       background=_get_c("ACCENT"), foreground="white",
                       headersbackground=_get_c("ACCENT"), headersforeground="white",
                       selectbackground=_get_c("ACCENT"), selectforeground="white",
                       weekendbackground=_get_c("SURFACE"), weekendforeground=_get_c("TEXT"),
                       borderwidth=2, font=("Segoe UI", 10))
        de.set_date(dt.date.today()) # type: ignore
        de.pack(fill="x", expand=True)  # type: ignore[attr-defined]
        self._date_entry = de

        def _on_date_selected() -> None:
            self.date_var.set(de.get_date().isoformat())  # type: ignore[attr-defined]
            self._refresh_slots()

        de.bind("<<DateEntrySelected>>",  # type: ignore[attr-defined]
                lambda _=None: self.after(100, _on_date_selected))  # type: ignore[misc]

        # ── Capacity filter row ───────────────────────────────────────────────
        lbl(2, 0, "SO NGUOI DU KIEN (de loc phong)")
        cap_frame = tk.Frame(card, bg=C_SURFACE)
        cap_frame.grid(row=3, column=0, sticky="w", pady=(0, 4))
        tk.Label(cap_frame, text="Toi thieu:", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        cap_spin = tk.Spinbox(cap_frame, from_=0, to=500, increment=5,
                              textvariable=self.capacity_var,
                              width=6, font=("Segoe UI", 10),
                              relief="solid", bd=1)
        cap_spin.pack(side="left", padx=6)
        cap_spin.bind("<FocusOut>", lambda _=None: self._refresh_room_suggestions())
        cap_spin.bind("<Return>", lambda _=None: self._refresh_room_suggestions())
        cap_spin.bind("<ButtonRelease-1>", lambda _=None: self.after(50, self._refresh_room_suggestions))
        cap_spin.bind("<<Increment>>", lambda _=None: self.after(50, self._refresh_room_suggestions))
        cap_spin.bind("<<Decrement>>", lambda _=None: self.after(50, self._refresh_room_suggestions))
        tk.Label(cap_frame, text="nguoi  (0 = hien thi tat ca)",
                 bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8)).pack(side="left")

        lbl(4, 0, "CA HOC  (click de chon)")
        lbl(4, 1, "CA CON TRONG")

        # ── Visual slot picker ──────────────────────────────────────────────
        self._slot_btns: dict[str, tk.Button] = {}
        slot_grid = tk.Frame(card, bg=C_SURFACE)
        slot_grid.grid(row=5, column=0, sticky="w")

        SLOT_INFO = [
            ("Ca 1", "7:00-9:00"),
            ("Ca 2", "9:15-11:15"),
            ("Ca 3", "13:00-15:00"),
            ("Ca 4", "15:15-17:15"),
            ("Ca 5", "17:30-19:30"),
        ]

        def _select_slot(slot_name: str) -> None:
            self.slot_var.set(slot_name)
            for sn, sb in self._slot_btns.items():
                if sn == slot_name:
                    sb.config(bg=C_PRIMARY, fg="white",
                              relief="sunken", font=("Segoe UI", 9, "bold"))
                else:
                    sb.config(bg="#f1f5f9", fg="#334155",
                              relief="flat", font=("Segoe UI", 9))
            self._refresh_room_suggestions()

        for i, (slot_name, slot_time) in enumerate(SLOT_INFO):
            sb = tk.Button(
                slot_grid,
                text=f"{slot_name}\n{slot_time}",
                bg="#f1f5f9", fg="#334155",
                font=("Segoe UI", 9), relief="flat",
                cursor="hand2", padx=8, pady=6, bd=1,
                activebackground=C_PRIMARY, activeforeground="white",
                command=lambda s=slot_name: _select_slot(s))
            sb.grid(row=0, column=i, padx=2)
            self._slot_btns[slot_name] = sb
            sb.bind("<Enter>", lambda e=None, s=sb: s.config(bg="#e0e7ff") if s.cget("bg") != C_PRIMARY else None)
            sb.bind("<Leave>", lambda e=None, s=sb: s.config(bg="#f1f5f9") if s.cget("bg") != C_PRIMARY else None)

        avail_lbl = tk.Label(card, textvariable=self.avail_var, bg="#f0fdf4",
                             fg="#15803d", font=("Segoe UI", 9), width=32,
                             anchor="w", relief="solid", bd=1,
                             wraplength=300)
        avail_lbl.grid(row=5, column=1, sticky="w", padx=(12, 0))
        self._avail_lbl = avail_lbl

        # ── Panel goi y phong con trong chu dong (hien khi chon ngay & ca) ───
        self._room_suggest_frame = tk.Frame(card, bg=C_SURFACE)
        self._room_suggest_frame.grid(row=6, column=0, columnspan=2,
                                      sticky="ew", pady=(6, 0))
        self._room_suggest_frame.grid_remove()  # hidden until date+slot selected

        # ── Suggestion panel (shown when selected room is fully booked) ────────
        self._suggest_outer = tk.Frame(card, bg=C_SURFACE)
        self._suggest_outer.grid(row=7, column=0, columnspan=2,
                                 sticky="ew", pady=(10, 0))
        self._suggest_outer.grid_remove()   # hidden by default

        # Select default slot (must be after _room_suggest_frame is created)
        _select_slot(self.slot_var.get() or "Ca 1")

        lbl(8, 0, "MUC DICH SU DUNG")
        self.purpose_text = tk.Text(card, width=64, height=5,
                                    relief="solid", bd=1,
                                    font=("Segoe UI", 10))
        self.purpose_text.grid(row=9, column=0, columnspan=2,
                               sticky="ew", pady=(0, 16))

        btn_f = tk.Frame(card, bg=C_SURFACE)
        btn_f.grid(row=10, column=1, sticky="e")
        btn(btn_f, "📤  Gui yeu cau dat phong", self._submit).pack()

        # ── Right: room info card ─────────────────────────────────────────────
        self._room_info_frame = tk.Frame(body, bg=C_SURFACE,
                                         highlightthickness=1,
                                         highlightbackground=C_BORDER,
                                         padx=18, pady=18)
        self._room_info_frame.grid(row=0, column=1, sticky="nsew")
        self._draw_room_placeholder()

    def _draw_room_placeholder(self) -> None:
        for w in self._room_info_frame.winfo_children():
            w.destroy()
        # Subtle canvas background for the placeholder area
        cv = tk.Canvas(self._room_info_frame, bg="#f8fafc",
                       highlightthickness=0, height=200)
        cv.pack(fill="both", expand=True)

        def _draw(_e: Any = None) -> None:
            if not cv.winfo_exists():
                return
            cv.delete("all")
            W = cv.winfo_width() or 260
            H = cv.winfo_height() or 200
            cv.create_oval(W - 80, -30, W + 20, 70, fill="#eef2ff", outline="")
            cv.create_oval(-20, H - 70, 60, H + 10, fill="#f0f9ff", outline="")
            # Icon circle
            cx, cy = W // 2, H // 2 - 20
            cv.create_oval(cx - 36, cy - 36, cx + 36, cy + 36,
                           fill="#e0e7ff", outline="#c7d2fe", width=1)
            cv.create_text(cx, cy, text="🏫",
                           font=("Segoe UI", 22))
            cv.create_text(W // 2, cy + 54,
                           text="Chon phong hoc",
                           font=("Segoe UI", 11, "bold"),
                           fill="#4f46e5")
            cv.create_text(W // 2, cy + 76,
                           text="de xem thong tin chi tiet",
                           font=("Segoe UI", 9),
                           fill="#94a3b8")

        cv.bind("<Configure>", _draw)
        cv.after(30, _draw)

    def _draw_room_info(self, room: Any) -> None:
        for w in self._room_info_frame.winfo_children():
            w.destroy()

        # Status badge color
        status_bg = "#dcfce7" if room.status == "Hoat dong" else "#fdf2f8"
        status_fg = "#15803d" if room.status == "Hoat dong" else "#db2777"

        tk.Label(self._room_info_frame, text="🏫  Thong tin phong",
                 bg=C_SURFACE, fg="#4f46e5",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 12))

        def info_row(icon: str, label: str, value: str,
                     val_color: str = "#1e293b") -> None:
            row = tk.Frame(self._room_info_frame, bg=C_SURFACE)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=icon, bg=C_SURFACE,
                     font=("Segoe UI", 13), width=2).pack(side="left")
            tk.Label(row, text=f"{label}: ", bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9)).pack(side="left")
            tk.Label(row, text=value, bg=C_SURFACE, fg=val_color,
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        info_row("🔑", "Ma phong",  room.room_id)
        info_row("📛", "Ten phong",  room.name)
        info_row("👥", "Suc chua",   f"{room.capacity} nguoi")
        info_row("📚", "Loai phong", room.room_type)

        # Status badge
        status_row = tk.Frame(self._room_info_frame, bg=C_SURFACE)
        status_row.pack(fill="x", pady=4)
        tk.Label(status_row, text="⚡", bg=C_SURFACE,
                 font=("Segoe UI", 13), width=2).pack(side="left")
        tk.Label(status_row, text="Trang thai: ", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Label(status_row, text=f"  {room.status}  ",
                 bg=status_bg, fg=status_fg,
                 font=("Segoe UI", 9, "bold")).pack(side="left")

        tk.Frame(self._room_info_frame, bg=C_BORDER, height=1).pack(fill="x", pady=8)

        # ── Real equipment list from database ────────────────────────────────
        eq_hdr = tk.Frame(self._room_info_frame, bg=C_SURFACE)
        eq_hdr.pack(fill="x", pady=(0, 4))
        tk.Label(eq_hdr, text="🔧  Thiet bi trong phong:",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", anchor="w")

        # Fetch real equipment list
        equip_items: list[Any] = []
        if self.equip_ctrl is not None:
            try:
                equip_items = self.equip_ctrl.list_equipment(room_id=room.room_id)
            except Exception:
                equip_items = []

        STATUS_ICON = {
            "Hoat dong": ("✅", "#15803d"),
            "Bao tri":   ("⚠️", "#b45309"),
            "Hong":      ("❌", "#db2777"),
            "Dang sua":  ("🔨", "#0369a1"),
            "Da thanh ly": ("🗑", "#64748b"),
        }

        if equip_items:
            eq_scroll = tk.Frame(self._room_info_frame, bg="#f8fafc",
                                 highlightthickness=1,
                                 highlightbackground=C_BORDER)
            eq_scroll.pack(fill="x", pady=(0, 6), ipadx=4, ipady=2)
            for eq in equip_items:
                icon, fg = STATUS_ICON.get(eq.status, ("•", "#64748b"))
                eq_row = tk.Frame(eq_scroll, bg="#f8fafc")
                eq_row.pack(fill="x", padx=6, pady=1)
                tk.Label(eq_row, text=icon, bg="#f8fafc",
                         font=("Segoe UI", 10), width=2).pack(side="left")
                tk.Label(eq_row, text=eq.name,
                         bg="#f8fafc", fg="#1e293b",
                         font=("Segoe UI", 9)).pack(side="left")
                tk.Label(eq_row, text=f"  [{eq.equipment_type}]",
                         bg="#f8fafc", fg="#94a3b8",
                         font=("Segoe UI", 8)).pack(side="left")
                tk.Label(eq_row, text=eq.status,
                         bg="#f8fafc", fg=fg,
                         font=("Segoe UI", 8, "bold")).pack(side="right", padx=4)
        elif room.equipment:
            # Fallback: show the text description from rooms table
            tk.Label(self._room_info_frame, text=room.equipment,
                     bg="#f8fafc", fg="#334155",
                     font=("Segoe UI", 9), wraplength=200,
                     justify="left", anchor="w",
                     relief="solid", bd=1).pack(fill="x", pady=(4, 0),
                                                padx=2, ipadx=6, ipady=4)
        else:
            tk.Label(self._room_info_frame, text="(Chua co thiet bi nao duoc dang ky)",
                     bg=C_SURFACE, fg="#94a3b8", font=("Segoe UI", 9)).pack(anchor="w")

        # ── "Báo hỏng thiết bị" button ───────────────────────────────────────
        if self.equip_ctrl is not None:
            tk.Frame(self._room_info_frame, bg=C_BORDER, height=1).pack(fill="x", pady=(8, 4))
            report_btn = tk.Button(
                self._room_info_frame,
                text="🔧  Bao hong thiet bi",
                bg="#fef3c7", fg="#92400e",
                font=("Segoe UI", 9, "bold"),
                relief="flat", bd=1, cursor="hand2",
                activebackground="#fde68a",
                command=lambda r=room: self._open_equipment_report(r))
            report_btn.pack(fill="x", pady=(0, 4), ipadx=4, ipady=4)

    def _on_room_selected(self, _event: Any = None) -> None:
        display = self.room_var.get()
        room_id = self._room_display_map.get(display, display.split(" – ")[0])
        room = self.room_ctrl.get_room(room_id)
        if room:
            self._draw_room_info(room)
        self._refresh_slots()

    def _open_equipment_report(self, room: Any) -> None:
        """Open the equipment report dialog for the selected room."""
        from gui.room_feedback_gui import EquipmentReportDialog
        EquipmentReportDialog(
            self,
            room_id=room.room_id,
            room_name=room.name,
            current_user=self.current_user,
            equipment_ctrl=self.equip_ctrl,
            on_done=lambda: self._draw_room_info(room),
        )

    def _refresh_slots(self) -> None:
        display = self.room_var.get().strip()
        room_id = self._room_display_map.get(display, display.split(" – ")[0]) if display else ""
        date    = self.date_var.get().strip()

        # Hide suggestion panel until we know we need it
        self._suggest_outer.grid_remove()
        self._refresh_room_suggestions()

        if not room_id or not date:
            self.avail_var.set("Chon phong va ngay de xem")
            return

        slots = self.booking_ctrl.available_slots(room_id, date)
        if slots:
            self.avail_var.set(", ".join(slots))
            self._avail_lbl.config(bg="#f0fdf4", fg="#15803d")
        else:
            self.avail_var.set("❌  Phong da duoc dat kin ca nay")
            self._avail_lbl.config(bg="#fdf2f8", fg="#db2777")

            # Build and show suggestions
            all_room_ids = [r.room_id for r in self.room_ctrl.list_rooms()
                            if r.status == "Hoat dong"]
            suggestions = self.booking_ctrl.suggest_alternatives(
                room_id=room_id,
                booking_date=date,
                slot=self.slot_var.get().strip(),
                all_room_ids=all_room_ids,
                days_ahead=7,
            )
            self._build_suggestion_panel(suggestions, date)

    # ── Suggestion panel builder ──────────────────────────────────────────────
    def _build_suggestion_panel(self, suggestions: dict[str, Any], base_date: str) -> None:
        """Rebuild and show the suggestion panel inside _suggest_outer."""
        outer = self._suggest_outer
        for w in outer.winfo_children():
            w.destroy()

        other_rooms  = suggestions.get("other_rooms",  [])
        other_slots  = suggestions.get("other_slots",  [])

        if not other_rooms and not other_slots:
            # Nothing to suggest at all
            tk.Label(outer,
                     text="⚠  Khong tim thay phong trong trong 7 ngay toi. "
                          "Vui long thu lai sau.",
                     bg="#fef9c3", fg="#92400e",
                     font=("Segoe UI", 9), wraplength=560,
                     relief="solid", bd=1).pack(fill="x", ipadx=10, ipady=6)
            outer.grid()
            return

        # Container card
        card = tk.Frame(outer, bg="#eff6ff",
                        highlightthickness=1,
                        highlightbackground="#bfdbfe")
        card.pack(fill="x", ipadx=4, ipady=4)

        # Header
        hdr = tk.Frame(card, bg="#eff6ff")
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(hdr, text="💡  Goi y phong / lich con trong",
                 bg="#eff6ff", fg="#1d4ed8",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(hdr, text="(Click de tu dong dien vao form)",
                 bg="#eff6ff", fg="#60a5fa",
                 font=("Segoe UI", 8)).pack(side="left", padx=(8, 0))

        # ── Section 1: other rooms same date+slot ─────────────────────────────
        if other_rooms:
            sec1 = tk.Frame(card, bg="#eff6ff")
            sec1.pack(fill="x", padx=12, pady=(0, 8))
            tk.Label(sec1,
                     text=f"🏫  Phong khac con trong vao {base_date}  "
                          f"{self.slot_var.get()}:",
                     bg="#eff6ff", fg="#1e40af",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

            chips = tk.Frame(sec1, bg="#eff6ff")
            chips.pack(anchor="w")
            for room_id, slot in other_rooms:   # hien thi tat ca
                # Look up display name
                display_name = next(
                    (k for k, v in self._room_display_map.items()
                     if v == room_id), room_id)

                chip = tk.Button(
                    chips,
                    text=f"  {room_id}  ",
                    bg="#dbeafe", fg="#1d4ed8",
                    font=("Segoe UI", 9, "bold"),
                    relief="flat", bd=0, cursor="hand2",
                    activebackground="#bfdbfe",
                    command=lambda rid=room_id, dn=display_name, s=slot:
                        self._apply_suggestion(dn, None, s),
                )
                chip.pack(side="left", padx=(0, 6), pady=2)

                # Tooltip-like label
                room_obj = self.room_ctrl.get_room(room_id)
                if room_obj:
                    tk.Label(chips,
                             text=f"{room_obj.name} ({room_obj.capacity} ch.)",
                             bg="#eff6ff", fg="#475569",
                             font=("Segoe UI", 8)).pack(
                        side="left", padx=(0, 14), pady=2)

        # ── Divider ───────────────────────────────────────────────────────────
        if other_rooms and other_slots:
            tk.Frame(card, bg="#bfdbfe", height=1).pack(
                fill="x", padx=12, pady=4)

        # ── Section 2: same room, other dates/slots ───────────────────────────
        if other_slots:
            sec2 = tk.Frame(card, bg="#eff6ff")
            sec2.pack(fill="x", padx=12, pady=(0, 10))
            tk.Label(sec2,
                     text=f"📅  Phong nay ({self.room_var.get().split(' – ')[0]}) "
                          f"con trong vao:",
                     bg="#eff6ff", fg="#1e40af",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

            # Group by date for readability
            from collections import defaultdict
            by_date: dict[str, list[str]] = defaultdict(list)
            for date_str, s in other_slots:   # tat ca slot con trong
                by_date[date_str].append(s)

            grid_f = tk.Frame(sec2, bg="#eff6ff")
            grid_f.pack(anchor="w")
            for col, (date_str, slots_list) in enumerate(
                    sorted(by_date.items())):
                try:
                    d = dt.date.fromisoformat(date_str)
                    day_label = d.strftime("%d/%m\n%a").replace(
                        "Mon","T2").replace("Tue","T3").replace(
                        "Wed","T4").replace("Thu","T5").replace(
                        "Fri","T6").replace("Sat","T7").replace("Sun","CN")
                except Exception:
                    day_label = date_str

                day_col = tk.Frame(grid_f, bg="#eff6ff")
                day_col.grid(row=0, column=col, padx=(0, 10), pady=2,
                             sticky="n")

                tk.Label(day_col, text=day_label,
                         bg="#dbeafe", fg="#1d4ed8",
                         font=("Segoe UI", 8, "bold"),
                         width=7, relief="flat",
                         anchor="center").pack(pady=(0, 3))

                for s in slots_list:
                    display = self.room_var.get()
                    tk.Button(
                        day_col,
                        text=s,
                        bg="#f0fdf4", fg="#15803d",
                        font=("Segoe UI", 8),
                        relief="flat", bd=0,
                        width=7, cursor="hand2",
                        activebackground="#dcfce7",
                        command=lambda ds=date_str, sl=s, dp=display:
                            self._apply_suggestion(dp, ds, sl),
                    ).pack(pady=1)

        outer.grid()

    def _refresh_room_suggestions(self) -> None:
        """Hien thi tat ca phong con trong theo ngay, ca hoc & suc chua toi thieu."""
        if not hasattr(self, '_room_suggest_frame'):
            return
        frame = self._room_suggest_frame
        for w in frame.winfo_children():
            w.destroy()

        date = self.date_var.get().strip()
        slot = self.slot_var.get().strip()

        if not date or not slot:
            frame.grid_remove()
            return
        try:
            dt.date.fromisoformat(date)
        except ValueError:
            frame.grid_remove()
            return

        try:
            min_cap = int(self.capacity_var.get() or "0")
        except ValueError:
            min_cap = 0

        free_rooms = self.room_ctrl.get_available_rooms_by_capacity(
            self.booking_ctrl, date, slot, min_capacity=min_cap
        )

        if not free_rooms:
            notice = tk.Frame(frame, bg="#fdf2f8", highlightthickness=1,
                              highlightbackground="#fbcfe8")
            notice.pack(fill="x", pady=(4, 0))
            cap_msg = f"  (suc chua ≥ {min_cap})" if min_cap > 0 else ""
            tk.Label(notice,
                     text=f"⚠️  Khong co phong trong nao vao {date}  –  {slot}{cap_msg}",
                     bg="#fdf2f8", fg="#db2777",
                     font=("Segoe UI", 9, "bold")).pack(padx=12, pady=7)
            frame.grid()
            return

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(frame, bg="#eff6ff", highlightthickness=1,
                       highlightbackground="#bfdbfe")
        hdr.pack(fill="x", pady=(4, 0))

        hdr_left = tk.Frame(hdr, bg="#eff6ff")
        hdr_left.pack(side="left", padx=12, pady=7)
        tk.Label(hdr_left, text="🟢  Phong con trong:",
                 bg="#eff6ff", fg="#1d4ed8",
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(hdr_left, text=f"  {date}  –  {slot}",
                 bg="#eff6ff", fg="#2563eb",
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        if min_cap > 0:
            tk.Label(hdr_left, text=f"  •  suc chua ≥ {min_cap} nguoi",
                     bg="#eff6ff", fg="#7c3aed",
                     font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(hdr, text=f"✅ {len(free_rooms)} phong  •  Click de chon nhanh",
                 bg="#eff6ff", fg="#60a5fa",
                 font=("Segoe UI", 8)).pack(side="right", padx=12)

        # ── Chips row ─────────────────────────────────────────────────────────
        chips_bg = tk.Frame(frame, bg=_get_c("BG"), highlightthickness=1,
                            highlightbackground=_get_c("BORDER"))
        chips_bg.pack(fill="x")

        for r in free_rooms:   # hien thi tat ca phong con trong
            display = f"{r.room_id} – {r.name} (SC: {r.capacity})"
            chip_col = tk.Frame(chips_bg, bg=_get_c("BG"))
            chip_col.pack(side="left", padx=6, pady=6)

            chip_btn = tk.Button(
                chip_col,
                text=f"  {r.room_id}  ",
                bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"),
                font=("Segoe UI", 9, "bold"),
                relief="flat", bd=0, cursor="hand2",
                activebackground=_get_c("SB_HOVER"),
                command=lambda dn=display, s=slot:
                    self._apply_suggestion(dn, None, s),
            )
            chip_btn.pack()
            chip_btn.bind("<Enter>", lambda e=None, b=chip_btn: b.config(bg=_get_c("SB_HOVER")))
            chip_btn.bind("<Leave>", lambda e=None, b=chip_btn: b.config(bg=_get_c("INFO_BG")))

            tk.Label(chip_col,
                     text=f"{r.name}",
                     bg=_get_c("BG"), fg=_get_c("TEXT"),
                     font=("Segoe UI", 7, "bold")).pack()
            tk.Label(chip_col,
                     text=f"{r.capacity} ch.  •  {r.room_type}",
                     bg=_get_c("BG"), fg=_get_c("MUTED"),
                     font=("Segoe UI", 7)).pack()

        frame.grid()

    def _apply_suggestion(self, room_display: str,
                          date_str: str | None, slot: str) -> None:
        """Auto-fill form fields from a suggestion chip click."""
        if room_display:
            self.room_var.set(room_display)
            # Update room info card
            room_id = self._room_display_map.get(
                room_display, room_display.split(" – ")[0])
            room = self.room_ctrl.get_room(room_id)
            if room:
                self._draw_room_info(room)
        if date_str:
            self.date_var.set(date_str)
            try:
                self._date_entry.set_date(dt.date.fromisoformat(date_str))  # type: ignore[attr-defined]
            except Exception:
                pass
        if slot:
            self.slot_var.set(slot)
        self._refresh_slots()

    def _submit(self) -> None:
        display = self.room_var.get().strip()
        room_id = self._room_display_map.get(display, display.split(" – ")[0]) if display else ""
        if not room_id:
            messagebox.showwarning("Chua chon phong",
                                   "Vui long chon phong hoc truoc khi dat.")
            return
        if not self.slot_var.get().strip():
            messagebox.showwarning("Chua chon ca",
                                   "Vui long chon ca hoc.")
            return
        purpose = self.purpose_text.get("1.0", "end").strip()
        if not purpose:
            messagebox.showwarning("Thieu muc dich",
                                   "Vui long nhap muc dich su dung phong.")
            return
        # Use DateEntry widget directly as authoritative date source
        try:
            booking_date = self._date_entry.get_date().isoformat()  # type: ignore[attr-defined]
        except Exception:
            booking_date = self.date_var.get().strip()
        try:
            self.booking_ctrl.create_booking(
                user=self.current_user,
                room_id=room_id,
                booking_date=booking_date,
                slot=self.slot_var.get().strip(),
                purpose=purpose,
            )
        except ValueError as err:
            messagebox.showerror("Khong the dat phong", str(err))
            return
        messagebox.showinfo("Dat phong thanh cong!",
                            "Yeu cau da duoc gui.\n"
                            "Vui long cho admin duyet de co hieu luc.")
        # Reset form fields to prevent accidental duplicate submission
        self.purpose_text.delete("1.0", "end")
        self.room_var.set("")
        self.date_var.set(dt.date.today().isoformat())
        self.slot_var.set("Ca 1")
        # Reset slot button visuals
        for sn, sb in self._slot_btns.items():
            if sn == "Ca 1":
                sb.config(bg=_get_c("ACCENT"), fg="white", relief="sunken",
                          font=("Segoe UI", 9, "bold"))
            else:
                sb.config(bg=_get_c("BG"), fg=_get_c("TEXT"), relief="flat",
                          font=("Segoe UI", 9))
        self._draw_room_placeholder()
        self._suggest_outer.grid_remove()
        self._room_suggest_frame.grid_remove()
        self.avail_var.set("Chon phong va ngay de xem")
        self._avail_lbl.config(bg=_get_c("SUCCESS_BG"), fg=_get_c("SUCCESS"))
        self._refresh_slots()
        if self.on_booking_created:
            self.on_booking_created()
