# user_gui.py  –  user management screen
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from gui.theme import (C_BG, C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED,
                       F_INPUT, make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box)


class UserDialog(tk.Toplevel):
    def __init__(self, master, user=None) -> None:
        super().__init__(master)
        self.title("Thong tin nguoi dung")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.result = None
        self.vars = {
            "user_id":   tk.StringVar(value=getattr(user, "user_id",   "")),
            "username":  tk.StringVar(value=getattr(user, "username",  "")),
            "full_name": tk.StringVar(value=getattr(user, "full_name", "")),
            "role":      tk.StringVar(value=getattr(user, "role",      "Giang vien")),
            "email":     tk.StringVar(value=getattr(user, "email",     "")),
            "phone":     tk.StringVar(value=getattr(user, "phone",     "")),
            "password":  tk.StringVar(),
            "status":    tk.StringVar(value=getattr(user, "status",    "Hoat dong")),
        }
        self._build()
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

        text_fields = [("user_id",   "Ma nguoi dung"),
                       ("username",  "Ten dang nhap"),
                       ("full_name", "Ho va ten"),
                       ("email",     "Email"),
                       ("phone",     "So dien thoai"),
                       ("password",  "Mat khau moi (bo trong neu khong doi)")]
        for i, (key, lbl) in enumerate(text_fields):
            tk.Label(frm, text=lbl, bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9, "bold")).grid(
                row=i * 2, column=0, columnspan=2,
                sticky="w", pady=(10 if i else 0, 2))
            show = "*" if key == "password" else ""
            tk.Entry(frm, textvariable=self.vars[key], width=36,
                     font=F_INPUT, show=show, relief="solid", bd=1).grid(
                row=i * 2 + 1, column=0, columnspan=2, sticky="ew")

        tk.Label(frm, text="Vai tro", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).grid(
            row=12, column=0, columnspan=2, sticky="w", pady=(10, 2))
        ttk.Combobox(frm, textvariable=self.vars["role"],
                     values=["Admin", "Giang vien", "Sinh vien"],
                     state="readonly", width=33).grid(
            row=13, column=0, columnspan=2, sticky="ew")

        tk.Label(frm, text="Trang thai", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).grid(
            row=14, column=0, columnspan=2, sticky="w", pady=(10, 2))
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Khoa"],
                     state="readonly", width=33).grid(
            row=15, column=0, columnspan=2, sticky="ew")

        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.grid(row=16, column=0, columnspan=2, sticky="e", pady=(20, 0))
        btn(btn_row, "Luu lai", self._save,
            icon="💾").pack(side="left", padx=6)
        btn(btn_row, "Huy", self.destroy,
            variant="ghost").pack(side="left")

    def _save(self) -> None:
        self.result = {k: v.get().strip() for k, v in self.vars.items()}
        self.destroy()


class UserManagementFrame(tk.Frame):
    def __init__(self, master, user_controller) -> None:
        super().__init__(master, bg=C_BG)
        self.user_ctrl  = user_controller
        self.search_var = tk.StringVar()
        self.tree: ttk.Treeview | None = None
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
        rows = [(u.user_id, u.username, u.full_name,
                 u.role, u.email, u.phone, u.status)
                for u in self.user_ctrl.list_users(self.search_var.get())]
        fill_tree(self.tree, rows)

    def _selected_user_id(self) -> str | None:
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _get_user(self):
        uid = self._selected_user_id()
        if uid is None:
            return None
        return next((u for u in self.user_ctrl.list_users()
                     if u.user_id == uid), None)

    def _add(self) -> None:
        dlg = UserDialog(self)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.user_ctrl.save_user(dlg.result)
        except ValueError as err:
            messagebox.showerror("Du lieu khong hop le", str(err))
            return
        self.refresh()

    def _edit(self) -> None:
        user = self._get_user()
        if user is None:
            messagebox.showwarning("Chua chon", "Hay chon nguoi dung de sua.")
            return
        dlg = UserDialog(self, user=user)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.user_ctrl.save_user(dlg.result)
        except ValueError as err:
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
        self.user_ctrl.delete_user(uid)
        self.refresh()
