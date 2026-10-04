"""
QUẢN LÝ NGƯỜI DÙNG: hồ sơ cá nhân, ảnh đại diện, tài khoản & phân quyền (quản trị viên).
"""

import random

from co_so_du_lieu import csdl, tao_dinh_danh
from hang_so import (
    BANG_DANG_KY,
    BANG_LICH_HOC,
    BANG_NGUOI_DUNG,
    DANH_SACH_TRANG_THAI_TAI_KHOAN,
    DANH_SACH_VAI_TRO,
    KHOA_MAC_DINH,
    KICH_THUOC_ANH_TOI_DA,
    TRANG_THAI_DA_KHOA,
    TRANG_THAI_HOAT_DONG,
    VAI_TRO_GIANG_VIEN,
    VAI_TRO_QUAN_TRI,
    VAI_TRO_SINH_VIEN,
)
from ngoai_le import KhongTimThay, LoiNghiepVu

CHUC_DANH_MAC_DINH = {
    VAI_TRO_QUAN_TRI: "Quản trị viên",
    VAI_TRO_GIANG_VIEN: "Giảng viên",
    VAI_TRO_SINH_VIEN: "Sinh viên",
}
TUOI_MAC_DINH = {VAI_TRO_QUAN_TRI: 40, VAI_TRO_GIANG_VIEN: 32, VAI_TRO_SINH_VIEN: 20}


# ----------------------------------------------------------------------
# Tiện ích
# ----------------------------------------------------------------------
def an_mat_khau(nguoi_dung: dict) -> dict:
    """Loại bỏ mật khẩu trước khi trả dữ liệu về giao diện."""
    return {khoa: gia_tri for khoa, gia_tri in nguoi_dung.items() if khoa != "mật_khẩu"}


def _khop_tu_khoa(ban_ghi: dict, tu_khoa: str, *cac_truong: str) -> bool:
    if not tu_khoa:
        return True
    tu_khoa = tu_khoa.lower()
    return any(tu_khoa in str(ban_ghi.get(truong) or "").lower() for truong in cac_truong)


def lay_nguoi_dung(dinh_danh: str) -> dict:
    nguoi_dung = csdl.lay_ban_ghi(BANG_NGUOI_DUNG, dinh_danh)
    if not nguoi_dung:
        raise KhongTimThay("Không tìm thấy người dùng.")
    return nguoi_dung


def _kiem_tra_vai_tro(vai_tro: str) -> None:
    if vai_tro not in DANH_SACH_VAI_TRO:
        raise LoiNghiepVu(f"Vai trò không hợp lệ. Chỉ chấp nhận: {', '.join(DANH_SACH_VAI_TRO)}.")


def _sinh_ma_so(vai_tro: str) -> str:
    if vai_tro == VAI_TRO_SINH_VIEN:
        return f"SV{random.randint(100000, 999999)}"
    if vai_tro == VAI_TRO_GIANG_VIEN:
        return f"GV{random.randint(100, 999)}"
    return f"AD{random.randint(100, 999)}"


# ----------------------------------------------------------------------
# Hồ sơ cá nhân (mọi vai trò)
# ----------------------------------------------------------------------
def cap_nhat_ho_so(nguoi_dung: dict, du_lieu: dict) -> dict:
    thay_doi = {
        "họ_tên": du_lieu["họ_tên"].strip(),
        "chức_danh": du_lieu.get("chức_danh", "").strip(),
        "tuổi": du_lieu.get("tuổi") or TUOI_MAC_DINH.get(nguoi_dung.get("vai_trò"), 20),
        "khoa": du_lieu.get("khoa", "").strip(),
        "email": du_lieu.get("email", "").strip(),
        "số_điện_thoại": du_lieu.get("số_điện_thoại", "").strip(),
    }
    csdl.cap_nhat_ban_ghi(BANG_NGUOI_DUNG, nguoi_dung["định_danh"], thay_doi)
    return an_mat_khau({**nguoi_dung, **thay_doi})


def cap_nhat_anh_dai_dien(nguoi_dung: dict, anh_dai_dien: str | None) -> dict:
    if anh_dai_dien:
        if not (anh_dai_dien.startswith("data:image/") or anh_dai_dien.startswith("http")):
            raise LoiNghiepVu("Vui lòng chọn file hình ảnh hợp lệ (PNG, JPG, JPEG, WEBP)!")
        if len(anh_dai_dien) > KICH_THUOC_ANH_TOI_DA:
            raise LoiNghiepVu("Kích thước ảnh quá lớn! Vui lòng chọn ảnh dưới 5MB.")

    csdl.cap_nhat_ban_ghi(BANG_NGUOI_DUNG, nguoi_dung["định_danh"], {"ảnh_đại_diện": anh_dai_dien})
    ket_qua = {**nguoi_dung, "ảnh_đại_diện": anh_dai_dien}
    if not anh_dai_dien:
        ket_qua.pop("ảnh_đại_diện", None)
    return an_mat_khau(ket_qua)


def the_nguoi_dung(dinh_danh: str) -> dict:
    """Thông tin rút gọn để xem ảnh đại diện phóng to."""
    nd = lay_nguoi_dung(dinh_danh)
    return {
        truong: nd.get(truong)
        for truong in ("định_danh", "họ_tên", "mã_số", "vai_trò", "khoa", "lớp", "ảnh_đại_diện")
    }


# ----------------------------------------------------------------------
# Danh sách
# ----------------------------------------------------------------------
def danh_sach_nguoi_dung(vai_tro: str | None = None, tu_khoa: str = "") -> list[dict]:
    ket_qua = csdl.lay_danh_sach(BANG_NGUOI_DUNG)
    if vai_tro:
        ket_qua = [nd for nd in ket_qua if nd.get("vai_trò") == vai_tro]
    ket_qua = [
        nd for nd in ket_qua if _khop_tu_khoa(nd, tu_khoa, "họ_tên", "tên_đăng_nhập", "mã_số", "khoa")
    ]
    return [an_mat_khau(nd) for nd in ket_qua]


def danh_sach_sinh_vien(tu_khoa: str = "") -> list[dict]:
    ket_qua = [
        nd
        for nd in csdl.lay_danh_sach(BANG_NGUOI_DUNG)
        if nd.get("vai_trò") == VAI_TRO_SINH_VIEN and _khop_tu_khoa(nd, tu_khoa, "họ_tên", "mã_số", "khoa", "lớp")
    ]
    ket_qua.sort(key=lambda nd: nd.get("mã_số") or "")
    return [an_mat_khau(nd) for nd in ket_qua]


def danh_sach_giang_vien() -> list[dict]:
    return [
        {
            "id": nd.get("id") or nd.get("định_danh"),
            "định_danh": nd.get("id") or nd.get("định_danh"),
            "họ_tên": nd.get("họ_tên"),
            "mã_số": nd.get("mã_số"),
        }
        for nd in csdl.lay_danh_sach(BANG_NGUOI_DUNG)
        if nd.get("vai_trò") == VAI_TRO_GIANG_VIEN
    ]


# ----------------------------------------------------------------------
# Quản trị tài khoản (chỉ quản trị viên)
# ----------------------------------------------------------------------
def tao_nguoi_dung(du_lieu: dict) -> dict:
    vai_tro = du_lieu["vai_trò"]
    _kiem_tra_vai_tro(vai_tro)
    ten_dang_nhap = du_lieu["tên_đăng_nhập"].strip()

    tat_ca = csdl.lay_danh_sach(BANG_NGUOI_DUNG)
    if any((nd.get("tên_đăng_nhập") or "").lower() == ten_dang_nhap.lower() for nd in tat_ca):
        raise LoiNghiepVu("Tên đăng nhập này đã tồn tại!")

    ma_so = du_lieu.get("mã_số", "").strip() or _sinh_ma_so(vai_tro)
    if any((nd.get("mã_số") or "").lower() == ma_so.lower() for nd in tat_ca):
        raise LoiNghiepVu(f"Mã số {ma_so} đã được sử dụng!")

    nguoi_dung_moi = {
        "định_danh": tao_dinh_danh("nd"),
        "tên_đăng_nhập": ten_dang_nhap,
        "mật_khẩu": du_lieu["mật_khẩu"].strip(),
        "vai_trò": vai_tro,
        "họ_tên": du_lieu["họ_tên"].strip(),
        "mã_số": ma_so,
        "khoa": du_lieu.get("khoa", "").strip() or KHOA_MAC_DINH,
        "email": du_lieu.get("email", "").strip() or f"{ten_dang_nhap}@university.edu.vn",
        "số_điện_thoại": du_lieu.get("số_điện_thoại", "").strip(),
        "chức_danh": CHUC_DANH_MAC_DINH[vai_tro],
        "tuổi": TUOI_MAC_DINH[vai_tro],
        "trạng_thái": TRANG_THAI_HOAT_DONG,
    }
    csdl.luu_ban_ghi(BANG_NGUOI_DUNG, nguoi_dung_moi)
    return an_mat_khau(nguoi_dung_moi)


def cap_nhat_nguoi_dung(dinh_danh: str, du_lieu: dict, nguoi_thuc_hien: dict) -> dict:
    nguoi_dung = lay_nguoi_dung(dinh_danh)
    _kiem_tra_vai_tro(du_lieu["vai_trò"])
    if du_lieu["trạng_thái"] not in DANH_SACH_TRANG_THAI_TAI_KHOAN:
        raise LoiNghiepVu("Trạng thái tài khoản không hợp lệ.")

    la_chinh_minh = dinh_danh == nguoi_thuc_hien["định_danh"]
    if la_chinh_minh and du_lieu["vai_trò"] != VAI_TRO_QUAN_TRI:
        raise LoiNghiepVu("Không thể tự gỡ quyền Quản trị viên của chính mình!")
    if la_chinh_minh and du_lieu["trạng_thái"] == TRANG_THAI_DA_KHOA:
        raise LoiNghiepVu("Không thể tự khóa tài khoản của chính mình!")

    thay_doi = {
        "họ_tên": du_lieu["họ_tên"].strip(),
        "vai_trò": du_lieu["vai_trò"],
        "mã_số": du_lieu.get("mã_số", "").strip(),
        "khoa": du_lieu.get("khoa", "").strip(),
        "email": du_lieu.get("email", "").strip(),
        "số_điện_thoại": du_lieu.get("số_điện_thoại", "").strip(),
        "trạng_thái": du_lieu["trạng_thái"],
    }
    mat_khau_moi = du_lieu.get("mật_khẩu_mới", "").strip()
    if mat_khau_moi:
        thay_doi["mật_khẩu"] = mat_khau_moi

    csdl.cap_nhat_ban_ghi(BANG_NGUOI_DUNG, dinh_danh, thay_doi)
    return an_mat_khau({**nguoi_dung, **thay_doi})


def doi_trang_thai_khoa(dinh_danh: str, nguoi_thuc_hien: dict) -> dict:
    nguoi_dung = lay_nguoi_dung(dinh_danh)
    if dinh_danh == nguoi_thuc_hien["định_danh"]:
        raise LoiNghiepVu("Không thể tự khóa tài khoản của chính mình!")

    trang_thai_moi = (
        TRANG_THAI_HOAT_DONG if nguoi_dung.get("trạng_thái") == TRANG_THAI_DA_KHOA else TRANG_THAI_DA_KHOA
    )
    csdl.cap_nhat_ban_ghi(BANG_NGUOI_DUNG, dinh_danh, {"trạng_thái": trang_thai_moi})
    return an_mat_khau({**nguoi_dung, "trạng_thái": trang_thai_moi})


def xoa_nguoi_dung(dinh_danh: str, nguoi_thuc_hien: dict) -> None:
    nguoi_dung = lay_nguoi_dung(dinh_danh)
    if dinh_danh == nguoi_thuc_hien["định_danh"]:
        raise LoiNghiepVu("Không thể xóa tài khoản đang đăng nhập!")

    if nguoi_dung.get("vai_trò") == VAI_TRO_GIANG_VIEN:
        so_lich = sum(
            1 for lh in csdl.lay_danh_sach(BANG_LICH_HOC) if lh.get("định_danh_giảng_viên") == dinh_danh
        )
        if so_lich:
            raise LoiNghiepVu(
                f"Giảng viên đang được phân công {so_lich} lịch dạy. Hãy chuyển lịch dạy trước khi xóa."
            )

    if nguoi_dung.get("vai_trò") == VAI_TRO_SINH_VIEN:
        cac_dang_ky = [
            dk["định_danh"]
            for dk in csdl.lay_danh_sach(BANG_DANG_KY)
            if dk.get("định_danh_sinh_viên") == dinh_danh
        ]
        csdl.xoa_nhieu_ban_ghi(BANG_DANG_KY, cac_dang_ky)

    csdl.xoa_ban_ghi(BANG_NGUOI_DUNG, dinh_danh)
