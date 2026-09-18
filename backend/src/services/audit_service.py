"""
Audit Service - xử lý log kiểm toán
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AuditLog, ActorType


class AuditService:
    """Service xử lý audit log"""

    @staticmethod
    async def create_log(
        db: AsyncSession,
        actor_type: ActorType,
        action: str,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        actor_id: Optional[UUID] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> AuditLog:
        """Tạo audit log mới"""
        log = AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            extra_data=metadata
        )
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Lấy danh sách audit logs với filter"""
        query = select(AuditLog)

        conditions = []
        if action:
            conditions.append(AuditLog.action == action)
        if entity_type:
            conditions.append(AuditLog.entity_type == entity_type)
        if from_date:
            conditions.append(AuditLog.created_at >= from_date)
        if to_date:
            conditions.append(AuditLog.created_at <= to_date)

        if conditions:
            query = query.where(*conditions)

        query = query.order_by(AuditLog.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
