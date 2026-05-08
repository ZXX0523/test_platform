# Docker Deploy Script
# Usage: .\deploy.ps1

Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[0] Git Pull" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
git stash 2>$null
git pull
git stash pop 2>$null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[1] Stop Old Container" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker stop testflask 2>$null
docker rm testflask 2>$null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[2] Build New Image" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker build -t testflask:latest .

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[3] Start New Container" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker run -d --name testflask -p 8088:8003 testflask:latest

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[4] Check Container Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Start-Sleep -Seconds 3
docker ps | Select-String "testflask"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Deploy Complete!" -ForegroundColor Green
Write-Host "URL: http://localhost:8088/dm_gubi/py/dm_gubi" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green