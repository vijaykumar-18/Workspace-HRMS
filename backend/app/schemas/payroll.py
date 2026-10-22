from pydantic import BaseModel, Field
class PayrollCreate(BaseModel):
    employee_id: int
    basic_salary: float = Field(ge=0)
    allowances: float = Field(default=0, ge=0)
    deductions: float = Field(default=0, ge=0)
    bonus: float = Field(default=0, ge=0)
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
