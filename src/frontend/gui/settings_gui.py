# settings_gui.py — Settings page (change password, update profile)
from __future__ import annotations
import tkinter as tk

from gui.theme import (
    F_SECTION, F_BODY, F_BODY_B, btn,
    labeled_entry, pw_strength_bar, eye_toggle, page_header, make_card, _get_c,
)


class SettingsFrame(tk.Frame):
    """Settings page: change password and update basic profile fields."""

    def __init__(self, master, auth_controller, current_user,
                 on_profile_updated=None, user_controller=None) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.auth_ctrl          = auth_controller
        self.user_ctrl          = user_controller
        self.user               = current_user
        self.on_profile_updated = on_profile_updated or (lambda: None)
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        page_header(self, "Cai dat tai khoan", "⚙️").pack(fill="x")

        # Scrollable body
        canvas = tk.Canvas(self, bg=_get_c("BG"), highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical",
                                 command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=_get_c("BG"))
        win_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        body.bind("<Configure>",
                  lambda e=None: canvas.config(scrollregion=canvas.bbox("all")))

        # ── Column layout ──────────────────────────────────────────────────
        cols = tk.Frame(body, bg=_get_c("BG"))
        cols.pack(fill="both", expand=True, padx=24, pady=16)

        self._build_password_card(cols)
        self._build_profile_card(cols)

    # ── Change-password card ──────────────────────────────────────────────────

    def _build_password_card(self, parent: tk.Frame) -> None:
        outer, card = make_card(parent)
        outer.pack(side="left", fill="both", expand=True,
                   padx=(0, 12), pady=8, anchor="n")

        tk.Label(card, text="🔒  Doi mat khau",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_SECTION).pack(anchor="w", pady=(0, 12))
        tk.Frame(card, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=(0, 16))

        self._cur_pw  = tk.StringVar()
        self._new_pw  = tk.StringVar()
        self._conf_pw = tk.StringVar()

        _, e_cur  = labeled_entry(card, "Mat khau hien tai", self._cur_pw, show="•")
        _, e_new  = labeled_entry(card, "Mat khau moi",      self._new_pw, show="•")
        _, e_conf = labeled_entry(card, "Xac nhan mat khau", self._conf_pw, show="•")

        # Eye-toggle buttons placed inside each entry's inner frame
        eye_toggle(e_cur.master,  e_cur,  bg=_get_c("SURFACE")).pack(side="right", padx=(0, 8))
        eye_toggle(e_new.master,  e_new,  bg=_get_c("SURFACE")).pack(side="right", padx=(0, 8))
        eye_toggle(e_conf.master, e_conf, bg=_get_c("SURFACE")).pack(side="right", padx=(0, 8))

        # Password-strength bar (hooks its own trace on self._new_pw)
        pw_strength_bar(card, self._new_pw, bg=_get_c("SURFACE")).pack(
            fill="x", pady=(4, 12))

        self._pw_status = tk.Label(card, text="", bg=_get_c("SURFACE"),
                                   fg=_get_c("MUTED"), font=F_BODY)
        self._pw_status.pack(anchor="w", pady=(0, 8))

        btn(card, "Cap nhat mat khau", self._change_password,
            variant="primary", icon="💾").pack(pady=(4, 0))

    # ── Profile info card ─────────────────────────────────────────────────────

    def _build_profile_card(self, parent: tk.Frame) -> None:
        outer, card = make_card(parent)
        outer.pack(side="left", fill="both", expand=True,
                   padx=(12, 0), pady=8, anchor="n")

        tk.Label(card, text="👤  Thong tin ca nhan",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_SECTION).pack(anchor="w", pady=(0, 12))
        tk.Frame(card, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=(0, 16))

        # Read-only fields
        fields = [
            ("Ho ten",      getattr(self.user, "full_name", "")),
            ("Ten dang nhap", getattr(self.user, "username", "")),
            ("Email",       getattr(self.user, "email", "")),
            ("So dien thoai", getattr(self.user, "phone", "")),
            ("Vai tro",     getattr(self.user, "role", "")),
        ]
        for label, value in fields:
            row = tk.Frame(card, bg=_get_c("SURFACE"))
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"{label}:", width=18, anchor="w",
                     bg=_get_c("SURFACE"), fg=_get_c("MUTED"), font=F_BODY).pack(side="left")
            tk.Label(row, text=str(value), anchor="w",
                     bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_BODY_B).pack(
                side="left", fill="x", expand=True)

        tk.Frame(card, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=12)

        # Editable: full_name, email, phone
        self._edit_name  = tk.StringVar(value=getattr(self.user, "full_name", ""))
        self._edit_email = tk.StringVar(value=getattr(self.user, "email", ""))
        self._edit_phone = tk.StringVar(value=getattr(self.user, "phone", ""))

        tk.Label(card, text="Chinh sua thong tin",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_BODY_B).pack(anchor="w", pady=(0, 8))

        labeled_entry(card, "Ho ten",       self._edit_name)[0].pack(fill="x", pady=4)
        labeled_entry(card, "Email",        self._edit_email)[0].pack(fill="x", pady=4)
        labeled_entry(card, "So dien thoai",self._edit_phone)[0].pack(fill="x", pady=4)

        self._profile_status = tk.Label(card, text="", bg=_get_c("SURFACE"),
                                        fg=_get_c("MUTED"), font=F_BODY)
        self._profile_status.pack(anchor="w", pady=(8, 4))

        btn(card, "Luu thay doi", self._save_profile,
            variant="primary", icon="💾").pack(pady=(4, 0))

    # ── Actions ───────────────────────────────────────────────────────────────

    def _change_password(self) -> None:
        cur  = self._cur_pw.get().strip()
        new  = self._new_pw.get()
        conf = self._conf_pw.get()

        if not cur:
            self._set_pw_status("Vui long nhap mat khau hien tai.", error=True)
            return
        if len(new) < 6:
            self._set_pw_status("Mat khau moi phai co it nhat 6 ky tu.", error=True)
            return
        if new != conf:
            self._set_pw_status("Xac nhan mat khau khong khop.", error=True)
            return

        try:
            self.auth_ctrl.change_password(
                self.user.username, cur, new)
            self._set_pw_status("✓ Mat khau da duoc cap nhat.", error=False)
            self._cur_pw.set("")
            self._new_pw.set("")
            self._conf_pw.set("")
        except ValueError as exc:
            self._set_pw_status(str(exc), error=True)
        except Exception:
            self._set_pw_status("Co loi xay ra. Vui long thu lai.", error=True)

    def _save_profile(self) -> None:
        name  = self._edit_name.get().strip()
        email = self._edit_email.get().strip()
        phone = self._edit_phone.get().strip()
        if not name:
            self._set_profile_status("Ho ten khong duoc de trong.", error=True)
            return
        if self.user_ctrl is None:
            self._set_profile_status("Khong co quyen cap nhat.", error=True)
            return
        try:
            self.user_ctrl.update_profile(
                self.user.user_id,
                full_name=name, email=email, phone=phone)
            if hasattr(self.user, "full_name"):
                self.user.full_name = name
            if hasattr(self.user, "email"):
                self.user.email = email
            if hasattr(self.user, "phone"):
                self.user.phone = phone
            self._set_profile_status("✓ Thong tin da duoc cap nhat.", error=False)
            self.on_profile_updated()
        except Exception:
            self._set_profile_status("Co loi xay ra. Vui long thu lai.", error=True)

    def _set_pw_status(self, msg: str, *, error: bool) -> None:
        self._pw_status.config(
            text=msg, fg=_get_c("DANGER") if error else "#16a34a")

    def _set_profile_status(self, msg: str, *, error: bool) -> None:
        self._profile_status.config(
            text=msg, fg=_get_c("DANGER") if error else "#16a34a")
