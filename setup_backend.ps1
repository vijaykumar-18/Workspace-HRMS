$ErrorActionPreference = 'Stop'
Set-Location "$PSScriptRoot\backend"
if (-not (Test-Path ".venv")) { py -m venv .venv }
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "Backend setup complete. Review backend\.env, then run .\run_backend.ps1 from the HRMS folder." -ForegroundColor Green
