# BTL-nhom24
Nhóm 24 – Hệ thống quản lý đặt phòng học trong trường đại học

---

## Mô tả chương trình

**Hệ Thống Quản Lý Đặt Phòng Học** là ứng dụng desktop xây dựng bằng Python + Tkinter, kết nối cơ sở dữ liệu MySQL. Hệ thống hỗ trợ ba vai trò: **Admin**, **Giảng viên** và **Sinh viên**.

### Chức năng chính

| Chức năng | Mô tả |
|---|---|
| Đăng nhập | Xác thực tài khoản, phân quyền theo vai trò |
| Trang chủ | Thống kê nhanh (tổng phòng, đặt hôm nay, chờ duyệt, từ chối), danh sách đặt phòng gần đây |
| Quản lý phòng học | Thêm/sửa/xóa phòng, tìm kiếm, xem tình trạng |
| Đặt phòng | Form đặt phòng 2 cột: chọn phòng, ngày, ca học, hiển thị ca còn trống |
| Danh sách đặt phòng | Lọc theo ngày/phòng/trạng thái, duyệt/từ chối, xuất Excel |
| Quản lý tài khoản | Thêm/sửa/xóa tài khoản (Admin/GV/SV) |
| Quản lý thiết bị | Theo dõi thiết bị theo phòng, trạng thái hoạt động/bảo trì |
| Báo cáo thống kê | Bảng tổng hợp + biểu đồ cột tỷ lệ sử dụng phòng, xuất Excel |
| Lịch biểu phòng | Lưới tuần (Ca × Thứ), hiển thị trạng thái từng ô |
| Thông báo | Thông báo kết quả duyệt/từ chối cho GV và SV |

---

## Thiết kế chi tiết

### Phân quyền (Role-based)

```
Admin       → Tất cả chức năng
Giảng viên  → Trang chủ · Đặt phòng · Lịch đặt của tôi · Thông báo
Sinh viên   → Trang chủ · Đặt phòng · Lịch đặt của tôi · Thông báo
```

### Giao diện (GUI Layout)

```
┌──────────────────────────────────────────────────────────┐
│  TOPBAR: Tiêu đề hệ thống  │  Tên người dùng │ Đăng xuất │
├────────────┬─────────────────────────────────────────────┤
│            │                                             │
│  SIDEBAR   │            CONTENT AREA                     │
│  (200 px)  │            (thay đổi theo trang)            │
│            │                                             │
└────────────┴─────────────────────────────────────────────┘
```

### Cơ sở dữ liệu (MySQL) – ERD chính

| Bảng | Các cột chính |
|---|---|
| `users` | id, ten, vaitro, email, sdt, mat_khau (SHA-256), trang_thai |
| `rooms` | id, ten, loai, suc_chua, tang, toa, trang_thiet_bi, trang_thai |
| `bookings` | id, user_id (FK), room_id (FK), ngay, ca, muc_dich, trang_thai |
| `equipment` | id, ten, loai, room_id (FK), trang_thai, ngay_mua |

---

## Cấu trúc mã nguồn

```
BTL-nhom24/
├── main.py                   # Toàn bộ ứng dụng GUI (entry point)
├── requirements.txt          # Các thư viện Python cần cài
├── README.md                 # Tài liệu dự án
├── Giao Dien.drawio          # Sơ đồ ERD / Use Case / Flowchart
└── Trang Giao Diện/          # Ảnh thiết kế mockup từng màn hình
    ├── Chức năng đăng nhập.png
    ├── Trang chủ ADMIN.png
    ├── Quản lý phòng học.png
    ├── FORM đặt phòng.png
    ├── Danh sách đặt phòng.png
    ├── Quản lý người dùng.png
    ├── Quản lý thiết bị.png
    ├── Báo cáo thống kê.png
    ├── Lịch Biểu Phòng Học.png
    └── Chi Tiết phòng học.png
```

### Giải thích `main.py`

| Lớp / Hàm | Ý nghĩa |
|---|---|
| `App` | Cửa sổ gốc Tk, điều hướng giữa màn hình đăng nhập và shell chính |
| `LoginFrame` | Màn hình đăng nhập (username, password, vai trò) |
| `MainShell` | Shell chính: TopBar + Sidebar + vùng Content; xây dựng nav theo role |
| `_BasePage` | Frame cơ sở có scroll dọc, tất cả trang kế thừa |
| `HomePage` | Trang chủ: 4 thẻ thống kê + bảng đặt phòng gần đây |
| `RoomManagementPage` | Quản lý phòng: CRUD table + dialog inline + tìm kiếm |
| `BookingFormPage` | Form đặt phòng 2 cột: thông tin người đặt / chọn ca và mục đích |
| `BookingListPage` | Danh sách đặt phòng: bộ lọc + bảng trạng thái màu + phân trang |
| `UserManagementPage` | Quản lý tài khoản: bảng + dialog thêm/sửa |
| `EquipmentPage` | Quản lý thiết bị: bảng lọc theo phòng |
| `StatisticsPage` | Báo cáo: bảng tổng hợp + biểu đồ cột vẽ trên Canvas |
| `SchedulePage` | Lịch biểu: lưới Ca × Thứ hiển thị đặt phòng theo tuần |
| `NotifyPage` | Thông báo duyệt/từ chối cho GV và SV |
| `build_treeview()` | Hàm tiện ích tạo Treeview có scrollbar và style chuẩn |
| `MOCK_*` | Dữ liệu mẫu (thay bằng kết nối MySQL thực khi triển khai) |

---

---
THÀNH VIÊN
- Trần Trung Hiếu
- Nguyễn Huy Hải
- Nguyễn Tuấn Minh
## Các công cụ xây dựng hệ thống

### 1. MySQL
Hệ quản trị cơ sở dữ liệu quan hệ (RDBMS) được sử dụng để lưu trữ toàn bộ dữ liệu của hệ thống: thông tin phòng học, lịch đặt phòng, tài khoản người dùng (admin, giảng viên), danh sách thiết bị trong phòng. Hỗ trợ các truy vấn SQL phức tạp như kiểm tra xung đột lịch, thống kê tần suất sử dụng phòng.

### 2. Visual Studio Code (VS Code)
Môi trường phát triển tích hợp (IDE) chính để viết code Python. Sử dụng các extension hỗ trợ: **Python Extension** (chạy & debug), **MySQL Extension** (xem và quản lý database trực tiếp trong VS Code), **GitLens** (quản lý lịch sử Git).

### 3. Git
Hệ thống quản lý phiên bản (Version Control System) cục bộ. Theo dõi lịch sử thay đổi source code, cho phép rollback khi có lỗi, hỗ trợ làm việc song song trên nhiều tính năng (branching).

### 4. GitHub
Nền tảng lưu trữ source code từ xa và cộng tác nhóm. Các thành viên nhóm 24 đẩy code lên (push), kéo code về (pull), tạo Pull Request để review code trước khi merge vào nhánh chính.

### 5. Draw.io
Công cụ vẽ sơ đồ thiết kế hệ thống, bao gồm:
- **Sơ đồ ERD** (Entity-Relationship Diagram): mô tả các bảng trong MySQL và mối quan hệ giữa chúng (phòng học – lịch đặt – người dùng).
- **Sơ đồ Use Case**: mô tả các chức năng của hệ thống theo từng vai trò (admin, giảng viên, sinh viên).
- **Flowchart**: mô tả luồng xử lý đặt phòng, kiểm tra xung đột lịch.

---

## Các module / thư viện Python được sử dụng

| Thư viện | Nhiệm vụ |
|---|---|
| `mysql-connector-python` | Kết nối Python với MySQL, thực hiện truy vấn SQL quản lý dữ liệu phòng học, lịch đặt, tài khoản |
| `tkinter` | Xây dựng giao diện đồ họa (GUI) desktop – form đăng nhập, quản lý phòng, form đặt phòng |
| `datetime` | Xử lý ngày giờ, kiểm tra ca đặt phòng hợp lệ, phát hiện xung đột lịch |
| `hashlib` | Mã hóa mật khẩu người dùng (SHA-256) trước khi lưu vào MySQL |
| `re` | Kiểm tra định dạng dữ liệu nhập vào – mã phòng, email, số điện thoại |
| `openpyxl` | Xuất báo cáo thống kê sử dụng phòng học ra file Excel (.xlsx) |
| `tkcalendar` | Hiển thị widget chọn ngày (DatePicker) trong giao diện tkinter |
| `Pillow` | Hiển thị logo trường hoặc hình ảnh minh họa trong giao diện tkinter |

---

## Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

## Tóm tắt luồng và công cụ tương ứng

```
Draw.io          → Thiết kế ERD, Use Case, Flowchart
VS Code          → Viết code Python
Git + GitHub     → Quản lý và chia sẻ source code nhóm

Giao diện        → tkinter, tkcalendar, Pillow
Xử lý logic      → datetime, re, hashlib
Kết nối CSDL     → mysql-connector-python ↔ MySQL
Xuất báo cáo     → openpyxl
```
