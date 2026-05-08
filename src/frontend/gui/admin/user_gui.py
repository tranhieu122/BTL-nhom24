# user_gui.py  –  user management screen
from __future__ import annotations
import re
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Any
from gui.theme import (_get_c, FONT_BODY, FONT_BODY_BOLD,
                       GlassCard, GlowButton, PillBadge, make_tree,
                       fill_tree, with_scrollbar, search_box)


class UserDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, user: Any = None) -> None: # type: ignore
        super().__init__(master)
        self._is_edit = user is not None
        self.title("Chinh sua nguoi dung" if self._is_edit else "Them nguoi dung moi")
        self.resizable(False, False)
        self.configure(bg=_get_c("BG"))
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
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            self.transient(master)
        self.grab_set()
        self.after(80, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        self.geometry(f"+{pw - self.winfo_width()//2}+{ph - self.winfo_height()//2}")

    def _build(self) -> None:
        # ── Dialog shell ───────────────────────────────────────────────────────
        dialog_card = GlassCard(self)
        dialog_card.pack(padx=18, pady=18)

        hdr = tk.Frame(dialog_card, bg=_get_c("SURFACE"))
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=_get_c("INDIGO_500"), height=3).pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg=_get_c("SURFACE"), padx=22, pady=14)
        hdr_inner.pack(fill="x")
        icon_lbl = tk.Label(hdr_inner,
                            text="✏️" if self._is_edit else "➕",
                            bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                            font=("Inter", 18))
        icon_lbl.pack(side="left", padx=(0, 12))
        title_f = tk.Frame(hdr_inner, bg=_get_c("SURFACE"))
        title_f.pack(side="left")
        tk.Label(title_f,
                 text="Chỉnh sửa người dùng" if self._is_edit else "Thêm người dùng mới",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                 font=("Inter", 13, "bold")).pack(anchor="w")
        tk.Label(title_f,
                 text="Cập nhật thông tin tài khoản" if self._is_edit
                      else "Điền đầy đủ thông tin người dùng mới",
                 bg=_get_c("SLATE_800"), fg=_get_c("INDIGO_200"),
                 font=("Inter", 9)).pack(anchor="w")

        frm = tk.Frame(dialog_card, bg=_get_c("BG"), padx=24, pady=20)
        frm.pack(fill="both", expand=True)

        def make_field(name: str, label: str, icon: str, show: str = "") -> tk.Entry:
            tk.Label(frm, text=label, bg=_get_c("BG"), fg=_get_c("TEXT"),
                     font=("Inter", 9, "bold")).pack(anchor="w", pady=(12, 4))
            outer = tk.Frame(frm, bg=_get_c("BORDER"), padx=1, pady=1)
            outer.pack(fill="x")
            inner = tk.Frame(outer, bg=_get_c("SURFACE"))
            inner.pack(fill="x")
            if icon:
                tk.Label(inner, text=icon, bg=_get_c("SURFACE"),
                         fg=_get_c("TEXT"), font=("Inter", 13)).pack(side="left", padx=(10, 6), pady=8)
            entry = tk.Entry(inner, textvariable=self.vars[name], show=show,
                             font=("Inter", 11), relief="flat",
                             bg=_get_c("BG"), fg=_get_c("TEXT"),
                             insertbackground=_get_c("INDIGO_500"))
            entry.pack(side="left", fill="x", expand=True, padx=(0 if icon else 10), pady=8)
            return entry

        labels = {
            "user_id": "Mã người dùng",
            "username": "Tên đăng nhập",
            "full_name": "Họ và tên",
            "email": "Email",
            "phone": "Số điện thoại",
            "password": "Mật khẩu mới (để trống nếu không đổi)",
        }
        icons = {
            "user_id": "🔑", "username": "👤", "full_name": "📛",
            "email": "📧", "phone": "📱", "password": "🔒",
        }
        for key in ("user_id", "username", "full_name", "email", "phone", "password"):
            make_field(key, labels[key], icons[key], show="*" if key == "password" else "")

        tk.Label(frm, text="Vai trò", bg=_get_c("BG"), fg=_get_c("MUTED"),
                 font=("Inter", 9, "bold")).pack(anchor="w", pady=(18, 4))
        ttk.Combobox(frm, textvariable=self.vars["role"],
                     values=["Admin", "Giang vien", "Sinh vien"],
                     state="readonly",
                     font=("Inter", 11)).pack(fill="x")

        tk.Label(frm, text="Trạng thái", bg=_get_c("BG"), fg=_get_c("MUTED"),
                 font=("Inter", 9, "bold")).pack(anchor="w", pady=(18, 4))
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Khoa"],
                     state="readonly",
                     font=("Inter", 11)).pack(fill="x")

        btn_row = tk.Frame(frm, bg=_get_c("BG"))
        btn_row.pack(fill="x", pady=(28, 0))
        tk.Label(btn_row, text="* Để trống mật khẩu để giữ nguyên",
                 bg=_get_c("BG"), fg=_get_c("MUTED"),
                 font=("Inter", 8, "italic")).pack(side="left")
        GlowButton(btn_row, "Lưu lại", self._save, style="primary").pack(side="right", padx=(6, 0))
        GlowButton(btn_row, "Hủy", self.destroy, style="ghost").pack(side="right")

    def _save(self) -> None:
        data = {k: v.get().strip() for k, v in self.vars.items()}
        # Required field validation
        for field, label in (("user_id", "Ma nguoi dung"),
                             ("username", "Ten dang nhap"),
                             ("full_name", "Ho va ten")):
            if not data[field]:
                messagebox.showwarning("Thieu thong tin",
                                       f"Vui long nhap: {label}.", parent=self)
                return
        # Password required for new user
        if not self._is_edit and not data["password"]:
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long nhap mat khau cho nguoi dung moi.",
                                   parent=self)
            return
        # Email format check
        if data["email"] and not re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", data["email"]):
            messagebox.showwarning("Email khong hop le",
                                   "Dinh dang email sai. Vi du: ten@truong.edu.vn",
                                   parent=self)
            return
        # Username: alphanumeric + underscore only
        if not re.match(r"^[\w]+$", data["username"]):
            messagebox.showwarning("Ten dang nhap khong hop le",
                                   "Ten dang nhap chi duoc chua chu, so, dau _.",
                                   parent=self)
            return
        self.result = data
        self.destroy()


class UserManagementFrame(tk.Frame):
    def __init__(self, master: tk.Misc, user_controller: Any) -> None: # type: ignore
        super().__init__(master, bg=_get_c("BG"))
        self.user_ctrl: 'user_controller' = user_controller # type: ignore
        self.search_var = tk.StringVar()
        self.role_filter_var = tk.StringVar(value="")
        self.tree: Optional[ttk.Treeview] = None
        self._stat_labels: dict[str, tk.Label] = {}
        self._search_timer: str | None = None
        self.search_var.trace_add("write", lambda *_: self._on_search_change())
        self._build()
        self.refresh()

    def _build(self) -> None:
        # ── Header ───────────────────────────────────────────────────────────
        header_card = GlassCard(self)
        header_card.pack(fill="x", padx=20, pady=(20, 16))

        # Header bar with accent
        header_bar = tk.Frame(header_card, bg=_get_c("ACCENT"), pady=0)
        header_bar.pack(fill="x")

        tk.Frame(header_bar, bg=_get_c("INFO_BG"), height=3).pack(fill="x")

        header_content = tk.Frame(header_bar, bg=_get_c("ACCENT"), padx=20, pady=12)
        header_content.pack(fill="x")
        tk.Label(header_content, text="👥", bg=_get_c("ACCENT"), fg="white",
                 font=("Inter", 15)).pack(side="left")
        tk.Label(header_content, text="  Quản lý người dùng",
                 bg=_get_c("ACCENT"), fg="white",
                 font=("Inter", 13, "bold")).pack(side="left")
        tk.Label(header_content,
                 text="Quản lý tài khoản và quyền truy cập của người dùng",
                 bg=_get_c("ACCENT"), fg=_get_c("INFO_BG"),
                 font=("Inter", 9)).pack(side="right")

        # ── Stat summary bar ─────────────────────────────────────────────────
        stats_card = GlassCard(self)
        stats_card.pack(fill="x", padx=20, pady=(0, 12))

        stat_defs = [
            ("total",    "👥", "Tổng người dùng",  _get_c("BG"), _get_c("TEXT")),
            ("admin",    "🛡️", "Quản trị viên",    _get_c("INFO_BG"), _get_c("ACCENT")),
            ("gv",       "🎓", "Giảng viên",       _get_c("SUCCESS_BG"), _get_c("SUCCESS")),
            ("sv",       "🧑‍🎓", "Sinh viên",        _get_c("WARNING_BG"), _get_c("WARNING")),
            ("locked",   "🔒", "Bị khóa",          _get_c("DANGER_BG"), _get_c("DANGER")),
        ]
        for key, icon, label, bg, fg in stat_defs:
            # Create a custom badge-like frame since we need specific colors
            chip = tk.Frame(stats_card, bg=bg, padx=12, pady=6)
            chip.pack(side="left", padx=(0, 8))
            tk.Label(chip, text=f"{icon} {label}:", bg=bg, fg=fg, 
                     font=("Inter", 9, "bold")).pack(side="left")
            val_lbl = tk.Label(chip, text="–", bg=bg, fg=fg, font=("Inter", 10, "bold"))
            val_lbl.pack(side="left", padx=(4, 0))
            self._stat_labels[key] = val_lbl

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=_get_c("BG"))
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        search_box(toolbar, self.search_var).pack(side="left")

        # Role filter pills
        tk.Label(toolbar, text="Vai trò:", bg=_get_c("BG"), fg=_get_c("MUTED"),
                 font=FONT_BODY).pack(side="left", padx=(16, 4))
        ROLE_PILLS = [
            ("Tất cả",     "",            _get_c("SURFACE"), _get_c("TEXT")),
            ("Admin",      "Admin",       _get_c("PURPLE_100"), _get_c("PURPLE_800")),
            ("Giảng viên", "Giang vien",  _get_c("EMERALD_100"), _get_c("EMERALD_800")),
            ("Sinh viên",  "Sinh vien",   _get_c("AMBER_100"), _get_c("AMBER_800")),
        ]
        self._role_pill_btns: list[tk.Button] = []

        def _set_role(val: str, idx: int) -> None:
            self.role_filter_var.set(val)
            for i, (pb, (_, _, bg, fg)) in enumerate(
                    zip(self._role_pill_btns, ROLE_PILLS)):
                pb.config(bg=fg if i == idx else bg,
                          fg="white" if i == idx else fg,
                          highlightbackground=fg if i == idx else _get_c("BORDER"))
            self.refresh()

        for i, (label, val, bg, fg) in enumerate(ROLE_PILLS):
            pb = tk.Button(toolbar, text=label, bg=bg, fg=fg,
                           font=("Segoe UI", 9, "bold"),
                           relief="flat", bd=0, padx=12, pady=4,
                           cursor="hand2",
                           highlightthickness=1, highlightbackground=_get_c("BORDER"),
                           command=lambda v=val, idx=i: _set_role(v, idx))
            pb.pack(side="left", padx=(0, 4))
            self._role_pill_btns.append(pb)

        GlowButton(toolbar, "Thêm", self._add, style="success").pack(side="left", padx=(12, 4))
        GlowButton(toolbar, "Sửa",  self._edit, style="ghost").pack(side="left", padx=4)
        GlowButton(toolbar, "Xóa",  self._delete, style="danger").pack(side="left", padx=4)

        # Status hint
        self._status_lbl = tk.Label(toolbar, text="", bg=_get_c("BG"), fg=_get_c("MUTED"),
                                    font=FONT_BODY)
        self._status_lbl.pack(side="right", padx=8)

        table_card = GlassCard(self)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "username", "ten", "vai_tro", "email", "phone", "trang_thai")
        hdrs = ("Mã", "Username", "Họ tên", "Vai trò", "Email", "SDT", "Trạng thái")
        wids = (80, 110, 160, 110, 180, 120, 110)
        self.tree = make_tree(table_card, cols, hdrs, wids)
        with_scrollbar(table_card, self.tree)
        # Initialise pill highlight after all widgets exist
        _set_role("", 0)

    def _on_search_change(self) -> None:
        """Debounced search: wait 300ms after last keystroke before refreshing."""
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(300, self.refresh)

    def refresh(self) -> None:
        all_users = self.user_ctrl.list_users("")  # type: ignore
        role_f    = self.role_filter_var.get()

        users = self.user_ctrl.list_users(self.search_var.get())  # type: ignore
        # Apply role filter
        if role_f:
            users = [u for u in users if u.role == role_f]  # type: ignore
        rows = [(u.user_id, u.username, u.full_name,  # type: ignore
                 u.role, u.email, u.phone, u.status)
                for u in users]
        if self.tree is not None:
            fill_tree(self.tree, rows)  # type: ignore
        # Update Stats with animation
        from gui.theme import animate_count
        total   = len(all_users)
        admins  = sum(1 for u in all_users if u.role == "Admin")
        gv      = sum(1 for u in all_users if u.role == "Giang vien")
        sv      = sum(1 for u in all_users if u.role == "Sinh vien")
        locked  = sum(1 for u in all_users if u.status == "Khoa")
        for key, val in (("total", total), ("admin", admins),
                         ("gv", gv), ("sv", sv), ("locked", locked)):
            if key in self._stat_labels:
                animate_count(self._stat_labels[key], val)

        shown = len(rows)
        self._status_lbl.config(
            text=f"Hien thi {shown}/{total} nguoi dung"
            if shown < total else f"Tong: {total} nguoi dung")

    def _selected_user_id(self) -> Optional[str]:
        if self.tree is None:
            return None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _get_user(self) -> Any: # type: ignore
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
