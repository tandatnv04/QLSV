"""
TUYẾN ĐƯỜNG HỒ SƠ: Xem/sửa thông tin cá nhân và cập nhật ảnh đại diện.
"""

from fastapi import APIRouter, Depends

from mo_hinh import YeuCauAnhDaiDien, YeuCauCapNhatHoSo
from phan_quyen import lay_nguoi_dung_hien_tai
from services.nguoi_dung import an_mat_khau, cap_nhat_anh_dai_dien, cap_nhat_ho_so, the_nguoi_dung

bo_dinh_tuyen = APIRouter(prefix="/api/ho-so", tags=["Hồ sơ cá nhân"])


@bo_dinh_tuyen.get("")
def xem_ho_so(nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai)):
    return {"thành_công": True, "hồ_sơ": an_mat_khau(nguoi_dung)}


@bo_dinh_tuyen.put("")
def cap_nhat_thong_tin(du_lieu: YeuCauCapNhatHoSo, nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai)):
    ho_so_moi = cap_nhat_ho_so(nguoi_dung, du_lieu.model_dump())
    return {
        "thành_công": True,
        "thông_báo": "Đã lưu thông tin hồ sơ thành công!",
        "hồ_sơ": ho_so_moi,
    }


@bo_dinh_tuyen.post("/anh-dai-dien")
def cap_nhat_anh(du_lieu: YeuCauAnhDaiDien, nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai)):
    ho_so_moi = cap_nhat_anh_dai_dien(nguoi_dung, du_lieu.ảnh_đại_diện)
    return {
        "thành_công": True,
        "thông_báo": "Đã cập nhật ảnh đại diện thành công!",
        "hồ_sơ": ho_so_moi,
    }


@bo_dinh_tuyen.delete("/anh-dai-dien")
def xoa_anh(nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai)):
    ho_so_moi = cap_nhat_anh_dai_dien(nguoi_dung, None)
    return {
        "thành_công": True,
        "thông_báo": "Đã chuyển về ảnh đại diện mặc định.",
        "hồ_sơ": ho_so_moi,
    }


@bo_dinh_tuyen.get("/the-thong-tin/{dinh_danh_nd}")
def xem_the_nguoi_dung(dinh_danh_nd: str, _: dict = Depends(lay_nguoi_dung_hien_tai)):
    return {"thành_công": True, "thẻ": the_nguoi_dung(dinh_danh_nd)}
