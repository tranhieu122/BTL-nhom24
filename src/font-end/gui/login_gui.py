# login_gui.py  –  split-panel login screen  (login + register + forgot-pw)
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from gui.theme import (C_DARK, C_PRIMARY, C_SURFACE, C_BORDER,
                       C_TEXT, C_MUTED, F_INPUT, btn)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _labeled_entry(parent, label: str, var: tk.StringVar,
                   show: str = "", width: int = 32) -> tk.Frame:
    """Return a labeled, focus-bordered entry block."""
    tk.Label(parent, text=label, bg=C_SURFACE, fg=C_MUTED,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 0))
    wrap = tk.Frame(parent, bg=C_SURFACE, highlightthickness=1,
                    highlightbackground=C_BORDER)
    wrap.pack(fill="x", pady=(4, 0))
    e = tk.Entry(wrap, textvariable=var, width=width, show=show,
                 font=F_INPUT, relief="flat", bg=C_SURFACE, fg=C_TEXT)
    e.pack(padx=12, pady=8)

    def on_in(_):
        wrap.config(highlightbackground="#2255a4", highlightthickness=2)
    def on_out(_):
        wrap.config(highlightbackground=C_BORDER,  highlightthickness=1)
    e.bind("<FocusIn>",  on_in)
    e.bind("<FocusOut>", on_out)
    return wrap


# ── Register dialog ───────────────────────────────────────────────────────────

class RegisterDialog(tk.Toplevel):
    def __init__(self, master, auth_controller) -> None:
        super().__init__(master)
        self.auth_ctrl = auth_controller
        self.title("Dang ky tai khoan")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)
        self.grab_set()
        self._vars = {k: tk.StringVar() for k in
                      ("full_name", "username", "email", "phone",
                       "password", "confirm", "role")}
        self._vars["role"].set("Sinh vien")
        self._build()
        self.after(100, self._center)

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _build(self) -> None:
        # Header
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=24, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📝  Dang ky tai khoan moi",
                 bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Tao tai khoan de dat phong hoc",
                 bg=C_PRIMARY, fg="#93c5fd",
                 font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(self, bg=C_SURFACE, padx=28, pady=20)
        body.pack(fill="x")

        _labeled_entry(body, "HO VA TEN *",        self._vars["full_name"])
        _labeled_entry(body, "TEN DANG NHAP *",    self._vars["username"])
        _labeled_entry(body, "EMAIL *",             self._vars["email"])
        _labeled_entry(body, "SO DIEN THOAI *",    self._vars["phone"])
        _labeled_entry(body, "MAT KHAU * (min 6)", self._vars["password"],  show="*")
        _labeled_entry(body, "XAC NHAN MAT KHAU",  self._vars["confirm"],   show="*")

        tk.Label(body, text="VAI TRO", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 0))
        ttk.Combobox(body, textvariable=self._vars["role"],
                     values=["Sinh vien", "Giang vien"],
                     state="readonly", width=30,
                     font=("Segoe UI", 10)).pack(fill="x", pady=(4, 0))

        # Notice
        notice = tk.Frame(body, bg="#eff6ff",
                          highlightthickness=1, highlightbackground="#bfdbfe")
        notice.pack(fill="x", pady=(16, 0))
        tk.Label(notice, text="ℹ  Tai khoan 'Admin' chi duoc tao boi quan tri vien.",
                 bg="#eff6ff", fg="#1d4ed8",
                 font=("Segoe UI", 8), anchor="w").pack(
            fill="x", padx=10, pady=6)

        # Buttons
        btn_row = tk.Frame(self, bg=C_SURFACE, padx=28, pady=(0, 20))
        btn_row.pack(fill="x")
        btn(btn_row, "  Dang ky  ", self._submit,
            icon="✅").pack(side="left")
        btn(btn_row, "Huy", self.destroy,
            variant="ghost").pack(side="left", padx=10)

    def _submit(self) -> None:
        v = {k: var.get().strip() for k, var in self._vars.items()}
        if v["password"] != v["confirm"]:
            messagebox.showerror("Loi", "Mat khau xac nhan khong khop.", parent=self)
            return
        try:
            self.auth_ctrl.register(
                full_name=v["full_name"],
                username=v["username"],
                email=v["email"],
                phone=v["phone"],
                password=v["password"],
                role=v["role"],
            )
        except ValueError as exc:
            messagebox.showerror("Dang ky that bai", str(exc), parent=self)
            return
        messagebox.showinfo(
            "Dang ky thanh cong",
            f"Tai khoan '{v['username']}' da duoc tao!\n"
            "Ban co the dang nhap ngay bay gio.",
            parent=self)
        self.destroy()


# ── Forgot-password dialog ────────────────────────────────────────────────────

class ForgotPasswordDialog(tk.Toplevel):
    def __init__(self, master, auth_controller) -> None:
        super().__init__(master)
        self.auth_ctrl = auth_controller
        self.title("Quen mat khau")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.transient(master)
        self.grab_set()
        self._step = 1          # 1 = verify identity, 2 = set new password
        self._verified_user = None
        self._vars = {k: tk.StringVar() for k in
                      ("username", "email", "new_pw", "confirm_pw")}
        self._build_step1()
        self.after(100, self._center)

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width()  // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _build_step1(self) -> None:
        self._clear()
        # Header
        hdr = tk.Frame(self, bg="#0369a1", padx=24, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔑  Quen mat khau",
                 bg="#0369a1", fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Buoc 1: Xac minh danh tinh",
                 bg="#0369a1", fg="#bae6fd",
                 font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(self, bg=C_SURFACE, padx=28, pady=20)
        body.pack(fill="x")

        info = tk.Frame(body, bg="#f0f9ff",
                        highlightthickness=1, highlightbackground="#bae6fd")
        info.pack(fill="x", pady=(0, 14))
        tk.Label(info,
                 text="  Nhap ten dang nhap va email da dang ky\n"
                      "  de xac minh danh tinh cua ban.",
                 bg="#f0f9ff", fg="#0369a1",
                 font=("Segoe UI", 9), justify="left", anchor="w").pack(
            fill="x", padx=8, pady=8)

        _labeled_entry(body, "TEN DANG NHAP",    self._vars["username"])
        _labeled_entry(body, "EMAIL DA DANG KY", self._vars["email"])

        btn_row = tk.Frame(self, bg=C_SURFACE, padx=28, pady=(0, 20))
        btn_row.pack(fill="x")
        btn(btn_row, "  Xac minh  ", self._verify_step1,
            variant="primary", icon="🔍").pack(side="left")
        btn(btn_row, "Huy", self.destroy,
            variant="ghost").pack(side="left", padx=10)

    def _verify_step1(self) -> None:
        username = self._vars["username"].get().strip()
        email    = self._vars["email"].get().strip()
        if not username or not email:
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long nhap day du thong tin.",
                                   parent=self)
            return
        user = self.auth_ctrl.find_account_for_reset(username, email)
        if user is None:
            messagebox.showerror(
                "Xac minh that bai",
                "Khong tim thay tai khoan voi ten dang nhap va email nay.\n"
                "Kiem tra lai thong tin va thu lai.",
                parent=self)
            return
        self._verified_user = user
        self._build_step2()

    def _build_step2(self) -> None:
        self._clear()
        # Header
        hdr = tk.Frame(self, bg="#15803d", padx=24, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✅  Xac minh thanh cong",
                 bg="#15803d", fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Buoc 2: Dat mat khau moi",
                 bg="#15803d", fg="#bbf7d0",
                 font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(self, bg=C_SURFACE, padx=28, pady=20)
        body.pack(fill="x")

        success_box = tk.Frame(body, bg="#f0fdf4",
                               highlightthickness=1,
                               highlightbackground="#bbf7d0")
        success_box.pack(fill="x", pady=(0, 14))
        name = getattr(self._verified_user, "full_name", "")
        tk.Label(success_box,
                 text=f"  Da xac minh: {name}",
                 bg="#f0fdf4", fg="#15803d",
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(
            fill="x", padx=8, pady=8)

        _labeled_entry(body, "MAT KHAU MOI * (min 6)",
                       self._vars["new_pw"], show="*")
        _labeled_entry(body, "XAC NHAN MAT KHAU MOI",
                       self._vars["confirm_pw"], show="*")

        btn_row = tk.Frame(self, bg=C_SURFACE, padx=28, pady=(0, 20))
        btn_row.pack(fill="x")
        btn(btn_row, "  Luu mat khau moi  ", self._save_password,
            variant="success", icon="💾").pack(side="left")
        btn(btn_row, "Huy", self.destroy,
            variant="ghost").pack(side="left", padx=10)

    def _save_password(self) -> None:
        new_pw     = self._vars["new_pw"].get().strip()
        confirm_pw = self._vars["confirm_pw"].get().strip()
        if new_pw != confirm_pw:
            messagebox.showerror("Loi",
                                 "Mat khau xac nhan khong khop.", parent=self)
            return
        try:
            self.auth_ctrl.reset_password(
                username=self._verified_user.username,
                email=self._verified_user.email,
                new_password=new_pw,
            )
        except ValueError as exc:
            messagebox.showerror("Loi", str(exc), parent=self)
            return
        messagebox.showinfo(
            "Thanh cong",
            "Mat khau da duoc doi thanh cong!\n"
            "Vui long dang nhap lai bang mat khau moi.",
            parent=self)
        self.destroy()


# ── Login frame ───────────────────────────────────────────────────────────────

class LoginFrame(tk.Frame):
    def __init__(self, master, on_login, auth_controller=None) -> None:
        super().__init__(master, bg=C_DARK)
        self.on_login   = on_login
        self.auth_ctrl  = auth_controller
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left animated branding panel ──────────────────────────────────────
        left = tk.Frame(self, bg=C_DARK)
        left.grid(row=0, column=0, sticky="nsew")

        cv = tk.Canvas(left, bg=C_DARK, highlightthickness=0)
        cv.pack(fill="both", expand=True)

        import random as _rnd
        _particles: list[dict] = []
        _anim_ref: list = [None]

        def _init_particles(w: int, h: int) -> None:
            _particles.clear()
            _COLORS = ["#243d72", "#1e3560", "#233a6a",
                       "#1c3260", "#2a4070", "#1e3878", "#16305a"]
            for _ in range(9):
                _particles.append({
                    'x':   _rnd.uniform(0, w),
                    'y':   _rnd.uniform(0, h),
                    'r':   _rnd.uniform(w * 0.05, w * 0.20),
                    'dy':  _rnd.uniform(0.20, 0.65),
                    'dx':  _rnd.uniform(-0.20, 0.20),
                    'col': _rnd.choice(_COLORS),
                })

        def _animate() -> None:
            if not cv.winfo_exists():
                return
            w, h = cv.winfo_width(), cv.winfo_height()
            if w < 20:
                _anim_ref[0] = cv.after(120, _animate)
                return
            if not _particles:
                _init_particles(w, h)

            cv.delete("all")

            # Floating orbs (draw first so text renders on top)
            for p in _particles:
                p['y'] -= p['dy']
                p['x'] += p['dx']
                if p['y'] + p['r'] < 0:
                    p['y'] = h + p['r']
                    p['x'] = _rnd.uniform(0, w)
                if p['x'] < -p['r']:
                    p['x'] = w + p['r']
                elif p['x'] > w + p['r']:
                    p['x'] = -p['r']
                r = p['r']
                cv.create_oval(p['x'] - r, p['y'] - r,
                               p['x'] + r, p['y'] + r,
                               fill=p['col'], outline='')

            # ── Static branding content ───────────────────────────────────────
            cx = w // 2

            # University icon glow ring
            cv.create_oval(cx - 52, h * .27 - 52, cx + 52, h * .27 + 52,
                           fill="#203870", outline="#3b5ea6", width=2)
            cv.create_text(cx, h * .27, text="\U0001f3eb",
                           font=("Segoe UI", 44), fill="white",
                           anchor="center")

            cv.create_text(cx, h * .42,
                           text="HE THONG",
                           font=("Segoe UI", 22, "bold"), fill="white",
                           anchor="center")
            cv.create_text(cx, h * .49,
                           text="QUAN LY DAT PHONG HOC",
                           font=("Segoe UI", 11), fill="#93c5fd",
                           anchor="center")

            # Divider
            cv.create_line(cx - 80, h * .56, cx + 80, h * .56,
                           fill="#3b5ea6", width=2)

            # Feature bullets
            for i, feat in enumerate([
                "✦  Dat phong tuc thi",
                "✦  Quan ly lich theo tuan",
                "✦  Bao cao & thong ke",
            ]):
                cv.create_text(cx, h * .62 + i * h * .065,
                               text=feat, font=("Segoe UI", 9),
                               fill="#94a3b8", anchor="center")

            cv.create_text(cx, h * .88, text="v2.0  \u2022  Nhom 24",
                           font=("Segoe UI", 8), fill="#4a6a9a",
                           anchor="center")

            _anim_ref[0] = cv.after(38, _animate)

        def _on_configure(_e=None) -> None:
            if _anim_ref[0] is None:
                _animate()

        def _on_destroy(_e=None) -> None:
            if _anim_ref[0] is not None:
                try:
                    cv.after_cancel(_anim_ref[0])
                except Exception:
                    pass
                _anim_ref[0] = None

        cv.bind("<Configure>", _on_configure)
        cv.bind("<Destroy>",   _on_destroy)

        # ── Right form panel ──────────────────────────────────────────────────
        right = tk.Frame(self, bg=C_SURFACE)
        right.grid(row=0, column=1, sticky="nsew")

        # Accent top stripe on right side
        tk.Frame(right, bg=C_PRIMARY, height=4).pack(fill="x")

        card = tk.Frame(right, bg=C_SURFACE)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Heading
        tk.Label(card, text="Chao mung tro lai!", bg=C_SURFACE, fg=C_DARK,
                 font=("Segoe UI", 26, "bold")).pack(anchor="w")
        tk.Label(card, text="Dang nhap de quan ly phong hoc",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 22))

        # ── Username field ────────────────────────────────────────────────────
        tk.Label(card, text="TEN DANG NHAP", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        un_wrap = tk.Frame(card, bg=C_SURFACE, highlightthickness=1,
                           highlightbackground=C_BORDER)
        un_wrap.pack(fill="x", pady=(4, 16))

        # Icon + entry
        un_inner = tk.Frame(un_wrap, bg=C_SURFACE)
        un_inner.pack(fill="x")
        tk.Label(un_inner, text="👤", bg=C_SURFACE,
                 font=("Segoe UI", 12)).pack(side="left", padx=(10, 4), pady=7)
        un_e = tk.Entry(un_inner, textvariable=self.username_var, width=28,
                        font=F_INPUT, relief="flat", bg=C_SURFACE, fg=C_TEXT)
        un_e.pack(side="left", padx=(0, 10), pady=7, fill="x", expand=True)
        un_e.focus_set()
        self._bind_focus(un_e, un_wrap)

        # ── Password field + eye toggle ────────────────────────────────────────
        pw_hdr = tk.Frame(card, bg=C_SURFACE)
        pw_hdr.pack(fill="x")
        tk.Label(pw_hdr, text="MAT KHAU", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        forgot_lbl = tk.Label(pw_hdr, text="Quen mat khau?",
                              bg=C_SURFACE, fg=C_PRIMARY,
                              font=("Segoe UI", 9, "underline"),
                              cursor="hand2")
        forgot_lbl.pack(side="right")
        forgot_lbl.bind("<Button-1>", lambda _: self._open_forgot())

        pw_wrap = tk.Frame(card, bg=C_SURFACE, highlightthickness=1,
                           highlightbackground=C_BORDER)
        pw_wrap.pack(fill="x", pady=(4, 22))

        pw_inner = tk.Frame(pw_wrap, bg=C_SURFACE)
        pw_inner.pack(fill="x")
        tk.Label(pw_inner, text="🔒", bg=C_SURFACE,
                 font=("Segoe UI", 12)).pack(side="left", padx=(10, 4), pady=7)
        pw_e = tk.Entry(pw_inner, textvariable=self.password_var, show="*",
                        width=24, font=F_INPUT, relief="flat",
                        bg=C_SURFACE, fg=C_TEXT)
        pw_e.pack(side="left", padx=(0, 4), pady=7, fill="x", expand=True)

        # Eye toggle
        _show_pw = [False]
        def _toggle_eye():
            _show_pw[0] = not _show_pw[0]
            pw_e.config(show="" if _show_pw[0] else "*")
            eye_btn.config(text="🙈" if _show_pw[0] else "👁")
        eye_btn = tk.Button(pw_inner, text="👁", bg=C_SURFACE, fg=C_MUTED,
                            font=("Segoe UI", 11), relief="flat", bd=0,
                            cursor="hand2", command=_toggle_eye,
                            activebackground=C_SURFACE)
        eye_btn.pack(side="right", padx=(0, 8))

        self._bind_focus(pw_e, pw_wrap)

        # ── Login button ──────────────────────────────────────────────────────
        b = btn(card, "  DANG NHAP  →", self._submit)
        b.config(width=30, pady=11, font=("Segoe UI", 12, "bold"))
        b.pack(fill="x")

        # ── Register link ─────────────────────────────────────────────────────
        reg_row = tk.Frame(card, bg=C_SURFACE)
        reg_row.pack(pady=(16, 0))
        tk.Label(reg_row, text="Chua co tai khoan?  ",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        reg_lbl = tk.Label(reg_row, text="Dang ky ngay →",
                           bg=C_SURFACE, fg=C_PRIMARY,
                           font=("Segoe UI", 10, "bold", "underline"),
                           cursor="hand2")
        reg_lbl.pack(side="left")
        reg_lbl.bind("<Button-1>", lambda _: self._open_register())

        self.bind_all("<Return>", lambda _: self._submit())

    @staticmethod
    def _bind_focus(entry: tk.Entry, frame: tk.Frame) -> None:
        def on_in(_):
            frame.config(highlightbackground="#2255a4", highlightthickness=2)
        def on_out(_):
            frame.config(highlightbackground=C_BORDER,  highlightthickness=1)
        entry.bind("<FocusIn>",  on_in)
        entry.bind("<FocusOut>", on_out)

    def _open_register(self) -> None:
        if self.auth_ctrl is None:
            messagebox.showinfo("Thong bao",
                                "Chuc nang dang ky chua duoc ket noi.")
            return
        RegisterDialog(self, self.auth_ctrl)

    def _open_forgot(self) -> None:
        if self.auth_ctrl is None:
            messagebox.showinfo("Thong bao",
                                "Chuc nang lay lai mat khau chua duoc ket noi.")
            return
        ForgotPasswordDialog(self, self.auth_ctrl)

    def _submit(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long nhap ten dang nhap va mat khau.")
            return
        self.on_login(username, password)
