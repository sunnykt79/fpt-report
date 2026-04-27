@echo off
title Khởi chạy - FPT Telecom Sales Reporting Dashboard
color 0A

echo ===================================================
echo     FPT TELECOM SALES REPORTING DASHBOARD (FSRD)
echo ===================================================
echo.
echo Dang kiem tra moi truong he thong...

:: Kiểm tra xem Python đã được cài đặt chưa
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [LOI] Khong tim thay Python tren he thong cua ban!
    echo.
    echo Vui long tai va cai dat Python tu trang chu: https://www.python.org/downloads/
    echo Luu y: Nho danh dau tich vao o "Add Python to PATH" truoc khi bam Install
    echo.
    pause
    exit /b
)

echo [OK] Da tim thay Python.

:: Cài đặt thư viện (pip tự động bỏ qua nếu đã cài)
echo.
echo Dang kiem tra va cai dat cac thu vien can thiet...
echo (Qua trinh nay co the mat vai phut neu day la lan dau chay)
python -m pip install -r requirements.txt

:: Khởi chạy ứng dụng
echo.
echo ===================================================
echo [THONG BAO] Dang khoi dong Web App...
echo Trinh duyet cua ban se tu dong mo len ngay bay gio.
echo (Vui long giu nguyen cua so nay trong qua trinh su dung app)
echo ===================================================
echo.

:: Chay Streamlit truc tiep tren cua so nay
python -m streamlit run app.py

pause
