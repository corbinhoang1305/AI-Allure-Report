@echo off
echo ===================================
echo  QUALIFY.AI - Stopping All Services
echo ===================================
echo.

REM Stop backend services
echo [1/2] Stopping Backend Services (Docker)...
cd /d %~dp0infrastructure\docker-compose
docker compose down
if %errorlevel% neq 0 (
    echo WARNING: Some backend services may not have stopped properly
)

echo.
echo Backend services stopped!
echo.

REM Stop frontend (kill node processes)
echo [2/2] Stopping Frontend...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo Frontend stopped!
) else (
    echo Frontend was not running
)

echo.
echo ===================================
echo  All services stopped!
echo ===================================
echo.
pause


