from pydantic import BaseModel, Field
from datetime import date
class LeaveCreate(BaseModel):
    leave_type: str = Field(pattern="^(SICK|CASUAL|PAID)$")
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=500)
class LeaveDecision(BaseModel):
    status: str = Field(pattern="^(APPROVED|REJECTED)$")
