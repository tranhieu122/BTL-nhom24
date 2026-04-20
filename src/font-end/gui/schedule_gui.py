# schedule_gui.py  –  schedule view (7-day × 5-shift visual grid)
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from gui.theme import C_BG, C_SURFACE, C_BORDER, C_PRIMARY, C_DARK, page_header

DAYS      = ["Thu 2", "Thu 3", "Thu 4", "Thu 5", "Thu 6", "Thu 7", "Chu nhat"]
SLOTS_LBL = [
    "Ca 1\n7:00–9:00",
    "Ca 2\n9:15–11:15",
    "Ca 3\n13:00–15:00",
    "Ca 4\n15:15–17:15",
    "Ca 5\n17:30–19:30",
]
SLOT_KEYS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]

CELL_COLORS = {
    "Da duyet":  ("#dcfce7", "#15803d"),
    "Cho duyet": ("#fef3c7", "#b45309"),
    "Tu choi":   ("#fee2e2", "#dc2626"),
}

# legend items
LEGEND = [
    ("Da duyet",  "#dcfce7", "#15803d"),
    ("Cho duyet", "#fef3c7", "#b45309"),
    ("Tu choi",   "#fee2e2", "#dc2626"),
    ("Trong",     "#f8fafc", "#94a3b8"),
]


class ScheduleFrame(tk.Frame):
    def __init__(self, master, booking_controller, room_controller) -> None:
        super().__init__(master, bg=C_BG)
        self.booking_ctrl = booking_controller
        self.room_ctrl    = room_controller
        self._build()

    def _build(self) -> None:
        page_header(self, "Lich bieu phong hoc", "📆").pack(fill="x")

        # ── Control bar ──────────────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=C_BG, padx=20, pady=6)
        ctrl.pack(fill="x")

        tk.Label(ctrl, text="Phong:", bg=C_BG,
                 font=("Segoe UI", 10)).pack(side="left")
        self._v_room = tk.StringVar(value="Tat ca phong")
        rooms = ["Tat ca phong"] + [r.room_id for r in self.room_ctrl.list_rooms()]
        ttk.Combobox(ctrl, textvariable=self._v_room, values=rooms,
                     state="readonly", font=("Segoe UI", 10),
                     width=16).pack(side="left", padx=(6, 12))
        tk.Button(ctrl, text="Lam moi", bg=C_PRIMARY, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat",
                  padx=10, pady=4, cursor="hand2",
                  command=self._refresh).pack(side="left")

        # ── Legend ────────────────────────────────────────────────────────────
        legend_f = tk.Frame(ctrl, bg=C_BG)
        legend_f.pack(side="right", padx=8)
        for lbl, bg, fg in LEGEND:
            chip = tk.Frame(legend_f, bg=bg, padx=6, pady=2,
                            highlightthickness=1, highlightbackground="#d1d5db")
            chip.pack(side="left", padx=4)
            tk.Label(chip, text=lbl, bg=bg, fg=fg,
                     font=("Segoe UI", 8)).pack()

        # ── Scrollable grid area ──────────────────────────────────────────────
        outer = tk.Frame(self, bg=C_BG)
        outer.pack(fill="both", expand=True, padx=20, pady=(4, 16))

        canvas = tk.Canvas(outer, bg=C_BG, highlightthickness=0)
        hsb = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview)
        vsb = ttk.Scrollbar(outer, orient="vertical",   command=canvas.yview)
        canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        self._grid_frame = tk.Frame(canvas, bg=C_BG)
        self._grid_frame.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")
        canvas.bind("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._refresh()

    def _refresh(self) -> None:
        for w in self._grid_frame.winfo_children():
            w.destroy()

        room_filter = self._v_room.get()
        schedule_rows = self.booking_ctrl.build_schedule()

        # build lookup {(day, slot_key): [(label, status), …]}
        lookup: dict[tuple, list] = {}
        for s in schedule_rows:
            if room_filter != "Tat ca phong" and s.room_id != room_filter:
                continue
            key = (s.weekday, s.slot)
            lookup.setdefault(key, []).append((s.label, s.status))

        gf = self._grid_frame

        # ── Corner cell ────────────────────────────────────────────────────
        tk.Label(gf, text="Ca / Ngay", bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 9, "bold"),
                 width=14, height=2, relief="flat").grid(
                     row=0, column=0, padx=1, pady=1)

        # ── Day headers ────────────────────────────────────────────────────
        for ci, day in enumerate(DAYS):
            tk.Label(gf, text=day, bg=C_PRIMARY, fg="white",
                     font=("Segoe UI", 9, "bold"),
                     width=17, height=2, relief="flat").grid(
                         row=0, column=ci + 1, padx=1, pady=1)

        # ── Shift rows ─────────────────────────────────────────────────────
        for ri, (shift_lbl, slot_key) in enumerate(zip(SLOTS_LBL, SLOT_KEYS)):
            tk.Label(gf, text=shift_lbl, bg=C_DARK, fg="white",
                     font=("Segoe UI", 8, "bold"),
                     width=13, height=4,
                     justify="center", relief="flat").grid(
                         row=ri + 1, column=0, padx=1, pady=1)

            for ci, day in enumerate(DAYS):
                entries = lookup.get((day, slot_key), [])
                if entries:
                    lines = "\n".join(e[0][:22] for e in entries[:2])
                    if len(entries) > 2:
                        lines += f"\n+{len(entries)-2} khac"
                    bg, fg = CELL_COLORS.get(entries[0][1], ("#e0f2fe", "#0369a1"))
                else:
                    lines = "Trong"
                    bg, fg = "#f8fafc", "#94a3b8"
                tk.Label(gf, text=lines, bg=bg, fg=fg,
                         font=("Segoe UI", 8),
                         width=17, height=4,
                         relief="solid", bd=1,
                         justify="center", wraplength=128).grid(
                             row=ri + 1, column=ci + 1, padx=1, pady=1)

