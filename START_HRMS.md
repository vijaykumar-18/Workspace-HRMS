# Start WorkSphere HRMS (Windows / VS Code)

## One-time setup

Open the extracted `HRMS` folder in VS Code. In the terminal, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\setup_backend.ps1
```

Then open a second terminal and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\setup_frontend.ps1
```

Before using the app, open `backend/.env` and replace `SECRET_KEY` with a long random secret. Do not share it or commit it to Git.

## Start it next time

Terminal 1:

```powershell
.\run_backend.ps1
```

Terminal 2:

```powershell
.\run_frontend.ps1
```

Open http://localhost:5173 for the React app and http://127.0.0.1:8000/docs for the API documentation.

Keep both terminals running. If PowerShell blocks scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in that terminal, then retry.

Public registration creates an EMPLOYEE role only. Follow the first-admin setup in README.md to test HR/Admin-only actions. This is a learning starter, not a production-ready HRMS; do not use real payroll or sensitive employee data without additional security review.
