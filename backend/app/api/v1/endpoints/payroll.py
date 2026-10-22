from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.employee import Employee
from app.models.payroll import Payroll
from app.models.notification import Notification
from app.schemas.payroll import PayrollCreate
router = APIRouter(prefix="/payroll", tags=["Payroll"])

@router.post("/")
def generate_payroll(data: PayrollCreate, db: Session = Depends(get_db), user: User = Depends(require_roles("HR", "ADMIN"))):
    emp = db.query(Employee).filter_by(id=data.employee_id).first()
    if not emp: raise HTTPException(404, "Employee not found")
    if db.query(Payroll).filter_by(employee_id=data.employee_id, month=data.month).first(): raise HTTPException(409, "Payroll already exists for this employee and month")
    net = data.basic_salary + data.allowances + data.bonus - data.deductions
    if net < 0: raise HTTPException(400, "Deductions cannot exceed gross salary")
    row = Payroll(employee_id=data.employee_id, basic_salary=data.basic_salary, allowances=data.allowances, deductions=data.deductions, bonus=data.bonus, net_salary=net, month=data.month)
    db.add(row); db.flush()
    db.add(Notification(user_id=emp.user_id, title="Payroll generated", message=f"Your payslip for {data.month} is available."))
    db.commit(); db.refresh(row)
    return row

@router.get("/my")
def my_payroll(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter_by(user_id=user.id).first()
    if not emp: raise HTTPException(404, "Employee profile not found")
    return db.query(Payroll).filter_by(employee_id=emp.id).order_by(Payroll.month.desc()).all()

@router.get("/")
def all_payroll(db: Session = Depends(get_db), _: User = Depends(require_roles("HR", "ADMIN"))):
    return db.query(Payroll).order_by(Payroll.month.desc()).all()
