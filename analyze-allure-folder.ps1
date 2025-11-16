# PowerShell version of Allure Folder Analyzer
param(
    [string]$FolderPath = "D:\allure-reports\14-11-2025"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ALLURE FOLDER ANALYZER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logic:" -ForegroundColor Yellow
Write-Host "  - Passed: Test chay 1 lan va passed" -ForegroundColor Green
Write-Host "  - Flaky:  Test failed lan dau, passed lan retry" -ForegroundColor Yellow
Write-Host "  - Failed: Test failed (du co retry hay khong)" -ForegroundColor Red
Write-Host ""

# Check folder exists
if (-not (Test-Path $FolderPath)) {
    Write-Host "ERROR: Folder khong ton tai: $FolderPath" -ForegroundColor Red
    exit 1
}

Write-Host "Dang phan tich folder: $FolderPath" -ForegroundColor Cyan
Write-Host ""

# Get all result JSON files
$jsonFiles = Get-ChildItem -Path $FolderPath -Filter "*-result.json"
Write-Host "Tim thay $($jsonFiles.Count) result files" -ForegroundColor Yellow
Write-Host ""

# Parse all files
$testCases = @{}

foreach ($file in $jsonFiles) {
    try {
        $json = Get-Content $file.FullName -Raw | ConvertFrom-Json
        
        # Get unique identifier
        $historyId = $json.historyId
        $testCaseId = $json.testCaseId
        $fullName = $json.fullName
        $testKey = if ($historyId) { $historyId } elseif ($testCaseId) { $testCaseId } else { $fullName }
        
        if (-not $testKey) {
            Write-Host "Warning: Skip $($file.Name) - no identifier" -ForegroundColor Yellow
            continue
        }
        
        # Get status and timing
        $status = $json.status
        $start = $json.start
        $stop = $json.stop
        $duration = if ($stop -gt $start) { ($stop - $start) / 1000 } else { 0 }
        
        if (-not $testCases.ContainsKey($testKey)) {
            $testCases[$testKey] = @()
        }
        
        $testCases[$testKey] += [PSCustomObject]@{
            File = $file.Name
            Name = $json.name
            Status = $status
            Start = $start
            Stop = $stop
            Duration = $duration
        }
    }
    catch {
        Write-Host "Warning: Error reading $($file.Name): $_" -ForegroundColor Yellow
    }
}

Write-Host "Nhan dien duoc $($testCases.Count) unique test cases" -ForegroundColor Green
Write-Host ""

# Categorize test cases
$passedTests = @()
$flakyTests = @()
$failedTests = @()

foreach ($testKey in $testCases.Keys) {
    $results = @($testCases[$testKey] | Sort-Object Start)
    $numRuns = $results.Count
    $statuses = @($results | ForEach-Object { $_.Status })
    $firstStatus = $results[0].Status
    $finalStatus = $results[-1].Status
    
    $testInfo = [PSCustomObject]@{
        Key = $testKey
        Name = $results[0].Name
        NumRuns = $numRuns
        Statuses = ($statuses -join " -> ")
        Results = $results
    }
    
    if ($numRuns -eq 1) {
        # Single run - no retry
        if ($firstStatus -eq 'passed') {
            # Passed: ran once and passed
            $passedTests += $testInfo
        }
        else {
            # Failed: ran once and failed
            $failedTests += $testInfo
        }
    }
    else {
        # Multiple runs - has retry
        if ($firstStatus -in @('failed', 'broken')) {
            # First run failed
            if ($finalStatus -eq 'passed') {
                # Flaky: failed first, passed on retry
                $flakyTests += $testInfo
            }
            else {
                # Failed: failed first, still failed after retry
                $failedTests += $testInfo
            }
        }
        elseif ($firstStatus -eq 'passed') {
            # First run passed but has multiple runs
            # Treat as Flaky (unstable)
            $flakyTests += $testInfo
        }
    }
}

# Print summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  KET QUA PHAN TICH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PASSED: $($passedTests.Count) tests (chay 1 lan va passed)" -ForegroundColor Green
Write-Host "FLAKY:  $($flakyTests.Count) tests (co retry)" -ForegroundColor Yellow
Write-Host "FAILED: $($failedTests.Count) tests (failed)" -ForegroundColor Red
Write-Host ""
Write-Host "Total test cases: $($testCases.Count)" -ForegroundColor White
Write-Host "Total result files: $($jsonFiles.Count)" -ForegroundColor White
Write-Host ""

# Show flaky tests details
if ($flakyTests.Count -gt 0) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  FLAKY TESTS (Chi tiet)" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    
    $index = 1
    foreach ($test in $flakyTests) {
        Write-Host "$index. $($test.Name)" -ForegroundColor Yellow
        Write-Host "   Runs: $($test.NumRuns)" -ForegroundColor White
        Write-Host "   Statuses: $($test.Statuses)" -ForegroundColor White
        
        $runIndex = 1
        foreach ($result in $test.Results) {
            $icon = if ($result.Status -eq 'passed') { '[OK]' } else { '[X]' }
            $color = if ($result.Status -eq 'passed') { 'Green' } else { 'Red' }
            Write-Host "      Run $runIndex`: " -NoNewline
            Write-Host "$icon $($result.Status.ToUpper())" -ForegroundColor $color -NoNewline
            Write-Host " ($([math]::Round($result.Duration, 2))s)" -ForegroundColor Gray
            $runIndex++
        }
        Write-Host ""
        $index++
    }
}

# Show failed tests details
if ($failedTests.Count -gt 0) {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  FAILED TESTS (Chi tiet)" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    
    $index = 1
    foreach ($test in $failedTests) {
        Write-Host "$index. $($test.Name)" -ForegroundColor Red
        Write-Host "   Runs: $($test.NumRuns)" -ForegroundColor White
        Write-Host "   Statuses: $($test.Statuses)" -ForegroundColor White
        
        if ($test.NumRuns -gt 1) {
            $runIndex = 1
            foreach ($result in $test.Results) {
                Write-Host "      Run $runIndex`: [X] $($result.Status.ToUpper()) ($([math]::Round($result.Duration, 2))s)" -ForegroundColor Red
                $runIndex++
            }
        }
        Write-Host ""
        $index++
    }
}

# Export to CSV
$csvFilename = "analyzed_results_14-11-2025.csv"
$csvData = @()

foreach ($test in $passedTests) {
    $csvData += [PSCustomObject]@{
        Category = "Passed"
        TestName = $test.Name
        Runs = $test.NumRuns
        Statuses = $test.Statuses
    }
}

foreach ($test in $flakyTests) {
    $csvData += [PSCustomObject]@{
        Category = "Flaky"
        TestName = $test.Name
        Runs = $test.NumRuns
        Statuses = $test.Statuses
    }
}

foreach ($test in $failedTests) {
    $csvData += [PSCustomObject]@{
        Category = "Failed"
        TestName = $test.Name
        Runs = $test.NumRuns
        Statuses = $test.Statuses
    }
}

$csvData | Export-Csv -Path $csvFilename -NoTypeInformation -Encoding UTF8

Write-Host "========================================" -ForegroundColor Green
Write-Host "Da export ra file: $csvFilename" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verification
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Expected: 66 passed, 4 flaky, 1 failed" -ForegroundColor Yellow
Write-Host "Actual:   $($passedTests.Count) passed, $($flakyTests.Count) flaky, $($failedTests.Count) failed" -ForegroundColor White
Write-Host ""

if ($passedTests.Count -eq 66 -and $flakyTests.Count -eq 4 -and $failedTests.Count -eq 1) {
    Write-Host "MATCH! Ket qua dung voi expected!" -ForegroundColor Green
}
else {
    Write-Host "Ket qua khac voi expected!" -ForegroundColor Yellow
    $diffPassed = $passedTests.Count - 66
    $diffFlaky = $flakyTests.Count - 4
    $diffFailed = $failedTests.Count - 1
    
    if ($diffPassed -ne 0) {
        Write-Host "   Passed: $($diffPassed.ToString('+#;-#;0'))" -ForegroundColor $(if ($diffPassed -gt 0) { 'Yellow' } else { 'Red' })
    }
    if ($diffFlaky -ne 0) {
        Write-Host "   Flaky: $($diffFlaky.ToString('+#;-#;0'))" -ForegroundColor $(if ($diffFlaky -gt 0) { 'Yellow' } else { 'Red' })
    }
    if ($diffFailed -ne 0) {
        Write-Host "   Failed: $($diffFailed.ToString('+#;-#;0'))" -ForegroundColor $(if ($diffFailed -gt 0) { 'Yellow' } else { 'Red' })
    }
}
Write-Host ""

