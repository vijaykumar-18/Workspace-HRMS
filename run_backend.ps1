$ErrorActionPreference = 'Stop'
Set-Location "$PSScriptRoot\backend"
if (-not (Test-Path ".venv\Scripts\python.exe")) {
  Write-Host "Backend environment not found. Run .\setup_backend.ps1 first from the HRMS folder." -ForegroundColor Yellow
  exit 1
}
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload
