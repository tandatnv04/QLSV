"""
QUẢN LÝ ĐIỂM SỐ, SỔ ĐIỂM & BẢNG ĐIỂM CHI TIẾT (TRANSCRIPT).
"""

import csv
import io

from co_so_du_lieu import csdl, tao_dinh_danh
from hang_so import (
    BANG_DANG_KY,
    BANG_MON_HOC,
    BANG_NGUOI_DUNG,
    VAI_TRO_GIANG_VIEN,
    VAI_TRO_QUAN_TRI,
    VAI_TRO_SINH_VIEN,
)
from ngoai_le import KhongCoQuyen, KhongTimThay, LoiNghiepVu
from services.mon_hoc import bang_tra_mon_hoc, lay_mon_hoc, trang_thai_cong_diem
from services.tinh_diem import (
    ket_qua_mot_mon,
    lam_tron,
    quy_doi_diem_chu,
    quy_doi_he_4,
    tinh_diem_tong_ket,
    tinh_gpa,
)


def lay_so_diem_mon_hoc(dinh_danh_mon: str, nguoi_dung: dict) -> dict:
    """
    Lấy sổ điểm môn học cho giảng viên và quản trị viên.
    Trả về thông tin môn học, trạng thái hạn mở/khóa sổ điểm, và danh sách điểm sinh viên.
    """
    mon_hoc = lay_mon_hoc(dinh_danh_mon)
    cong_diem = trang_thai_cong_diem(mon_hoc, nguoi_dung)

    # Đọc danh sách sinh viên
    sinh_vien_dict = {
        nd["định_danh"]: nd
        for nd in csdl.lay_danh_sach(BANG_NGUOI_DUNG)
        if nd.get("vai_trò") == VAI_TRO_SINH_VIEN
    }

    # Đọc danh sách đăng ký môn này
    dang_ky_list = [
        dk for dk in csdl.lay_danh_sach(BANG_DANG_KY)
        if dk.get("định_danh_môn") == dinh_danh_mon
    ]
    dang_ky_dict = {dk.get("định_danh_sinh_viên"): dk for dk in dang_ky_list}

    danh_sach = []
    for sv_id, sv in sinh_vien_dict.items():
        dk = dang_ky_dict.get(sv_id)
        giua_ky = dk.get("điểm_giữa_kỳ") if dk else 8.0
        cuoi_ky = dk.get("điểm_cuối_kỳ") if dk else 8.5
        tong_ket = tinh_diem_tong_ket(giua_ky, cuoi_ky)

        danh_sach.append({
            "định_danh_sinh_viên": sv_id,
            "mã_số": sv.get("mã_số", "SV-000"),
            "họ_tên": sv.get("họ_tên", ""),
            "ảnh_đại_diện": sv.get("ảnh_đại_diện"),
            "điểm_giữa_kỳ": giua_ky,
            "điểm_cuối_kỳ": cuoi_ky,
            "điểm_tổng_kết": tong_ket,
            "điểm_chữ": quy_doi_diem_chu(tong_ket),
            "điểm_hệ_4": quy_doi_he_4(tong_ket),
            "nhận_xét": dk.get("nhận_xét", "") if dk else "",
            "đã_đăng_ký": dk is not None,
        })

    danh_sach.sort(key=lambda item: item["mã_số"])
    return {
        "môn_học": mon_hoc,
        "cổng_điểm": cong_diem,
        "danh_sách": danh_sach,
    }


def luu_diem_sinh_vien(dinh_danh_mon: str, dinh_danh_sv: str, du_lieu: dict, nguoi_dung: dict) -> dict:
    """Lưu điểm giữa kỳ, cuối kỳ và nhận xét cho một sinh viên."""
    mon_hoc = lay_mon_hoc(dinh_danh_mon)
    cong_diem = trang_thai_cong_diem(mon_hoc, nguoi_dung)
    if not cong_diem["được_phép_sửa"]:
        raise KhongCoQuyen(f"Không thể sửa điểm: {cong_diem['lý_do_khóa']}")

    giua_ky = float(du_lieu["điểm_giữa_kỳ"])
    cuoi_ky = float(du_lieu["điểm_cuối_kỳ"])
    if not (0.0 <= giua_ky <= 10.0 and 0.0 <= cuoi_ky <= 10.0):
        raise LoiNghiepVu("Điểm số phải nằm trong khoảng từ 0.0 đến 10.0!")

    nhan_xet = du_lieu.get("nhận_xét", "").strip()

    # Tìm đăng ký học phần tương ứng
    tat_ca_dk = csdl.lay_danh_sach(BANG_DANG_KY)
    dk_hien_tai = next(
        (dk for dk in tat_ca_dk if dk.get("định_danh_môn") == dinh_danh_mon and dk.get("định_danh_sinh_viên") == dinh_danh_sv),
        None,
    )

    tong_ket = tinh_diem_tong_ket(giua_ky, cuoi_ky)
    diem_chu = quy_doi_diem_chu(tong_ket)
    he_4 = quy_doi_he_4(tong_ket)

    if dk_hien_tai:
        thay_doi = {
            "điểm_giữa_kỳ": giua_ky,
            "điểm_cuối_kỳ": cuoi_ky,
            "nhận_xét": nhan_xet,
        }
        csdl.cap_nhat_ban_ghi(BANG_DANG_KY, dk_hien_tai["định_danh"], thay_doi)
    else:
        ban_ghi_moi = {
            "định_danh": tao_dinh_danh("dk"),
            "định_danh_sinh_viên": dinh_danh_sv,
            "định_danh_môn": dinh_danh_mon,
            "điểm_giữa_kỳ": giua_ky,
            "điểm_cuối_kỳ": cuoi_ky,
            "điểm_chuyên_cần": 10.0,
            "nhận_xét": nhan_xet,
            "đã_đóng_học_phí": True,
        }
        csdl.luu_ban_ghi(BANG_DANG_KY, ban_ghi_moi)

    return {
        "điểm_giữa_kỳ": giua_ky,
        "điểm_cuối_kỳ": cuoi_ky,
        "điểm_tổng_kết": tong_ket,
        "điểm_chữ": diem_chu,
        "điểm_hệ_4": he_4,
        "nhận_xét": nhan_xet,
    }


def xuat_bang_diem_csv(dinh_danh_mon: str, nguoi_dung: dict) -> tuple[str, str]:
    """Xuất bảng điểm ra file CSV UTF-8 kèm BOM để mở tốt trên Excel."""
    du_lieu = lay_so_diem_mon_hoc(dinh_danh_mon, nguoi_dung)
    mon = du_lieu["môn_học"]

    output = io.StringIO()
    # Thêm BOM UTF-8
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow([f"BẢNG ĐIỂM: {mon.get('tên_môn')} ({mon.get('mã_môn')})"])
    writer.writerow(["Mã SV", "Họ và Tên", "Điểm Giữa Kỳ (40%)", "Điểm Cuối Kỳ (60%)", "Điểm Tổng Kết", "Điểm Chữ", "Điểm Hệ 4", "Ghi Chú"])

    for item in du_lieu["danh_sách"]:
        writer.writerow([
            item["mã_số"],
            item["họ_tên"],
            item["điểm_giữa_kỳ"],
            item["điểm_cuối_kỳ"],
            item["điểm_tổng_kết"],
            item["điểm_chữ"],
            item["điểm_hệ_4"],
            item["nhận_xét"],
        ])

    ten_tep = f"BangDiem_{mon.get('mã_môn', 'MonHoc')}.csv"
    return output.getvalue(), ten_tep


def lay_bang_diem_chi_tiet_sinh_vien(dinh_danh_sv: str) -> dict:
    """Tra cứu toàn bộ kết quả học tập, điểm các môn, GPA và học phí của một sinh viên."""
    sinh_vien = csdl.lay_ban_ghi(BANG_NGUOI_DUNG, dinh_danh_sv)
    if not sinh_vien:
        raise KhongTimThay("Không tìm thấy thông tin sinh viên.")

    cac_mon = bang_tra_mon_hoc()
    cac_dk = [
        dk for dk in csdl.lay_danh_sach(BANG_DANG_KY)
        if (dk.get("id_sinh_viên") or dk.get("định_danh_sinh_viên")) == dinh_danh_sv
    ]

    danh_sach_ket_qua = []
    tong_hoc_phi = 0
    hoc_phi_da_dong = 0

    for dk in cac_dk:
        mon = cac_mon.get(dk.get("id_môn") or dk.get("định_danh_môn"))
        kq = ket_qua_mot_mon(dk, mon)
        danh_sach_ket_qua.append(kq)

        don_gia = mon.get("đơn_giá_tín_chỉ", 450000) if mon else 450000
        tien_mon = kq["số_tín_chỉ"] * don_gia
        tong_hoc_phi += tien_mon
        if kq["đã_đóng_học_phí"]:
            hoc_phi_da_dong += tien_mon

    gpa_info = tinh_gpa(danh_sach_ket_qua)

    return {
        "sinh_viên": {
            "id": sinh_vien.get("id") or sinh_vien.get("định_danh"),
            "định_danh": sinh_vien.get("định_danh") or sinh_vien.get("id"),
            "mã_số": sinh_vien.get("mã_số", "SV-N/A"),
            "họ_tên": sinh_vien.get("họ_tên", ""),
            "khoa": sinh_vien.get("khoa", "Công nghệ thông tin"),
            "lớp": sinh_vien.get("lớp") or sinh_vien.get("chức_danh") or "K66",
            "email": sinh_vien.get("email", ""),
            "ảnh_đại_diện": sinh_vien.get("ảnh_đại_diện"),
        },
        "kết_quả_học_tập": danh_sach_ket_qua,
        "tổng_kết": {
            **gpa_info,
            "tổng_học_phí": tong_hoc_phi,
            "học_phí_đã_đóng": hoc_phi_da_dong,
            "đã_hoàn_thành_học_phí": hoc_phi_da_dong >= tong_hoc_phi and tong_hoc_phi > 0,
        }
    }
