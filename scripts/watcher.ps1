# Report Watcher - PowerShell Version
# Scans Allure folders every 5 minutes and updates frontend data

$WatchFolder = "D:\allure-reports"
$OutputFolder = "D:\practice\AI-Allure-Report\frontend\public\real-data"
$ScanIntervalSeconds = 300  # 5 minutes

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  QUALIFY.AI - Report Watcher Service" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Watching: $WatchFolder" -ForegroundColor Yellow
Write-Host "Output: $OutputFolder" -ForegroundColor Yellow
Write-Host "Interval: $($ScanIntervalSeconds / 60) minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

function Scan-AllureFolders {
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "Scanning at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Get all date folders (dd-MM-yyyy format)
    $dateFolders = Get-ChildItem $WatchFolder -Directory | 
                   Where-Object { $_.Name -match '^\d{2}-\d{2}-\d{4}$' } |
                   Sort-Object Name
    
    if ($dateFolders.Count -eq 0) {
        Write-Host "No folders found with format dd-MM-yyyy" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Found $($dateFolders.Count) date folders" -ForegroundColor Cyan
    Write-Host ""
    
    # Process each folder
    $allResults = @()
    $trendData = @()
    
    foreach ($folder in $dateFolders) {
        $resultFiles = Get-ChildItem $folder.FullName -Filter "*-result.json"
        
        if ($resultFiles.Count -eq 0) { continue }
        
        Write-Host "Processing $($folder.Name): $($resultFiles.Count) files" -ForegroundColor Gray
        
        # Parse date for display (dd/MM)
        $dateParts = $folder.Name.Split('-')
        $displayDate = "$($dateParts[0])/$($dateParts[1])"
        
        # Analyze files
        $dayPassed = 0
        $dayFailed = 0
        
        foreach ($file in $resultFiles) {
            try {
                $content = Get-Content $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                $allResults += $content
                
                if ($content.status -eq 'passed') {
                    $dayPassed++
                } elseif ($content.status -in @('failed', 'broken')) {
                    $dayFailed++
                }
            } catch {
                Write-Host "  Error reading $($file.Name)" -ForegroundColor Red
            }
        }
        
        # Add to trend
        $trendData += @{
            date = $displayDate
            passed = $dayPassed
            failed = $dayFailed
            total = $dayPassed + $dayFailed
        }
        
        Write-Host "  $dayPassed passed, $dayFailed failed" -ForegroundColor Green
    }
    
    # Create output directory
    New-Item -ItemType Directory -Force -Path $OutputFolder | Out-Null
    
    # Save all results
    $allResultsFile = Join-Path $OutputFolder "all-results.json"
    $allResults | ConvertTo-Json -Depth 10 | Out-File $allResultsFile -Encoding UTF8
    
    # Save trend data
    $trendDataFile = Join-Path $OutputFolder "trend-data.json"
    $trendData | ConvertTo-Json -Depth 10 | Out-File $trendDataFile -Encoding UTF8
    
    # Calculate stats
    $totalPassed = ($allResults | Where-Object { $_.status -eq 'passed' }).Count
    $totalFailed = ($allResults | Where-Object { $_.status -in @('failed', 'broken') }).Count
    $totalTests = $allResults.Count
    $passRate = if ($totalTests -gt 0) { [math]::Round(($totalPassed / $totalTests) * 100, 1) } else { 0 }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Yellow
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Total Tests: $totalTests" -ForegroundColor White
    Write-Host "Passed: $totalPassed" -ForegroundColor Green
    Write-Host "Failed: $totalFailed" -ForegroundColor Red
    Write-Host "Pass Rate: $passRate%" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Files updated:" -ForegroundColor Yellow
    Write-Host "  - all-results.json" -ForegroundColor White
    Write-Host "  - trend-data.json" -ForegroundColor White
    Write-Host ""
    Write-Host "Dashboard will auto-refresh in next cycle" -ForegroundColor Gray
    Write-Host "Or refresh manually: http://localhost:3000/dashboard" -ForegroundColor Cyan
    Write-Host ""
}

# Initial scan
Scan-AllureFolders

# Continuous scanning
while ($true) {
    Write-Host "Next scan in $($ScanIntervalSeconds / 60) minutes..." -ForegroundColor Gray
    Write-Host "Waiting..." -ForegroundColor DarkGray
    Write-Host ""
    
    Start-Sleep -Seconds $ScanIntervalSeconds
    Scan-AllureFolders
}

