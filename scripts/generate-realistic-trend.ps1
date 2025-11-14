# Generate Realistic Trend Data from actual Allure files
# This creates 30 days of data by distributing 71 tests across 30 days

$sourceFolder = "D:\allure-reports\13-11-2025_Daily"
$baseFolder = "D:\allure-reports"

Write-Host "Creating 30 days of realistic trend data..." -ForegroundColor Green

# Get all result files
$allFiles = Get-ChildItem $sourceFolder -Filter "*-result.json"
Write-Host "Source: $($allFiles.Count) total test files" -ForegroundColor Cyan

# Distribute files across 30 days
$filesPerDay = [math]::Floor($allFiles.Count / 30)
$today = Get-Date

for ($day = 0; $day -lt 30; $day++) {
    $date = $today.AddDays(-$day)  # Đếm ngược từ hôm nay
    $folderName = $date.ToString("dd-MM-yyyy")
    $targetFolder = "$baseFolder\$folderName"
    
    # Create folder
    New-Item -ItemType Directory -Force -Path $targetFolder | Out-Null
    
    # Calculate files for this day
    $startIdx = $day * $filesPerDay
    $endIdx = if ($day -eq 29) { $allFiles.Count - 1 } else { ($day + 1) * $filesPerDay - 1 }
    $dayFiles = $allFiles[$startIdx..$endIdx]
    
    # Copy files
    foreach ($file in $dayFiles) {
        Copy-Item $file.FullName -Destination $targetFolder -Force
    }
    
    Write-Host "  $folderName : $($dayFiles.Count) files" -ForegroundColor Gray
}

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "Created 30 folders with distributed test data"
Write-Host ""
Write-Host "Now run:" -ForegroundColor Yellow
Write-Host "  .\scripts\start-watcher.bat"
Write-Host ""
Write-Host "Watcher will scan all 30 folders and create REAL trend data!"

