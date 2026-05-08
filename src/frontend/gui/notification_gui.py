# notification_gui.py — Internal notification screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from gui.theme import (F_BODY, F_BODY_B, F_SECTION, _get_c, C_SURFACE, C_BORDER, C_TEXT,
                       page_header, btn, relative_time)

def _get_category_style(combined: str) -> tuple[str, str, str]:
    """Return (icon, badge_bg, badge_fg) for a notification."""
    if any(k in combined for k in ["dat phong", "booking", "phong"]):
        return "📅", _get_c("INFO_BG"), _get_c("ACCENT")
    if any(k in combined for k in ["duyet", "phe duyet"]):
        return "✅", _get_c("SUCCESS_BG"), _get_c("SUCCESS")
    if any(k in combined for k in ["tu choi", "huy"]):
        return "❌", _get_c("DANGER_BG"), _get_c("DANGER")
    if any(k in combined for k in ["thiet bi", "equipment"]):
        return "🔧", "#faf5ff" if _get_c("BG") == "#f8fafc" else "#4c1d95", "#a855f7"
    if any(k in combined for k in ["bao tri", "sua chua"]):
        return "🛠", _get_c("WARNING_BG"), _get_c("WARNING")
    if any(k in combined for k in ["he thong", "system"]):
        return "⚙",  _get_c("SLATE_100") if _get_c("BG") == "#f8fafc" else "#1e293b", _get_c("MUTED")
    
    return "🔔", _get_c("INFO_BG"), _get_c("ACCENT")


class NotificationFrame(tk.Frame):
    def __init__(self, master: tk.Misc, notif_controller: Any,
                 current_user: Any, user_controller: Any = None) -> None:
        super().__init__(master, bg=_get_c("BG"))
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

        body = tk.Frame(self, bg=_get_c("BG"))
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # ── Admin compose panel ───────────────────────────────────────────────
        if self.current_user.role == "Admin":
            self._build_compose(body)
            tk.Frame(body, bg=_get_c("BORDER"), height=1).pack(fill="x", pady=(0, 12))

        # ── List header ───────────────────────────────────────────────────────
        list_hdr = tk.Frame(body, bg=_get_c("BG"))
        list_hdr.pack(fill="x", pady=(0, 8))
        tk.Label(list_hdr, text="Thong bao cua ban",
                 bg=_get_c("BG"), fg=_get_c("TEXT"), font=F_SECTION).pack(side="left")
        btn(list_hdr, "Danh dau tat ca da doc", self._mark_all_read,
            variant="ghost", icon="✅").pack(side="right")

        # ── Scrollable notification list ──────────────────────────────────────
        outer = tk.Frame(body, bg=_get_c("SURFACE"), highlightthickness=1,
                         highlightbackground=_get_c("BORDER"))
        outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(outer, bg=_get_c("SURFACE"), highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical",
                            command=self._canvas.yview)  # type: ignore[arg-type]
        self._list_frame = tk.Frame(self._canvas, bg=_get_c("SURFACE"))
        
        # Store window ID to allow resizing
        self._canvas_window = self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")
        
        def _on_canvas_resize(e: Any) -> None:
            # Sync list_frame width with canvas width
            self._canvas.itemconfig(self._canvas_window, width=e.width)
            # If content is short, we can make the list_frame fill the height
            # to allow for vertical centering of the empty message.
            bbox = self._canvas.bbox("all")
            if bbox and bbox[3] < e.height:
                self._canvas.itemconfig(self._canvas_window, height=e.height)
            else:
                self._canvas.itemconfig(self._canvas_window, height="")

        self._canvas.bind("<Configure>", _on_canvas_resize)
        
        self._list_frame.bind(
            "<Configure>",
            lambda _=None: self._canvas.configure(  # type: ignore[union-attr]
                scrollregion=self._canvas.bbox("all")))  # type: ignore[union-attr]
        
        self._canvas.configure(yscrollcommand=vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._canvas.bind(
            "<MouseWheel>",
            lambda e=None: self._canvas.yview_scroll(-1 * (e.delta // 120) if e else 0, "units"))  # type: ignore[union-attr]

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
        if not title:
            messagebox.showwarning("Thieu tieu de", "Vui long nhap tieu de thong bao.")
            return
        if not message:
            messagebox.showwarning("Thieu noi dung", "Vui long nhap noi dung thong bao.")
            return
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
                bg="#db2777", fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=4, pady=2)
            self._badge_lbl.pack(side="right", padx=16, pady=10)

        if not notifs:
            empty_frame = tk.Frame(self._list_frame, bg=C_SURFACE)
            empty_frame.pack(fill="both", expand=True, pady=60)
            tk.Label(empty_frame, text="🔔", bg=_get_c("SURFACE"),
                     font=("Segoe UI", 36)).pack()
            tk.Label(empty_frame,
                     text="Khong co thong bao nao",
                     bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                     font=("Segoe UI", 12, "bold")).pack(pady=(8, 2))
            tk.Label(empty_frame,
                     text="Cac thong bao moi se hien thi o day",
                     bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                     font=("Segoe UI", 10)).pack()
            return

        for n in notifs:
            self._draw_row(n) # type: ignore

    def _draw_row(self, n: dict) -> None: # type: ignore
        is_unread = not n["is_read"]
        row_bg    = _get_c("INFO_BG") if is_unread else _get_c("SURFACE")
        icon, cat_bg, cat_fg = _get_category_style((n.get("title", "") + " " + n.get("message", "")).lower()) # type: ignore

        # ── Outer card wrapper ────────────────────────────────────────────────
        card_wrap = tk.Frame(self._list_frame, bg=_get_c("BG"), padx=8, pady=4)
        card_wrap.pack(fill="x")

        card = tk.Frame(card_wrap, bg=row_bg, padx=14, pady=12,
                        highlightthickness=1,
                        highlightbackground=_get_c("ACCENT") if is_unread else _get_c("BORDER"),
                        cursor="hand2")
        card.pack(fill="x")

        # Hover effect
        def _enter(_: Any, c=card, bg=row_bg) -> None: # type: ignore
            darken = _get_c("SB_HOVER") if bg == _get_c("INFO_BG") else _get_c("ROW_EVEN")
            c.config(bg=darken)
            for ch in c.winfo_children():
                try:
                    ch.config(bg=darken) # type: ignore
                except Exception:
                    pass

        def _leave(_: Any, c=card, bg=row_bg) -> None: # type: ignore
            c.config(bg=bg)
            for ch in c.winfo_children():
                try:
                    ch.config(bg=bg) # type: ignore
                except Exception:
                    pass

        card.bind("<Enter>", _enter)
        card.bind("<Leave>", _leave)

        # ── Left accent bar (unread = indigo, read = transparent) ────────────
        accent_color = _get_c("ACCENT") if is_unread else row_bg
        accent = tk.Frame(card, bg=accent_color, width=3)
        accent.pack(side="left", fill="y", padx=(0, 10))

        # ── Icon bubble ───────────────────────────────────────────────────────
        ic_frame = tk.Frame(card, bg=cat_bg, padx=6, pady=6)
        ic_frame.pack(side="left", padx=(0, 12))
        tk.Label(ic_frame, text=icon, bg=cat_bg,
                 font=("Segoe UI", 16)).pack()

        # ── Main content ──────────────────────────────────────────────────────
        content = tk.Frame(card, bg=row_bg)
        content.pack(side="left", fill="both", expand=True)

        # Top row: title + relative time + unread dot
        top = tk.Frame(content, bg=row_bg)
        top.pack(fill="x")

        if is_unread:
            tk.Label(top, text="●", bg=row_bg, fg=_get_c("ACCENT"),
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))

        tk.Label(top, text=n.get("title", "Thong bao"), # type: ignore
                 bg=row_bg, fg=_get_c("TEXT"),
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        rel = relative_time(n.get("created_at", "")) # type: ignore
        tk.Label(top, text=rel, bg=row_bg, fg=_get_c("MUTED"),
                 font=("Segoe UI", 8, "italic")).pack(side="right")

        # Message preview (max 2 lines)
        msg = n.get("message", "") # type: ignore
        tk.Label(content, text=msg, bg=row_bg, fg=_get_c("TEXT"), # type: ignore
                 font=F_BODY, wraplength=700,
                 justify="left", anchor="w").pack(fill="x", pady=(3, 0))

        # Bottom row: sender chip + "Danh dau da doc" action
        bottom = tk.Frame(content, bg=row_bg)
        bottom.pack(fill="x", pady=(5, 0))

        sender = n.get("sender_name", "He thong") # type: ignore
        sender_chip = tk.Frame(bottom, bg=cat_bg, padx=6, pady=2)
        sender_chip.pack(side="left")
        tk.Label(sender_chip, text=f"Tu: {sender}",
                 bg=cat_bg, fg=cat_fg,
                 font=("Segoe UI", 8, "bold")).pack()

        if is_unread:
            def _mark_read(event: Any = None, nid: int = n["id"]) -> str:
                self.notif_ctrl.mark_read(nid)
                self.refresh()
                return "break"  # Stop event propagating to card click handler

            read_btn = tk.Label(bottom, text="✓ Danh dau da doc",
                                bg=row_bg, fg=_get_c("ACCENT"),
                                font=("Segoe UI", 8, "underline"),
                                cursor="hand2")
            read_btn.pack(side="right")
            read_btn.bind("<Button-1>", _mark_read)

        # ── Click to view detail ──────────────────────────────────────────────
        def _on_click(_: Any = None, nid: int = n["id"], item: dict = n) -> None: # type: ignore
            if not n["is_read"]:
                self.notif_ctrl.mark_read(nid)
            self._show_notification_detail(item) # pyright: ignore[reportUnknownMemberType]
            self.refresh()

        for widget in (card, content, top, bottom):
            widget.bind("<Button-1>", _on_click) # pyright: ignore[reportUnknownArgumentType]


    def _show_notification_detail(self, n: dict) -> None: # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
        dlg = tk.Toplevel(self)
        dlg.title("Chi tiet thong bao")
        dlg.configure(bg=_get_c("SURFACE"))
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())

        icon, cat_bg, cat_fg = _get_category_style((n.get("title", "") + " " + n.get("message", "")).lower()) # pyright: ignore[reportUnknownArgumentType, reportUnusedVariable, reportUnknownMemberType]

        # Header
        hdr = tk.Frame(dlg, bg=_get_c("ACCENT"), padx=18, pady=14)
        hdr.pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg=_get_c("ACCENT"))
        hdr_inner.pack(fill="x")
        ic_bg = tk.Frame(hdr_inner, bg=cat_bg, padx=8, pady=8)
        ic_bg.pack(side="left", padx=(0, 12))
        tk.Label(ic_bg, text=icon, bg=cat_bg,
                 font=("Segoe UI", 18)).pack()
        info = tk.Frame(hdr_inner, bg=_get_c("ACCENT"))
        info.pack(side="left")
        tk.Label(info, text=n.get("title", "Thong bao"), # type: ignore
                 bg=_get_c("ACCENT"), fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        sender = n.get("sender_name", "He thong") # type: ignore
        tk.Label(info, text=f"Tu: {sender}",
                 bg=_get_c("ACCENT"), fg="#c7d2fe",
                 font=("Segoe UI", 9)).pack(anchor="w")

        card = tk.Frame(dlg, bg=_get_c("SURFACE"), padx=18, pady=14)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        # Time row
        created = n.get("created_at", "") # type: ignore
        rel = relative_time(created) # type: ignore
        try:
            abs_time = dt.datetime.fromisoformat(str(created)).strftime("%d/%m/%Y %H:%M") # type: ignore
        except Exception:
            abs_time = str(created) # type: ignore
        time_row = tk.Frame(card, bg=_get_c("BG"), highlightthickness=1,
                            highlightbackground=_get_c("BORDER"), padx=10, pady=6)
        time_row.pack(fill="x", pady=(0, 12))
        tk.Label(time_row, text=f"🕐  {rel}  ({abs_time})",
                 bg=_get_c("BG"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 9)).pack(anchor="w")

        msg_box = tk.Frame(card, bg=_get_c("BG"),
                           highlightthickness=1, highlightbackground=_get_c("BORDER"))
        msg_box.pack(fill="x")
        tk.Label(msg_box, text=n.get("message", ""), # pyright: ignore[reportUnknownMemberType] # type: ignore
                 bg=_get_c("BG"), fg=_get_c("TEXT"),
                 font=("Segoe UI", 11), wraplength=520,
                 justify="left", anchor="w").pack(fill="x", padx=12, pady=12)

        btn(card, "Dong", dlg.destroy, variant="ghost").pack(anchor="e", pady=(14, 0))

        dlg.update_idletasks()
        pw = self.winfo_rootx() + self.winfo_width() // 2
        ph = self.winfo_rooty() + self.winfo_height() // 2
        w, h = dlg.winfo_width(), dlg.winfo_height()
        dlg.geometry(f"+{pw - w//2}+{ph - h//2}")
