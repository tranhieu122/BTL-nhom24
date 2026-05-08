# room_gui.py  –  room management screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from tkcalendar import DateEntry  # type: ignore[import-untyped]
from gui.room_detail_gui import RoomDetailDialog
from gui.room_feedback_gui import RoomRatingDialog, RoomIssueDialog
from gui.theme import (_get_c, FONT_H3, FONT_BODY, FONT_CAPTION,
                       GlassCard, GlowButton, PillBadge, custom_dialog,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box,
                       toast, confirm_dialog, alert, ask)


class RoomManagementFrame(tk.Frame):
    SLOT_OPTIONS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]

    def __init__(self, master: tk.Misc, room_controller: Any, booking_controller: Any = None,
                 feedback_ctrl: Any = None, current_user: Any = None) -> None:
        super().__init__(master, bg=_get_c("BG"))
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
        # GlassCard header
        header_card = GlassCard(self)
        header_card.pack(fill="x", padx=20, pady=(20, 12))

        tk.Label(header_card, text="🏫 Quản lý phòng học", bg=_get_c("SURFACE"),
                 fg=_get_c("TEXT"), font=FONT_H3).pack(anchor="w", pady=(16, 8), padx=20)

        # ── Stat summary bar ─────────────────────────────────────────────────
        stats_outer = tk.Frame(header_card, bg=_get_c("SURFACE"))
        stats_outer.pack(fill="x", padx=20, pady=(0, 16))

        self._stat_labels: dict[str, tk.Label] = {}
        stat_defs = [
            ("total",    "🏫", "Tổng số phòng",   _get_c("INFO_BG"), _get_c("ACCENT")),
            ("active",   "🟢", "Đang hoạt động",  _get_c("SUCCESS_BG"), _get_c("SUCCESS")),
            ("maintain", "🟡", "Đang bảo trì",    _get_c("WARNING_BG"), _get_c("WARNING")),
            ("off",      "🔴", "Ngừng sử dụng",   _get_c("DANGER_BG"), _get_c("DANGER")),
        ]
        for key, icon, label, bg, fg in stat_defs:
            chip = PillBadge(stats_outer, f"{icon} –", color="neutral")
            chip.pack(side="left", padx=(0, 8))
            val_lbl = tk.Label(chip, text="–", bg=bg, fg=fg, font=("Inter", 16, "bold"))
            val_lbl.pack(side="left", padx=(4, 0))
            tk.Label(chip, text=f" {label}", bg=bg, fg=fg, font=("Inter", 10)).pack(side="left")
            self._stat_labels[key] = val_lbl

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=_get_c("BG"))
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Search box with live search
        search_frame = tk.Frame(toolbar, bg=_get_c("BORDER"), padx=1, pady=1)
        search_frame.pack(side="left", pady=8)
        inner_search = tk.Frame(search_frame, bg=_get_c("SURFACE"))
        inner_search.pack(fill="both", expand=True)
        tk.Label(inner_search, text="🔍", bg=_get_c("SURFACE"), font=("Inter", 12)).pack(side="left", padx=(8, 2))
        search_entry = tk.Entry(inner_search, textvariable=self.search_var,
                               bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                               font=FONT_BODY, relief="flat", width=20,
                               insertbackground=_get_c("ACCENT"))
        search_entry.pack(side="left", padx=(0, 8), pady=6)
        search_entry.insert(0, "Tìm phòng...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end") if self.search_var.get() == "Tìm phòng..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Tìm phòng...") if not self.search_var.get() else None)

        self._search_timer: str | None = None
        self.search_var.trace_add("write", lambda *_: self._on_search_change())

        # Action buttons
        is_admin = (self.current_user is not None
                    and getattr(self.current_user, "role", "") == "Admin")
        if is_admin:
            tk.Frame(toolbar, bg=_get_c("BORDER"), width=1).pack(side="left", fill="y", padx=12, pady=4)
            GlowButton(toolbar, "Thêm phòng", self._add, style="primary").pack(side="left", padx=4)
            GlowButton(toolbar, "Sửa", self._edit, style="ghost").pack(side="left", padx=4)
            GlowButton(toolbar, "Xóa", self._delete, style="danger").pack(side="left", padx=4)

        # Feedback buttons (visible to all users)
        tk.Frame(toolbar, bg=_get_c("BORDER"), width=1).pack(side="left", fill="y", padx=12, pady=4)
        GlowButton(toolbar, "Đánh giá", self._rate_room, style="primary").pack(side="left", padx=4)
        GlowButton(toolbar, "Báo lỗi", self._report_issue, style="ghost").pack(side="left", padx=4)

        # Data table in GlassCard
        table_card = GlassCard(self)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "ten", "suc_chua", "loai", "thiet_bi", "danh_gia", "trang_thai")
        hdrs = ("Mã phòng", "Tên phòng", "Sức chứa", "Loại phòng",
                "Trang thiết bị", "Đánh giá", "Trạng thái")
        wids = (100, 160, 90, 140, 260, 90, 110)
        self.tree = make_tree(table_card, cols, hdrs, wids)
        with_scrollbar(table_card, self.tree)

        # Color tags for room status
        self.tree.tag_configure("hoat_dong",  background=_get_c("EMERALD_100"), foreground=_get_c("EMERALD_800"))
        self.tree.tag_configure("bao_tri",    background=_get_c("AMBER_100"), foreground=_get_c("AMBER_800"))
        self.tree.tag_configure("ngung_su",   background=_get_c("ROSE_100"), foreground=_get_c("ROSE_800"))

        # ── Panel gợi ý phòng còn trống ─────────────────────────────────────
        suggest_card = GlassCard(self)
        suggest_card.pack(fill="x", padx=20, pady=(0, 20))

        # Header bar with accent
        header_bar = tk.Frame(suggest_card, bg=_get_c("INDIGO_500"), pady=0)
        header_bar.pack(fill="x")

        tk.Frame(header_bar, bg=_get_c("INDIGO_400"), height=3).pack(fill="x")

        header_content = tk.Frame(header_bar, bg=_get_c("INDIGO_500"), padx=20, pady=12)
        header_content.pack(fill="x")
        tk.Label(header_content, text="💡", bg=_get_c("INDIGO_500"), fg="white",
                 font=("Inter", 15)).pack(side="left")
        tk.Label(header_content, text="  Gợi ý phòng còn trống",
                 bg=_get_c("INDIGO_500"), fg="white",
                 font=("Inter", 13, "bold")).pack(side="left")
        tk.Label(header_content,
                 text="Chọn ngày và ca học để tìm phòng trống nhanh",
                 bg=_get_c("INDIGO_500"), fg=_get_c("INDIGO_200"),
                 font=("Inter", 9)).pack(side="right")

        # Body
        body = tk.Frame(suggest_card, bg=_get_c("SLATE_800"), padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # ── Controls row ──────────────────────────────────────────────────────
        ctrl_row = tk.Frame(body, bg=_get_c("SLATE_800"))
        ctrl_row.pack(fill="x", pady=(0, 12))

        # Ngay label + entry
        tk.Label(ctrl_row, text="📅  Ngày:", bg=_get_c("SLATE_800"),
                 fg=_get_c("SLATE_100"), font=FONT_BODY).pack(side="left")

        date_entry = DateEntry(  # type: ignore[possibly-unbound]
            ctrl_row, textvariable=self._date_var,
            width=12, date_pattern="yyyy-mm-dd",
            background=_get_c("INDIGO_500"), foreground="white",
            state="readonly", font=("Inter", 11),
        )
        date_entry.pack(side="left", padx=(6, 18), ipady=2)
        date_entry.bind("<<DateEntrySelected>>", lambda _=None: self._show_available())

        # Ca hoc label + combobox
        tk.Label(ctrl_row, text="🕐  Ca học:", bg=_get_c("SLATE_800"),
                 fg=_get_c("SLATE_100"), font=FONT_BODY).pack(side="left")
        slot_cb = ttk.Combobox(ctrl_row, textvariable=self._slot_var,
                               values=self.SLOT_OPTIONS, state="readonly",
                               width=9, font=("Inter", 11))
        slot_cb.pack(side="left", padx=(6, 18), ipady=4)
        slot_cb.bind("<<ComboboxSelected>>", lambda _=None: self._show_available())

        self._suggest_status = tk.Label(ctrl_row, text="", bg=_get_c("SLATE_800"),
                                        fg=_get_c("SLATE_400"), font=("Inter", 9, "italic"))
        self._suggest_status.pack(side="left", padx=(14, 0))

        # ── Divider ───────────────────────────────────────────────────────────
        tk.Frame(body, bg=_get_c("SLATE_600"), height=1).pack(fill="x", pady=(0, 10))

        # ── Result treeview (chiều cao cố định 7 dòng) ────────────────────────
        s_cols = ("ma", "ten", "suc_chua", "loai", "thiet_bi")
        s_hdrs = ("Mã phòng", "Tên phòng", "Sức chứa", "Loại phòng", "Trang thiết bị")
        s_wids = (110, 180, 90, 160, 280)
        self._suggest_tree = make_tree(body, s_cols, s_hdrs, s_wids, height=7)
        with_scrollbar(body, self._suggest_tree)

    def _on_search_change(self) -> None:
        """Debounced search: wait 300ms after last keystroke before refreshing."""
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(300, self.refresh)

    def refresh(self) -> None:
        assert self.tree is not None
        self.tree.delete(*self.tree.get_children())
        
        search_val = self.search_var.get().strip()
        q = search_val if search_val != "Tìm phòng..." else ""
        filtered_rooms = self.room_ctrl.list_rooms(keyword=q)
        all_rooms = self.room_ctrl.list_rooms("") # For stats
        
        STATUS_ICON = {
            "Hoat dong": "🟢 Hoat dong",
            "Bao tri":   "🟡 Bao tri",
            "Ngung su dung": "🔴 Ngung su dung",
        }
        STATUS_TAG = {
            "Hoat dong":    "hoat_dong",
            "Bao tri":      "bao_tri",
            "Ngung su dung": "ngung_su",
        }

        for r in filtered_rooms:
            rating = "N/A"
            if self.feedback_ctrl:
                avg = self.feedback_ctrl.rating_dao.average_stars(r.room_id)
                rating = f"{avg} ⭐" if avg > 0 else "Chua co"
            status_display = STATUS_ICON.get(r.status, r.status)
            tag = STATUS_TAG.get(r.status, "")
            self.tree.insert("", "end",
                             values=(r.room_id, r.name, r.capacity,
                                     r.room_type, r.equipment,
                                     rating, status_display),
                             tags=(tag,) if tag else ())
        
        # Update Stats with animation
        from gui.theme import animate_count
        total = len(all_rooms)
        active = sum(1 for r in all_rooms if r.status == "Hoat dong")
        maintain = sum(1 for r in all_rooms if r.status == "Bao tri")
        off = sum(1 for r in all_rooms if r.status == "Ngung su dung")
        
        for key, val in [("total", total), ("active", active), ("maintain", maintain), ("off", off)]:
            if key in self._stat_labels:
                animate_count(self._stat_labels[key], val)

    def _selected_room_id(self) -> str | None:
        assert self.tree is not None
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
        toast(self, "Da them phong hoc moi.", kind="success")

    def _edit(self) -> None:
        rid = self._selected_room_id()
        if rid is None:
            alert(self, "Chua chon phong", "Hay chon phong can sua.", kind="warning")
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
        toast(self, "Da cap nhat thong tin phong.", kind="success")

    def _delete(self) -> None:
        rid = self._selected_room_id()
        if rid is None:
            alert(self, "Chua chon phong", "Hay chon phong can xoa.", kind="warning")
            return
        if not ask(self, "Xac nhan xoa phong",
                              f"Ban chac chan muon xoa phong {rid}?\n"
                              "Du lieu lien quan se bi anh huong.",
                              kind="danger"):
            return
        self.room_ctrl.delete_room(rid)
        self.refresh()
        toast(self, f"Da xoa phong {rid}.", kind="success")

    def _get_selected_room(self) -> tuple[str | None, str | None]:
        """Return (room_id, room_name) of selected row, or (None, None)."""
        rid = self._selected_room_id()
        if rid is None:
            return None, None
        rooms: dict[str, Any] = {r.room_id: r for r in self.room_ctrl.list_rooms()}
        room = rooms.get(rid)
        name: str = str(room.name) if room else rid
        return rid, name

    def _rate_room(self) -> None:
        rid, name = self._get_selected_room()
        if rid is None:
            alert(self, "Chua chon phong", "Hay chon phong can danh gia.", kind="warning")
            return
        assert name is not None
        if self.feedback_ctrl is None or self.current_user is None:
            alert(self, "Chua san sang", "Tinh nang chua duoc ket noi.", kind="warning")
            return
        RoomRatingDialog(self, rid, name, self.current_user, self.feedback_ctrl)

    def _report_issue(self) -> None:
        rid, name = self._get_selected_room()
        if rid is None:
            alert(self, "Chua chon phong", "Hay chon phong can bao loi.", kind="warning")
            return
        assert name is not None
        if self.feedback_ctrl is None or self.current_user is None:
            alert(self, "Chua san sang", "Tinh nang chua duoc ket noi.", kind="warning")
            return
        RoomIssueDialog(self, rid, name, self.current_user, self.feedback_ctrl)

    def _show_available(self) -> None:
        if self.booking_ctrl is None:
            alert(self, "Chua san sang",
                                   "Tinh nang goi y chua duoc ket noi.", kind="warning")
            return
        date_text = self._date_var.get().strip()
        slot = self._slot_var.get()
        try:
            dt.date.fromisoformat(date_text)
        except ValueError:
            alert(self, "Ngay khong hop le",
                                 "Vui long nhap ngay theo dinh dang YYYY-MM-DD.", kind="error")
            return
        rooms = self.room_ctrl.get_available_rooms(
            self.booking_ctrl, date_text, slot)
        rows = [(r.room_id, r.name, r.capacity, r.room_type, r.equipment)
                for r in rooms]
        assert self._suggest_tree is not None
        fill_tree(self._suggest_tree, rows)
        count = len(rows)
        if count:
            self._suggest_status.config(
                text=f"✅  Tim thay {count} phong trong  |  {date_text}  –  {slot}",
                fg="#16a34a")
        else:
            self._suggest_status.config(
                text=f"⚠️  Khong co phong trong  |  {date_text}  –  {slot}",
                fg="#db2777")
