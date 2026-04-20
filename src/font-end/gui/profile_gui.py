# profile_gui.py  –  user profile dialog with password change  (v2.0)
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from gui.theme import (C_PRIMARY, C_SURFACE, C_BORDER, C_MUTED, F_INPUT, btn)


class ProfileDialog(tk.Toplevel):
    """Shows current user profile and allows password change."""

    def __init__(self, master, current_user, auth_controller) -> None:
        super().__init__(master)
        self.user      = current_user
        self.auth_ctrl = auth_controller
        self.title("Thong tin ca nhan")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)
        self.grab_set()
        self._build()
        self.after(100, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # Role color
        role_colors = {
            "Admin":      ("#2255a4", "#dbeafe"),
            "Giang vien": ("#15803d", "#dcfce7"),
            "Sinh vien":  ("#854d0e", "#fef9c3"),
        }
        fg, bg = role_colors.get(self.user.role, ("#475569", "#f1f5f9"))

        # Header with avatar
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=24, pady=18)
        hdr.pack(fill="x")

        av = tk.Canvas(hdr, width=56, height=56, bg=C_PRIMARY,
                       highlightthickness=0)
        av.pack(side="left", padx=(0, 14))
        av.create_oval(2, 2, 54, 54, fill="#4a8ecb", outline="")
        initials = "".join(p[0] for p in self.user.full_name.split()[:2]).upper()
        av.create_text(28, 28, text=initials, fill="white",
                       font=("Segoe UI", 18, "bold"))

        info = tk.Frame(hdr, bg=C_PRIMARY)
        info.pack(side="left", fill="x")
        tk.Label(info, text=self.user.full_name, bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(info, text=f"@{self.user.username}", bg=C_PRIMARY, fg="#93c5fd",
                 font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(info, text=f"  {self.user.role}  ",
                 bg=bg, fg=fg,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 0))

        # Profile info
        body = tk.Frame(self, bg=C_SURFACE, padx=26, pady=18)
        body.pack(fill="x")

        def info_row(icon, label, value):
            row = tk.Frame(body, bg=C_SURFACE)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=icon, bg=C_SURFACE,
                     font=("Segoe UI", 13), width=2).pack(side="left")
            tk.Label(row, text=f"{label}:", bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9), width=14, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=C_SURFACE, fg="#1e293b",
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        info_row("🔑", "Ma tai khoan", self.user.user_id)
        info_row("👤", "Ten dang nhap", self.user.username)
        info_row("📛", "Ho va ten",    self.user.full_name)
        info_row("📧", "Email",        self.user.email)
        info_row("📱", "So dien thoai", self.user.phone)
        info_row("🔒", "Trang thai",   self.user.status)

        # Divider
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x", padx=24)

        # Change password section
        pw_frame = tk.Frame(self, bg=C_SURFACE, padx=26, pady=18)
        pw_frame.pack(fill="x")

        tk.Label(pw_frame, text="🔐  Doi mat khau",
                 bg=C_SURFACE, fg="#1a2f5e",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 12))

        self._old_pw  = tk.StringVar()
        self._new_pw  = tk.StringVar()
        self._conf_pw = tk.StringVar()

        for label, var in [
            ("Mat khau hien tai",     self._old_pw),
            ("Mat khau moi (min 6)",  self._new_pw),
            ("Xac nhan mat khau moi", self._conf_pw),
        ]:
            tk.Label(pw_frame, text=label, bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0))
            wrap = tk.Frame(pw_frame, bg=C_SURFACE, highlightthickness=1,
                            highlightbackground=C_BORDER)
            wrap.pack(fill="x", pady=(3, 0))
            e = tk.Entry(wrap, textvariable=var, show="*", width=34,
                         font=("Segoe UI", 10), relief="flat", bg=C_SURFACE)
            e.pack(padx=10, pady=7)

            def _in(_, w=wrap):
                w.config(highlightbackground="#2255a4", highlightthickness=2)
            def _out(_, w=wrap):
                w.config(highlightbackground=C_BORDER, highlightthickness=1)
            e.bind("<FocusIn>",  _in)
            e.bind("<FocusOut>", _out)

        # Buttons
        btn_row = tk.Frame(self, bg=C_SURFACE, padx=26)
        btn_row.pack(fill="x", pady=(4, 20))
        btn(btn_row, "  Doi mat khau  ", self._change_pw,
            variant="primary", icon="💾").pack(side="left")
        btn(btn_row, "Dong", self.destroy,
            variant="ghost").pack(side="left", padx=10)

    def _change_pw(self) -> None:
        old   = self._old_pw.get().strip()
        new   = self._new_pw.get().strip()
        conf  = self._conf_pw.get().strip()

        if not old or not new or not conf:
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long dien day du mat khau.",
                                   parent=self)
            return
        if new != conf:
            messagebox.showerror("Loi",
                                 "Mat khau xac nhan khong khop.",
                                 parent=self)
            return
        if len(new) < 6:
            messagebox.showwarning("Qua ngan",
                                   "Mat khau moi phai co it nhat 6 ky tu.",
                                   parent=self)
            return

        # Verify current password
        user_check = self.auth_ctrl.authenticate(self.user.username, old)
        if user_check is None:
            messagebox.showerror("Sai mat khau",
                                 "Mat khau hien tai khong dung.",
                                 parent=self)
            return

        # Apply reset
        try:
            self.auth_ctrl.reset_password(
                username=self.user.username,
                email=self.user.email,
                new_password=new,
            )
        except ValueError as exc:
            messagebox.showerror("Loi", str(exc), parent=self)
            return

        messagebox.showinfo("Thanh cong",
                            "Mat khau da duoc doi thanh cong!",
                            parent=self)
        self._old_pw.set("")
        self._new_pw.set("")
        self._conf_pw.set("")
