# Script to generate SQL UPDATE statements for backfilling Allure UUID
# Usage: .\scripts\backfill-allure-uuid-sql.ps1 [folder_path]
# Example: .\scripts\backfill-allure-uuid-sql.ps1 "D:\allure-reports\14-11-2025"

param(
    [string]$FolderPath = "D:\allure-reports\14-11-2025"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Generate SQL for Backfilling Allure UUID" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $FolderPath)) {
    Write-Host "❌ Folder not found: $FolderPath" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Scanning folder: $FolderPath" -ForegroundColor Yellow
Write-Host ""

# Find all result.json files
$resultFiles = Get-ChildItem -Path $FolderPath -Filter "*-result.json" -ErrorAction SilentlyContinue

if ($resultFiles.Count -eq 0) {
    Write-Host "❌ No *-result.json files found in $FolderPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found $($resultFiles.Count) result files" -ForegroundColor Green
Write-Host ""

# Parse JSON files and create mapping
$mappings = @()

foreach ($file in $resultFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        
        $allureUuid = $content.uuid
        $testName = $content.name
        $fullName = $content.fullName
        $historyId = $content.historyId
        $testCaseId = $content.testCaseId
        
        if (-not $allureUuid) {
            continue
        }
        
        $mapping = [PSCustomObject]@{
            AllureUuid = $allureUuid
            TestName = $testName
            FullName = $fullName
            HistoryId = $historyId
            TestCaseId = $testCaseId
        }
        
        $mappings += $mapping
        
        $displayName = if ($testName.Length -gt 50) { $testName.Substring(0, 50) } else { $testName }
        Write-Host "  ✓ $($file.Name): $($allureUuid.Substring(0, 8))... ($displayName)" -ForegroundColor Gray
        
    } catch {
        Write-Host "  ✗ Error reading $($file.Name): $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 Created mapping for $($mappings.Count) tests" -ForegroundColor Green
Write-Host ""

# Generate SQL UPDATE statements
$sqlLines = @()
$sqlLines += "-- Backfill Allure UUID from JSON files"
$sqlLines += "-- Generated from folder: $FolderPath"
$sqlLines += "-- Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$sqlLines += ""
$sqlLines += "BEGIN;"
$sqlLines += ""

$updateCount = 0

foreach ($mapping in $mappings) {
    $allureUuid = $mapping.AllureUuid
    $testName = $mapping.TestName
    $fullName = $mapping.FullName
    $historyId = $mapping.HistoryId
    
    # Escape single quotes for SQL (replace ' with '')
    $singleQuote = [char]39
    $testNameEscaped = $testName -replace $singleQuote, "''"
    $fullNameEscaped = $fullName -replace $singleQuote, "''"
    
    # Generate UPDATE statement using test_name and history_id
    if ($testName -and $historyId) {
        $sql = "UPDATE test_results SET allure_uuid = '$allureUuid' WHERE test_name = '$testNameEscaped' AND history_id = '$historyId' AND (allure_uuid IS NULL OR allure_uuid = '');"
        $sqlLines += $sql
        $sqlLines += ""
        $updateCount++
    }
    
    # Also try with full_name if different
    if ($fullName -and $fullName -ne $testName -and $historyId) {
        $sql = "UPDATE test_results SET allure_uuid = '$allureUuid' WHERE full_name = '$fullNameEscaped' AND history_id = '$historyId' AND (allure_uuid IS NULL OR allure_uuid = '');"
        $sqlLines += $sql
        $sqlLines += ""
        $updateCount++
    }
}

$sqlLines += "COMMIT;"
$sqlLines += ""
$sqlLines += "-- Verify updates"
$sqlLines += "SELECT COUNT(*) as updated_count FROM test_results WHERE allure_uuid IS NOT NULL AND allure_uuid != '';"
$sqlLines += ""

# Save SQL to file
$outputFile = "scripts\backfill-allure-uuid-updates.sql"
$sqlLines | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ SQL file generated!" -ForegroundColor Green
Write-Host "   File: $outputFile" -ForegroundColor Yellow
Write-Host "   Updates: $updateCount statements" -ForegroundColor Yellow
Write-Host ""
Write-Host "To apply updates:" -ForegroundColor Cyan
Write-Host "   1. psql -U qualify -d qualify_db -f $outputFile" -ForegroundColor Gray
Write-Host "   2. Or open in pgAdmin and execute" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
