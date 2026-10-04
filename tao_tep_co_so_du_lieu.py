"""
TẠO TỆP CƠ SỞ DỮ LIỆU SQLITE (.db)
Đọc dữ liệu từ du_lieu/du_lieu_mau.json hoặc firebase_database_seed.json và tạo:
- quan_ly_sinh_vien.db (ở thư mục gốc)
- du_lieu/quan_ly_sinh_vien.db

Các cột định danh được đặt tên chuẩn là:
  - id (thay cho định_danh)
  - id_môn (thay cho định_danh_môn)
  - id_giảng_viên (thay cho định_danh_giảng_viên)
  - id_sinh_viên (thay cho định_danh_sinh_viên)
  - id_lịch_học (thay cho định_danh_lịch_học)
"""

import json
import os
import sqlite3

THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
FILE_JSON = os.path.join(THU_MUC_GOC, "du_lieu", "du_lieu_mau.json")
if not os.path.exists(FILE_JSON):
    FILE_JSON = os.path.join(THU_MUC_GOC, "firebase_database_seed.json")

DUONG_DAN_DB_GOC = os.path.join(THU_MUC_GOC, "quan_ly_sinh_vien.db")
DUONG_DAN_DB_DU_LIEU = os.path.join(THU_MUC_GOC, "du_lieu", "quan_ly_sinh_vien.db")


def khoi_tao_sqlite(duong_dan_db: str):
    print(f"[*] Đang tạo cơ sở dữ liệu SQLite tại: {duong_dan_db}")
    if os.path.exists(duong_dan_db):
        try:
            os.remove(duong_dan_db)
        except Exception:
            pass

    os.makedirs(os.path.dirname(duong_dan_db), exist_ok=True)
    ket_noi = sqlite3.connect(duong_dan_db)
    con_tro = ket_noi.cursor()

    # Bật khóa ngoại
    con_tro.execute("PRAGMA foreign_keys = ON;")

    # 1. Bảng người_dùng
    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS người_dùng (
        id TEXT PRIMARY KEY,
        tên_đăng_nhập TEXT UNIQUE NOT NULL,
        mật_khẩu TEXT NOT NULL,
        vai_trò TEXT NOT NULL,
        họ_tên TEXT NOT NULL,
        mã_số TEXT,
        email TEXT,
        số_điện_thoại TEXT,
        khoa TEXT,
        chức_danh TEXT,
        tuổi INTEGER,
        lớp TEXT,
        ảnh_đại_diện TEXT,
        trạng_thái TEXT DEFAULT 'Hoạt động'
    );
    """)

    # 2. Bảng môn_học
    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS môn_học (
        id TEXT PRIMARY KEY,
        mã_môn TEXT UNIQUE NOT NULL,
        tên_môn TEXT NOT NULL,
        số_tín_chỉ INTEGER NOT NULL,
        khoa TEXT,
        đơn_giá_tín_chỉ REAL DEFAULT 450000,
        học_kỳ TEXT,
        mô_tả TEXT,
        ngày_mở_nhập_điểm TEXT,
        ngày_chốt_điểm TEXT,
        khóa_nhập_điểm INTEGER DEFAULT 0
    );
    """)

    # 3. Bảng lịch_học
    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS lịch_học (
        id TEXT PRIMARY KEY,
        id_môn TEXT,
        mã_môn TEXT,
        tên_môn TEXT,
        id_giảng_viên TEXT,
        tên_giảng_viên TEXT,
        phòng_học TEXT,
        thứ INTEGER,
        tuần TEXT,
        giờ_bắt_đầu TEXT,
        giờ_kết_thúc TEXT,
        FOREIGN KEY (id_môn) REFERENCES môn_học(id) ON DELETE CASCADE,
        FOREIGN KEY (id_giảng_viên) REFERENCES người_dùng(id) ON DELETE SET NULL
    );
    """)

    # 4. Bảng đăng_ký_học_phần
    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS đăng_ký_học_phần (
        id TEXT PRIMARY KEY,
        id_sinh_viên TEXT NOT NULL,
        id_môn TEXT NOT NULL,
        điểm_giữa_kỳ REAL,
        điểm_cuối_kỳ REAL,
        điểm_chuyên_cần REAL,
        nhận_xét TEXT,
        đã_đóng_học_phí INTEGER DEFAULT 0,
        FOREIGN KEY (id_sinh_viên) REFERENCES người_dùng(id) ON DELETE CASCADE,
        FOREIGN KEY (id_môn) REFERENCES môn_học(id) ON DELETE CASCADE
    );
    """)

    # 5. Bảng điểm_danh
    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS điểm_danh (
        id TEXT PRIMARY KEY,
        id_lịch_học TEXT NOT NULL,
        ngày TEXT NOT NULL,
        danh_sách TEXT,
        FOREIGN KEY (id_lịch_học) REFERENCES lịch_học(id) ON DELETE CASCADE
    );
    """)

    # Đọc dữ liệu mẫu từ JSON
    with open(FILE_JSON, "r", encoding="utf-8") as f:
        du_lieu = json.load(f)

    # Nạp người_dùng
    for r in du_lieu.get("người_dùng", {}).values():
        con_tro.execute(
            """
            INSERT OR REPLACE INTO người_dùng (
                id, tên_đăng_nhập, mật_khẩu, vai_trò, họ_tên,
                mã_số, email, số_điện_thoại, khoa, chức_danh, tuổi, lớp, ảnh_đại_diện, trạng_thái
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r.get("id") or r.get("định_danh"),
                r.get("tên_đăng_nhập"),
                r.get("mật_khẩu"),
                r.get("vai_trò"),
                r.get("họ_tên"),
                r.get("mã_số"),
                r.get("email"),
                r.get("số_điện_thoại"),
                r.get("khoa"),
                r.get("chức_danh"),
                r.get("tuổi"),
                r.get("lớp"),
                r.get("ảnh_đại_diện"),
                r.get("trạng_thái", "Hoạt động"),
            ),
        )

    # Nạp môn_học
    for r in du_lieu.get("môn_học", {}).values():
        con_tro.execute(
            """
            INSERT OR REPLACE INTO môn_học (
                id, mã_môn, tên_môn, số_tín_chỉ, khoa, đơn_giá_tín_chỉ,
                học_kỳ, mô_tả, ngày_mở_nhập_điểm, ngày_chốt_điểm, khóa_nhập_điểm
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r.get("id") or r.get("định_danh"),
                r.get("mã_môn"),
                r.get("tên_môn"),
                r.get("số_tín_chỉ"),
                r.get("khoa"),
                r.get("đơn_giá_tín_chỉ", 450000),
                r.get("học_kỳ"),
                r.get("mô_tả"),
                r.get("ngày_mở_nhập_điểm"),
                r.get("ngày_chốt_điểm"),
                1 if r.get("khóa_nhập_điểm") else 0,
            ),
        )

    # Nạp lịch_học
    for r in du_lieu.get("lịch_học", {}).values():
        con_tro.execute(
            """
            INSERT OR REPLACE INTO lịch_học (
                id, id_môn, mã_môn, tên_môn, id_giảng_viên,
                tên_giảng_viên, phòng_học, thứ, tuần, giờ_bắt_đầu, giờ_kết_thúc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r.get("id") or r.get("định_danh"),
                r.get("id_môn") or r.get("định_danh_môn"),
                r.get("mã_môn"),
                r.get("tên_môn"),
                r.get("id_giảng_viên") or r.get("định_danh_giảng_viên"),
                r.get("tên_giảng_viên"),
                r.get("phòng_học"),
                r.get("thứ"),
                str(r.get("tuần")),
                r.get("giờ_bắt_đầu"),
                r.get("giờ_kết_thúc"),
            ),
        )

    # Nạp đăng_ký_học_phần
    for r in du_lieu.get("đăng_ký_học_phần", {}).values():
        con_tro.execute(
            """
            INSERT OR REPLACE INTO đăng_ký_học_phần (
                id, id_sinh_viên, id_môn,
                điểm_giữa_kỳ, điểm_cuối_kỳ, điểm_chuyên_cần, nhận_xét, đã_đóng_học_phí
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r.get("id") or r.get("định_danh"),
                r.get("id_sinh_viên") or r.get("định_danh_sinh_viên"),
                r.get("id_môn") or r.get("định_danh_môn"),
                r.get("điểm_giữa_kỳ"),
                r.get("điểm_cuối_kỳ"),
                r.get("điểm_chuyên_cần"),
                r.get("nhận_xét"),
                1 if r.get("đã_đóng_học_phí") else 0,
            ),
        )

    # Nạp điểm_danh
    for r in du_lieu.get("điểm_danh", {}).values():
        danh_sach = r.get("danh_sách")
        if isinstance(danh_sach, (dict, list)):
            danh_sach_str = json.dumps(danh_sach, ensure_ascii=False)
        else:
            danh_sach_str = str(danh_sach or "")
        con_tro.execute(
            """
            INSERT OR REPLACE INTO điểm_danh (
                id, id_lịch_học, ngày, danh_sách
            ) VALUES (?, ?, ?, ?)
            """,
            (
                r.get("id") or r.get("định_danh"),
                r.get("id_lịch_học") or r.get("định_danh_lịch_học"),
                r.get("ngày"),
                danh_sach_str,
            ),
        )

    ket_noi.commit()
    ket_noi.close()
    print(f"[OK] Đã tạo thành công cơ sở dữ liệu SQLite: {duong_dan_db}")


if __name__ == "__main__":
    khoi_tao_sqlite(DUONG_DAN_DB_GOC)
    khoi_tao_sqlite(DUONG_DAN_DB_DU_LIEU)
    print("\n[HOÀN TẤT] Cả 2 file .db đã sẵn sàng sử dụng!")
