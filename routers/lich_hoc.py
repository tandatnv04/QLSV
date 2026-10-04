"""
TUYẾN ĐƯỜNG THỜI KHÓA BIỂU / LỊCH HỌC & LỊCH DẠY.
"""

from fastapi import APIRouter, Depends, Query

from hang_so import VAI_TRO_QUAN_TRI
from mo_hinh import YeuCauTaoLichHoc
from phan_quyen import lay_nguoi_dung_hien_tai, yeu_cau_vai_tro
from services.lich_hoc import danh_sach_lich_hoc, tao_lich_hoc

bo_dinh_tuyen = APIRouter(prefix="/api/lich-hoc", tags=["Thời khóa biểu"])


@bo_dinh_tuyen.get("")
def xem_thoi_khoa_bieu(
    tuan: int | None = Query(default=None),
    thu: str | None = Query(default=None),
    nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai),
):
    """
    Xem thời khóa biểu theo quyền của người dùng hiện tại (Admin/Giảng viên/Sinh viên),
    hỗ trợ lọc theo tuần học và thứ trong tuần.
    """
    ket_qua = danh_sach_lich_hoc(nguoi_dung, tuan, thu)
    return {"thành_công": True, **ket_qua}


@bo_dinh_tuyen.post("")
def xep_lich_day(
    du_lieu: YeuCauTaoLichHoc,
    _: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI)),
):
    """Quản trị viên xếp lịch giảng dạy mới cho giảng viên và môn học."""
    lich_moi = tao_lich_hoc(du_lieu.model_dump())
    return {
        "thành_công": True,
        "thông_báo": "Đã xếp lịch giảng dạy thành công!",
        "lịch_học": lich_moi,
    }
