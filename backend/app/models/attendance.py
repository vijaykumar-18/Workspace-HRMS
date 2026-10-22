from datetime import datetime, date
from sqlalchemy import Date, DateTime, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    check_in: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    check_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PRESENT")
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)
    working_hours: Mapped[float] = mapped_column(Float, default=0)
