from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    # Public registration always creates EMPLOYEE; HR/ADMIN must be assigned by an administrator.
class LoginIn(BaseModel):
    username: str
    password: str
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class EmployeeIn(BaseModel):
    user_id: int | None = None
    full_name: str = Field(min_length=2, max_length=150)
    designation: str = "Employee"
    department: str = "General"
    joining_date: date = Field(default_factory=date.today)
    salary: float = Field(ge=0)
    status: str = "ACTIVE"
class EmployeeOut(EmployeeIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class AttendanceIn(BaseModel):
    employee_id: int
class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    check_in: datetime | None
    check_out: datetime | None
    date: date
    status: str

class LeaveIn(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=1000)
    @model_validator(mode="after")
    def valid_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if self.leave_type not in {"SICK", "CASUAL", "PAID"}:
            raise ValueError("leave_type must be SICK, CASUAL, or PAID")
        return self
class LeaveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str
    created_at: datetime

class PayrollIn(BaseModel):
    employee_id: int
    basic_salary: float = Field(ge=0)
    deductions: float = Field(default=0, ge=0)
    bonus: float = Field(default=0, ge=0)
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
class PayrollOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    basic_salary: float
    deductions: float
    bonus: float
    net_salary: float
    month: str
    created_at: datetime
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
