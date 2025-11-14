# Auto Watcher - Runs every 5 minutes
# Updates dashboard data automatically

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=============================================="
Write-Host "  QUALIFY.AI - Auto Watcher" -ForegroundColor Green  
Write-Host "=============================================="
Write-Host ""
Write-Host "Watching: D:\allure-reports"
Write-Host "Updates every: 5 minutes"
Write-Host "Output: frontend\public\real-data"
Write-Host ""
Write-Host "Press Ctrl+C to stop"
Write-Host ""

# Load update script
$scriptPath = Join-Path $PSScriptRoot "update-trend-data.ps1"

# Initial scan
Write-Host "Running initial scan..." -ForegroundColor Yellow
& $scriptPath

# Continuous monitoring
$count = 1
while ($true) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host "Waiting 5 minutes for next scan..."
    Write-Host "Scan #$count completed. Next scan in 5 min" -ForegroundColor Gray
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    
    Start-Sleep -Seconds 300  # 5 minutes
    
    $count++
    Write-Host ""
    Write-Host "Running scan #$count..." -ForegroundColor Yellow
    & $scriptPath
}

