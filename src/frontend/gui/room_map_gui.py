import datetime as dt
import tkinter as tk
from tkinter import ttk
from typing import Any
from gui.theme import (
    F_TITLE, F_SECTION, page_header, toast, tooltip, _get_c,
    C_BG, C_MUTED, C_PRIMARY, C_SUCCESS, C_WARNING, C_DANGER,
    C_SURFACE, C_BORDER, C_TEXT
)

class RoomMapFrame(tk.Frame):
    def __init__(self, master: tk.Misc, room_controller: Any, booking_controller: Any) -> None:
        super().__init__(master, bg=_get_c("BG"))
        self.room_ctrl = room_controller
        self.booking_ctrl = booking_controller
        
        self._floor_var = tk.StringVar(value="Tat ca")
        self._current_slot = self._get_current_slot()
        
        self._build()
        self.refresh()

    def _get_current_slot(self) -> str:
        now = dt.datetime.now().time()
        slots = [
            ("Ca 1", dt.time(7, 0), dt.time(9, 0)),
            ("Ca 2", dt.time(9, 15), dt.time(11, 15)),
            ("Ca 3", dt.time(13, 0), dt.time(15, 0)),
            ("Ca 4", dt.time(15, 15), dt.time(17, 15)),
            ("Ca 5", dt.time(17, 30), dt.time(19, 30)),
        ]
        for name, start, end in slots:
            if start <= now <= end:
                return name
        return "Ngoai gio"

    def _build(self) -> None:
        hdr = page_header(self, "Sơ đồ phòng học 2D", "🗺️")
        hdr.pack(fill="x")
        
        # Toolbar: Floor filter + Search + Current slot info
        toolbar = tk.Frame(self, bg=_get_c("BG"), padx=25, pady=15)
        toolbar.pack(fill="x")
        
        # Floor filter (Segmented-like buttons)
        filter_wrap = tk.Frame(toolbar, bg=_get_c("BG"))
        filter_wrap.pack(side="left")
        
        tk.Label(filter_wrap, text="Tầng:", bg=_get_c("BG"), fg=_get_c("TEXT"), font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 12))
        
        floors_frame = tk.Frame(filter_wrap, bg=_get_c("BORDER"), padx=1, pady=1)
        floors_frame.pack(side="left")
        
        floors = ["Tat ca", "Tang 1", "Tang 2", "Tang 3", "Tang 4", "Tang 5"]
        for f in floors:
            btn_text = f.replace("Tang ", "T") if f != "Tat ca" else "Tất cả"
            btn_f = tk.Radiobutton(
                floors_frame, text=btn_text, variable=self._floor_var, value=f,
                indicatoron=0, bg=_get_c("SURFACE"), fg=_get_c("TEXT"), selectcolor=_get_c("ACCENT"),
                activebackground=_get_c("ACCENT"), font=("Segoe UI", 8, "bold"),
                padx=12, pady=5, borderwidth=0, command=self.refresh,
                cursor="hand2"
            )
            btn_f.pack(side="left", padx=0)

        # Search box (Premium style)
        search_wrap = tk.Frame(toolbar, bg=_get_c("BG"))
        search_wrap.pack(side="left", padx=(40, 0))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        
        s_box = tk.Frame(search_wrap, bg=_get_c("SURFACE"), highlightthickness=1, highlightbackground=_get_c("BORDER"))
        s_box.pack(side="left")
        
        tk.Label(s_box, text=" 🔍 ", bg=_get_c("SURFACE"), fg=_get_c("MUTED"), font=("Segoe UI", 10)).pack(side="left")
        search_e = tk.Entry(s_box, textvariable=self.search_var, bg=_get_c("SURFACE"), fg=_get_c("TEXT"),
                             font=("Segoe UI", 9), width=20, relief="flat", insertbackground=_get_c("TEXT"))
        search_e.pack(side="left", pady=5, padx=(0, 10))
        search_e.bind("<FocusIn>", lambda _=None: s_box.config(highlightbackground=_get_c("ACCENT")))
        search_e.bind("<FocusOut>", lambda _=None: s_box.config(highlightbackground=_get_c("BORDER")))

        # Right Slot Info Card
        slot_card = tk.Frame(toolbar, bg=_get_c("INFO_BG"), padx=12, pady=6)
        slot_card.pack(side="right")
        tk.Label(slot_card, text="Ca hiện tại:", bg=_get_c("INFO_BG"), fg=_get_c("ACCENT"), font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(slot_card, text=f" {self._current_slot} ", bg=_get_c("ACCENT"), fg="white", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(5, 0))

        # Legend
        legend_bar = tk.Frame(self, bg=_get_c("BG"), padx=25)
        legend_bar.pack(fill="x", pady=(0, 15))
        for label, color in [("Trống", _get_c("SUCCESS")), ("Đang dùng", _get_c("DANGER")), ("Bảo trì", _get_c("WARNING"))]:
            f_leg = tk.Frame(legend_bar, bg=_get_c("BG"))
            f_leg.pack(side="left", padx=(0, 25))
            # Bullet with glow
            dot_cv = tk.Canvas(f_leg, width=12, height=12, bg=_get_c("BG"), highlightthickness=0)
            dot_cv.pack(side="left", padx=(0, 8))
            dot_cv.create_oval(2, 2, 10, 10, fill=color, outline="")
            tk.Label(f_leg, text=label, bg=_get_c("BG"), fg=_get_c("TEXT"), font=("Segoe UI", 8, "bold")).pack(side="left")

        # Main canvas wrap
        wrap = tk.Frame(self, bg=_get_c("BG"))
        wrap.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        self.canvas = tk.Canvas(wrap, bg=C_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _=None: self.refresh())

    def refresh(self) -> None:
        self.canvas.delete("all")
        rooms = self.room_ctrl.list_rooms()
        
        # Filter by floor
        floor_sel = self._floor_var.get()
        if floor_sel != "Tat ca":
            f_num = floor_sel.split()[-1]
            rooms = [r for r in rooms if r.room_id.startswith(f"P{f_num}") or r.room_id.startswith(f"E{f_num}")]

        # Filter by search
        search_q = self.search_var.get().lower()
        if search_q:
            rooms = [r for r in rooms if search_q in r.room_id.lower() or search_q in r.name.lower()]

        if not rooms:
            self.canvas.create_text(self.canvas.winfo_width()//2, 100, 
                                     text="Không tìm thấy phòng nào khớp với yêu cầu", 
                                     fill=C_MUTED, font=("Segoe UI", 10))
            return

        w = self.canvas.winfo_width()
        if w < 100: return

        # Grid Calculation
        card_w, card_h = 240, 130
        gap = 20
        cols = max(1, (w - 10) // (card_w + gap))
        margin = (w - (cols * card_w + (cols - 1) * gap)) // 2
        
        now_date = dt.date.today().isoformat()
        
        for i, room in enumerate(rooms):
            r, c = divmod(i, cols)
            x0, y0 = margin + c * (card_w + gap), gap + r * (card_h + gap)
            x1, y1 = x0 + card_w, y0 + card_h
            
            # Logic: Determine status
            status_color = C_SUCCESS
            status_text = "TRỐNG"
            busy_by = ""
            
            if room.status == "Bao tri":
                status_color = C_WARNING
                status_text = "BẢO TRÌ"
            elif room.status == "Ngung su dung":
                status_color = _get_c("MUTED")
                status_text = "KHÓA"
            elif self._current_slot != "Ngoai gio":
                busy_bookings = self.booking_ctrl.booking_dao.search(
                    room_id=room.room_id, date_from=now_date, date_to=now_date, status="Da duyet"
                )
                current_booking = next((b for b in busy_bookings if b.slot == self._current_slot), None)
                if current_booking:
                    status_color = _get_c("DANGER")
                    status_text = "ĐANG DÙNG"
                    busy_by = current_booking.user_full_name if hasattr(current_booking, "user_full_name") else "Đã đặt"

            # 1. Draw Card Background (Rounded with subtle shadow)
            # Shadow
            self._draw_rounded_rect(x0+2, y0+4, x1+2, y1+4, 15, fill=_get_c("SHADOW"), outline="")
            # Main Body
            card_id = self._draw_rounded_rect(x0, y0, x1, y1, 15, fill=_get_c("SURFACE"), outline=_get_c("BORDER"), width=1)
            
            # 2. Header Stripe
            self.canvas.create_arc(x0, y0, x0+30, y0+30, start=90, extent=90, fill=status_color, outline="")
            self.canvas.create_arc(x1-30, y0, x1, y0+30, start=0, extent=90, fill=status_color, outline="")
            self.canvas.create_rectangle(x0+15, y0, x1-15, y0+15, fill=status_color, outline="")
            self.canvas.create_rectangle(x0, y0+15, x1, y0+30, fill=status_color, outline="")

            # 3. Text Info
            # Room ID (White on status color background)
            self.canvas.create_text(x0 + 15, y0 + 15, text=room.room_id, 
                                     font=("Segoe UI", 11, "bold"), fill="white", anchor="w")
            
            # Room Type Icon
            type_icon = "💻" if "Lab" in room.room_type else "📖"
            self.canvas.create_text(x1 - 15, y0 + 15, text=type_icon, font=("Segoe UI", 10), anchor="e", fill="white")
            
            # Room Name (Large and bold)
            self.canvas.create_text(x0 + 15, y0 + 55, text=room.name, 
                                     font=("Segoe UI", 10, "bold"), fill=_get_c("TEXT"), anchor="w")
            
            # Details (Capacity)
            self.canvas.create_text(x0 + 15, y0 + 80, text=f"👥 Sức chứa: {room.capacity} chỗ", 
                                     font=("Segoe UI", 8), fill=_get_c("MUTED"), anchor="w")
            
            # Status Badge (Bottom)
            badge_y = y1 - 22
            self.canvas.create_rectangle(x0 + 15, badge_y - 8, x0 + 100, badge_y + 8, fill=_get_c("BG"), outline=_get_c("BORDER"), width=1)
            self.canvas.create_oval(x0+20, badge_y-3, x0+26, badge_y+3, fill=status_color, outline="")
            self.canvas.create_text(x0 + 32, badge_y, text=status_text, 
                                     font=("Segoe UI", 7, "bold"), fill=_get_c("TEXT"), anchor="w")
            
            # If busy, show user
            if busy_by:
                self.canvas.create_text(x1 - 15, badge_y, text=f"👤 {busy_by}", 
                                         font=("Segoe UI", 8, "italic"), fill="#94a3b8", anchor="e")

            # 4. Interactive Bindings
            def _on_enter(e, cid=card_id, x0=x0, y0=y0, x1=x1, y1=y1):
                self.canvas.itemconfig(cid, outline=C_PRIMARY, width=2)
                # Could add a tooltip here
            
            def _on_leave(e, cid=card_id):
                self.canvas.itemconfig(cid, outline="#e2e8f0", width=1)
            
            def _on_click(e, r=room, st=status_text, by=busy_by):
                msg = f"📍 Phòng {r.room_id}: {r.name}\n\n"
                msg += f"• Loại: {r.room_type}\n"
                msg += f"• Sức chứa: {r.capacity}\n"
                msg += f"• Trạng thái: {st}\n"
                if by: msg += f"• Đang dùng bởi: {by}"
                toast(self, msg, kind="info")

            self.canvas.tag_bind(card_id, "<Enter>", _on_enter)
            self.canvas.tag_bind(card_id, "<Leave>", _on_leave)
            self.canvas.tag_bind(card_id, "<Button-1>", _on_click)

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)
