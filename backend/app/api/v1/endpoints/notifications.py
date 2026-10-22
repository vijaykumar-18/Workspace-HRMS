from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification
router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()

@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Notification).filter_by(id=notification_id, user_id=user.id).first()
    if not row: raise HTTPException(404, "Notification not found")
    row.is_read = True; db.commit(); return {"message": "Marked as read"}
