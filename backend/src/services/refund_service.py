"""
Refund Service - xử lý nghiệp vụ hoàn tiền
"""
import random
import string
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import RefundRequest, RefundStatus, ComplaintStatus, ActorType
from src.schemas import RefundCreate
from src.services.audit_service import AuditService
from src.services.complaint_service import ComplaintService


class RefundService:
    """Service xử lý hoàn tiền"""

    @staticmethod
    def _generate_refund_code() -> str:
        """Tạo mã hoàn tiền ngẫu nhiên"""
        prefix = "RF"
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{random_part}"

    @staticmethod
    async def get_refunds_by_customer(db: AsyncSession, customer_id: UUID) -> List[RefundRequest]:
        """Lấy danh sách refund của customer"""
        query = select(RefundRequest).order_by(RefundRequest.created_at.desc())
        result = await db.execute(query)
        all_refunds = list(result.scalars().all())

        # Filter theo customer thông qua booking
        customer_refunds = []
        for refund in all_refunds:
            if refund.booking and refund.booking.user_id == customer_id:
                customer_refunds.append(refund)
        return customer_refunds

    @staticmethod
    async def get_all_refunds(
        db: AsyncSession,
        status: Optional[RefundStatus] = None
    ) -> List[RefundRequest]:
        """Lấy tất cả refunds (cho owner)"""
        query = select(RefundRequest).options(
            selectinload(RefundRequest.booking),
            selectinload(RefundRequest.complaint)
        )

        if status:
            query = query.where(RefundRequest.status == status)

        query = query.order_by(RefundRequest.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_refund_by_id(db: AsyncSession, refund_id: UUID) -> Optional[RefundRequest]:
        """Lấy refund theo ID"""
        query = select(RefundRequest).options(
            selectinload(RefundRequest.booking),
            selectinload(RefundRequest.complaint)
        ).where(RefundRequest.id == refund_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_refund(db: AsyncSession, customer_id: UUID, data: RefundCreate) -> RefundRequest:
        """Tạo yêu cầu hoàn tiền mới"""
        refund_code = RefundService._generate_refund_code()

        # Nếu có complaint_id, cập nhật status complaint
        if data.complaint_id:
            complaint = await ComplaintService.get_complaint_by_id(db, data.complaint_id)
            if complaint and complaint.booking and complaint.booking.user_id == customer_id:
                complaint.status = ComplaintStatus.IN_PROGRESS

        refund = RefundRequest(
            refund_code=refund_code,
            complaint_id=data.complaint_id,
            booking_id=data.booking_id,
            amount=data.amount,
            bank_name=data.bank_name,
            account_number=data.account_number,
            account_holder=data.account_holder,
            reason=data.reason,
            status=RefundStatus.WAITING_OWNER_APPROVAL
        )
        db.add(refund)
        await db.flush()
        await db.refresh(refund)
        return refund

    @staticmethod
    async def approve_refund(
        db: AsyncSession,
        refund_id: UUID,
        owner_id: UUID
    ) -> Optional[RefundRequest]:
        """Owner duyệt refund"""
        refund = await RefundService.get_refund_by_id(db, refund_id)
        if not refund:
            return None

        if refund.status not in [RefundStatus.WAITING_OWNER_APPROVAL]:
            raise ValueError(f"Không thể duyệt refund ở trạng thái {refund.status}")

        refund.status = RefundStatus.APPROVED

        # Tạo audit log
        await AuditService.create_log(
            db,
            actor_type=ActorType.OWNER,
            actor_id=owner_id,
            action="APPROVE_REFUND",
            entity_type="RefundRequest",
            entity_id=refund_id,
            description=f"Phê duyệt yêu cầu hoàn tiền {refund.refund_code} - {refund.amount:,} VND",
            metadata={
                "refund_code": refund.refund_code,
                "amount": refund.amount,
                "bank": refund.bank_name,
                "account": refund.account_number
            }
        )

        await db.flush()
        await db.refresh(refund)
        return refund

    @staticmethod
    async def reject_refund(
        db: AsyncSession,
        refund_id: UUID,
        owner_id: UUID,
        note: str
    ) -> Optional[RefundRequest]:
        """Owner từ chối refund"""
        refund = await RefundService.get_refund_by_id(db, refund_id)
        if not refund:
            return None

        if refund.status not in [RefundStatus.WAITING_OWNER_APPROVAL]:
            raise ValueError(f"Không thể từ chối refund ở trạng thái {refund.status}")

        refund.status = RefundStatus.REJECTED
        refund.owner_note = note

        # Tạo audit log
        await AuditService.create_log(
            db,
            actor_type=ActorType.OWNER,
            actor_id=owner_id,
            action="REJECT_REFUND",
            entity_type="RefundRequest",
            entity_id=refund_id,
            description=f"Từ chối yêu cầu hoàn tiền {refund.refund_code}",
            metadata={
                "refund_code": refund.refund_code,
                "reason": note
            }
        )

        await db.flush()
        await db.refresh(refund)
        return refund

    @staticmethod
    async def mark_as_refunded(
        db: AsyncSession,
        refund_id: UUID,
        owner_id: UUID
    ) -> Optional[RefundRequest]:
        """Đánh dấu đã hoàn tiền"""
        refund = await RefundService.get_refund_by_id(db, refund_id)
        if not refund:
            return None

        if refund.status != RefundStatus.APPROVED:
            raise ValueError(f"Không thể đánh dấu đã hoàn tiền khi ở trạng thái {refund.status}")

        refund.status = RefundStatus.REFUNDED

        # Tạo audit log
        await AuditService.create_log(
            db,
            actor_type=ActorType.OWNER,
            actor_id=owner_id,
            action="MARK_REFUNDED",
            entity_type="RefundRequest",
            entity_id=refund_id,
            description=f"Đã hoàn tiền {refund.refund_code} - {refund.amount:,} VND cho {refund.account_holder}",
            metadata={
                "refund_code": refund.refund_code,
                "amount": refund.amount,
                "account_holder": refund.account_holder
            }
        )

        await db.flush()
        await db.refresh(refund)
        return refund

    @staticmethod
    async def get_pending_refunds_count(db: AsyncSession) -> int:
        """Đếm số refund đang chờ duyệt"""
        result = await db.execute(
            select(RefundRequest).where(
                RefundRequest.status == RefundStatus.WAITING_OWNER_APPROVAL
            )
        )
        return len(result.scalars().all())
