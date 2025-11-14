# Update Dashboard with Real Allure Data
# Usage: .\scripts\update-dashboard-data.ps1 "D:\allure-reports\13-11-2025_Daily"

param(
    [string]$SourceFolder = "D:\allure-reports\13-11-2025_Daily"
)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Updating Dashboard with Real Data" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if source folder exists
if (!(Test-Path $SourceFolder)) {
    Write-Host "ERROR: Source folder not found: $SourceFolder" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available folders in D:\allure-reports:" -ForegroundColor Yellow
    Get-ChildItem "D:\allure-reports" -Directory | Select-Object Name | Format-Table
    exit 1
}

# Get all result files
$resultFiles = Get-ChildItem $SourceFolder -Filter "*-result.json"
Write-Host "Found $($resultFiles.Count) result files in source folder" -ForegroundColor Green

if ($resultFiles.Count -eq 0) {
    Write-Host "ERROR: No *-result.json files found!" -ForegroundColor Red
    exit 1
}

# Target directory
$targetDir = "D:\practice\AI-Allure-Report\frontend\public\real-data"
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

Write-Host "Merging JSON files..." -ForegroundColor Yellow

# Merge all JSON files
$allResults = @()
foreach ($file in $resultFiles) {
    try {
        $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
        $allResults += $content
        Write-Host "  ✓ $($file.Name)" -ForegroundColor Gray
    } catch {
        Write-Host "  ✗ Error parsing $($file.Name)" -ForegroundColor Red
    }
}

# Save merged JSON
$outputFile = "$targetDir\all-results.json"
$allResults | ConvertTo-Json -Depth 10 | Out-File $outputFile -Encoding utf8

$fileSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 2)

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output: $outputFile" -ForegroundColor White
Write-Host "Size: $fileSize KB" -ForegroundColor White  
Write-Host "Tests: $($allResults.Count)" -ForegroundColor White
Write-Host ""

# Analyze data
$passed = ($allResults | Where-Object { $_.status -eq 'passed' }).Count
$failed = ($allResults | Where-Object { $_.status -eq 'failed' -or $_.status -eq 'broken' }).Count
$passRate = if ($allResults.Count -gt 0) { [math]::Round(($passed / $allResults.Count) * 100, 1) } else { 0 }

Write-Host "Statistics:" -ForegroundColor Yellow
Write-Host "  Total: $($allResults.Count)" -ForegroundColor White
Write-Host "  Passed: $passed" -ForegroundColor Green
Write-Host "  Failed: $failed" -ForegroundColor Red
Write-Host "  Pass Rate: $passRate%" -ForegroundColor Cyan
Write-Host ""
Write-Host "REFRESH DASHBOARD TO SEE REAL DATA:" -ForegroundColor Yellow
Write-Host "http://localhost:3000/dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press F5 in browser!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan

