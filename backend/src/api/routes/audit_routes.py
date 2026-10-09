"""
API Routes - Audit Logs
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import require_role
from src.models import User, UserRole
from src.schemas import AuditLogResponse
from src.services.audit_service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogResponse])
async def get_audit_logs(
    action: str | None = Query(None, description="Lọc theo action"),
    entity_type: str | None = Query(None, description="Lọc theo entity type"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(require_role(UserRole.OWNER))
):
    """Lấy danh sách audit logs (chỉ owner)"""
    logs = await AuditService.get_logs(db, action, entity_type, limit=limit)
    return logs
