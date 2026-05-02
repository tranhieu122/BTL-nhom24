# booking_list_gui.py  –  booking list screen
from __future__ import annotations
import csv
import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any
from utils.export_excel import export_rows_to_excel  # type: ignore[import-untyped]
from gui.theme import (C_BG, C_SURFACE, C_BORDER, C_MUTED,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box,
                       toast, confirm_dialog)

_has_calendar = False
try:
    from tkcalendar import DateEntry  # type: ignore[import-untyped]
    _has_calendar = True
except ImportError:
    pass


class BookingListFrame(tk.Frame):
    def __init__(self, master: tk.Misc, booking_controller: Any,
                 current_user: Any,
                 room_controller: Any = None) -> None:
        super().__init__(master, bg=C_BG)
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
        page_header(self, "Danh sach dat phong", "📋").pack(fill="x")

        # ── Search bar ───────────────────────────────────────────────────────
        search_bar = tk.Frame(self, bg=C_BG)
        search_bar.pack(fill="x", padx=20, pady=(0, 4))
        tk.Label(search_bar, text="Tim kiem:", bg=C_BG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 6))
        search_box(search_bar, self.search_var, width=26,
                   command=self.refresh).pack(side="left")
        btn(search_bar, "Tim", self.refresh,
            variant="primary", icon="🔍").pack(side="left", padx=6)
        tk.Label(search_bar, text="(Tim theo ten nguoi dat, ma phong, muc dich)",
                 bg=C_BG, fg=C_MUTED, font=("Segoe UI", 8)).pack(
            side="left", padx=4)

        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(toolbar, text="Trang thai:", bg=C_BG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))
        ttk.Combobox(toolbar, textvariable=self.status_var,
                     values=["", "Cho duyet", "Da duyet", "Tu choi"],
                     width=14, state="readonly").pack(side="left")
        btn(toolbar, "Loc", self.refresh,
            variant="ghost", icon="🔍").pack(side="left", padx=(8, 0))
        btn(toolbar, "Xuat Excel", self._export,
            variant="ghost", icon="📊").pack(side="left", padx=6)
        if self.current_user.role in ("Admin", "Giang vien"):
            btn(toolbar, "Xuat CSV", self._export_csv,
                variant="ghost", icon="📎").pack(side="left", padx=4)

        # Sửa lịch – chủ lịch hoặc Admin
        btn(toolbar, "Sua lich", self._edit_booking,
            variant="outline", icon="✏️").pack(side="left", padx=4)
        # Xóa lịch – chủ lịch hoặc Admin
        btn(toolbar, "Xoa lich", self._delete_booking,
            variant="danger", icon="🗑").pack(side="left", padx=4)

        if self.current_user.role == "Admin":
            btn(toolbar, "Duyet",
                lambda: self._set_status("Da duyet"),
                variant="success", icon="✔").pack(side="left", padx=4)
            btn(toolbar, "Tu choi",
                lambda: self._set_status("Tu choi"),
                variant="danger",  icon="✖").pack(side="left", padx=4)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("ma", "nguoi_dat", "phong", "ngay", "ca", "muc_dich", "trang_thai")
        hdrs = ("Ma", "Nguoi dat", "Phong", "Ngay", "Ca", "Muc dich", "Trang thai")
        wids = (90, 150, 90, 110, 80, 240, 120)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # Sortable headers
        self._make_sortable(self.tree, list(cols))

        # Double-click to edit
        self.tree.bind("<Double-1>", lambda _: self._edit_booking())

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
        except ValueError:
            items.sort(key=lambda t: t[0].lower(), reverse=self._sort_rev)
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
        arrow = " ▲" if not self._sort_rev else " ▼"
        # Reset all headers then set arrow on active column
        cols = ("ma", "nguoi_dat", "phong", "ngay", "ca", "muc_dich", "trang_thai")
        hdrs = ("Ma", "Nguoi dat", "Phong", "Ngay", "Ca", "Muc dich", "Trang thai")
        for c, h in zip(cols, hdrs):
            lbl = h + (arrow if c == col else "")
            self.tree.heading(c, text=lbl)

    def refresh(self) -> None:
        q = self.search_var.get().strip().lower()
        all_rows = [
            (b.booking_id, b.user_name, b.room_id,
             b.booking_date, b.slot, b.purpose, b.status)
            for b in self.booking_ctrl.list_bookings(
                current_user=self.current_user,
                status=self.status_var.get().strip(),
                from_today=False)
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
        fill_tree(self.tree, all_rows)

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

        from gui.theme import C_BG, F_INPUT, btn as theme_btn

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
        if _has_calendar:
            de = DateEntry(self, textvariable=self.date_var, width=34,  # type: ignore[possibly-unbound]
                           date_pattern="yyyy-mm-dd", background="#4f46e5",
                           foreground="white", borderwidth=1,
                           font=("Segoe UI", 10))
            de.grid(row=4, column=0, columnspan=2, padx=20, pady=6)  # type: ignore[attr-defined]
        else:
            tk.Entry(self, textvariable=self.date_var, width=36,
                     font=F_INPUT, relief="solid", bd=1).grid(
                row=4, column=0, columnspan=2, padx=20, pady=6)

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
