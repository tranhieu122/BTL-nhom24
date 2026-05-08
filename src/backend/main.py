#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — Thin entry-point for the Classroom Booking System.

Classroom Booking System - Nhom 24
Members: Tran Trung Hieu, Nguyen Huy Hai, Nguyen Tuan Minh

This file only:
  1. Loads .env configuration.
  2. Adds src/frontend to sys.path so gui.* modules are importable.
  3. Instantiates App and starts the Tkinter event loop.

Business logic lives in:
  app.py   — Tk root window + controller singletons + login flow
  shell.py — MainShell (topbar, sidebar, content routing)
"""

from __future__ import annotations

from pathlib import Path
import sys
from tkinter import messagebox

# Load optional .env file (python-dotenv) ------------------------------------
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_ENV_FILE, override=False)
except ImportError:
    pass  # python-dotenv not installed — fall back to os.environ defaults

# Ensure src/frontend is importable ------------------------------------------
ROOT_DIR     = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

# Entry point ----------------------------------------------------------------
if __name__ == "__main__":
    from utils.logger import get_logger as _gl
    from app import App

    _log = _gl("main")
    _log.info("Application starting")
    try:
        App().mainloop()
        _log.info("Application exited normally")
    except Exception:
        _log.critical("Unhandled exception — application crashed",
                      exc_info=True)
        messagebox.showerror(
            "Loi khong mong muon",
            "Ung dung gap su co nghiem trong.\n"
            "Chi tiet da duoc luu vao file logs/app.log.",
        )
        sys.exit(1)