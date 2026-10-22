from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import Leave
from app.models.payroll import Payroll
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), _: User = Depends(require_roles("HR", "ADMIN"))):
    return {
        "total_employees": db.query(Employee).count(),
        "active_employees": db.query(Employee).filter_by(status="ACTIVE").count(),
        "attendance_records": db.query(Attendance).count(),
        "pending_leaves": db.query(Leave).filter_by(status="PENDING").count(),
        "approved_leaves": db.query(Leave).filter_by(status="APPROVED").count(),
        "payroll_records": db.query(Payroll).count(),
        "payroll_total": sum(x.net_salary for x in db.query(Payroll).all())
    }
