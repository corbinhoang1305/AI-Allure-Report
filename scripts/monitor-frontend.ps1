# Monitor and Auto-Restart Frontend
# Usage: .\scripts\monitor-frontend.ps1

$checkInterval = 30 # seconds
$frontendPath = Join-Path $PSScriptRoot "..\frontend"
$port = 3000

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Monitor Started" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Monitoring port $port every $checkInterval seconds" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
        return $connection
    } catch {
        return $false
    }
}

function Start-Frontend {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting frontend..." -ForegroundColor Yellow
    
    # Kill existing node processes on port 3000
    $existingProcesses = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($existingProcesses) {
        foreach ($pid in $existingProcesses) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "  Stopped existing process $pid" -ForegroundColor Gray
            } catch {}
        }
        Start-Sleep -Seconds 2
    }
    
    # Start frontend
    Push-Location $frontendPath
    try {
        $process = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -PassThru -WindowStyle Minimized
        Write-Host "  Frontend started (PID: $($process.Id))" -ForegroundColor Green
        
        # Wait for frontend to start
        $maxWait = 30
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 2
            $waited += 2
            if (Test-Port -Port $port) {
                Write-Host "  Frontend is ready on port $port" -ForegroundColor Green
                return $true
            }
        }
        Write-Host "  Warning: Frontend may not have started properly" -ForegroundColor Yellow
        return $false
    } finally {
        Pop-Location
    }
}

# Initial check
if (-not (Test-Port -Port $port)) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Frontend is not running. Starting..." -ForegroundColor Red
    Start-Frontend
}

# Monitor loop
while ($true) {
    Start-Sleep -Seconds $checkInterval
    
    if (-not (Test-Port -Port $port)) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ⚠️  Frontend is DOWN! Restarting..." -ForegroundColor Red
        Start-Frontend
    } else {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ Frontend is running" -ForegroundColor Green
    }
}

