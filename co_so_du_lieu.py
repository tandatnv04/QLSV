"""
KẾT NỐI CƠ SỞ DỮ LIỆU FIREBASE REALTIME DATABASE (qua REST API).

Cấu trúc dữ liệu: mỗi bảng là một nhánh gốc, mỗi bản ghi được lưu theo khóa "định_danh":
    /người_dùng/{định_danh}
    /môn_học/{định_danh}
    /lịch_học/{định_danh}
    /đăng_ký_học_phần/{định_danh}
    /điểm_danh/{định_danh}
"""

import json
import os
from pathlib import Path
import sqlite3
import time
import uuid
from typing import Any, Iterable
from urllib.parse import quote

import httpx

from cau_hinh import (
    DUONG_DAN_FIREBASE,
    DUONG_DAN_SQLITE,
    LOAI_CSDL,
    MA_XAC_THUC_FIREBASE,
    TEP_DU_LIEU_MAU,
    THOI_GIAN_CHO_FIREBASE,
)
from hang_so import BANG_NGUOI_DUNG, dong_bo_id, lay_id
from ngoai_le import LoiNghiepVu


class CoSoDuLieuFirebase:
    def __init__(self, duong_dan: str, ma_xac_thuc: str = ""):
        if not duong_dan.startswith("http"):
            raise RuntimeError("Chưa cấu hình FIREBASE_DATABASE_URL hợp lệ.")
        self.duong_dan = duong_dan.rstrip("/")
        self.ma_xac_thuc = ma_xac_thuc
        self._may_khach = httpx.Client(timeout=THOI_GIAN_CHO_FIREBASE)

    # ------------------------------------------------------------------
    # Thao tác cấp thấp
    # ------------------------------------------------------------------
    def _dia_chi(self, *nhanh: str) -> str:
        duong_dan_con = "/".join(quote(str(n), safe="") for n in nhanh if n)
        return f"{self.duong_dan}/{duong_dan_con}.json"

    def _tham_so(self) -> dict:
        return {"auth": self.ma_xac_thuc} if self.ma_xac_thuc else {}

    def _gui_yeu_cau(self, phuong_thuc: str, *nhanh: str, du_lieu: Any = None) -> Any:
        try:
            phan_hoi = self._may_khach.request(
                phuong_thuc,
                self._dia_chi(*nhanh),
                params=self._tham_so(),
                content=None if du_lieu is None else json.dumps(du_lieu, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
        except httpx.HTTPError as loi:
            raise LoiNghiepVu(f"Không thể kết nối tới Firebase: {loi}", 503) from loi

        if phan_hoi.status_code in (401, 403):
            raise LoiNghiepVu("Firebase từ chối truy cập. Kiểm tra quy tắc bảo mật hoặc FIREBASE_AUTH.", 503)
        if phan_hoi.status_code >= 400:
            raise LoiNghiepVu(f"Lỗi Firebase ({phan_hoi.status_code}): {phan_hoi.text}", 502)
        return phan_hoi.json() if phan_hoi.content else None

    def doc(self, *nhanh: str) -> Any:
        return self._gui_yeu_cau("GET", *nhanh)

    def ghi(self, du_lieu: Any, *nhanh: str) -> Any:
        return self._gui_yeu_cau("PUT", *nhanh, du_lieu=du_lieu)

    def cap_nhat(self, du_lieu: dict, *nhanh: str) -> Any:
        return self._gui_yeu_cau("PATCH", *nhanh, du_lieu=du_lieu)

    def xoa(self, *nhanh: str) -> None:
        self._gui_yeu_cau("DELETE", *nhanh)

    # ------------------------------------------------------------------
    # Thao tác theo bảng / bản ghi
    # ------------------------------------------------------------------
    def lay_danh_sach(self, bang: str) -> list[dict]:
        """Đọc toàn bộ bản ghi của một bảng dưới dạng danh sách."""
        du_lieu = self.doc(bang)
        if not du_lieu:
            return []
        if isinstance(du_lieu, dict):
            danh_sach = [ban_ghi for ban_ghi in du_lieu.values() if isinstance(ban_ghi, dict)]
        else:
            danh_sach = [ban_ghi for ban_ghi in du_lieu if isinstance(ban_ghi, dict)]
        return [dong_bo_id(bg) for bg in danh_sach]

    def lay_ban_ghi(self, bang: str, dinh_danh: str) -> dict | None:
        if not dinh_danh:
            return None
        ban_ghi = self.doc(bang, dinh_danh)
        return dong_bo_id(ban_ghi) if isinstance(ban_ghi, dict) else None

    def luu_ban_ghi(self, bang: str, ban_ghi: dict) -> dict:
        khoa_id = ban_ghi.get("id") or ban_ghi.get("định_danh")
        self.ghi(ban_ghi, bang, khoa_id)
        return ban_ghi

    def cap_nhat_ban_ghi(self, bang: str, dinh_danh: str, thay_doi: dict) -> None:
        self.cap_nhat(thay_doi, bang, dinh_danh)

    def xoa_ban_ghi(self, bang: str, dinh_danh: str) -> None:
        self.xoa(bang, dinh_danh)

    def xoa_nhieu_ban_ghi(self, bang: str, cac_dinh_danh: Iterable[str]) -> None:
        """Xóa nhiều bản ghi trong một lần gọi (PATCH với giá trị null)."""
        thay_doi = {dd: None for dd in cac_dinh_danh}
        if thay_doi:
            self.cap_nhat(thay_doi, bang)

    # ------------------------------------------------------------------
    # Khởi tạo dữ liệu mẫu
    # ------------------------------------------------------------------
    def da_co_du_lieu(self) -> bool:
        return self.doc(BANG_NGUOI_DUNG) is not None

    def nap_du_lieu_mau(self, ghi_de_toan_bo: bool = False) -> None:
        """
        Nạp file du_lieu/du_lieu_mau.json lên Firebase.
          - ghi_de_toan_bo=False: chỉ thêm/ghi đè các bảng tiếng Việt, giữ nguyên dữ liệu khác (PATCH).
          - ghi_de_toan_bo=True : xóa sạch và thay thế toàn bộ cơ sở dữ liệu (PUT).
        """
        with open(TEP_DU_LIEU_MAU, encoding="utf-8") as tep:
            du_lieu_mau = json.load(tep)
        if ghi_de_toan_bo:
            self.ghi(du_lieu_mau)
        else:
            self.cap_nhat(du_lieu_mau)


def tao_id(tien_to: str) -> str:
    """Sinh id duy nhất, ví dụ: dk_1759590000123_a1b2."""
    return f"{tien_to}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}"


tao_dinh_danh = tao_id


class CoSoDuLieuSQLite:
    def __init__(self, duong_dan: Path | str):
        self.duong_dan = str(duong_dan)
        if not os.path.exists(self.duong_dan):
            from tao_tep_co_so_du_lieu import khoi_tao_sqlite
            khoi_tao_sqlite(self.duong_dan)

    def _ket_noi(self):
        conn = sqlite3.connect(self.duong_dan)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def lay_danh_sach(self, bang: str) -> list[dict]:
        with self._ket_noi() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM [{bang}]")
            rows = cursor.fetchall()
            return [dong_bo_id(dict(r)) for r in rows]

    def lay_ban_ghi(self, bang: str, dinh_danh: str) -> dict | None:
        if not dinh_danh:
            return None
        with self._ket_noi() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM [{bang}] WHERE [id] = ? OR [định_danh] = ?", (dinh_danh, dinh_danh))
            r = cursor.fetchone()
            return dong_bo_id(dict(r)) if r else None

    def luu_ban_ghi(self, bang: str, ban_ghi: dict) -> dict:
        cot = list(ban_ghi.keys())
        dau_hoi = ", ".join(["?"] * len(cot))
        cot_str = ", ".join(f"[{c}]" for c in cot)
        gia_tri = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for v in ban_ghi.values()]
        sql = f"INSERT OR REPLACE INTO [{bang}] ({cot_str}) VALUES ({dau_hoi})"
        with self._ket_noi() as conn:
            conn.cursor().execute(sql, gia_tri)
            conn.commit()
        return ban_ghi

    def cap_nhat_ban_ghi(self, bang: str, dinh_danh: str, thay_doi: dict) -> None:
        if not thay_doi:
            return
        set_clauses = []
        gia_tri = []
        for k, v in thay_doi.items():
            set_clauses.append(f"[{k}] = ?")
            gia_tri.append(json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
        gia_tri.extend([dinh_danh, dinh_danh])
        sql = f"UPDATE [{bang}] SET {', '.join(set_clauses)} WHERE [id] = ? OR [định_danh] = ?"
        with self._ket_noi() as conn:
            conn.cursor().execute(sql, gia_tri)
            conn.commit()

    def xoa_ban_ghi(self, bang: str, dinh_danh: str) -> None:
        with self._ket_noi() as conn:
            conn.cursor().execute(f"DELETE FROM [{bang}] WHERE [id] = ? OR [định_danh] = ?", (dinh_danh, dinh_danh))
            conn.commit()

    def xoa_nhieu_ban_ghi(self, bang: str, cac_dinh_danh: Iterable[str]) -> None:
        danh_sach = list(cac_dinh_danh)
        if not danh_sach:
            return
        placeholders = ", ".join(["?"] * len(danh_sach))
        with self._ket_noi() as conn:
            conn.cursor().execute(f"DELETE FROM [{bang}] WHERE [id] IN ({placeholders}) OR [định_danh] IN ({placeholders})", danh_sach + danh_sach)
            conn.commit()

    def da_co_du_lieu(self) -> bool:
        try:
            return len(self.lay_danh_sach(BANG_NGUOI_DUNG)) > 0
        except Exception:
            return False

    def nap_du_lieu_mau(self, ghi_de_toan_bo: bool = False) -> None:
        from tao_tep_co_so_du_lieu import khoi_tao_sqlite
        khoi_tao_sqlite(self.duong_dan)


# Khởi tạo CSDL theo cấu hình LOAI_CSDL
if LOAI_CSDL == "sqlite":
    csdl = CoSoDuLieuSQLite(DUONG_DAN_SQLITE)
else:
    try:
        csdl = CoSoDuLieuFirebase(DUONG_DAN_FIREBASE, MA_XAC_THUC_FIREBASE)
    except Exception:
        csdl = CoSoDuLieuSQLite(DUONG_DAN_SQLITE)
