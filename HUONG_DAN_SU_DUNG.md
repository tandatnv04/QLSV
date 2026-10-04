# HƯỚNG DẪN HỆ THỐNG QUẢN LÝ SINH VIÊN EDUPRO ENTERPRISE
*(Kiến trúc Backend Python FastAPI & Dữ liệu chuẩn Tiếng Việt)*

---

## 1. Cấu Trúc Mã Nguồn Sau Khi Viết Lại

Tất cả các logic xử lý và router đã được viết lại bằng **Python (FastAPI)**, với tên file và hàm hoàn toàn bằng **tiếng Việt có dấu theo chuẩn chức năng**:

```
Quản lý sinh viên/
│
├── du_lieu/
│   └── du_lieu_mau.json              # Dữ liệu mẫu chuẩn tiếng Việt có dấu
│
├── services/                         # Tầng xử lý nghiệp vụ (Business Services)
│   ├── __init__.py
│   ├── xac_thuc.py                   # Đăng nhập, khôi phục mật khẩu
│   ├── nguoi_dung.py                 # Hồ sơ, đổi avatar, phân quyền & CRUD tài khoản
│   ├── mon_hoc.py                    # Danh mục môn học, cấu hình hạn mở/khóa điểm
│   ├── lich_hoc.py                   # Thời khóa biểu, xếp lịch dạy, kiểm tra trùng phòng/giờ
│   ├── diem_danh.py                  # Điểm danh chuyên cần theo lớp học phần
│   ├── diem_so.py                    # Sổ điểm, nhập điểm, xuất CSV, bảng điểm transcript
│   ├── hoc_phan.py                   # Đăng ký môn học, tra cứu và nộp học phí
│   ├── tinh_diem.py                  # Tính điểm tổng kết, quy đổi điểm chữ, hệ 4, GPA
│   └── thong_ke.py                   # Thống kê KPI & phân bố môn học cho Dashboard
│
├── routers/                          # Tầng Router API (FastAPI Routers)
│   ├── __init__.py
│   ├── xac_thuc.py                   # /api/xac-thuc (dang-nhap, dang-xuat, quen-mat-khau)
│   ├── ho_so.py                      # /api/ho-so (xem, sua, anh-dai-dien)
│   ├── nguoi_dung.py                 # /api/nguoi-dung (sinh-vien, giang-vien, CRUD)
│   ├── mon_hoc.py                    # /api/mon-hoc (them, xoa, han-nhap-diem)
│   ├── lich_hoc.py                   # /api/lich-hoc (thoi-khoa-bieu, xep-lich)
│   ├── diem_danh.py                  # /api/diem-danh (danh-sach, luu)
│   ├── diem_so.py                    # /api/diem-so (so-diem, xuat-csv, bang-diem-sinh-vien)
│   ├── hoc_phan.py                   # /api/hoc-phan (dang-ky, huy-dang-ky, hoc-phi)
│   └── thong_ke.py                   # /api/thong-ke (tong-quan)
│
├── cau_hinh.py                       # Cấu hình tập trung (Firebase URL, Secret Key, Session)
├── co_so_du_lieu.py                  # Lớp kết nối CSDL (hỗ trợ cả Firebase Realtime Database và SQLite .db)
├── quan_ly_sinh_vien.db              # Tệp Cơ sở dữ liệu SQLite (.db) lưu toàn bộ bảng dữ liệu
├── tao_tep_co_so_du_lieu.py          # Script tự động tạo / reset tệp SQLite .db từ dữ liệu mẫu
├── hang_so.py                        # Các hằng số tiếng Việt (Vai trò, Trạng thái, Bảng dữ liệu)
├── mo_hinh.py                        # Các mô hình Pydantic kiểm tra dữ liệu yêu cầu
├── ngoai_le.py                       # Lớp ngoại lệ nghiệp vụ trả về thông báo lỗi chuẩn
├── ung_dung.py                       # File khởi chạy FastAPI App, Mount Static & Middleware
├── requirements.txt                  # Danh sách thư viện phụ thuộc Python
├── chay_he_thong.bat                 # Script chạy nhanh 1 chạm trên Windows
│
├── index.html                        # Giao diện HTML5 chuẩn giữ nguyên phong cách Flame Slate
└── static/
    ├── css/style.css                 # CSS Glassmorphism giao diện tối/sáng
    ├── js/dieu_khien.js              # Bộ điều khiển giao diện gọi API Backend FastAPI
    └── img/                          # Hình ảnh tài nguyên
```

---

## 2. Chuẩn Dữ Liệu Tiếng Việt Có Dấu Mới

File dữ liệu [`du_lieu/du_lieu_mau.json`](file:///c:/Users/duyih/Downloads/Quản%20lý%20sinh%20viên/du_lieu/du_lieu_mau.json) và các nhánh trên Firebase Realtime Database được chuẩn hóa hoàn toàn sang tiếng Việt:

| Nhánh dữ liệu | Tên cột / trường chuẩn tiếng Việt có dấu |
| :--- | :--- |
| **người_dùng** | `định_danh`, `tên_đăng_nhập`, `mật_khẩu`, `vai_trò`, `họ_tên`, `mã_số`, `email`, `số_điện_thoại`, `khoa`, `chức_danh`, `tuổi`, `lớp`, `ảnh_đại_diện`, `trạng_thái` |
| **môn_học** | `định_danh`, `mã_môn`, `tên_môn`, `số_tín_chỉ`, `khoa`, `đơn_giá_tín_chỉ`, `học_kỳ`, `mô_tả`, `ngày_mở_nhập_điểm`, `ngày_chốt_điểm`, `khóa_nhập_điểm` |
| **lịch_học** | `định_danh`, `định_danh_môn`, `mã_môn`, `tên_môn`, `định_danh_giảng_viên`, `tên_giảng_viên`, `phòng_học`, `thứ`, `tuần`, `giờ_bắt_đầu`, `giờ_kết_thúc` |
| **đăng_ký_học_phần** | `định_danh`, `định_danh_sinh_viên`, `định_danh_môn`, `điểm_giữa_kỳ`, `điểm_cuối_kỳ`, `điểm_chuyên_cần`, `nhận_xét`, `đã_đóng_học_phí` |
| **điểm_danh** | `định_danh`, `định_danh_lịch_học`, `ngày`, `danh_sách` (`định_danh_sinh_viên`, `trạng_thái`, `ghi_chú`) |

---

## 3. Cách Khởi Chạy Ứng Dụng

### Cách 1: Chạy bằng file Batch
Nháy đúp chuột vào file [`chay_he_thong.bat`](file:///c:/Users/duyih/Downloads/Quản%20lý%20sinh%20viên/chay_he_thong.bat).

### Cách 2: Chạy bằng lệnh Terminal
```powershell
python -m uvicorn ung_dung:app --host 127.0.0.1 --port 8000 --reload
```

- **Giao diện người dùng:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Tài liệu API Swagger tự động:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 4. Danh Sách Tài Khoản Đăng Nhập Chính Xác

Tất cả các tài khoản mặc định đều có mật khẩu chung là: **`123`**

| Vai trò | Tên đăng nhập | Mật khẩu | Họ và tên | Mã số |
| :--- | :--- | :--- | :--- | :--- |
| **Quản trị viên** | `admin` | **`123`** | TS. Nguyễn Hoàng Nam | AD001 |
| **Giảng viên 1** | `teacher1` | **`123`** | ThS. Lê Thị Mai | GV001 |
| **Giảng viên 2** | `teacher2` | **`123`** | TS. Trần Quốc Bảo | GV002 |
| **Sinh viên 1** | `student1` | **`123`** | Nguyễn Văn An | SV2026001 |
| **Sinh viên 2** | `student2` | **`123`** | Trần Thị Bích | SV2026002 |
| **Sinh viên 3** | `student3` | **`123`** | Phạm Quốc Cường | SV2026003 |
