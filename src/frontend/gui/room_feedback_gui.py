# room_feedback_gui.py – dialogs and admin page for room ratings & issue reports
from __future__ import annotations
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, cast
from gui.theme import (F_BODY, F_BODY_B, F_SECTION, F_SMALL, _get_c,
                       make_tree, fill_tree, with_scrollbar,
                       page_header, btn, search_box, toast)


# ─────────────────────────────────────────────────────────────────────────────
# RoomRatingDialog – mọi người dùng đều có thể đánh giá phòng
# ─────────────────────────────────────────────────────────────────────────────

class RoomRatingDialog(tk.Toplevel):
    """Modal: chọn số sao (1-5) và nhập nhận xét cho một phòng."""

    def __init__(self, parent: tk.Misc, room_id: str, room_name: str,
                 current_user: Any, feedback_ctrl: Any,
                 on_done: Any = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.title(f"Đánh giá phòng – {room_name}")
        self.resizable(False, False)
        self.grab_set()
        self.room_id        = room_id
        self.current_user   = current_user
        self.feedback_ctrl  = feedback_ctrl
        self.on_done        = on_done
        self._stars         = tk.IntVar(value=0)
        self.configure(bg=_get_c("BG"))
        self._build(room_name)

    def _build(self, room_name: str) -> None:
        tk.Label(self, text=f"Đánh giá phòng  {room_name}", bg=_get_c("BG"),
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 4))

        tk.Label(self, text="Chon so sao:", bg=_get_c("BG"),
                 font=F_BODY_B).pack(anchor="w", padx=20, pady=6)

        # ── star buttons ──────────────────────────────────────────────────────
        star_row = tk.Frame(self, bg=_get_c("BG"))
        star_row.pack(pady=(0, 4))
        self._star_btns: list[tk.Label] = []
        for i in range(1, 6):
            lbl = tk.Label(star_row, text="☆", bg=_get_c("BG"),
                           font=("Segoe UI", 28), cursor="hand2", fg="#fbbf24")
            lbl.pack(side="left", padx=2)
            lbl.bind("<Button-1>", lambda e=None, v=i: self._set_stars(v))
            lbl.bind("<Enter>",    lambda e=None, v=i: self._hover_stars(v))
            lbl.bind("<Leave>",    lambda e=None: self._render_stars(self._stars.get()))
            self._star_btns.append(lbl)

        self._rating_label = tk.Label(self, text="Chưa chọn sao", bg=_get_c("BG"),
                                      fg=_get_c("MUTED"), font=F_BODY)
        self._rating_label.pack(pady=(0, 6))

        # ── comment ───────────────────────────────────────────────────────────
        tk.Label(self, text="Nhan xet (tuy chon):", bg=_get_c("BG"),
                 font=F_BODY_B).pack(anchor="w", padx=20, pady=6)
        self._comment = tk.Text(self, width=40, height=4, font=("Segoe UI", 10),
                                relief="solid", bd=1, wrap="word")
        self._comment.pack(padx=20, pady=(0, 10))

        # ── existing rating ───────────────────────────────────────────────────
        existing = self.feedback_ctrl.get_user_rating(
            self.room_id, self.current_user.user_id)
        if existing:
            self._set_stars(existing.stars)
            self._comment.insert("1.0", existing.comment)
            tk.Label(self, text="(Bạn đã đánh giá phòng này trước đó)",
                     bg=_get_c("BG"), fg=_get_c("MUTED"), font=("Segoe UI", 8)).pack()

        # ── buttons ───────────────────────────────────────────────────────────
        bf = tk.Frame(self, bg=_get_c("BG"))
        bf.pack(pady=(6, 18))
        btn(bf, "Gui danh gia", self._submit,
            variant="primary", icon="⭐").pack(side="left", padx=6)
        btn(bf, "Huy", self.destroy,
            variant="ghost").pack(side="left", padx=6)

    # ── internal helpers ──────────────────────────────────────────────────────

    def _set_stars(self, v: int) -> None:
        self._stars.set(v)
        self._render_stars(v)
        self._update_rating_label(v)

    def _hover_stars(self, v: int) -> None:
        self._render_stars(v)
        self._update_rating_label(v)

    def _render_stars(self, n: int) -> None:
        for i, lbl in enumerate(self._star_btns):
            lbl.config(text="★" if i < n else "☆")

    def _update_rating_label(self, stars: int) -> None:
        labels = ["", "Rất tệ", "Tệ", "Bình thường", "Tốt", "Rất tốt"]
        self._rating_label.config(text=labels[stars] if stars > 0 else "Chưa chọn sao")

    def _submit(self) -> None:
        stars = self._stars.get()
        if stars == 0:
            messagebox.showwarning("Chua chon sao", "Vui long chon so sao (1-5).",
                                   parent=self)
            return
        comment = self._comment.get("1.0", "end-1c").strip()
        try:
            self.feedback_ctrl.add_rating(
                self.room_id, self.current_user, stars, comment)
            messagebox.showinfo("Thanh cong", "Cam on ban da danh gia phong!",
                                parent=self)
            if self.on_done:
                self.on_done()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Loi", str(e), parent=self)


# ─────────────────────────────────────────────────────────────────────────────
# RoomIssueDialog – mọi người dùng đều có thể báo lỗi phòng
# ─────────────────────────────────────────────────────────────────────────────

class RoomIssueDialog(tk.Toplevel):
    """Modal: nhập mô tả sự cố/lỗi của một phòng."""

    def __init__(self, parent: tk.Misc, room_id: str, room_name: str,
                 current_user: Any, feedback_ctrl: Any,
                 on_done: Any = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.title(f"Báo lỗi phòng – {room_name}")
        self.resizable(False, False)
        self.grab_set()
        self.room_id       = room_id
        self.current_user  = current_user
        self.feedback_ctrl = feedback_ctrl
        self.on_done       = on_done
        self.configure(bg=_get_c("BG"))
        self._build(room_name)

    def _build(self, room_name: str) -> None:
        tk.Label(self, text=f"Báo lỗi phòng  {room_name}", bg=_get_c("BG"),
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 4))

        tk.Label(self, text="Mo ta su co / loi:", bg=_get_c("BG"),
                 font=F_BODY_B).pack(anchor="w", padx=20, pady=6)
        self._desc = tk.Text(self, width=44, height=5, font=("Segoe UI", 10),
                             relief="solid", bd=1, wrap="word")
        self._desc.pack(padx=20, pady=(0, 10))

        tk.Label(self,
                 text="Bao cao se duoc gui toi Admin de xu ly.",
                 bg=_get_c("BG"), fg=_get_c("MUTED"), font=("Segoe UI", 9)).pack()

        bf = tk.Frame(self, bg=_get_c("BG"))
        bf.pack(pady=(8, 18))
        btn(bf, "Gui bao cao", self._submit,
            variant="danger", icon="🚨").pack(side="left", padx=6)
        btn(bf, "Huy", self.destroy,
            variant="ghost").pack(side="left", padx=6)

    def _submit(self) -> None:
        desc = self._desc.get("1.0", "end-1c").strip()
        if not desc:
            messagebox.showwarning("Thieu thong tin",
                                   "Vui long mo ta su co.", parent=self)
            return
        try:
            self.feedback_ctrl.report_issue(
                self.room_id, self.current_user, desc)
            messagebox.showinfo("Thanh cong",
                                "Da gui bao cao! Admin se kiem tra som.",
                                parent=self)
            if self.on_done:
                self.on_done()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Loi", str(e), parent=self)


# ─────────────────────────────────────────────────────────────────────────────
# RoomIssueManagementFrame – trang Admin: xem & giải quyết sự cố
# ─────────────────────────────────────────────────────────────────────────────

class RoomIssueManagementFrame(tk.Frame):
    """Admin page – danh sach bao cao su co phong."""

    def __init__(self, master: tk.Misc, feedback_ctrl: Any, equip_ctrl: Any = None) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.feedback_ctrl = feedback_ctrl
        self.equip_ctrl = equip_ctrl
        self.filter_var    = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Bao cao su co phong hoc", "🚨").pack(fill="x")

        toolbar = tk.Frame(self, bg=_get_c("BG"))
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(toolbar, text="Trang thai:", bg=_get_c("BG"),
                 font=F_BODY).pack(side="left", padx=(0, 4))
        ttk.Combobox(toolbar, textvariable=self.filter_var,
                     values=["", "Chua xu ly", "Da xu ly"],
                     width=14, state="readonly").pack(side="left")
        btn(toolbar, "Loc", self.refresh,
            variant="ghost", icon="🔍").pack(side="left", padx=(8, 0))
        btn(toolbar, "Danh dau Da xu ly", self._resolve,
            variant="success", icon="✔").pack(side="left", padx=8)

        wrap = tk.Frame(self, bg=_get_c("SURFACE"), highlightthickness=1,
                        highlightbackground=_get_c("BORDER"), padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("id", "phong", "nguoi_bao", "mo_ta", "trang_thai", "thoi_gian")
        hdrs = ("ID", "Phong", "Nguoi bao", "Mo ta su co", "Trang thai", "Thoi gian")
        wids = (50, 90, 130, 340, 110, 150)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # ── ratings summary panel ──────────────────────────────────────────────
        rating_lbl_wrap = tk.Frame(self, bg=_get_c("SURFACE"), highlightthickness=1,
                                   highlightbackground=_get_c("BORDER"), padx=14, pady=10)
        rating_lbl_wrap.pack(fill="x", padx=20, pady=(0, 16))
        tk.Label(rating_lbl_wrap, text="⭐  Danh sach danh gia gan nhat",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"), font=F_BODY_B).pack(anchor="w")

        rating_cols = ("phong", "nguoi_dg", "sao", "nhan_xet", "thoi_gian")
        rating_hdrs = ("Phong", "Nguoi danh gia", "So sao", "Nhan xet", "Thoi gian")
        rating_wids = (90, 150, 70, 360, 150)
        self._rating_tree = make_tree(rating_lbl_wrap, rating_cols,
                                      rating_hdrs, rating_wids)
        with_scrollbar(rating_lbl_wrap, self._rating_tree)
        self._refresh_ratings()

    def refresh(self) -> None:
        issues = self.feedback_ctrl.get_issues()
        f = self.filter_var.get().strip()

        rows = []
        for i in issues:
            if f and i.status != f:
                continue
            rows.append((f"PH-{i.issue_id}", i.room_id, i.user_name,
                         i.description, i.status, i.created_at))

        if self.equip_ctrl:
            eq_reports = self.equip_ctrl.list_reports()
            for er in eq_reports:
                # Map "Cho xu ly" to "Chua xu ly" to match the UI filter options
                mapped_status = "Chua xu ly" if er.status == "Cho xu ly" else er.status
                if f and mapped_status != f:
                    continue
                desc = f"[Thiet bi: {er.equipment_name}] {er.description}"
                rows.append((f"TB-{er.report_id}", er.room_id, er.user_name,
                             desc, mapped_status, er.created_at))

        # Sort by time descending
        rows.sort(key=lambda x: x[5], reverse=True)

        assert self.tree is not None
        fill_tree(self.tree, rows)

        # colour rows by status
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if vals[4] == "Chua xu ly":
                self.tree.tag_configure("pending", background=_get_c("DANGER_BG"))
                self.tree.item(item, tags=("pending",))
            else:
                self.tree.tag_configure("done", background=_get_c("SUCCESS_BG"))
                self.tree.item(item, tags=("done",))

    def _refresh_ratings(self) -> None:
        """Show recent ratings using the controller (no raw SQL in UI)."""
        ratings = self.feedback_ctrl.get_all_ratings(limit=100)
        conn_rows = []
        for r in ratings:
            conn_rows.append((r.room_id, r.user_name, "★" * r.stars, r.comment, r.created_at))
        fill_tree(self._rating_tree, conn_rows)

    def _resolve(self) -> None:
        assert self.tree is not None
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chua chon", "Hay chon mot bao cao.")
            return

        try:
            item_id_str = str(self.tree.item(sel[0], "values")[0])
            
            if item_id_str.startswith("PH-"):
                issue_id = int(item_id_str.replace("PH-", ""))
                self.feedback_ctrl.resolve_issue(issue_id)
            elif item_id_str.startswith("TB-"):
                report_id = int(item_id_str.replace("TB-", ""))
                if self.equip_ctrl:
                    # Ask if we should reset equipment status to 'Hoat dong'
                    ans = messagebox.askyesno(
                        "Xac nhan",
                        "Ban co muon cap nhat thiet bi ve trang thai 'Hoat dong' khong?",
                        parent=self
                    )
                    self.equip_ctrl.resolve_report(report_id, fix_equipment=ans)
                else:
                    # Fallback for old calls
                    issue_id = int(item_id_str.replace("TB-", ""))
                    self.feedback_ctrl.resolve_issue(issue_id)
            else:
                # Direct ID numeric
                issue_id = int(item_id_str)
                self.feedback_ctrl.resolve_issue(issue_id)

            self.refresh()
            messagebox.showinfo("Thanh cong", "Da cap nhat trang thai 'Da xu ly'.")
        except (ValueError, IndexError, Exception) as e:
            messagebox.showerror("Loi", f"Khong the xu ly bao cao: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# EquipmentReportDialog – báo hỏng thiết bị trong phòng
# ─────────────────────────────────────────────────────────────────────────────

class EquipmentReportDialog(tk.Toplevel):
    """Modal: hiển thị danh sách thiết bị của phòng, cho phép đánh dấu hỏng."""

    def __init__(self, parent: tk.Misc, room_id: str, room_name: str,
                 current_user: Any, equipment_ctrl: Any,
                 on_done: Any = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.title(f"Báo hỏng thiết bị – {room_name}")
        self.geometry("560x520")
        self.resizable(False, False)
        self.grab_set()
        self.room_id        = room_id
        self.room_name      = room_name
        self.current_user   = current_user
        self.equipment_ctrl = equipment_ctrl
        self.on_done        = on_done
        self.configure(bg=_get_c("BG"))
        self._check_vars: dict[str, tk.BooleanVar] = {}
        self._desc_vars:  dict[str, tk.StringVar]  = {}
        self._desc_widgets: dict[str, tk.Entry] = {}
        self._build()

    def _build(self) -> None:
        # Header
        hdr = tk.Frame(self, bg=_get_c("INFO_BG"), highlightthickness=1,
                       highlightbackground=_get_c("BORDER"))
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🔧  Bao hong thiet bi  –  {self.room_name}",
                 bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"),
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=16, pady=10)
        tk.Label(hdr, text=f"Phong: {self.room_id}",
                 bg=_get_c("INFO_BG"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 9)).pack(side="right", padx=16)

        tk.Label(self,
                 text="Chon thiet bi bi hong, sau do nhap mo ta su co va nhan 'Gui bao cao'.",
                 bg=_get_c("BG"), fg=_get_c("MUTED"), font=F_SMALL, wraplength=520).pack(
            anchor="w", padx=16, pady=(10, 4))

        # Scrollable equipment list
        list_frame = tk.Frame(self, bg=_get_c("BG"))
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        canvas = tk.Canvas(list_frame, bg=_get_c("BG"), highlightthickness=0)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)  # type: ignore[arg-type]
        scroll_body = tk.Frame(canvas, bg=_get_c("BG"))
        scroll_body.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_body, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
                    lambda e=None: canvas.yview_scroll(-1 * (e.delta // 120) if e else 0, "units"))

        equipment_list = self.equipment_ctrl.list_equipment(room_id=self.room_id)

        if not equipment_list:
            tk.Label(scroll_body,
                     text="ℹ  Phong nay chua co thiet bi nao duoc dang ky trong he thong.",
                     bg=_get_c("BG"), fg=_get_c("MUTED"), font=F_BODY).pack(pady=20)
        else:
            # Status colour map
            STATUS_BG = {
                "Hoat dong": _get_c("SUCCESS_BG"), "Bao tri": _get_c("WARNING_BG"),
                "Hong": _get_c("DANGER_BG"), "Dang sua": _get_c("INFO_BG"), "Da thanh ly": _get_c("BORDER"),
            }
            STATUS_FG = {
                "Hoat dong": _get_c("SUCCESS"), "Bao tri": _get_c("WARNING"),
                "Hong": _get_c("DANGER"), "Dang sua": _get_c("ACCENT"), "Da thanh ly": _get_c("MUTED"),
            }
            for equip in equipment_list:
                row_bg = _get_c("INFO_BG") if equip.status != "Hoat dong" else _get_c("SURFACE")
                row = tk.Frame(scroll_body, bg=row_bg, highlightthickness=1,
                               highlightbackground=_get_c("BORDER"))
                row.pack(fill="x", pady=3, padx=2, ipadx=6, ipady=4)

                # Checkbox
                var = tk.BooleanVar(value=False)
                self._check_vars[equip.equipment_id] = var
                cb = tk.Checkbutton(row, variable=var, bg=row_bg,
                                    activebackground=row_bg,
                                    command=lambda eid=equip.equipment_id:
                                        self._toggle_desc(eid))
                cb.pack(side="left", padx=(4, 0))

                # Equipment info
                info_col = tk.Frame(row, bg=row_bg)
                info_col.pack(side="left", fill="x", expand=True, padx=6)

                top_row = tk.Frame(info_col, bg=row_bg)
                top_row.pack(fill="x")
                tk.Label(top_row, text=equip.name,
                         bg=row_bg, fg=_get_c("TEXT"),
                         font=F_BODY_B).pack(side="left")
                tk.Label(top_row, text=f"  [{equip.equipment_type}]",
                         bg=row_bg, fg=_get_c("MUTED"), font=F_SMALL).pack(side="left")
                tk.Label(top_row,
                         text=f"  {equip.status}  ",
                         bg=STATUS_BG.get(equip.status, "#f1f5f9"),
                         fg=STATUS_FG.get(equip.status, "#64748b"),
                         font=F_SMALL).pack(side="right", padx=(0, 4))

                # Description entry (initially hidden, shown when checkbox ticked)
                desc_var = tk.StringVar()
                self._desc_vars[equip.equipment_id] = desc_var
                desc_entry = tk.Entry(info_col, textvariable=desc_var,
                                      font=("Segoe UI", 10), relief="solid", bd=1,
                                      bg=_get_c("BG"), fg=_get_c("TEXT"),
                                      insertbackground=_get_c("ACCENT"))
                self._desc_widgets[equip.equipment_id] = desc_entry
                # Don't pack yet — shown only when checkbox is ticked

        # Footer buttons
        footer = tk.Frame(self, bg=_get_c("BG"))
        footer.pack(fill="x", padx=16, pady=(4, 16))
        btn(footer, "📤  Gui bao cao hong", self._submit,
            variant="danger").pack(side="right", padx=(8, 0))
        btn(footer, "Huy", self.destroy,
            variant="ghost").pack(side="right")
        tk.Label(footer,
                 text="* Thiet bi duoc chon se tu dong chuyen sang trang thai 'Bao tri'",
                 bg=_get_c("BG"), fg=_get_c("MUTED"), font=F_SMALL, wraplength=300).pack(
            side="left")

    def _toggle_desc(self, equipment_id: str) -> None:
        """Show/hide description entry when checkbox is toggled."""
        widget = self._desc_widgets.get(equipment_id)
        if widget is None:
            return
        if self._check_vars[equipment_id].get():
            widget.pack(fill="x", pady=(3, 0))
            # Placeholder behaviour
            if not widget.get():
                widget.insert(0, "Mo ta su co...")
                widget.config(fg="#94a3b8")
            def _on_focus_in(e: Any, w: tk.Entry = widget) -> None:
                if w.get() == "Mo ta su co...":
                    w.delete(0, "end")
                    w.config(fg="#1e293b")
            def _on_focus_out(e: Any, w: tk.Entry = widget) -> None:
                if not w.get().strip():
                    w.insert(0, "Mo ta su co...")
                    w.config(fg="#94a3b8")
            widget.bind("<FocusIn>", _on_focus_in)
            widget.bind("<FocusOut>", _on_focus_out)
        else:
            widget.pack_forget()

    def _submit(self) -> None:
        selected = [eid for eid, var in self._check_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("Chua chon thiet bi",
                                   "Vui long chon it nhat mot thiet bi bi hong.",
                                   parent=self)
            return

        errors: list[str] = []
        success_count = 0
        for eid in selected:
            desc = ""
            widget = self._desc_widgets.get(eid)
            if widget:
                raw = widget.get().strip()
                desc = raw if raw and raw != "Mo ta su co..." else f"Thiet bi bi hong – bao cao boi {self.current_user.full_name}"
            try:
                self.equipment_ctrl.report_broken(eid, self.current_user, desc)
                success_count += 1
            except ValueError as e:
                errors.append(str(e))

        if errors:
            messagebox.showerror("Co loi xay ra",
                                 "\n".join(errors), parent=self)
        if success_count:
            messagebox.showinfo("Bao cao thanh cong",
                                f"Da gui {success_count} bao cao hong thiet bi.\n"
                                "Bo phan ky thuat se xu ly som.",
                                parent=self)
            if self.on_done:
                self.on_done()
            self.destroy()
