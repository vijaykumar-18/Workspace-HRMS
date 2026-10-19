from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user, require_roles

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=list[schemas.EmployeeOut])
def list_employees(search: str | None = Query(None), department: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Employee)
    if search:
        q = q.filter(models.Employee.full_name.ilike(f"%{search}%"))
    if department:
        q = q.filter(models.Employee.department.ilike(f"%{department}%"))
    return q.order_by(models.Employee.id.desc()).all()

@router.post("/", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(data: schemas.EmployeeIn, db: Session = Depends(get_db), user=Depends(require_roles("HR", "ADMIN"))):
    if data.user_id and not db.get(models.User, data.user_id):
        raise HTTPException(404, "Linked user not found")
    if data.user_id and db.query(models.Employee).filter_by(user_id=data.user_id).first():
        raise HTTPException(409, "This user already has an employee profile")
    obj = models.Employee(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = db.get(models.Employee, employee_id)
    if not obj: raise HTTPException(404, "Employee not found")
    return obj

@router.put("/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(employee_id: int, data: schemas.EmployeeIn, db: Session = Depends(get_db), user=Depends(require_roles("HR", "ADMIN"))):
    obj = db.get(models.Employee, employee_id)
    if not obj: raise HTTPException(404, "Employee not found")
    for key, value in data.model_dump().items(): setattr(obj, key, value)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), user=Depends(require_roles("ADMIN"))):
    obj = db.get(models.Employee, employee_id)
    if not obj: raise HTTPException(404, "Employee not found")
    obj.status = "INACTIVE"; db.commit()
    return {"message": "Employee marked inactive"}
