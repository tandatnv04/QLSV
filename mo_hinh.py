"""
MÔ HÌNH DỮ LIỆU YÊU CẦU (Pydantic) — tên trường trùng với tên cột tiếng Việt trong cơ sở dữ liệu.
"""

from datetime import date

from pydantic import BaseModel, Field


# ---------------- Xác thực ----------------
class YeuCauDangNhap(BaseModel):
    tên_đăng_nhập: str = Field(min_length=1)
    mật_khẩu: str = Field(min_length=1)


class YeuCauQuenMatKhau(BaseModel):
    thông_tin_tài_khoản: str = Field(min_length=1, description="Tên đăng nhập, email hoặc mã số")
    mật_khẩu_mới: str
    xác_nhận_mật_khẩu: str


# ---------------- Hồ sơ & người dùng ----------------
class YeuCauCapNhatHoSo(BaseModel):
    họ_tên: str = Field(min_length=1)
    chức_danh: str = ""
    tuổi: int | None = Field(default=None, ge=1, le=120)
    khoa: str = ""
    email: str = ""
    số_điện_thoại: str = ""


class YeuCauAnhDaiDien(BaseModel):
    ảnh_đại_diện: str = Field(min_length=1, description="Ảnh dạng data URL base64")


class YeuCauTaoNguoiDung(BaseModel):
    tên_đăng_nhập: str = Field(min_length=1)
    mật_khẩu: str = Field(min_length=1)
    vai_trò: str
    họ_tên: str = Field(min_length=1)
    mã_số: str = ""
    khoa: str = ""
    email: str = ""
    số_điện_thoại: str = ""


class YeuCauCapNhatNguoiDung(BaseModel):
    họ_tên: str = Field(min_length=1)
    vai_trò: str
    mã_số: str = ""
    khoa: str = ""
    email: str = ""
    số_điện_thoại: str = ""
    trạng_thái: str
    mật_khẩu_mới: str = ""


# ---------------- Môn học ----------------
class YeuCauTaoMonHoc(BaseModel):
    mã_môn: str = Field(min_length=1)
    tên_môn: str = Field(min_length=1)
    số_tín_chỉ: int = Field(default=3, ge=1, le=10)
    đơn_giá_tín_chỉ: int = Field(default=450_000, ge=0)
    khoa: str = ""
    học_kỳ: str = ""
    mô_tả: str = ""


class YeuCauHanNhapDiem(BaseModel):
    ngày_mở_nhập_điểm: date
    ngày_chốt_điểm: date
    khóa_nhập_điểm: bool = False


# ---------------- Lịch học ----------------
class YeuCauTaoLichHoc(BaseModel):
    id_môn: str = ""
    định_danh_môn: str = ""
    id_giảng_viên: str = ""
    định_danh_giảng_viên: str = ""
    phòng_học: str = Field(min_length=1)
    thứ: str
    tuần: int = Field(default=1, ge=1, le=60)
    giờ_bắt_đầu: str = Field(pattern=r"^\d{1,2}:\d{2}$")
    giờ_kết_thúc: str = Field(pattern=r"^\d{1,2}:\d{2}$")

    def lay_id_mon(self) -> str:
        return self.id_môn or self.định_danh_môn

    def lay_id_giang_vien(self) -> str:
        return self.id_giảng_viên or self.định_danh_giảng_viên


# ---------------- Điểm danh ----------------
class BanGhiDiemDanh(BaseModel):
    id_sinh_viên: str = ""
    định_danh_sinh_viên: str = ""
    trạng_thái: str
    ghi_chú: str = ""

    def lay_id_sinh_vien(self) -> str:
        return self.id_sinh_viên or self.định_danh_sinh_viên


class YeuCauLuuDiemDanh(BaseModel):
    id_lịch_học: str = ""
    định_danh_lịch_học: str = ""
    ngày: date
    danh_sách: list[BanGhiDiemDanh]

    def lay_id_lich_hoc(self) -> str:
        return self.id_lịch_học or self.định_danh_lịch_học


# ---------------- Điểm số ----------------
class YeuCauLuuDiem(BaseModel):
    điểm_giữa_kỳ: float = Field(ge=0, le=10)
    điểm_cuối_kỳ: float = Field(ge=0, le=10)
    nhận_xét: str = ""


class YeuCauTinhDiem(BaseModel):
    điểm_giữa_kỳ: float | None = None
    điểm_cuối_kỳ: float | None = None
