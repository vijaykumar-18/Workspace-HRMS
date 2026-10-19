from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models
from ..auth import require_roles

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user=Depends(require_roles("HR", "ADMIN"))):
    employees = db.query(models.Employee)
    total = employees.count()
    active = employees.filter_by(status="ACTIVE").count()
    attendance = db.query(models.Attendance.status, func.count(models.Attendance.id)).group_by(models.Attendance.status).all()
    leaves = db.query(models.Leave.status, func.count(models.Leave.id)).group_by(models.Leave.status).all()
    payroll_total = db.query(func.coalesce(func.sum(models.Payroll.net_salary), 0)).scalar()
    return {
        "total_employees": total,
        "active_employees": active,
        "attendance_summary": {status: count for status, count in attendance},
        "leave_summary": {status: count for status, count in leaves},
        "total_payroll_amount": float(payroll_total or 0),
    }
