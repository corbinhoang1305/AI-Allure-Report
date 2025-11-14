@echo off
echo ====================================
echo Starting Report Watcher Service
echo ====================================
echo.

cd /d "%~dp0\..\backend\services\report-watcher"

echo Setting up Python environment...
python -m venv venv
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Report Watcher Service...
echo Watching folder: D:\allure-reports
echo Scan interval: 5 minutes
echo.

uvicorn app.main:app --reload --port 8005

