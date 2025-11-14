# Script to run migration and backfill Allure UUID
# Usage: .\scripts\run-migration-and-backfill.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration and Backfill Allure UUID" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run migration
Write-Host "Step 1: Running database migration..." -ForegroundColor Yellow
Write-Host ""

$migrationPath = "backend\shared"
if (-not (Test-Path $migrationPath)) {
    Write-Host "❌ Migration path not found: $migrationPath" -ForegroundColor Red
    exit 1
}

Push-Location $migrationPath

try {
    # Check if alembic is available
    $alembicCheck = Get-Command alembic -ErrorAction SilentlyContinue
    if (-not $alembicCheck) {
        Write-Host "❌ Alembic not found. Please install: pip install alembic" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Running: alembic upgrade head" -ForegroundColor Cyan
    alembic upgrade head
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migration completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Migration failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error running migration: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Step 2: Backfilling Allure UUID from JSON files..." -ForegroundColor Yellow
Write-Host ""

# Step 2: Run backfill script
$backfillScript = "scripts\backfill-allure-uuid.py"
if (-not (Test-Path $backfillScript)) {
    Write-Host "❌ Backfill script not found: $backfillScript" -ForegroundColor Red
    exit 1
}

# Check if Python is available
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "❌ Python not found. Please install Python or use python3" -ForegroundColor Red
    exit 1
}

try {
    Write-Host "Running: python $backfillScript" -ForegroundColor Cyan
    python $backfillScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backfill completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backfill completed with warnings (check output above)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error running backfill: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ All done! Refresh your browser to see Allure UUID" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

