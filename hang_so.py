"""
HẰNG SỐ DÙNG CHUNG: tên bảng dữ liệu, vai trò, trạng thái, giá trị mặc định.
"""

# ---- Tên các bảng (nhánh gốc) trong Firebase Realtime Database ----
BANG_NGUOI_DUNG = "người_dùng"
BANG_MON_HOC = "môn_học"
BANG_LICH_HOC = "lịch_học"
BANG_DANG_KY = "đăng_ký_học_phần"
BANG_DIEM_DANH = "điểm_danh"

# ---- Vai trò người dùng ----
VAI_TRO_QUAN_TRI = "Quản trị viên"
VAI_TRO_GIANG_VIEN = "Giảng viên"
VAI_TRO_SINH_VIEN = "Sinh viên"
DANH_SACH_VAI_TRO = (VAI_TRO_QUAN_TRI, VAI_TRO_GIANG_VIEN, VAI_TRO_SINH_VIEN)

# ---- Trạng thái tài khoản ----
TRANG_THAI_HOAT_DONG = "Hoạt động"
TRANG_THAI_DA_KHOA = "Đã khóa"
DANH_SACH_TRANG_THAI_TAI_KHOAN = (TRANG_THAI_HOAT_DONG, TRANG_THAI_DA_KHOA)

# ---- Trạng thái điểm danh ----
DIEM_DANH_CO_MAT = "Có mặt"
DIEM_DANH_DI_MUON = "Đi muộn"
DIEM_DANH_VANG_CO_PHEP = "Vắng có phép"
DIEM_DANH_VANG_KHONG_PHEP = "Vắng không phép"
DANH_SACH_TRANG_THAI_DIEM_DANH = (
    DIEM_DANH_CO_MAT,
    DIEM_DANH_DI_MUON,
    DIEM_DANH_VANG_CO_PHEP,
    DIEM_DANH_VANG_KHONG_PHEP,
)

# ---- Thứ trong tuần (dùng để sắp xếp thời khóa biểu) ----
THU_TRONG_TUAN = ("Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật")

# ---- Giá trị mặc định ----
DON_GIA_TIN_CHI_MAC_DINH = 450_000
SO_TIN_CHI_MAC_DINH = 3
HOC_KY_MAC_DINH = "Học kỳ 1 - 2026"
KHOA_MAC_DINH = "Công nghệ thông tin"
NGAY_MO_NHAP_DIEM_MAC_DINH = "2026-09-15"
NGAY_CHOT_DIEM_MAC_DINH = "2026-10-20"

# ---- Trọng số tính điểm ----
TRONG_SO_GIUA_KY = 0.4
TRONG_SO_CUOI_KY = 0.6

# ---- Giới hạn ảnh đại diện (chuỗi base64 của ảnh 5MB ~ 6.7MB ký tự) ----
KICH_THUOC_ANH_TOI_DA = 7 * 1024 * 1024


# ---- Các hàm tiện ích trích xuất ID an toàn (hỗ trợ cả id và định_danh) ----
def lay_id(ban_ghi: dict | None) -> str:
    if not ban_ghi or not isinstance(ban_ghi, dict):
        return ""
    return str(ban_ghi.get("id") or ban_ghi.get("định_danh") or "")


def lay_id_mon(ban_ghi: dict | None) -> str:
    if not ban_ghi or not isinstance(ban_ghi, dict):
        return ""
    return str(ban_ghi.get("id_môn") or ban_ghi.get("định_danh_môn") or "")


def lay_id_sinh_vien(ban_ghi: dict | None) -> str:
    if not ban_ghi or not isinstance(ban_ghi, dict):
        return ""
    return str(ban_ghi.get("id_sinh_viên") or ban_ghi.get("định_danh_sinh_viên") or "")


def lay_id_giang_vien(ban_ghi: dict | None) -> str:
    if not ban_ghi or not isinstance(ban_ghi, dict):
        return ""
    return str(ban_ghi.get("id_giảng_viên") or ban_ghi.get("định_danh_giảng_viên") or "")


def lay_id_lich_hoc(ban_ghi: dict | None) -> str:
    if not ban_ghi or not isinstance(ban_ghi, dict):
        return ""
    return str(ban_ghi.get("id_lịch_học") or ban_ghi.get("định_danh_lịch_học") or "")


def dong_bo_id(ban_ghi: dict | None) -> dict:
    """Đảm bảo bản ghi có đủ cả khóa 'id' và 'định_danh' để tương thích ngược 100%."""
    if not ban_ghi or not isinstance(ban_ghi, dict):
        return ban_ghi
    _id = lay_id(ban_ghi)
    if _id:
        ban_ghi["id"] = _id
        ban_ghi["định_danh"] = _id
    _id_mon = lay_id_mon(ban_ghi)
    if _id_mon:
        ban_ghi["id_môn"] = _id_mon
        ban_ghi["định_danh_môn"] = _id_mon
    _id_sv = lay_id_sinh_vien(ban_ghi)
    if _id_sv:
        ban_ghi["id_sinh_viên"] = _id_sv
        ban_ghi["định_danh_sinh_viên"] = _id_sv
    _id_gv = lay_id_giang_vien(ban_ghi)
    if _id_gv:
        ban_ghi["id_giảng_viên"] = _id_gv
        ban_ghi["định_danh_giảng_viên"] = _id_gv
    _id_lh = lay_id_lich_hoc(ban_ghi)
    if _id_lh:
        ban_ghi["id_lịch_học"] = _id_lh
        ban_ghi["định_danh_lịch_học"] = _id_lh
    return ban_ghi
