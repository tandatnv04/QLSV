"""
THỐNG KÊ TỔNG QUAN HỆ THỐNG (DASHBOARD METRICS).
"""

from co_so_du_lieu import csdl
from hang_so import (
    BANG_LICH_HOC,
    BANG_MON_HOC,
    BANG_NGUOI_DUNG,
    VAI_TRO_GIANG_VIEN,
    VAI_TRO_SINH_VIEN,
)


def lay_thong_ke_tong_quan() -> dict:
    """Thống kê số lượng người dùng, môn học, lịch dạy và cơ cấu phân bố môn học theo khoa."""
    tat_ca_nd = csdl.lay_danh_sach(BANG_NGUOI_DUNG)
    so_giang_vien = sum(1 for nd in tat_ca_nd if nd.get("vai_trò") == VAI_TRO_GIANG_VIEN)
    so_sinh_vien = sum(1 for nd in tat_ca_nd if nd.get("vai_trò") == VAI_TRO_SINH_VIEN)

    tat_ca_mon = csdl.lay_danh_sach(BANG_MON_HOC)
    so_mon_hoc = len(tat_ca_mon)

    tat_ca_lich = csdl.lay_danh_sach(BANG_LICH_HOC)
    so_lich_day = len(tat_ca_lich)

    # Phân bố môn học theo khoa
    phan_bo_khoa = {}
    for mon in tat_ca_mon:
        khoa = mon.get("khoa") or "Chung"
        phan_bo_khoa[khoa] = phan_bo_khoa.get(khoa, 0) + 1

    danh_sach_phan_bo = [
        {"khoa": khoa, "số_lượng": count, "tỷ_lệ": round((count / so_mon_hoc) * 100, 1) if so_mon_hoc else 0}
        for khoa, count in phan_bo_khoa.items()
    ]
    danh_sach_phan_bo.sort(key=lambda x: x["số_lượng"], reverse=True)

    return {
        "số_giảng_viên": so_giang_vien,
        "số_sinh_viên": so_sinh_vien,
        "số_môn_học": so_mon_hoc,
        "số_lịch_dạy": so_lich_day,
        "phân_bố_khoa": danh_sach_phan_bo,
    }
