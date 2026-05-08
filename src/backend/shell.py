#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shell.py — Main application shell (TopBar + Sidebar + Content area).

Responsibilities
----------------
* Build the persistent chrome (top-bar, sidebar, content slot).
* Handle sidebar navigation and page routing.
* Refresh notification / pending-booking badges.
* Register global keyboard shortcuts.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from config.constants import (
    SIDEBAR_W, TOPBAR_H,
    TP_BG, TP_BORDER, TP_TEXT, TP_MUTED, ROLE_CHIP,
    ROLE_AVATAR, NAV_ALL,
    NAV_GV_SV, PAGE_TITLES,
)
from gui.theme import (
    _get_c, FONT_H3, FONT_BODY, FONT_CAPTION
)


def _initials(name: str) -> str:
    """Return two-letter initials from a full name."""
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"


class _NavTooltip:
    """Lightweight tooltip that pops up to the right of a sidebar nav item."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self._widget = widget
        self._text   = text
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show, add=True)
        widget.bind("<Leave>", self._hide, add=True)

    def _show(self, _event: object = None) -> None:
        if self._tip is not None:
            return
        try:
            x = self._widget.winfo_rootx() + self._widget.winfo_width() + 6
            y = (self._widget.winfo_rooty()
                 + self._widget.winfo_height() // 2 - 12)
        except Exception:
            return
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self._tip, text=self._text,
                 bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
                 font=("Segoe UI", 9), padx=10, pady=5).pack()

    def _hide(self, _event: object = None) -> None:
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


class MainShell(tk.Frame):
    """Top-level application frame rendered after login.

    Contains the top-bar, sidebar navigation and a content slot that
    is replaced on every navigation event.
    """

    def __init__(self, app) -> None:  # app: App (avoid circular import)
        super().__init__(app, bg=_get_c("BG"))
        self.app = app
        self._nav_parts: dict[str, dict] = {}
        self._active_key = ""
        self._page_lbl: tk.Label | None = None
        self._badge_host: tk.Label | None = None
        self._badge_lbl: tk.Label | None = None
        self._notif_badge_host: tk.Label | None = None
        self._notif_badge_lbl: tk.Label | None = None
        self._content: tk.Frame | None = None
        self._content_frame: tk.Frame | None = None
        self._sb_collapsed: bool = False
        self._sb_frame: tk.Frame | None = None
        self._sb_toggle_btn: tk.Button | None = None
        self._build()
        self._bind_shortcuts()
        self._navigate("dashboard")

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self._build_topbar()
        body = tk.Frame(self, bg=_get_c("BG"))
        body.pack(fill="both", expand=True)
        self._body_frame = body                      # saved for sidebar rebuild
        self._build_sidebar(body)
        self._content_frame = tk.Frame(body, bg=_get_c("BG"))
        self._content_frame.pack(side="left", fill="both", expand=True)

    def _refresh_theme_icons(self) -> None:
        """Update shell icons and logo when theme changes."""
        from gui.theme import CURRENT_THEME
        if hasattr(self, "_theme_btn"):
            icon = "☀️" if CURRENT_THEME == "dark" else "🌙"
            self._theme_btn.config(text=icon)
        
        # Redraw sidebar to refresh logo and canvas backgrounds
        if hasattr(self, "_sb_frame") and self._sb_frame.winfo_exists():
            for child in self._sb_frame.winfo_children():
                child.destroy()
            self._fill_sidebar_content(self._sb_frame)

    # ── TopBar ─────────────────────────────────────────────────────────────────

    def _build_topbar(self) -> None:
        tb_wrap = tk.Frame(self, bg=_get_c("SB_BG"))
        tb_wrap.pack(fill="x")
        tk.Frame(tb_wrap, bg=_get_c("BORDER"), height=1).pack(fill="x", side="bottom")

        tb = tk.Frame(tb_wrap, bg=_get_c("SB_BG"), height=56)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Left: Breadcrumb navigation -----------------------------------------------
        left = tk.Frame(tb, bg=_get_c("SB_BG"))
        left.pack(side="left", fill="y", padx=(16, 0))

        self._sb_toggle_btn = tk.Button(
            left, text="☰", bg=_get_c("SB_BG"), fg=_get_c("SB_ACTIVE"),
            font=("Inter", 14), relief="flat", bd=0, cursor="hand2",
            activebackground=_get_c("SB_HOVER"), activeforeground=_get_c("SB_ACTIVE"),
            command=self._toggle_sidebar)
        self._sb_toggle_btn.pack(side="left", pady=12, padx=(0, 8))
        self._sb_toggle_btn.bind("<Enter>",
            lambda _=None: self._sb_toggle_btn.config(bg=_get_c("SB_HOVER")))
        self._sb_toggle_btn.bind("<Leave>",
            lambda _=None: self._sb_toggle_btn.config(bg=_get_c("SB_BG")))

        # Breadcrumb
        tk.Label(left, text="Dashboard", bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
                 font=FONT_BODY).pack(side="left")
        tk.Label(left, text=" › ", bg=_get_c("SB_BG"), fg=_get_c("MUTED"),
                 font=FONT_BODY).pack(side="left")
        self._page_lbl = tk.Label(left, text="", bg=_get_c("SB_BG"), fg=_get_c("SB_ACTIVE"),
                                  font=FONT_H3)
        self._page_lbl.pack(side="left")

        # Right: Search + Notifications + Theme toggle ---------------------------
        right = tk.Frame(tb, bg=_get_c("SB_BG"))
        right.pack(side="right", fill="y", padx=16)

        self._clock_lbl = tk.Label(right, text="", bg=_get_c("SB_BG"), fg=_get_c("MUTED"),
                                   font=FONT_CAPTION)
        self._clock_lbl.pack(side="right", padx=(0, 16), pady=18)
        self._tick_clock()

        # Theme toggle button
        from gui.theme import switch_theme, CURRENT_THEME
        theme_icon = "☀️" if CURRENT_THEME == "dark" else "🌙"
        self._theme_btn = tk.Button(
            right, text=theme_icon, bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
            font=("Inter", 16), relief="flat", cursor="hand2",
            bd=0, padx=8, pady=5,
            activebackground=_get_c("SB_HOVER"), activeforeground=_get_c("SB_ACTIVE"),
            command=lambda: switch_theme(self.app))
        self._theme_btn.pack(side="right", padx=(0, 8), pady=14)

        # Notification bell
        self._notif_badge_host = tk.Label(
            right, text="🔔", bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
            font=("Inter", 16), cursor="hand2")
        self._notif_badge_host.pack(side="right", padx=(0, 4))
        self._refresh_notif_badge()
        self._notif_badge_host.bind(
            "<Button-1>", lambda _=None: self._navigate("notifications"))

        # Search box
        search_frame = tk.Frame(right, bg=_get_c("BORDER"), padx=1, pady=1)
        search_frame.pack(side="right", padx=(0, 8), pady=14)
        inner_search = tk.Frame(search_frame, bg=_get_c("SURFACE"))
        inner_search.pack(fill="both", expand=True)
        tk.Label(inner_search, text="🔍", bg=_get_c("SURFACE"), fg=_get_c("MUTED"),
                 font=("Inter", 12)).pack(side="left", padx=(8, 2))
        self._search_var = tk.StringVar()
        search_entry = tk.Entry(inner_search, textvariable=self._search_var,
                               bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                               font=FONT_BODY, relief="flat", width=20,
                               insertbackground=_get_c("SB_ACTIVE"))
        search_entry.pack(side="left", padx=(0, 8), pady=6)
        search_entry.insert(0, "Tìm kiếm...")
        
        tk.Frame(right, bg=_get_c("BORDER"), width=1, height=24).pack(
            side="right", padx=12, fill="y", pady=16)

        user = self.app.current_user
        
        def _get_role_style(role: str) -> tuple[str, str, str]:
            # Returns (chip_bg, chip_fg, avatar_bg)
            if role == "Admin":
                return (_get_c("INFO_BG"), _get_c("ACCENT"), _get_c("ACCENT"))
            elif role == "Giang vien":
                return (_get_c("SUCCESS_BG"), _get_c("SUCCESS"), _get_c("SUCCESS"))
            else: # Sinh vien
                return (_get_c("WARNING_BG"), _get_c("WARNING"), _get_c("WARNING"))

        chip_bg, chip_fg, av_bg = _get_role_style(user.role)

        # Pending bookings badge (admin only) -----------------------------------
        if user.role == "Admin":
            badge_wrap = tk.Frame(right, bg=_get_c("SB_BG"))
            badge_wrap.pack(side="right", padx=(0, 4))
            bell = tk.Label(badge_wrap, text="📋", bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
                            font=("Inter", 16), cursor="hand2")
            bell.pack()
            self._badge_host = bell
            self._refresh_pending_badge()
            bell.bind("<Button-1>", lambda _=None: self._navigate("booking_list"))

        # User info
        tk.Label(right, text=f"  {user.role}  ", bg=chip_bg, fg=chip_fg,
                 font=FONT_CAPTION).pack(side="right", pady=18)
        tk.Label(right, text=user.full_name, bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"),
                 font=FONT_BODY).pack(side="right", padx=(0, 8), pady=18)

        av = tk.Canvas(right, width=32, height=32, bg=_get_c("SB_BG"),
                       highlightthickness=0, cursor="hand2")
        av.pack(side="right", pady=12, padx=(0, 4))
        av.create_oval(1, 1, 31, 31, fill=av_bg, outline="")
        av.create_text(16, 16, text=_initials(user.full_name), fill="white", font=("Inter", 10, "bold"))
        av.bind("<Button-1>", lambda _=None: self._open_profile())
        av.bind("<Enter>", lambda _=None: av.config(
            highlightthickness=2, highlightbackground=_get_c("SB_ACTIVE")))
        av.bind("<Leave>", lambda _=None: av.config(highlightthickness=0))

        tk.Frame(tb_wrap, bg=_get_c("SB_ACTIVE"), height=2).pack(fill="x", side="bottom")

    def _open_profile(self) -> None:
        from gui.profile_gui import ProfileDialog
        ProfileDialog(self, self.app.current_user, self.app.auth_ctrl)

    def _tick_clock(self) -> None:
        """Refresh the live clock label every second."""
        import datetime as _dt
        if not self.winfo_exists():
            return
        self._clock_lbl.config(
            text=_dt.datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y"))
        self.after(1000, self._tick_clock)

    def _pending_count(self) -> int:
        try:
            return sum(
                1 for b in self.app.booking_ctrl.list_bookings(from_today=False)
                if getattr(b, "status", "") == "Cho duyet")
        except Exception:
            return 0

    def _refresh_pending_badge(self) -> None:
        if self._badge_host is None:
            return
        n = self._pending_count()
        if n <= 0:
            if self._badge_lbl is not None:
                self._badge_lbl.destroy()
                self._badge_lbl = None
            return
        if self._badge_lbl is None:
            self._badge_lbl = tk.Label(
                self._badge_host.master,
                bg=_get_c("ROSE_500"), fg="white",
                font=("Inter", 7, "bold"), width=2)
            self._badge_lbl.place(
                in_=self._badge_host, relx=1.0, rely=0.0,
                anchor="ne", x=4, y=-2)
        self._badge_lbl.config(text=str(n))
        # Inline nav badge on "booking_list" item
        self._update_nav_badge("booking_list", n, bg=_get_c("AMBER_500"))

    def _refresh_notif_badge(self) -> None:
        """Refresh the unread-notification badge on the 📩 bell."""
        if self._notif_badge_host is None or not self.app.current_user:
            return
        try:
            count = self.app.notif_ctrl.count_unread(
                self.app.current_user.user_id)
        except Exception:
            count = 0
        if count <= 0:
            if self._notif_badge_lbl is not None:
                self._notif_badge_lbl.destroy()
                self._notif_badge_lbl = None
            return
        if self._notif_badge_lbl is None:
            self._notif_badge_lbl = tk.Label(
                self._notif_badge_host.master,
                bg=_get_c("INDIGO_500"), fg="white",
                font=("Inter", 7, "bold"), width=2)
            self._notif_badge_lbl.place(
                in_=self._notif_badge_host, relx=1.0, rely=0.0,
                anchor="ne", x=4, y=-2)
        self._notif_badge_lbl.config(text=str(count))
        # Inline nav badge on "notifications" item
        self._update_nav_badge("notifications", count, bg=_get_c("INDIGO_500"))

    def _update_nav_badge(self, key: str, count: int,
                          bg: str = "#db2777") -> None:
        """Show/hide the inline badge label on a sidebar nav item."""
        p = self._nav_parts.get(key)
        if p is None:
            return
        badge: tk.Label = p.get("badge")  # type: ignore[assignment]
        if badge is None:
            return
        if count > 0:
            badge.config(text=str(count), bg=bg)
            if not badge.winfo_ismapped():
                badge.pack(side="right", padx=(0, 4))
        else:
            if badge.winfo_ismapped():
                badge.pack_forget()

    # ── Sidebar ────────────────────────────────────────────────────────────────

    _SB_ICON_W: int = 52
    _SHORTCUT_HINTS: dict[str, str] = {
        "dashboard":    "Ctrl+D",
        "booking_form": "Ctrl+B",
        "booking_list": "Ctrl+L",
        "settings":     "Ctrl+,",
    }
    _ADMIN_NAV_KEYS: frozenset[str] = frozenset(
        {"users", "equipment", "rooms", "report", "room_issues"})

    def _build_sidebar(self, parent: tk.Frame) -> None:
        collapsed = self._sb_collapsed
        w = 64 if collapsed else 220
        sb = tk.Frame(parent, bg=_get_c("SB_BG"), width=w,
                      highlightthickness=1, highlightbackground=_get_c("BORDER"))
        if (self._content_frame is not None and self._content_frame.winfo_exists()):
            sb.pack(side="left", fill="y", before=self._content_frame)
        else:
            sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        self._sb_frame = sb
        self._fill_sidebar_content(sb)

    def _fill_sidebar_content(self, sb: tk.Frame) -> None:
        collapsed = self._sb_collapsed
        if not collapsed:
            logo_frame = tk.Frame(sb, bg=_get_c("SB_BG"), height=72)
            logo_frame.pack(fill="x")
            logo_frame.pack_propagate(False)

            logo_cv = tk.Canvas(logo_frame, width=200, height=72, bg=_get_c("SB_BG"),
                               highlightthickness=0)
            logo_cv.pack(fill="both", expand=True)
            logo_cv.create_oval(16, 16, 48, 48, fill=_get_c("SB_ACTIVE"),
                               outline=_get_c("SB_ACCENT"), width=1)
            logo_cv.create_text(32, 32, text="🏫", font=("Inter", 16), fill="white")
            logo_cv.create_text(58, 29, text="Quản Lý Phòng Học", font=("Inter", 10, "bold"),
                               fill=_get_c("SB_TEXT"), anchor="w")
            logo_cv.create_text(58, 48, text="Nebula Slate v2.0", font=("Inter", 7),
                               fill=_get_c("SB_TEXT"), anchor="w")
        else:
            logo_cv = tk.Canvas(sb, width=64, height=56, bg=_get_c("SB_BG"),
                               highlightthickness=0)
            logo_cv.pack(fill="x")
            logo_cv.create_oval(8, 8, 44, 44, fill=_get_c("SB_ACTIVE"),
                               outline=_get_c("SB_ACCENT"), width=1)
            logo_cv.create_text(26, 26, text="🏫", font=("Inter", 16), fill="white")

        tk.Frame(sb, bg=_get_c("BORDER"), height=1).pack(fill="x")

        user = self.app.current_user
        nav_items = NAV_ALL if user.role == "Admin" else NAV_GV_SV

        # Menu container
        menu_container = tk.Frame(sb, bg=_get_c("SB_BG"))
        menu_container.pack(fill="both", expand=True)
        
        # Scrollable menu
        self.menu_canvas = tk.Canvas(menu_container, bg=_get_c("SB_BG"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(menu_container, orient="vertical", command=self.menu_canvas.yview)
        self.menu_scroll_frame = tk.Frame(self.menu_canvas, bg=_get_c("SB_BG"))
        self.menu_scroll_frame.bind("<Configure>", lambda e=None: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all")))
        canvas_win = self.menu_canvas.create_window((0, 0), window=self.menu_scroll_frame, anchor="nw")
        self.menu_canvas.bind("<Configure>", lambda e=None: self.menu_canvas.itemconfig(canvas_win, width=e.width if e else self.menu_canvas.winfo_width()))
        self.menu_canvas.configure(yscrollcommand=scrollbar.set)
        self.menu_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event=None):
            if event:
                self.menu_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.menu_canvas.bind("<MouseWheel>", _on_mousewheel)

        def _bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel, add="+")
            for child in widget.winfo_children(): _bind_mousewheel(child)

        self._nav_items_data = []
        self._nav_parts = {}
        self._menu_positions = {}  # Store Y positions for indicator animation

        for label, key, icon in nav_items:
            if key == "---":
                if not collapsed:
                    sep = self._section_header(self.menu_scroll_frame, label)
                    self._nav_items_data.append(("header", label, sep))
            else:
                item = self._nav_item(self.menu_scroll_frame, label, key, icon or "•", collapsed)
                self._nav_items_data.append(("item", label, item))

        _bind_mousewheel(self.menu_scroll_frame)

        # Profile card at bottom
        self._bottom_user_card(sb, collapsed)

    def _section_header(self, parent: tk.Frame, text: str) -> tk.Frame:
        f = tk.Frame(parent, bg=_get_c("SB_BG")); f.pack(fill="x", pady=(14, 2))
        tk.Frame(f, bg=_get_c("BORDER"), height=1).pack(fill="x", padx=18, pady=(0, 8))
        tk.Label(f, text=text, bg=_get_c("SB_BG"), fg=_get_c("SB_ACCENT"), font=("Inter", 8, "bold"), anchor="w", padx=20, pady=2).pack(fill="x")
        return f

    def _nav_item(self, parent: tk.Frame, label: str, key: str, icon: str, collapsed: bool = False) -> tk.Frame:
        row = tk.Frame(parent, bg=_get_c("SB_BG"), cursor="hand2")
        row.pack(fill="x")

        # Store position for indicator animation
        row.update_idletasks()
        self._menu_positions[key] = row.winfo_y()

        # Active indicator bar (hidden by default)
        row.indicator = tk.Frame(row, bg=_get_c("SB_ACTIVE"), width=4)
        row.indicator.place(x=0, y=0, relheight=1.0)
        row.indicator.place_forget()

        if collapsed:
            inner = tk.Frame(row, bg=_get_c("SB_BG"), padx=5, pady=9)
            inner.pack(side="left")
            icon_cv = tk.Canvas(inner, width=38, height=28, bg=_get_c("SB_BG"), highlightthickness=0)
            icon_cv.pack()
            icon_cv.create_text(19, 14, text=icon, font=("Inter", 14), fill=_get_c("SB_ACCENT"), tags="ico")
            text_lbl, badge_lbl = None, tk.Label(inner, text="", bg=_get_c("ROSE_500"), fg="white", font=("Inter", 7, "bold"), padx=3)
            _NavTooltip(row, label)
        else:
            inner = tk.Frame(row, bg=_get_c("SB_BG"), padx=12, pady=9)
            inner.pack(side="left", fill="x", expand=True)
            icon_cv = tk.Canvas(inner, width=28, height=28, bg=_get_c("SB_BG"), highlightthickness=0)
            icon_cv.pack(side="left", padx=(0, 10))
            icon_cv.create_text(14, 14, text=icon, font=("Inter", 13), fill=_get_c("SB_ACCENT"), tags="ico")
            text_lbl = tk.Label(inner, text=label, bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"), font=("Inter", 10), anchor="w")
            text_lbl.pack(side="left", fill="x", expand=True)
            if key in self._ADMIN_NAV_KEYS:
                tk.Label(inner, text="🛡️", bg=_get_c("SB_BG"), fg=_get_c("SB_ACTIVE"), font=("Inter", 8)).pack(side="right", padx=(0, 2))
            hint = self._SHORTCUT_HINTS.get(key, "")
            if hint:
                tk.Label(inner, text=hint, bg=_get_c("SB_BG"), fg=_get_c("MUTED"), font=("Inter", 7)).pack(side="right", padx=(0, 4))
            badge_lbl = tk.Label(inner, text="", bg=_get_c("ROSE_500"), fg="white", font=("Inter", 7, "bold"), padx=4, relief="flat")

        self._nav_parts[key] = {"row": row, "inner": inner, "icon_cv": icon_cv, "text": text_lbl, "badge": badge_lbl}

        def on_enter(e, k=key):
            if k != self._active_key:
                p = self._nav_parts[k]
                [w.config(bg=_get_c("SLATE_800")) for w in (p["row"], p["inner"])]
                p["icon_cv"].config(bg=_get_c("SLATE_800"))
                if p["text"]: p["text"].config(bg=_get_c("SLATE_800"))

        def on_leave(e, k=key):
            if k != self._active_key:
                p = self._nav_parts[k]
                [w.config(bg=_get_c("SB_BG")) for w in (p["row"], p["inner"])]
                p["icon_cv"].config(bg=_get_c("SB_BG"))
                if p["text"]: p["text"].config(bg=_get_c("SB_BG"))

        def on_click(e, k=key):
            self._navigate(k)

        for w in [row, inner, icon_cv] + ([text_lbl] if text_lbl else []):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return row

    def _bottom_user_card(self, parent: tk.Frame, collapsed: bool = False) -> None:
        """Glassy profile card at bottom of sidebar."""
        user = self.app.current_user
        av_color = ROLE_AVATAR.get(user.role, _get_c("INDIGO_500"))

        # Glassy card container with transparency effect
        card = tk.Frame(parent, bg=_get_c("SB_HOVER"), padx=8 if collapsed else 16,
                       pady=8 if collapsed else 12, cursor="hand2",
                       highlightthickness=1, highlightbackground=_get_c("SB_ACTIVE"))
        card.pack(side="bottom", fill="x", pady=(8, 0))
        tk.Frame(parent, bg=_get_c("BORDER"), height=1).pack(side="bottom", fill="x")

        # Avatar
        av = tk.Canvas(card, width=36, height=36, bg=_get_c("SB_HOVER"), highlightthickness=0)
        av.pack(side="top" if collapsed else "left", padx=(0, 0 if collapsed else 10))
        av.create_oval(2, 2, 34, 34, fill=av_color, outline=_get_c("SB_ACCENT"), width=1)
        av.create_text(18, 18, text=_initials(user.full_name), fill="white", font=("Inter", 10, "bold"))

        if not collapsed:
            info = tk.Frame(card, bg=_get_c("SB_HOVER"))
            info.pack(side="left", fill="x", expand=True)

            tk.Label(info, text=user.full_name, bg=_get_c("SB_HOVER"), fg=_get_c("SB_TEXT"),
                     font=("Inter", 9, "bold"), anchor="w", cursor="hand2").pack(fill="x")

            tk.Label(info, text=user.role, bg=_get_c("SB_HOVER"), fg=_get_c("SB_ACCENT"),
                     font=("Inter", 8), anchor="w").pack(fill="x")

            # Action row (Logout / Settings) - hidden by default
            action_row = tk.Frame(info, bg=_get_c("SB_HOVER"))

            lo = tk.Label(action_row, text="Đăng xuất", bg=_get_c("SB_HOVER"), fg=_get_c("SB_ACCENT"),
                          font=("Inter", 7, "bold"), cursor="hand2")
            lo.pack(side="left")
            lo.bind("<Button-1>", lambda _: self.app.logout())
            lo.bind("<Enter>", lambda _: lo.config(fg="white"))
            lo.bind("<Leave>", lambda _: lo.config(fg=_get_c("SB_ACCENT")))

            tk.Label(action_row, text=" • ", bg=_get_c("SB_HOVER"), fg=_get_c("SB_ACCENT"), font=("Inter", 7)).pack(side="left")

            st = tk.Label(action_row, text="Cài đặt", bg=_get_c("SB_HOVER"), fg=_get_c("SB_ACCENT"),
                          font=("Inter", 7), cursor="hand2")
            st.pack(side="left")
            st.bind("<Button-1>", lambda _: self._navigate("settings"))
            st.bind("<Enter>", lambda _: st.config(fg="white"))
            st.bind("<Leave>", lambda _: st.config(fg=_get_c("SB_ACCENT")))

            # Toggle logic
            def _toggle_card(_e=None):
                if action_row.winfo_ismapped():
                    action_row.pack_forget()
                else:
                    action_row.pack(fill="x", pady=(2, 0))

            # Bind click to toggle
            for w in (card, av, info):
                w.bind("<Button-1>", _toggle_card)

            # Hover effects
            def _on_card_enter(_e):
                card.config(bg=_get_c("SB_ACTIVE"))
                av.config(bg=_get_c("SB_ACTIVE"))
                info.config(bg=_get_c("SB_ACTIVE"))

            def _on_card_leave(_e):
                card.config(bg=_get_c("SB_HOVER"))
                av.config(bg=_get_c("SB_HOVER"))
                info.config(bg=_get_c("SB_HOVER"))

            card.bind("<Enter>", _on_card_enter)
            card.bind("<Leave>", _on_card_leave)

    def _filter_menu(self) -> None:
        query = self._menu_search_var.get().lower()
        if query == "tìm menu...": return
        for kind, label, widget in self._nav_items_data:
            if kind == "item":
                if query in label.lower(): widget.pack(fill="x")
                else: widget.pack_forget()
            elif kind == "header": widget.pack(fill="x")

    def _toggle_sidebar(self) -> None:
        if self._sb_frame is None or not hasattr(self, "_body_frame"): return
        target_w = self._SB_ICON_W if not self._sb_collapsed else SIDEBAR_W
        self._animate_sidebar(self._sb_frame.winfo_width(), target_w)

    def _animate_sidebar(self, current_w: int, target_w: int, frame_count: int = 0) -> None:
        """Animate sidebar width with ease-out effect."""
        if current_w == target_w:
            self._sb_collapsed = (target_w == 64)
            self._finalize_sidebar_toggle()
            return

        # Ease-out calculation: decelerating animation
        total_frames = 20  # Total animation frames
        if frame_count >= total_frames:
            new_w = target_w
        else:
            # Cubic ease-out: progress = 1 - (1 - t)^3
            t = frame_count / total_frames
            progress = 1 - (1 - t) ** 3
            new_w = int(current_w + (target_w - current_w) * progress)

        # Ensure we don't overshoot
        if (current_w < target_w and new_w > target_w) or (current_w > target_w and new_w < target_w):
            new_w = target_w

        self._sb_frame.config(width=new_w)

        # Hide elements when collapsing
        if current_w > target_w and current_w == 220 and frame_count > total_frames * 0.3:
            self._hide_sidebar_elements()

        # Continue animation
        if new_w != target_w:
            self.after(12, lambda: self._animate_sidebar(new_w, target_w, frame_count + 1))

    def _hide_sidebar_elements(self) -> None:
        for p in self._nav_parts.values():
            if p.get("text") and p["text"].winfo_exists(): p["text"].pack_forget()
            if p.get("badge") and p["badge"].winfo_exists(): p["badge"].pack_forget()

    def _finalize_sidebar_toggle(self) -> None:
        if self._sb_frame is None or not self._sb_frame.winfo_exists(): return
        for child in self._sb_frame.winfo_children(): child.destroy()
        active = self._active_key; self._nav_parts.clear(); self._active_key = ""
        self._fill_sidebar_content(self._sb_frame)
        if active: self._navigate(active)
        self._refresh_pending_badge(); self._refresh_notif_badge()

    # ── Navigation / page routing ─────────────────────────────────────────────

    _ADMIN_KEYS: frozenset[str] = frozenset({"users", "equipment"})

    def _navigate(self, key: str) -> None:
        """Route to page identified by *key*, updating sidebar state."""
        # ── Admin middleware ──────────────────────────────────────────────────
        if key in self._ADMIN_KEYS:
            user_role = getattr(self.app.current_user, "role", "")
            if user_role != "Admin":
                from gui.theme import toast
                toast(self, "⛔  Chuc nang nay chi danh cho Admin.", kind="error")
                return
        self._refresh_pending_badge()
        self._refresh_notif_badge()

        # Deactivate previous nav item
        if self._active_key in self._nav_parts:
            p = self._nav_parts[self._active_key]
            for w in (p["row"], p["inner"]):
                w.config(bg=_get_c("SB_BG"))
            p["icon_cv"].config(bg=_get_c("SB_BG"))
            # Remove active circle if exists
            p["icon_cv"].delete("bg_circle")
            # Restore icon color
            p["icon_cv"].itemconfigure("ico", fill=_get_c("SB_TEXT"))
            if p["text"] is not None:
                p["text"].config(bg=_get_c("SB_BG"), fg=_get_c("SB_TEXT"), font=("Inter", 10))
            if hasattr(p["row"], "indicator"):
                p["row"].indicator.place_forget()

        self._active_key = key

        # Activate new nav item
        if key in self._nav_parts:
            p = self._nav_parts[key]
            for w in (p["row"], p["inner"]):
                w.config(bg=_get_c("SB_ACTIVE"))
            p["icon_cv"].config(bg=_get_c("SB_ACTIVE"))

            # Create/Show highlight circle behind the icon
            p["icon_cv"].delete("bg_circle")
            cw = 28 if not self._sb_collapsed else 38
            ch = 28
            p["icon_cv"].create_oval(cw//2-13, ch//2-13, cw//2+13, ch//2+13,
                                     fill=_get_c("INDIGO_400"), outline="", tags="bg_circle")
            p["icon_cv"].tag_lower("bg_circle")

            # Update icon and text color
            p["icon_cv"].itemconfigure("ico", fill="white")
            if p["text"] is not None:
                p["text"].config(bg=_get_c("SB_ACTIVE"), fg="white", font=("Inter", 10, "bold"))

            # Show active indicator
            if hasattr(p["row"], "indicator"):
                p["row"].indicator.place(x=0, y=0, relheight=1.0)

        if self._page_lbl:
            self._page_lbl.config(text=PAGE_TITLES.get(key, ""))

        if self._content is not None:
            self._content.destroy()

        frame = self._build_page(key)
        frame.pack(fill="both", expand=True)
        self._content = frame


    def _build_page(self, key: str) -> tk.Frame:
        """Instantiate and return the Frame for *key*."""
        from gui.booking_form_gui import BookingFormFrame
        from gui.admin.booking_list_gui import BookingListFrame
        from gui.dashboard_gui import DashboardFrame
        from gui.admin.equipment_gui import EquipmentManagementFrame
        from gui.notification_gui import NotificationFrame
        from gui.report_gui import ReportFrame
        from gui.room_feedback_gui import RoomIssueManagementFrame
        from gui.admin.room_gui import RoomManagementFrame
        from gui.room_map_gui import RoomMapFrame
        from gui.schedule_gui import ScheduleFrame
        from gui.recurring_schedule_gui import RecurringScheduleFrame
        from gui.admin.user_gui import UserManagementFrame
        from gui.settings_gui import SettingsFrame
        from gui.about_gui import AboutFrame

        app = self.app
        cf  = self._content_frame

        if key == "dashboard":
            return DashboardFrame(cf, app.report_ctrl, app.booking_ctrl,
                                  current_user=app.current_user)
        if key == "rooms":
            return RoomManagementFrame(cf, app.room_ctrl,
                                       app.booking_ctrl, app.feedback_ctrl,
                                       app.current_user)
        if key == "room_map":
            return RoomMapFrame(cf, app.room_ctrl, app.booking_ctrl)
        if key == "booking_form":
            return BookingFormFrame(
                cf, app.booking_ctrl, app.room_ctrl,
                app.current_user,
                on_booking_created=lambda: self._navigate("booking_list"),
                equipment_controller=app.equip_ctrl)
        if key in ("booking_list", "lich_su_dat"):
            return BookingListFrame(cf, app.booking_ctrl, app.current_user,
                                    room_controller=app.room_ctrl)
        if key == "users":
            return UserManagementFrame(cf, app.user_ctrl)
        if key == "equipment":
            return EquipmentManagementFrame(cf, app.equip_ctrl, app.room_ctrl)
        if key == "report":
            return ReportFrame(cf, app.report_ctrl)
        if key == "room_issues":
            return RoomIssueManagementFrame(cf, app.feedback_ctrl, app.equip_ctrl)
        if key == "notifications":
            return NotificationFrame(cf, app.notif_ctrl, app.current_user,
                                     user_controller=app.user_ctrl)
        if key in ("schedule", "lich_bieu"):
            return ScheduleFrame(cf, app.booking_ctrl, app.room_ctrl, app.current_user)
        if key == "recurring_schedule":
            return RecurringScheduleFrame(
                cf, app.schedule_rule_ctrl, app.room_ctrl,
                app.user_ctrl, current_user=app.current_user)
        if key == "settings":
            return SettingsFrame(cf, app.auth_ctrl, app.current_user,
                                 on_profile_updated=lambda: None,
                                 user_controller=app.user_ctrl)
        if key == "about":
            return AboutFrame(cf)

        # Fallback: "under construction" placeholder
        frame = tk.Frame(cf, bg=_get_c("BG"))
        tk.Label(frame, text=f"Trang '{key}' dang phat trien.",
                 bg=_get_c("BG"), fg=_get_c("MUTED"),
                 font=("Segoe UI", 14)).pack(expand=True)
        return frame

    # ── Keyboard shortcuts ────────────────────────────────────────────────────

    def _bind_shortcuts(self) -> None:
        app = self.app
        app.bind_all("<Control-Home>",     lambda _: self._navigate("dashboard"))
        app.bind_all("<F5>",               lambda _: self._navigate(self._active_key))
        app.bind_all("<Control-d>",        lambda _: self._navigate("dashboard"))
        app.bind_all("<Control-b>",        lambda _: self._navigate("booking_form"))
        app.bind_all("<Control-l>",        lambda _: self._navigate("booking_list"))
        app.bind_all("<Control-comma>",    lambda _: self._navigate("settings"))
        app.bind_all("<Control-backslash>",lambda _: self._toggle_sidebar())
        app.bind_all("<F11>",
            lambda _: app.attributes("-fullscreen",
                                     not app.attributes("-fullscreen")))
        app.bind_all("<Escape>",
            lambda _: app.attributes("-fullscreen", False)
                      if app.attributes("-fullscreen") else None)
