from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.employee import Employee
from app.models.leave import Leave, LeavePolicy, LeaveBalance
from app.models.notification import Notification
from app.schemas.leave import LeaveCreate, LeaveDecision
router = APIRouter(prefix="/leaves", tags=["Leaves"])

def employee_for(db, user):
    emp = db.query(Employee).filter_by(user_id=user.id).first()
    if not emp: raise HTTPException(404, "Employee profile not found")
    return emp

@router.post("/")
def apply_leave(data: LeaveCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.end_date < data.start_date or data.start_date < date.today(): raise HTTPException(400, "Invalid leave date range")
    emp = employee_for(db, user)
    days = (data.end_date - data.start_date).days + 1
    balance = db.query(LeaveBalance).filter_by(employee_id=emp.id, leave_type=data.leave_type).first()
    policy = db.query(LeavePolicy).filter_by(leave_type=data.leave_type).first()
    if not balance and policy:
        balance = LeaveBalance(employee_id=emp.id, leave_type=data.leave_type, remaining_days=policy.total_days_allowed); db.add(balance); db.flush()
    if balance and days > balance.remaining_days: raise HTTPException(400, f"Insufficient {data.leave_type} leave balance")
    row = Leave(employee_id=emp.id, leave_type=data.leave_type, start_date=data.start_date, end_date=data.end_date, reason=data.reason)
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.get("/my")
def my_leaves(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = employee_for(db, user)
    return db.query(Leave).filter_by(employee_id=emp.id).order_by(Leave.id.desc()).all()

@router.get("/balances")
def my_balances(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = employee_for(db, user)
    return db.query(LeaveBalance).filter_by(employee_id=emp.id).all()

@router.get("/")
def all_leaves(db: Session = Depends(get_db), _: User = Depends(require_roles("HR", "ADMIN"))):
    return db.query(Leave).order_by(Leave.id.desc()).all()

@router.patch("/{leave_id}/decision")
def decide_leave(leave_id: int, data: LeaveDecision, db: Session = Depends(get_db), user: User = Depends(require_roles("HR", "ADMIN"))):
    row = db.query(Leave).filter_by(id=leave_id).first()
    if not row: raise HTTPException(404, "Leave request not found")
    if row.status != "PENDING": raise HTTPException(409, "This request has already been processed")
    if data.status == "APPROVED":
        days = (row.end_date - row.start_date).days + 1
        balance = db.query(LeaveBalance).filter_by(employee_id=row.employee_id, leave_type=row.leave_type).first()
        if not balance:
            policy = db.query(LeavePolicy).filter_by(leave_type=row.leave_type).first()
            if not policy: raise HTTPException(400, "Leave policy is not configured")
            balance = LeaveBalance(employee_id=row.employee_id, leave_type=row.leave_type, remaining_days=policy.total_days_allowed); db.add(balance); db.flush()
        if balance.remaining_days < days: raise HTTPException(400, "Insufficient balance to approve leave")
        balance.remaining_days -= days
    row.status = data.status
    employee = db.query(Employee).filter_by(id=row.employee_id).first()
    if employee:
        db.add(Notification(user_id=employee.user_id, title="Leave request update", message=f"Your leave request was {data.status.lower()}."))
    db.commit()
    return {"message": f"Leave {data.status.lower()}", "remaining_days": balance.remaining_days if data.status == "APPROVED" else None}

@router.get("/policies")
def policies(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(LeavePolicy).all()
