# room_gui.py  –  room management screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from gui.room_detail_gui import RoomDetailDialog
from gui.room_feedback_gui import RoomRatingDialog, RoomIssueDialog
from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_PRIMARY, C_DARK,
                       C_TEXT, C_MUTED, C_SUCCESS,
                       F_SECTION, F_BODY, F_BODY_B, F_SMALL,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box)


class RoomManagementFrame(tk.Frame):
    SLOT_OPTIONS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]

    def __init__(self, master, room_controller, booking_controller=None,
                 feedback_ctrl=None, current_user=None) -> None:
        super().__init__(master, bg=C_BG)
        self.room_ctrl     = room_controller
        self.booking_ctrl  = booking_controller
        self.feedback_ctrl = feedback_ctrl
        self.current_user  = current_user
        self.search_var   = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._suggest_tree: ttk.Treeview | None = None
        self._date_var = tk.StringVar(value=dt.date.today().isoformat())
        self._slot_var = tk.StringVar(value="Ca 1")
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Quan ly phong hoc", "🏫").pack(fill="x")

        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        search_box(toolbar, self.search_var).pack(side="left")
        btn(toolbar, "Tim kiem", self.refresh,
            variant="ghost",   icon="🔍").pack(side="left", padx=(6, 0))

        is_admin = (self.current_user is not None
                    and getattr(self.current_user, "role", "") == "Admin")
        if is_admin:
            btn(toolbar, "Them phong", self._add,
                variant="success", icon="+").pack(side="left", padx=6)
            btn(toolbar, "Sua",       self._edit,
                variant="outline", icon="✏️").pack(side="left", padx=4)
            btn(toolbar, "Xoa",       self._delete,
                variant="danger",  icon="🗑").pack(side="left", padx=4)

        # Feedback buttons (visible to all users)
        tk.Frame(toolbar, bg="#e2e8f0", width=1).pack(
            side="left", fill="y", padx=8, pady=4)
        btn(toolbar, "Danh gia", self._rate_room,
            variant="accent", icon="⭐").pack(side="left", padx=4)
        btn(toolbar, "Bao loi",  self._report_issue,
            variant="outline", icon="🚨").pack(side="left", padx=4)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "ten", "suc_chua", "loai", "thiet_bi", "trang_thai")
        hdrs = ("Ma phong", "Ten phong", "Suc chua", "Loai phong",
                "Trang thiet bi", "Trang thai")
        wids = (100, 160, 90, 140, 260, 120)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # ── Panel gợi ý phòng còn trống ─────────────────────────────────────
        # Outer shadow frame (giả lập shadow bằng viền màu primary)
        suggest_outer = tk.Frame(self, bg=C_BORDER, padx=1, pady=1)
        suggest_outer.pack(fill="x", padx=20, pady=(0, 20))

        suggest_wrap = tk.Frame(suggest_outer, bg=C_SURFACE)
        suggest_wrap.pack(fill="both", expand=True)

        # Header bar – gradient xanh
        header_bar = tk.Frame(suggest_wrap, bg=C_PRIMARY, pady=0)
        header_bar.pack(fill="x")

        # Accent stripe trên cùng header
        tk.Frame(header_bar, bg="#3b82f6", height=3).pack(fill="x")

        header_content = tk.Frame(header_bar, bg=C_PRIMARY, padx=16, pady=10)
        header_content.pack(fill="x")
        tk.Label(header_content, text="💡", bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 15)).pack(side="left")
        tk.Label(header_content, text="  Goi y phong con trong",
                 bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(header_content,
                 text="Chon ngay va ca hoc de tim phong trong nhanh",
                 bg=C_PRIMARY, fg="#bfdbfe",
                 font=("Segoe UI", 9)).pack(side="right")

        # Body
        body = tk.Frame(suggest_wrap, bg=C_SURFACE, padx=16, pady=14)
        body.pack(fill="both", expand=True)

        # ── Controls row ──────────────────────────────────────────────────────
        ctrl_row = tk.Frame(body, bg=C_SURFACE)
        ctrl_row.pack(fill="x", pady=(0, 12))

        # Ngay label + entry với viền focus
        tk.Label(ctrl_row, text="📅  Ngay:", bg=C_SURFACE,
                 fg=C_TEXT, font=F_BODY_B).pack(side="left")

        date_frame = tk.Frame(ctrl_row, bg=C_SURFACE, highlightthickness=1,
                              highlightbackground=C_BORDER)
        date_frame.pack(side="left", padx=(6, 18))
        date_entry = tk.Entry(date_frame, textvariable=self._date_var,
                              font=("Segoe UI", 11), width=12,
                              relief="flat", bg=C_SURFACE, fg=C_TEXT,
                              insertbackground=C_PRIMARY)
        date_entry.pack(padx=8, pady=5)
        date_entry.bind("<FocusIn>",
            lambda _: date_frame.config(highlightbackground=C_PRIMARY,
                                        highlightthickness=2))
        date_entry.bind("<FocusOut>",
            lambda _: date_frame.config(highlightbackground=C_BORDER,
                                        highlightthickness=1))

        # Ca hoc label + combobox
        tk.Label(ctrl_row, text="🕐  Ca hoc:", bg=C_SURFACE,
                 fg=C_TEXT, font=F_BODY_B).pack(side="left")
        slot_cb = ttk.Combobox(ctrl_row, textvariable=self._slot_var,
                               values=self.SLOT_OPTIONS, state="readonly",
                               width=9, font=("Segoe UI", 11))
        slot_cb.pack(side="left", padx=(6, 18), ipady=4)

        btn(ctrl_row, "Xem phong trong", self._show_available,
            variant="primary", icon="🔍").pack(side="left")

        self._suggest_status = tk.Label(ctrl_row, text="", bg=C_SURFACE,
                                        fg=C_MUTED, font=("Segoe UI", 9, "italic"))
        self._suggest_status.pack(side="left", padx=(14, 0))

        # ── Divider ───────────────────────────────────────────────────────────
        tk.Frame(body, bg=C_BORDER, height=1).pack(fill="x", pady=(0, 10))

        # ── Result treeview (chiều cao cố định 7 dòng) ────────────────────────
        s_cols = ("ma", "ten", "suc_chua", "loai", "thiet_bi")
        s_hdrs = ("Ma phong", "Ten phong", "Suc chua", "Loai phong", "Trang thiet bi")
        s_wids = (110, 180, 90, 160, 280)
        self._suggest_tree = make_tree(body, s_cols, s_hdrs, s_wids, height=7)
        with_scrollbar(body, self._suggest_tree)

    def refresh(self) -> None:
        rows = [(r.room_id, r.name, r.capacity,
                 r.room_type, r.equipment, r.status)
                for r in self.room_ctrl.list_rooms(self.search_var.get())]
        fill_tree(self.tree, rows)

    def _selected_room_id(self) -> str | None:
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _add(self) -> None:
        dlg = RoomDetailDialog(self)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.room_ctrl.save_room(dlg.result)
        except ValueError as err:
            messagebox.showerror("Du lieu khong hop le", str(err))
            return
        self.refresh()

    def _edit(self) -> None:
        rid = self._selected_room_id()
        if rid is None:
            messagebox.showwarning("Chua chon phong", "Hay chon phong can sua.")
            return
        dlg = RoomDetailDialog(self, room=self.room_ctrl.get_room(rid))
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self.room_ctrl.save_room(dlg.result)
        except ValueError as err:
            messagebox.showerror("Du lieu khong hop le", str(err))
            return
        self.refresh()

    def _delete(self) -> None:
        rid = self._selected_room_id()
        if rid is None:
            messagebox.showwarning("Chua chon phong", "Hay chon phong can xoa.")
            return
        if not messagebox.askyesno("Xac nhan xoa", f"Xoa phong {rid}?"):
            return
        self.room_ctrl.delete_room(rid)
        self.refresh()

    def _get_selected_room(self):
        """Return (room_id, room_name) of selected row, or (None, None)."""
        rid = self._selected_room_id()
        if rid is None:
            return None, None
        rooms = {r.room_id: r for r in self.room_ctrl.list_rooms()}
        room = rooms.get(rid)
        name = room.name if room else rid
        return rid, name

    def _rate_room(self) -> None:
        rid, name = self._get_selected_room()
        if rid is None:
            messagebox.showwarning("Chua chon phong", "Hay chon phong can danh gia.")
            return
        if self.feedback_ctrl is None or self.current_user is None:
            messagebox.showwarning("Chua san sang", "Tinh nang chua duoc ket noi.")
            return
        RoomRatingDialog(self, rid, name, self.current_user, self.feedback_ctrl)

    def _report_issue(self) -> None:
        rid, name = self._get_selected_room()
        if rid is None:
            messagebox.showwarning("Chua chon phong", "Hay chon phong can bao loi.")
            return
        if self.feedback_ctrl is None or self.current_user is None:
            messagebox.showwarning("Chua san sang", "Tinh nang chua duoc ket noi.")
            return
        RoomIssueDialog(self, rid, name, self.current_user, self.feedback_ctrl)

    def _show_available(self) -> None:
        if self.booking_ctrl is None:
            messagebox.showwarning("Chua san sang",
                                   "Tinh nang goi y chua duoc ket noi.")
            return
        date_text = self._date_var.get().strip()
        slot = self._slot_var.get()
        try:
            dt.date.fromisoformat(date_text)
        except ValueError:
            messagebox.showerror("Ngay khong hop le",
                                 "Vui long nhap ngay theo dinh dang YYYY-MM-DD.")
            return
        rooms = self.room_ctrl.get_available_rooms(
            self.booking_ctrl, date_text, slot)
        rows = [(r.room_id, r.name, r.capacity, r.room_type, r.equipment)
                for r in rooms]
        fill_tree(self._suggest_tree, rows)
        count = len(rows)
        if count:
            self._suggest_status.config(
                text=f"✅  Tim thay {count} phong trong  |  {date_text}  –  {slot}",
                fg="#16a34a")
        else:
            self._suggest_status.config(
                text=f"⚠️  Khong co phong trong  |  {date_text}  –  {slot}",
                fg="#dc2626")
