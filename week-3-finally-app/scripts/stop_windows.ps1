$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "Stopping FinAlly AI Trading Workstation..." -ForegroundColor Yellow
docker compose down

Write-Host "FinAlly container stopped. SQLite database persisted in db/ directory." -ForegroundColor Green
