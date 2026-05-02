# user_gui.py  –  user management screen
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from gui.theme import (C_BG, C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box,
                       labeled_entry, eye_toggle)


class UserDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, user: Optional['User'] = None) -> None: # type: ignore
        super().__init__(master)
        self.title("Thong tin nguoi dung")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.result = None
        self.vars = {
            "user_id":   tk.StringVar(value=user.user_id if user else ""), # type: ignore
            "username":  tk.StringVar(value=user.username if user else ""), # type: ignore
            "full_name": tk.StringVar(value=user.full_name if user else ""), # type: ignore
            "role":      tk.StringVar(value=user.role if user else "Giang vien"), # type: ignore
            "email":     tk.StringVar(value=user.email if user else ""), # type: ignore
            "phone":     tk.StringVar(value=user.phone if user else ""), # type: ignore
            "password":  tk.StringVar(),
            "status":    tk.StringVar(value=user.status if user else "Hoat dong"), # type: ignore
        }
        self._build()
        # For static checkers, cast master to tk.Tk for transient
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            self.transient(master)
        self.grab_set()

    def _build(self) -> None:
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="👤  Thong tin nguoi dung",
                 bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")

        frm = tk.Frame(self, bg=C_SURFACE, padx=24, pady=20)
        frm.pack()

        # --- styled labeled entries ---
        icons = {"user_id": "🔑", "username": "👤", "full_name": "📛",
                 "email": "📧", "phone": "📱", "password": "🔒"}
        labels = {"user_id": "MA NGUOI DUNG", "username": "TEN DANG NHAP",
                  "full_name": "HO VA TEN", "email": "EMAIL",
                  "phone": "SO DIEN THOAI",
                  "password": "MAT KHAU MOI (BO TRONG NEU KHONG DOI)"}
        r = 0
        for key in ("user_id", "username", "full_name", "email", "phone", "password"):
            show = "*" if key == "password" else ""
            outer, entry = labeled_entry(
                frm, labels[key], self.vars[key],
                icon=icons[key], show=show, width=32)
            outer.grid(row=r, column=0, columnspan=2, sticky="ew",
                       pady=(6, 0))
            if key == "password":
                eye_toggle(entry.master, entry, bg=C_SURFACE).pack(
                    side="right", padx=(0, 6))
            r += 1

        tk.Label(frm, text="VAI TRO", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))
        r += 1
        ttk.Combobox(frm, textvariable=self.vars["role"],
                     values=["Admin", "Giang vien", "Sinh vien"],
                     state="readonly", width=33).grid(
            row=r, column=0, columnspan=2, sticky="ew")
        r += 1

        tk.Label(frm, text="TRANG THAI", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))
        r += 1
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Khoa"],
                     state="readonly", width=33).grid(
            row=r, column=0, columnspan=2, sticky="ew")
        r += 1

        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.grid(row=r, column=0, columnspan=2, sticky="e", pady=(20, 0))
        btn(btn_row, "Luu lai", self._save,
            icon="💾").pack(side="left", padx=6)
        btn(btn_row, "Huy", self.destroy,
            variant="ghost").pack(side="left")

    def _save(self) -> None:
        self.result = {k: v.get().strip() for k, v in self.vars.items()}
        self.destroy()


class UserManagementFrame(tk.Frame):
    def __init__(self, master: tk.Misc, user_controller: 'UserController') -> None: # type: ignore
        super().__init__(master, bg=C_BG)
        self.user_ctrl: 'user_controller' = user_controller # type: ignore
        self.search_var = tk.StringVar()
        self.tree: Optional[ttk.Treeview] = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Quan ly nguoi dung", "👥").pack(fill="x")

        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        search_box(toolbar, self.search_var).pack(side="left")
        btn(toolbar, "Tim kiem", self.refresh,
            variant="ghost",   icon="🔍").pack(side="left", padx=(6, 0))
        btn(toolbar, "Them",  self._add,
            variant="success", icon="+").pack(side="left", padx=6)
        btn(toolbar, "Sua",   self._edit,
            variant="outline", icon="✏️").pack(side="left", padx=4)
        btn(toolbar, "Xoa",   self._delete,
            variant="danger",  icon="🗑").pack(side="left", padx=4)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "username", "ten", "vai_tro", "email", "phone", "trang_thai")
        hdrs = ("Ma", "Username", "Ho ten", "Vai tro", "Email", "SDT", "Trang thai")
        wids = (80, 110, 160, 110, 180, 120, 110)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

    def refresh(self) -> None:
        users = self.user_ctrl.list_users(self.search_var.get()) # type: ignore
        rows = [(u.user_id, u.username, u.full_name, u.role, u.email, u.phone, u.status) for u in users] # type: ignore
        if self.tree is not None:
            fill_tree(self.tree, rows) # type: ignore

    def _selected_user_id(self) -> Optional[str]:
        if self.tree is None:
            return None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _get_user(self) -> Optional['User']: # type: ignore
        uid = self._selected_user_id()
        if uid is None:
            return None
        for u in self.user_ctrl.list_users(): # type: ignore
            if u.user_id == uid: # type: ignore
                return u # type: ignore
        return None

    def _add(self) -> None:
        dlg = UserDialog(self)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.user_ctrl.save_user(dlg.result) # type: ignore
        except Exception as err:
            messagebox.showerror("Du lieu khong hop le", str(err))
            return
        self.refresh()

    def _edit(self) -> None:
        user = self._get_user() # type: ignore
        if user is None:
            messagebox.showwarning("Chua chon", "Hay chon nguoi dung de sua.")
            return
        dlg = UserDialog(self, user=user) # type: ignore
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.user_ctrl.save_user(dlg.result) # type: ignore
        except Exception as err:
            messagebox.showerror("Du lieu khong hop le", str(err))
            return
        self.refresh()

    def _delete(self) -> None:
        uid = self._selected_user_id()
        if uid is None:
            messagebox.showwarning("Chua chon", "Hay chon nguoi dung de xoa.")
            return
        if not messagebox.askyesno("Xac nhan xoa", f"Xoa nguoi dung {uid}?"):
            return
        try:
            self.user_ctrl.delete_user(uid) # type: ignore
        except Exception as err:
            messagebox.showerror("Loi xoa", str(err))
            return
        self.refresh()
