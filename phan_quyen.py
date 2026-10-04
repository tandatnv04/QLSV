"""
PHÂN QUYỀN & PHIÊN ĐĂNG NHẬP

Cung cấp các phụ thuộc (dependency) FastAPI:
  - lay_nguoi_dung_hien_tai : bắt buộc đã đăng nhập
  - yeu_cau_vai_tro(...)    : bắt buộc thuộc một trong các vai trò cho trước
"""

from fastapi import Depends, Request

from co_so_du_lieu import csdl
from hang_so import BANG_NGUOI_DUNG, TRANG_THAI_DA_KHOA
from ngoai_le import ChuaDangNhap, KhongCoQuyen

KHOA_PHIEN_NGUOI_DUNG = "định_danh_người_dùng"


def ghi_phien(request: Request, nguoi_dung: dict) -> None:
    request.session[KHOA_PHIEN_NGUOI_DUNG] = nguoi_dung.get("id") or nguoi_dung.get("định_danh")


def xoa_phien(request: Request) -> None:
    request.session.clear()


def lay_nguoi_dung_hien_tai(request: Request) -> dict:
    dinh_danh = request.session.get(KHOA_PHIEN_NGUOI_DUNG)
    if not dinh_danh:
        raise ChuaDangNhap("Bạn chưa đăng nhập.")

    nguoi_dung = csdl.lay_ban_ghi(BANG_NGUOI_DUNG, dinh_danh)
    if not nguoi_dung:
        xoa_phien(request)
        raise ChuaDangNhap("Tài khoản không còn tồn tại trên hệ thống.")
    if nguoi_dung.get("trạng_thái") == TRANG_THAI_DA_KHOA:
        xoa_phien(request)
        raise ChuaDangNhap("Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Quản trị viên!")
    return nguoi_dung


def yeu_cau_vai_tro(*cac_vai_tro: str):
    def kiem_tra(nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai)) -> dict:
        if nguoi_dung.get("vai_trò") not in cac_vai_tro:
            raise KhongCoQuyen()
        return nguoi_dung

    return kiem_tra
