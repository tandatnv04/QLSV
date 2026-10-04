"""
ĐIỂM DANH CHUYÊN CẦN.
"""

from datetime import date

from co_so_du_lieu import csdl, tao_dinh_danh
from hang_so import (
    BANG_DANG_KY,
    BANG_DIEM_DANH,
    BANG_NGUOI_DUNG,
    DANH_SACH_TRANG_THAI_DIEM_DANH,
    DIEM_DANH_CO_MAT,
    VAI_TRO_GIANG_VIEN,
)
from ngoai_le import KhongCoQuyen, LoiNghiepVu
from services.lich_hoc import lay_lich_hoc


def _kiem_tra_quyen_lich(lich: dict, nguoi_dung: dict) -> None:
    if nguoi_dung.get("vai_trò") == VAI_TRO_GIANG_VIEN and lich.get("định_danh_giảng_viên") != nguoi_dung["định_danh"]:
        raise KhongCoQuyen("Bạn chỉ được điểm danh lớp học phần do mình phụ trách!")


def _sinh_vien_cua_mon(dinh_danh_mon: str) -> list[dict]:
    cac_sinh_vien = {
        dk.get("định_danh_sinh_viên")
        for dk in csdl.lay_danh_sach(BANG_DANG_KY)
        if dk.get("định_danh_môn") == dinh_danh_mon
    }
    ket_qua = [nd for nd in csdl.lay_danh_sach(BANG_NGUOI_DUNG) if nd.get("định_danh") in cac_sinh_vien]
    ket_qua.sort(key=lambda nd: nd.get("mã_số") or "")
    return ket_qua


def _tim_buoi_diem_danh(dinh_danh_lich: str, ngay: str) -> dict | None:
    return next(
        (
            dd
            for dd in csdl.lay_danh_sach(BANG_DIEM_DANH)
            if dd.get("định_danh_lịch_học") == dinh_danh_lich and dd.get("ngày") == ngay
        ),
        None,
    )


def danh_sach_diem_danh(dinh_danh_lich: str, ngay: date, nguoi_dung: dict) -> dict:
    """Danh sách sinh viên của lớp học phần, kèm kết quả đã điểm danh (nếu có) của ngày được chọn."""
    lich = lay_lich_hoc(dinh_danh_lich)
    _kiem_tra_quyen_lich(lich, nguoi_dung)

    buoi = _tim_buoi_diem_danh(dinh_danh_lich, ngay.isoformat())
    da_ghi = {bg.get("định_danh_sinh_viên"): bg for bg in (buoi or {}).get("danh_sách", []) if bg}

    danh_sach = []
    for sv in _sinh_vien_cua_mon(lich.get("định_danh_môn")):
        ban_ghi = da_ghi.get(sv["định_danh"], {})
        danh_sach.append(
            {
                "định_danh": sv["định_danh"],
                "mã_số": sv.get("mã_số"),
                "họ_tên": sv.get("họ_tên"),
                "ảnh_đại_diện": sv.get("ảnh_đại_diện"),
                "trạng_thái": ban_ghi.get("trạng_thái", DIEM_DANH_CO_MAT),
                "ghi_chú": ban_ghi.get("ghi_chú", ""),
            }
        )

    return {
        "lịch_học": lich,
        "đã_điểm_danh": buoi is not None,
        "các_trạng_thái": list(DANH_SACH_TRANG_THAI_DIEM_DANH),
        "danh_sách": danh_sach,
    }


def luu_diem_danh(du_lieu: dict, nguoi_dung: dict) -> dict:
    lich = lay_lich_hoc(du_lieu["định_danh_lịch_học"])
    _kiem_tra_quyen_lich(lich, nguoi_dung)

    sinh_vien_hop_le = {sv["định_danh"] for sv in _sinh_vien_cua_mon(lich.get("định_danh_môn"))}
    danh_sach = []
    for ban_ghi in du_lieu["danh_sách"]:
        if ban_ghi["trạng_thái"] not in DANH_SACH_TRANG_THAI_DIEM_DANH:
            raise LoiNghiepVu(f"Trạng thái điểm danh '{ban_ghi['trạng_thái']}' không hợp lệ.")
        if ban_ghi["định_danh_sinh_viên"] not in sinh_vien_hop_le:
            raise LoiNghiepVu("Có sinh viên không thuộc lớp học phần này.")
        danh_sach.append(
            {
                "định_danh_sinh_viên": ban_ghi["định_danh_sinh_viên"],
                "trạng_thái": ban_ghi["trạng_thái"],
                "ghi_chú": ban_ghi.get("ghi_chú", "").strip(),
            }
        )
    if not danh_sach:
        raise LoiNghiepVu("Lớp học phần chưa có sinh viên nào để điểm danh.")

    ngay = du_lieu["ngày"].isoformat()
    buoi_cu = _tim_buoi_diem_danh(lich["định_danh"], ngay)
    buoi = {
        "định_danh": buoi_cu["định_danh"] if buoi_cu else tao_dinh_danh("dd"),
        "định_danh_lịch_học": lich["định_danh"],
        "ngày": ngay,
        "danh_sách": danh_sach,
    }
    csdl.luu_ban_ghi(BANG_DIEM_DANH, buoi)
    return {"buổi_điểm_danh": buoi, "cập_nhật_lại": buoi_cu is not None}
