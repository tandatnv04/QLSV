"""
TUYẾN ĐƯỜNG ĐĂNG KÝ HỌC PHẦN & HỌC PHÍ (Dành cho Sinh viên).
"""

from fastapi import APIRouter, Depends

from hang_so import VAI_TRO_SINH_VIEN
from phan_quyen import yeu_cau_vai_tro
from services.hoc_phan import (
    dang_ky_mon,
    danh_sach_dang_ky_hoc_phan,
    huy_dang_ky_mon,
    nop_hoc_phi_truc_tuyen,
    tra_cuu_hoc_phi,
)

bo_dinh_tuyen = APIRouter(prefix="/api/hoc-phan", tags=["Đăng ký học phần & Học phí"])


@bo_dinh_tuyen.get("/danh-sach-mo")
def lay_danh_sach_mon_mo(nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_SINH_VIEN))):
    """Lấy danh sách các học phần mở đăng ký trong kỳ."""
    ket_qua = danh_sach_dang_ky_hoc_phan(nguoi_dung["định_danh"])
    return {"thành_công": True, "danh_sách": ket_qua}


@bo_dinh_tuyen.post("/dang-ky/{dinh_danh_mon}")
def dang_ky(dinh_danh_mon: str, nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_SINH_VIEN))):
    """Sinh viên đăng ký môn học."""
    ban_ghi = dang_ky_mon(nguoi_dung["định_danh"], dinh_danh_mon)
    return {
        "thành_công": True,
        "thông_báo": "Đăng ký học phần thành công!",
        "bản_ghi": ban_ghi,
    }


@bo_dinh_tuyen.delete("/huy-dang-ky/{dinh_danh_mon}")
def huy_dang_ky(dinh_danh_mon: str, nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_SINH_VIEN))):
    """Sinh viên hủy đăng ký môn học."""
    huy_dang_ky_mon(nguoi_dung["định_danh"], dinh_danh_mon)
    return {"thành_công": True, "thông_báo": "Đã hủy đăng ký học phần thành công."}


@bo_dinh_tuyen.get("/hoc-phi")
def xem_hoc_phi(nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_SINH_VIEN))):
    """Tra cứu bảng kê học phí các môn đã đăng ký."""
    ket_qua = tra_cuu_hoc_phi(nguoi_dung["định_danh"])
    return {"thành_công": True, **ket_qua}


@bo_dinh_tuyen.post("/hoc-phi/thanh-toan")
def thanh_toan_hoc_phi(nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_SINH_VIEN))):
    """Mô phỏng thanh toán học phí trực tuyến."""
    ket_qua = nop_hoc_phi_truc_tuyen(nguoi_dung["định_danh"])
    return {"thành_công": True, **ket_qua}
