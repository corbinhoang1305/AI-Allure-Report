# Update Dashboard with 30 days REAL trend data
$baseFolder = "D:\allure-reports"
$outputDir = "D:\practice\AI-Allure-Report\frontend\public\real-data"

Write-Host "Generating 30-day trend data..." -ForegroundColor Green

# Get all date folders
$dateFolders = Get-ChildItem $baseFolder -Directory | Where-Object { $_.Name -match '^\d{2}-\d{2}-\d{4}$' } | Sort-Object Name

Write-Host "Found $($dateFolders.Count) date folders" -ForegroundColor Cyan

# Create output directory
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

# Process each date folder to create trend data
$trendData = @()
$allResults = @()

foreach ($folder in $dateFolders) {
    $resultFiles = Get-ChildItem $folder.FullName -Filter "*-result.json"
    
    if ($resultFiles.Count -eq 0) { continue }
    
    # Parse date from folder name (dd-MM-yyyy)
    $dateParts = $folder.Name.Split('-')
    $displayDate = "$($dateParts[0])/$($dateParts[1])"  # dd/MM
    
    # Load and analyze files for this day
    $dayPassed = 0
    $dayFailed = 0
    
    foreach ($file in $resultFiles) {
        try {
            $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
            $allResults += $content
            
            if ($content.status -eq 'passed') {
                $dayPassed++
            } elseif ($content.status -in @('failed', 'broken')) {
                $dayFailed++
            }
        } catch {
            Write-Host "  Error parsing $($file.Name)" -ForegroundColor Red
        }
    }
    
    # Add to trend data
    $trendData += @{
        date = $displayDate
        passed = $dayPassed
        failed = $dayFailed
        total = $dayPassed + $dayFailed
    }
    
    Write-Host "  $($folder.Name): $dayPassed passed, $dayFailed failed" -ForegroundColor Gray
}

# Save all results for overall stats
$allResults | ConvertTo-Json -Depth 10 | Out-File "$outputDir\all-results.json" -Encoding utf8

# Save trend data
$trendData | ConvertTo-Json -Depth 10 | Out-File "$outputDir\trend-data.json" -Encoding utf8

# Calculate overall stats
$totalPassed = ($allResults | Where-Object { $_.status -eq 'passed' }).Count
$totalFailed = ($allResults | Where-Object { $_.status -in @('failed', 'broken') }).Count
$totalTests = $allResults.Count
$passRate = if ($totalTests -gt 0) { [math]::Round(($totalPassed / $totalTests) * 100, 1) } else { 0 }

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SUCCESS!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Generated trend data from $($dateFolders.Count) days" -ForegroundColor White
Write-Host ""
Write-Host "Overall Statistics:" -ForegroundColor Yellow
Write-Host "  Total Tests: $totalTests" -ForegroundColor White
Write-Host "  Passed: $totalPassed" -ForegroundColor Green
Write-Host "  Failed: $totalFailed" -ForegroundColor Red
Write-Host "  Pass Rate: $passRate%" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output files:" -ForegroundColor Yellow
Write-Host "  - all-results.json (all tests)" -ForegroundColor White
Write-Host "  - trend-data.json (30 days trend)" -ForegroundColor White
Write-Host ""
Write-Host "REFRESH DASHBOARD:" -ForegroundColor Cyan
Write-Host "http://localhost:3000/dashboard (F5)" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green

