# booking_form_gui.py  –  room booking form  (v2.0 - DatePicker + room info card + suggestions)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from gui.theme import (C_BG, C_PRIMARY, C_SURFACE, C_BORDER,
                       C_TEXT, C_MUTED, C_DARK, F_INPUT, page_header, btn)

try:
    from tkcalendar import DateEntry
    _HAS_CALENDAR = True
except ImportError:
    _HAS_CALENDAR = False


class BookingFormFrame(tk.Frame):
    def __init__(self, master, booking_controller, room_controller,
                 current_user, on_booking_created=None) -> None:
        super().__init__(master, bg=C_BG)
        self.booking_ctrl = booking_controller
        self.room_ctrl    = room_controller
        self.current_user = current_user
        self.on_booking_created = on_booking_created
        self.room_var  = tk.StringVar()
        self.date_var  = tk.StringVar(value=dt.date.today().isoformat())
        self.slot_var  = tk.StringVar(value="Ca 1")
        self.avail_var = tk.StringVar()
        self._build()
        self._refresh_slots()

    def _build(self) -> None:
        page_header(self, "Dat phong hoc", "📝").pack(fill="x")

        # User info banner
        info = tk.Frame(self, bg="#eef4fc", highlightthickness=1,
                        highlightbackground=C_BORDER)
        info.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(info, text=f"👤  {self.current_user.full_name}",
                 bg="#eef4fc", fg="#1a2f5e",
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(info, text=f"  │  Vai tro: {self.current_user.role}",
                 bg="#eef4fc", fg=C_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Label(info, text="📌 Dat phong se duoc admin duyet truoc khi co hieu luc",
                 bg="#eef4fc", fg="#475569",
                 font=("Segoe UI", 9)).pack(side="right", padx=16)

        # Main form + room info card side by side
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # ── Left: form ────────────────────────────────────────────────────────
        card = tk.Frame(body, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=24, pady=20)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        def lbl(row, col, text):
            tk.Label(card, text=text, bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9, "bold")).grid(
                row=row, column=col, sticky="w", pady=(14, 2))

        lbl(0, 0, "PHONG HOC")
        lbl(0, 1, "NGAY DAT")

        room_values = [f"{r.room_id} – {r.name} (SC: {r.capacity})"
                       for r in self.room_ctrl.list_rooms()
                       if r.status == "Hoat dong"]
        self._room_display_map = {}
        for r in self.room_ctrl.list_rooms():
            key = f"{r.room_id} – {r.name} (SC: {r.capacity})"
            self._room_display_map[key] = r.room_id

        room_cb = ttk.Combobox(card, textvariable=self.room_var,
                               values=room_values, state="readonly", width=28)
        room_cb.grid(row=1, column=0, sticky="w")
        room_cb.bind("<<ComboboxSelected>>", self._on_room_selected)

        # Date picker
        if _HAS_CALENDAR:
            date_frame = tk.Frame(card, bg=C_SURFACE)
            date_frame.grid(row=1, column=1, sticky="w", padx=(12, 0))
            de = DateEntry(date_frame, textvariable=self.date_var,
                           width=26, date_pattern="yyyy-mm-dd",
                           background=C_PRIMARY, foreground="white",
                           borderwidth=1, font=("Segoe UI", 10))
            de.pack()
            de.bind("<<DateEntrySelected>>",
                    lambda _: self.after(100, self._refresh_slots))
        else:
            date_e = tk.Entry(card, textvariable=self.date_var, width=30,
                              font=F_INPUT, relief="solid", bd=1)
            date_e.grid(row=1, column=1, sticky="w", padx=(12, 0))
            date_e.bind("<FocusOut>", lambda _: self._refresh_slots())

        lbl(2, 0, "CA HOC")
        lbl(2, 1, "CA CON TRONG")

        slot_cb_form = ttk.Combobox(card, textvariable=self.slot_var,
                                    values=self.booking_ctrl.SLOT_OPTIONS,
                                    state="readonly", width=28)
        slot_cb_form.grid(row=3, column=0, sticky="w")
        slot_cb_form.bind("<<ComboboxSelected>>",
                          lambda _: self._refresh_room_suggestions())

        avail_lbl = tk.Label(card, textvariable=self.avail_var, bg="#f0fdf4",
                             fg="#15803d", font=("Segoe UI", 9), width=32,
                             anchor="w", relief="solid", bd=1,
                             wraplength=300)
        avail_lbl.grid(row=3, column=1, sticky="w", padx=(12, 0))
        self._avail_lbl = avail_lbl

        # ── Panel goi y phong con trong chu dong (hien khi chon ngay & ca) ───
        self._room_suggest_frame = tk.Frame(card, bg=C_SURFACE)
        self._room_suggest_frame.grid(row=4, column=0, columnspan=2,
                                      sticky="ew", pady=(6, 0))
        self._room_suggest_frame.grid_remove()  # hidden until date+slot selected

        # ── Suggestion panel (shown when selected room is fully booked) ────────
        self._suggest_outer = tk.Frame(card, bg=C_SURFACE)
        self._suggest_outer.grid(row=5, column=0, columnspan=2,
                                 sticky="ew", pady=(10, 0))
        self._suggest_outer.grid_remove()   # hidden by default

        lbl(6, 0, "MUC DICH SU DUNG")
        self.purpose_text = tk.Text(card, width=64, height=5,
                                    relief="solid", bd=1,
                                    font=("Segoe UI", 10))
        self.purpose_text.grid(row=7, column=0, columnspan=2,
                               sticky="ew", pady=(0, 16))

        btn_f = tk.Frame(card, bg=C_SURFACE)
        btn_f.grid(row=8, column=1, sticky="e")
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
        tk.Label(self._room_info_frame,
                 text="🏫", bg=C_SURFACE,
                 font=("Segoe UI", 40)).pack(pady=(30, 8))
        tk.Label(self._room_info_frame,
                 text="Chon phong hoc\nde xem thong tin chi tiet",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 11), justify="center").pack()

    def _draw_room_info(self, room) -> None:
        for w in self._room_info_frame.winfo_children():
            w.destroy()

        # Status badge color
        status_bg = "#dcfce7" if room.status == "Hoat dong" else "#fee2e2"
        status_fg = "#15803d" if room.status == "Hoat dong" else "#dc2626"

        tk.Label(self._room_info_frame, text="🏫  Thong tin phong",
                 bg=C_SURFACE, fg="#1a2f5e",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 12))

        def info_row(icon, label, value, val_color="#1e293b"):
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

        if room.equipment:
            tk.Frame(self._room_info_frame, bg=C_BORDER,
                     height=1).pack(fill="x", pady=8)
            tk.Label(self._room_info_frame, text="🔧  Trang thiet bi:",
                     bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(self._room_info_frame, text=room.equipment,
                     bg="#f8fafc", fg="#334155",
                     font=("Segoe UI", 9), wraplength=200,
                     justify="left", anchor="w",
                     relief="solid", bd=1).pack(fill="x", pady=(4, 0),
                                                padx=2, ipadx=6, ipady=4)

    def _on_room_selected(self, _event=None) -> None:
        display = self.room_var.get()
        room_id = self._room_display_map.get(display, display.split(" – ")[0])
        room = self.room_ctrl.get_room(room_id)
        if room:
            self._draw_room_info(room)
        self._refresh_slots()

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
            self._avail_lbl.config(bg="#fef2f2", fg="#dc2626")

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
    def _build_suggestion_panel(self, suggestions: dict, base_date: str) -> None:
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
            for room_id, slot in other_rooms[:8]:   # cap at 8 chips
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
            for date_str, s in other_slots[:35]:   # limit to ~5 days × 5 slots
                by_date[date_str].append(s)

            grid_f = tk.Frame(sec2, bg="#eff6ff")
            grid_f.pack(anchor="w")
            for col, (date_str, slots_list) in enumerate(
                    sorted(by_date.items())[:7]):
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
        """Hien thi tat ca phong con trong theo ngay & ca hoc da chon."""
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

        free_rooms = [
            r for r in self.room_ctrl.list_rooms()
            if r.status == "Hoat dong"
            and slot in self.booking_ctrl.available_slots(r.room_id, date)
        ]

        if not free_rooms:
            notice = tk.Frame(frame, bg="#fef2f2", highlightthickness=1,
                              highlightbackground="#fecaca")
            notice.pack(fill="x", pady=(4, 0))
            tk.Label(notice,
                     text=f"⚠️  Khong co phong trong nao vao {date}  –  {slot}",
                     bg="#fef2f2", fg="#dc2626",
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
        tk.Label(hdr, text=f"✅ {len(free_rooms)} phong  •  Click de chon nhanh",
                 bg="#eff6ff", fg="#60a5fa",
                 font=("Segoe UI", 8)).pack(side="right", padx=12)

        # ── Chips row ─────────────────────────────────────────────────────────
        chips_bg = tk.Frame(frame, bg="#f8fafc", highlightthickness=1,
                            highlightbackground="#e2e8f0")
        chips_bg.pack(fill="x")

        for r in free_rooms[:14]:   # gioi han 14 chip
            display = f"{r.room_id} – {r.name} (SC: {r.capacity})"
            chip_col = tk.Frame(chips_bg, bg="#f8fafc")
            chip_col.pack(side="left", padx=6, pady=6)

            chip_btn = tk.Button(
                chip_col,
                text=f"  {r.room_id}  ",
                bg="#dbeafe", fg="#1d4ed8",
                font=("Segoe UI", 9, "bold"),
                relief="flat", bd=0, cursor="hand2",
                activebackground="#bfdbfe",
                command=lambda dn=display, s=slot:
                    self._apply_suggestion(dn, None, s),
            )
            chip_btn.pack()
            chip_btn.bind("<Enter>", lambda e, b=chip_btn: b.config(bg="#bfdbfe"))
            chip_btn.bind("<Leave>", lambda e, b=chip_btn: b.config(bg="#dbeafe"))

            tk.Label(chip_col,
                     text=f"{r.name}",
                     bg="#f8fafc", fg="#334155",
                     font=("Segoe UI", 7, "bold")).pack()
            tk.Label(chip_col,
                     text=f"{r.capacity} ch.  •  {r.room_type}",
                     bg="#f8fafc", fg="#64748b",
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
        if slot:
            self.slot_var.set(slot)
        self._refresh_slots()

    def _submit(self) -> None:
        display = self.room_var.get().strip()
        room_id = self._room_display_map.get(display, display.split(" – ")[0]) if display else ""
        try:
            self.booking_ctrl.create_booking(
                user=self.current_user,
                room_id=room_id,
                booking_date=self.date_var.get().strip(),
                slot=self.slot_var.get().strip(),
                purpose=self.purpose_text.get("1.0", "end"),
            )
        except ValueError as err:
            messagebox.showerror("Khong the dat phong", str(err))
            return
        messagebox.showinfo("Dat phong thanh cong!",
                            "Yeu cau da duoc gui.\n"
                            "Vui long cho admin duyet de co hieu luc.")
        self.purpose_text.delete("1.0", "end")
        self._refresh_slots()
        if self.on_booking_created:
            self.on_booking_created()
