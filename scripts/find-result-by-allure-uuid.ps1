# Script to find result.json file by Allure UUID
# Usage: .\scripts\find-result-by-allure-uuid.ps1 "b7ee92bc-8dbd-4425-8b7e-a985f16b3508"

param(
    [Parameter(Mandatory=$true)]
    [string]$AllureUUID
)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Finding result.json by Allure UUID" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Allure UUID: $AllureUUID" -ForegroundColor Yellow
Write-Host ""

# Search in common locations
$searchPaths = @(
    "D:\allure-reports",
    "frontend\public\real-data"
)

$foundFiles = @()

foreach ($searchPath in $searchPaths) {
    if (Test-Path $searchPath) {
        Write-Host "Searching in: $searchPath" -ForegroundColor Gray
        
        # Search for all result.json files
        $resultFiles = Get-ChildItem -Path $searchPath -Filter "*-result.json" -Recurse -ErrorAction SilentlyContinue
        
        foreach ($file in $resultFiles) {
            try {
                $content = Get-Content $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                
                # Check if UUID matches
                if ($content.uuid -eq $AllureUUID) {
                    Write-Host "  FOUND MATCHING FILE!" -ForegroundColor Green
                    Write-Host "    File: $($file.FullName)" -ForegroundColor Cyan
                    Write-Host "    Test Name: $($content.name)" -ForegroundColor White
                    $statusColor = if ($content.status -eq 'failed') { 'Red' } else { 'Green' }
                    Write-Host "    Status: $($content.status)" -ForegroundColor $statusColor
                    Write-Host "    Date Folder: $($file.Directory.Name)" -ForegroundColor Yellow
                    Write-Host ""
                    $foundFiles += $file
                }
            } catch {
                Write-Host "  Error reading $($file.Name)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Path not found: $searchPath" -ForegroundColor Yellow
    }
}

Write-Host "==================================" -ForegroundColor Cyan
if ($foundFiles.Count -gt 0) {
    Write-Host "Found $($foundFiles.Count) matching file(s)" -ForegroundColor Green
} else {
    Write-Host "No matching files found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Note: Make sure the UUID is the Allure UUID from result.json," -ForegroundColor Yellow
    Write-Host "not the database UUID shown in the dashboard." -ForegroundColor Yellow
}
Write-Host "==================================" -ForegroundColor Cyan
