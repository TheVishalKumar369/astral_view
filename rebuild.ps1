# Rebuild script for Cosmic Explorer containers (PowerShell)
# Usage: .\rebuild.ps1 [service_name]
# Examples:
#   .\rebuild.ps1 data_service    # Rebuild only data service
#   .\rebuild.ps1 desktop_app     # Rebuild only desktop app
#   .\rebuild.ps1 web_portal      # Rebuild only web portal
#   .\rebuild.ps1                 # Rebuild all services

param(
    [string]$ServiceName = ""
)

Write-Host "🚀 Cosmic Explorer Rebuild Script" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

if ($ServiceName -eq "") {
    Write-Host "Rebuilding all services..." -ForegroundColor Yellow
    docker compose build
    Write-Host "✅ All services rebuilt successfully!" -ForegroundColor Green
} else {
    Write-Host "Rebuilding service: $ServiceName" -ForegroundColor Yellow
    docker compose build $ServiceName
    Write-Host "✅ Service '$ServiceName' rebuilt successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "To run the services:" -ForegroundColor Cyan
Write-Host "  docker compose up [$ServiceName]" -ForegroundColor White
Write-Host ""
Write-Host "To run without rebuilding:" -ForegroundColor Cyan
Write-Host "  docker compose run --rm [$ServiceName]" -ForegroundColor White 