# Quick Flaky Test Checker - PowerShell Version
# Không cần Python, chỉ dùng PowerShell

param(
    [string]$FolderPath = "D:\allure-reports\14-11-2025"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Flaky Test Detector (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check folder exists
if (-not (Test-Path $FolderPath)) {
    Write-Host "ERROR: Folder khong ton tai: $FolderPath" -ForegroundColor Red
    exit 1
}

Write-Host "Dang quet folder: $FolderPath" -ForegroundColor Yellow
Write-Host ""

# Load all JSON files
$jsonFiles = Get-ChildItem -Path $FolderPath -Filter "*-result.json"
$totalFiles = $jsonFiles.Count

if ($totalFiles -eq 0) {
    Write-Host "ERROR: Khong tim thay file JSON nao!" -ForegroundColor Red
    exit 1
}

Write-Host "Tim thay $totalFiles file JSON result" -ForegroundColor Green
Write-Host ""
Write-Host "Dang phan tich..." -ForegroundColor Yellow

# Parse all tests
$tests = @()
$stats = @{
    passed = 0
    failed = 0
    broken = 0
    skipped = 0
    unknown = 0
}

foreach ($file in $jsonFiles) {
    try {
        $json = Get-Content $file.FullName -Raw | ConvertFrom-Json
        
        $testInfo = [PSCustomObject]@{
            File = $file.Name
            Name = $json.name
            FullName = $json.fullName
            Status = $json.status
            TestCaseId = $json.testCaseId
            HistoryId = $json.historyId
            Start = $json.start
            Stop = $json.stop
        }
        
        $tests += $testInfo
        
        # Update stats
        if ($stats.ContainsKey($json.status)) {
            $stats[$json.status]++
        } else {
            $stats.unknown++
        }
    }
    catch {
        Write-Host "Warning: Khong doc duoc file $($file.Name)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TONG QUAN THONG KE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tong so test results: $totalFiles"
Write-Host "  Passed: $($stats.passed)" -ForegroundColor Green
Write-Host "  Failed: $($stats.failed)" -ForegroundColor Red
Write-Host "  Broken: $($stats.broken)" -ForegroundColor Magenta
Write-Host "  Skipped: $($stats.skipped)" -ForegroundColor Yellow
Write-Host "  Unknown: $($stats.unknown)" -ForegroundColor Gray
Write-Host ""

# Group by TestCaseId
$groupedByTestId = $tests | Where-Object { $_.TestCaseId } | Group-Object -Property TestCaseId

# Find flaky tests
$flakyTests = @()

foreach ($group in $groupedByTestId) {
    if ($group.Count -gt 1) {
        $statuses = $group.Group | Select-Object -ExpandProperty Status -Unique
        if ($statuses.Count -gt 1) {
            $flakyTests += [PSCustomObject]@{
                Name = $group.Group[0].Name
                FullName = $group.Group[0].FullName
                TestCaseId = $group.Name
                Occurrences = $group.Count
                Statuses = $statuses -join ", "
                Tests = $group.Group
            }
        }
    }
}

# Also group by FullName (fallback)
$groupedByFullName = $tests | Where-Object { $_.FullName } | Group-Object -Property FullName

foreach ($group in $groupedByFullName) {
    if ($group.Count -gt 1) {
        $statuses = $group.Group | Select-Object -ExpandProperty Status -Unique
        if ($statuses.Count -gt 1) {
            # Check if not already added
            $alreadyAdded = $flakyTests | Where-Object { $_.FullName -eq $group.Group[0].FullName }
            if (-not $alreadyAdded) {
                $flakyTests += [PSCustomObject]@{
                    Name = $group.Group[0].Name
                    FullName = $group.Group[0].FullName
                    TestCaseId = $group.Group[0].TestCaseId
                    Occurrences = $group.Count
                    Statuses = $statuses -join ", "
                    Tests = $group.Group
                }
            }
        }
    }
}

Write-Host "Tong so FLAKY TESTS phat hien: $($flakyTests.Count)" -ForegroundColor $(if ($flakyTests.Count -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($flakyTests.Count -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  TUYET VOI! Khong co flaky test nao!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    exit 0
}

Write-Host "========================================" -ForegroundColor Red
Write-Host "  DANH SACH FLAKY TESTS" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

$index = 1
foreach ($flaky in $flakyTests) {
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "Flaky Test #$index" -ForegroundColor Red
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "Test Name: $($flaky.Name)"
    Write-Host "Full Name: $($flaky.FullName)"
    Write-Host "Test Case ID: $($flaky.TestCaseId)"
    Write-Host "So lan xuat hien: $($flaky.Occurrences)"
    Write-Host "Cac trang thai: $($flaky.Statuses)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Chi tiet cac lan chay:"
    
    $runIndex = 1
    foreach ($test in $flaky.Tests) {
        $statusColor = switch ($test.Status) {
            "passed" { "Green" }
            "failed" { "Red" }
            "broken" { "Magenta" }
            "skipped" { "Yellow" }
            default { "Gray" }
        }
        
        $duration = if ($test.Stop -gt $test.Start) {
            [math]::Round(($test.Stop - $test.Start) / 1000, 2)
        } else { 0 }
        
        $statusIcon = switch ($test.Status) {
            "passed" { "[OK]" }
            "failed" { "[X]" }
            "broken" { "[!]" }
            "skipped" { "[-]" }
            default { "[?]" }
        }
        
        Write-Host "  Run $runIndex`: " -NoNewline
        Write-Host "$statusIcon $($test.Status.ToUpper())" -ForegroundColor $statusColor -NoNewline
        Write-Host " | Duration: ${duration}s | File: $($test.File)"
        $runIndex++
    }
    
    Write-Host ""
    $index++
}

Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$csvFile = "flaky_tests_report_$timestamp.csv"

$flakyTests | Select-Object Name, FullName, TestCaseId, Occurrences, Statuses | 
    Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8

Write-Host "Bao cao da duoc export ra file: $csvFile" -ForegroundColor Green
Write-Host ""

exit 1


