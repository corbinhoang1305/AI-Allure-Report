#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Import Allure JSON results to database with complete retry information

.DESCRIPTION
    This script imports Allure test results from JSON files into the PostgreSQL database,
    preserving all retry information so flaky tests can be accurately detected.

.PARAMETER AllureFolder
    Path to the folder containing Allure result JSON files

.PARAMETER Date
    Date of the test run in YYYY-MM-DD format (optional, auto-detected from folder name)

.EXAMPLE
    .\import-allure-to-db.ps1 -AllureFolder "D:\allure-reports\14-11-2025"

.EXAMPLE
    .\import-allure-to-db.ps1 -AllureFolder "D:\allure-reports\14-11-2025" -Date "2025-11-14"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$AllureFolder = "D:\allure-reports\14-11-2025",
    
    [Parameter(Mandatory=$false)]
    [string]$Date = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ALLURE TO DATABASE IMPORTER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if folder exists
if (-not (Test-Path $AllureFolder)) {
    Write-Host "ERROR: Folder not found: $AllureFolder" -ForegroundColor Red
    exit 1
}

# Auto-detect date from folder name if not provided
if ([string]::IsNullOrEmpty($Date)) {
    $folderName = Split-Path $AllureFolder -Leaf
    if ($folderName -match '(\d{2})-(\d{2})-(\d{4})') {
        $Date = "$($matches[3])-$($matches[2])-$($matches[1])"
        Write-Host "Auto-detected date from folder name: $Date" -ForegroundColor Yellow
    } else {
        $Date = Get-Date -Format "yyyy-MM-dd"
        Write-Host "Using current date: $Date" -ForegroundColor Yellow
    }
}

Write-Host "Source folder: $AllureFolder" -ForegroundColor White
Write-Host "Target date:   $Date" -ForegroundColor White
Write-Host ""

# Check if Python is available
$pythonCmd = $null
foreach ($cmd in @('python', 'python3', 'py')) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "Found Python: $version" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if ($null -eq $pythonCmd) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python or use the native PowerShell importer." -ForegroundColor Yellow
    exit 1
}

# Check if psycopg2 is installed
Write-Host "Checking required Python packages..." -ForegroundColor Yellow
$packages = & $pythonCmd -m pip list 2>$null | Select-String "psycopg2"
if (-not $packages) {
    Write-Host "Installing psycopg2-binary..." -ForegroundColor Yellow
    & $pythonCmd -m pip install psycopg2-binary
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install psycopg2-binary" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting import..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the Python script
& $pythonCmd import_allure_to_db.py $AllureFolder $Date

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  IMPORT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Open dashboard: http://localhost:3000" -ForegroundColor White
    Write-Host "2. Check API: http://localhost:8000/api/analytics/dashboard" -ForegroundColor White
    Write-Host "3. View historical trend chart to see flaky tests" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  IMPORT FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}

