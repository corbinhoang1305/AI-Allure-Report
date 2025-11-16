# ========================================
# QUALIFY.AI - Script Setup và Chạy Web
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  QUALIFY.AI - Setup và Chạy Web" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra Docker Desktop
Write-Host "[1/5] Kiểm tra Docker Desktop..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    docker info 2>$null | Out-Null
    $dockerRunning = $true
    Write-Host "✅ Docker Desktop đang chạy" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop không chạy hoặc chưa cài đặt" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vui lòng:" -ForegroundColor Yellow
    Write-Host "  1. Mở Docker Desktop" -ForegroundColor White
    Write-Host "  2. Đợi cho đến khi Docker Desktop khởi động xong" -ForegroundColor White
    Write-Host "  3. Chạy lại script này" -ForegroundColor White
    Write-Host ""
    Read-Host "Nhấn Enter để thoát"
    exit 1
}

Write-Host ""

# Kiểm tra file .env
Write-Host "[2/5] Kiểm tra file cấu hình..." -ForegroundColor Yellow
if (Test-Path "infrastructure\docker-compose\.env") {
    Write-Host "✅ File .env đã tồn tại" -ForegroundColor Green
} else {
    Write-Host "⚠️  File .env chưa tồn tại, đang tạo file mặc định..." -ForegroundColor Yellow
    Write-Host "   (Bạn có thể thay đổi OPENAI_API_KEY sau nếu muốn)" -ForegroundColor Gray
}

Write-Host ""

# Start Backend Services với Docker
Write-Host "[3/5] Khởi động Backend Services (PostgreSQL, Redis, MinIO, APIs)..." -ForegroundColor Yellow
Write-Host "   Đây có thể mất vài phút lần đầu tiên (tải Docker images)..." -ForegroundColor Gray
Write-Host ""

Push-Location infrastructure\docker-compose
try {
    # Build và start các services
    docker compose up -d --build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend services đã được khởi động" -ForegroundColor Green
    } else {
        Write-Host "❌ Có lỗi khi khởi động backend services" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "❌ Lỗi: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""

# Đợi services khởi động
Write-Host "   Đợi các services khởi động hoàn toàn..." -ForegroundColor Gray
Start-Sleep -Seconds 15

Write-Host ""

# Kiểm tra node_modules
Write-Host "[4/5] Cài đặt Frontend Dependencies..." -ForegroundColor Yellow

Push-Location frontend
if (!(Test-Path "node_modules")) {
    Write-Host "   Đang cài đặt npm packages (có thể mất vài phút)..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend dependencies đã được cài đặt" -ForegroundColor Green
    } else {
        Write-Host "❌ Có lỗi khi cài đặt dependencies" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "✅ Frontend dependencies đã có sẵn" -ForegroundColor Green
}
Pop-Location

Write-Host ""

# Start Frontend
Write-Host "[5/5] Khởi động Frontend Development Server..." -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ SETUP HOÀN TẤT!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Các dịch vụ đang chạy:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Frontend:        http://localhost:3000" -ForegroundColor White
Write-Host "   API Gateway:     http://localhost:8000" -ForegroundColor White
Write-Host "   Auth Service:    http://localhost:8001" -ForegroundColor White
Write-Host "   Report Service:  http://localhost:8002" -ForegroundColor White
Write-Host "   AI Service:      http://localhost:8003" -ForegroundColor White
Write-Host "   Analytics:       http://localhost:8004" -ForegroundColor White
Write-Host "   MinIO Console:   http://localhost:9001 (minioadmin/minioadmin123)" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Đang khởi động Frontend..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   Nhấn Ctrl+C để dừng Frontend" -ForegroundColor Gray
Write-Host "   Để dừng Backend, chạy: docker compose -f infrastructure\docker-compose\docker-compose.yml down" -ForegroundColor Gray
Write-Host ""

# Start frontend
Push-Location frontend
npm run dev
Pop-Location

