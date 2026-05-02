# notification_gui.py — Internal notification screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from gui.theme import (C_BG, C_BORDER, C_DARK, C_MUTED, C_SURFACE, C_TEXT,
                       F_BODY, F_BODY_B, F_SECTION,
                       page_header, btn)


class NotificationFrame(tk.Frame):
    def __init__(self, master: tk.Misc, notif_controller: Any,
                 current_user: Any, user_controller: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.notif_ctrl = notif_controller
        self.user_ctrl = user_controller
        self.current_user = current_user
        self._canvas: tk.Canvas | None = None
        self._list_frame: tk.Frame | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        self._header_frame = page_header(self, "Thong bao noi bo", "🔔")
        self._header_frame.pack(fill="x")
        # Unread badge (appended to header after first refresh)
        self._badge_lbl: tk.Label | None = None

        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # ── Admin compose panel ───────────────────────────────────────────────
        if self.current_user.role == "Admin":
            self._build_compose(body)
            tk.Frame(body, bg=C_BORDER, height=1).pack(fill="x", pady=(0, 12))

        # ── List header ───────────────────────────────────────────────────────
        list_hdr = tk.Frame(body, bg=C_BG)
        list_hdr.pack(fill="x", pady=(0, 8))
        tk.Label(list_hdr, text="Thong bao cua ban",
                 bg=C_BG, fg=C_DARK, font=F_SECTION).pack(side="left")
        btn(list_hdr, "Danh dau tat ca da doc", self._mark_all_read,
            variant="ghost", icon="✅").pack(side="right")

        # ── Scrollable notification list ──────────────────────────────────────
        outer = tk.Frame(body, bg=C_SURFACE, highlightthickness=1,
                         highlightbackground=C_BORDER)
        outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(outer, bg=C_SURFACE, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical",
                            command=self._canvas.yview)  # type: ignore[arg-type]
        self._list_frame = tk.Frame(self._canvas, bg=C_SURFACE)
        self._list_frame.bind(
            "<Configure>",
            lambda _: self._canvas.configure(  # type: ignore[union-attr]
                scrollregion=self._canvas.bbox("all")))  # type: ignore[union-attr]
        self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._canvas.bind(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))  # type: ignore[union-attr]

    def _build_compose(self, parent: tk.Frame) -> None:
        frm = tk.Frame(parent, bg=C_SURFACE, highlightthickness=1,
                       highlightbackground=C_BORDER, padx=18, pady=14)
        frm.pack(fill="x", pady=(0, 4))

        tk.Label(frm, text="✉  Gui thong bao moi",
                 bg=C_SURFACE, fg="#1e1b4b",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Target row
        r1 = tk.Frame(frm, bg=C_SURFACE)
        r1.pack(fill="x", pady=(0, 6))
        tk.Label(r1, text="Gui den:", bg=C_SURFACE, fg=C_TEXT,
                 font=F_BODY_B, width=10, anchor="w").pack(side="left")
        self._target_var = tk.StringVar(value="Tat ca")
        ttk.Combobox(r1, textvariable=self._target_var,
                     values=["Tat ca", "Giang vien", "Sinh vien"],
                     state="readonly", width=18,
                     font=("Segoe UI", 10)).pack(side="left", padx=(4, 0))

        # Title row
        r2 = tk.Frame(frm, bg=C_SURFACE)
        r2.pack(fill="x", pady=(0, 6))
        tk.Label(r2, text="Tieu de:", bg=C_SURFACE, fg=C_TEXT,
                 font=F_BODY_B, width=10, anchor="w").pack(side="left")
        self._title_var = tk.StringVar()
        tk.Entry(r2, textvariable=self._title_var, font=("Segoe UI", 10),
                 relief="flat", bg="#f8fafc", fg=C_TEXT,
                 width=52).pack(side="left", padx=(4, 0), ipady=4)

        # Message row
        r3 = tk.Frame(frm, bg=C_SURFACE)
        r3.pack(fill="x", pady=(0, 8))
        tk.Label(r3, text="Noi dung:", bg=C_SURFACE, fg=C_TEXT,
                 font=F_BODY_B, width=10, anchor="nw").pack(
            side="left", pady=(4, 0))
        self._msg_text = tk.Text(r3, font=("Segoe UI", 10), height=3,
                                  relief="flat", bg="#f8fafc", fg=C_TEXT,
                                  width=52, wrap="word")
        self._msg_text.pack(side="left", padx=(4, 0), pady=(4, 0))

        btn(frm, "Gui thong bao", self._send,
            variant="primary", icon="📨").pack(anchor="e", pady=(4, 0))

    def _send(self) -> None:
        title = self._title_var.get().strip()
        message = self._msg_text.get("1.0", "end").strip()
        target = self._target_var.get()
        try:
            if not self.user_ctrl:
                raise ValueError("Khong co user controller.")
            all_users = self.user_ctrl.list_users()
            if target == "Tat ca":
                count = self.notif_ctrl.send_to_all(
                    self.current_user, title, message, all_users)
            else:
                count = self.notif_ctrl.send_to_role(
                    self.current_user, target, title, message, all_users)
            self._title_var.set("")
            self._msg_text.delete("1.0", "end")
            messagebox.showinfo("Thanh cong", f"Da gui {count} thong bao.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Loi", str(e))

    def _mark_all_read(self) -> None:
        self.notif_ctrl.mark_all_read(self.current_user.user_id)
        self.refresh()

    def refresh(self) -> None:
        if self._list_frame is None:
            return
        for w in self._list_frame.winfo_children():
            w.destroy()

        notifs = self.notif_ctrl.get_notifications(self.current_user.user_id)

        # ── Update unread badge in header ─────────────────────────────────
        unread_count = sum(1 for n in notifs if not n["is_read"])
        if self._badge_lbl is not None:
            self._badge_lbl.destroy()
            self._badge_lbl = None
        if unread_count > 0:
            self._badge_lbl = tk.Label(
                self._header_frame,
                text=f"  {unread_count} chua doc  ",
                bg="#dc2626", fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=4, pady=2)
            self._badge_lbl.pack(side="right", padx=16, pady=10)

        if not notifs:
            tk.Label(self._list_frame, text="Khong co thong bao nao.",
                     bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 11, "italic")).pack(pady=30)
            return

        for n in notifs:
            self._draw_row(n)

    def _draw_row(self, n: dict) -> None:
        is_unread = not n["is_read"]
        row_bg = "#eef2ff" if is_unread else C_SURFACE
        row = tk.Frame(self._list_frame, bg=row_bg, padx=16, pady=10,
                       cursor="hand2")
        row.pack(fill="x")
        tk.Frame(self._list_frame, bg=C_BORDER, height=1).pack(fill="x")

        # Top: dot + title + timestamp
        top = tk.Frame(row, bg=row_bg)
        top.pack(fill="x")
        dot_color = "#4f46e5" if is_unread else C_MUTED
        tk.Label(top, text="●  " if is_unread else "○  ",
                 bg=row_bg, fg=dot_color,
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Label(top, text=n["title"], bg=row_bg, fg=C_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        try:
            ts_str = dt.datetime.fromisoformat(n["created_at"]).strftime("%d/%m/%Y %H:%M")
        except Exception:
            ts_str = str(n["created_at"])
        tk.Label(top, text=ts_str, bg=row_bg, fg=C_MUTED,
                 font=("Segoe UI", 8)).pack(side="right")

        # Message body
        tk.Label(row, text=n["message"], bg=row_bg, fg=C_TEXT,
                 font=F_BODY, wraplength=760, justify="left",
                 anchor="w").pack(fill="x", pady=(4, 2))

        # Sender
        tk.Label(row, text=f"Tu: {n['sender_name']}",
                 bg=row_bg, fg=C_MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w")

        def _on_click(event=None, nid=n["id"], item=n):
            self.notif_ctrl.mark_read(nid)
            self.refresh()
            self._show_notification_detail(item)

        row.bind("<Button-1>", _on_click)
        # Bind all descendants recursively so clicking on any child triggers mark-as-read
        def _bind_children(widget: tk.Misc) -> None:
            for child in widget.winfo_children():
                child.bind("<Button-1>", _on_click)
                _bind_children(child)
        _bind_children(row)

    def _show_notification_detail(self, n: dict) -> None:
        dlg = tk.Toplevel(self)
        dlg.title("Chi tiet thong bao")
        dlg.configure(bg=C_SURFACE)
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())

        card = tk.Frame(dlg, bg=C_SURFACE, padx=18, pady=14,
                        highlightthickness=1, highlightbackground=C_BORDER)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(card, text=n.get("title", "Thong bao"),
                 bg=C_SURFACE, fg=C_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")

        created = n.get("created_at", "")
        sender = n.get("sender_name", "He thong")
        tk.Label(card, text=f"Tu: {sender}   |   {created}",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 10))

        msg_box = tk.Frame(card, bg="#f8fafc",
                           highlightthickness=1, highlightbackground=C_BORDER)
        msg_box.pack(fill="x")
        tk.Label(msg_box, text=n.get("message", ""),
                 bg="#f8fafc", fg=C_TEXT,
                 font=F_BODY, wraplength=520,
                 justify="left", anchor="w").pack(fill="x", padx=10, pady=10)

        btn(card, "Dong", dlg.destroy, variant="ghost").pack(anchor="e", pady=(10, 0))

        dlg.update_idletasks()
        pw = self.winfo_rootx() + self.winfo_width() // 2
        ph = self.winfo_rooty() + self.winfo_height() // 2
        w, h = dlg.winfo_width(), dlg.winfo_height()
        dlg.geometry(f"+{pw - w//2}+{ph - h//2}")
