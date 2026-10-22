from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import Leave, LeaveBalance
from app.models.payroll import Payroll
from app.models.notification import Notification
router = APIRouter(prefix="/portal", tags=["Employee Self-Service"])

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter_by(user_id=user.id).first()
    if not emp: raise HTTPException(404, "Employee profile not found")
    return {
        "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
        "employee": emp,
        "attendance": db.query(Attendance).filter_by(employee_id=emp.id).order_by(Attendance.date.desc()).limit(10).all(),
        "leaves": db.query(Leave).filter_by(employee_id=emp.id).order_by(Leave.id.desc()).limit(10).all(),
        "leave_balances": db.query(LeaveBalance).filter_by(employee_id=emp.id).all(),
        "payroll": db.query(Payroll).filter_by(employee_id=emp.id).order_by(Payroll.month.desc()).limit(6).all(),
        "notifications": db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(10).all()
    }
