# gui/theme.py  –  shared palette, fonts, widget factories
from __future__ import annotations
import datetime as _dt
import tkinter as tk
from tkinter import ttk
from typing import Any

# ── Palette: Nebula Slate & Indigo ──────────────────────────────────────────
# Modern dark theme with Slate depths and Indigo accents
PALETTES = {
    "dark": {
        "SLATE_900":    "#0f172a",
        "SLATE_800":    "#1e293b",
        "SLATE_700":    "#334155",
        "SLATE_600":    "#475569",
        "SLATE_500":    "#64748b",
        "SLATE_400":    "#94a3b8",
        "SLATE_300":    "#cbd5e1",
        "SLATE_200":    "#e2e8f0",
        "SLATE_100":    "#f1f5f9",
        "SLATE_50":     "#f8fafc",
        "INDIGO_500":   "#6366f1",
        "INDIGO_400":   "#818cf8",
        "INDIGO_200":   "#c7d2fe",
        "INDIGO_100":   "#e0e7ff",
        "EMERALD_500":  "#10b981",
        "EMERALD_100":  "#d1fae5",
        "EMERALD_800":  "#065f46",
        "ROSE_500":     "#f43f5e",
        "ROSE_100":     "#ffe4e6",
        "ROSE_800":     "#831843",
        "AMBER_400":    "#fbbf24",
        "AMBER_100":    "#fef3c7",
        "AMBER_200":    "#fde68a",
        "AMBER_800":    "#78350f",
        "PURPLE_100":   "#ede9fe",
        "PURPLE_800":   "#5b21b6",
        "BG":           "#020617",     # Deep navy background
        "SURFACE":      "#0f172a",     # Card surface
        "BORDER":       "#1e293b",     # Muted slate border
        "TEXT":         "#f8fafc",     # Light text
        "MUTED":        "#94a3b8",     # Muted text
        "SUCCESS":      "#10b981",
        "SUCCESS_BG":   "#064e3b",     # Emerald 900
        "DANGER":       "#f43f5e",
        "DANGER_BG":    "#881337",     # Rose 900
        "WARNING":      "#fbbf24",
        "WARNING_BG":   "#78350f",     # Amber 900
        "ACCENT":       "#6366f1",
        "PRIMARY":      "#6366f1",     # Indigo 500
        "PRIMARY_H":    "#818cf8",     # Indigo 400
        "LIGHT":        "#818cf8",
        "INFO_BG":      "#0f172a",
        "ROW_ODD":      "#0f172a",
        "ROW_EVEN":     "#1e293b",
        "SB_BG":        "#020618",     # Unique deep navy for sidebar
        "SB_HOVER":     "#1e293c",     # Unique hover
        "SB_ACTIVE":    "#4f46e6",     # Unique indigo
        "SB_ACCENT":    "#6366f2",     # Unique accent
        "SB_TEXT":      "#ffffff",     # Pure white for text
        "_LG_BG":       "#1e1b4b",     # Indigo 950 (login panel background)
        "_LG_MID":      "#312e81",     # Indigo 900
        "_LG_GLOW":     "#4f46e5",     # Indigo 600
        "_LG_TEXT":     "#e0e7ff",     # Indigo 100
        "_LG_MUTED":    "#818cf8",     # Indigo 400
        "SHADOW":       "#334155",     # Slate 700 (shadow)
    },
    "light": {
        "SLATE_900":    "#0f172a",
        "SLATE_800":    "#f8fafc",
        "SLATE_700":    "#e2e8f0",
        "SLATE_600":    "#cbd5e1",
        "SLATE_500":    "#94a3b8",
        "SLATE_400":    "#64748b",
        "SLATE_300":    "#475569",
        "SLATE_200":    "#1e293b",
        "SLATE_100":    "#0f172a",
        "SLATE_50":     "#020617",
        "INDIGO_500":   "#4f46e5",
        "INDIGO_400":   "#6366f1",
        "INDIGO_200":   "#eef2ff",
        "INDIGO_100":   "#e0e7ff",
        "EMERALD_500":  "#10b981",
        "EMERALD_100":  "#d1fae5",
        "EMERALD_800":  "#065f46",
        "ROSE_500":     "#f43f5e",
        "ROSE_100":     "#ffe4e6",
        "ROSE_800":     "#831843",
        "AMBER_400":    "#fbbf24",
        "AMBER_100":    "#fef3c7",
        "AMBER_200":    "#fde68a",
        "AMBER_800":    "#78350f",
        "PURPLE_100":   "#ede9fe",
        "PURPLE_800":   "#5b21b6",
        "BG":           "#f8fafc",     # Light grey background
        "SURFACE":      "#ffffff",     # White cards
        "BORDER":       "#e2e8f0",     # Soft borders
        "TEXT":         "#0f172a",     # Deep navy text
        "MUTED":        "#64748b",     # Muted text
        "SUCCESS":      "#10b981",
        "SUCCESS_BG":   "#d1fae5",     # Emerald 100
        "DANGER":       "#f43f5e",
        "DANGER_BG":    "#ffe4e6",     # Rose 100
        "WARNING":      "#fbbf24",
        "WARNING_BG":   "#fef3c7",     # Amber 100
        "ACCENT":       "#4f46e5",
        "PRIMARY":      "#4f46e5",     # Indigo 600
        "PRIMARY_H":    "#6366f1",     # Indigo 500
        "LIGHT":        "#6366f1",
        "INFO_BG":      "#eff6ff",
        "ROW_ODD":      "#ffffff",
        "ROW_EVEN":     "#f1f5f9",
        "SB_BG":        "#ffffff",     # White sidebar for Light mode
        "SB_HOVER":     "#f1f5f9",
        "SB_ACTIVE":    "#4f46e5",
        "SB_ACCENT":    "#6366f1",
        "SB_TEXT":      "#0f172a",
        "_LG_BG":       "#1e1b4b",     # Indigo 950 (login panel background)
        "_LG_MID":      "#312e81",     # Indigo 900
        "_LG_GLOW":     "#4f46e5",     # Indigo 600
        "_LG_TEXT":     "#e0e7ff",     # Indigo 100
        "_LG_MUTED":    "#818cf8",     # Indigo 400
        "SHADOW":       "#334155",     # Slate 700 (shadow)
    }
}

# Current active theme
CURRENT_THEME = "light"

# Typography Scale - Nebula Slate
FONT_H1 = ("Inter", 22, "bold")
FONT_H2 = ("Inter", 18, "bold")
FONT_H3 = ("Inter", 15, "bold")
FONT_BODY = ("Inter", 13)
FONT_CAPTION = ("Inter", 11)

# Fallback fonts
try:
    import tkinter.font as tkfont
    if not tkfont.families().count("Inter"):
        FONT_H1 = ("Segoe UI", 22, "bold") # type: ignore
        FONT_H2 = ("Segoe UI", 18, "bold") # type: ignore
        FONT_H3 = ("Segoe UI", 15, "bold") # type: ignore
        FONT_BODY = ("Segoe UI", 13) # type: ignore
        FONT_CAPTION = ("Segoe UI", 11) # type: ignore
except:
    pass

FONT_BODY_BOLD = (FONT_BODY[0], FONT_BODY[1], "bold")

# Proxies for global constants (to avoid breaking existing imports)
def _get_c(key: str) -> str:
    return PALETTES[CURRENT_THEME][key]

# Legacy color constants for backward compatibility
C_DARK = _get_c("SLATE_900")
C_PRIMARY = _get_c("PRIMARY")
C_PRIMARY_H = _get_c("PRIMARY_H")
C_ACCENT = _get_c("ACCENT")
C_LIGHT = _get_c("LIGHT")
C_BG = _get_c("BG")
C_SURFACE = _get_c("SURFACE")
C_BORDER = _get_c("BORDER")
C_SHADOW = _get_c("SLATE_700")
C_TEXT = _get_c("TEXT")
C_MUTED = _get_c("MUTED")
C_SUCCESS = _get_c("SUCCESS")
C_SUCCESS_BG = _get_c("SUCCESS_BG")
C_WARNING = _get_c("WARNING")
C_WARNING_BG = _get_c("WARNING_BG")
C_DANGER = _get_c("DANGER")
C_DANGER_BG = _get_c("DANGER_BG")
C_INFO_BG = _get_c("INFO_BG")
ROW_ODD = _get_c("ROW_ODD")
ROW_EVEN = _get_c("ROW_EVEN")
SB_BG = _get_c("SB_BG")
SB_HOVER = _get_c("SB_HOVER")
SB_ACTIVE = _get_c("SB_ACTIVE")
SB_ACCENT = _get_c("SB_ACCENT")
SB_TEXT = _get_c("SB_TEXT")

# ── Typography Scale (Nebula Slate) ────────────────────────────────────
# Modern font hierarchy with Inter as primary, Segoe UI fallback
F_TITLE   = FONT_H1      # 22pt bold - page titles
F_SECTION = FONT_H2      # 18pt bold - section headers
F_BODY    = FONT_BODY    # 13pt reg - content, labels
F_BODY_B  = ("Inter", 13, "bold")  # 13pt bold - emphasis
F_SMALL   = FONT_CAPTION # 11pt reg - captions, hints
F_INPUT   = ("Inter", 13) # 13pt reg - form entries
F_BTN     = ("Inter", 13, "bold") # 13pt bold - CTAs

# Legacy/Compatibility aliases
FONT_BODY = F_BODY # type: ignore
FONT_BODY_BOLD = F_BODY_B # type: ignore


def apply_theme(style: ttk.Style) -> None:
    """Call once at app start to configure all ttk styles."""
    style.theme_use("clam")

    def _global_mouse_scroll(e: Any) -> None:
        try:
            # If the specific widget under the mouse already handles MouseWheel, do nothing to prevent double-scroll
            if e.widget.bind("<MouseWheel>"):
                return
        except Exception:
            pass

        w = e.widget
        delta = -1 * (e.delta // 120) if hasattr(e, "delta") and e.delta else 0
        if not delta:
            return

        while w:
            if isinstance(w, (tk.Canvas, ttk.Treeview)):
                try:
                    # Check if it is actually scrollable vertically
                    if w.cget("yscrollcommand"):
                        w.yview_scroll(delta, "units")
                        return
                except Exception:
                    pass
            w = getattr(w, "master", None)

    try:
        style.master.bind_all("<MouseWheel>", _global_mouse_scroll, add="+")
    except Exception:
        pass

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure("TV.Treeview.Heading",
                    background=C_PRIMARY, foreground="white",
                    font=F_BODY_B, relief="flat", padding=11)
    style.map("TV.Treeview.Heading",
              background=[("active", C_PRIMARY_H)])
    style.configure("TV.Treeview",
                    rowheight=36, font=F_BODY,
                    fieldbackground=C_BG, background=C_BG,
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
                    background=_get_c("SURFACE"), fieldbackground=_get_c("SURFACE"),
                    foreground=_get_c("TEXT"), bordercolor=_get_c("BORDER"),
                    arrowcolor=_get_c("PRIMARY"), relief="flat", padding=4)
def switch_theme(root: tk.Tk) -> None:
    """Toggle between light and dark mode and refresh all widgets."""
    global CURRENT_THEME, C_DARK, C_PRIMARY, C_PRIMARY_H, C_ACCENT, C_LIGHT, \
        C_BG, C_SURFACE, C_BORDER, C_SHADOW, C_TEXT, C_MUTED, C_SUCCESS, \
        C_SUCCESS_BG, C_WARNING, C_WARNING_BG, C_DANGER, C_DANGER_BG, \
        C_INFO_BG, ROW_ODD, ROW_EVEN, SB_BG, SB_HOVER, SB_ACTIVE, SB_ACCENT, SB_TEXT

    CURRENT_THEME = "dark" if CURRENT_THEME == "light" else "light" # type: ignore

    # Update global variables from the new palette
    p = PALETTES[CURRENT_THEME]
    C_DARK       = p["SLATE_900"] # type: ignore
    C_PRIMARY    = p["PRIMARY"] # type: ignore
    C_PRIMARY_H  = p["PRIMARY_H"] # type: ignore
    C_ACCENT     = p["ACCENT"] # type: ignore
    C_LIGHT      = p["LIGHT"] # type: ignore
    C_BG         = p["BG"] # type: ignore
    C_SURFACE    = p["SURFACE"] # type: ignore
    C_BORDER     = p["BORDER"] # type: ignore
    C_SHADOW     = p["SLATE_700"] # type: ignore
    C_TEXT       = p["TEXT"] # type: ignore
    C_MUTED      = p["MUTED"] # pyright: ignore[reportConstantRedefinition]
    C_SUCCESS    = p["SUCCESS"] # pyright: ignore[reportConstantRedefinition]
    C_SUCCESS_BG = p["SUCCESS_BG"] # pyright: ignore[reportConstantRedefinition]
    C_DANGER     = p["DANGER"] # pyright: ignore[reportConstantRedefinition]
    C_DANGER_BG  = p["DANGER_BG"] # pyright: ignore[reportConstantRedefinition]
    C_WARNING    = p["WARNING"] # pyright: ignore[reportConstantRedefinition]
    C_WARNING_BG = p["WARNING_BG"] # pyright: ignore[reportConstantRedefinition]
    C_INFO_BG    = p["INFO_BG"] # pyright: ignore[reportConstantRedefinition]
    ROW_ODD      = p["ROW_ODD"] # pyright: ignore[reportConstantRedefinition]
    ROW_EVEN     = p["ROW_EVEN"] # pyright: ignore[reportConstantRedefinition]
    SB_BG        = p["SB_BG"] # pyright: ignore[reportConstantRedefinition]
    SB_HOVER     = p["SB_HOVER"] # pyright: ignore[reportConstantRedefinition]
    SB_ACTIVE    = p["SB_ACTIVE"] # pyright: ignore[reportConstantRedefinition]
    SB_ACCENT    = p["SB_ACCENT"] # pyright: ignore[reportConstantRedefinition]
    SB_TEXT      = p["SB_TEXT"] # pyright: ignore[reportConstantRedefinition]

    # Re-apply ttk styles
    apply_theme(ttk.Style(root))

    # Map of old color -> new color for the current theme
    # Build color mapping from old theme to new theme
    COLOR_MAP = {}
    
    # Fill from both palettes to cover all bases
    for theme_name in ["light", "dark"]:
        # Process generic colors first
        for key, val in PALETTES[theme_name].items():
            COLOR_MAP[val.lower()] = PALETTES[CURRENT_THEME][key]
            
    # Re-process critical semantic keys LAST to ensure they win collisions
    priority_keys = ["BG", "SURFACE", "SB_BG", "TEXT", "SB_TEXT", "SB_ACTIVE", "ACCENT"]
    for theme_name in ["light", "dark"]:
        for key in priority_keys:
            if key in PALETTES[theme_name]:
                val = PALETTES[theme_name][key]
                COLOR_MAP[val.lower()] = PALETTES[CURRENT_THEME][key]

    def _refresh_widget(widget: Any):
        if not widget.winfo_exists():
            return
        
        # Update standard widget configs
        try:
            cfg = widget.config()
            updates = {}
            for attr in ("bg", "background", "fg", "foreground", "highlightbackground", "activebackground"):
                if attr in cfg:
                    curr = str(widget.cget(attr)).lower()
                    if curr in COLOR_MAP:
                        updates[attr] = COLOR_MAP[curr]
            if updates:
                widget.config(**updates)
        except Exception:
            pass

        # Update Canvas items
        if isinstance(widget, tk.Canvas):
            for item in widget.find_all():
                for attr in ("fill", "outline"):
                    try:
                        curr = str(widget.itemcget(item, attr)).lower() # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                        if curr in COLOR_MAP:
                            widget.itemconfigure(item, {attr: COLOR_MAP[curr]})
                    except Exception:
                        pass

        # Recurse through children
        for child in widget.winfo_children():
            _refresh_widget(child)

    # Start recursion from root
    _refresh_widget(root)

    # Special case: Notify shell to update logo and toggle icons
    try:
        if hasattr(root, "_refresh_theme_icons"):
            root._refresh_theme_icons() # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        else:
            for child in root.winfo_children():
                if hasattr(child, "_refresh_theme_icons"):
                    child._refresh_theme_icons() # type: ignore
    except Exception:
        pass
            
    except Exception: # type: ignore
        pass


def btn(parent: tk.Misc, text: str, command: Any, variant: str = "primary",
    icon: str = "", **kw: Any) -> tk.Button:
    """Themed button with dynamic theme-aware hover transitions."""
    label = f"{icon}  {text}" if icon else text
    
    def _get_variant_colors() -> tuple[str, str, str]:
        if variant == "success":
            return (_get_c("SUCCESS"), _get_c("SUCCESS"), "white")
        if variant == "danger":
            return (_get_c("DANGER"), _get_c("DANGER"), "white")
        if variant == "ghost":
            return (_get_c("SB_BG"), _get_c("SB_HOVER"), _get_c("SB_TEXT"))
        if variant == "outline":
            return (_get_c("SURFACE"), _get_c("INFO_BG"), _get_c("ACCENT"))
        if variant == "accent":
            return (_get_c("ACCENT"), _get_c("LIGHT"), "white")
        # primary
        return (_get_c("PRIMARY"), _get_c("PRIMARY_H"), "white")

    bg, _, fg = _get_variant_colors()
    b = tk.Button(parent, text=label, bg=bg, fg=fg,
                  font=F_BTN, relief="flat", cursor="hand2",
                  padx=16, pady=7, bd=0, command=command,
                  activeforeground=fg, **kw)
    
    def _on_enter(_e=None): # type: ignore
        _, bg_h, _ = _get_variant_colors()
        b.config(bg=bg_h, activebackground=bg_h)
    def _on_leave(_e=None): # type: ignore
        bg, _, _ = _get_variant_colors()
        b.config(bg=bg)

    b.bind("<Enter>", _on_enter) # type: ignore
    b.bind("<Leave>", _on_leave) # type: ignore
    b.bind("<ButtonPress-1>", _on_enter) # type: ignore
    b.bind("<ButtonRelease-1>", _on_enter) # type: ignore
    return b


def search_box(parent: tk.Misc, var: tk.StringVar, width: int = 22,
               command: Any = None) -> tk.Frame:
    outer = tk.Frame(parent, bg=_get_c("SURFACE"), highlightthickness=1,
                     highlightbackground=_get_c("BORDER"))
    tk.Label(outer, text="🔍", bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
             font=("Segoe UI", 10)).pack(side="left", padx=(8, 2))
    e = tk.Entry(outer, textvariable=var, relief="flat",
                 font=("Segoe UI", 11), width=width,
                 bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                 insertbackground=_get_c("ACCENT"))
    e.pack(side="left", ipady=6, padx=(0, 8))

    def _in(_: Any) -> None:
        outer.config(highlightbackground=_get_c("PRIMARY"), highlightthickness=2)
    def _out(_: Any) -> None:
        outer.config(highlightbackground=_get_c("BORDER"), highlightthickness=1)
    e.bind("<FocusIn>",  _in)  # type: ignore[arg-type]
    e.bind("<FocusOut>", _out)  # type: ignore[arg-type]
    if command is not None:
        e.bind("<Return>", lambda _=None: command())  # type: ignore[arg-type]
    return outer


def page_header(parent: tk.Misc, text: str, icon: str = "") -> tk.Frame:
    frm = tk.Frame(parent, bg=_get_c("BG"))

    # Gradient accent bar: solid Indigo 600 stripe
    tk.Frame(frm, bg=_get_c("PRIMARY"), height=4).pack(fill="x")

    row = tk.Frame(frm, bg=_get_c("BG"))
    row.pack(fill="x", padx=20, pady=(6, 4))

    if icon:
        # Icon in a pill background
        ic_bg = tk.Frame(row, bg=_get_c("INFO_BG"), padx=8, pady=4)
        ic_bg.pack(side="left", padx=(0, 12))
        tk.Label(ic_bg, text=icon, bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"),
                 font=("Segoe UI", 18)).pack()
    tk.Label(row, text=text, bg=_get_c("BG"), fg=_get_c("TEXT"),
             font=F_TITLE).pack(side="left")

    # Subtle divider
    tk.Frame(frm, bg=_get_c("BORDER"), height=1).pack(fill="x", padx=20, pady=(0, 2))
    return frm


def make_card(parent: tk.Widget, padx: int = 20, pady: int = 16,
              shadow: bool = True, **kw: Any) -> tuple[tk.Frame, tk.Frame]:
    """Returns (outer_frame, content_frame). Deeper shadow for premium feel."""
    if shadow:
        # Two-layer shadow: mid + dark bottom-right offset
        shadow_outer = tk.Frame(parent, bg=_get_c("SLATE_200"))
        shadow_inner = tk.Frame(shadow_outer, bg=_get_c("SLATE_300"))
        shadow_inner.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))
        content = tk.Frame(shadow_inner, bg=_get_c("SURFACE"), padx=padx, pady=pady, **kw)
        content.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
        outer = shadow_outer
    else:
        outer = tk.Frame(parent, bg=_get_c("SURFACE"),
                         highlightthickness=1,
                         highlightbackground=_get_c("BORDER"),
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
    tree.tag_configure("empty",     foreground=C_MUTED, font=("Segoe UI", 10, "italic"))
    tree.tag_configure("Da duyet",  background=C_SUCCESS_BG, foreground=C_SUCCESS)
    tree.tag_configure("Cho duyet", background=C_WARNING_BG, foreground=C_WARNING)
    tree.tag_configure("Tu choi",   background=C_DANGER_BG,  foreground=C_DANGER)
    tree.tag_configure("Hoat dong", background=C_SUCCESS_BG, foreground=C_SUCCESS)
    tree.tag_configure("Bao tri",   background=C_WARNING_BG, foreground=C_WARNING)
    tree.tag_configure("Khoa",      background=C_DANGER_BG,  foreground=C_DANGER)


def fill_tree(tree: ttk.Treeview, rows: list[tuple[object, ...]],
              empty_msg: str = "  Khong co du lieu") -> None:
    for item in tree.get_children():
        tree.delete(item)
    if not rows:
        cols = tree["columns"]
        placeholder = tuple([empty_msg] + [""] * (len(cols) - 1))
        tree.insert("", "end", values=placeholder, tags=["empty"])
        return
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
        self.bind("<Configure>", lambda _=None: self._draw())
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
        "Tu choi":   ("#fdf2f8", "#db2777"),
        "Khoa":      ("#fdf2f8", "#db2777"),
        "Hong":      ("#fdf2f8", "#db2777"),
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
            (1,  0.2,  "#ec4899", "Rat yeu"),
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


def toast(master: tk.Misc, message: str, kind: str = "success", # type: ignore
          duration_ms: int = 2800) -> None:
    """Show a short non-blocking toast notification at the bottom-right.
    kind: "success" | "error" | "info" | "warning"
    """
    COLORS = {
        "success": ("#dcfce7", "#15803d", "✔"),
        "error":   ("#fdf2f8", "#db2777", "✖"),
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
        "danger":  ("#fdf2f8", "#db2777", "#ec4899"),
        "error":   ("#fef2f2", "#b91c1c", "#ef4444"),
        "info":    ("#eef2ff", "#4f46e5", "#4f46e5"),
        "success": ("#f0fdf4", "#15803d", "#22c55e"),
    }
    ICONS: dict[str, str] = {
        "warning": "⚠", "danger": "🗑", "error": "❌", 
        "info": "ℹ", "success": "✅"
    }
    bg, fg, hdr_bg = COLORS.get(kind, COLORS["info"])
    icon = ICONS.get(kind, "ℹ")

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
        variant="danger" if kind in ("danger", "error") else "primary").pack(side="right")
    
    if cancel_text:
        btn(btn_row, cancel_text, _cancel,
            variant="ghost").pack(side="right", padx=8)

    dlg.update_idletasks()
    rx = root.winfo_x() + root.winfo_width() // 2
    ry = root.winfo_y() + root.winfo_height() // 2
    dlg.geometry(f"+{rx - dlg.winfo_width() // 2}+{ry - dlg.winfo_height() // 2}")
    dlg.bind("<Return>", lambda _=None: _ok())
    dlg.bind("<Escape>", lambda _=None: _cancel())
    dlg.wait_window()
    return result[0]


def alert(parent: tk.Misc, title: str, message: str, kind: str = "info") -> None:
    """Styled modal alert dialog (OK only)."""
    confirm_dialog(parent, title, message, ok_text="Dong", cancel_text="", kind=kind)


def ask(parent: tk.Misc, title: str, message: str, kind: str = "warning") -> bool:
    """Styled modal confirmation dialog (Yes/No). Returns True if OK."""
    return confirm_dialog(parent, title, message, ok_text="Dong y", cancel_text="Bo qua", kind=kind)


# ── Nebula Slate Components ─────────────────────────────────────────────────

class GlassCard(tk.Frame):
    """Modern glass-morphism card with subtle shadow and rounded corners."""

    def __init__(self, parent, **kwargs): # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
        # Create shadow layer
        shadow = tk.Frame(parent, bg=_get_c("SLATE_700")) # type: ignore
        shadow.pack(padx=(2, 0), pady=(2, 0), fill="both", expand=True)

        # Create main card
        super().__init__(shadow, bg=_get_c("SLATE_800"), **kwargs) # type: ignore

        # Add subtle border
        self.config(highlightthickness=1, highlightbackground=_get_c("SLATE_600"))

        # Pack with padding for glass effect
        self.pack(padx=(0, 2), pady=(0, 2), fill="both", expand=True)


class GlowButton(tk.Button):
    """Button with glow hover effect and multiple style variants."""

    def __init__(self, parent, text, command, style="primary", **kwargs): # type: ignore
        self._style = style
        bg, fg, _, _ = self._get_colors()

        super().__init__(
            parent, # type: ignore
            text=text, # type: ignore
            command=command, # type: ignore
            bg=bg, # type: ignore
            fg=fg,
            font=F_BTN,
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            **kwargs # type: ignore
        )

        # Bind hover effects
        self.bind("<Enter>", self._on_enter) # type: ignore
        self.bind("<Leave>", self._on_leave) # type: ignore

    def _get_colors(self) -> tuple[str, str, str, str]:
        # Returns (bg, fg, hover_bg, border)
        if self._style == "danger":
            return (_get_c("DANGER"), "white", _get_c("DANGER"), _get_c("DANGER"))
        if self._style == "ghost":
            return (_get_c("SB_BG"), _get_c("SB_TEXT"), _get_c("SB_HOVER"), _get_c("SB_ACCENT"))
        # primary
        return (_get_c("PRIMARY"), "white", _get_c("PRIMARY_H"), _get_c("PRIMARY_H"))

    def _on_enter(self, _e=None): # type: ignore
        _, _, hover_bg, border = self._get_colors()
        self.config(bg=hover_bg, highlightthickness=2, highlightbackground=border)

    def _on_leave(self, _e=None): # type: ignore
        bg, _, _, _ = self._get_colors()
        self.config(bg=bg, highlightthickness=0)


class PillBadge(tk.Label):
    """Rounded badge with color variants for status indicators."""

    def __init__(self, parent, text, color="neutral", **kwargs): # type: ignore
        # Color configurations
        colors = {
            "success": (_get_c("EMERALD_500"), "white"),
            "error": (_get_c("ROSE_500"), "white"),
            "warning": (_get_c("AMBER_400"), _get_c("SLATE_900")),
            "neutral": (_get_c("SLATE_600"), _get_c("SLATE_100"))
        }

        bg_color, fg_color = colors.get(color, colors["neutral"])

        super().__init__(
            parent, # type: ignore
            text=f"  {text}  ",
            bg=bg_color,
            fg=fg_color,
            font=("Inter", 11, "bold"),
            **kwargs # type: ignore
        )


def custom_dialog(parent, type="info", title="", message=""): # type: ignore
    """Modern custom dialog replacing messagebox with Nebula Slate styling."""

    # Icon and color configurations
    configs = {
        "info": ("ℹ", _get_c("INDIGO_500"), _get_c("SLATE_800")),
        "error": ("❌", _get_c("ROSE_500"), _get_c("SLATE_800")),
        "confirm": ("⚠", _get_c("AMBER_400"), _get_c("SLATE_800"))
    }

    icon, accent_color, bg_color = configs.get(type, configs["info"])

    # Create dialog window
    root = parent.winfo_toplevel() # type: ignore
    dlg = tk.Toplevel(root) # type: ignore
    dlg.title(title)
    dlg.resizable(False, False)
    dlg.configure(bg=_get_c("SLATE_900"))
    dlg.transient(root) # type: ignore
    dlg.grab_set()

    result = [False]

    # Header with icon and title
    header_frame = tk.Frame(dlg, bg=accent_color, padx=20, pady=12)
    header_frame.pack(fill="x")

    tk.Label(
        header_frame,
        text=f"  {icon}  {title}",
        bg=accent_color,
        fg="white",
        font=FONT_H3,
        anchor="w"
    ).pack(side="left")

    # Content area
    content_frame = tk.Frame(dlg, bg=_get_c("SLATE_900"), padx=24, pady=20)
    content_frame.pack(fill="x")

    # Message with background
    msg_frame = tk.Frame(
        content_frame,
        bg=bg_color,
        highlightthickness=1,
        highlightbackground=_get_c("SLATE_600")
    )
    msg_frame.pack(fill="x", pady=(0, 16))

    tk.Label(
        msg_frame,
        text=message,
        bg=bg_color,
        fg=_get_c("SLATE_100"),
        font=FONT_BODY,
        wraplength=340,
        justify="left",
        anchor="w"
    ).pack(padx=16, pady=12)

    # Buttons
    btn_frame = tk.Frame(content_frame, bg=_get_c("SLATE_900"))
    btn_frame.pack(fill="x")

    def on_ok():
        result[0] = True
        dlg.destroy()

    def on_cancel():
        dlg.destroy()

    # OK button
    GlowButton(
        btn_frame,
        "OK" if type != "confirm" else "Xác nhận",
        on_ok,
        style="primary" if type != "error" else "danger"
    ).pack(side="right")

    # Cancel button for confirm dialogs
    if type == "confirm":
        GlowButton(
            btn_frame,
            "Hủy",
            on_cancel,
            style="ghost"
        ).pack(side="right", padx=(0, 8))

    # Center dialog
    dlg.update_idletasks()
    rx = root.winfo_x() + root.winfo_width() // 2 # type: ignore
    ry = root.winfo_y() + root.winfo_height() // 2 # type: ignore
    dlg.geometry(f"+{rx - dlg.winfo_width() // 2}+{ry - dlg.winfo_height() // 2}")

    # Bind keys
    dlg.bind("<Return>", lambda e: on_ok())
    dlg.bind("<Escape>", lambda e: on_cancel())
    dlg.wait_window()

    return result[0]


# ── Utility helpers ────────────────────────────────────────────────────────

def relative_time(dt_str: str) -> str:
    """Convert ISO datetime string to Vietnamese relative time.
    E.g. '2 phut truoc', '3 gio truoc', '1 ngay truoc'.
    """
    try:
        then = _dt.datetime.fromisoformat(str(dt_str))
        now  = _dt.datetime.now()
        secs = int((now - then).total_seconds())
        if secs < 60:
            return "Vua xong"
        elif secs < 3600:
            m = secs // 60
            return f"{m} phut truoc"
        elif secs < 86400:
            h = secs // 3600
            return f"{h} gio truoc"
        elif secs < 604800:
            d = secs // 86400
            return f"{d} ngay truoc"
        else:
            return then.strftime("%d/%m/%Y")
    except Exception:
        return str(dt_str)


def animate_count(label: tk.Label, end_value: int,
                  duration_ms: int = 700, steps: int = 24) -> None:
    """Animate a label's text from 0 up to end_value over duration_ms."""
    if end_value <= 0:
        label.config(text="0")
        return
    interval = max(1, duration_ms // steps)
    step_size = max(1, end_value // steps)

    def _tick(current: int) -> None:
        if not label.winfo_exists():
            return
        label.config(text=str(current))
        if current < end_value:
            nxt = min(current + step_size, end_value)
            label.after(interval, lambda: _tick(nxt))

    label.after(60, lambda: _tick(0))


def section_label(parent: tk.Misc, text: str, bg: str | None = None) -> tk.Label:
    """Small section separator label styled like a tab header."""
    _bg = bg if bg is not None else _get_c("BG")
    return tk.Label(parent, text=text, bg=_bg, fg=_get_c("MUTED"),
                    font=("Segoe UI", 8, "bold"), anchor="w")


def toast(parent: tk.Misc, message: str, kind: str = "info") -> None:
    """Show a non-blocking floating notification that disappears."""
    root = parent.winfo_toplevel()
    t = tk.Toplevel(root)
    t.overrideredirect(True)
    t.attributes("-topmost", True) # type: ignore
    
    colors = {
        "info":    (_get_c("SLATE_800"), _get_c("SLATE_100")),
        "success": (_get_c("EMERALD_500"), "white"),
        "error":   (_get_c("ROSE_500"), "white"),
    }
    bg, fg = colors.get(kind, colors["info"])
    
    lbl = tk.Label(t, text=message, bg=bg, fg=fg,
                   font=("Inter", 10, "bold"), padx=15, pady=8)
    lbl.pack()
    
    # Position: Bottom center
    t.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (t.winfo_width() // 2)
    y = root.winfo_y() + root.winfo_height() - 80
    t.geometry(f"+{x}+{y}")
    
    # Animate fade out
    def _fade(alpha: float) -> None:
        if not t.winfo_exists(): return
        if alpha <= 0:
            t.destroy()
        else:
            t.attributes("-alpha", alpha) # type: ignore
            t.after(40, lambda: _fade(alpha - 0.05))

    t.after(2000, lambda: _fade(1.0))
