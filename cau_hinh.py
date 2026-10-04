"""
CẤU HÌNH HỆ THỐNG EDUPRO

Mọi giá trị đều có thể ghi đè bằng biến môi trường khi triển khai:
  - FIREBASE_DATABASE_URL : Đường dẫn Firebase Realtime Database
  - FIREBASE_AUTH         : (Tùy chọn) Khóa bí mật / mã truy cập Firebase nếu đã bật quy tắc bảo mật
  - KHOA_BI_MAT_PHIEN     : Khóa ký cookie phiên đăng nhập (BẮT BUỘC đổi khi triển khai thật)
  - TU_DONG_KHOI_TAO      : "1" (mặc định) để tự nạp dữ liệu mẫu khi Firebase chưa có dữ liệu
"""

import os
from pathlib import Path

THU_MUC_GOC = Path(__file__).resolve().parent
THU_MUC_GIAO_DIEN = THU_MUC_GOC / "static"
TEP_TRANG_CHU = THU_MUC_GOC / "index.html"
TEP_DU_LIEU_MAU = THU_MUC_GOC / "du_lieu" / "du_lieu_mau.json"

DUONG_DAN_FIREBASE = os.getenv(
    "FIREBASE_DATABASE_URL",
    "https://websinhvien-7ccec-default-rtdb.asia-southeast1.firebasedatabase.app",
).strip().rstrip("/")
MA_XAC_THUC_FIREBASE = os.getenv("FIREBASE_AUTH", "").strip()
THOI_GIAN_CHO_FIREBASE = float(os.getenv("THOI_GIAN_CHO_FIREBASE", "15"))

KHOA_BI_MAT_PHIEN = os.getenv("KHOA_BI_MAT_PHIEN", "edupro-khoa-phien-mac-dinh-hay-doi-khi-trien-khai")
TEN_COOKIE_PHIEN = "phien_edupro"
THOI_HAN_PHIEN_GIAY = 7 * 24 * 60 * 60  # 7 ngày

TU_DONG_KHOI_TAO = os.getenv("TU_DONG_KHOI_TAO", "1") == "1"

# Cấu hình Cơ sở dữ liệu: "firebase" (mặc định) hoặc "sqlite"
LOAI_CSDL = os.getenv("LOAI_CSDL", "firebase").lower()
DUONG_DAN_SQLITE = Path(os.getenv("DUONG_DAN_SQLITE", str(THU_MUC_GOC / "quan_ly_sinh_vien.db")))
