# 🏫 Hệ Thống Quản Lý Đặt Phòng Học (Classroom Booking Management System)

**Nhóm 24** — Bài tập lớn môn Phát triển ứng dụng Desktop.

---

## 📝 Giới thiệu

Hệ thống **Quản lý đặt phòng học** là ứng dụng desktop xây dựng bằng **Python + Tkinter**, sử dụng kiến trúc **MVC** (Model – View – Controller). Ứng dụng cung cấp giải pháp chuyển đổi số cho việc quản lý, theo dõi và đặt phòng học trong môi trường đại học, giúp tối ưu hóa việc sử dụng cơ sở vật chất và quy trình phê duyệt.

## ✨ Tính năng chính

### 🛠️ Quản trị viên (Admin)
- **Quản lý người dùng:** Thêm, sửa, xóa và phân quyền tài khoản.
- **Quản lý phòng học:** CRUD thông tin phòng, tình trạng, sức chứa.
- **Quản lý thiết bị:** Theo dõi thiết bị theo từng phòng, tình trạng bảo trì.
- **Phê duyệt yêu cầu:** Duyệt/từ chối yêu cầu đặt phòng, gửi email thông báo tự động.
- **Báo cáo thống kê:** Dashboard tổng hợp, xuất Excel/PDF.
- **Quản lý sự cố:** Xem & xử lý báo cáo lỗi phòng học.

### 👨‍🏫 Giảng viên
- Đặt phòng học, theo dõi trạng thái phê duyệt.
- Xem lịch biểu phòng, tìm phòng trống.
- Đánh giá & báo lỗi phòng học.

### 🎓 Sinh viên
- Yêu cầu mượn phòng (cần Admin duyệt).
- Xem lịch sử đặt phòng cá nhân.
- Đánh giá & báo lỗi phòng học.

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.10+ |
| Giao diện | Tkinter + ttk (có theme tùy chỉnh) |
| Cơ sở dữ liệu | SQLite (tự khởi tạo, không cần cài đặt riêng) |
| Bảo mật | PBKDF2-HMAC-SHA256 (100 000 iterations) cho mật khẩu |
| Email | SMTP (Gmail App Password, tùy chọn) |
| Xuất file | openpyxl (Excel), fpdf2 (PDF) |
| Lịch | tkcalendar |
| Testing | pytest |
| Logging | Rotating file handler → `logs/app.log` |

---

## 📂 Cấu trúc thư mục

```text
BTL-nhom24/
├── main.py                  # Root launcher
├── requirements.txt         # Thư viện cần cài
├── src/
│   ├── back end/
│   │   ├── main.py          # Entry point chính (Tkinter App)
│   │   ├── controllers/     # Business logic (MVC Controller)
│   │   │   ├── auth_controller.py
│   │   │   ├── booking_controller.py
│   │   │   ├── equipment_controller.py
│   │   │   ├── report_controller.py
│   │   │   ├── room_controller.py
│   │   │   ├── room_feedback_controller.py
│   │   │   └── user_controller.py
│   │   ├── dao/             # Data Access Object (SQLite)
│   │   ├── database/        # Schema, migrations, seed data
│   │   ├── models/          # Dataclass models
│   │   └── utils/           # Helpers: hash, email, export, logger
│   └── font-end/
│       └── gui/             # Tkinter GUI frames
├── tests/                   # pytest test suite (75 tests)
└── Docs/                    # Tài liệu thiết kế
```

---

## 🚀 Hướng dẫn cài đặt & chạy

### 1. Clone & chuẩn bị

```bash
git clone https://github.com/tranhieu122/BTL-nhom24.git
cd BTL-nhom24

# (Khuyến nghị) Tạo môi trường ảo
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Cài thư viện

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
python main.py
```

> **Lưu ý:** Không cần cài đặt CSDL riêng. SQLite tự động tạo file `classroom_booking.db` và seed dữ liệu mẫu khi chạy lần đầu.

### 4. Tài khoản mặc định

| Username | Password | Vai trò |
|---|---|---|
| `admin` | `admin123` | Admin |
| `gv01` | `gv123` | Giảng viên |
| `sv01` | `sv123` | Sinh viên |

### 5. Chạy tests

```bash
python -m pytest tests/ -v
```

### 6. Cấu hình email (tùy chọn)

Tạo file `.env` ở thư mục gốc:

```env
EMAIL_ENABLED=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## 🔒 Bảo mật

- **Mật khẩu:** Mã hóa bằng PBKDF2-HMAC-SHA256 với salt ngẫu nhiên 16 byte, 100 000 iterations. Tương thích ngược với hash SHA-256 cũ (tự động nâng cấp khi đăng nhập).
- **SQL Injection:** Tất cả truy vấn sử dụng parameterized queries (`?`).
- **Phân quyền:** 3 vai trò (Admin, Giảng viên, Sinh viên) với quyền truy cập khác nhau.
- **Logging:** Tất cả thao tác quan trọng được ghi vào `logs/app.log` (rotate 2MB, 3 backup).

---

## 📊 Kiến trúc hệ thống

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   GUI/View   │────▶│  Controller  │────▶│   DAO/Model  │
│  (Tkinter)   │◀────│ (Logic)      │◀────│   (SQLite)   │
└──────────────┘     └──────────────┘     └──────────────┘
```

- **Model:** Dataclass đơn giản (`User`, `Room`, `Booking`, `Equipment`, `Schedule`).
- **View:** Tkinter frames trong `gui/`, mỗi màn hình một file.
- **Controller:** Xử lý validation, business logic, giao tiếp giữa GUI và DAO.
- **DAO:** Thao tác CRUD trực tiếp với SQLite qua parameterized queries.

---

## 👥 Nhóm thực hiện (Nhóm 24)

| STT | Họ và Tên | Vai trò |
|---|---|---|
| 1 | **Trần Trung Hiếu** | |
| 2 | **Nguyễn Huy Hải** | |
| 3 | **Nguyễn Tuấn Minh** | |

