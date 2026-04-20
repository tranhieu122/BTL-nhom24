# equipment_gui.py  –  equipment management screen  (v2.0 - full CRUD)
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from gui.theme import (C_BG, C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED,
                       F_INPUT, make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box)


class EquipmentDialog(tk.Toplevel):
    """Add / Edit equipment dialog."""

    def __init__(self, master, room_controller, equipment=None) -> None:
        super().__init__(master)
        self.room_ctrl = room_controller
        self.result = None
        self.title("Them thiet bi" if equipment is None else "Sua thiet bi")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)
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
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=22, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔧  Thong tin thiet bi",
                 bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")

        frm = tk.Frame(self, bg=C_SURFACE, padx=26, pady=18)
        frm.pack()

        fields = [
            ("equipment_id",   "Ma thiet bi *",         False),
            ("name",           "Ten thiet bi *",         False),
            ("equipment_type", "Loai thiet bi *",        False),
            ("purchase_date",  "Ngay mua (YYYY-MM-DD) *", False),
        ]
        for i, (key, lbl, _) in enumerate(fields):
            tk.Label(frm, text=lbl, bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9, "bold")).grid(
                row=i * 2, column=0, columnspan=2,
                sticky="w", pady=(10 if i else 0, 2))
            tk.Entry(frm, textvariable=self.vars[key], width=36,
                     font=F_INPUT, relief="solid", bd=1).grid(
                row=i * 2 + 1, column=0, columnspan=2, sticky="ew")

        # Room combobox
        tk.Label(frm, text="Phong *", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(10, 2))
        room_ids = [r.room_id for r in self.room_ctrl.list_rooms()]
        ttk.Combobox(frm, textvariable=self.vars["room_id"],
                     values=room_ids, state="readonly", width=33).grid(
            row=9, column=0, columnspan=2, sticky="ew")

        # Status combobox
        tk.Label(frm, text="Trang thai", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).grid(
            row=10, column=0, columnspan=2, sticky="w", pady=(10, 2))
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Bao tri", "Hong"],
                     state="readonly", width=33).grid(
            row=11, column=0, columnspan=2, sticky="ew")

        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.grid(row=12, column=0, columnspan=2,
                     sticky="e", pady=(20, 0))
        btn(btn_row, "Luu lai", self._save, icon="💾").pack(side="left", padx=6)
        btn(btn_row, "Huy",     self.destroy, variant="ghost").pack(side="left")

    def _save(self) -> None:
        v = {k: var.get().strip() for k, var in self.vars.items()}
        if not all([v["equipment_id"], v["name"], v["equipment_type"],
                    v["room_id"], v["purchase_date"]]):
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long dien day du cac truong bat buoc (*).",
                                   parent=self)
            return
        self.result = v
        self.destroy()


class EquipmentManagementFrame(tk.Frame):
    def __init__(self, master, equipment_controller, room_controller) -> None:
        super().__init__(master, bg=C_BG)
        self.equip_ctrl = equipment_controller
        self.room_ctrl  = room_controller
        self.room_var    = tk.StringVar()
        self.search_var  = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Quan ly thiet bi", "🔧").pack(fill="x")

        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Search box
        search_box(toolbar, self.search_var).pack(side="left")
        btn(toolbar, "Tim kiem", self.refresh,
            variant="ghost", icon="🔍").pack(side="left", padx=(4, 0))

        # Room filter
        tk.Label(toolbar, text="  |  Phong:", bg=C_BG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(8, 4))
        room_values = ["Tat ca"] + [r.room_id for r in self.room_ctrl.list_rooms()]
        self.room_var.set("Tat ca")
        self.room_cb = ttk.Combobox(toolbar, textvariable=self.room_var,
                                    values=room_values, state="readonly", width=14)
        self.room_cb.pack(side="left")
        self.room_cb.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        # CRUD buttons
        btn(toolbar, "Them",  self._add,
            variant="success", icon="+").pack(side="left", padx=(12, 4))
        btn(toolbar, "Sua",   self._edit,
            variant="outline", icon="✏️").pack(side="left", padx=4)
        btn(toolbar, "Xoa",   self._delete,
            variant="danger",  icon="🗑").pack(side="left", padx=4)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "ten", "loai", "phong", "trang_thai", "ngay_mua")
        hdrs = ("Ma TB", "Ten thiet bi", "Loai", "Phong", "Trang thai", "Ngay mua")
        wids = (90, 220, 140, 90, 120, 120)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # Status bar
        self._status_lbl = tk.Label(self, text="", bg=C_BG, fg="#64748b",
                                    font=("Segoe UI", 9))
        self._status_lbl.pack(anchor="w", padx=22, pady=(0, 6))

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
        fill_tree(self.tree, rows)
        self._status_lbl.config(text=f"Hien thi {len(rows)} thiet bi")

    def _selected_id(self) -> str | None:
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _add(self) -> None:
        dlg = EquipmentDialog(self, self.room_ctrl)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.equip_ctrl.save_equipment(dlg.result)
        except ValueError as e:
            messagebox.showerror("Loi", str(e))
            return
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
        except ValueError as e:
            messagebox.showerror("Loi", str(e))
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
