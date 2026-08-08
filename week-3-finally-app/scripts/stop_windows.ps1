$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $ProjectRoot

Write-Host "=== Stopping FinAlly Trading Workstation ===" -ForegroundColor Cyan

if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $ComposeCmd = "docker-compose"
} else {
    $ComposeCmd = "docker compose"
}

Invoke-Expression "$ComposeCmd down"
Write-Host "FinAlly containers stopped successfully." -ForegroundColor Green
