from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.models.employee import Employee
router = APIRouter(prefix="/employees", tags=["Employees"])

class EmployeeInput(BaseModel):
    user_id: int
    full_name: str = Field(min_length=2)
    designation: str = "Employee"
    department: str = "General"
    joining_date: date = date.today()
    salary: float = Field(default=0, ge=0)
    status: str = Field(default="ACTIVE", pattern="^(ACTIVE|INACTIVE)$")

@router.get("/")
def list_employees(q: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_roles("HR", "ADMIN"))):
    query = db.query(Employee)
    if q: query = query.filter(Employee.full_name.ilike(f"%{q}%"))
    return query.order_by(Employee.id).all()

@router.post("/")
def create_employee(data: EmployeeInput, db: Session = Depends(get_db), _: User = Depends(require_roles("HR", "ADMIN"))):
    if not db.query(User).filter_by(id=data.user_id).first(): raise HTTPException(404, "User not found")
    if db.query(Employee).filter_by(user_id=data.user_id).first(): raise HTTPException(409, "Employee profile already exists")
    row = Employee(**data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row

@router.put("/{employee_id}")
def update_employee(employee_id: int, data: EmployeeInput, db: Session = Depends(get_db), _: User = Depends(require_roles("HR", "ADMIN"))):
    row = db.query(Employee).filter_by(id=employee_id).first()
    if not row: raise HTTPException(404, "Employee not found")
    for key, value in data.model_dump().items(): setattr(row, key, value)
    db.commit(); db.refresh(row); return row
