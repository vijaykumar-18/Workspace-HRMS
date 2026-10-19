from datetime import date, datetime
from sqlalchemy.orm import Session
from . import models

def notify(db: Session, user_id: int | None, title: str, message: str):
    if user_id is not None:
        db.add(models.Notification(user_id=user_id, title=title, message=message))
