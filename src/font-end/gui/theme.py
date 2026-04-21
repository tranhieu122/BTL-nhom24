# gui/theme.py  –  shared palette, fonts, widget factories
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Any

# ── Palette ──────────────────────────────────────────────────────────────────
C_DARK       = "#1a2f5e"
C_PRIMARY    = "#2255a4"
C_PRIMARY_H  = "#1a4490"
C_ACCENT     = "#3b82f6"     # brighter blue for glow/highlight
C_LIGHT      = "#4a8ecb"
C_BG         = "#f0f4fa"
C_SURFACE    = "#ffffff"
C_BORDER     = "#dbe4f0"
C_SHADOW     = "#c8d3e8"     # shadow simulation
C_TEXT       = "#1e293b"
C_MUTED      = "#64748b"
C_SUCCESS    = "#16a34a"
C_SUCCESS_BG = "#dcfce7"
C_WARNING    = "#b45309"
C_WARNING_BG = "#fef3c7"
C_DANGER     = "#dc2626"
C_DANGER_BG  = "#fee2e2"
C_INFO_BG    = "#dbeafe"
ROW_ODD      = "#f8fafc"
ROW_EVEN     = "#ffffff"

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_TITLE   = ("Segoe UI", 18, "bold")
F_SECTION = ("Segoe UI", 13, "bold")
F_BODY    = ("Segoe UI", 10)
F_BODY_B  = ("Segoe UI", 10, "bold")
F_SMALL   = ("Segoe UI", 9)
F_INPUT   = ("Segoe UI", 11)
F_BTN     = ("Segoe UI", 10, "bold")


def apply_theme(style: ttk.Style) -> None:
    """Call once at app start to configure all ttk styles."""
    style.theme_use("clam")

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure("TV.Treeview.Heading",
                    background=C_PRIMARY, foreground="white",
                    font=F_BODY_B, relief="flat", padding=10)
    style.map("TV.Treeview.Heading",
              background=[("active", C_LIGHT)])
    style.configure("TV.Treeview",
                    rowheight=34, font=F_BODY,
                    fieldbackground=C_SURFACE, background=C_SURFACE,
                    borderwidth=0, relief="flat")
    style.map("TV.Treeview",
              background=[("selected", "#bfdbfe")],
              foreground=[("selected", C_TEXT)])

    # ── Scrollbar (thin, minimal) ─────────────────────────────────────────────
    style.configure("Vertical.TScrollbar",
                    background=C_BORDER, troughcolor=C_BG,
                    arrowcolor=C_MUTED, borderwidth=0,
                    relief="flat", width=6)
    style.map("Vertical.TScrollbar",
              background=[("active", C_MUTED), ("!active", C_BORDER)])
    style.configure("Horizontal.TScrollbar",
                    background=C_BORDER, troughcolor=C_BG,
                    arrowcolor=C_MUTED, borderwidth=0,
                    relief="flat", width=6)

    # ── Combobox ──────────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    background=C_SURFACE, fieldbackground=C_SURFACE,
                    foreground=C_TEXT, bordercolor=C_BORDER,
                    arrowcolor=C_PRIMARY, relief="flat", padding=4)
    style.map("TCombobox",
              fieldbackground=[("readonly", C_SURFACE)],
              bordercolor=[("focus", C_PRIMARY), ("!focus", C_BORDER)])

    # ── Button (ttk) ─────────────────────────────────────────────────────────
    style.configure("TButton",
                    background=C_PRIMARY, foreground="white",
                    font=F_BODY_B, relief="flat", padding=(12, 6))
    style.map("TButton",
              background=[("active", "#1a4490"), ("pressed", "#1a4490")])


def btn(parent: tk.Misc, text: str, command: Any, variant: str = "primary",
    icon: str = "", **kw: Any) -> tk.Button:
    """Themed button with hover + active press effects."""
    label = f"{icon}  {text}" if icon else text
    colours = {
        "primary": (C_PRIMARY,   C_PRIMARY_H, "white"),
        "success": ("#16a34a",   "#15803d",   "white"),
        "danger":  (C_DANGER,    "#b91c1c",   "white"),
        "ghost":   ("#e2e8f0",   "#cbd5e1",   C_TEXT),
        "outline": (C_SURFACE,   C_INFO_BG,   C_PRIMARY),
        "accent":  (C_ACCENT,    "#2563eb",   "white"),
    }
    bg, bg_h, fg = colours.get(variant, colours["primary"])
    b = tk.Button(parent, text=label, bg=bg, fg=fg,
                  font=F_BTN, relief="flat", cursor="hand2",
                  padx=14, pady=6, bd=0, command=command,
                  activebackground=bg_h, activeforeground=fg, **kw)
    b.bind("<Enter>", lambda _: b.config(bg=bg_h))
    b.bind("<Leave>", lambda _: b.config(bg=bg))
    b.bind("<ButtonPress-1>",   lambda _: b.config(bg=bg_h))
    b.bind("<ButtonRelease-1>", lambda _: b.config(bg=bg_h))
    return b


def search_box(parent: tk.Misc, var: tk.StringVar, width: int = 22) -> tk.Frame:
    outer = tk.Frame(parent, bg=C_SURFACE, highlightthickness=1,
                     highlightbackground=C_BORDER)
    tk.Label(outer, text="🔍", bg=C_SURFACE,
             font=("Segoe UI", 10)).pack(side="left", padx=(8, 2))
    e = tk.Entry(outer, textvariable=var, relief="flat",
                 font=("Segoe UI", 11), width=width,
                 bg=C_SURFACE, fg=C_TEXT)
    e.pack(side="left", ipady=6, padx=(0, 8))

    def _in(_: Any) -> None:
        outer.config(highlightbackground=C_PRIMARY, highlightthickness=2)
    def _out(_: Any) -> None:
        outer.config(highlightbackground=C_BORDER, highlightthickness=1)
    e.bind("<FocusIn>",  _in)  # type: ignore[arg-type]
    e.bind("<FocusOut>", _out)  # type: ignore[arg-type]
    return outer


def page_header(parent: tk.Misc, text: str, icon: str = "") -> tk.Frame:
    frm = tk.Frame(parent, bg=C_BG)

    # Accent top bar (gradient simulation with two frames)
    accent = tk.Frame(frm, bg=C_PRIMARY, height=3)
    accent.pack(fill="x")

    row = tk.Frame(frm, bg=C_BG)
    row.pack(fill="x", padx=20, pady=(12, 6))

    if icon:
        tk.Label(row, text=icon, bg=C_BG,
                 font=("Segoe UI", 22)).pack(side="left", padx=(0, 10))
    tk.Label(row, text=text, bg=C_BG, fg=C_DARK,
             font=F_TITLE).pack(side="left")

    # Breadcrumb divider
    tk.Frame(frm, bg=C_BORDER, height=1).pack(fill="x", padx=20, pady=(0, 8))
    return frm


def make_card(parent: tk.Widget, padx: int = 16, pady: int = 14,
              shadow: bool = True, **kw: Any) -> tuple[tk.Frame, tk.Frame]:
    """Returns (outer_frame, content_frame).
    Pack/grid the outer_frame; add widgets to content_frame.
    The outer frame simulates a drop shadow."""
    if shadow:
        outer = tk.Frame(parent, bg=C_SHADOW)
        content = tk.Frame(outer, bg=C_SURFACE, padx=padx, pady=pady, **kw)
        content.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))
    else:
        outer = tk.Frame(parent, bg=C_SURFACE,
                         highlightthickness=1,
                         highlightbackground=C_BORDER,
                         padx=padx, pady=pady, **kw)
        content = outer
    return outer, content


def make_tree(parent: tk.Misc, columns: tuple[str, ...] | list[str],
              headers: tuple[str, ...] | list[str],
              widths: tuple[int, ...] | list[int],
              height: int = 0) -> ttk.Treeview:
    if height:
        tree = ttk.Treeview(parent, style="TV.Treeview", columns=columns,
                            show="headings", height=height)
    else:
        tree = ttk.Treeview(parent, style="TV.Treeview", columns=columns,
                            show="headings")
    for col, hdr, w in zip(columns, headers, widths):
        tree.heading(col, text=hdr)
        tree.column(col, width=w, anchor="center", minwidth=40)
    _tag_cfg(tree)
    return tree


def _tag_cfg(tree: ttk.Treeview) -> None:
    tree.tag_configure("odd",       background=ROW_ODD)
    tree.tag_configure("even",      background=ROW_EVEN)
    tree.tag_configure("Da duyet",  background=C_SUCCESS_BG, foreground=C_SUCCESS)
    tree.tag_configure("Cho duyet", background=C_WARNING_BG, foreground=C_WARNING)
    tree.tag_configure("Tu choi",   background=C_DANGER_BG,  foreground=C_DANGER)
    tree.tag_configure("Hoat dong", background=C_SUCCESS_BG, foreground=C_SUCCESS)
    tree.tag_configure("Bao tri",   background=C_WARNING_BG, foreground=C_WARNING)
    tree.tag_configure("Khoa",      background=C_DANGER_BG,  foreground=C_DANGER)


def fill_tree(tree: ttk.Treeview, rows: list[tuple[object, ...]]) -> None:
    for item in tree.get_children():
        tree.delete(item)
    for i, values in enumerate(rows):
        tags = ["odd" if i % 2 == 0 else "even"]
        status = str(values[-1]) if values else ""
        if status in ("Da duyet", "Cho duyet", "Tu choi",
                      "Hoat dong", "Bao tri", "Khoa"):
            tags.append(status)
        tree.insert("", "end", values=values, tags=tags)


def with_scrollbar(parent: tk.Misc, tree: ttk.Treeview) -> None:
    vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)  # type: ignore[arg-type]
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")


class MiniProgressBar(tk.Canvas):
    """Thin horizontal progress bar drawn on Canvas."""
    def __init__(self, parent: tk.Widget, value: float, total: float,
                 color: str = C_PRIMARY, height: int = 5,
                 width: int = 160) -> None:
        super().__init__(parent, width=width, height=height,
                         bg="white", highlightthickness=0)
        self._color  = color
        self._h      = height
        self._value  = value
        self._total  = total
        self.bind("<Configure>", lambda _: self._draw())
        self.after(10, self._draw)

    def _draw(self) -> None:
        self.delete("all")
        w = self.winfo_width() or 160
        # Track (rounded appearance via rectangle)
        self.create_rectangle(0, 0, w, self._h, fill="#e2e8f0", outline="")
        if self._total > 0:
            fill_w = int(w * min(self._value / self._total, 1.0))
            if fill_w > 0:
                self.create_rectangle(0, 0, fill_w, self._h,
                                      fill=self._color, outline="")
