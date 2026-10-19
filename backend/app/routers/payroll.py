from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..crud import notify
from ..auth import get_current_user, require_roles

router = APIRouter(prefix="/payroll", tags=["Payroll"])

@router.post("/", response_model=schemas.PayrollOut, status_code=201)
def generate_payroll(data: schemas.PayrollIn, db: Session = Depends(get_db), user=Depends(require_roles("HR", "ADMIN"))):
    employee = db.get(models.Employee, data.employee_id)
    if not employee: raise HTTPException(404, "Employee not found")
    if db.query(models.Payroll).filter_by(employee_id=data.employee_id, month=data.month).first():
        raise HTTPException(409, "Payroll already exists for this employee and month")
    row = models.Payroll(**data.model_dump(), net_salary=data.basic_salary - data.deductions + data.bonus)
    db.add(row)
    if employee.user_id: notify(db, employee.user_id, "Payroll generated", f"Your payslip for {data.month} is available.")
    db.commit(); db.refresh(row); return row

@router.get("/", response_model=list[schemas.PayrollOut])
def list_payroll(employee_id: int | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Payroll)
    if user.role == "EMPLOYEE":
        employee = db.query(models.Employee).filter_by(user_id=user.id).first()
        if not employee: return []
        q = q.filter_by(employee_id=employee.id)
    elif employee_id:
        q = q.filter_by(employee_id=employee_id)
    return q.order_by(models.Payroll.month.desc()).all()
