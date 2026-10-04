"""
TUYẾN ĐƯỜNG THỐNG KÊ DASHBOARD TỔNG QUAN.
"""

from fastapi import APIRouter, Depends

from phan_quyen import lay_nguoi_dung_hien_tai
from services.thong_ke import lay_thong_ke_tong_quan

bo_dinh_tuyen = APIRouter(prefix="/api/thong-ke", tags=["Thống kê"])


@bo_dinh_tuyen.get("/tong-quan")
def thong_ke_tong_quan(_: dict = Depends(lay_nguoi_dung_hien_tai)):
    """Lấy số liệu tổng quan hệ thống và phân bố môn học cho biểu đồ."""
    ket_qua = lay_thong_ke_tong_quan()
    return {"thành_công": True, **ket_qua}
