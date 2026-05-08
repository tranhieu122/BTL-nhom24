# equipment_gui.py  –  equipment management screen  (v2.0 - full CRUD)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any
from tkcalendar import DateEntry  # type: ignore[import-untyped]
from gui.theme import (
    _get_c, C_BG, C_MUTED, C_TEXT, C_SURFACE, C_BORDER,
    make_tree, fill_tree, with_scrollbar,
    page_header, btn, search_box, labeled_entry
)


class EquipmentDialog(tk.Toplevel):
    """Add / Edit equipment dialog."""

    def __init__(self, master: tk.Misc, room_controller: Any,
                 equipment: Any = None) -> None:
        super().__init__(master)  # type: ignore[arg-type]
        self.room_ctrl = room_controller
        self.result = None
        self.title("Them thiet bi" if equipment is None else "Sua thiet bi")
        self.resizable(False, False)
        self.configure(bg=_get_c("SURFACE"))
        self.transient(master)  # type: ignore[arg-type]
        self.grab_set()

        self.vars = {
            "equipment_id":   tk.StringVar(value=getattr(equipment, "equipment_id",   "")),
            "name":           tk.StringVar(value=getattr(equipment, "name",           "")),
            "equipment_type": tk.StringVar(value=getattr(equipment, "equipment_type", "")),
            "room_id":        tk.StringVar(value=getattr(equipment, "room_id",        "")),
            "status":         tk.StringVar(value=getattr(equipment, "status",         "Hoat dong")),
            "purchase_date":  tk.StringVar(value=getattr(equipment, "purchase_date",  "")),
        }
        self._build()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # Header
        hdr = tk.Frame(self, bg=_get_c("SB_BG"))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=_get_c("INDIGO_500"), height=3).pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg=_get_c("SB_BG"), padx=22, pady=14)
        hdr_inner.pack(fill="x")
        icon_lbl = tk.Label(hdr_inner,
                            text="✏️" if "Sua" in self.title() else "🔧",
                            bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"), font=("Segoe UI", 18))
        icon_lbl.pack(side="left", padx=(0, 12))
        title_f = tk.Frame(hdr_inner, bg=_get_c("SB_BG"))
        title_f.pack(side="left")
        tk.Label(title_f, text=self.title(),
                 bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_f,
                 text="Cap nhat thong tin thiet bi" if "Sua" in self.title()
                       else "Dien day du thong tin thiet bi moi (*)",
                 bg=_get_c("SB_BG"), fg=_get_c("INDIGO_400"),
                 font=("Segoe UI", 9)).pack(anchor="w")

        frm = tk.Frame(self, bg=_get_c("SURFACE"), padx=26, pady=18)
        frm.pack()

        icons = {"equipment_id": "🔑", "name": "🔧",
                 "equipment_type": "📦"}
        labels_map = {"equipment_id": "MA THIET BI *", "name": "TEN THIET BI *",
                      "equipment_type": "LOAI THIET BI *"}
        r = 0
        for key in ("equipment_id", "name", "equipment_type"):
            wrapper = tk.Frame(frm, bg=_get_c("SURFACE"))
            wrapper.grid(row=r, column=0, columnspan=2, sticky="ew", pady=(0, 6))
            labeled_entry(
                wrapper, labels_map[key], self.vars[key],
                icon=icons[key], width=32)
            r += 1

        # Date picker for purchase_date
        tk.Label(frm, text="NGAY MUA *", bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 8, "bold")).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))
        r += 1
        _init_date = self.vars["purchase_date"].get()
        try:
            _dt_val = dt.date.fromisoformat(_init_date) if _init_date else dt.date.today()
        except ValueError:
            _dt_val = dt.date.today()
        self._date_entry = DateEntry(
            frm, font=("Segoe UI", 10), date_pattern="yyyy-mm-dd",
            background="#4f46e5", foreground="white", width=32)
        self._date_entry.set_date(_dt_val) # type: ignore
        self._date_entry.grid(row=r, column=0, columnspan=2, sticky="ew", ipady=4) # type: ignore
        r += 1

        # Room combobox
        tk.Label(frm, text="PHONG *", bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 8, "bold")).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))
        r += 1
        room_ids = [r2.room_id for r2 in self.room_ctrl.list_rooms()]
        ttk.Combobox(frm, textvariable=self.vars["room_id"],
                     values=room_ids, state="readonly", width=33).grid(
            row=r, column=0, columnspan=2, sticky="ew")
        r += 1

        # Status combobox
        tk.Label(frm, text="TRANG THAI", bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 8, "bold")).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))
        r += 1
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Bao tri", "Hong"],
                     state="readonly", width=33).grid(
            row=r, column=0, columnspan=2, sticky="ew")
        r += 1

        btn_row = tk.Frame(frm, bg=_get_c("SURFACE"))
        btn_row.grid(row=r, column=0, columnspan=2,
                     sticky="e", pady=(20, 0))
        btn(btn_row, "Luu lai", self._save, icon="💾").pack(side="left", padx=6)
        btn(btn_row, "Huy",     self.destroy, variant="ghost").pack(side="left")

    def _save(self) -> None:
        v = {k: var.get().strip() for k, var in self.vars.items()}
        # Read purchase_date from DateEntry widget
        v["purchase_date"] = self._date_entry.get_date().isoformat() # type: ignore
        if not all([v["equipment_id"], v["name"], v["equipment_type"],
                    v["room_id"], v["purchase_date"]]): # type: ignore
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long dien day du cac truong bat buoc (*).",
                                   parent=self)
            return
        self.result = v
        self.destroy()


class EquipmentManagementFrame(tk.Frame):
    def __init__(self, master: tk.Misc, equipment_controller: Any,
                 room_controller: Any) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.equip_ctrl = equipment_controller
        self.room_ctrl  = room_controller
        self.room_var    = tk.StringVar()
        self.search_var  = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._stat_labels: dict[str, tk.Label] = {}
        self._search_timer: str | None = None
        self.search_var.trace_add("write", lambda *_: self._on_search_change())
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Quan ly thiet bi", "🔧").pack(fill="x")

        # ── Stat summary bar ─────────────────────────────────────────────────
        stats_outer = tk.Frame(self, bg=C_BG)
        stats_outer.pack(fill="x", padx=20, pady=(0, 12))

        stat_defs = [
            ("total",    "🔧", "Tong thiet bi",  "#eef2ff", "#4f46e5"),
            ("active",   "✅", "Hoat dong",       "#dcfce7", "#15803d"),
            ("maintain", "⚙️", "Bao tri",         "#fef3c7", "#b45309"),
            ("broken",   "❌", "Hong",            "#fdf2f8", "#db2777"),
            ("rooms",    "🏫", "Phong co TB",     "#f0f9ff", "#0369a1"),
        ]
        for key, icon, label, bg, fg in stat_defs:
            chip = tk.Frame(stats_outer, bg=bg, highlightthickness=1,
                            highlightbackground="#e2e8f0", padx=16, pady=10)
            chip.pack(side="left", padx=(0, 8))
            top_f = tk.Frame(chip, bg=bg)
            top_f.pack(anchor="w")
            tk.Label(top_f, text=icon, bg=bg,
                     font=("Segoe UI", 16)).pack(side="left", padx=(0, 6))
            val_lbl = tk.Label(top_f, text="–", bg=bg, fg=fg,
                               font=("Segoe UI", 20, "bold"))
            val_lbl.pack(side="left")
            tk.Label(chip, text=label, bg=bg, fg="#64748b",
                     font=("Segoe UI", 9)).pack(anchor="w")
            self._stat_labels[key] = val_lbl

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=_get_c("BG"))
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Search box
        search_box(toolbar, self.search_var).pack(side="left")

        # Room filter
        tk.Label(toolbar, text="  |  Phong:", bg=C_BG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(8, 4))
        room_values = ["Tat ca"] + [r.room_id for r in self.room_ctrl.list_rooms()]
        self.room_var.set("Tat ca")
        self.room_cb = ttk.Combobox(toolbar, textvariable=self.room_var,
                                    values=room_values, state="readonly", width=14)
        self.room_cb.pack(side="left")
        self.room_cb.bind("<<ComboboxSelected>>", lambda _=None: self.refresh())

        # CRUD buttons
        btn(toolbar, "Them",  self._add,
            variant="success", icon="+").pack(side="left", padx=(12, 4))
        btn(toolbar, "Sua",   self._edit,
            variant="outline", icon="✏️").pack(side="left", padx=4)
        btn(toolbar, "Xoa",   self._delete,
            variant="danger",  icon="🗑").pack(side="left", padx=4)

        # Status bar
        self._status_lbl = tk.Label(toolbar, text="", bg=C_BG, fg=C_MUTED,
                                    font=("Segoe UI", 9))
        self._status_lbl.pack(side="right", padx=8)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "ten", "loai", "phong", "trang_thai", "ngay_mua")
        hdrs = ("Ma TB", "Ten thiet bi", "Loai", "Phong", "Trang thai", "Ngay mua")
        wids = (90, 220, 140, 90, 120, 120)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

    def _on_search_change(self) -> None:
        """Debounced search: wait 300ms after last keystroke before refreshing."""
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(300, self.refresh)

    def refresh(self) -> None:
        selected = self.room_var.get().strip()
        room_filter = "" if selected in ("Tat ca", "") else selected
        q = self.search_var.get().strip().lower()
        all_eq = self.equip_ctrl.list_equipment(room_filter)
        if q:
            all_eq = [e for e in all_eq
                      if q in e.name.lower() or q in e.equipment_id.lower()
                      or q in e.equipment_type.lower()]
        rows = [(e.equipment_id, e.name, e.equipment_type,
                 e.room_id, e.status, e.purchase_date)
                for e in all_eq]
        assert self.tree is not None
        fill_tree(self.tree, rows)  # type: ignore[arg-type]

        # Update stat chips (with animation)
        from gui.theme import animate_count
        all_eq_full = self.equip_ctrl.list_equipment("")
        total    = len(all_eq_full)
        active   = sum(1 for e in all_eq_full if e.status == "Hoat dong")
        maintain = sum(1 for e in all_eq_full if e.status == "Bao tri")
        broken   = sum(1 for e in all_eq_full if e.status == "Hong")
        rooms_with = len({e.room_id for e in all_eq_full if e.room_id})
        for key, val in (("total", total), ("active", active),
                         ("maintain", maintain), ("broken", broken),
                         ("rooms", rooms_with)):
            if key in self._stat_labels:
                animate_count(self._stat_labels[key], val)

        shown = len(rows)
        self._status_lbl.config(
            text=f"Hien thi {shown}/{total} thiet bi"
            if shown < total else f"Tong: {total} thiet bi")

    def _selected_id(self) -> str | None:
        assert self.tree is not None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _add(self) -> None:
        dlg = EquipmentDialog(self, self.room_ctrl)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.equip_ctrl.save_equipment(dlg.result)
        except Exception as e:
            messagebox.showerror("Loi khi luu thiet bi", str(e))
            return
        # Reset filter to show all so the newly added item is visible
        self.room_var.set("Tat ca")
        self.refresh()
        messagebox.showinfo("Thanh cong",
                            f"Da them thiet bi '{dlg.result['name']}'.")

    def _edit(self) -> None:
        eid = self._selected_id()
        if eid is None:
            messagebox.showwarning("Chua chon", "Hay chon thiet bi can sua.")
            return
        # Find the equipment object
        all_eq = self.equip_ctrl.list_equipment()
        equip  = next((e for e in all_eq if e.equipment_id == eid), None)
        dlg = EquipmentDialog(self, self.room_ctrl, equipment=equip)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.equip_ctrl.save_equipment(dlg.result)
        except Exception as e:
            messagebox.showerror("Loi khi cap nhat thiet bi", str(e))
            return
        self.refresh()

    def _delete(self) -> None:
        eid = self._selected_id()
        if eid is None:
            messagebox.showwarning("Chua chon", "Hay chon thiet bi can xoa.")
            return
        if not messagebox.askyesno("Xac nhan xoa",
                                   f"Xoa thiet bi '{eid}'?"):
            return
        self.equip_ctrl.delete_equipment(eid)
        self.refresh()
