@echo off
echo ===================================
echo Starting QUALIFY.AI Backend Services (Docker)
echo ===================================
echo.

cd /d %~dp0infrastructure\docker-compose

echo Checking for Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo.
echo Creating .env file if it doesn't exist...
if not exist ".env" (
    echo OPENAI_API_KEY=your-openai-api-key-here > .env
    echo SECRET_KEY=your-secret-key-change-in-production-min-32-chars >> .env
    echo.
    echo WARNING: Please update .env file with your actual values!
    echo.
    pause
)

echo.
echo Starting all backend services...
docker compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 5 /nobreak >nul

echo.
echo Service Status:
docker compose ps

echo.
echo ===================================
echo Backend services started!
echo ===================================
echo.
echo Service URLs:
echo   - Auth Service: http://localhost:8001
echo   - Report Aggregator: http://localhost:8002
echo   - AI Analysis: http://localhost:8003
echo   - Analytics: http://localhost:8004
echo   - API Gateway: http://localhost:8000
echo   - MinIO Console: http://localhost:9001 (admin/minioadmin123)
echo.
echo To view logs: docker compose logs -f [service-name]
echo To stop services: docker compose down
echo.

pause



