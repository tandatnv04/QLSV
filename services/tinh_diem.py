"""
TÍNH ĐIỂM & XẾP LOẠI HỌC LỰC

Quy tắc:
  - Điểm tổng kết (hệ 10) = Giữa kỳ x 40% + Cuối kỳ x 60%, làm tròn 1 chữ số thập phân.
  - Quy đổi điểm chữ và hệ 4 theo thang chuẩn tín chỉ.
  - GPA = trung bình có trọng số theo số tín chỉ.
"""

from decimal import ROUND_HALF_UP, Decimal

from hang_so import SO_TIN_CHI_MAC_DINH, TRONG_SO_CUOI_KY, TRONG_SO_GIUA_KY

# (ngưỡng điểm hệ 10, điểm chữ, điểm hệ 4)
BANG_QUY_DOI = (
    (8.5, "A", 4.0),
    (8.0, "B+", 3.5),
    (7.0, "B", 3.0),
    (6.5, "C+", 2.5),
    (5.5, "C", 2.0),
    (5.0, "D+", 1.5),
    (4.0, "D", 1.0),
    (0.0, "F", 0.0),
)


def lam_tron(gia_tri: float, so_chu_so: int = 1) -> float:
    """Làm tròn nửa lên (5 -> lên) để tránh sai số dấu phẩy động."""
    mau = Decimal(1).scaleb(-so_chu_so)
    return float(Decimal(str(gia_tri)).quantize(mau, rounding=ROUND_HALF_UP))


def tinh_diem_tong_ket(diem_giua_ky: float | None, diem_cuoi_ky: float | None) -> float | None:
    if diem_giua_ky is None or diem_cuoi_ky is None:
        return None
    return lam_tron(float(diem_giua_ky) * TRONG_SO_GIUA_KY + float(diem_cuoi_ky) * TRONG_SO_CUOI_KY)


def _tra_bang(diem_he_10: float) -> tuple[float, str, float]:
    for nguong, diem_chu, he_4 in BANG_QUY_DOI:
        if diem_he_10 >= nguong:
            return nguong, diem_chu, he_4
    return BANG_QUY_DOI[-1]


def quy_doi_diem_chu(diem_he_10: float | None) -> str:
    return "-" if diem_he_10 is None else _tra_bang(diem_he_10)[1]


def quy_doi_he_4(diem_he_10: float | None) -> float:
    return 0.0 if diem_he_10 is None else _tra_bang(diem_he_10)[2]


def xep_loai_hoc_luc(diem_he_10: float) -> dict:
    """
    Trả về xếp loại và "mức" (tốt / khá / yếu) để giao diện chọn màu hiển thị.
    """
    if diem_he_10 >= 9.0:
        return {"xếp_loại": "Xuất sắc", "mức": "tốt"}
    if diem_he_10 >= 8.0:
        return {"xếp_loại": "Giỏi", "mức": "tốt"}
    if diem_he_10 >= 6.5:
        return {"xếp_loại": "Khá", "mức": "khá"}
    if diem_he_10 >= 5.0:
        return {"xếp_loại": "Trung bình", "mức": "yếu"}
    return {"xếp_loại": "Yếu / Cảnh báo học vụ", "mức": "yếu"}


def muc_diem_mon(diem_he_10: float | None) -> str:
    """Mức hiển thị cho điểm một môn: >= 8 tốt, >= 6.5 khá, còn lại yếu."""
    if diem_he_10 is None:
        return "khá"
    if diem_he_10 >= 8.0:
        return "tốt"
    if diem_he_10 >= 6.5:
        return "khá"
    return "yếu"


def ket_qua_mot_mon(dang_ky: dict, mon_hoc: dict | None) -> dict:
    """Ghép bản ghi đăng ký với môn học và tính toàn bộ chỉ số điểm của môn."""
    mon_hoc = mon_hoc or {}
    giua_ky = dang_ky.get("điểm_giữa_kỳ")
    cuoi_ky = dang_ky.get("điểm_cuối_kỳ")
    tong_ket = tinh_diem_tong_ket(giua_ky, cuoi_ky)
    return {
        "id": dang_ky.get("id") or dang_ky.get("định_danh"),
        "định_danh": dang_ky.get("id") or dang_ky.get("định_danh"),
        "id_môn": dang_ky.get("id_môn") or dang_ky.get("định_danh_môn"),
        "định_danh_môn": dang_ky.get("id_môn") or dang_ky.get("định_danh_môn"),
        "mã_môn": mon_hoc.get("mã_môn", "-"),
        "tên_môn": mon_hoc.get("tên_môn", "Môn học đã bị xóa"),
        "khoa": mon_hoc.get("khoa", ""),
        "học_kỳ": mon_hoc.get("học_kỳ", ""),
        "số_tín_chỉ": int(mon_hoc.get("số_tín_chỉ") or SO_TIN_CHI_MAC_DINH),
        "điểm_giữa_kỳ": giua_ky,
        "điểm_cuối_kỳ": cuoi_ky,
        "điểm_tổng_kết": tong_ket,
        "điểm_chữ": quy_doi_diem_chu(tong_ket),
        "điểm_hệ_4": quy_doi_he_4(tong_ket),
        "mức": muc_diem_mon(tong_ket),
        "nhận_xét": dang_ky.get("nhận_xét", ""),
        "đã_đóng_học_phí": bool(dang_ky.get("đã_đóng_học_phí")),
    }


def tinh_gpa(danh_sach_ket_qua: list[dict]) -> dict:
    """Tính GPA hệ 10, hệ 4 (quy đổi từng môn) và tổng tín chỉ."""
    tong_tin_chi = 0
    tong_he_10 = 0.0
    tong_he_4 = 0.0
    for ket_qua in danh_sach_ket_qua:
        if ket_qua["điểm_tổng_kết"] is None:
            continue
        tin_chi = ket_qua["số_tín_chỉ"]
        tong_tin_chi += tin_chi
        tong_he_10 += ket_qua["điểm_tổng_kết"] * tin_chi
        tong_he_4 += ket_qua["điểm_hệ_4"] * tin_chi

    gpa_he_10 = lam_tron(tong_he_10 / tong_tin_chi, 2) if tong_tin_chi else 0.0
    gpa_he_4 = lam_tron(tong_he_4 / tong_tin_chi, 2) if tong_tin_chi else 0.0
    return {
        "gpa_hệ_10": gpa_he_10,
        "gpa_hệ_4": gpa_he_4,
        "tổng_tín_chỉ": tong_tin_chi,
        **xep_loai_hoc_luc(gpa_he_10),
    }
