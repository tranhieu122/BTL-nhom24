# gui/theme.py  –  shared palette, fonts, widget factories
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Any

# ── Palette: Modern Indigo / Slate ──────────────────────────────────────────
C_DARK       = "#0f172a"     # Slate 900
C_PRIMARY    = "#4f46e5"     # Indigo 600
C_PRIMARY_H  = "#4338ca"     # Indigo 700  (hover/pressed)
C_ACCENT     = "#6366f1"     # Indigo 500  (glow/highlight)
C_LIGHT      = "#818cf8"     # Indigo 400
C_BG         = "#f8fafc"     # Slate 50
C_SURFACE    = "#ffffff"
C_BORDER     = "#e2e8f0"     # Slate 200
C_SHADOW     = "#c7d2fe"     # Indigo 200  (shadow)
C_TEXT       = "#1e293b"     # Slate 800
C_MUTED      = "#64748b"     # Slate 500
C_SUCCESS    = "#16a34a"
C_SUCCESS_BG = "#dcfce7"
C_WARNING    = "#b45309"
C_WARNING_BG = "#fef3c7"
C_DANGER     = "#dc2626"
C_DANGER_BG  = "#fee2e2"
C_INFO_BG    = "#eef2ff"     # Indigo 50
ROW_ODD      = "#fafafa"
ROW_EVEN     = "#ffffff"

# ── Typography Scale (8pt base, 4px grid) ────────────────────────────────────
# Heading  : 20 bold  → page titles
# SubHead  : 14 bold  → section headers / dialog titles
# Body     : 10 reg   → content, labels
# BodyBold : 10 bold  → emphasis
# Small    :  9 reg   → captions, hints
# Input    : 11 reg   → form entries
# Button   : 10 bold  → CTAs
F_TITLE   = ("Segoe UI", 20, "bold")
F_SECTION = ("Segoe UI", 14, "bold")
F_BODY    = ("Segoe UI", 10)
F_BODY_B  = ("Segoe UI", 10, "bold")
F_SMALL   = ("Segoe UI",  9)
F_INPUT   = ("Segoe UI", 11)
F_BTN     = ("Segoe UI", 10, "bold")


def apply_theme(style: ttk.Style) -> None:
    """Call once at app start to configure all ttk styles."""
    style.theme_use("clam")

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure("TV.Treeview.Heading",
                    background=C_PRIMARY, foreground="white",
                    font=F_BODY_B, relief="flat", padding=11)
    style.map("TV.Treeview.Heading",
              background=[("active", C_PRIMARY_H)])
    style.configure("TV.Treeview",
                    rowheight=36, font=F_BODY,
                    fieldbackground=C_SURFACE, background=C_SURFACE,
                    borderwidth=0, relief="flat")
    style.map("TV.Treeview",
              background=[("selected", "#e0e7ff")],
              foreground=[("selected", "#3730a3")])

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
              background=[("active", "#4338ca"), ("pressed", "#4338ca")])


def btn(parent: tk.Misc, text: str, command: Any, variant: str = "primary",
    icon: str = "", **kw: Any) -> tk.Button:
    """Themed button with smooth hover + press transitions."""
    label = f"{icon}  {text}" if icon else text
    colours = {
        "primary": (C_PRIMARY,    C_PRIMARY_H,  "white"),
        "success": ("#16a34a",    "#15803d",    "white"),
        "danger":  (C_DANGER,     "#b91c1c",    "white"),
        "ghost":   ("#f1f5f9",    "#e2e8f0",    C_TEXT),
        "outline": (C_SURFACE,    C_INFO_BG,    C_PRIMARY),
        "accent":  (C_ACCENT,     C_PRIMARY_H,  "white"),
    }
    bg, bg_h, fg = colours.get(variant, colours["primary"])
    b = tk.Button(parent, text=label, bg=bg, fg=fg,
                  font=F_BTN, relief="flat", cursor="hand2",
                  padx=16, pady=7, bd=0, command=command,
                  activebackground=bg_h, activeforeground=fg, **kw)
    b.bind("<Enter>",           lambda _: b.config(bg=bg_h))
    b.bind("<Leave>",           lambda _: b.config(bg=bg))
    b.bind("<ButtonPress-1>",   lambda _: b.config(bg=bg_h))
    b.bind("<ButtonRelease-1>", lambda _: b.config(bg=bg_h))
    return b


def search_box(parent: tk.Misc, var: tk.StringVar, width: int = 22,
               command: Any = None) -> tk.Frame:
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
    if command is not None:
        e.bind("<Return>", lambda _: command())  # type: ignore[arg-type]
    return outer


def page_header(parent: tk.Misc, text: str, icon: str = "") -> tk.Frame:
    frm = tk.Frame(parent, bg=C_BG)

    # Gradient accent bar: solid Indigo 600 stripe
    tk.Frame(frm, bg=C_PRIMARY, height=4).pack(fill="x")

    row = tk.Frame(frm, bg=C_BG)
    row.pack(fill="x", padx=20, pady=(14, 6))

    if icon:
        # Icon in a pill background
        ic_bg = tk.Frame(row, bg="#eef2ff", padx=8, pady=4)
        ic_bg.pack(side="left", padx=(0, 12))
        tk.Label(ic_bg, text=icon, bg="#eef2ff",
                 font=("Segoe UI", 18)).pack()
    tk.Label(row, text=text, bg=C_BG, fg=C_DARK,
             font=F_TITLE).pack(side="left")

    # Subtle divider
    tk.Frame(frm, bg=C_BORDER, height=1).pack(fill="x", padx=20, pady=(0, 8))
    return frm


def make_card(parent: tk.Widget, padx: int = 20, pady: int = 16,
              shadow: bool = True, **kw: Any) -> tuple[tk.Frame, tk.Frame]:
    """Returns (outer_frame, content_frame). Deeper shadow for premium feel."""
    if shadow:
        # Two-layer shadow: mid + dark bottom-right offset
        shadow_outer = tk.Frame(parent, bg="#c7d2fe")   # indigo-200 shadow
        shadow_inner = tk.Frame(shadow_outer, bg="#a5b4fc")  # indigo-300
        shadow_inner.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))
        content = tk.Frame(shadow_inner, bg=C_SURFACE, padx=padx, pady=pady, **kw)
        content.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
        outer = shadow_outer
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


# ── Shared UI helpers used by multiple screens ─────────────────────────────

def labeled_entry(parent: tk.Misc, label: str, var: tk.StringVar,
                  icon: str = "", show: str = "",
                  width: int = 32) -> tuple[tk.Frame, tk.Entry]:
    """Labeled, focus-bordered entry with icon and crisp focus ring."""
    tk.Label(parent, text=label, bg=C_SURFACE, fg=C_MUTED,
             font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(12, 0))
    outer = tk.Frame(parent, bg=C_BORDER, padx=1, pady=1)  # border via padding
    outer.pack(fill="x", pady=(3, 0))
    inner_bg = tk.Frame(outer, bg=C_SURFACE)
    inner_bg.pack(fill="both", expand=True)
    inner = tk.Frame(inner_bg, bg=C_SURFACE)
    inner.pack(fill="x")
    if icon:
        tk.Label(inner, text=icon, bg=C_SURFACE,
                 font=("Segoe UI", 13)).pack(side="left", padx=(10, 4), pady=8)
    e = tk.Entry(inner, textvariable=var, width=width, show=show,
                 font=F_INPUT, relief="flat", bg=C_SURFACE, fg=C_TEXT,
                 insertbackground=C_PRIMARY)
    e.pack(side="left", padx=(0 if icon else 12, 10), pady=9,
           fill="x", expand=True)

    def _in(_: Any) -> None:
        outer.config(bg=C_PRIMARY)          # 1px indigo ring on focus
    def _out(_: Any) -> None:
        outer.config(bg=C_BORDER)
    e.bind("<FocusIn>",  _in)   # type: ignore[arg-type]
    e.bind("<FocusOut>", _out)  # type: ignore[arg-type]
    return outer, e


def status_badge(parent: tk.Misc, text: str, bg: str = C_SURFACE) -> tk.Label:
    """Pill-shaped status chip with soft Indigo-tuned colors."""
    PRESETS: dict[str, tuple[str, str]] = {
        "Hoat dong": ("#dcfce7", "#15803d"),
        "Da duyet":  ("#dcfce7", "#15803d"),
        "Cho duyet": ("#fef3c7", "#b45309"),
        "Bao tri":   ("#fef3c7", "#b45309"),
        "Tu choi":   ("#fee2e2", "#dc2626"),
        "Khoa":      ("#fee2e2", "#dc2626"),
        "Hong":      ("#fee2e2", "#dc2626"),
        "Admin":     ("#eef2ff", "#4f46e5"),   # Indigo chip for Admin
        "Giang vien":("#dcfce7", "#15803d"),
        "Sinh vien": ("#fef9c3", "#854d0e"),
    }
    chip_bg, chip_fg = PRESETS.get(text, ("#f1f5f9", C_MUTED))
    return tk.Label(parent, text=f"  {text}  ",
                    bg=chip_bg, fg=chip_fg,
                    font=("Segoe UI", 8, "bold"),
                    padx=2, pady=2)


def pw_strength_bar(parent: tk.Misc, var: tk.StringVar,
                    bg: str = C_SURFACE) -> tk.Frame:
    """Returns a frame containing a live password-strength indicator."""
    frame = tk.Frame(parent, bg=bg)
    bar_bg = tk.Frame(frame, bg="#e2e8f0", height=5)
    bar_bg.pack(fill="x", pady=(3, 0))
    bar_fill = tk.Frame(bar_bg, bg="#e2e8f0", height=5)
    bar_fill.place(x=0, y=0, relheight=1.0, relwidth=0)
    lbl = tk.Label(frame, text="", bg=bg, fg=C_MUTED,
                   font=("Segoe UI", 8))
    lbl.pack(anchor="w")

    def _update(*_: Any) -> None:
        pw = var.get()
        length = len(pw)
        score = 0
        if length >= 6:  score += 1
        if length >= 10: score += 1
        import re
        if re.search(r"[A-Z]", pw): score += 1
        if re.search(r"[0-9]", pw): score += 1
        if re.search(r"[^A-Za-z0-9]", pw): score += 1
        levels = [
            (0,  0.0,  "#e2e8f0", ""),
            (1,  0.2,  "#ef4444", "Rat yeu"),
            (2,  0.4,  "#f97316", "Yeu"),
            (3,  0.6,  "#eab308", "Trung binh"),
            (4,  0.8,  "#22c55e", "Manh"),
            (5,  1.0,  "#16a34a", "Rat manh"),
        ]
        _, rel, color, text = levels[min(score, 5)] # type: ignore
        bar_fill.place(relwidth=rel)
        bar_fill.config(bg=color)
        lbl.config(text=text, fg=color if text else C_MUTED)

    var.trace_add("write", _update)
    return frame


def eye_toggle(parent: tk.Misc, entry: tk.Entry,
               bg: str = C_SURFACE) -> tk.Label:
    """Eye icon that toggles password visibility. Place it inside entry's row."""
    _shown = [False]
    lbl = tk.Label(parent, text="👁", bg=bg, fg=C_MUTED,
                   font=("Segoe UI", 11), cursor="hand2")

    def _toggle(_: Any = None) -> None:
        _shown[0] = not _shown[0]
        entry.config(show="" if _shown[0] else "*")
        lbl.config(fg=C_PRIMARY if _shown[0] else C_MUTED)

    lbl.bind("<Button-1>", _toggle)
    return lbl


def toast(master: tk.Misc, message: str, kind: str = "success",
          duration_ms: int = 2800) -> None:
    """Show a short non-blocking toast notification at the bottom-right.
    kind: "success" | "error" | "info" | "warning"
    """
    COLORS = {
        "success": ("#dcfce7", "#15803d", "✔"),
        "error":   ("#fee2e2", "#dc2626", "✖"),
        "info":    ("#dbeafe", "#1d4ed8", "ℹ"),
        "warning": ("#fef3c7", "#b45309", "⚠"),
    }
    bg, fg, icon = COLORS.get(kind, COLORS["info"])

    # Find the root window
    root = master.winfo_toplevel()  # type: ignore[union-attr]

    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True) # type: ignore
    popup.configure(bg=bg)

    frame = tk.Frame(popup, bg=bg, padx=14, pady=10,
                     highlightthickness=1, highlightbackground=fg)
    frame.pack()
    tk.Label(frame, text=icon, bg=bg, fg=fg,
             font=("Segoe UI", 12)).pack(side="left", padx=(0, 8))
    tk.Label(frame, text=message, bg=bg, fg=fg,
             font=("Segoe UI", 10, "bold"), wraplength=320).pack(side="left")

    def _place() -> None:
        popup.update_idletasks()
        rx = root.winfo_x() + root.winfo_width()
        ry = root.winfo_y() + root.winfo_height()
        pw, ph = popup.winfo_width(), popup.winfo_height()
        popup.geometry(f"+{rx - pw - 20}+{ry - ph - 40}")

    popup.after(10, _place)
    popup.after(duration_ms, popup.destroy)


def tooltip(widget: tk.Widget, text: str) -> None:
    """Attach a lightweight hover tooltip to a widget."""
    tip: list[tk.Toplevel | None] = [None]

    def _show(_: Any = None) -> None:
        if tip[0] or not widget.winfo_exists():
            return
        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 6
        popup = tk.Toplevel(widget)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)  # type: ignore[arg-type]
        frame = tk.Frame(popup, bg="#1e1b4b", padx=9, pady=5,
                         highlightthickness=1, highlightbackground="#4f46e5")
        frame.pack()
        tk.Label(frame, text=text, bg="#1e1b4b", fg="#e0e7ff",
                 font=("Segoe UI", 8)).pack()
        popup.update_idletasks()
        pw = popup.winfo_width()
        popup.geometry(f"+{x - pw // 2}+{y}")
        tip[0] = popup

    def _hide(_: Any = None) -> None:
        if tip[0]:
            try:
                tip[0].destroy()
            except Exception:
                pass
            tip[0] = None

    widget.bind("<Enter>", _show, add="+")
    widget.bind("<Leave>", _hide, add="+")


def confirm_dialog(parent: tk.Misc, title: str, message: str,
                   ok_text: str = "Xac nhan", cancel_text: str = "Huy",
                   kind: str = "warning") -> bool:
    """Styled modal confirmation dialog. Returns True if user clicks OK."""
    COLORS: dict[str, tuple[str, str, str]] = {
        "warning": ("#fef3c7", "#b45309", "#f59e0b"),
        "danger":  ("#fee2e2", "#dc2626", "#ef4444"),
        "info":    ("#eef2ff", "#4f46e5", "#4f46e5"),
    }
    ICONS: dict[str, str] = {"warning": "⚠", "danger": "🗑", "info": "ℹ"}
    bg, fg, hdr_bg = COLORS.get(kind, COLORS["warning"])
    icon = ICONS.get(kind, "?")

    root = parent.winfo_toplevel()  # type: ignore[union-attr]
    dlg = tk.Toplevel(root)
    dlg.title(title)
    dlg.resizable(False, False)
    dlg.configure(bg=C_SURFACE)
    dlg.transient(root)  # type: ignore[arg-type]
    dlg.grab_set()
    result = [False]

    hdr = tk.Frame(dlg, bg=hdr_bg, padx=20, pady=12)
    hdr.pack(fill="x")
    tk.Label(hdr, text=f"  {icon}  {title}", bg=hdr_bg, fg="white",
             font=("Segoe UI", 11, "bold")).pack(anchor="w")

    body = tk.Frame(dlg, bg=C_SURFACE, padx=24, pady=20)
    body.pack(fill="x")
    msg_box = tk.Frame(body, bg=bg, highlightthickness=1,
                       highlightbackground=fg)
    msg_box.pack(fill="x", pady=(0, 16))
    tk.Label(msg_box, text=message, bg=bg, fg=fg,
             font=("Segoe UI", 10), wraplength=340,
             justify="left", anchor="w").pack(padx=12, pady=10)

    btn_row = tk.Frame(body, bg=C_SURFACE)
    btn_row.pack(fill="x")

    def _ok() -> None:
        result[0] = True
        dlg.destroy()

    def _cancel() -> None:
        dlg.destroy()

    btn(btn_row, ok_text, _ok,
        variant="danger" if kind == "danger" else "primary").pack(side="right")
    btn(btn_row, cancel_text, _cancel,
        variant="ghost").pack(side="right", padx=8)

    dlg.update_idletasks()
    rx = root.winfo_x() + root.winfo_width() // 2
    ry = root.winfo_y() + root.winfo_height() // 2
    dlg.geometry(f"+{rx - dlg.winfo_width() // 2}+{ry - dlg.winfo_height() // 2}")
    dlg.bind("<Return>", lambda _: _ok())
    dlg.bind("<Escape>", lambda _: _cancel())
    dlg.wait_window()
    return result[0]
