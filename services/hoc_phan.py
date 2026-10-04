"""
ĐĂNG KÝ HỌC PHẦN & QUẢN LÝ HỌC PHÍ CHO SINH VIÊN.
"""

from co_so_du_lieu import csdl, tao_dinh_danh, tao_id
from hang_so import BANG_DANG_KY, BANG_MON_HOC
from ngoai_le import KhongTimThay, LoiNghiepVu
from services.mon_hoc import bang_tra_mon_hoc, lay_mon_hoc


def danh_sach_dang_ky_hoc_phan(dinh_danh_sv: str) -> list[dict]:
    """Danh sách các môn học mở cùng trạng thái đăng ký của sinh viên hiện tại."""
    cac_mon = csdl.lay_danh_sach(BANG_MON_HOC)
    mon_da_dang_ky = {
        dk.get("định_danh_môn")
        for dk in csdl.lay_danh_sach(BANG_DANG_KY)
        if dk.get("định_danh_sinh_viên") == dinh_danh_sv
    }

    ket_qua = []
    for mh in cac_mon:
        ket_qua.append({
            "id": mh.get("id") or mh.get("định_danh"),
            "định_danh": mh.get("id") or mh.get("định_danh"),
            "mã_môn": mh.get("mã_môn"),
            "tên_môn": mh.get("tên_môn"),
            "số_tín_chỉ": mh.get("số_tín_chỉ", 3),
            "đơn_giá_tín_chỉ": mh.get("đơn_giá_tín_chỉ", 450000),
            "khoa": mh.get("khoa", "Công nghệ thông tin"),
            "học_kỳ": mh.get("học_kỳ", "Học kỳ 1 - 2026"),
            "mô_tả": mh.get("mô_tả", ""),
            "đã_đăng_ký": mh["định_danh"] in mon_da_dang_ky,
        })
    ket_qua.sort(key=lambda m: m["mã_môn"] or "")
    return ket_qua


def dang_ky_mon(dinh_danh_sv: str, dinh_danh_mon: str) -> dict:
    """Sinh viên đăng ký môn học."""
    mon_hoc = lay_mon_hoc(dinh_danh_mon)
    tat_ca_dk = csdl.lay_danh_sach(BANG_DANG_KY)

    da_dang_ky = any(
        dk.get("định_danh_sinh_viên") == dinh_danh_sv and dk.get("định_danh_môn") == dinh_danh_mon
        for dk in tat_ca_dk
    )
    if da_dang_ky:
        raise LoiNghiepVu("Bạn đã đăng ký học phần này rồi!")

    ma_dk = tao_id("dk")
    ban_ghi = {
        "id": ma_dk,
        "id_sinh_viên": dinh_danh_sv,
        "id_môn": dinh_danh_mon,
        "định_danh": ma_dk,
        "định_danh_sinh_viên": dinh_danh_sv,
        "định_danh_môn": dinh_danh_mon,
        "điểm_giữa_kỳ": 0.0,
        "điểm_cuối_kỳ": 0.0,
        "điểm_chuyên_cần": 10.0,
        "nhận_xét": "Mới đăng ký học phần",
        "đã_đóng_học_phí": False,
    }
    csdl.luu_ban_ghi(BANG_DANG_KY, ban_ghi)
    return ban_ghi


def huy_dang_ky_mon(dinh_danh_sv: str, dinh_danh_mon: str) -> None:
    """Sinh viên hủy đăng ký môn học."""
    tat_ca_dk = csdl.lay_danh_sach(BANG_DANG_KY)
    dk_can_xoa = next(
        (
            dk for dk in tat_ca_dk
            if dk.get("định_danh_sinh_viên") == dinh_danh_sv and dk.get("định_danh_môn") == dinh_danh_mon
        ),
        None,
    )
    if not dk_can_xoa:
        raise KhongTimThay("Không tìm thấy thông tin đăng ký học phần này.")

    csdl.xoa_ban_ghi(BANG_DANG_KY, dk_can_xoa["định_danh"])


def tra_cuu_hoc_phi(dinh_danh_sv: str) -> dict:
    """Tra cứu danh sách môn đã đăng ký và hóa đơn học phí của sinh viên."""
    cac_mon = bang_tra_mon_hoc()
    cac_dk = [
        dk for dk in csdl.lay_danh_sach(BANG_DANG_KY)
        if dk.get("định_danh_sinh_viên") == dinh_danh_sv
    ]

    danh_sach = []
    tong_tin_chi = 0
    tong_tien = 0
    tat_ca_da_dong = len(cac_dk) > 0

    for dk in cac_dk:
        mon = cac_mon.get(dk.get("định_danh_môn"))
        so_tc = mon.get("số_tín_chỉ", 3) if mon else 3
        don_gia = mon.get("đơn_giá_tín_chỉ", 450000) if mon else 450000
        thanh_tien = so_tc * don_gia
        da_dong = bool(dk.get("đã_đóng_học_phí"))

        tong_tin_chi += so_tc
        tong_tien += thanh_tien
        if not da_dong:
            tat_ca_da_dong = False

        danh_sach.append({
            "định_danh_đăng_ký": dk.get("định_danh"),
            "định_danh_môn": dk.get("định_danh_môn"),
            "mã_môn": mon.get("mã_môn", "-") if mon else "-",
            "tên_môn": mon.get("tên_môn", "Môn học đã bị xóa") if mon else "Môn học đã bị xóa",
            "số_tín_chỉ": so_tc,
            "đơn_giá_tín_chỉ": don_gia,
            "thành_tiền": thanh_tien,
            "đã_đóng_học_phí": da_dong,
        })

    return {
        "danh_sách": danh_sach,
        "tổng_tín_chỉ": tong_tin_chi,
        "tổng_tiền": tong_tien,
        "tất_cả_đã_đóng": tat_ca_da_dong,
    }


def nop_hoc_phi_truc_tuyen(dinh_danh_sv: str) -> dict:
    """Mô phỏng thanh toán học phí trực tuyến cho toàn bộ học phần còn nợ."""
    cac_dk = [
        dk for dk in csdl.lay_danh_sach(BANG_DANG_KY)
        if dk.get("định_danh_sinh_viên") == dinh_danh_sv
    ]
    if not cac_dk:
        raise LoiNghiepVu("Bạn chưa đăng ký môn học nào để nộp học phí!")

    for dk in cac_dk:
        if not dk.get("đã_đóng_học_phí"):
            csdl.cap_nhat_ban_ghi(BANG_DANG_KY, dk["định_danh"], {"đã_đóng_học_phí": True})

    return {"thông_báo": "Thanh toán học phí trực tuyến thành công!", "số_học_phần": len(cac_dk)}
