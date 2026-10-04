"""
TUYẾN ĐƯỜNG QUẢN LÝ NGƯỜI DÙNG & PHÂN QUYỀN (Admin & tra cứu giảng viên/sinh viên).
"""

from fastapi import APIRouter, Depends, Query

from hang_so import VAI_TRO_GIANG_VIEN, VAI_TRO_QUAN_TRI
from mo_hinh import YeuCauCapNhatNguoiDung, YeuCauTaoNguoiDung
from phan_quyen import lay_nguoi_dung_hien_tai, yeu_cau_vai_tro
from services.nguoi_dung import (
    cap_nhat_nguoi_dung,
    danh_sach_giang_vien,
    danh_sach_nguoi_dung,
    danh_sach_sinh_vien,
    doi_trang_thai_khoa,
    tao_nguoi_dung,
    xoa_nguoi_dung,
)

bo_dinh_tuyen = APIRouter(prefix="/api/nguoi-dung", tags=["Người dùng & Phân quyền"])


@bo_dinh_tuyen.get("/sinh-vien")
def xem_danh_sach_sinh_vien(
    tu_khoa: str = Query(default="", alias="tu_khoa"),
    _: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI, VAI_TRO_GIANG_VIEN)),
):
    """Tra cứu danh sách sinh viên dành cho Giảng viên & Quản trị viên."""
    return {"thành_công": True, "danh_sách": danh_sach_sinh_vien(tu_khoa)}


@bo_dinh_tuyen.get("/giang-vien")
def xem_danh_sach_giang_vien(_: dict = Depends(lay_nguoi_dung_hien_tai)):
    """Danh sách giảng viên để phục vụ dropdown chọn khi xếp lịch dạy."""
    return {"thành_công": True, "danh_sách": danh_sach_giang_vien()}


@bo_dinh_tuyen.get("")
def xem_tat_ca_nguoi_dung(
    vai_tro: str | None = Query(default=None),
    tu_khoa: str = Query(default=""),
    _: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    """Quản trị viên xem và lọc toàn bộ tài khoản người dùng trong hệ thống."""
    return {"thành_công": True, "danh_sách": danh_sach_nguoi_dung(vai_tro, tu_khoa)}


@bo_dinh_tuyen.post("")
def them_nguoi_dung_moi(
    du_lieu: YeuCauTaoNguoiDung,
    _: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    nguoi_dung_moi = tao_nguoi_dung(du_lieu.model_dump())
    return {
        "thành_công": True,
        "thông_báo": f"Đã tạo tài khoản cho {nguoi_dung_moi.get('họ_tên')} ({nguoi_dung_moi.get('vai_trò')}) thành công!",
        "người_dùng": nguoi_dung_moi,
    }


@bo_dinh_tuyen.put("/{dinh_danh}")
def cap_nhat_tai_khoan(
    dinh_danh: str,
    du_lieu: YeuCauCapNhatNguoiDung,
    nguoi_thuc_hien: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    cap_nhat = cap_nhat_nguoi_dung(dinh_danh, du_lieu.model_dump(), nguoi_thuc_hien)
    return {
        "thành_công": True,
        "thông_báo": f"Đã cập nhật thông tin & quyền cho {cap_nhat.get('họ_tên')}!",
        "người_dùng": cap_nhat,
    }


@bo_dinh_tuyen.patch("/{dinh_danh}/khoa")
def doi_khoa_tai_khoan(
    dinh_danh: str,
    nguoi_thuc_hien: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    nd = doi_trang_thai_khoa(dinh_danh, nguoi_thuc_hien)
    thong_bao = (
        f"Đã mở khóa tài khoản @{nd.get('tên_đăng_nhập')}."
        if nd.get("trạng_thái") == "Hoạt động"
        else f"Đã tạm khóa tài khoản @{nd.get('tên_đăng_nhập')}."
    )
    return {"thành_công": True, "thông_báo": thong_bao, "người_dùng": nd}


@bo_dinh_tuyen.delete("/{dinh_danh}")
def xoa_tai_khoan(
    dinh_danh: str,
    nguoi_thuc_hien: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    xoa_nguoi_dung(dinh_danh, nguoi_thuc_hien)
    return {"thành_công": True, "thông_báo": "Đã xóa tài khoản khỏi hệ thống!"}
