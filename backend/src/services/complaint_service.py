"""
Complaint Service - xử lý nghiệp vụ khiếu nại
"""
import random
import string
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Complaint, ComplaintStatus, ComplaintType, ComplaintPriority
from src.schemas import ComplaintCreate, ComplaintUpdate


class ComplaintService:
    """Service xử lý khiếu nại"""

    @staticmethod
    def _generate_complaint_code() -> str:
        """Tạo mã khiếu nại ngẫu nhiên"""
        prefix = "CL"
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{random_part}"

    @staticmethod
    async def get_complaints_by_customer(db: AsyncSession, customer_id: UUID) -> List[Complaint]:
        """Lấy danh sách khiếu nại của customer"""
        query = select(Complaint).where(Complaint.customer_id == customer_id).order_by(Complaint.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_complaints(
        db: AsyncSession,
        status: Optional[ComplaintStatus] = None,
        priority: Optional[ComplaintPriority] = None
    ) -> List[Complaint]:
        """Lấy tất cả khiếu nại (cho owner)"""
        query = select(Complaint).options(
            selectinload(Complaint.booking)
        )

        conditions = []
        if status:
            conditions.append(Complaint.status == status)
        if priority:
            conditions.append(Complaint.priority == priority)

        if conditions:
            query = query.where(*conditions)

        query = query.order_by(Complaint.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_complaint_by_id(db: AsyncSession, complaint_id: UUID) -> Optional[Complaint]:
        """Lấy khiếu nại theo ID"""
        query = select(Complaint).options(
            selectinload(Complaint.booking),
            selectinload(Complaint.refund_requests)
        ).where(Complaint.id == complaint_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_complaint(db: AsyncSession, customer_id: UUID, data: ComplaintCreate) -> Complaint:
        """Tạo khiếu nại mới"""
        complaint_code = ComplaintService._generate_complaint_code()

        complaint = Complaint(
            complaint_code=complaint_code,
            customer_id=customer_id,
            booking_id=data.booking_id,
            type=data.type,
            description=data.description,
            status=ComplaintStatus.OPEN,
            priority=data.priority
        )
        db.add(complaint)
        await db.flush()
        await db.refresh(complaint)
        return complaint

    @staticmethod
    async def update_complaint(
        db: AsyncSession,
        complaint_id: UUID,
        data: ComplaintUpdate
    ) -> Optional[Complaint]:
        """Cập nhật khiếu nại"""
        complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
        if not complaint:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(complaint, field, value)

        await db.flush()
        await db.refresh(complaint)
        return complaint

    @staticmethod
    async def resolve_complaint(db: AsyncSession, complaint_id: UUID, owner_note: str) -> Optional[Complaint]:
        """Giải quyết khiếu nại"""
        complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
        if not complaint:
            return None

        complaint.status = ComplaintStatus.RESOLVED
        complaint.owner_note = owner_note

        await db.flush()
        await db.refresh(complaint)
        return complaint

    @staticmethod
    async def get_open_complaints_count(db: AsyncSession) -> int:
        """Đếm số khiếu nại đang mở"""
        result = await db.execute(
            select(Complaint).where(Complaint.status == ComplaintStatus.OPEN)
        )
        return len(result.scalars().all())
