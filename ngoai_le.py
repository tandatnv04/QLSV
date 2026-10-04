"""
NGOẠI LỆ NGHIỆP VỤ: lỗi do người dùng hoặc quy tắc nghiệp vụ gây ra,
được bộ xử lý chung trong ung_dung.py chuyển thành phản hồi JSON {"thông_báo": ...}.
"""


class LoiNghiepVu(Exception):
    def __init__(self, thong_bao: str, ma_trang_thai: int = 400):
        super().__init__(thong_bao)
        self.thong_bao = thong_bao
        self.ma_trang_thai = ma_trang_thai


class KhongTimThay(LoiNghiepVu):
    def __init__(self, thong_bao: str = "Không tìm thấy dữ liệu yêu cầu."):
        super().__init__(thong_bao, 404)


class ChuaDangNhap(LoiNghiepVu):
    def __init__(self, thong_bao: str = "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!"):
        super().__init__(thong_bao, 401)


class KhongCoQuyen(LoiNghiepVu):
    def __init__(self, thong_bao: str = "Bạn không có quyền thực hiện thao tác này!"):
        super().__init__(thong_bao, 403)
