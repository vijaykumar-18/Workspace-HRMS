import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app import models
from app.api.v1.api import api_router
from app.models.user import User
from app.models.leave import LeavePolicy
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
app = FastAPI(title="WorkSphere HRMS API", version="1.0.0", description="WorkSphere HR Management System - Phase 1 & 2")
origins = [os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"), "http://127.0.0.1:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")

def seed_defaults():
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(username="admin", email="admin@worksphere.local", hashed_password=hash_password("Admin123!"), role="ADMIN"))
        defaults = [("SICK", 10), ("CASUAL", 12), ("PAID", 15)]
        for kind, days in defaults:
            if not db.query(LeavePolicy).filter_by(leave_type=kind).first():
                db.add(LeavePolicy(leave_type=kind, total_days_allowed=days))
        db.commit()
    finally:
        db.close()
seed_defaults()

@app.get("/")
def root():
    return {"message": "WorkSphere HRMS API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
