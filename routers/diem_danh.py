"""
TUYẾN ĐƯỜNG ĐIỂM DANH CHUYÊN CẦN (Dành cho Giảng viên & Quản trị viên).
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from hang_so import VAI_TRO_GIANG_VIEN, VAI_TRO_QUAN_TRI
from mo_hinh import YeuCauLuuDiemDanh
from phan_quyen import yeu_cau_vai_tro
from services.diem_danh import danh_sach_diem_danh, luu_diem_danh

bo_dinh_tuyen = APIRouter(prefix="/api/diem-danh", tags=["Điểm danh"])


@bo_dinh_tuyen.get("")
def lay_danh_sach_diem_danh(
    dinh_danh_lich: str = Query(alias="dinh_danh_lich"),
    ngay: date = Query(alias="ngay"),
    nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI, VAI_TRO_GIANG_VIEN)),
):
    """Lấy danh sách sinh viên và trạng thái điểm danh của buổi học được chọn."""
    ket_qua = danh_sach_diem_danh(dinh_danh_lich, ngay, nguoi_dung)
    return {"thành_công": True, **ket_qua}


@bo_dinh_tuyen.post("")
def ghi_nhan_diem_danh(
    du_lieu: YeuCauLuuDiemDanh,
    nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI, VAI_TRO_GIANG_VIEN)),
):
    """Lưu kết quả điểm danh chuyên cần của buổi học."""
    ket_qua = luu_diem_danh(du_lieu.model_dump(), nguoi_dung)
    ngay_str = du_lieu.ngày.isoformat()
    thong_bao = (
        f"Đã cập nhật lại kết quả điểm danh ngày {ngay_str}!"
        if ket_qua["cập_nhật_lại"]
        else f"Đã lưu kết quả điểm danh ngày {ngay_str} thành công!"
    )
    return {"thành_công": True, "thông_báo": thong_bao, **ket_qua}
