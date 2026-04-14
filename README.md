# BTL-nhom24
Nhóm 24 – Hệ thống quản lý đặt phòng học

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
