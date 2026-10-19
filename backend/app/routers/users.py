from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import hash_password, verify_password, create_access_token, get_current_user, require_roles

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.TokenOut, status_code=201)
def register(data: schemas.RegisterIn, db: Session = Depends(get_db)):
    if db.query(models.User).filter((models.User.username == data.username) | (models.User.email == data.email)).first():
        raise HTTPException(409, "Username or email already exists")
    user = models.User(username=data.username, email=data.email, hashed_password=hash_password(data.password), role="EMPLOYEE")
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token(user), "user": user}

@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect username or password")
    return {"access_token": create_access_token(user), "user": user}

@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user

@router.patch("/users/{user_id}/role")
def update_role(user_id: int, role: str, db: Session = Depends(get_db), admin: models.User = Depends(require_roles("ADMIN"))):
    if role not in {"EMPLOYEE", "HR", "ADMIN"}:
        raise HTTPException(400, "Invalid role")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.role = role; db.commit()
    return {"message": "Role updated", "user_id": user.id, "role": user.role}
