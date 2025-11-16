@echo off
echo ========================================
echo   Flaky Test Detector
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python chua duoc cai dat!
    echo.
    echo Vui long cai dat Python tu: https://www.python.org/downloads/
    echo Nho chon "Add Python to PATH" khi cai dat
    echo.
    pause
    exit /b 1
)

echo Python da san sang!
echo.

REM Run the script
echo Dang kiem tra flaky tests trong folder: D:\allure-reports\14-11-2025
echo.

python check_flaky_tests.py

echo.
echo ========================================
echo.
pause


