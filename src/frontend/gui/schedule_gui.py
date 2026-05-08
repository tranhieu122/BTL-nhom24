# schedule_gui.py  –  schedule view (7-day × 5-shift visual grid)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import ttk
from gui.theme import (
    _get_c, page_header, btn, toast,
    C_DARK, C_ACCENT, C_LIGHT, C_BG, C_TEXT, C_SURFACE, C_BORDER
)

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
    "Tu choi":   ("#fdf2f8", "#db2777"),
    "Lich day":  ("#e0f2fe", "#0369a1"),   # light-blue: recurring schedule
}
CELL_ACCENT = {
    "Da duyet":  "#16a34a",
    "Cho duyet": "#f59e0b",
    "Tu choi":   "#ec4899",
}

LEGEND = [
    ("Da duyet",  "#dcfce7", "#15803d"),
    ("Cho duyet", "#fef3c7", "#b45309"),
    ("Tu choi",   "#fdf2f8", "#db2777"),
    ("Lich day",  "#e0f2fe", "#0369a1"),
    ("Trong",     "#f8fafc", "#94a3b8"),
]


def _cell_tooltip(cell: tk.Label, entries: "list[tuple[str, str]]",
                   date_str: str, slot_key: str) -> None:
    """Attach a rich hover tooltip to a busy schedule cell."""
    tip: list[tk.Toplevel | None] = [None]

    def _show(_: object = None) -> None:
        if tip[0] or not cell.winfo_exists():
            return
        x = cell.winfo_rootx() + cell.winfo_width() + 4
        y = cell.winfo_rooty()
        popup = tk.Toplevel(cell)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)  # type: ignore[arg-type]
        popup.configure(bg=C_DARK)

        frame = tk.Frame(popup, bg=C_DARK, padx=12, pady=10,
                         highlightthickness=1, highlightbackground=C_ACCENT)
        frame.pack()

        tk.Label(frame, text=f"📅  {date_str}  •  {slot_key}",
                 bg=C_DARK, fg=C_LIGHT,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 6))

        STATUS_CHIP: dict[str, tuple[str, str]] = {
            "Da duyet":  ("#dcfce7", "#15803d"),
            "Cho duyet": ("#fef3c7", "#b45309"),
            "Tu choi":   ("#fdf2f8", "#db2777"),
        }
        for label, status in entries[:5]:
            chip_bg, chip_fg = STATUS_CHIP.get(status, ("#f1f5f9", "#475569"))
            row_f = tk.Frame(frame, bg=_get_c("SB_BG"))
            row_f.pack(fill="x", pady=1)
            tk.Label(row_f, text=f"  {label[:28]}",
                     bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
                     font=("Segoe UI", 9)).pack(side="left")
            tk.Label(row_f, text=f"  {status}  ",
                     bg=chip_bg, fg=chip_fg,
                     font=("Segoe UI", 7, "bold")).pack(side="right", padx=4)

        if len(entries) > 5:
            tk.Label(frame, text=f"  + {len(entries) - 5} lich khac...",
                     bg=C_DARK, fg=C_ACCENT,
                     font=("Segoe UI", 7, "italic")).pack(anchor="w", pady=(4, 0))

        popup.update_idletasks()
        pw = popup.winfo_width()
        try:
            sw = cell.winfo_screenwidth()
            if x + pw > sw - 10:
                x = cell.winfo_rootx() - pw - 4
        except Exception:
            pass
        popup.geometry(f"+{x}+{y}")
        tip[0] = popup

    def _hide(_: object = None) -> None:
        if tip[0]:
            try:
                tip[0].destroy()
            except Exception:
                pass
            tip[0] = None

    cell.bind("<Enter>", _show, add="+")
    cell.bind("<Leave>", _hide, add="+")
    cell.bind("<Destroy>", _hide, add="+")

VN_MONTHS = ["", "Thang 1", "Thang 2", "Thang 3", "Thang 4", "Thang 5",
             "Thang 6", "Thang 7", "Thang 8", "Thang 9", "Thang 10",
             "Thang 11", "Thang 12"]


class ScheduleFrame(tk.Frame):
    def __init__(self, master, booking_controller, room_controller, current_user): # type: ignore
        super().__init__(master, bg=_get_c("BG")) # type: ignore
        self.booking_ctrl  = booking_controller
        self.room_ctrl     = room_controller
        self.current_user  = current_user
        self._week_offset  = 0
        self._week_lbl_var = tk.StringVar()
        self._only_mine    = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        page_header(self, "Lich bieu phong hoc", "📆").pack(fill="x")

        ctrl = tk.Frame(self, bg=_get_c("BG"), padx=20)
        ctrl.pack(fill="x", pady=(0, 4))

        tk.Label(ctrl, text="Phong:", bg=_get_c("BG"), fg=_get_c("TEXT"), font=("Segoe UI", 10)).pack(side="left")
        self._v_room = tk.StringVar(value="Tat ca phong")
        rooms = ["Tat ca phong"] + [r.room_id for r in self.room_ctrl.list_rooms()] # type: ignore
        ttk.Combobox(ctrl, textvariable=self._v_room, values=rooms,
                     state="readonly", font=("Segoe UI", 10),
                     width=16).pack(side="left", padx=(6, 12))
        
        tk.Checkbutton(ctrl, text="Chi hien lich cua toi", variable=self._only_mine,
                       bg=_get_c("BG"), fg=_get_c("TEXT"), activebackground=_get_c("BG"), font=("Segoe UI", 10),
                       command=self._refresh).pack(side="left", padx=(0, 12))

        btn(ctrl, "🔄 Lam moi", self._refresh, variant="primary").pack(side="left")
        btn(ctrl, "📊 Xuat CSV", self._export_csv, variant="secondary").pack(
            side="left", padx=(8, 0))

        legend_f = tk.Frame(ctrl, bg=_get_c("BG"))
        legend_f.pack(side="right", padx=8)
        for lbl, bg, fg in LEGEND:
            chip = tk.Frame(legend_f, bg=bg, padx=6, pady=2,
                            highlightthickness=1, highlightbackground="#d1d5db")
            chip.pack(side="left", padx=4)
            tk.Label(chip, text=lbl, bg=bg, fg=fg, font=("Segoe UI", 8)).pack()

        nav_bar = tk.Frame(self, bg=_get_c("SURFACE"), highlightthickness=1,
                           highlightbackground=_get_c("BORDER"))
        nav_bar.pack(fill="x", padx=20, pady=0)
        nav_inner = tk.Frame(nav_bar, bg=_get_c("SURFACE"), pady=4)
        nav_inner.pack()

        def _nav_btn(parent, text, cmd): # type: ignore
            b = tk.Button(parent, text=text, bg=_get_c("SURFACE"), fg=_get_c("TEXT"), # type: ignore
                          font=("Segoe UI", 9, "bold"), relief="flat",
                          cursor="hand2", padx=12, pady=5, bd=0,
                          activebackground=_get_c("BORDER"), command=cmd) # pyright: ignore[reportUnknownArgumentType]
            b.bind("<Enter>", lambda _: b.config(bg=_get_c("BORDER")))
            b.bind("<Leave>", lambda _: b.config(bg=_get_c("SURFACE")))
            return b

        _nav_btn(nav_inner, "< Tuan truoc", self._prev_week).pack(side="left", padx=(0, 8))

        tk.Label(nav_inner, textvariable=self._week_lbl_var,
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                 font=("Segoe UI", 11, "bold"), width=32,
                 anchor="center").pack(side="left")

        today_b = tk.Button(nav_inner, text="Hom nay", bg=_get_c("ACCENT"), fg="white",
                            font=("Segoe UI", 9, "bold"), relief="flat",
                            cursor="hand2", padx=10, pady=5, bd=0,
                            activebackground=_get_c("INDIGO_400"), command=self._go_today)
        today_b.pack(side="left", padx=8)
        today_b.bind("<Enter>", lambda _: today_b.config(bg=_get_c("INDIGO_400")))
        today_b.bind("<Leave>", lambda _: today_b.config(bg=_get_c("ACCENT")))

        _nav_btn(nav_inner, "Tuan sau >", self._next_week).pack(side="left")

        self._offset_badge = tk.Label(nav_inner, text="", bg="#dcfce7",
                                      fg="#15803d", font=("Segoe UI", 8, "bold"),
                                      padx=8, pady=3)
        self._offset_badge.pack(side="left", padx=10)

        # ── Scrollable grid canvas — expands to fill all remaining space ──────
        outer = tk.Frame(self, bg=_get_c("BG"))
        outer.pack(side="top", fill="both", expand=True, padx=20, pady=0)

        # ── Week summary stats bar
        self._stats_bar = tk.Frame(self, bg=_get_c("SURFACE"),
                                   highlightthickness=1,
                                   highlightbackground=_get_c("BORDER"))
        self._stats_bar.pack(side="bottom", fill="x", padx=20, pady=(8, 16))

        canvas = tk.Canvas(outer, bg=_get_c("BG"), highlightthickness=0)
        hsb = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview) # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        vsb = ttk.Scrollbar(outer, orient="vertical",   command=canvas.yview) # type: ignore
        canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)
        self._grid_frame = tk.Frame(canvas, bg=_get_c("BG")) # Changed to C_BG to avoid white gap
        self._grid_window = canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")
        
        def _on_frame_resize(e): # type: ignore
            canvas.configure(scrollregion=canvas.bbox("all"))
                
        def _on_canvas_resize(e): # type: ignore
            # Force the grid frame to be at least as wide as the canvas
            canvas.itemconfig(self._grid_window, width=e.width) # type: ignore
            
        self._grid_frame.bind("<Configure>", _on_frame_resize) # type: ignore
        canvas.bind("<Configure>", _on_canvas_resize) # type: ignore
        canvas.bind("<MouseWheel>",
                    lambda e=None: canvas.yview_scroll(-1*(e.delta//120) if e else 0, "units"))

        # Keyboard week navigation: bind on the toplevel; guard with winfo_ismapped
        def _kb_prev(ev: object = None) -> None:
            try:
                if self.winfo_ismapped():
                    self._prev_week()
            except Exception:
                pass

        def _kb_next(ev: object = None) -> None:
            try:
                if self.winfo_ismapped():
                    self._next_week()
            except Exception:
                pass

        def _kb_today(ev: object = None) -> None:
            try:
                if self.winfo_ismapped():
                    self._go_today()
            except Exception:
                pass

        self.after(200, lambda: (
            self.winfo_toplevel().bind("<Left>",  _kb_prev, add="+"),
            self.winfo_toplevel().bind("<Right>", _kb_next, add="+"),
            self.winfo_toplevel().bind("<Control-t>", _kb_today, add="+"),
        ))
        self._refresh()

    # ── Export current week to CSV ──────────────────────────────────────────
    def _export_csv(self) -> None:
        import csv
        from tkinter import filedialog
        mon, sun = self.booking_ctrl.week_date_range(self._week_offset)  # type: ignore
        default_name = f"lich_phong_{mon.isoformat()}_den_{sun.isoformat()}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_name,
            title="Luu lich bieu thanh CSV",
        )
        if not path:
            return
        try:
            only_mine = self._only_mine.get()
            uid  = self.current_user.user_id if only_mine else ""  # type: ignore
            rows = self.booking_ctrl.build_schedule(  # type: ignore
                self._week_offset, only_user_id=uid)
            room_filter = self._v_room.get()
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Ngay", "Ca hoc", "Phong", "Lich / Mon hoc", "Trang thai"])
                for r in rows:  # type: ignore
                    if room_filter != "Tat ca phong" and r.room_id != room_filter:  # type: ignore
                        continue
                    w.writerow([r.weekday, r.slot, r.room_id, r.label, r.status])  # type: ignore
            fname = path.replace("\\", "/").split("/")[-1]
            toast(self, f"✅ Xuat CSV thanh cong: {fname}")
        except Exception as exc:
            from tkinter import messagebox
            messagebox.showerror("Loi xuat CSV", str(exc))

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

    def _show_attendance_dialog(self, entry: tuple[str, str, str], date_str: str,
                                day_name: str, slot_label: str) -> None:
        import tkinter as tk
        from tkinter import ttk
        from dao.user_dao import UserDAO
        from gui.theme import C_PRIMARY, C_BG, C_SURFACE, C_BORDER, C_TEXT, C_MUTED, btn, toast # type: ignore
        
        label, status, room_id = entry # type: ignore
        subject = label.replace("[CK] ", "")
        
        root = self.winfo_toplevel()
        dlg = tk.Toplevel(root)
        dlg.title(f"Diem danh - {subject}")
        dlg.geometry("1000x700")
        dlg.configure(bg="#f1f5f9")
        dlg.transient(root) # type: ignore
        dlg.grab_set()

        # Custom Styles
        style = ttk.Style(dlg)
        style.theme_use("clam")
        style.configure("Attendance.Treeview", 
                        rowheight=40, 
                        font=("Segoe UI", 10), 
                        background="#ffffff", 
                        fieldbackground="#ffffff", 
                        borderwidth=0,
                        relief="flat")
        style.configure("Attendance.Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background="#f8fafc", 
                        foreground="#64748b",
                        relief="flat",
                        padding=10)
        style.map("Attendance.Treeview", 
                  background=[("selected", "#eef2ff")], 
                  foreground=[("selected", "#4f46e5")])

        # Top Decorative Header (Gradient simulation)
        top_bar = tk.Frame(dlg, bg="#1e1b4b", height=4)
        top_bar.pack(fill="x")

        # Main Header Card
        header_card = tk.Frame(dlg, bg="#ffffff", padx=30, pady=25, highlightthickness=1, highlightbackground="#e2e8f0")
        header_card.pack(fill="x", padx=0, pady=0)
        
        # Left side: Subject & Time
        title_f = tk.Frame(header_card, bg="#ffffff")
        title_f.pack(side="left", fill="y")
        
        tk.Label(title_f, text=f"Lop hoc: {subject}", 
                 bg="#ffffff", fg="#0f172a", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        
        details_f = tk.Frame(title_f, bg="#ffffff")
        details_f.pack(anchor="w", pady=(8, 0))
        
        tk.Label(details_f, text=f"📅 {day_name}, {date_str}", 
                 bg="#ffffff", fg="#64748b", font=("Segoe UI", 10)).pack(side="left")
        tk.Label(details_f, text=" • ", bg="#ffffff", fg="#cbd5e1").pack(side="left")
        tk.Label(details_f, text=f"🕒 {slot_label.split(chr(10))[0]}", 
                 bg="#ffffff", fg="#64748b", font=("Segoe UI", 10)).pack(side="left")
        tk.Label(details_f, text=" • ", bg="#ffffff", fg="#cbd5e1").pack(side="left")
        tk.Label(details_f, text=f"📍 {room_id}", 
                 bg="#ffffff", fg="#4f46e5", font=("Segoe UI", 10, "bold")).pack(side="left")

        # Right side: Stats/Actions
        stats_f = tk.Frame(header_card, bg="#ffffff")
        stats_f.pack(side="right", fill="y")
        
        present_badge = tk.Frame(stats_f, bg="#dcfce7", padx=12, pady=6)
        present_badge.pack(side="right")
        tk.Label(present_badge, text="DA DIEM DANH: 0", bg="#dcfce7", fg="#166534", font=("Segoe UI", 9, "bold")).pack()

        # Body Area
        body = tk.Frame(dlg, bg="#f1f5f9", padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Toolbar Card
        toolbar = tk.Frame(body, bg="#ffffff", padx=20, pady=15, highlightthickness=1, highlightbackground="#e2e8f0")
        toolbar.pack(fill="x", pady=(0, 20))

        # Search / Filter
        search_f = tk.Frame(toolbar, bg="#ffffff")
        search_f.pack(side="left")
        
        tk.Label(search_f, text="Loc danh sach:", bg="#ffffff", fg="#64748b", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        search_var = tk.StringVar()
        search_ent = tk.Entry(search_f, textvariable=search_var, font=("Segoe UI", 10), width=25, relief="flat", highlightthickness=1, highlightbackground="#e2e8f0", highlightcolor="#4f46e5")
        search_ent.pack(side="left", ipady=6, padx=5)
        
        # Attendance Code Input
        code_f = tk.Frame(toolbar, bg="#ffffff")
        code_f.pack(side="right")
        
        tk.Label(code_f, text="Ma diem danh:", bg="#ffffff", fg="#64748b", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        kw_entry = tk.Entry(code_f, font=("Segoe UI", 10, "bold"), width=12, relief="flat", highlightthickness=1, highlightbackground="#e2e8f0", highlightcolor="#10b981", justify="center")
        kw_entry.pack(side="left", ipady=6, padx=5)
        
        def _save_kw():
            from tkinter import messagebox
            if not kw_entry.get().strip():
                messagebox.showwarning("Loi", "Vui long nhap ma diem danh", parent=dlg)
                return
            toast(dlg, "Da mo cong diem danh thanh cong!", kind="success")
            kw_entry.delete(0, tk.END)

        btn(code_f, "Mo diem danh", _save_kw, variant="primary", icon="⚡").pack(side="left", padx=(10, 0))

        # Table Container
        table_f = tk.Frame(body, bg="#ffffff", highlightthickness=1, highlightbackground="#e2e8f0")
        table_f.pack(fill="both", expand=True)
        
        cols = ("stt", "ma_so", "ho_dem", "ten", "trang_thai")
        hdrs = ("STT", "MA SINH VIEN", "HO VA TEN DEM", "TEN", "TRANG THAI")
        wids = (60, 150, 300, 150, 150)
        
        tree = ttk.Treeview(table_f, columns=cols, show="headings", style="Attendance.Treeview")
        for c, h, w in zip(cols, hdrs, wids):
            tree.heading(c, text=h, anchor="w")
            tree.column(c, width=w, anchor="w" if c != "stt" else "center")
            
        vsb = ttk.Scrollbar(table_f, orient="vertical", command=tree.yview) # type: ignore
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        tree.tag_configure("odd", background="#ffffff")
        tree.tag_configure("even", background="#f8fafc")

        # Load Data
        try:
            students = UserDAO().search(role="Sinh vien")
        except Exception:
            students = []
            
        if not students:
            from models.user import User
            students = [
                User(f"SV{i}", f"2023{1000+i}", f"Nguyen Van {chr(65+i)}", "Sinh vien", "", "", "", "Hoat dong") # type: ignore
                for i in range(1, 20)
            ]

        def _fill_tree(filter_text=""): # type: ignore
            for item in tree.get_children():
                tree.delete(item)
            
            filtered = [s for s in students if filter_text.lower() in s.full_name.lower() or filter_text.lower() in s.username.lower()]
            
            for i, s in enumerate(filtered, 1):
                parts = s.full_name.rsplit(" ", 1)
                ho_dem, ten = (parts[0], parts[1]) if len(parts) == 2 else ("", s.full_name)
                
                status_text = "● Co mat" if i <= 3 else "○ Chua co mat"
                status_val = "Co mat" if i <= 3 else "Vang" # type: ignore
                
                tags = ("even" if i % 2 == 0 else "odd",)
                tree.insert("", "end", values=(i, s.username, ho_dem, ten, status_text), tags=tags)

        search_var.trace_add("write", lambda *args: _fill_tree(search_var.get())) # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
        _fill_tree()

        # Footer
        footer = tk.Frame(dlg, bg="#ffffff", padx=30, pady=15, highlightthickness=1, highlightbackground="#e2e8f0")
        footer.pack(fill="x")
        
        tk.Label(footer, text="He thong quan ly diem danh tu dong v2.0", bg="#ffffff", fg="#94a3b8", font=("Segoe UI", 8)).pack(side="left")
        
        btn(footer, "Dong", dlg.destroy, variant="ghost").pack(side="right")

        # Center Dialog
        dlg.update_idletasks()
        rx = root.winfo_x() + root.winfo_width() // 2
        ry = root.winfo_y() + root.winfo_height() // 2
        dlg.geometry(f"+{rx - dlg.winfo_width() // 2}+{ry - dlg.winfo_height() // 2}")

    def _show_cell_detail(self, entries: list[tuple[str, str, str]], date_str: str,
                           day_name: str, slot_label: str) -> None:
        """Handle clicking a cell: directly show dialog if 1 entry, or show a picker if multiple."""
        if not entries: return
        if len(entries) == 1:
            self._show_attendance_dialog(entries[0], date_str, day_name, slot_label)
            return

        root = self.winfo_toplevel()
        dlg = tk.Toplevel(root)
        dlg.title("Chon lich bieu")
        dlg.geometry("450x350")
        dlg.configure(bg="#ffffff")
        dlg.transient(root) # type: ignore
        dlg.grab_set()

        tk.Label(dlg, text="O nay co nhieu lich trung nhau", bg="#ffffff", 
                 fg="#1e1b4b", font=("Segoe UI", 11, "bold"), pady=15).pack()
        
        container = tk.Frame(dlg, bg="#ffffff", padx=20)
        container.pack(fill="both", expand=True)

        for e in entries:
            lbl_txt, status, room_id = e # type: ignore
            row = tk.Frame(container, bg="#f8fafc", highlightthickness=1, 
                           highlightbackground="#e2e8f0", pady=8)
            row.pack(fill="x", pady=4)
            
            tk.Label(row, text=f"📍 {room_id} - {lbl_txt}", bg="#f8fafc", 
                     fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=10)
            
            def _go(entry=e): # type: ignore
                dlg.destroy()
                self._show_attendance_dialog(entry, date_str, day_name, slot_label) # type: ignore

            b = tk.Button(row, text="Xem diem danh", command=_go, bg="#4f46e5",  # type: ignore
                          fg="white", font=("Segoe UI", 8, "bold"), relief="flat", 
                          padx=12, pady=4, cursor="hand2")
            b.pack(side="right", padx=10)
            b.bind("<Enter>", lambda _, bt=b: bt.config(bg="#4338ca"))
            b.bind("<Leave>", lambda _, bt=b: bt.config(bg="#4f46e5"))

        tk.Button(dlg, text="Dong", command=dlg.destroy, bg="#ffffff", 
                  fg="#64748b", font=("Segoe UI", 9), relief="flat", 
                  pady=10, cursor="hand2").pack(side="bottom")

    def _refresh(self):
        self._update_week_label()
        for w in self._grid_frame.winfo_children():
            w.destroy()
        
        room_filter = self._v_room.get()
        only_mine = self._only_mine.get()
        user_id = self.current_user.user_id if only_mine else "" # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        schedule_rows = self.booking_ctrl.build_schedule(self._week_offset, only_user_id=user_id) # type: ignore

        today = dt.date.today()
        mon, _ = self.booking_ctrl.week_date_range(self._week_offset) # type: ignore

        # Stats counters
        total_bookings = 0
        stats = {"Da duyet": 0, "Cho duyet": 0, "Tu choi": 0}

        grid_data: dict[tuple[int, str], list[tuple[str, str, str]]] = {}
        for row in schedule_rows: # type: ignore
            if room_filter != "Tat ca phong" and row.room_id != room_filter: # type: ignore
                continue
            
            if row.status in stats: # type: ignore
                stats[row.status] += 1 # type: ignore
                total_bookings += 1
            
            try:
                day_idx = DAYS.index(row.weekday) # type: ignore
                grid_data.setdefault((day_idx, row.slot), []).append( # type: ignore
                    (row.label, row.status, row.room_id) # type: ignore
                )
            except ValueError:
                continue

        # ── Slot-label column (col 0) ─────────────────────────────────────────
        for s_idx, s_lbl in enumerate(SLOTS_LBL):
            sh = tk.Frame(self._grid_frame, bg="#f1f5f9",
                          highlightthickness=1, highlightbackground="#e2e8f0")
            sh.grid(row=s_idx + 1, column=0, sticky="nsew")
            tk.Label(sh, text=s_lbl, bg="#f1f5f9", fg="#64748b",
                     font=("Segoe UI", 8, "bold"),
                     justify="center").pack(expand=True, padx=4, pady=6)

        # ── Day columns ───────────────────────────────────────────────────────
        for d_idx in range(7):
            d_date     = mon + dt.timedelta(days=d_idx)  # type: ignore
            d_str      = d_date.strftime("%d/%m")         # type: ignore
            is_today   = (d_date == today)                # type: ignore
            is_weekend = d_idx >= 5

            # Day header
            hdr_bg = "#dbeafe" if is_today else ("#f9fafb" if is_weekend else "#f1f5f9")
            hdr_fg = "#1d4ed8" if is_today else ("#94a3b8" if is_weekend else "#64748b")
            h = tk.Frame(self._grid_frame, bg=hdr_bg,
                         highlightthickness=1, highlightbackground="#e2e8f0")
            h.grid(row=0, column=d_idx + 1, sticky="nsew")
            if is_today:
                tk.Frame(h, bg="#3b82f6", height=3).pack(fill="x", side="top")
                badge_row = tk.Frame(h, bg=hdr_bg)
                badge_row.pack(fill="x")
                tk.Label(badge_row, text=DAYS[d_idx], bg=hdr_bg, fg=hdr_fg,
                         font=("Segoe UI", 9, "bold")).pack(side="left", padx=6, pady=(3, 0))
                tk.Label(badge_row, text=" HOM NAY ", bg="#3b82f6", fg="white",
                         font=("Segoe UI", 6, "bold")).pack(side="right", padx=4, pady=(3, 0))
                tk.Label(h, text=d_str, bg=hdr_bg, fg=hdr_fg,
                         font=("Segoe UI", 8)).pack(pady=(0, 4))
            else:
                tk.Label(h, text=DAYS[d_idx], bg=hdr_bg, fg=hdr_fg,
                         font=("Segoe UI", 9, "bold")).pack(pady=(5, 0))
                tk.Label(h, text=d_str, bg=hdr_bg, fg=hdr_fg,
                         font=("Segoe UI", 8)).pack(pady=(0, 5))

            # Slot cells
            for s_idx, s_key in enumerate(SLOT_KEYS):
                entries  = grid_data.get((d_idx, s_key), [])
                cell_bg  = "#f0f6ff" if is_today else ("#fafafa" if is_weekend else "#f8fafc")
                cell_hl  = "#bfdbfe" if is_today else "#e2e8f0"
                cell = tk.Frame(self._grid_frame, bg=cell_bg,
                                highlightthickness=1, highlightbackground=cell_hl)
                cell.grid(row=s_idx + 1, column=d_idx + 1, sticky="nsew")

                if entries:
                    _, top_status, _ = entries[0]
                    top_bg, top_fg = CELL_COLORS.get(top_status, ("#f1f5f9", "#475569"))
                    accent_c = CELL_ACCENT.get(top_status, "#94a3b8")

                    inner = tk.Frame(cell, bg=top_bg, cursor="hand2")
                    inner.pack(fill="both", expand=True, padx=2, pady=2)
                    tk.Frame(inner, bg=accent_c, width=3).pack(side="left", fill="y")
                    content = tk.Frame(inner, bg=top_bg)
                    content.pack(fill="both", expand=True, padx=4, pady=3)

                    # Up to 2 stacked entry chips + overflow badge
                    for e_lbl, e_status, _ in entries[:2]:
                        e_bg, e_fg = CELL_COLORS.get(e_status, ("#f1f5f9", "#475569"))
                        short = (e_lbl[:16] + "\u2026") if len(e_lbl) > 16 else e_lbl
                        tk.Label(content, text=short,
                                 bg=e_bg, fg=e_fg,
                                 font=("Segoe UI", 7, "bold"),
                                 anchor="w", padx=3, pady=1
                                 ).pack(fill="x", pady=(0, 1))
                    if len(entries) > 2:
                        tk.Label(content,
                                 text=f"  +{len(entries) - 2} lich nua",
                                 bg=top_bg, fg="#94a3b8",
                                 font=("Segoe UI", 6, "italic"),
                                 anchor="w").pack(fill="x")

                    _cell_tooltip(inner, [(e[0], e[1]) for e in entries],  # type: ignore
                                  d_date.isoformat(), s_key)               # type: ignore

                    def _open(  # type: ignore
                        ev,
                        ents=entries, ds=d_date.isoformat(),  # type: ignore
                        dn=DAYS[d_idx], sl=SLOTS_LBL[s_idx],
                    ) -> None:
                        self._show_cell_detail(ents, ds, dn, sl)  # type: ignore

                    inner.bind("<Button-1>", _open)    # type: ignore
                    content.bind("<Button-1>", _open)  # type: ignore
                    for ch in content.winfo_children():
                        ch.bind("<Button-1>", _open)   # type: ignore
                else:
                    # Empty cell — subtle hover
                    orig_bg  = cell_bg
                    hover_bg = "#f0fdf4" if not is_weekend else "#f9fafb"
                    dash = tk.Label(cell, text="\u2014", bg=orig_bg,
                                    fg="#e2e8f0", font=("Segoe UI", 10))
                    dash.pack(expand=True)

                    def _enter(_, c=cell, d=dash, hbg=hover_bg) -> None:
                        c.config(bg=hbg); d.config(bg=hbg, fg="#dcfce7")

                    def _leave(_, c=cell, d=dash, obg=orig_bg) -> None:
                        c.config(bg=obg); d.config(bg=obg, fg="#e2e8f0")

                    cell.bind("<Enter>", _enter)
                    cell.bind("<Leave>", _leave)
                    dash.bind("<Enter>", _enter)
                    dash.bind("<Leave>", _leave)

        # Update Stats Bar
        for w in self._stats_bar.winfo_children():
            w.destroy()

        busy_cells = sum(1 for v in grid_data.values() if v)
        total_cells = 7 * 5
        rate = int(busy_cells * 100 / total_cells) if total_cells else 0

        # Dark header strip with keyboard hint
        header_f = tk.Frame(self._stats_bar, bg=_get_c("ACCENT"), padx=16, pady=8)
        header_f.pack(fill="x")
        tk.Label(header_f, text="📊 Thong ke tuan nay",
                 bg=_get_c("ACCENT"), fg="white",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(header_f, text="← →  chuyen tuan  |  Ctrl+T  ve hom nay",
                 bg=_get_c("ACCENT"), fg=_get_c("LIGHT"),
                 font=("Segoe UI", 8)).pack(side="right")

        # Stat chips
        chips_f = tk.Frame(self._stats_bar, bg=_get_c("SURFACE"), padx=14, pady=10)
        chips_f.pack(fill="x")

        def _stat_chip(parent, icon, label, value, fg):  # type: ignore
            chip = tk.Frame(parent, bg=_get_c("SURFACE"),
                            highlightthickness=1, highlightbackground=_get_c("BORDER"),
                            padx=14, pady=8)
            chip.pack(side="left", padx=4)
            tk.Label(chip, text=f"{icon}  {value}",
                     bg=_get_c("SURFACE"), fg=fg,
                     font=("Segoe UI", 15, "bold")).pack(anchor="w")
            tk.Label(chip, text=label,
                     bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                     font=("Segoe UI", 8)).pack(anchor="w")

        _stat_chip(chips_f, "📅", "Tong so lich",  str(total_bookings),    "#4f46e5")
        _stat_chip(chips_f, "✅", "Da duyet",       str(stats["Da duyet"]), "#15803d")
        _stat_chip(chips_f, "⏳", "Cho duyet",      str(stats["Cho duyet"]),"#b45309")
        _stat_chip(chips_f, "❌", "Tu choi",        str(stats["Tu choi"]),  "#db2777")
        _stat_chip(chips_f, "📈", "Ty le su dung",  f"{rate}%",            "#0369a1")

        # Occupancy progress bar
        prog_f = tk.Frame(self._stats_bar, bg=_get_c("SURFACE"), padx=14)
        prog_f.pack(fill="x", pady=(0, 8))
        tk.Label(prog_f,
                 text=f"Su dung phong: {busy_cells}/{total_cells} o",
                 bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 8)).pack(side="left")
        bar_outer = tk.Frame(prog_f, bg=_get_c("BORDER"), height=6)
        bar_outer.pack(side="left", fill="x", expand=True, padx=(12, 0))
        fill_pct = min(rate, 100) / 100
        bar_color = "#15803d" if rate >= 70 else ("#b45309" if rate >= 30 else "#0369a1")
        tk.Frame(bar_outer, bg=bar_color, height=6).place(
            x=0, y=0, relheight=1.0, relwidth=fill_pct)
        tk.Label(prog_f, text=f"  {rate}%",
                 bg=_get_c("SURFACE"), fg=bar_color,
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        # ── Grid proportions ─────────────────────────────────────────────────
        self._grid_frame.columnconfigure(0, weight=0, minsize=82)
        for i in range(1, 8):
            self._grid_frame.columnconfigure(i, weight=1, uniform="col", minsize=106)
        self._grid_frame.rowconfigure(0, weight=0, minsize=58)
        for i in range(1, 6):
            self._grid_frame.rowconfigure(i, weight=1, uniform="row", minsize=72)
