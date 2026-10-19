from datetime import datetime, date
from sqlalchemy import String, Integer, Float, DateTime, Date, Time, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="EMPLOYEE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    employee: Mapped["Employee"] = relationship(back_populates="user", uselist=False)

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(150))
    designation: Mapped[str] = mapped_column(String(100), default="Employee")
    department: Mapped[str] = mapped_column(String(100), default="General")
    joining_date: Mapped[date] = mapped_column(Date, default=date.today)
    salary: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    user: Mapped[User | None] = relationship(back_populates="employee")
    attendance: Mapped[list["Attendance"]] = relationship(back_populates="employee")
    leaves: Mapped[list["Leave"]] = relationship(back_populates="employee")
    payroll: Mapped[list["Payroll"]] = relationship(back_populates="employee")

class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    check_in: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    check_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    date: Mapped[date] = mapped_column(Date, default=date.today)
    status: Mapped[str] = mapped_column(String(20), default="PRESENT")
    employee: Mapped[Employee] = relationship(back_populates="attendance")

class Leave(Base):
    __tablename__ = "leaves"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    leave_type: Mapped[str] = mapped_column(String(20))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    employee: Mapped[Employee] = relationship(back_populates="leaves")

class Payroll(Base):
    __tablename__ = "payroll"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    basic_salary: Mapped[float] = mapped_column(Float)
    deductions: Mapped[float] = mapped_column(Float, default=0)
    bonus: Mapped[float] = mapped_column(Float, default=0)
    net_salary: Mapped[float] = mapped_column(Float)
    month: Mapped[str] = mapped_column(String(7))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    employee: Mapped[Employee] = relationship(back_populates="payroll")

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(150))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
