import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import users, employees, attendance, leaves, payroll, notifications, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="WorkSphere HRMS API", version="1.0.0", description="HR management API with JWT authentication and role-based access.")

origins = [item.strip() for item in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for router in [users.router, employees.router, attendance.router, leaves.router, payroll.router, notifications.router, dashboard.router]:
    app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "WorkSphere HRMS API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
