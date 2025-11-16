# QUALIFY.AI - Setup and Run Script for Windows
# This script helps setup and run the application

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "QUALIFY.AI - Setup and Run" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if frontend dependencies are installed
Write-Host "📦 Checking frontend dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Check for Docker
Write-Host "🐳 Checking for Docker..." -ForegroundColor Yellow
$dockerAvailable = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
        $dockerAvailable = $true
    }
} catch {
    Write-Host "❌ Docker not found" -ForegroundColor Red
}

# Check for Python
Write-Host "🐍 Checking for Python..." -ForegroundColor Yellow
$pythonAvailable = $false
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
        $pythonAvailable = $true
    }
} catch {
    try {
        $pythonVersion = py --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
            $pythonAvailable = $true
        }
    } catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Setup Options:" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

if ($dockerAvailable) {
    Write-Host "✅ Option 1: Use Docker (Recommended)" -ForegroundColor Green
    Write-Host "   - All services will run in Docker containers" -ForegroundColor Gray
    Write-Host "   - No need to install Python, PostgreSQL, Redis separately" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   To start backend with Docker:" -ForegroundColor Yellow
    Write-Host "   cd infrastructure\docker-compose" -ForegroundColor White
    Write-Host "   docker compose up -d" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Option 1: Docker not available" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop from https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host ""
}

if ($pythonAvailable) {
    Write-Host "✅ Option 2: Manual Setup (Python required)" -ForegroundColor Green
    Write-Host "   - You'll need PostgreSQL and Redis installed separately" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   To setup backend manually:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   python -m venv venv" -ForegroundColor White
    Write-Host "   .\venv\Scripts\activate" -ForegroundColor White
    Write-Host "   pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Option 2: Python not available" -ForegroundColor Red
    Write-Host "   Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location frontend
npm run dev



