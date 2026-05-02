# schedule_gui.py  –  schedule view (7-day × 5-shift visual grid)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
from gui.theme import C_BG, C_SURFACE, C_BORDER, page_header, btn

DAYS      = ["Thu 2", "Thu 3", "Thu 4", "Thu 5", "Thu 6", "Thu 7", "Chu nhat"]
SLOTS_LBL = [
    "Ca 1\n7:00-9:00",
    "Ca 2\n9:15-11:15",
    "Ca 3\n13:00-15:00",
    "Ca 4\n15:15-17:15",
    "Ca 5\n17:30-19:30",
]
SLOT_KEYS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]

CELL_COLORS = {
    "Da duyet":  ("#dcfce7", "#15803d"),
    "Cho duyet": ("#fef3c7", "#b45309"),
    "Tu choi":   ("#fee2e2", "#dc2626"),
}

LEGEND = [
    ("Da duyet",  "#dcfce7", "#15803d"),
    ("Cho duyet", "#fef3c7", "#b45309"),
    ("Tu choi",   "#fee2e2", "#dc2626"),
    ("Trong",     "#f8fafc", "#94a3b8"),
]

VN_MONTHS = ["", "Thang 1", "Thang 2", "Thang 3", "Thang 4", "Thang 5",
             "Thang 6", "Thang 7", "Thang 8", "Thang 9", "Thang 10",
             "Thang 11", "Thang 12"]


class ScheduleFrame(tk.Frame):
    def __init__(self, master, booking_controller, room_controller): # type: ignore
        super().__init__(master, bg=C_BG) # type: ignore
        self.booking_ctrl  = booking_controller
        self.room_ctrl     = room_controller
        self._week_offset  = 0
        self._week_lbl_var = tk.StringVar()
        self._build()

    def _build(self):
        page_header(self, "Lich bieu phong hoc", "📆").pack(fill="x")

        ctrl = tk.Frame(self, bg=C_BG, padx=20, pady=6)
        ctrl.pack(fill="x")

        tk.Label(ctrl, text="Phong:", bg=C_BG, font=("Segoe UI", 10)).pack(side="left")
        self._v_room = tk.StringVar(value="Tat ca phong")
        rooms = ["Tat ca phong"] + [r.room_id for r in self.room_ctrl.list_rooms()] # type: ignore
        ttk.Combobox(ctrl, textvariable=self._v_room, values=rooms,
                     state="readonly", font=("Segoe UI", 10),
                     width=16).pack(side="left", padx=(6, 12))
        btn(ctrl, "Lam moi", self._refresh, variant="primary").pack(side="left")

        legend_f = tk.Frame(ctrl, bg=C_BG)
        legend_f.pack(side="right", padx=8)
        for lbl, bg, fg in LEGEND:
            chip = tk.Frame(legend_f, bg=bg, padx=6, pady=2,
                            highlightthickness=1, highlightbackground="#d1d5db")
            chip.pack(side="left", padx=4)
            tk.Label(chip, text=lbl, bg=bg, fg=fg, font=("Segoe UI", 8)).pack()

        nav_bar = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                           highlightbackground=C_BORDER)
        nav_bar.pack(fill="x", padx=20, pady=(0, 6))
        nav_inner = tk.Frame(nav_bar, bg=C_SURFACE, pady=8)
        nav_inner.pack()

        def _nav_btn(parent, text, cmd): # type: ignore
            b = tk.Button(parent, text=text, bg="#f1f5f9", fg="#1e293b", # type: ignore
                          font=("Segoe UI", 9, "bold"), relief="flat",
                          cursor="hand2", padx=12, pady=5, bd=0,
                          activebackground="#e2e8f0", command=cmd) # pyright: ignore[reportUnknownArgumentType]
            b.bind("<Enter>", lambda _: b.config(bg="#e2e8f0"))
            b.bind("<Leave>", lambda _: b.config(bg="#f1f5f9"))
            return b

        _nav_btn(nav_inner, "< Tuan truoc", self._prev_week).pack(side="left", padx=(0, 8))

        tk.Label(nav_inner, textvariable=self._week_lbl_var,
                 bg=C_SURFACE, fg="#1e1b4b",
                 font=("Segoe UI", 11, "bold"), width=32,
                 anchor="center").pack(side="left")

        today_b = tk.Button(nav_inner, text="Hom nay", bg="#4f46e5", fg="white",
                            font=("Segoe UI", 9, "bold"), relief="flat",
                            cursor="hand2", padx=10, pady=5, bd=0,
                            activebackground="#4338ca", command=self._go_today)
        today_b.pack(side="left", padx=8)
        today_b.bind("<Enter>", lambda _: today_b.config(bg="#4338ca"))
        today_b.bind("<Leave>", lambda _: today_b.config(bg="#4f46e5"))

        _nav_btn(nav_inner, "Tuan sau >", self._next_week).pack(side="left")

        self._offset_badge = tk.Label(nav_inner, text="", bg="#dcfce7",
                                      fg="#15803d", font=("Segoe UI", 8, "bold"),
                                      padx=8, pady=3)
        self._offset_badge.pack(side="left", padx=10)

        outer = tk.Frame(self, bg=C_BG)
        outer.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        canvas = tk.Canvas(outer, bg=C_BG, highlightthickness=0)
        hsb = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview) # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        vsb = ttk.Scrollbar(outer, orient="vertical",   command=canvas.yview) # type: ignore
        canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)
        self._grid_frame = tk.Frame(canvas, bg=C_BG)
        self._grid_frame.bind("<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        self._refresh()

    def _prev_week(self):
        self._week_offset -= 1
        self._refresh()

    def _next_week(self):
        self._week_offset += 1
        self._refresh()

    def _go_today(self):
        self._week_offset = 0
        self._refresh()

    def _update_week_label(self):
        mon, sun = self.booking_ctrl.week_date_range(self._week_offset) # type: ignore
        m1, m2 = VN_MONTHS[mon.month], VN_MONTHS[sun.month] # type: ignore
        if mon.month == sun.month: # type: ignore
            label = f"Tuan  {mon.day} - {sun.day}  {m1}  {mon.year}" # type: ignore
        else:
            label = f"{mon.day} {m1} - {sun.day} {m2}  {mon.year}" # type: ignore
        self._week_lbl_var.set(label)
        if self._week_offset == 0:
            self._offset_badge.config(text="* Tuan nay", bg="#dcfce7", fg="#15803d")
        elif self._week_offset == -1:
            self._offset_badge.config(text="Tuan truoc", bg="#fef3c7", fg="#b45309")
        elif self._week_offset == 1:
            self._offset_badge.config(text="Tuan sau", bg="#dbeafe", fg="#1d4ed8")
        elif self._week_offset < 0:
            self._offset_badge.config(text=f"{abs(self._week_offset)} tuan truoc",
                                      bg="#fef3c7", fg="#b45309")
        else:
            self._offset_badge.config(text=f"+{self._week_offset} tuan",
                                      bg="#dbeafe", fg="#1d4ed8")

    def _show_cell_detail(self, entries: list, date_str: str,
                          day_name: str, slot_label: str) -> None:
        """Show a popup with booking details for a clicked schedule cell."""
        import tkinter as tk
        root = self.winfo_toplevel()
        dlg = tk.Toplevel(root)
        dlg.title(f"Chi tiet lich – {day_name}  {slot_label.split(chr(10))[0]}")
        dlg.resizable(False, False)
        dlg.configure(bg="#f8fafc")
        dlg.transient(root)  # type: ignore
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg="#1e1b4b", padx=20, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text=f"📆  {day_name}  –  {slot_label.split(chr(10))[0]}",
                 bg="#1e1b4b", fg="#e0e7ff",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(hdr, text=f"Ngay: {date_str}",
                 bg="#1e1b4b", fg="#818cf8",
                 font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(dlg, bg="#f8fafc", padx=18, pady=14)
        body.pack(fill="x")

        STATUS_COLORS = {
            "Da duyet":  ("#dcfce7", "#15803d"),
            "Cho duyet": ("#fef3c7", "#b45309"),
            "Tu choi":   ("#fee2e2", "#dc2626"),
        }
        for label, status in entries:
            sbg, sfg = STATUS_COLORS.get(status, ("#f1f5f9", "#475569"))
            row = tk.Frame(body, bg="#ffffff",
                           highlightthickness=1, highlightbackground="#e2e8f0")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"  {label}", bg="#ffffff", fg="#1e293b",
                     font=("Segoe UI", 10), anchor="w").pack(
                side="left", padx=8, pady=8, fill="x", expand=True)
            tk.Label(row, text=f"  {status}  ",
                     bg=sbg, fg=sfg,
                     font=("Segoe UI", 8, "bold")).pack(
                side="right", padx=8, pady=8)

        tk.Button(dlg, text="  Dong  ", bg="#4f46e5", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", padx=12, pady=6,
                  activebackground="#4338ca",
                  command=dlg.destroy).pack(pady=(0, 14))

        dlg.update_idletasks()
        rx = root.winfo_x() + root.winfo_width() // 2
        ry = root.winfo_y() + root.winfo_height() // 2
        dlg.geometry(f"+{rx - dlg.winfo_width() // 2}+{ry - dlg.winfo_height() // 2}")

    def _refresh(self):
        self._update_week_label()
        for w in self._grid_frame.winfo_children():
            w.destroy()

        room_filter = self._v_room.get()
        schedule_rows = self.booking_ctrl.build_schedule(self._week_offset) # type: ignore

        today = dt.date.today()
        mon, _ = self.booking_ctrl.week_date_range(self._week_offset) # type: ignore
        today_col = None
        if mon <= today <= mon + dt.timedelta(days=6):
            today_col = today.weekday()

        lookup = {}
        for s in schedule_rows: # type: ignore
            if room_filter != "Tat ca phong" and s.room_id != room_filter: # type: ignore
                continue
            key = (s.weekday, s.slot) # type: ignore
            lookup.setdefault(key, []).append((s.label, s.status)) # type: ignore

        gf = self._grid_frame

        tk.Label(gf, text="Ca / Ngay", bg="#1e1b4b", fg="#e0e7ff",
                 font=("Segoe UI", 9, "bold"),
                 width=14, height=2, relief="flat").grid(
                     row=0, column=0, padx=1, pady=1)

        for ci, day in enumerate(DAYS):
            date_for_col = mon + dt.timedelta(days=ci) # type: ignore
            date_str = f"{date_for_col.day}/{date_for_col.month}" # type: ignore
            is_today = (ci == today_col)
            if is_today:
                hdr_bg, hdr_fg = "#f59e0b", "#1a1a1a"
                day_text = f"\u25cf {day}\n{date_str}"
            else:
                hdr_bg, hdr_fg = "#1e1b4b", "#e0e7ff"
                day_text = f"{day}\n{date_str}"
            tk.Label(gf, text=day_text, bg=hdr_bg, fg=hdr_fg,
                     font=("Segoe UI", 9, "bold"),
                     width=17, height=2, relief="flat").grid(
                         row=0, column=ci + 1, padx=1, pady=1)

        for ri, (shift_lbl, slot_key) in enumerate(zip(SLOTS_LBL, SLOT_KEYS)):
            tk.Label(gf, text=shift_lbl, bg="#1e1b4b", fg="#a5b4fc",
                     font=("Segoe UI", 8, "bold"),
                     width=13, height=4, justify="center", relief="flat").grid(
                         row=ri + 1, column=0, padx=1, pady=1)

            for ci, day in enumerate(DAYS):
                entries = lookup.get((day, slot_key), []) # type: ignore
                is_today_col = (ci == today_col)

                if entries:
                    lines = "\n".join(e[0][:22] for e in entries[:3]) # type: ignore
                    if len(entries) > 3: # type: ignore
                        lines += f"\n+{len(entries)-3} khac" # type: ignore
                    bg, fg = CELL_COLORS.get(entries[0][1], ("#e0f2fe", "#0369a1")) # type: ignore
                    bd = 2 if is_today_col else 1
                    relief = "groove" if is_today_col else "solid"
                    cursor = "hand2"
                else:
                    bg = "#fffbeb" if is_today_col else "#f8fafc"
                    fg = "#b45309" if is_today_col else "#94a3b8"
                    lines = "Trong"
                    bd = 2 if is_today_col else 1
                    relief = "solid"
                    cursor = "arrow"

                cell_lbl = tk.Label(gf, text=lines, bg=bg, fg=fg,
                         font=("Segoe UI", 8), width=17, height=4,
                         relief=relief, bd=bd, cursor=cursor,
                         justify="center", wraplength=128)
                cell_lbl.grid(row=ri + 1, column=ci + 1, padx=1, pady=1)

                # Click to show details popup
                if entries:
                    date_for_cell = mon + dt.timedelta(days=ci) # type: ignore
                    date_str = date_for_cell.strftime("%d/%m/%Y") # type: ignore
                    cell_info = list(entries)  # capture
                    day_name = day
                    slot_label = SLOTS_LBL[ri]

                    def _show_detail(e: object,
                                     info=cell_info, ds=date_str,
                                     dn=day_name, sl=slot_label) -> None:
                        self._show_cell_detail(info, ds, dn, sl)

                    cell_lbl.bind("<Button-1>", _show_detail)