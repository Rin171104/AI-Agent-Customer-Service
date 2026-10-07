"""
API Routes - Dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User
from src.schemas import DashboardStats, ChartData
from src.services.dashboard_service import DashboardService
from src.dependencies import require_role
from src.models import UserRole

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy thống kê dashboard (chỉ owner)"""
    stats = await DashboardService.get_owner_stats(db)
    return stats


@router.get("/chart-data", response_model=ChartData)
async def get_chart_data(
    days: int = Query(default=7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy dữ liệu chart cho dashboard"""
    chart_data = await DashboardService.get_chart_data(db, days)
    return chart_data
