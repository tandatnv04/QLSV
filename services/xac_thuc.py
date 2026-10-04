"""
XÁC THỰC: đăng nhập, khôi phục mật khẩu.
"""

from co_so_du_lieu import csdl
from hang_so import BANG_NGUOI_DUNG, TRANG_THAI_DA_KHOA
from ngoai_le import KhongTimThay, LoiNghiepVu

DO_DAI_MAT_KHAU_TOI_THIEU = 3


def dang_nhap(ten_dang_nhap: str, mat_khau: str) -> dict:
    ten_dang_nhap = ten_dang_nhap.strip()
    mat_khau = mat_khau.strip()

    nguoi_dung = next(
        (
            nd
            for nd in csdl.lay_danh_sach(BANG_NGUOI_DUNG)
            if nd.get("tên_đăng_nhập") == ten_dang_nhap and nd.get("mật_khẩu") == mat_khau
        ),
        None,
    )
    if not nguoi_dung:
        raise LoiNghiepVu("Tên đăng nhập hoặc mật khẩu không chính xác!", 401)
    if nguoi_dung.get("trạng_thái") == TRANG_THAI_DA_KHOA:
        raise LoiNghiepVu("Tài khoản này đã bị khóa. Vui lòng liên hệ Quản trị viên!", 403)
    return nguoi_dung


def dat_lai_mat_khau(thong_tin_tai_khoan: str, mat_khau_moi: str, xac_nhan_mat_khau: str) -> dict:
    thong_tin = thong_tin_tai_khoan.strip().lower()
    mat_khau_moi = mat_khau_moi.strip()

    if not thong_tin:
        raise LoiNghiepVu("Vui lòng nhập tên đăng nhập, email hoặc mã số!")
    if len(mat_khau_moi) < DO_DAI_MAT_KHAU_TOI_THIEU:
        raise LoiNghiepVu(f"Mật khẩu mới phải có ít nhất {DO_DAI_MAT_KHAU_TOI_THIEU} ký tự!")
    if mat_khau_moi != xac_nhan_mat_khau.strip():
        raise LoiNghiepVu("Mật khẩu xác nhận không trùng khớp!")

    nguoi_dung = next(
        (
            nd
            for nd in csdl.lay_danh_sach(BANG_NGUOI_DUNG)
            if thong_tin
            in (
                (nd.get("tên_đăng_nhập") or "").lower(),
                (nd.get("email") or "").lower(),
                (nd.get("mã_số") or "").lower(),
            )
        ),
        None,
    )
    if not nguoi_dung:
        raise KhongTimThay("Không tìm thấy tài khoản tương ứng với thông tin đã nhập!")

    csdl.cap_nhat_ban_ghi(BANG_NGUOI_DUNG, nguoi_dung["định_danh"], {"mật_khẩu": mat_khau_moi})
    return nguoi_dung
