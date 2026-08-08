$ErrorActionPreference = "Stop"

# Get script parent directory (project root)
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $ProjectRoot

Write-Host "=== Starting FinAlly Trading Workstation ===" -ForegroundColor Cyan

# 1. Check Docker status
try {
    docker info | Out-Null
} catch {
    Write-Host "Error: Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Determine docker compose variant
if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $ComposeCmd = "docker-compose"
} else {
    $ComposeCmd = "docker compose"
}

# 2. Ensure db folder exists on host
if (-not (Test-Path -Path "db")) {
    New-Item -ItemType Directory -Path "db" | Out-Null
}

# 3. Build and launch container
Write-Host "Building and starting Docker container with $ComposeCmd..." -ForegroundColor Yellow
Invoke-Expression "$ComposeCmd up -d --build"

# 4. Poll health endpoint
Write-Host "Waiting for FinAlly workstation to become ready..." -ForegroundColor Yellow
$MaxAttempts = 30
$Attempt = 0
$Ready = $false

while ($Attempt -lt $MaxAttempts) {
    try {
        $Response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($Response.status -eq "ok") {
            $Ready = $true
            break
        }
    } catch {
        # Server not ready yet
    }
    $Attempt++
    Start-Sleep -Seconds 1
}

if ($Ready) {
    Write-Host "FinAlly Workstation is ready at http://localhost:8000" -ForegroundColor Green
    Start-Process "http://localhost:8000"
} else {
    Write-Host "Error: FinAlly Workstation failed to respond within 30 seconds." -ForegroundColor Red
    Invoke-Expression "$ComposeCmd logs --tail=50"
    exit 1
}
