"""
ỨNG DỤNG CHÍNH EDUPRO (FastAPI Application).
Điểm khởi chạy máy chủ backend, quản lý phiên cookie, xử lý lỗi và đăng ký toàn bộ router.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from cau_hinh import (
    KHOA_BI_MAT_PHIEN,
    TEP_TRANG_CHU,
    TEN_COOKIE_PHIEN,
    THOI_HAN_PHIEN_GIAY,
    THU_MUC_GIAO_DIEN,
    TU_DONG_KHOI_TAO,
)
from co_so_du_lieu import csdl
from hang_so import BANG_NGUOI_DUNG
from ngoai_le import LoiNghiepVu
from routers.diem_danh import bo_dinh_tuyen as router_diem_danh
from routers.diem_so import bo_dinh_tuyen as router_diem_so
from routers.ho_so import bo_dinh_tuyen as router_ho_so
from routers.hoc_phan import bo_dinh_tuyen as router_hoc_phan
from routers.lich_hoc import bo_dinh_tuyen as router_lich_hoc
from routers.mon_hoc import bo_dinh_tuyen as router_mon_hoc
from routers.nguoi_dung import bo_dinh_tuyen as router_nguoi_dung
from routers.thong_ke import bo_dinh_tuyen as router_thong_ke
from routers.xac_thuc import bo_dinh_tuyen as router_xac_thuc


@asynccontextmanager
async def vong_doi_ung_dung(app: FastAPI):
    """Khởi động hệ thống: tự động nạp dữ liệu chuẩn tiếng Việt lên Firebase nếu chưa có."""
    if TU_DONG_KHOI_TAO:
        try:
            if not csdl.da_co_du_lieu():
                print("[EduPro] Phát hiện Firebase chưa có nhánh 'người_dùng'. Đang nạp dữ liệu mẫu tiếng Việt...")
                csdl.nap_du_lieu_mau(ghi_de_toan_bo=False)
                print("[EduPro] Nạp dữ liệu mẫu thành công!")
        except Exception as e:
            print(f"[EduPro Warning] Không thể tự động nạp dữ liệu mẫu lên Firebase: {e}")
    yield


app = FastAPI(
    title="EduPro Enterprise - Hệ Thống Quản Lý Sinh Viên",
    description="Backend FastAPI quản lý đào tạo, thời khóa biểu, điểm số và học phí theo phân quyền 3 tầng.",
    version="4.0.0",
    lifespan=vong_doi_ung_dung,
)

# Quản lý phiên bằng SessionMiddleware (lưu session an toàn trong cookie có chữ ký mật mã)
app.add_middleware(
    SessionMiddleware,
    secret_key=KHOA_BI_MAT_PHIEN,
    session_cookie=TEN_COOKIE_PHIEN,
    max_age=THOI_HAN_PHIEN_GIAY,
    same_site="lax",
    https_only=False,
)

# Cho phép CORS linh hoạt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Xử lý lỗi nghiệp vụ thống nhất dạng JSON tiếng Việt
@app.exception_handler(LoiNghiepVu)
async def xu_ly_loi_nghiep_vu(request: Request, loi: LoiNghiepVu):
    return JSONResponse(
        status_code=loi.ma_trang_thai,
        content={"thành_công": False, "thông_báo": loi.thong_bao},
    )


# Đăng ký các router chức năng
app.include_router(router_xac_thuc)
app.include_router(router_ho_so)
app.include_router(router_nguoi_dung)
app.include_router(router_mon_hoc)
app.include_router(router_lich_hoc)
app.include_router(router_diem_danh)
app.include_router(router_diem_so)
app.include_router(router_hoc_phan)
app.include_router(router_thong_ke)


@app.post("/api/he-thong/nap-du-lieu-mau", tags=["Hệ thống"])
def nap_lai_du_lieu_mau():
    """Endpoint tiện ích để nạp lại dữ liệu mẫu tiếng Việt từ file du_lieu/du_lieu_mau.json."""
    csdl.nap_du_lieu_mau(ghi_de_toan_bo=False)
    return {"thành_công": True, "thông_báo": "Đã nạp thành công bộ dữ liệu chuẩn tiếng Việt lên Firebase!"}


# Phục vụ tệp tĩnh (CSS, JS, hình ảnh)
if THU_MUC_GIAO_DIEN.exists():
    app.mount("/static", StaticFiles(directory=str(THU_MUC_GIAO_DIEN)), name="static")


# Phục vụ trang giao diện chính index.html
@app.get("/", include_in_schema=False)
def trang_chu():
    return FileResponse(TEP_TRANG_CHU)


if __name__ == "__main__":
    import uvicorn
    print("[EduPro] Đang khởi chạy máy chủ tại http://127.0.0.1:8000 ...")
    uvicorn.run("ung_dung:app", host="127.0.0.1", port=8000, reload=True)
