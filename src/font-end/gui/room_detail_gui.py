# room_detail_gui.py  –  room add/edit dialog
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from gui.theme import (C_PRIMARY, C_SURFACE, C_BORDER,
                       C_MUTED, F_INPUT, btn)


class RoomDetailDialog(tk.Toplevel):
    def __init__(self, master, room=None) -> None:
        super().__init__(master)
        self.title("Thong tin phong hoc")
        self.resizable(False, False)
        self.configure(bg=C_SURFACE)
        self.result = None
        self.vars = {
            "room_id":   tk.StringVar(value=getattr(room, "room_id",   "")),
            "name":      tk.StringVar(value=getattr(room, "name",      "")),
            "capacity":  tk.StringVar(value=str(getattr(room, "capacity", ""))),
            "room_type": tk.StringVar(value=getattr(room, "room_type", "Phong hoc")),
            "equipment": tk.StringVar(value=getattr(room, "equipment", "")),
            "status":    tk.StringVar(value=getattr(room, "status",    "Hoat dong")),
        }
        self._build()
        self.transient(master)
        self.grab_set()

    def _build(self) -> None:
        hdr = tk.Frame(self, bg=C_PRIMARY, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏫  Thong tin phong hoc",
                 bg=C_PRIMARY, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")

        frm = tk.Frame(self, bg=C_SURFACE, padx=24, pady=20)
        frm.pack(fill="both", expand=True)

        fields = [("room_id",   "Ma phong"),
                  ("name",      "Ten phong"),
                  ("capacity",  "Suc chua (nguoi)"),
                  ("room_type", "Loai phong"),
                  ("equipment", "Trang thiet bi")]
        for i, (key, lbl) in enumerate(fields):
            tk.Label(frm, text=lbl, bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 9, "bold")).grid(
                row=i * 2, column=0, columnspan=2,
                sticky="w", pady=(10 if i else 0, 2))
            tk.Entry(frm, textvariable=self.vars[key], width=36,
                     font=F_INPUT, relief="solid", bd=1).grid(
                row=i * 2 + 1, column=0, columnspan=2, sticky="ew")

        tk.Label(frm, text="Trang thai", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).grid(
            row=10, column=0, columnspan=2, sticky="w", pady=(10, 2))
        ttk.Combobox(frm, textvariable=self.vars["status"],
                     values=["Hoat dong", "Bao tri"],
                     state="readonly", width=33).grid(
            row=11, column=0, columnspan=2, sticky="ew")

        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.grid(row=12, column=0, columnspan=2,
                     sticky="e", pady=(20, 0))
        btn(btn_row, "Luu lai", self._save,
            icon="💾").pack(side="left", padx=6)
        btn(btn_row, "Huy", self.destroy,
            variant="ghost").pack(side="left")

    def _save(self) -> None:
        self.result = {k: v.get().strip() for k, v in self.vars.items()}
        self.destroy()
