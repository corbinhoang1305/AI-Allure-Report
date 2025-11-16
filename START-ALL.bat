@echo off
echo ===================================
echo  QUALIFY.AI - Starting All Services
echo ===================================
echo.

REM Start backend services with Docker
echo [1/2] Starting Backend Services (Docker)...
cd /d %~dp0infrastructure\docker-compose
docker compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start backend services
    pause
    exit /b 1
)

echo.
echo Backend services started successfully!
echo.

REM Start frontend in a new window
echo [2/2] Starting Frontend...
cd /d %~dp0
start "QUALIFY.AI Frontend" cmd /k start-frontend.bat

echo.
echo ===================================
echo  All services started!
echo ===================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo Run "show-status.ps1" to check status
echo.
pause


