# report_gui.py  –  statistics / report screen  (v2.1 – date filter)
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any
from gui.theme import (F_SECTION, F_BODY_B, make_tree, fill_tree, with_scrollbar,
                       page_header, _get_c)

from tkcalendar import DateEntry  # type: ignore[import-untyped]

def _get_card_palette() -> list[tuple[str, str, str]]:
    return [
        (_get_c("INFO_BG"), _get_c("ACCENT"), "📚"),   # Indigo
        (_get_c("SUCCESS_BG"), _get_c("SUCCESS"), "📅"), # Green
        (_get_c("WARNING_BG"), _get_c("WARNING"), "📋"), # Amber
        (_get_c("DANGER_BG"), _get_c("DANGER"), "🚫"),  # Red
        (_get_c("INFO_BG"), _get_c("ACCENT"), "👤"),    # Indigo/Violet
        (_get_c("BORDER"), _get_c("MUTED"), "🛠"),     # Slate
    ]

def _get_bar_colors() -> list[str]:
    return [
        _get_c("ACCENT"), _get_c("SUCCESS"), _get_c("WARNING"), _get_c("DANGER"),
        "#6366f1", "#8b5cf6", "#ec4899", "#14b8a6",
    ]


class ReportFrame(tk.Frame):
    def __init__(self, master: tk.Misc, report_controller: Any) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.report_ctrl = report_controller
        # Date filter state
        self._date_from = tk.StringVar()
        self._date_to   = tk.StringVar()
        self._body_ref: tk.Frame | None = None
        self._build()

    def _build(self) -> None:
        # ── Header + export toolbar ───────────────────────────────────────────
        hdr_row = tk.Frame(self, bg=_get_c("BG"))
        hdr_row.pack(fill="x")
        page_header(hdr_row, "Bao cao thong ke", "📊").pack(
            side="left", fill="x", expand=True)

        toolbar = tk.Frame(hdr_row, bg=_get_c("BG"))
        toolbar.pack(side="right", padx=16, pady=10)

        xlsx_btn = tk.Button(
            toolbar, text="📥  Xuat Excel",
            bg=_get_c("SUCCESS"), fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._export_excel,
        )
        xlsx_btn.pack(side="left", padx=(0, 8))

        pdf_btn = tk.Button(
            toolbar, text="📄  Xuat PDF",
            bg=_get_c("DANGER"), fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._export_pdf,
        )
        pdf_btn.pack(side="left")

        # ── Date range filter panel ───────────────────────────────────────────
        filter_panel = tk.Frame(self, bg=_get_c("SURFACE"), highlightthickness=1,
                                highlightbackground=_get_c("BORDER"), padx=16, pady=10)
        filter_panel.pack(fill="x", padx=20, pady=(6, 0))

        tk.Label(filter_panel, text="🗓  Loc theo khoang thoi gian:",
                 bg=_get_c("SURFACE"), fg=_get_c("ACCENT"),
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        def _date_entry(parent: tk.Frame, var: tk.StringVar,
                        placeholder: str) -> tk.Widget:
            wrap = tk.Frame(parent, bg=_get_c("SURFACE"), highlightthickness=1,
                            highlightbackground=_get_c("BORDER"))
            wrap.pack(side="left", padx=(8, 0))

            e = DateEntry(wrap, textvariable=var, width=12,
                           date_pattern="yyyy-mm-dd",
                           background=_get_c("ACCENT"), foreground="white",
                           weekendbackground=_get_c("SURFACE"), weekendforeground=_get_c("TEXT"),
                           state="readonly",
                           borderwidth=1, font=("Segoe UI", 10))
            e.pack(padx=6, pady=4)
            return e

        tk.Label(filter_panel, text="Tu:", bg=_get_c("SURFACE"), fg=_get_c("ACCENT"),
                 font=F_BODY_B).pack(side="left", padx=(10, 0))
        self._from_entry = _date_entry(filter_panel, self._date_from, "YYYY-MM-DD")
        tk.Label(filter_panel, text="Den:", bg=_get_c("SURFACE"), fg=_get_c("ACCENT"),
                 font=F_BODY_B).pack(side="left", padx=(8, 0))
        self._to_entry = _date_entry(filter_panel, self._date_to, "YYYY-MM-DD")

        # Live refresh on date change
        self._from_entry.bind("<<DateEntrySelected>>", lambda _: self._apply_filter())
        self._to_entry.bind("<<DateEntrySelected>>", lambda _: self._apply_filter())

        # Reset helper if needed (not packed as a button anymore)

        self._filter_info = tk.Label(filter_panel, text="",
                                     bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"),
                                     font=("Segoe UI", 8, "bold"))
        self._filter_info.pack(side="right", padx=8)

        # ── Scrollable body ──────────────────────────────────────────────────
        self._canvas = tk.Canvas(self, bg=_get_c("BG"), highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical",
                            command=self._canvas.yview)  # type: ignore[arg-type]
        self._body_ref = tk.Frame(self._canvas, bg=_get_c("BG"))
        self._body_ref.bind(
            "<Configure>",
            lambda _e=None: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.create_window((0, 0), window=self._body_ref, anchor="nw")
        self._canvas.configure(yscrollcommand=vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._canvas.bind(
            "<MouseWheel>",
            lambda e=None: self._canvas.yview_scroll(-1*(e.delta//120) if e else 0, "units"))

        self._render_body()

    def _apply_filter(self) -> None:
        from_val = self._from_entry.get().strip()
        to_val   = self._to_entry.get().strip()
        placeholder = "YYYY-MM-DD"
        df = from_val if from_val != placeholder else ""
        dt_ = to_val  if to_val   != placeholder else ""
        # Validate
        for v, label in ((df, "Tu ngay"), (dt_, "Den ngay")):
            if v:
                try:
                    dt.date.fromisoformat(v)
                except ValueError:
                    messagebox.showerror(
                        "Ngay khong hop le",
                        f"{label} phai theo dinh dang YYYY-MM-DD.",
                        parent=self)
                    return
        self._date_from.set(df)
        self._date_to.set(dt_)
        if df or dt_:
            label_parts = []
            if df:
                label_parts.append(f"Tu {df}")
            if dt_:
                label_parts.append(f"Den {dt_}")
            self._filter_info.config(text="  🔵 " + "  –  ".join(label_parts))
        else:
            self._filter_info.config(text="")
        self._render_body()

    def _reset_filter(self) -> None:
        self._date_from.set("")
        self._date_to.set("")
        self._from_entry.delete(0, "end")
        self._from_entry.insert(0, "YYYY-MM-DD")
        self._from_entry.config(fg=_get_c("MUTED"))
        self._to_entry.delete(0, "end")
        self._to_entry.insert(0, "YYYY-MM-DD")
        self._to_entry.config(fg=_get_c("MUTED"))
        self._filter_info.config(text="")
        self._render_body()

    def _render_body(self) -> None:
        """Clear and redraw the scrollable body with current filter."""
        if self._body_ref is None:
            return
        for w in self._body_ref.winfo_children():
            w.destroy()
        df = self._date_from.get()
        dt_ = self._date_to.get()
        self._draw_stat_cards(self._body_ref, df, dt_)
        self._draw_detail_section(self._body_ref, df, dt_)

    # ── Export helpers ────────────────────────────────────────────────────────

    def _export_excel(self) -> None:
        from utils.export_excel import export_rows_to_excel  # type: ignore[import-not-found]
        path = filedialog.asksaveasfilename(
            title="Luu file Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"BaoCao_{dt.date.today()}.xlsx",
        )
        if not path:
            return
        rows: list[tuple[object, object, object, object, object]] = self.report_ctrl.room_stats_table(
            date_from=self._date_from.get(), date_to=self._date_to.get())
        try:
            export_rows_to_excel(
                headers=["Phong", "Tong dat", "Da duyet", "Tu choi", "Ty le SD (%)"],
                rows=rows,
                output_path=path,
            )
            messagebox.showinfo("Xuat Excel thanh cong",
                                f"Da luu tai:\n{path}")
        except Exception as exc:
            messagebox.showerror("Loi xuat Excel", str(exc))

    def _export_pdf(self) -> None:
        try:
            from utils.export_pdf import export_report_pdf  # type: ignore[import-not-found]
        except ImportError:
            messagebox.showerror(
                "Thieu thu vien",
                "Chua cai fpdf2.\nChay lenh:  pip install fpdf2",
            )
            return
        path = filedialog.asksaveasfilename(
            title="Luu file PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"BaoCao_{dt.date.today()}.pdf",
        )
        if not path:
            return
        try:
            export_report_pdf(
                output_path=path,
                title="BAO CAO SU DUNG PHONG HOC",
                stat_rows=self.report_ctrl.room_stats_table(
                    date_from=self._date_from.get(),
                    date_to=self._date_to.get()),
                summary=self.report_ctrl.build_dashboard(
                    date_from=self._date_from.get(),
                    date_to=self._date_to.get()),
            )
            messagebox.showinfo("Xuat PDF thanh cong",
                                f"Da luu tai:\n{path}")
        except Exception as exc:
            messagebox.showerror("Loi xuat PDF", str(exc))

    # ── Stat cards ────────────────────────────────────────────────────────────

    def _draw_stat_cards(self, body: tk.Frame,
                         date_from: str = "", date_to: str = "") -> None:
        panel = tk.Frame(body, bg=_get_c("BG"))
        panel.pack(fill="x", padx=20, pady=(10, 4))
        summary: dict[str, object] = self.report_ctrl.build_dashboard(
            date_from=date_from, date_to=date_to)
        
        from gui.theme import animate_count
        palette = _get_card_palette()
        for idx, (label, value) in enumerate(summary.items()):
            bg, fg, icon = palette[idx % len(palette)]

            # Indigo-tinted shadow wrapper
            shadow = tk.Frame(panel, bg=_get_c("BORDER"))
            shadow.grid(row=idx // 3, column=idx % 3,
                        sticky="nsew", padx=6, pady=6)
            card = tk.Frame(shadow, bg=bg, padx=18, pady=16)
            card.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

            top = tk.Frame(card, bg=bg)
            top.pack(fill="x")

            # Icon circle
            ic = tk.Canvas(top, width=46, height=46, bg=bg,
                           highlightthickness=0)
            ic.pack(side="left")
            ic.create_oval(2, 2, 44, 44, fill=fg, outline="")
            ic.create_text(23, 23, text=icon, font=("Segoe UI", 18),
                           fill="white")

            val_lbl = tk.Label(top, text="0", bg=bg, fg=fg,
                               font=("Segoe UI", 30, "bold"))
            val_lbl.pack(side="right", anchor="s")
            
            try:
                val_int = int(str(value).replace("%", "").strip())
                animate_count(val_lbl, val_int)
                if "%" in str(value):
                    val_lbl.after(800, lambda v=value, l=val_lbl: l.config(text=str(v)))
            except Exception:
                val_lbl.config(text=str(value))

            tk.Label(card, text=label, bg=bg, fg=_get_c("TEXT"),
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 0))
        for col in range(3):
            panel.grid_columnconfigure(col, weight=1)

    # ── Detail section (table + chart) ───────────────────────────────────────

    def _draw_detail_section(self, body: tk.Frame,
                             date_from: str = "", date_to: str = "") -> None:
        tk.Label(body, text="Tan suat su dung phong",
                 bg=_get_c("BG"), fg=_get_c("TEXT"), font=F_SECTION).pack(
            anchor="w", padx=20, pady=(12, 6))

        row_data: list[tuple[object, object, object, object, str]] = self.report_ctrl.room_stats_table(
            date_from=date_from, date_to=date_to)

        # Two-column layout
        two_col = tk.Frame(body, bg=_get_c("BG"))
        two_col.pack(fill="x", padx=20, pady=(0, 16))
        two_col.grid_columnconfigure(0, weight=0)
        two_col.grid_columnconfigure(1, weight=1)

        # ── Left: summary table ─────────────────────────────────────────────
        left = tk.Frame(two_col, bg=_get_c("SURFACE"), highlightthickness=1,
                        highlightbackground=_get_c("BORDER"), padx=12, pady=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(left, text="Tong hop theo phong",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        tree = make_tree(
            left,
            ("phong", "tong", "duyet", "tuchoi", "tyle"),
            ("Phong", "Tong dat", "Da duyet", "Tu choi", "Ty le SD"),
            (70, 80, 80, 80, 80),
            height=8,
        )
        with_scrollbar(left, tree)
        rows: list[tuple[object, object, object, object, str]] = [(r[0], r[1], r[2], r[3], r[4]) for r in row_data]
        fill_tree(tree, rows)

        # ── Right: bar chart (usage rate %) ─────────────────────────────────
        right = tk.Frame(two_col, bg=_get_c("SURFACE"), highlightthickness=1,
                         highlightbackground=_get_c("BORDER"), padx=14, pady=12)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Bieu do ty le su dung phong (%)",
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        self._chart_canvas = tk.Canvas(right, bg=_get_c("SURFACE"), height=220,
                                       highlightthickness=0)
        self._chart_canvas.pack(fill="x", expand=True)
        right.after(60, lambda: self._draw_bar_chart(row_data))

        # plain usage count bar (secondary)
        tk.Label(body, text="So lan dat phong (tong hop)",
                 bg=_get_c("BG"), fg=_get_c("TEXT"), font=F_SECTION).pack(
            anchor="w", padx=20, pady=(8, 6))
        wrap2 = tk.Frame(body, bg=_get_c("SURFACE"), highlightthickness=1,
                         highlightbackground=_get_c("BORDER"), padx=14, pady=12)
        wrap2.pack(fill="x", padx=20, pady=(0, 16))
        tree2 = make_tree(wrap2, ("room", "count"),
                          ("Phong", "So lan dat"), (200, 160), height=5)
        with_scrollbar(wrap2, tree2)
        usage_rows: list[tuple[object, object]] = [(rid, cnt)
                                                   for rid, cnt in self.report_ctrl.room_usage_rows()
                                                   if cnt > 0]
        fill_tree(tree2, usage_rows)

    def _draw_bar_chart(self, row_data: list[tuple[object, object, object, object, str]]) -> None:
        c = self._chart_canvas
        c.update_idletasks()
        W = c.winfo_width() or 420
        H = 200
        ml, mr, mb, mt = 40, 12, 38, 16

        if not row_data:
            c.create_text(W // 2, H // 2, text="Chua co du lieu",
                          font=("Segoe UI", 11), fill=_get_c("MUTED"))
            return

        n = len(row_data)
        gap = 8
        bar_area = W - ml - mr
        bar_w = max(20, (bar_area - gap * (n + 1)) // n)

        # axes
        c.create_line(ml, mt, ml, H - mb, fill=_get_c("BORDER"), width=1)
        c.create_line(ml, H - mb, W - mr, H - mb, fill=_get_c("BORDER"), width=1)

        for v in range(0, 101, 25):
            y = H - mb - int((H - mt - mb) * v / 100)
            c.create_line(ml - 4, y, W - mr, y, fill=_get_c("BORDER"), dash=(3, 2))
            c.create_text(ml - 6, y, text=str(v),
                          font=("Segoe UI", 7), fill=_get_c("MUTED"), anchor="e")

        colors = _get_bar_colors()
        for idx, (room_id, _total, _approved, _rejected, rate_str) in enumerate(row_data):
            pct = int(rate_str.replace("%", "")) if rate_str.replace("%", "").isdigit() else 0
            color = colors[idx % len(colors)]
            x0 = ml + gap + idx * (bar_w + gap)
            bh = int((H - mt - mb) * pct / 100) if pct > 0 else 2
            y0 = H - mb - bh
            y1 = H - mb
            # bar with rounded-top illusion
            c.create_rectangle(x0, y0, x0 + bar_w, y1, fill=color, outline="")
            # value label
            c.create_text(x0 + bar_w // 2, y0 - 8,
                          text=rate_str,
                          font=("Segoe UI", 8, "bold"), fill=_get_c("TEXT"))
            # room label
            c.create_text(x0 + bar_w // 2, H - mb + 14,
                          text=str(room_id), font=("Segoe UI", 8), fill=_get_c("TEXT"))

