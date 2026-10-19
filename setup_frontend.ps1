$ErrorActionPreference = 'Stop'
Set-Location "$PSScriptRoot\frontend"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  Write-Host "Node.js/npm was not found. Install the current Node.js LTS version, reopen PowerShell, and run this script again." -ForegroundColor Red
  exit 1
}
npm install
Write-Host "Frontend setup complete. Run .\run_frontend.ps1 from the HRMS folder." -ForegroundColor Green
