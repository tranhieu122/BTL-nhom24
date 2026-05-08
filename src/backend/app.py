#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — Tkinter root window and application lifecycle.

Responsibilities
----------------
* Create / center the Tk root window.
* Instantiate all shared controller singletons.
* Own the login/logout flow (show LoginFrame ↔ MainShell).
* Expose ``current_user`` to the rest of the UI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from tkinter import ttk
import tkinter as tk

# Ensure src/frontend is importable when this module is imported directly.
ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from controllers.auth_controller import AuthController
from controllers.booking_controller import BookingController
from controllers.equipment_controller import EquipmentController
from controllers.notification_controller import NotificationController
from controllers.report_controller import ReportController
from controllers.room_controller import RoomController
from controllers.room_feedback_controller import RoomFeedbackController
from controllers.schedule_rule_controller import ScheduleRuleController
from controllers.user_controller import UserController

from gui.theme import apply_theme
from config.constants import C_BG


class App(tk.Tk):
    """Tkinter root window.  Owns all shared controller instances."""

    def __init__(self) -> None:
        super().__init__()
        self.title("He Thong Quan Ly Phong Hoc")
        self.geometry("1280x780")
        self.minsize(960, 600)
        self.configure(bg=C_BG)
        apply_theme(ttk.Style())
        self._center()

        # Shared controller singletons -----------------------------------------
        # Pattern: Application-level singleton + constructor injection.
        # Each controller is instantiated exactly once here and passed into
        # GUI frames as an argument.  This gives us:
        #   • A single DB connection pool shared across all controllers.
        #   • Easy unit-testing (inject mock DAOs or controllers in tests).
        #   • No global state — the App instance owns the object graph.
        # Alternative (module-level singleton) was rejected because it makes
        # testing harder and creates hidden coupling between modules.
        self.auth_ctrl          = AuthController()
        self.room_ctrl          = RoomController()
        self.booking_ctrl       = BookingController()
        self.user_ctrl          = UserController()
        self.equip_ctrl         = EquipmentController()
        self.feedback_ctrl      = RoomFeedbackController()
        self.report_ctrl        = ReportController(
            self.room_ctrl, self.booking_ctrl,
            self.user_ctrl, self.equip_ctrl)
        self.schedule_rule_ctrl = ScheduleRuleController()
        self.notif_ctrl         = NotificationController()

        # Auto-backup on startup (silent fail) ---------------------------------
        try:
            from database.sqlite_db import backup_database
            backup_database()
        except Exception:
            pass

        self.current_user = None
        self._show_login()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _center(self) -> None:
        """Center the window on screen."""
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"1280x780+{(sw - 1280) // 2}+{(sh - 780) // 2}")

    # ── Login / logout flow ───────────────────────────────────────────────────

    def _show_login(self) -> None:
        """Replace all children with the LoginFrame."""
        from gui.login_gui import LoginFrame
        for w in self.winfo_children():
            w.destroy()
        LoginFrame(self, on_login=self._do_login,
                   auth_controller=self.auth_ctrl).pack(fill="both", expand=True)

    def _do_login(self, username: str, password: str) -> None:
        """Callback invoked by LoginFrame on submit."""
        user = self.auth_ctrl.authenticate(username, password)
        if user is None:
            return  # LoginFrame handles the error display
        self.current_user = user
        for w in self.winfo_children():
            w.destroy()
        from shell import MainShell
        MainShell(self).pack(fill="both", expand=True)

    def logout(self) -> None:
        """Log out current user and return to the login screen."""
        self.current_user = None
        self._show_login()
