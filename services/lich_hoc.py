"""
THỜI KHÓA BIỂU / LỊCH HỌC & LỊCH DẠY.
"""

from co_so_du_lieu import csdl, tao_dinh_danh
from hang_so import (
    BANG_DANG_KY,
    BANG_LICH_HOC,
    BANG_NGUOI_DUNG,
    THU_TRONG_TUAN,
    VAI_TRO_GIANG_VIEN,
    VAI_TRO_SINH_VIEN,
)
from ngoai_le import KhongTimThay, LoiNghiepVu
from services.mon_hoc import lay_mon_hoc


def chuan_hoa_gio(gio: str) -> str:
    """'7:30' -> '07:30' để so sánh chuỗi chính xác."""
    gio_phut = gio.strip().split(":")
    if len(gio_phut) != 2 or not all(p.isdigit() for p in gio_phut):
        raise LoiNghiepVu(f"Giờ học '{gio}' không đúng định dạng HH:MM.")
    gio_so, phut_so = int(gio_phut[0]), int(gio_phut[1])
    if not (0 <= gio_so <= 23 and 0 <= phut_so <= 59):
        raise LoiNghiepVu(f"Giờ học '{gio}' không hợp lệ.")
    return f"{gio_so:02d}:{phut_so:02d}"


def _khoa_sap_xep(lich: dict) -> tuple:
    thu = lich.get("thứ")
    vi_tri_thu = THU_TRONG_TUAN.index(thu) if thu in THU_TRONG_TUAN else len(THU_TRONG_TUAN)
    return (int(lich.get("tuần") or 0), vi_tri_thu, lich.get("giờ_bắt_đầu") or "")


def lay_lich_hoc(dinh_danh: str) -> dict:
    lich = csdl.lay_ban_ghi(BANG_LICH_HOC, dinh_danh)
    if not lich:
        raise KhongTimThay("Không tìm thấy lịch học.")
    return lich


def lich_theo_vai_tro(nguoi_dung: dict) -> tuple[list[dict], bool]:
    """
    Trả về (danh sách lịch theo quyền, cờ 'sinh viên chưa đăng ký môn nào').
      - Quản trị viên: toàn trường
      - Giảng viên  : lịch mình được phân công
      - Sinh viên   : lịch của các môn đã đăng ký
    """
    danh_sach = csdl.lay_danh_sach(BANG_LICH_HOC)
    vai_tro = nguoi_dung.get("vai_trò")
    chua_dang_ky = False

    if vai_tro == VAI_TRO_GIANG_VIEN:
        danh_sach = [lh for lh in danh_sach if lh.get("định_danh_giảng_viên") == nguoi_dung["định_danh"]]
    elif vai_tro == VAI_TRO_SINH_VIEN:
        mon_da_dang_ky = {
            dk.get("định_danh_môn")
            for dk in csdl.lay_danh_sach(BANG_DANG_KY)
            if dk.get("định_danh_sinh_viên") == nguoi_dung["định_danh"]
        }
        chua_dang_ky = not mon_da_dang_ky
        danh_sach = [lh for lh in danh_sach if lh.get("định_danh_môn") in mon_da_dang_ky]

    danh_sach.sort(key=_khoa_sap_xep)
    return danh_sach, chua_dang_ky


def danh_sach_lich_hoc(nguoi_dung: dict, tuan: int | None = None, thu: str | None = None) -> dict:
    danh_sach, chua_dang_ky = lich_theo_vai_tro(nguoi_dung)
    if tuan:
        danh_sach = [lh for lh in danh_sach if int(lh.get("tuần") or 0) == tuan]
    if thu:
        danh_sach = [lh for lh in danh_sach if lh.get("thứ") == thu]
    return {"danh_sách": danh_sach, "chưa_đăng_ký_môn": chua_dang_ky}


def _giao_nhau(lich_a: dict, bat_dau: str, ket_thuc: str) -> bool:
    return chuan_hoa_gio(lich_a["giờ_bắt_đầu"]) < ket_thuc and bat_dau < chuan_hoa_gio(lich_a["giờ_kết_thúc"])


def tao_lich_hoc(du_lieu: dict) -> dict:
    thu = du_lieu["thứ"]
    if thu not in THU_TRONG_TUAN:
        raise LoiNghiepVu("Thứ trong tuần không hợp lệ.")

    bat_dau = chuan_hoa_gio(du_lieu["giờ_bắt_đầu"])
    ket_thuc = chuan_hoa_gio(du_lieu["giờ_kết_thúc"])
    if bat_dau >= ket_thuc:
        raise LoiNghiepVu("Giờ kết thúc phải sau giờ bắt đầu!")

    mon_hoc = lay_mon_hoc(du_lieu["định_danh_môn"])
    giang_vien = csdl.lay_ban_ghi(BANG_NGUOI_DUNG, du_lieu["định_danh_giảng_viên"])
    if not giang_vien or giang_vien.get("vai_trò") != VAI_TRO_GIANG_VIEN:
        raise LoiNghiepVu("Giảng viên được chọn không hợp lệ.")

    phong_hoc = du_lieu["phòng_học"].strip()
    tuan = int(du_lieu["tuần"])

    # Kiểm tra trùng lịch: cùng tuần, cùng thứ, khung giờ giao nhau
    for lich in csdl.lay_danh_sach(BANG_LICH_HOC):
        if int(lich.get("tuần") or 0) != tuan or lich.get("thứ") != thu:
            continue
        if not _giao_nhau(lich, bat_dau, ket_thuc):
            continue
        if lich.get("phòng_học", "").lower() == phong_hoc.lower():
            raise LoiNghiepVu(f"Phòng {phong_hoc} đã có lớp {lich.get('mã_môn')} vào khung giờ này!")
        if lich.get("định_danh_giảng_viên") == giang_vien["định_danh"]:
            raise LoiNghiepVu(f"Giảng viên {giang_vien.get('họ_tên')} đã có lịch dạy {lich.get('mã_môn')} vào khung giờ này!")

    lich_moi = {
        "định_danh": tao_dinh_danh("lh"),
        "định_danh_môn": mon_hoc["định_danh"],
        "mã_môn": mon_hoc.get("mã_môn"),
        "tên_môn": mon_hoc.get("tên_môn"),
        "định_danh_giảng_viên": giang_vien["định_danh"],
        "tên_giảng_viên": giang_vien.get("họ_tên"),
        "phòng_học": phong_hoc,
        "thứ": thu,
        "tuần": tuan,
        "giờ_bắt_đầu": bat_dau,
        "giờ_kết_thúc": ket_thuc,
    }
    csdl.luu_ban_ghi(BANG_LICH_HOC, lich_moi)
    return lich_moi
