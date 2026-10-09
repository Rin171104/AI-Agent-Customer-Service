"""
Audit Service - xử lý log kiểm toán
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ActorType, AuditLog


class AuditService:
    """Service xử lý audit log"""

    @staticmethod
    async def create_log(
        db: AsyncSession,
        actor_type: ActorType,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        actor_id: UUID | None = None,
        description: str | None = None,
        metadata: dict | None = None
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
        action: str | None = None,
        entity_type: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 100
    ) -> list[AuditLog]:
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
