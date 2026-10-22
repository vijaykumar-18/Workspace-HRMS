from fastapi import APIRouter
from app.api.v1.endpoints import auth, admin, attendance, leaves, payroll, portal, employees, analytics, notifications
api_router = APIRouter()
for router in [auth.router, admin.router, attendance.router, leaves.router, payroll.router, portal.router, employees.router, analytics.router, notifications.router]:
    api_router.include_router(router)
