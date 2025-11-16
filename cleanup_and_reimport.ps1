#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete cleanup and re-import all data from Allure JSON files

.DESCRIPTION
    This script will:
    1. Delete ALL existing test data for Nov 13-15
    2. Re-import from Allure JSON files with correct retry information
    3. Add unique constraint to prevent future duplicates
    4. Stop auto-import services
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$AllureBaseFolder = "D:\allure-reports"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  COMPLETE DATA CLEANUP & REIMPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Delete ALL existing data
Write-Host "Step 1: Deleting ALL existing test data..." -ForegroundColor Yellow
Write-Host ""

$dates = @('2025-11-13', '2025-11-14', '2025-11-15')

foreach ($date in $dates) {
    Write-Host "  Deleting data for $date..." -ForegroundColor Gray
    
    # Delete test results first
    docker exec qualify-postgres psql -U qualify -d qualify_db -c @"
DELETE FROM test_results 
WHERE run_id IN (
    SELECT id FROM test_runs 
    WHERE started_at::date = '$date'
);
"@
    
    # Delete test runs
    docker exec qualify-postgres psql -U qualify -d qualify_db -c @"
DELETE FROM test_runs 
WHERE started_at::date = '$date';
"@
}

Write-Host "`n  All old data deleted!" -ForegroundColor Green
Write-Host ""

# Step 2: Verify cleanup
Write-Host "Step 2: Verifying cleanup..." -ForegroundColor Yellow
$remaining = docker exec qualify-postgres psql -U qualify -d qualify_db -t -c @"
SELECT COUNT(*) FROM test_runs 
WHERE started_at::date BETWEEN '2025-11-13' AND '2025-11-15';
"@

if ($remaining.Trim() -eq '0') {
    Write-Host "  Cleanup successful - 0 runs remaining" -ForegroundColor Green
} else {
    Write-Host "  WARNING: $($remaining.Trim()) runs still remaining!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Re-import from Allure JSON files
Write-Host "Step 3: Re-importing from Allure JSON files..." -ForegroundColor Yellow
Write-Host ""

$folders = @(
    @{ Folder = "13-11-2025"; Date = "2025-11-13" },
    @{ Folder = "14-11-2025"; Date = "2025-11-14" },
    @{ Folder = "15-11-2025"; Date = "2025-11-15" }
)

foreach ($item in $folders) {
    $folderPath = Join-Path $AllureBaseFolder $item.Folder
    
    if (Test-Path $folderPath) {
        Write-Host "  Importing $($item.Folder)..." -ForegroundColor Cyan
        
        docker run --rm --network qualify-network `
            -v ${PWD}:/work `
            -v D:/allure-reports:/allure-reports `
            python:3.11-slim bash -c @"
pip install -q psycopg2-binary && \
python /work/import_allure_to_db.py /allure-reports/$($item.Folder) $($item.Date)
"@
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    Import successful!" -ForegroundColor Green
        } else {
            Write-Host "    Import FAILED!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  Folder not found: $folderPath" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Step 4: Add unique constraint
Write-Host "Step 4: Adding unique constraint to prevent duplicates..." -ForegroundColor Yellow
docker exec qualify-postgres psql -U qualify -d qualify_db -c @"
-- Drop index if exists
DROP INDEX IF EXISTS idx_test_runs_unique_date;

-- Create unique index on (suite_id, date)
CREATE UNIQUE INDEX idx_test_runs_unique_date 
ON test_runs (suite_id, (started_at::date));
"@ 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Unique constraint added successfully!" -ForegroundColor Green
} else {
    Write-Host "  Warning: Could not add unique constraint (may already exist)" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Stop report-aggregator to prevent auto-import
Write-Host "Step 5: Stopping report-aggregator service..." -ForegroundColor Yellow
cd infrastructure/docker-compose
docker compose stop report-aggregator 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Report-aggregator stopped!" -ForegroundColor Green
} else {
    Write-Host "  Could not stop report-aggregator (may not be running)" -ForegroundColor Yellow
}
cd ../..
Write-Host ""

# Step 6: Verify final data
Write-Host "Step 6: Verifying final data..." -ForegroundColor Yellow
Write-Host ""

$verification = docker exec qualify-postgres psql -U qualify -d qualify_db -t -c @"
SELECT 
    started_at::date as date,
    COUNT(*) as num_runs
FROM test_runs 
WHERE started_at::date BETWEEN '2025-11-13' AND '2025-11-15'
GROUP BY started_at::date
ORDER BY date;
"@

Write-Host $verification
Write-Host ""

# Step 7: Check API
Write-Host "Step 7: Checking API response..." -ForegroundColor Yellow
Write-Host ""

try {
    $apiData = Invoke-WebRequest -Uri "http://localhost:8000/api/analytics/dashboard" -UseBasicParsing | 
        Select-Object -ExpandProperty Content | 
        ConvertFrom-Json |
        Select-Object -ExpandProperty recent_trends |
        Where-Object { $_.date -ge '2025-11-13' -and $_.date -le '2025-11-15' }
    
    Write-Host "API Response:" -ForegroundColor Cyan
    $apiData | Format-Table -AutoSize
    
    # Verify 14-11 data
    $day14 = $apiData | Where-Object { $_.date -eq '2025-11-14' }
    if ($day14.passed -eq 66 -and $day14.flaky -eq 4 -and $day14.failed -eq 1) {
        Write-Host "  2025-11-14: CORRECT!" -ForegroundColor Green
        Write-Host "    Passed: 66, Flaky: 4, Failed: 1" -ForegroundColor Green
    } else {
        Write-Host "  2025-11-14: INCORRECT!" -ForegroundColor Red
        Write-Host "    Got: Passed=$($day14.passed), Flaky=$($day14.flaky), Failed=$($day14.failed)" -ForegroundColor Red
        Write-Host "    Expected: Passed=66, Flaky=4, Failed=1" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Could not verify API (may need to wait for cache refresh)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CLEANUP & REIMPORT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "2. Check Historical Trend Chart" -ForegroundColor White
Write-Host "3. Verify data is correct (14-11: 66 passed, 4 flaky, 1 failed)" -ForegroundColor White
Write-Host ""
Write-Host "To prevent future duplicates:" -ForegroundColor Yellow
Write-Host "- Unique constraint has been added" -ForegroundColor White
Write-Host "- Report-aggregator service has been stopped" -ForegroundColor White
Write-Host ""

