"""
TUYẾN ĐƯỜNG MÔN HỌC & CÀI ĐẶT HẠN NHẬP ĐIỂM.
"""

from fastapi import APIRouter, Depends

from hang_so import VAI_TRO_QUAN_TRI
from mo_hinh import YeuCauHanNhapDiem, YeuCauTaoMonHoc
from phan_quyen import lay_nguoi_dung_hien_tai, yeu_cau_vai_tro
from services.mon_hoc import (
    cap_nhat_han_nhap_diem,
    danh_sach_mon_hoc,
    tao_mon_hoc,
    trang_thai_cong_diem,
    xoa_mon_hoc,
)

bo_dinh_tuyen = APIRouter(prefix="/api/mon-hoc", tags=["Môn học"])


@bo_dinh_tuyen.get("")
def lay_danh_sach(_: dict = Depends(lay_nguoi_dung_hien_tai)):
    """Lấy danh sách tất cả các môn học kèm thông tin tín chỉ và học phí."""
    return {"thành_công": True, "danh_sách": danh_sach_mon_hoc()}


@bo_dinh_tuyen.post("")
def them_mon_hoc(
    du_lieu: YeuCauTaoMonHoc,
    _: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    """Quản trị viên thêm môn học mới."""
    mon_moi = tao_mon_hoc(du_lieu.model_dump())
    return {
        "thành_công": True,
        "thông_báo": f"Đã thêm môn học: {mon_moi.get('tên_môn')} ({mon_moi.get('mã_môn')})!",
        "môn_học": mon_moi,
    }


@bo_dinh_tuyen.delete("/{dinh_danh}")
def xoa_mon(
    dinh_danh: str,
    _: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    """Quản trị viên xóa môn học."""
    xoa_mon_hoc(dinh_danh)
    return {"thành_công": True, "thông_báo": "Đã xóa môn học thành công!"}


@bo_dinh_tuyen.put("/{dinh_danh}/han-nhap-diem")
def cai_dat_han_diem(
    dinh_danh: str,
    du_lieu: YeuCauHanNhapDiem,
    _: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    """Quản trị viên cấu hình thời hạn mở/đóng sổ điểm cho từng môn học."""
    mon = cap_nhat_han_nhap_diem(dinh_danh, du_lieu.model_dump())
    return {
        "thành_công": True,
        "thông_báo": f"Đã cập nhật thời hạn nhập điểm cho môn {mon.get('mã_môn')}!",
        "môn_học": mon,
    }
