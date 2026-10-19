from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..crud import notify
from ..auth import get_current_user, require_roles

router = APIRouter(prefix="/leaves", tags=["Leaves"])

@router.post("/", response_model=schemas.LeaveOut, status_code=201)
def apply_leave(data: schemas.LeaveIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    employee = db.get(models.Employee, data.employee_id)
    if not employee: raise HTTPException(404, "Employee not found")
    if user.role == "EMPLOYEE" and employee.user_id != user.id: raise HTTPException(403, "You can only apply for yourself")
    row = models.Leave(**data.model_dump(), status="PENDING")
    db.add(row); db.commit(); db.refresh(row)
    if employee.user_id: notify(db, employee.user_id, "Leave application received", f"Your leave request #{row.id} is pending review.")
    db.commit()
    return row

@router.get("/", response_model=list[schemas.LeaveOut])
def list_leaves(db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Leave)
    if user.role == "EMPLOYEE":
        employee = db.query(models.Employee).filter_by(user_id=user.id).first()
        if not employee: return []
        q = q.filter_by(employee_id=employee.id)
    return q.order_by(models.Leave.created_at.desc()).all()

@router.patch("/{leave_id}/decision", response_model=schemas.LeaveOut)
def decide_leave(leave_id: int, decision: str, db: Session = Depends(get_db), user=Depends(require_roles("HR", "ADMIN"))):
    if decision not in {"APPROVED", "REJECTED"}: raise HTTPException(400, "decision must be APPROVED or REJECTED")
    row = db.get(models.Leave, leave_id)
    if not row: raise HTTPException(404, "Leave request not found")
    row.status = decision
    employee = db.get(models.Employee, row.employee_id)
    if employee and employee.user_id:
        notify(db, employee.user_id, f"Leave {decision.lower()}", f"Your leave request #{row.id} was {decision.lower()}.")
    db.commit(); db.refresh(row); return row
