# booking_list_gui.py  –  booking list screen
from __future__ import annotations
import csv
import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any
from utils.export_excel import export_rows_to_excel  # type: ignore[import-untyped]
from utils.export_ics import export_bookings_to_ics  # type: ignore[import-untyped]
from gui.theme import (
    F_BODY, F_BODY_B, F_SECTION,
    C_SURFACE, C_BORDER, C_WARNING, C_DANGER, C_SUCCESS,
    C_TEXT, C_MUTED, C_BG, C_PRIMARY,
    make_tree, fill_tree, with_scrollbar,
    page_header, _get_c, btn, search_box,
    toast, confirm_dialog, animate_count
)

from tkcalendar import DateEntry  # type: ignore[import-untyped]


class BookingListFrame(tk.Frame):
    def __init__(self, master: tk.Misc, booking_controller: Any,
                 current_user: Any,
                 room_controller: Any = None) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.booking_ctrl = booking_controller
        self.room_ctrl    = room_controller
        self.current_user = current_user
        self.status_var   = tk.StringVar()
        self.search_var   = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._sort_col: str = ""
        self._sort_rev: bool = False
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Danh sách đặt phòng", "📋").pack(fill="x")

        # ── Stat summary bar ─────────────────────────────────────────────────
        stats_outer = tk.Frame(self, bg=_get_c("BG"))
        stats_outer.pack(fill="x", padx=20, pady=(0, 12))

        self._stat_labels: dict[str, tk.Label] = {}
        stat_defs = [
            ("total",    "📋", "Tổng yêu cầu",   _get_c("INFO_BG"), _get_c("ACCENT")),
            ("pending",  "⏳", "Chờ duyệt",      _get_c("WARNING_BG"), _get_c("WARNING")),
            ("approved", "✅", "Đã duyệt",       _get_c("SUCCESS_BG"), _get_c("SUCCESS")),
            ("rejected", "❌", "Từ chối",        _get_c("DANGER_BG"), _get_c("DANGER")),
        ]
        for key, icon, label, bg, fg in stat_defs:
            chip = tk.Frame(stats_outer, bg=bg, highlightthickness=1,
                            highlightbackground=_get_c("BORDER"), padx=16, pady=10)
            chip.pack(side="left", padx=(0, 8))
            top_f = tk.Frame(chip, bg=bg)
            top_f.pack(anchor="w")
            tk.Label(top_f, text=icon, bg=bg, font=("Segoe UI", 16)).pack(side="left", padx=(0, 6))
            val_lbl = tk.Label(top_f, text="–", bg=bg, fg=fg, font=("Segoe UI", 20, "bold"))
            val_lbl.pack(side="left")
            tk.Label(chip, text=label, bg=bg, fg=_get_c("MUTED"), font=("Segoe UI", 9)).pack(anchor="w")
            self._stat_labels[key] = val_lbl

        self._search_timer: str | None = None
        self.search_var.trace_add("write", lambda *_: self._on_search_change())

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=_get_c("BG"))
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        
        search_box(toolbar, self.search_var, width=28).pack(side="left")
        
        tk.Frame(toolbar, bg=_get_c("BORDER"), width=1).pack(side="left", fill="y", padx=14, pady=4)

        tk.Label(toolbar, text="Trạng thái:", bg=_get_c("BG"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
        status_cb = ttk.Combobox(toolbar, textvariable=self.status_var,
                                 values=["Tất cả", "Cho duyet", "Da duyet", "Tu choi"],
                                 width=12, state="readonly")
        status_cb.pack(side="left")
        if not self.status_var.get(): self.status_var.set("Tất cả")
        status_cb.bind("<<ComboboxSelected>>", lambda _=None: self.refresh())

        # Export actions
        tk.Frame(toolbar, bg=_get_c("BORDER"), width=1).pack(side="left", fill="y", padx=14, pady=4)
        btn(toolbar, "Excel", self._export,
            variant="ghost", icon="📊").pack(side="left", padx=2)
        btn(toolbar, "ICS",   self._export_ics,
            variant="ghost", icon="📅").pack(side="left", padx=2)

        # Admin actions
        if self.current_user.role == "Admin":
            tk.Frame(toolbar, bg=_get_c("BORDER"), width=1).pack(side="left", fill="y", padx=14, pady=4)
            btn(toolbar, "Duyệt",
                lambda: self._set_status("Da duyet"),
                variant="success", icon="✔").pack(side="left", padx=4)
            btn(toolbar, "Từ chối",
                self._reject_booking,
                variant="danger",  icon="✖").pack(side="left", padx=4)

        # Right actions (Delete/Edit)
        btn(toolbar, "Xóa", self._delete_booking,
            variant="danger", icon="🗑").pack(side="right", padx=4)
        btn(toolbar, "Sửa", self._edit_booking,
            variant="outline", icon="✏️").pack(side="right", padx=4)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._COLS = ("ma", "nguoi_dat", "phong", "ngay", "ca", "muc_dich", "trang_thai")
        self._HDRS = ("Ma", "Nguoi dat", "Phong", "Ngay", "Ca", "Muc dich", "Trang thai")
        wids = (90, 150, 90, 110, 80, 240, 120)
        self.tree = make_tree(wrap, self._COLS, self._HDRS, wids)
        with_scrollbar(wrap, self.tree)

        # Sortable headers
        self._make_sortable(self.tree, list(self._COLS))

        # Double-click to edit
        self.tree.bind("<Double-1>", lambda _=None: self._edit_booking())

    def _make_sortable(self, tree: ttk.Treeview, columns: list[str]) -> None:
        """Make all column headers sortable on click; shows ▲/▼ indicator."""
        for col in columns:
            tree.heading(col, command=lambda c=col: self._sort_by(c))

    def _sort_by(self, col: str) -> None:
        assert self.tree is not None
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda t: float(t[0]), reverse=self._sort_rev)
        except (ValueError, TypeError):
            items.sort(key=lambda t: str(t[0] or "").lower(), reverse=self._sort_rev)
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
        arrow = " ▲" if not self._sort_rev else " ▼"
        for c, h in zip(self._COLS, self._HDRS):
            self.tree.heading(c, text=h + (arrow if c == col else ""))

    def _on_search_change(self) -> None:
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(300, self.refresh)

    def refresh(self) -> None:
        q = self.search_var.get().strip().lower()
        st_filter = self.status_var.get().strip()
        if st_filter == "Tất cả": st_filter = ""
        
        # Get all bookings for stats
        all_bookings = self.booking_ctrl.list_bookings(
            current_user=self.current_user,
            status="",
            from_today=False)
            
        # Get filtered bookings for treeview
        bookings = [b for b in all_bookings 
                   if (not st_filter or b.status == st_filter)]
        
        self._last_bookings = bookings  # keep for ICS export
        all_rows = [
            (b.booking_id, b.user_name, b.room_id,
             b.booking_date, b.slot, b.purpose, b.status,
             getattr(b, "rejection_reason", "") or "")
            for b in bookings
        ]
        if q:
            all_rows = [
                r for r in all_rows
                if q in str(r[1]).lower()   # user_name
                or q in str(r[2]).lower()   # room_id
                or q in str(r[5]).lower()   # purpose
                or q in str(r[0]).lower()   # booking_id
            ]
        assert self.tree is not None
        self.tree.delete(*self.tree.get_children())
        STATUS_TAG = {"Da duyet": "duyet", "Cho duyet": "cho", "Tu choi": "tuchoi"}
        for row in all_rows:
            tag = STATUS_TAG.get(str(row[6]), "")
            self.tree.insert("", "end", values=row, tags=(tag,) if tag else ())
            
        # Update Stats with animation
        total = len(all_bookings)
        pending = sum(1 for b in all_bookings if b.status == "Cho duyet")
        approved = sum(1 for b in all_bookings if b.status == "Da duyet")
        rejected = sum(1 for b in all_bookings if b.status == "Tu choi")
        
        for key, val in [("total", total), ("pending", pending), ("approved", approved), ("rejected", rejected)]:
            if key in self._stat_labels:
                animate_count(self._stat_labels[key], val)

    def _selected_id(self) -> str | None:
        assert self.tree is not None
        sel = self.tree.selection()
        return str(self.tree.item(sel[0], "values")[0]) if sel else None

    def _set_status(self, new_status: str) -> None:
        bid = self._selected_id()
        if bid is None:
            messagebox.showwarning("Chua chon yeu cau", "Hay chon mot ban ghi.")
            return
        self.booking_ctrl.update_status(bid, new_status)
        self.refresh()
        kind = "success" if new_status == "Da duyet" else "error"
        toast(self, f"Da cap nhat trang thai: {new_status}", kind=kind)

    def _reject_booking(self) -> None:
        bid = self._selected_id()
        if bid is None:
            messagebox.showwarning("Chua chon yeu cau", "Hay chon mot ban ghi.")
            return
        reason = self._ask_reject_reason()
        if reason is None:
            return
        self.booking_ctrl.reject_booking(bid, reason=reason)
        self.refresh()
        toast(self, "Da tu choi va luu ly do", kind="error")

    def _ask_reject_reason(self) -> str | None:
        dlg = tk.Toplevel(self)
        dlg.title("Ly do tu choi")
        dlg.configure(bg=C_BG)
        dlg.configure(bg=_get_c("BG"))
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        result: list[str] = []

        tk.Label(dlg, text="Nhap ly do tu choi:", bg=_get_c("BG"), fg=_get_c("TEXT"), font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        text_area = tk.Text(dlg, width=40, height=4, font=("Segoe UI", 9), relief="solid", bd=1)
        text_area.pack(padx=20, pady=5)
        text_area.focus()

        def _ok():
            val = text_area.get("1.0", "end").strip()
            if not val:
                messagebox.showwarning("Canh bao", "Vui long nhap ly do tu choi.", parent=dlg)
                return
            result.append(val)
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=C_BG)
        btn_row.pack(fill="x", padx=20, pady=(10, 15))
        btn(btn_row, "Xac nhan", _ok, variant="danger").pack(side="left")
        btn(btn_row, "Huy bo", dlg.destroy, variant="secondary").pack(side="left", padx=(8, 0))

        dlg.wait_window()
        return result[0] if result else None



    def _export(self) -> None:
        assert self.tree is not None
        rows = [list(self.tree.item(item, "values"))
                for item in self.tree.get_children()]
        if not rows:
            messagebox.showinfo("Khong co du lieu", "Khong co ban ghi de xuat.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx")],
            initialfile=f"DanhSachDat_{dt.date.today()}.xlsx")
        if not path:
            return
        export_rows_to_excel(
            headers=["Ma", "Nguoi dat", "Phong", "Ngay", "Ca",
                     "Muc dich", "Trang thai"],
            rows=rows, output_path=path)
        messagebox.showinfo("Thanh cong", "Da xuat file Excel.")

    def _export_ics(self) -> None:
        bookings = getattr(self, "_last_bookings", None)
        if not bookings:
            messagebox.showinfo("Khong co du lieu", "Khong co lich dat de xuat.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar file", "*.ics")],
            initialfile=f"LichDatPhong_{dt.date.today()}.ics")
        if not path:
            return
        try:
            export_bookings_to_ics(bookings, path)
            messagebox.showinfo("Thanh cong", "Da xuat file ICS.\n"
                                "Ban co the mo bang Google Calendar, Outlook...")
        except OSError as e:
            messagebox.showerror("Loi", str(e))

    def _export_csv(self) -> None:
        assert self.tree is not None
        rows = [list(self.tree.item(item, "values"))
                for item in self.tree.get_children()]
        if not rows:
            messagebox.showinfo("Khong co du lieu", "Khong co ban ghi de xuat.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile=f"DanhSachDat_{dt.date.today()}.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Ma", "Nguoi dat", "Phong", "Ngay", "Ca",
                                  "Muc dich", "Trang thai"])
                writer.writerows(rows)
            messagebox.showinfo("Thanh cong", "Da xuat file CSV.")
        except OSError as e:
            messagebox.showerror("Loi", str(e))

    def _delete_booking(self) -> None:
        bid = self._selected_id()
        if bid is None:
            messagebox.showwarning("Chua chon", "Hay chon mot ban ghi.")
            return
        if not confirm_dialog(self, "Xac nhan xoa",
                              f"Ban chac chan muon xoa lich [{bid}]?\n"
                              "Thao tac nay khong the hoan tac.",
                              ok_text="Xoa", kind="danger"):
            return
        try:
            self.booking_ctrl.delete_booking(bid, self.current_user)
            self.refresh()
            toast(self, "Da xoa lich dat phong.", kind="success")
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Loi", str(e))

    def _edit_booking(self) -> None:
        bid = self._selected_id()
        if bid is None:
            messagebox.showwarning("Chua chon", "Hay chon mot ban ghi.")
            return
        booking = self.booking_ctrl.get_booking(bid)
        if booking is None:
            messagebox.showerror("Loi", "Khong tim thay ban ghi.")
            return
        if (self.current_user.role != "Admin"
                and booking.user_id != self.current_user.user_id):
            messagebox.showerror("Khong co quyen", "Ban chi co the sua lich cua chinh minh.")
            return
        _EditBookingDialog(self, booking, self.booking_ctrl,
                           self.room_ctrl, self.current_user,
                           on_done=self.refresh)


class _EditBookingDialog(tk.Toplevel):
    """Modal dialog to edit an existing booking."""

    def __init__(self, parent: tk.Misc, booking: Any, booking_ctrl: Any,
                 room_ctrl: Any, current_user: Any, on_done: Any = None):
        super().__init__(parent)
        self.title("Sua lich dat phong")
        self.resizable(False, False)
        self.grab_set()
        self.booking    = booking
        self.booking_ctrl = booking_ctrl
        self.room_ctrl  = room_ctrl
        self.current_user = current_user
        self.on_done    = on_done

        from gui.theme import C_BG, F_INPUT, btn as theme_btn # type: ignore

        self.configure(bg=C_BG)

        tk.Label(self, text="Sua lich dat phong", bg=C_BG,
                 font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(16, 8))

        def lbl(row: int, text: str) -> None:
            tk.Label(self, text=text, bg=C_BG,
                     font=("Segoe UI", 9, "bold"), anchor="w").grid(
                row=row, column=0, sticky="w", padx=20, pady=(8, 0))

        # Room
        lbl(1, "PHONG HOC")
        rooms: list[Any] = room_ctrl.list_rooms() if room_ctrl else []
        room_values = [f"{r.room_id} – {r.name}" for r in rooms if r.status == "Hoat dong"]
        self._room_map: dict[str, Any] = {f"{r.room_id} – {r.name}": r.room_id for r in rooms}
        self.room_var = tk.StringVar(value=next(
            (k for k, v in self._room_map.items() if v == booking.room_id), booking.room_id))
        ttk.Combobox(self, textvariable=self.room_var,
                     values=room_values, state="readonly", width=34).grid(
            row=2, column=0, columnspan=2, padx=20, pady=6)

        # Date
        lbl(3, "NGAY DAT (YYYY-MM-DD)")
        self.date_var = tk.StringVar(value=booking.booking_date)
        de = DateEntry(self, textvariable=self.date_var, width=34,  # type: ignore[possibly-unbound]
                       date_pattern="yyyy-mm-dd", background="#4f46e5",
                       foreground="white", weekendbackground="white",
                       weekendforeground="black",
                       state="readonly",
                       borderwidth=1,
                       font=("Segoe UI", 10))
        de.grid(row=4, column=0, columnspan=2, padx=20, pady=6)  # type: ignore[attr-defined]

        # Slot
        lbl(5, "CA HOC")
        self.slot_var = tk.StringVar(value=booking.slot)
        ttk.Combobox(self, textvariable=self.slot_var,
                     values=booking_ctrl.SLOT_OPTIONS,
                     state="readonly", width=34).grid(
            row=6, column=0, columnspan=2, padx=20, pady=6)

        # Purpose
        lbl(7, "MUC DICH SU DUNG")
        self.purpose_text = tk.Text(self, width=38, height=4,
                                    relief="solid", bd=1,
                                    font=("Segoe UI", 10))
        self.purpose_text.insert("1.0", booking.purpose)
        self.purpose_text.grid(row=8, column=0, columnspan=2, padx=20, pady=6)

        # Buttons
        btn_f = tk.Frame(self, bg=C_BG)
        btn_f.grid(row=9, column=0, columnspan=2, pady=16)
        theme_btn(btn_f, "Luu thay doi", self._save).pack(side="left", padx=6)
        theme_btn(btn_f, "Huy", self.destroy, variant="ghost").pack(side="left", padx=6)

    def _save(self) -> None:
        room_display = self.room_var.get()
        room_id = self._room_map.get(room_display, room_display.split(" – ")[0])
        date    = self.date_var.get().strip()
        slot    = self.slot_var.get()
        purpose = self.purpose_text.get("1.0", "end-1c").strip()
        try:
            self.booking_ctrl.update_booking(
                self.booking.booking_id, self.current_user,
                room_id, date, slot, purpose)
            if self.on_done:
                self.on_done()
            messagebox.showinfo("Thanh cong", "Da cap nhat lich dat phong.")
            self.destroy()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Loi", str(e))
