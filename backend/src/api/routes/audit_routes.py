"""
API Routes - Audit Logs
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User
from src.schemas import AuditLogResponse
from src.services.audit_service import AuditService
from src.dependencies import require_role
from src.models import UserRole

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogResponse])
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Lọc theo action"),
    entity_type: Optional[str] = Query(None, description="Lọc theo entity type"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy danh sách audit logs (chỉ owner)"""
    logs = await AuditService.get_logs(db, action, entity_type, limit=limit)
    return logs
