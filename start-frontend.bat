@echo off
echo ===================================
echo Starting QUALIFY.AI Frontend
echo ===================================
echo.

cd /d %~dp0frontend

echo Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause



