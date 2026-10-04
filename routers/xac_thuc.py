"""
TUYẾN ĐƯỜNG XÁC THỰC: Đăng nhập, Đăng xuất, Khôi phục mật khẩu, Thông tin phiên hiện tại.
"""

from fastapi import APIRouter, Depends, Request

from mo_hinh import YeuCauDangNhap, YeuCauQuenMatKhau
from phan_quyen import ghi_phien, lay_nguoi_dung_hien_tai, xoa_phien
from services.nguoi_dung import an_mat_khau
from services.xac_thuc import dang_nhap, dat_lai_mat_khau

bo_dinh_tuyen = APIRouter(prefix="/api/xac-thuc", tags=["Xác thực"])


@bo_dinh_tuyen.post("/dang-nhap")
def xu_ly_dang_nhap(du_lieu: YeuCauDangNhap, request: Request):
    nguoi_dung = dang_nhap(du_lieu.tên_đăng_nhập, du_lieu.mật_khẩu)
    ghi_phien(request, nguoi_dung)
    return {
        "thành_công": True,
        "thông_báo": f"Chào mừng {nguoi_dung.get('họ_tên')} trở lại hệ thống!",
        "người_dùng": an_mat_khau(nguoi_dung),
    }


@bo_dinh_tuyen.post("/dang-xuat")
def xu_ly_dang_xuat(request: Request):
    xoa_phien(request)
    return {"thành_công": True, "thông_báo": "Bạn đã đăng xuất khỏi hệ thống."}


@bo_dinh_tuyen.get("/nguoi-dung-hien-tai")
def xu_ly_lay_nguoi_dung_hien_tai(nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai)):
    return {"thành_công": True, "người_dùng": an_mat_khau(nguoi_dung)}


@bo_dinh_tuyen.post("/quen-mat-khau")
def xu_ly_quen_mat_khau(du_lieu: YeuCauQuenMatKhau):
    nguoi_dung = dat_lai_mat_khau(
        du_lieu.thông_tin_tài_khoản,
        du_lieu.mật_khẩu_mới,
        du_lieu.xác_nhận_mật_khẩu,
    )
    return {
        "thành_công": True,
        "thông_báo": f"Đã đặt lại mật khẩu mới cho tài khoản {nguoi_dung.get('họ_tên')} thành công!",
    }
