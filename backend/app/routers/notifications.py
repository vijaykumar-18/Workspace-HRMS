from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=list[schemas.NotificationOut])
def list_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Notification).filter_by(user_id=user.id).order_by(models.Notification.created_at.desc()).all()

@router.patch("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.query(models.Notification).filter_by(id=notification_id, user_id=user.id).first()
    if not row: raise HTTPException(404, "Notification not found")
    row.is_read = True; db.commit(); db.refresh(row); return row
