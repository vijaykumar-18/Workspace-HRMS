from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user, require_roles

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/check-in", response_model=schemas.AttendanceOut)
def check_in(data: schemas.AttendanceIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    employee = db.get(models.Employee, data.employee_id)
    if not employee: raise HTTPException(404, "Employee not found")
    if user.role == "EMPLOYEE" and employee.user_id != user.id: raise HTTPException(403, "You can only check in for yourself")
    today = date.today()
    row = db.query(models.Attendance).filter_by(employee_id=data.employee_id, date=today).first()
    if row and row.check_in: raise HTTPException(409, "Already checked in today")
    if not row:
        row = models.Attendance(employee_id=data.employee_id, date=today, status="PRESENT")
        db.add(row)
    row.check_in = datetime.now(); row.status = "PRESENT"
    db.commit(); db.refresh(row); return row

@router.post("/check-out/{attendance_id}", response_model=schemas.AttendanceOut)
def check_out(attendance_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.get(models.Attendance, attendance_id)
    if not row: raise HTTPException(404, "Attendance record not found")
    employee = db.get(models.Employee, row.employee_id)
    if user.role == "EMPLOYEE" and (not employee or employee.user_id != user.id): raise HTTPException(403, "You can only check out for yourself")
    if not row.check_in: raise HTTPException(400, "Check-in is required first")
    if row.check_out: raise HTTPException(409, "Already checked out")
    row.check_out = datetime.now()
    hours = (row.check_out - row.check_in).total_seconds() / 3600
    row.status = "HALF_DAY" if hours < 4 else "PRESENT"
    db.commit(); db.refresh(row); return row

@router.get("/", response_model=list[schemas.AttendanceOut])
def history(employee_id: int | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Attendance)
    if employee_id: q = q.filter_by(employee_id=employee_id)
    if user.role == "EMPLOYEE":
        employee = db.query(models.Employee).filter_by(user_id=user.id).first()
        if not employee: return []
        q = q.filter_by(employee_id=employee.id)
    return q.order_by(models.Attendance.date.desc()).all()

@router.post("/absent/{employee_id}")
def mark_absent(employee_id: int, db: Session = Depends(get_db), user=Depends(require_roles("HR", "ADMIN"))):
    if not db.get(models.Employee, employee_id): raise HTTPException(404, "Employee not found")
    today = date.today()
    if db.query(models.Attendance).filter_by(employee_id=employee_id, date=today).first():
        raise HTTPException(409, "Attendance already exists for today")
    row = models.Attendance(employee_id=employee_id, date=today, status="ABSENT")
    db.add(row); db.commit(); db.refresh(row); return row

@router.get("/hours/{attendance_id}")
def working_hours(attendance_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.get(models.Attendance, attendance_id)
    if not row: raise HTTPException(404, "Attendance record not found")
    hours = round((row.check_out - row.check_in).total_seconds()/3600, 2) if row.check_in and row.check_out else None
    return {"attendance_id": row.id, "working_hours": hours}
