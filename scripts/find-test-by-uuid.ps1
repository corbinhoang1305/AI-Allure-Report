# Script to find test result.json file by database UUID
# Usage: .\scripts\find-test-by-uuid.ps1 "966f8822-2852-4139-80cd-2d631366abcb"

param(
    [Parameter(Mandatory=$true)]
    [string]$DatabaseUUID
)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Finding Test by Database UUID" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database UUID: $DatabaseUUID" -ForegroundColor Yellow
Write-Host ""

# Check if database connection is available
# For now, we'll search result.json files directly by test name
# You'll need to query the database first to get test details

Write-Host "Searching for test in result.json files..." -ForegroundColor Yellow
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
                
                # Check if UUID matches (though this is unlikely since UUID shown is database UUID)
                if ($content.uuid -eq $DatabaseUUID) {
                    Write-Host "  ✓ Found matching UUID in: $($file.FullName)" -ForegroundColor Green
                    $foundFiles += $file
                }
                
                # Also check test name for "should fail to create user with missing required field"
                if ($content.name -like "*should fail to create user with missing required field*") {
                    Write-Host "  ✓ Found matching test name in: $($file.FullName)" -ForegroundColor Cyan
                    Write-Host "    UUID: $($content.uuid)" -ForegroundColor Gray
                    Write-Host "    Status: $($content.status)" -ForegroundColor Gray
                    Write-Host "    Date folder: $($file.Directory.Name)" -ForegroundColor Gray
                    $foundFiles += $file
                }
            } catch {
                Write-Host "  ✗ Error reading $($file.Name)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Path not found: $searchPath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
if ($foundFiles.Count -gt 0) {
    Write-Host "Found $($foundFiles.Count) matching file(s)" -ForegroundColor Green
} else {
    Write-Host "No matching files found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Note: The UUID shown in dashboard ($DatabaseUUID) is a DATABASE UUID," -ForegroundColor Yellow
    Write-Host "not the Allure UUID from result.json files." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To find the actual result.json file, you need to:" -ForegroundColor Yellow
    Write-Host "1. Query the database to get test details (name, history_id, etc.)" -ForegroundColor Yellow
    Write-Host "2. Search result.json files for matching test name/details" -ForegroundColor Yellow
}
Write-Host "==================================" -ForegroundColor Cyan

