# Update Dashboard Data
$SourceFolder = "D:\allure-reports\13-11-2025_Daily"
$TargetDir = "D:\practice\AI-Allure-Report\frontend\public\real-data"

Write-Host "Updating Dashboard Data..." -ForegroundColor Green

# Create target directory
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

# Get result files
$resultFiles = Get-ChildItem $SourceFolder -Filter "*-result.json"
Write-Host "Found $($resultFiles.Count) result files"

# Merge all JSON
$allResults = @()
foreach ($file in $resultFiles) {
    $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
    $allResults += $content
}

# Save
$outputFile = "$TargetDir\all-results.json"
$allResults | ConvertTo-Json -Depth 10 | Out-File $outputFile -Encoding utf8

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "Created: $outputFile"
Write-Host "Tests: $($allResults.Count)"
Write-Host ""
Write-Host "REFRESH BROWSER: http://localhost:3000/dashboard" -ForegroundColor Cyan

