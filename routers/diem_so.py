"""
TUYẾN ĐƯỜNG ĐIỂM SỐ, SỔ ĐIỂM & BẢNG ĐIỂM CHI TIẾT (TRANSCRIPT).
"""

from fastapi import APIRouter, Depends, Query, Response

from hang_so import VAI_TRO_GIANG_VIEN, VAI_TRO_QUAN_TRI, VAI_TRO_SINH_VIEN
from mo_hinh import YeuCauLuuDiem, YeuCauTinhDiem
from phan_quyen import lay_nguoi_dung_hien_tai, yeu_cau_vai_tro
from services.diem_so import (
    lay_bang_diem_chi_tiet_sinh_vien,
    lay_so_diem_mon_hoc,
    luu_diem_sinh_vien,
    xuat_bang_diem_csv,
)
from services.tinh_diem import (
    quy_doi_diem_chu,
    quy_doi_he_4,
    tinh_diem_tong_ket,
    xep_loai_hoc_luc,
)

bo_dinh_tuyen = APIRouter(prefix="/api/diem-so", tags=["Điểm số & Bảng điểm"])


@bo_dinh_tuyen.get("/so-diem/{dinh_danh_mon}")
def xem_so_diem(
    dinh_danh_mon: str,
    nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI, VAI_TRO_GIANG_VIEN)),
):
    """Xem sổ điểm của một môn học (dành cho Giảng viên & Quản trị viên)."""
    ket_qua = lay_so_diem_mon_hoc(dinh_danh_mon, nguoi_dung)
    return {"thành_công": True, **ket_qua}


@bo_dinh_tuyen.put("/so-diem/{dinh_danh_mon}/sinh-vien/{dinh_danh_sv}")
def cap_nhat_diem_sinh_vien(
    dinh_danh_mon: str,
    dinh_danh_sv: str,
    du_lieu: YeuCauLuuDiem,
    nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI, VAI_TRO_GIANG_VIEN)),
):
    """Nhập hoặc sửa điểm giữa kỳ, cuối kỳ của sinh viên."""
    ket_qua = luu_diem_sinh_vien(dinh_danh_mon, dinh_danh_sv, du_lieu.model_dump(), nguoi_dung)
    return {
        "thành_công": True,
        "thông_báo": "Đã lưu điểm cho sinh viên thành công!",
        "kết_quả": ket_qua,
    }


@bo_dinh_tuyen.get("/xuat-csv/{dinh_danh_mon}")
def xuat_csv(
    dinh_danh_mon: str,
    nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_QUAN_TRI, VAI_TRO_GIANG_VIEN)),
):
    """Xuất bảng điểm môn học ra file CSV UTF-8 để tải về."""
    noi_dung_csv, ten_tep = xuat_bang_diem_csv(dinh_danh_mon, nguoi_dung)
    return Response(
        content=noi_dung_csv.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{ten_tep}"'},
    )


@bo_dinh_tuyen.get("/bang-diem-sinh-vien/{dinh_danh_sv}")
def xem_bang_diem_sinh_vien(
    dinh_danh_sv: str,
    nguoi_dung: dict = Depends(lay_nguoi_dung_hien_tai),
):
    """
    Xem toàn bộ bảng điểm chi tiết (Transcript), GPA và học phí của một sinh viên.
    Sinh viên chỉ được xem bảng điểm của chính mình; Quản trị viên và Giảng viên được xem của mọi sinh viên.
    """
    if nguoi_dung.get("vai_trò") == VAI_TRO_SINH_VIEN and nguoi_dung["định_danh"] != dinh_danh_sv:
        dinh_danh_sv = nguoi_dung["định_danh"]

    ket_qua = lay_bang_diem_chi_tiet_sinh_vien(dinh_danh_sv)
    return {"thành_công": True, **ket_qua}


@bo_dinh_tuyen.get("/bang-diem-cua-toi")
def xem_bang_diem_cua_toi(
    nguoi_dung: dict = Depends(yeu_cau_vai_tro(VAI_TRO_SINH_VIEN)),
):
    """Sinh viên xem kết quả học tập và GPA cá nhân."""
    ket_qua = lay_bang_diem_chi_tiet_sinh_vien(nguoi_dung["định_danh"])
    return {"thành_công": True, **ket_qua}


@bo_dinh_tuyen.post("/tinh-nhanh")
def tinh_nhanh_diem(du_lieu: YeuCauTinhDiem):
    """Tiện ích tính thử điểm tổng kết, điểm chữ và hệ 4 theo thời gian thực."""
    tong_ket = tinh_diem_tong_ket(du_lieu.điểm_giữa_kỳ, du_lieu.điểm_cuối_kỳ)
    return {
        "điểm_tổng_kết": tong_ket,
        "điểm_chữ": quy_doi_diem_chu(tong_ket),
        "điểm_hệ_4": quy_doi_he_4(tong_ket),
        "xếp_loại": xep_loai_hoc_luc(tong_ket)["xếp_loại"] if tong_ket is not None else "-",
    }
