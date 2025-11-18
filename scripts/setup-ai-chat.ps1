#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup và khởi động AI-Chat feature
.DESCRIPTION
    Script này sẽ:
    1. Kiểm tra file .env
    2. Yêu cầu OpenAI API key nếu chưa có
    3. Khởi động backend services
    4. Kiểm tra services đã sẵn sàng
#>

$ErrorActionPreference = "Stop"

# Colors
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Info "==================================="
Write-Info "  QUALIFY.AI - AI-Chat Setup"
Write-Info "==================================="
Write-Host ""

# Check Docker
Write-Info "Checking Docker..."
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
    Write-Success "✓ Docker is installed"
} catch {
    Write-Error "✗ Docker is not installed or not running"
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Navigate to docker-compose directory
$dockerComposeDir = Join-Path $PSScriptRoot ".." "infrastructure" "docker-compose"
if (-not (Test-Path $dockerComposeDir)) {
    Write-Error "✗ Docker compose directory not found: $dockerComposeDir"
    exit 1
}

Set-Location $dockerComposeDir
Write-Success "✓ Found docker-compose directory"

# Check .env file
$envFile = Join-Path $dockerComposeDir ".env"
$needsSetup = $false

if (-not (Test-Path $envFile)) {
    Write-Warning "! .env file not found"
    $needsSetup = $true
} else {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -notmatch "OPENAI_API_KEY=sk-") {
        Write-Warning "! OpenAI API key not configured properly in .env"
        $needsSetup = $true
    } else {
        Write-Success "✓ .env file exists with API key"
    }
}

# Setup .env if needed
if ($needsSetup) {
    Write-Host ""
    Write-Info "Let's setup your .env file..."
    Write-Host ""
    Write-Host "You need an OpenAI API key to use AI features."
    Write-Host "Get one at: https://platform.openai.com/api-keys"
    Write-Host ""
    
    $apiKey = Read-Host "Enter your OpenAI API key (starts with sk-proj- or sk-)"
    
    if ($apiKey -notmatch "^sk-") {
        Write-Error "✗ Invalid API key format. Must start with 'sk-'"
        exit 1
    }
    
    # Create .env file
    $envContent = @"
# OpenAI API Key for AI features
OPENAI_API_KEY=$apiKey
"@
    
    Set-Content -Path $envFile -Value $envContent
    Write-Success "✓ Created .env file"
}

# Check if services are already running
Write-Host ""
Write-Info "Checking existing services..."
$runningContainers = docker ps --filter "name=qualify" --format "{{.Names}}"

if ($runningContainers) {
    Write-Info "Found running containers:"
    $runningContainers | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
    $restart = Read-Host "Do you want to restart services? (y/N)"
    
    if ($restart -eq "y" -or $restart -eq "Y") {
        Write-Info "Stopping existing services..."
        docker-compose down
        Write-Success "✓ Services stopped"
    }
}

# Start services
Write-Host ""
Write-Info "Starting backend services..."
Write-Host "This may take a few minutes on first run..."
Write-Host ""

# Start core services first
Write-Info "Starting database and cache..."
docker-compose up -d postgres redis minio

# Wait for health checks
Write-Info "Waiting for services to be healthy..."
Start-Sleep -Seconds 10

# Start application services
Write-Info "Starting application services..."
docker-compose up -d ai-analysis analytics report-aggregator auth-service nginx

# Wait for services to be ready
Write-Info "Waiting for services to start..."
Start-Sleep -Seconds 15

# Check services status
Write-Host ""
Write-Info "Checking services status..."
$services = @(
    @{Name="qualify-postgres"; Port=5432},
    @{Name="qualify-redis"; Port=6379},
    @{Name="qualify-ai"; Port=8003},
    @{Name="qualify-nginx"; Port=8000}
)

$allHealthy = $true
foreach ($service in $services) {
    $status = docker ps --filter "name=$($service.Name)" --format "{{.Status}}"
    if ($status -match "Up") {
        Write-Success "✓ $($service.Name) is running"
    } else {
        Write-Error "✗ $($service.Name) is not running"
        $allHealthy = $false
    }
}

if (-not $allHealthy) {
    Write-Host ""
    Write-Warning "Some services failed to start. Check logs with:"
    Write-Host "  docker-compose logs ai-analysis"
    Write-Host "  docker-compose logs nginx"
    exit 1
}

# Test API endpoint
Write-Host ""
Write-Info "Testing API endpoint..."
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/ai/health" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "✓ AI service is responding"
    }
} catch {
    Write-Warning "! AI service might not be ready yet. You can check with:"
    Write-Host "  curl http://localhost:8000/api/ai/health"
}

# Success message
Write-Host ""
Write-Success "==================================="
Write-Success "  Setup Complete! ✓"
Write-Success "==================================="
Write-Host ""
Write-Info "Services are running:"
Write-Host "  • AI Analysis Service: http://localhost:8003"
Write-Host "  • API Gateway (Nginx): http://localhost:8000"
Write-Host "  • Frontend: http://localhost:3000"
Write-Host ""
Write-Info "You can now use AI-Chat feature on the dashboard!"
Write-Host ""
Write-Info "Useful commands:"
Write-Host "  • View logs: docker-compose logs -f ai-analysis"
Write-Host "  • Stop services: docker-compose down"
Write-Host "  • Restart: docker-compose restart ai-analysis"
Write-Host ""

# Ask if user wants to see logs
$showLogs = Read-Host "Do you want to see AI service logs? (y/N)"
if ($showLogs -eq "y" -or $showLogs -eq "Y") {
    Write-Info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f ai-analysis
}

