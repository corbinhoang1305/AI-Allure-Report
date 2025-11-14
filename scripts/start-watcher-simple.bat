@echo off
echo ====================================
echo QUALIFY.AI - Report Watcher
echo ====================================
echo.
echo Starting Report Watcher Service...
echo Watching: D:\allure-reports
echo Scan interval: Every 5 minutes
echo Output: frontend\public\real-data
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0\..\backend\services\report-watcher-standalone"

python watcher.py

pause

