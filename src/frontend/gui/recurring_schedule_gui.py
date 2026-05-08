# recurring_schedule_gui.py  –  Tao lich day theo chu ky tuan
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any
from tkcalendar import DateEntry  # type: ignore[import-untyped]

from gui.theme import (
    F_BODY, F_BODY_B, F_SECTION, F_SMALL, _get_c,
    C_BG, C_BORDER, C_SURFACE, C_TEXT, C_MUTED,
    C_PRIMARY, C_SUCCESS, C_SUCCESS_BG,
    C_WARNING, C_WARNING_BG,
    C_DANGER, C_DANGER_BG,
    page_header, btn, fill_tree, toast,
)

# ── Constants ────────────────────────────────────────────────────────────────
WEEKDAYS = [
    (1, "Thu 2 (Mon)"),
    (2, "Thu 3 (Tue)"),
    (3, "Thu 4 (Wed)"),
    (4, "Thu 5 (Thu)"),
    (5, "Thu 6 (Fri)"),
    (6, "Thu 7 (Sat)"),
    (7, "Chu nhat (Sun)"),
]
SHORT_DAY = {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}

SLOT_PRESETS = [
    ("Ca 1  (07:00 – 09:00)", "07:00", "09:00"),
    ("Ca 2  (09:15 – 11:15)", "09:15", "11:15"),
    ("Ca 3  (13:00 – 15:00)", "13:00", "15:00"),
    ("Ca 4  (15:15 – 17:15)", "15:15", "17:15"),
    ("Ca 5  (17:30 – 19:30)", "17:30", "19:30"),
    ("Tuy chinh",              "",      ""),
]

def _get_status_chip(status: str) -> tuple[str, str]:
    mapping = {
        "Hoat dong": (_get_c("SUCCESS_BG"), _get_c("SUCCESS")),
        "Da xong":   (_get_c("INFO_BG"),    _get_c("ACCENT")),
        "Huy":       (_get_c("DANGER_BG"),  _get_c("DANGER")),
        "Du kien":   (_get_c("WARNING_BG"), _get_c("WARNING")),
        "Da dien ra":(_get_c("SUCCESS_BG"), _get_c("SUCCESS")),
    }
    return mapping.get(status, (_get_c("BORDER"), _get_c("MUTED")))

# ── Helpers ───────────────────────────────────────────────────────────────────

def _chip(parent: tk.Widget, text: str, bg: str, fg: str) -> tk.Label:
    return tk.Label(parent, text=f"  {text}  ", bg=bg, fg=fg,
                    font=F_SMALL, relief="flat")


def _section(parent: tk.Widget, title: str) -> tk.Frame:
    wrapper = tk.Frame(parent, bg=_get_c("BG"))
    wrapper.pack(fill="x", padx=20, pady=(10, 2))
    tk.Frame(wrapper, bg=_get_c("BORDER"), height=1).pack(fill="x")
    tk.Label(wrapper, text=title, bg=_get_c("BG"), fg=_get_c("MUTED"),
             font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 0))
    return wrapper


def _field_row(parent: tk.Widget, label: str,
               widget_fn) -> tk.Frame:
    row = tk.Frame(parent, bg=_get_c("SURFACE"))
    row.pack(fill="x", padx=20, pady=3)
    tk.Label(row, text=label, bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
             font=F_BODY, width=22, anchor="w").pack(side="left")
    widget_fn(row)
    return row


# ═══════════════════════════════════════════════════════════════════════════════
#  Main Frame
# ═══════════════════════════════════════════════════════════════════════════════

class RecurringScheduleFrame(tk.Frame):
    """Page: Tao lich day theo chu ky tuan."""

    def __init__(self, master: tk.Misc,
                 schedule_rule_controller: Any,
                 room_controller: Any,
                 user_controller: Any,
                 current_user: Any = None) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.ctrl       = schedule_rule_controller
        self.room_ctrl  = room_controller
        self.user_ctrl  = user_controller
        self.current_user = current_user
        self._selected_rule_id: int | None = None
        self._build()

    # ── Build layout ──────────────────────────────────────────────────────────

    def _build(self) -> None:
        page_header(self, "Lich day theo chu ky tuan", "🔁").pack(fill="x")

        # Two-column layout: left = form, right = list
        pane = tk.Frame(self, bg=_get_c("BG"))
        pane.pack(fill="both", expand=True, padx=0, pady=0)
        pane.columnconfigure(0, weight=3)
        pane.columnconfigure(1, weight=5)
        pane.rowconfigure(0, weight=1)

        self._build_form(pane)
        self._build_list(pane)
        self._refresh_list()

    # ── LEFT: Form ────────────────────────────────────────────────────────────

    def _build_form(self, parent: tk.Frame) -> None:
        left = tk.Frame(parent, bg=_get_c("BG"),
                        highlightthickness=1, highlightbackground=_get_c("BORDER"))
        left.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)

        tk.Label(left, text="Tao moi lich day chu ky", bg=_get_c("BG"),
                 fg=_get_c("TEXT"), font=F_SECTION).pack(anchor="w", padx=20, pady=(14, 4))

        # Scrollable form body
        canvas = tk.Canvas(left, bg=_get_c("BG"), highlightthickness=0)
        vsb = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)  # type: ignore
        canvas.configure(yscrollcommand=vsb.set)
        body = tk.Frame(canvas, bg=_get_c("BG"))
        body.bind("<Configure>",
                  lambda _=None: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")
        
        def _on_canvas_resize(e: Any) -> None:
            canvas.itemconfig(canvas_window, width=e.width)
            
        canvas.bind("<Configure>", _on_canvas_resize)
        
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind("<MouseWheel>",
                    lambda e=None: canvas.yview_scroll(-1*(e.delta//120) if e else 0, "units"))

        self._form_body = body
        self._build_form_fields(body)

    def _build_form_fields(self, body: tk.Frame) -> None:
        pad = {"padx": 20, "pady": 6}

        # ── Mon hoc ──────────────────────────────────────────────────────────
        _section(body, "THONG TIN MON HOC")
        f_subject = tk.Frame(body, bg=_get_c("BG"))
        f_subject.pack(fill="x", **pad)
        tk.Label(f_subject, text="Ten mon / buoi day *", bg=_get_c("BG"),
                 fg=_get_c("TEXT"), font=F_BODY_B, anchor="w").pack(fill="x", pady=(0, 4))
        self._v_subject = tk.StringVar()
        tk.Entry(f_subject, textvariable=self._v_subject,
                 font=("Segoe UI", 11), relief="solid", bd=1).pack(fill="x", ipady=4)

        # ── Giang vien ───────────────────────────────────────────────────────
        f_lect = tk.Frame(body, bg=C_BG)
        f_lect.pack(fill="x", **pad)
        tk.Label(f_lect, text="Giang vien *", bg=C_BG,
                 fg=C_TEXT, font=F_BODY_B, anchor="w").pack(fill="x", pady=(0, 4))
        self._v_lecturer = tk.StringVar()
        # Prefill with current user if lecturer / admin
        if self.current_user:
            self._v_lecturer.set(self.current_user.full_name)
        lect_vals = self._lecturer_options()
        self._cb_lecturer = ttk.Combobox(
            f_lect, textvariable=self._v_lecturer,
            values=lect_vals, font=("Segoe UI", 10),
            state="readonly" if lect_vals else "normal",
        )
        self._cb_lecturer.pack(fill="x", ipady=2)

        # ── Phong hoc ────────────────────────────────────────────────────────
        f_room = tk.Frame(body, bg=C_BG)
        f_room.pack(fill="x", **pad)
        tk.Label(f_room, text="Phong hoc *", bg=C_BG,
                 fg=C_TEXT, font=F_BODY_B, anchor="w").pack(fill="x", pady=(0, 4))
        self._v_room = tk.StringVar()
        room_vals = [r.room_id for r in self.room_ctrl.list_rooms()]
        self._cb_room = ttk.Combobox(
            f_room, textvariable=self._v_room,
            values=room_vals, font=("Segoe UI", 10),
            state="readonly",
        )
        self._cb_room.pack(fill="x", ipady=2)

        # ── Cac thu trong tuan ───────────────────────────────────────────────
        _section(body, "NGAY TRONG TUAN (chon 1 hoac nhieu thu)")
        day_row = tk.Frame(body, bg=C_BG)
        day_row.pack(fill="x", padx=20, pady=(6, 4))
        self._day_vars: dict[int, tk.BooleanVar] = {}
        self._day_btns: dict[int, tk.Button] = {}
        for iso_wd, _ in WEEKDAYS:
            v = tk.BooleanVar(value=False)
            self._day_vars[iso_wd] = v
            short = SHORT_DAY[iso_wd]
            pill = tk.Button(
                day_row, text=short,
                bg="#f1f5f9", fg="#64748b",
                font=("Segoe UI", 9, "bold"),
                relief="flat", bd=0, width=4, pady=7,
                cursor="hand2",
                highlightthickness=1, highlightbackground="#e2e8f0",
            )
            pill.pack(side="left", padx=3)
            self._day_btns[iso_wd] = pill

            def _toggle(wd: int = iso_wd, p: tk.Button = pill, var: tk.BooleanVar = v) -> None:
                new_val = not var.get()
                var.set(new_val)
                p.config(
                    bg=C_PRIMARY if new_val else "#f1f5f9",
                    fg="white"   if new_val else "#64748b",
                    highlightbackground=C_PRIMARY if new_val else "#e2e8f0",
                )
                self._update_preview()

            pill.config(command=_toggle)
            pill.bind("<Enter>", lambda e, p=pill, var=v:
                      p.config(bg=C_PRIMARY if var.get() else "#e0e7ff"))
            pill.bind("<Leave>", lambda e, p=pill, var=v:
                      p.config(bg=C_PRIMARY if var.get() else "#f1f5f9"))

        # ── Khung gio ────────────────────────────────────────────────────────
        _section(body, "KHUNG GIO")
        f_slot = tk.Frame(body, bg=C_BG)
        f_slot.pack(fill="x", **pad)
        tk.Label(f_slot, text="Ca hoc (preset)", bg=C_BG,
                 fg=C_TEXT, font=F_BODY_B, anchor="w").pack(fill="x", pady=(0, 4))
        self._v_slot = tk.StringVar(value=SLOT_PRESETS[0][0])
        slot_names = [s[0] for s in SLOT_PRESETS]
        cb_slot = ttk.Combobox(
            f_slot, textvariable=self._v_slot,
            values=slot_names, font=("Segoe UI", 10),
            state="readonly",
        )
        cb_slot.pack(fill="x", ipady=2)
        cb_slot.bind("<<ComboboxSelected>>", self._on_slot_preset)

        f_time = tk.Frame(body, bg=C_BG)
        f_time.pack(fill="x", **pad)
        
        # Split time into two columns
        f_time.columnconfigure(0, weight=1)
        f_time.columnconfigure(1, weight=1)
        
        tk.Label(f_time, text="Gio bat dau *", bg=C_BG,
                 fg=C_TEXT, font=F_BODY_B, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._v_start_time = tk.StringVar(value="07:00")
        tk.Entry(f_time, textvariable=self._v_start_time,
                 font=("Segoe UI", 11), relief="solid", bd=1).grid(row=1, column=0, sticky="ew", padx=(0, 8), ipady=4)
                 
        tk.Label(f_time, text="Gio ket thuc *", bg=C_BG,
                 fg=C_TEXT, font=F_BODY_B, anchor="w").grid(row=0, column=1, sticky="w", pady=(0, 4))
        self._v_end_time = tk.StringVar(value="09:00")
        tk.Entry(f_time, textvariable=self._v_end_time,
                 font=("Segoe UI", 11), relief="solid", bd=1).grid(row=1, column=1, sticky="ew", ipady=4)

        # ── Khoang thoi gian ─────────────────────────────────────────────────
        _section(body, "KHOANG THOI GIAN HIEU LUC")
        f_date = tk.Frame(body, bg=C_BG)
        f_date.pack(fill="x", **pad)
        f_date.columnconfigure(0, weight=1)
        f_date.columnconfigure(1, weight=1)
        
        tk.Label(f_date, text="Ngay bat dau *", bg=C_BG,
                 fg=C_TEXT, font=F_BODY_B, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._de_start = DateEntry(
            f_date, font=("Segoe UI", 11), date_pattern="dd/mm/yyyy",
            background="#4f46e5", foreground="white")
        self._de_start.set_date(dt.date.today())
        self._de_start.grid(row=1, column=0, sticky="ew", padx=(0, 8), ipady=3)

        tk.Label(f_date, text="Ngay ket thuc *", bg=C_BG,
                 fg=C_TEXT, font=F_BODY_B, anchor="w").grid(row=0, column=1, sticky="w", pady=(0, 4))
        self._de_end = DateEntry(
            f_date, font=("Segoe UI", 11), date_pattern="dd/mm/yyyy",
            background="#4f46e5", foreground="white")
        self._de_end.set_date(dt.date.today() + dt.timedelta(weeks=16))
        self._de_end.grid(row=1, column=1, sticky="ew", ipady=3)

        # Preview info
        self._preview_lbl = tk.Label(
            body, text="", bg="#eef2ff", fg="#4f46e5",
            font=("Segoe UI", 9, "italic"),
            anchor="w", padx=16, pady=8, wraplength=300, justify="left",
        )
        self._preview_lbl.pack(fill="x", padx=20, pady=(12, 6))

        self._de_start.bind("<<DateEntrySelected>>", lambda _=None: self._update_preview())
        self._de_end.bind("<<DateEntrySelected>>", lambda _=None: self._update_preview())
        for dv in self._day_vars.values():
            dv.trace_add("write", lambda *_: self._update_preview())
        self._update_preview()

        # ── Submit button ─────────────────────────────────────────────────────
        btn_row = tk.Frame(body, bg=C_BG)
        btn_row.pack(fill="x", padx=20, pady=(10, 24))
        btn(btn_row, "  Tao lich  ", self._submit,
            variant="primary").pack(side="left", fill="x", expand=True, padx=(0, 6))
        btn(btn_row, "  Xoa form  ", self._clear_form,
            variant="secondary").pack(side="right", fill="x", expand=True, padx=(6, 0))

    # ── RIGHT: List of rules ──────────────────────────────────────────────────

    def _build_list(self, parent: tk.Frame) -> None:
        right = tk.Frame(parent, bg=C_BG,
                         highlightthickness=1, highlightbackground=C_BORDER)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)

        hdr = tk.Frame(right, bg=C_BG)
        hdr.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(hdr, text="Danh sach lich day da tao", bg=C_BG,
                 fg=C_TEXT, font=F_SECTION).pack(side="left")
        btn(hdr, "🔄 Lam moi", self._refresh_list,
            variant="secondary").pack(side="right")

        # Filter + search bar
        fbar = tk.Frame(right, bg=C_BG)
        fbar.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(fbar, text="Trang thai:", bg=C_BG, fg=C_MUTED,
                 font=F_SMALL).pack(side="left")
        self._v_filter = tk.StringVar(value="Tat ca")
        ttk.Combobox(
            fbar, textvariable=self._v_filter,
            values=["Tat ca", "Hoat dong", "Da xong", "Huy"],
            state="readonly", font=("Segoe UI", 9), width=12,
        ).pack(side="left", padx=(6, 0))
        self._v_filter.trace_add("write", lambda *_: self._refresh_list())
        tk.Label(fbar, text="  🔍", bg=C_BG, fg=C_MUTED,
                 font=F_SMALL).pack(side="left", padx=(16, 0))
        self._v_search = tk.StringVar()
        tk.Entry(fbar, textvariable=self._v_search,
                 font=("Segoe UI", 9), width=16,
                 relief="solid", bd=1).pack(side="left", padx=(4, 0), ipady=3)
        self._v_search.trace_add("write", lambda *_: self._refresh_list())

        # Treeview: rules
        cols = ("id", "subject", "days", "time", "date_range", "room", "count", "status")
        heads = ("Ma", "Mon hoc", "Thu trong tuan", "Khung gio",
                 "Khoang thoi gian", "Phong", "So buoi", "Trang thai")
        widths = (40, 150, 120, 100, 160, 60, 60, 80)

        tree_frame = tk.Frame(right, bg=C_BG)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 6))

        self._tree = ttk.Treeview(  # type: ignore
            tree_frame, columns=cols, show="headings",
            style="TV.Treeview", selectmode="browse",
        )
        for col, head, w in zip(cols, heads, widths):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=w, minwidth=50, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",  # type: ignore
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._tree.bind("<<TreeviewSelect>>", self._on_rule_select)
        self._tree.tag_configure("odd",  background="#f1f5f9")
        self._tree.tag_configure("even", background="#ffffff")

        # Action bar
        act = tk.Frame(right, bg=C_BG)
        act.pack(fill="x", padx=16, pady=(2, 8))
        btn(act, "📋 Xem cac buoi hoc", self._view_occurrences,
            variant="primary").pack(side="left")
        btn(act, "✏️ Doi trang thai", self._change_status,
            variant="secondary").pack(side="left", padx=(8, 0))
        btn(act, "🗑️ Xoa", self._delete_rule,
            variant="danger").pack(side="right")

        # Occurrence detail panel (hidden by default)
        self._occ_panel = tk.Frame(right, bg=C_BG,
                                   highlightthickness=1,
                                   highlightbackground=C_BORDER)
        # Not packed yet — shown on demand

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_slot_preset(self, _event: Any = None) -> None:
        val = self._v_slot.get()
        for name, st, et in SLOT_PRESETS:
            if val == name:
                if st:
                    self._v_start_time.set(st)
                    self._v_end_time.set(et)
                return

    @staticmethod
    def _parse_date_input(s: str) -> dt.date:
        """Parse DD/MM/YYYY → date. Raises ValueError on bad input."""
        return dt.datetime.strptime(s.strip(), "%d/%m/%Y").date()

    def _update_preview(self) -> None:
        try:
            d_start = self._de_start.get_date()
            d_end   = self._de_end.get_date()
        except Exception:
            self._preview_lbl.config(
                text="⚠  Ngay khong hop le.",
                bg="#fdf2f8", fg="#db2777")
            return

        selected_days = [d for d, v in self._day_vars.items() if v.get()]
        if not selected_days:
            self._preview_lbl.config(
                text="ℹ  Chon thu trong tuan de xem uoc tinh so buoi.",
                bg="#eef2ff", fg="#4f46e5")
            return

        # Count occurrences
        count = 0
        cur = d_start
        day_set = set(selected_days)
        while cur <= d_end:
            if cur.isoweekday() in day_set:
                count += 1
            cur += dt.timedelta(days=1)

        days_str = ", ".join(SHORT_DAY.get(d, str(d)) for d in sorted(selected_days))
        weeks = (d_end - d_start).days // 7 + 1
        self._preview_lbl.config(
            text=f"✅  Uoc tinh {count} buoi hoc trong ~{weeks} tuan "
                 f"({d_start.strftime('%d/%m/%Y')} – {d_end.strftime('%d/%m/%Y')})  "
                 f"│  Cac thu: {days_str}",
            bg=C_SUCCESS_BG, fg=C_SUCCESS,
        )

    def _submit(self) -> None:
        days = [d for d, v in self._day_vars.items() if v.get()]
        # Resolve lecturer id/name
        lect_text = self._v_lecturer.get().strip()
        lect_id = ""
        lect_name = lect_text
        if self.current_user:
            # Try to match by name from combobox
            try:
                all_users = self.user_ctrl.list_users()
                match = next(
                    (u for u in all_users if u.full_name == lect_text), None)
                if match:
                    lect_id = match.user_id
                    lect_name = match.full_name
                else:
                    lect_id = self.current_user.user_id
                    lect_name = lect_text or self.current_user.full_name
            except Exception:
                lect_id = getattr(self.current_user, "user_id", "")
                lect_name = lect_text

        # Read dates from DateEntry widgets (always valid ISO format)
        start_iso = self._de_start.get_date().isoformat()
        end_iso   = self._de_end.get_date().isoformat()

        payload = {
            "subject":      self._v_subject.get(),
            "days_of_week": days,
            "start_time":   self._v_start_time.get(),
            "end_time":     self._v_end_time.get(),
            "start_date":   start_iso,
            "end_date":     end_iso,
            "room_id":      self._v_room.get(),
            "lecturer_id":  lect_id or "unknown",
            "lecturer_name": lect_name,
        }

        try:
            rule = self.ctrl.create_rule(payload)
        except ValueError as exc:
            messagebox.showerror("Loi nhap lieu", str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror("Loi he thong", str(exc), parent=self)
            return

        n_occ = self.ctrl.count_occurrences(rule.rule_id)
        toast(self, f"✅ Da tao lich #{rule.rule_id} — {n_occ} buoi hoc duoc sinh ra!")
        self._clear_form()
        self._refresh_list()

    def _clear_form(self) -> None:
        self._v_subject.set("")
        for iso_wd, v in self._day_vars.items():
            v.set(False)
            if iso_wd in self._day_btns:
                self._day_btns[iso_wd].config(
                    bg="#f1f5f9", fg="#64748b",
                    highlightbackground="#e2e8f0",
                )
        self._v_slot.set(SLOT_PRESETS[0][0])
        self._v_start_time.set("07:00")
        self._v_end_time.set("09:00")
        self._de_start.set_date(dt.date.today())
        self._de_end.set_date(dt.date.today() + dt.timedelta(weeks=16))
        self._update_preview()

    def _refresh_list(self) -> None:
        filter_val  = self._v_filter.get()
        search_var  = getattr(self, "_v_search", None)
        search_term = search_var.get().strip().lower() if search_var else ""
        status_filter = "" if filter_val == "Tat ca" else filter_val
        rules = self.ctrl.list_rules(status=status_filter)
        rows = []
        for r in rules:
            subj = (r.subject or "").lower()
            rid  = (r.room_id or "").lower()
            if search_term and search_term not in subj and search_term not in rid:
                continue
            days_lbl = ", ".join(
                SHORT_DAY.get(d, str(d)) for d in sorted(r.days_of_week))
            time_lbl = f"{r.start_time} – {r.end_time}"
            date_lbl = (f"{r.start_date[8:]}/{r.start_date[5:7]}/{r.start_date[:4]}"
                        f" → {r.end_date[8:]}/{r.end_date[5:7]}/{r.end_date[:4]}")
            n = self.ctrl.count_occurrences(r.rule_id)
            rows.append((
                str(r.rule_id), r.subject, days_lbl, time_lbl, date_lbl, r.room_id, str(n), r.status
            ))

        fill_tree(self._tree, rows)
        # Color rows by status
        for item in self._tree.get_children():
            tags = list(self._tree.item(item, "tags"))
            if "empty" in tags:
                continue
            vals = self._tree.item(item, "values")
            status = vals[7] if len(vals) > 7 else ""
            tag = "odd" if self._tree.index(item) % 2 == 0 else "even"
            
            new_tags = [tag]
            if status == "Huy":
                self._tree.tag_configure("huy_row", background="#fdf2f8")
                new_tags.append("huy_row")
            elif status == "Da xong":
                self._tree.tag_configure("done_row", background="#e0e7ff")
                new_tags.append("done_row")
            
            self._tree.item(item, tags=tuple(new_tags))

    def _on_rule_select(self, _event: Any = None) -> None:
        sel = self._tree.selection()
        if sel:
            try:
                val0 = self._tree.item(sel[0], "values")[0]
                self._selected_rule_id = int(val0)
            except (ValueError, IndexError):
                self._selected_rule_id = None
        else:
            self._selected_rule_id = None

    def _view_occurrences(self) -> None:
        if self._selected_rule_id is None:
            messagebox.showinfo("Thong bao", "Hay chon mot lich de xem chi tiet.",
                                parent=self)
            return
        rule = self.ctrl.get_rule(self._selected_rule_id)
        if rule is None:
            messagebox.showerror("Loi", "Khong tim thay lich.", parent=self)
            return
        occurrences = self.ctrl.list_occurrences(self._selected_rule_id)
        _OccurrenceDialog(self, rule, occurrences, self.ctrl)

    def _change_status(self) -> None:
        if self._selected_rule_id is None:
            messagebox.showinfo("Thong bao", "Hay chon mot lich.",
                                parent=self)
            return
        rule = self.ctrl.get_rule(self._selected_rule_id)
        if rule is None:
            return
        _ChangeStatusDialog(self, rule, self.ctrl,
                            on_done=self._refresh_list)

    def _delete_rule(self) -> None:
        if self._selected_rule_id is None:
            messagebox.showinfo("Thong bao", "Hay chon mot lich de xoa.",
                                parent=self)
            return
        rule = self.ctrl.get_rule(self._selected_rule_id)
        if rule is None:
            return
        n = self.ctrl.count_occurrences(self._selected_rule_id)
        confirm = messagebox.askyesno(
            "Xac nhan xoa",
            f"Xoa lich '{rule.subject}'?\n"
            f"Se xoa toan bo {n} buoi hoc da sinh ra.\n"
            "Hanh dong nay khong the hoan tac.",
            parent=self,
        )
        if not confirm:
            return
        self.ctrl.delete_rule(self._selected_rule_id)
        self._selected_rule_id = None
        toast(self, "🗑️ Da xoa lich va toan bo cac buoi hoc.")
        self._refresh_list()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _lecturer_options(self) -> list[str]:
        try:
            users = self.user_ctrl.list_users()
            return [u.full_name for u in users
                    if getattr(u, "role", "") in ("Admin", "Giang vien")]
        except Exception:
            return []


# ═══════════════════════════════════════════════════════════════════════════════
#  Dialog: xem danh sach cac buoi hoc
# ═══════════════════════════════════════════════════════════════════════════════

class _OccurrenceDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, rule: Any,
                 occurrences: list, ctrl: Any) -> None:
        super().__init__(parent)
        self.ctrl = ctrl
        self.title(f"Cac buoi hoc — {rule.subject}")
        self.resizable(True, True)
        self.geometry("820x560")
        self.configure(bg=C_BG)
        self.transient(parent)
        self.grab_set()

        # Header
        hdr = tk.Frame(self, bg="#1e1b4b", padx=20, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text=f"🗓  {rule.subject}  —  {rule.room_id}",
                 bg="#1e1b4b", fg="#e0e7ff",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")

        days_str = "  ".join(
            SHORT_DAY.get(d, str(d)) for d in sorted(rule.days_of_week))
        tk.Label(hdr,
                 text=(f"Thu: {days_str}   │   "
                       f"{rule.start_time}–{rule.end_time}   │   "
                       f"{rule.start_date} → {rule.end_date}   │   "
                       f"{rule.lecturer_name}"),
                 bg="#1e1b4b", fg="#818cf8",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        # Stats bar
        n_total  = len(occurrences)
        n_done   = sum(1 for o in occurrences if o.status == "Da dien ra")
        n_cancel = sum(1 for o in occurrences if o.status == "Huy")
        n_plan   = n_total - n_done - n_cancel

        sbar = tk.Frame(self, bg="#f1f5f9", pady=6)
        sbar.pack(fill="x")
        for label, val, fg in [
            ("Tong so buoi:", n_total, "#1e293b"),
            ("Du kien:",      n_plan,  C_WARNING),
            ("Da dien ra:",   n_done,  C_SUCCESS),
            ("Huy:",          n_cancel, C_DANGER),
        ]:
            tk.Label(sbar, text=f"{label} {val}", bg="#f1f5f9", fg=fg,
                     font=F_BODY_B).pack(side="left", padx=16)

        # Completion progress bar
        if n_total > 0:
            pct = int(n_done * 100 / n_total)
            prog_f = tk.Frame(self, bg="#ffffff", padx=16)
            prog_f.pack(fill="x", pady=(4, 8))
            fill_color = C_SUCCESS if pct >= 80 else (C_WARNING if pct >= 40 else C_DANGER)
            tk.Label(prog_f,
                     text=f"Tien do hoan thanh: {pct}%  ({n_done}/{n_total} buoi)",
                     bg="#ffffff", fg=fill_color,
                     font=F_SMALL).pack(side="left")
            bar_bg = tk.Frame(prog_f, bg="#e2e8f0", height=7)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(12, 0))
            tk.Frame(bar_bg, bg=fill_color, height=7).place(
                x=0, y=0, relheight=1.0, relwidth=pct / 100)

        # Filter
        fbar = tk.Frame(self, bg=C_BG)
        fbar.pack(fill="x", padx=16, pady=(6, 2))
        tk.Label(fbar, text="Loc:", bg=C_BG, fg=C_MUTED,
                 font=F_SMALL).pack(side="left")
        self._v_occ_filter = tk.StringVar(value="Tat ca")
        ttk.Combobox(
            fbar, textvariable=self._v_occ_filter,
            values=["Tat ca", "Du kien", "Da dien ra", "Huy"],
            state="readonly", font=("Segoe UI", 9), width=14,
        ).pack(side="left", padx=(6, 0))
        self._v_occ_filter.trace_add(
            "write", lambda *_: self._fill(occurrences))

        # Treeview
        cols = ("occ_id", "date", "weekday", "time", "room", "status")
        heads = ("#", "Ngay", "Thu", "Khung gio", "Phong", "Trang thai")
        widths = (40, 110, 80, 120, 70, 100)

        tf = tk.Frame(self, bg=C_BG)
        tf.pack(fill="both", expand=True, padx=16, pady=4)

        self._tree = ttk.Treeview(  # type: ignore
            tf, columns=cols, show="headings",
            style="TV.Treeview", selectmode="browse",
        )
        for col, head, w in zip(cols, heads, widths):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(tf, orient="vertical",  # type: ignore
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._all_occs = occurrences
        self._fill(occurrences)

        # Action row
        act = tk.Frame(self, bg=C_BG)
        act.pack(fill="x", padx=16, pady=(4, 12))
        btn(act, "✏️ Doi trang thai buoi", self._change_occ_status,
            variant="secondary").pack(side="left")
        btn(act, "Dong", self.destroy, variant="primary").pack(side="right")

    def _fill(self, occurrences: list) -> None:
        fval = self._v_occ_filter.get()
        for item in self._tree.get_children():
            self._tree.delete(item)
        WD_VN = {1: "Thu 2", 2: "Thu 3", 3: "Thu 4",
                 4: "Thu 5", 5: "Thu 6", 6: "Thu 7", 7: "CN"}
        for idx, o in enumerate(occurrences):
            if fval != "Tat ca" and o.status != fval:
                continue
            d = o.occurrence_date
            date_disp = f"{d[8:]}/{d[5:7]}/{d[:4]}"
            wd_disp = WD_VN.get(o.day_of_week, str(o.day_of_week))
            time_disp = f"{o.start_time} – {o.end_time}"
            tag = "odd" if idx % 2 == 0 else "even"
            self._tree.insert(
                "", "end", iid=str(o.occ_id),
                values=(o.occ_id, date_disp, wd_disp,
                        time_disp, o.room_id, o.status),
                tags=(tag,),
            )
        self._tree.tag_configure("odd",  background="#f1f5f9")
        self._tree.tag_configure("even", background="#ffffff")

    def _change_occ_status(self) -> None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Thong bao", "Hay chon mot buoi hoc.",
                                parent=self)
            return
        occ_id = int(sel[0])
        new_status = _ask_occ_status(self)
        if not new_status:
            return
        try:
            self.ctrl.update_occurrence_status(occ_id, new_status)
        except ValueError as exc:
            messagebox.showerror("Loi", str(exc), parent=self)
            return
        # Refresh
        for o in self._all_occs:
            if o.occ_id == occ_id:
                o.status = new_status
        self._fill(self._all_occs)


def _ask_occ_status(parent: tk.Widget) -> str | None:
    dlg = tk.Toplevel(parent)
    dlg.title("Chon trang thai")
    dlg.configure(bg=C_BG)
    dlg.resizable(False, False)
    dlg.transient(parent)
    dlg.grab_set()
    result: list[str] = []

    tk.Label(dlg, text="Chon trang thai moi cho buoi hoc:",
             bg=C_BG, fg=C_TEXT, font=F_BODY,
             padx=20, pady=12).pack()

    v = tk.StringVar(value="Da dien ra")
    for s in ("Du kien", "Da dien ra", "Huy"):
        tk.Radiobutton(dlg, text=s, variable=v, value=s,
                       bg=C_BG, fg=C_TEXT, font=F_BODY,
                       selectcolor=C_SURFACE, activebackground=C_BG,
                       cursor="hand2").pack(anchor="w", padx=30)

    def _ok():
        result.append(v.get())
        dlg.destroy()

    btn_r = tk.Frame(dlg, bg=C_BG)
    btn_r.pack(pady=(10, 14), padx=20, fill="x")
    btn(btn_r, "Xac nhan", _ok, variant="primary").pack(side="left")
    btn(btn_r, "Huy bo", dlg.destroy, variant="secondary").pack(side="left", padx=(8, 0))

    dlg.wait_window()
    return result[0] if result else None


# ═══════════════════════════════════════════════════════════════════════════════
#  Dialog: change rule status
# ═══════════════════════════════════════════════════════════════════════════════

class _ChangeStatusDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, rule: Any,
                 ctrl: Any, on_done) -> None:
        super().__init__(parent)
        self.title("Doi trang thai lich")
        self.configure(bg=C_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.ctrl = ctrl
        self.rule = rule
        self._on_done = on_done

        tk.Label(self,
                 text=f"Lich: {rule.subject}  (hien tai: {rule.status})",
                 bg=C_BG, fg=C_TEXT, font=F_BODY_B,
                 padx=20, pady=12).pack()

        self._v = tk.StringVar(value=rule.status)
        for s in ("Hoat dong", "Da xong", "Huy"):
            tk.Radiobutton(self, text=s, variable=self._v, value=s,
                           bg=C_BG, fg=C_TEXT, font=F_BODY,
                           selectcolor=C_SURFACE, activebackground=C_BG,
                           cursor="hand2").pack(anchor="w", padx=30)

        btn_r = tk.Frame(self, bg=C_BG)
        btn_r.pack(pady=(10, 14), padx=20, fill="x")
        btn(btn_r, "Luu", self._save, variant="primary").pack(side="left")
        btn(btn_r, "Huy", self.destroy, variant="secondary").pack(
            side="left", padx=(8, 0))

    def _save(self) -> None:
        try:
            self.ctrl.update_rule_status(self.rule.rule_id, self._v.get())
        except ValueError as exc:
            messagebox.showerror("Loi", str(exc), parent=self)
            return
        self.destroy()
        self._on_done()
