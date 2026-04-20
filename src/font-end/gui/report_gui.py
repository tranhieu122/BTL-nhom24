# report_gui.py  –  statistics / report screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from gui.theme import (C_BG, C_DARK, C_SURFACE, C_BORDER, C_PRIMARY,
                       F_SECTION, make_tree, fill_tree, with_scrollbar,
                       page_header, btn)

CARD_PALETTE = [
    ("#dbeafe", "#2255a4", "📚"),
    ("#dcfce7", "#16a34a", "📅"),
    ("#fef3c7", "#b45309", "📋"),
    ("#fee2e2", "#dc2626", "🚫"),
    ("#e0f2fe", "#0369a1", "👤"),
    ("#ede9fe", "#6d28d9", "🛠"),
]

BAR_COLORS = [
    "#2255a4", "#4a8ecb", "#16a34a", "#f59e0b",
    "#9333ea", "#06b6d4", "#ef4444", "#84cc16",
]


class ReportFrame(tk.Frame):
    def __init__(self, master, report_controller) -> None:
        super().__init__(master, bg=C_BG)
        self.report_ctrl = report_controller
        self._build()

    def _build(self) -> None:
        # ── Header + export toolbar ───────────────────────────────────────────
        hdr_row = tk.Frame(self, bg="#f8fafc")
        hdr_row.pack(fill="x")
        page_header(hdr_row, "Bao cao thong ke", "📊").pack(
            side="left", fill="x", expand=True)

        toolbar = tk.Frame(hdr_row, bg="#f8fafc")
        toolbar.pack(side="right", padx=16, pady=10)

        xlsx_btn = tk.Button(
            toolbar, text="📥  Xuat Excel",
            bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._export_excel,
        )
        xlsx_btn.pack(side="left", padx=(0, 8))

        pdf_btn = tk.Button(
            toolbar, text="📄  Xuat PDF",
            bg="#dc2626", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._export_pdf,
        )
        pdf_btn.pack(side="left")

        # ── Scrollable body ──────────────────────────────────────────────────
        canvas = tk.Canvas(self, bg=C_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=C_BG)
        body.bind("<Configure>",
                  lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._draw_stat_cards(body)
        self._draw_detail_section(body)

    # ── Export helpers ────────────────────────────────────────────────────────

    def _export_excel(self) -> None:
        from utils.export_excel import export_rows_to_excel
        path = filedialog.asksaveasfilename(
            title="Luu file Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"BaoCao_{dt.date.today()}.xlsx",
        )
        if not path:
            return
        rows = self.report_ctrl.room_stats_table()
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
            from utils.export_pdf import export_report_pdf
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
                stat_rows=self.report_ctrl.room_stats_table(),
                summary=self.report_ctrl.build_dashboard(),
            )
            messagebox.showinfo("Xuat PDF thanh cong",
                                f"Da luu tai:\n{path}")
        except Exception as exc:
            messagebox.showerror("Loi xuat PDF", str(exc))

    # ── Stat cards ────────────────────────────────────────────────────────────

    def _draw_stat_cards(self, body: tk.Frame) -> None:
        panel = tk.Frame(body, bg=C_BG)
        panel.pack(fill="x", padx=20, pady=(10, 4))
        summary = self.report_ctrl.build_dashboard()
        for idx, (label, value) in enumerate(summary.items()):
            bg, fg, icon = CARD_PALETTE[idx % len(CARD_PALETTE)]
            card = tk.Frame(panel, bg=bg, padx=18, pady=14,
                            highlightthickness=1, highlightbackground="#c7d8f5")
            card.grid(row=idx // 3, column=idx % 3,
                      sticky="nsew", padx=6, pady=6)
            top = tk.Frame(card, bg=bg)
            top.pack(fill="x")
            tk.Label(top, text=icon, bg=bg,
                     font=("Segoe UI", 22)).pack(side="left")
            tk.Label(top, text=str(value), bg=bg, fg=fg,
                     font=("Segoe UI", 26, "bold")).pack(side="right")
            tk.Label(card, text=label, bg=bg, fg="#475569",
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
        for col in range(3):
            panel.grid_columnconfigure(col, weight=1)

    # ── Detail section (table + chart) ───────────────────────────────────────

    def _draw_detail_section(self, body: tk.Frame) -> None:
        tk.Label(body, text="Tan suat su dung phong",
                 bg=C_BG, fg=C_DARK, font=F_SECTION).pack(
            anchor="w", padx=20, pady=(12, 6))

        row_data = self.report_ctrl.room_stats_table()

        # Two-column layout
        two_col = tk.Frame(body, bg=C_BG)
        two_col.pack(fill="x", padx=20, pady=(0, 16))
        two_col.grid_columnconfigure(0, weight=0)
        two_col.grid_columnconfigure(1, weight=1)

        # ── Left: summary table ─────────────────────────────────────────────
        left = tk.Frame(two_col, bg=C_SURFACE, highlightthickness=1,
                        highlightbackground=C_BORDER, padx=12, pady=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(left, text="Tong hop theo phong",
                 bg=C_SURFACE, fg=C_DARK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        tree = make_tree(
            left,
            ("phong", "tong", "duyet", "tuchoi", "tyle"),
            ("Phong", "Tong dat", "Da duyet", "Tu choi", "Ty le SD"),
            (70, 80, 80, 80, 80),
            height=8,
        )
        with_scrollbar(left, tree)
        rows = [(r[0], r[1], r[2], r[3], r[4]) for r in row_data]
        fill_tree(tree, rows)

        # ── Right: bar chart (usage rate %) ─────────────────────────────────
        right = tk.Frame(two_col, bg=C_SURFACE, highlightthickness=1,
                         highlightbackground=C_BORDER, padx=14, pady=12)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Bieu do ty le su dung phong (%)",
                 bg=C_SURFACE, fg=C_DARK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        self._chart_canvas = tk.Canvas(right, bg="#f8fafc", height=220,
                                       highlightthickness=0)
        self._chart_canvas.pack(fill="x", expand=True)
        right.after(60, lambda: self._draw_bar_chart(row_data))

        # plain usage count bar (secondary)
        tk.Label(body, text="So lan dat phong (tong hop)",
                 bg=C_BG, fg=C_DARK, font=F_SECTION).pack(
            anchor="w", padx=20, pady=(8, 6))
        wrap2 = tk.Frame(body, bg=C_SURFACE, highlightthickness=1,
                         highlightbackground=C_BORDER, padx=14, pady=12)
        wrap2.pack(fill="x", padx=20, pady=(0, 16))
        tree2 = make_tree(wrap2, ("room", "count"),
                          ("Phong", "So lan dat"), (200, 160), height=5)
        with_scrollbar(wrap2, tree2)
        usage_rows = [(rid, cnt)
                      for rid, cnt in self.report_ctrl.room_usage_rows()
                      if cnt > 0]
        fill_tree(tree2, usage_rows)

    def _draw_bar_chart(self, row_data: list[tuple]) -> None:
        c = self._chart_canvas
        c.update_idletasks()
        W = c.winfo_width() or 420
        H = 200
        ml, mr, mb, mt = 40, 12, 38, 16

        if not row_data:
            c.create_text(W // 2, H // 2, text="Chua co du lieu",
                          font=("Segoe UI", 11), fill="#94a3b8")
            return

        n = len(row_data)
        gap = 8
        bar_area = W - ml - mr
        bar_w = max(20, (bar_area - gap * (n + 1)) // n)

        # axes
        c.create_line(ml, mt, ml, H - mb, fill="#d1d5db", width=1)
        c.create_line(ml, H - mb, W - mr, H - mb, fill="#d1d5db", width=1)

        for v in range(0, 101, 25):
            y = H - mb - int((H - mt - mb) * v / 100)
            c.create_line(ml - 4, y, W - mr, y, fill="#e5e7eb", dash=(3, 2))
            c.create_text(ml - 6, y, text=str(v),
                          font=("Segoe UI", 7), fill="#9ca3af", anchor="e")

        for idx, (room_id, _total, _approved, _rejected, rate_str) in enumerate(row_data):
            pct = int(rate_str.replace("%", "")) if rate_str.replace("%", "").isdigit() else 0
            color = BAR_COLORS[idx % len(BAR_COLORS)]
            x0 = ml + gap + idx * (bar_w + gap)
            bh = int((H - mt - mb) * pct / 100) if pct > 0 else 2
            y0 = H - mb - bh
            y1 = H - mb
            # bar with rounded-top illusion
            c.create_rectangle(x0, y0, x0 + bar_w, y1, fill=color, outline="")
            # value label
            c.create_text(x0 + bar_w // 2, y0 - 8,
                          text=rate_str,
                          font=("Segoe UI", 8, "bold"), fill=C_DARK)
            # room label
            c.create_text(x0 + bar_w // 2, H - mb + 14,
                          text=room_id, font=("Segoe UI", 8), fill="#374151")

