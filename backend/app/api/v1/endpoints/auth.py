from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.models.employee import Employee

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterInput(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8)

class LoginInput(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(data: RegisterInput, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == data.username) | (User.email == data.email)).first():
        raise HTTPException(409, "Username or email already exists")
    user = User(username=data.username, email=data.email, hashed_password=hash_password(data.password), role="EMPLOYEE")
    db.add(user); db.commit(); db.refresh(user)
    employee = Employee(user_id=user.id, full_name=data.username)
    db.add(employee); db.commit()
    return {"message": "Registration successful", "id": user.id, "role": user.role}

@router.post("/login")
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password) or not user.is_active:
        raise HTTPException(401, "Invalid username or password")
    return {"access_token": create_access_token(user), "token_type": "bearer", "role": user.role, "username": user.username}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role, "is_active": user.is_active}
