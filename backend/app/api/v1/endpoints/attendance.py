from datetime import datetime, date, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance
router = APIRouter(prefix="/attendance", tags=["Attendance"])

def own_employee(db, user):
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee: raise HTTPException(404, "Employee profile not found")
    return employee

@router.post("/check-in")
def check_in(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = own_employee(db, user); today = date.today()
    row = db.query(Attendance).filter_by(employee_id=emp.id, date=today).first()
    if row and row.check_in: raise HTTPException(409, "You have already checked in today")
    now = datetime.now()
    if not row:
        row = Attendance(employee_id=emp.id, date=today)
        db.add(row)
    row.check_in = now
    row.status = "PRESENT"
    row.is_late = now.time() > time(9, 30)
    db.commit(); db.refresh(row)
    return {"message": "Checked in", "check_in": row.check_in, "is_late": row.is_late}

@router.post("/check-out")
def check_out(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = own_employee(db, user); row = db.query(Attendance).filter_by(employee_id=emp.id, date=date.today()).first()
    if not row or not row.check_in: raise HTTPException(400, "Check in before checking out")
    if row.check_out: raise HTTPException(409, "You have already checked out today")
    row.check_out = datetime.now()
    row.working_hours = round((row.check_out - row.check_in).total_seconds() / 3600, 2)
    if row.working_hours < 4: row.status = "HALF_DAY"
    db.commit()
    return {"message": "Checked out", "working_hours": row.working_hours}

@router.get("/my")
def my_attendance(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = own_employee(db, user)
    return db.query(Attendance).filter_by(employee_id=emp.id).order_by(Attendance.date.desc()).all()

@router.get("/")
def all_attendance(db: Session = Depends(get_db), _: User = Depends(require_roles("HR", "ADMIN"))):
    return db.query(Attendance).order_by(Attendance.date.desc()).all()
