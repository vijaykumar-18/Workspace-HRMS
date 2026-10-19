$ErrorActionPreference = 'Stop'
Set-Location "$PSScriptRoot\frontend"
if (-not (Test-Path "node_modules")) {
  Write-Host "Frontend packages not found. Run .\setup_frontend.ps1 first from the HRMS folder." -ForegroundColor Yellow
  exit 1
}
npm run dev
