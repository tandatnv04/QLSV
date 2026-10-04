@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul

echo ======================================================================
echo    EDUPRO - HE THONG QUAN LY SINH VIEN (FASTAPI BACKEND)
echo ======================================================================
echo.
echo Dang kiem tra moi truong Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python tren may tinh. Vui long cai dat Python 3.10+!
    pause
    exit /b 1
)

python -c "import fastapi, uvicorn, httpx, itsdangerous, pydantic" >nul 2>&1
if errorlevel 1 (
    echo Dang cai dat cac thu vien can thiet tu requirements.txt...
    pip install -r requirements.txt
)

echo.
echo ======================================================================
echo Dang khoi chay may chu tai: http://127.0.0.1:8000
echo Tai lieu API (Swagger UI): http://127.0.0.1:8000/docs
echo Bam Ctrl + C trong cua so nay de tat may chu.
echo ======================================================================
echo.

python -m uvicorn ung_dung:app --host 127.0.0.1 --port 8000 --reload
pause
