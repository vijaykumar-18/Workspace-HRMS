from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_roles, hash_password
from app.models.user import User
router = APIRouter(prefix="/admin", tags=["Admin"])

class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(EMPLOYEE|HR|ADMIN)$")

class UserUpdate(BaseModel):
    role: str | None = Field(default=None, pattern="^(EMPLOYEE|HR|ADMIN)$")
    is_active: bool | None = None

@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))):
    return db.query(User).order_by(User.id).all()

@router.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))):
    if db.query(User).filter((User.username == data.username) | (User.email == data.email)).first():
        raise HTTPException(409, "Username or email already exists")
    user = User(username=data.username, email=data.email, hashed_password=hash_password(data.password), role=data.role)
    db.add(user); db.commit(); db.refresh(user)
    return {"id": user.id, "username": user.username, "role": user.role}

@router.patch("/users/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    if data.role is not None: user.role = data.role
    if data.is_active is not None: user.is_active = data.is_active
    db.commit()
    return {"message": "User updated"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current: User = Depends(require_roles("ADMIN"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    if user.id == current.id: raise HTTPException(400, "You cannot delete your own account")
    db.delete(user); db.commit()
    return {"message": "User deleted"}
