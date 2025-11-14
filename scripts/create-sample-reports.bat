@echo off
echo ====================================
echo Creating Sample Allure Reports
echo ====================================
echo.

REM Create base directory
set REPORTS_DIR=D:\allure-reports

echo Creating folder structure: %REPORTS_DIR%
mkdir "%REPORTS_DIR%" 2>nul

REM Get today's date in dd-mm-yyyy format
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set TODAY=%%a-%%b-%%c
)

echo Creating today's folder: %TODAY%
mkdir "%REPORTS_DIR%\%TODAY%" 2>nul

REM Copy sample data
echo Copying sample Allure reports...
copy /Y "%~dp0\..\frontend\public\sample-data\sample-allure-result.json" "%REPORTS_DIR%\%TODAY%\test-result-001.json"

echo.
echo ✓ Sample reports created successfully!
echo Location: %REPORTS_DIR%\%TODAY%
echo.
echo You can now start the Report Watcher Service
echo Run: scripts\start-watcher.bat
echo.

pause

