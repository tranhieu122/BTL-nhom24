# room_feedback_gui.py – dialogs and admin page for room ratings & issue reports
from __future__ import annotations
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, cast
from gui.theme import (
    C_BG, C_SURFACE, C_BORDER, C_MUTED,
    C_SUCCESS_BG,
    C_DANGER_BG, F_BODY, F_BODY_B, F_INPUT, F_SMALL,
    make_tree, fill_tree, with_scrollbar, page_header, btn,
)


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
        self.configure(bg=C_BG)
        self._build(room_name)

    def _build(self, room_name: str) -> None:
        tk.Label(self, text=f"Đánh giá phòng  {room_name}", bg=C_BG,
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 4))

        tk.Label(self, text="Chon so sao:", bg=C_BG,
                 font=F_BODY_B).pack(anchor="w", padx=20, pady=6)

        # ── star buttons ──────────────────────────────────────────────────────
        star_row = tk.Frame(self, bg=C_BG)
        star_row.pack(pady=(0, 4))
        self._star_btns: list[tk.Label] = []
        for i in range(1, 6):
            lbl = tk.Label(star_row, text="☆", bg=C_BG,
                           font=("Segoe UI", 28), cursor="hand2", fg="#fbbf24")
            lbl.pack(side="left", padx=2)
            lbl.bind("<Button-1>", lambda e, v=i: self._set_stars(v))
            lbl.bind("<Enter>",    lambda e, v=i: self._hover_stars(v))
            lbl.bind("<Leave>",    lambda e: self._render_stars(self._stars.get()))
            self._star_btns.append(lbl)

        self._rating_label = tk.Label(self, text="Chưa chọn sao", bg=C_BG,
                                      fg=C_MUTED, font=F_BODY)
        self._rating_label.pack(pady=(0, 6))

        # ── comment ───────────────────────────────────────────────────────────
        tk.Label(self, text="Nhan xet (tuy chon):", bg=C_BG,
                 font=F_BODY_B).pack(anchor="w", padx=20, pady=6)
        self._comment = tk.Text(self, width=40, height=4, font=F_INPUT,
                                relief="solid", bd=1, wrap="word")
        self._comment.pack(padx=20, pady=(0, 10))

        # ── existing rating ───────────────────────────────────────────────────
        existing = self.feedback_ctrl.get_user_rating(
            self.room_id, self.current_user.user_id)
        if existing:
            self._set_stars(existing.stars)
            self._comment.insert("1.0", existing.comment)
            tk.Label(self, text="(Bạn đã đánh giá phòng này trước đó)",
                     bg=C_BG, fg=C_MUTED, font=F_SMALL).pack()

        # ── buttons ───────────────────────────────────────────────────────────
        bf = tk.Frame(self, bg=C_BG)
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
        self.configure(bg=C_BG)
        self._build(room_name)

    def _build(self, room_name: str) -> None:
        tk.Label(self, text=f"Báo lỗi phòng  {room_name}", bg=C_BG,
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 4))

        tk.Label(self, text="Mo ta su co / loi:", bg=C_BG,
                 font=F_BODY_B).pack(anchor="w", padx=20, pady=6)
        self._desc = tk.Text(self, width=44, height=5, font=F_INPUT,
                             relief="solid", bd=1, wrap="word")
        self._desc.pack(padx=20, pady=(0, 10))

        tk.Label(self,
                 text="Bao cao se duoc gui toi Admin de xu ly.",
                 bg=C_BG, fg=C_MUTED, font=F_SMALL).pack()

        bf = tk.Frame(self, bg=C_BG)
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

    def __init__(self, master: tk.Misc, feedback_ctrl: Any) -> None:
        super().__init__(master, bg=C_BG)
        self.feedback_ctrl = feedback_ctrl
        self.filter_var    = tk.StringVar()
        self.tree: ttk.Treeview | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        page_header(self, "Bao cao su co phong hoc", "🚨").pack(fill="x")

        toolbar = tk.Frame(self, bg=C_BG)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(toolbar, text="Trang thai:", bg=C_BG,
                 font=F_BODY).pack(side="left", padx=(0, 4))
        ttk.Combobox(toolbar, textvariable=self.filter_var,
                     values=["", "Chua xu ly", "Da xu ly"],
                     width=14, state="readonly").pack(side="left")
        btn(toolbar, "Loc", self.refresh,
            variant="ghost", icon="🔍").pack(side="left", padx=(8, 0))
        btn(toolbar, "Danh dau Da xu ly", self._resolve,
            variant="success", icon="✔").pack(side="left", padx=8)

        wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=14, pady=14)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("id", "phong", "nguoi_bao", "mo_ta", "trang_thai", "thoi_gian")
        hdrs = ("ID", "Phong", "Nguoi bao", "Mo ta su co", "Trang thai", "Thoi gian")
        wids = (50, 90, 130, 340, 110, 150)
        self.tree = make_tree(wrap, cols, hdrs, wids)
        with_scrollbar(wrap, self.tree)

        # ── ratings summary panel ──────────────────────────────────────────────
        rating_lbl_wrap = tk.Frame(self, bg=C_SURFACE, highlightthickness=1,
                                   highlightbackground=C_BORDER, padx=14, pady=10)
        rating_lbl_wrap.pack(fill="x", padx=20, pady=(0, 16))
        tk.Label(rating_lbl_wrap, text="⭐  Danh sach danh gia gan nhat",
                 bg=C_SURFACE, font=F_BODY_B).pack(anchor="w")

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
        if f:
            issues = [i for i in issues if i.status == f]
        rows = [(i.issue_id, i.room_id, i.user_name,
                 i.description, i.status, i.created_at)
                for i in issues]
        assert self.tree is not None
        fill_tree(self.tree, rows)

        # colour rows by status
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if vals[4] == "Chua xu ly":
                self.tree.tag_configure("pending", background=C_DANGER_BG)
                self.tree.item(item, tags=("pending",))
            else:
                self.tree.tag_configure("done", background=C_SUCCESS_BG)
                self.tree.item(item, tags=("done",))

    def _refresh_ratings(self) -> None:
        # Show all ratings (no filter)
        conn_rows: list[tuple[object, object, str, object, object]] = []
        from database.sqlite_db import get_connection  # type: ignore[import-not-found]
        conn: sqlite3.Connection = get_connection()  # type: ignore[assignment]
        raw_rows = conn.execute(  # type: ignore[reportUnknownMemberType]
            "SELECT room_id, user_name, stars, comment, created_at "
            "FROM room_ratings ORDER BY created_at DESC LIMIT 100"
        ).fetchall()  # type: ignore[reportUnknownMemberType]
        rows = cast(list[tuple[object, object, int, object, object]], raw_rows)
        for r in rows:
            conn_rows.append((r[0], r[1], "★" * r[2], r[3], r[4]))
        fill_tree(self._rating_tree, conn_rows)

    def _resolve(self) -> None:
        assert self.tree is not None
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chua chon", "Hay chon mot bao cao.")
            return
        issue_id = int(self.tree.item(sel[0], "values")[0])
        self.feedback_ctrl.resolve_issue(issue_id)
        self.refresh()
        messagebox.showinfo("Thanh cong", "Da cap nhat trang thai 'Da xu ly'.")
