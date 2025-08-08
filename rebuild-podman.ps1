# Rebuild script for Cosmic Explorer containers using Podman (PowerShell)
# Usage: .\rebuild-podman.ps1 [service_name]
# Examples:
#   .\rebuild-podman.ps1 data_service    # Rebuild only data service
#   .\rebuild-podman.ps1 desktop_app     # Rebuild only desktop app
#   .\rebuild-podman.ps1 web_portal      # Rebuild only web portal
#   .\rebuild-podman.ps1                 # Rebuild all services

param(
    [string]$ServiceName = ""
)

Write-Host "🚀 Cosmic Explorer Podman Rebuild Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

if ($ServiceName -eq "") {
    Write-Host "Rebuilding all services..." -ForegroundColor Yellow
    podman-compose build
    Write-Host "✅ All services rebuilt successfully!" -ForegroundColor Green
} else {
    Write-Host "Rebuilding service: $ServiceName" -ForegroundColor Yellow
    podman-compose build $ServiceName
    Write-Host "✅ Service '$ServiceName' rebuilt successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "To run the services:" -ForegroundColor Cyan
Write-Host "  podman-compose up [$ServiceName]" -ForegroundColor White
Write-Host ""
Write-Host "To run without rebuilding:" -ForegroundColor Cyan
Write-Host "  podman-compose run --rm [$ServiceName]" -ForegroundColor White
Write-Host ""
Write-Host "Alternative Podman commands:" -ForegroundColor Cyan
Write-Host "  podman build -f Containerfile.data -t cosmic_explorer_data ." -ForegroundColor White
Write-Host "  podman build -f Containerfile.desktop -t cosmic_explorer_desktop ." -ForegroundColor White
Write-Host "  podman build -f Containerfile.web -t cosmic_explorer_web ." -ForegroundColor White
Write-Host ""
Write-Host "For Windows compatibility, use:" -ForegroundColor Cyan
Write-Host "  podman-compose -f podman-compose-windows.yml build" -ForegroundColor White
Write-Host ""
Write-Host "To test individual builds:" -ForegroundColor Cyan
Write-Host "  podman build --no-cache -f Containerfile.data -t cosmic_explorer_data ." -ForegroundColor White
