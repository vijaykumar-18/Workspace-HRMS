from pydantic import BaseModel
class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    date: str
    check_in: str | None
    check_out: str | None
    status: str
    is_late: bool
    working_hours: float
    class Config:
        from_attributes = True
