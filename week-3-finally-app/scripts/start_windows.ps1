param (
    [switch]$Build
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

if (-not (Test-Path "db")) {
    New-Item -ItemType Directory -Path "db" | Out-Null
}

$BuildArg = ""
if ($Build) {
    $BuildArg = "--build"
}

Write-Host "Starting FinAlly AI Trading Workstation..." -ForegroundColor Green
docker compose up -d $BuildArg

Write-Host "FinAlly is running!" -ForegroundColor Green
Write-Host "Access the application at: http://localhost:8000" -ForegroundColor Cyan

Start-Process "http://localhost:8000"
