# QUALIFY.AI - Services Status Check
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    QUALIFY.AI Services Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check services
$services = @{
    "Frontend Dashboard" = @{Port=3000; Url="http://localhost:3000"}
    "API Gateway (Nginx)" = @{Port=8000; Url="http://localhost:8000"}
    "Auth Service" = @{Port=8001; Url="http://localhost:8001/docs"}
    "Report Aggregator" = @{Port=8002; Url="http://localhost:8002/docs"}
    "AI Analysis" = @{Port=8003; Url="http://localhost:8003/docs"}
    "Analytics Service" = @{Port=8004; Url="http://localhost:8004/docs"}
    "MinIO Console" = @{Port=9001; Url="http://localhost:9001"}
}

$allRunning = $true

foreach ($name in $services.Keys | Sort-Object) {
    $service = $services[$name]
    $port = $service.Port
    $url = $service.Url
    
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    
    if ($connection) {
        Write-Host "[OK]" -ForegroundColor Green -NoNewline
        Write-Host " $name" -ForegroundColor White
        Write-Host "     Port: $port | URL: $url" -ForegroundColor Gray
    } else {
        Write-Host "[X]" -ForegroundColor Red -NoNewline
        Write-Host " $name - NOT RUNNING" -ForegroundColor Red
        Write-Host "     Port: $port should be listening" -ForegroundColor Gray
        $allRunning = $false
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan

if ($allRunning) {
    Write-Host ""
    Write-Host "All services are running!" -ForegroundColor Green
    Write-Host "Access the dashboard at: http://localhost:3000" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Some services are not running!" -ForegroundColor Red
    Write-Host "To start backend services:" -ForegroundColor Yellow
    Write-Host "  cd infrastructure\docker-compose" -ForegroundColor Gray
    Write-Host "  docker compose up -d" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To start frontend:" -ForegroundColor Yellow
    Write-Host "  .\start-frontend.bat" -ForegroundColor Gray
    Write-Host ""
}

# Show Docker containers status
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Containers:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    Push-Location
    Set-Location "infrastructure\docker-compose"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    Pop-Location
} catch {
    Write-Host "Could not get Docker container status" -ForegroundColor Yellow
}

Write-Host ""


