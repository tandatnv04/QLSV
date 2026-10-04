"""
QUẢN LÝ MÔN HỌC & CỔNG NHẬP ĐIỂM.
"""

from datetime import date

from co_so_du_lieu import csdl, tao_dinh_danh
from hang_so import (
    BANG_DANG_KY,
    BANG_LICH_HOC,
    BANG_MON_HOC,
    DON_GIA_TIN_CHI_MAC_DINH,
    HOC_KY_MAC_DINH,
    KHOA_MAC_DINH,
    NGAY_CHOT_DIEM_MAC_DINH,
    NGAY_MO_NHAP_DIEM_MAC_DINH,
    SO_TIN_CHI_MAC_DINH,
    VAI_TRO_QUAN_TRI,
)
from ngoai_le import KhongTimThay, LoiNghiepVu


def lay_mon_hoc(dinh_danh: str) -> dict:
    mon_hoc = csdl.lay_ban_ghi(BANG_MON_HOC, dinh_danh)
    if not mon_hoc:
        raise KhongTimThay("Không tìm thấy môn học.")
    return mon_hoc


def bo_sung_hoc_phi(mon_hoc: dict) -> dict:
    so_tin_chi = int(mon_hoc.get("số_tín_chỉ") or SO_TIN_CHI_MAC_DINH)
    don_gia = int(mon_hoc.get("đơn_giá_tín_chỉ") or DON_GIA_TIN_CHI_MAC_DINH)
    return {**mon_hoc, "số_tín_chỉ": so_tin_chi, "đơn_giá_tín_chỉ": don_gia, "tổng_học_phí": so_tin_chi * don_gia}


def danh_sach_mon_hoc() -> list[dict]:
    ket_qua = [bo_sung_hoc_phi(mh) for mh in csdl.lay_danh_sach(BANG_MON_HOC)]
    ket_qua.sort(key=lambda mh: mh.get("mã_môn") or "")
    return ket_qua


def bang_tra_mon_hoc() -> dict[str, dict]:
    """Bảng tra cứu nhanh: định_danh -> môn học."""
    return {mh["định_danh"]: mh for mh in csdl.lay_danh_sach(BANG_MON_HOC)}


def tao_mon_hoc(du_lieu: dict) -> dict:
    ma_mon = du_lieu["mã_môn"].strip().upper()
    if any((mh.get("mã_môn") or "").upper() == ma_mon for mh in csdl.lay_danh_sach(BANG_MON_HOC)):
        raise LoiNghiepVu(f"Mã môn {ma_mon} đã tồn tại!")

    mon_hoc = {
        "định_danh": tao_dinh_danh("mh"),
        "mã_môn": ma_mon,
        "tên_môn": du_lieu["tên_môn"].strip(),
        "số_tín_chỉ": du_lieu.get("số_tín_chỉ") or SO_TIN_CHI_MAC_DINH,
        "đơn_giá_tín_chỉ": du_lieu.get("đơn_giá_tín_chỉ") or DON_GIA_TIN_CHI_MAC_DINH,
        "khoa": du_lieu.get("khoa", "").strip() or KHOA_MAC_DINH,
        "học_kỳ": du_lieu.get("học_kỳ", "").strip() or HOC_KY_MAC_DINH,
        "mô_tả": du_lieu.get("mô_tả", "").strip() or "Môn học chương trình chính khóa.",
        "ngày_mở_nhập_điểm": NGAY_MO_NHAP_DIEM_MAC_DINH,
        "ngày_chốt_điểm": NGAY_CHOT_DIEM_MAC_DINH,
        "khóa_nhập_điểm": False,
    }
    csdl.luu_ban_ghi(BANG_MON_HOC, mon_hoc)
    return bo_sung_hoc_phi(mon_hoc)


def xoa_mon_hoc(dinh_danh: str) -> None:
    """Xóa môn học kèm toàn bộ lịch học và đăng ký học phần liên quan."""
    lay_mon_hoc(dinh_danh)
    cac_lich = [lh["định_danh"] for lh in csdl.lay_danh_sach(BANG_LICH_HOC) if lh.get("định_danh_môn") == dinh_danh]
    cac_dang_ky = [dk["định_danh"] for dk in csdl.lay_danh_sach(BANG_DANG_KY) if dk.get("định_danh_môn") == dinh_danh]
    csdl.xoa_nhieu_ban_ghi(BANG_LICH_HOC, cac_lich)
    csdl.xoa_nhieu_ban_ghi(BANG_DANG_KY, cac_dang_ky)
    csdl.xoa_ban_ghi(BANG_MON_HOC, dinh_danh)


# ----------------------------------------------------------------------
# Cổng nhập điểm
# ----------------------------------------------------------------------
def cap_nhat_han_nhap_diem(dinh_danh: str, du_lieu: dict) -> dict:
    mon_hoc = lay_mon_hoc(dinh_danh)
    ngay_mo: date = du_lieu["ngày_mở_nhập_điểm"]
    ngay_chot: date = du_lieu["ngày_chốt_điểm"]
    if ngay_mo > ngay_chot:
        raise LoiNghiepVu("Ngày mở cổng phải trước hoặc bằng ngày chốt sổ điểm!")

    thay_doi = {
        "ngày_mở_nhập_điểm": ngay_mo.isoformat(),
        "ngày_chốt_điểm": ngay_chot.isoformat(),
        "khóa_nhập_điểm": bool(du_lieu.get("khóa_nhập_điểm")),
    }
    csdl.cap_nhat_ban_ghi(BANG_MON_HOC, dinh_danh, thay_doi)
    return {**mon_hoc, **thay_doi}


def trang_thai_cong_diem(mon_hoc: dict, nguoi_dung: dict) -> dict:
    """
    Xác định cổng điểm đang mở hay khóa với người dùng hiện tại.
    Quản trị viên luôn được phép sửa điểm; giảng viên chỉ sửa được trong thời hạn và khi chưa khóa sổ.
    """
    hom_nay = date.today().isoformat()
    ngay_mo = mon_hoc.get("ngày_mở_nhập_điểm") or NGAY_MO_NHAP_DIEM_MAC_DINH
    ngay_chot = mon_hoc.get("ngày_chốt_điểm") or NGAY_CHOT_DIEM_MAC_DINH
    la_quan_tri = nguoi_dung.get("vai_trò") == VAI_TRO_QUAN_TRI

    ly_do_khoa = ""
    if mon_hoc.get("khóa_nhập_điểm"):
        ly_do_khoa = "Sổ điểm đã được Quản trị viên khóa"
    elif hom_nay > ngay_chot and not la_quan_tri:
        ly_do_khoa = "Đã hết hạn sửa điểm"
    elif hom_nay < ngay_mo and not la_quan_tri:
        ly_do_khoa = "Chưa đến ngày mở nhập điểm"

    return {
        "ngày_mở_nhập_điểm": ngay_mo,
        "ngày_chốt_điểm": ngay_chot,
        "đã_khóa": bool(ly_do_khoa),
        "lý_do_khóa": ly_do_khoa,
        "được_phép_sửa": la_quan_tri or not ly_do_khoa,
    }
