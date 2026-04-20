#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
He Thong Quan Ly Dat Phong Hoc - BTL Nhom 24
Root launcher: runs src/back end/main.py as the application entry point.
"""
import runpy
from pathlib import Path

BACKEND_MAIN = Path(__file__).resolve().parent / "src" / "back end" / "main.py"
runpy.run_path(str(BACKEND_MAIN), run_name="__main__")

