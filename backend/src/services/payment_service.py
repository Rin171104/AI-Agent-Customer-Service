"""
Payment Service - xử lý nghiệp vụ thanh toán
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Payment, PaymentStatus, Booking, BookingStatus
from src.services.audit_service import AuditService
from src.models import ActorType


class PaymentService:
    """Service xử lý thanh toán"""

    @staticmethod
    async def get_payment_by_booking(db: AsyncSession, booking_id: UUID) -> Optional[Payment]:
        """Lấy payment theo booking ID"""
        result = await db.execute(
            select(Payment).where(Payment.booking_id == booking_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_payment_by_id(db: AsyncSession, payment_id: UUID) -> Optional[Payment]:
        """Lấy payment theo ID"""
        result = await db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_payment(db: AsyncSession, booking_id: UUID) -> Payment:
        """Tạo payment record cho booking"""
        # Kiểm tra booking đã có payment chưa
        existing = await PaymentService.get_payment_by_booking(db, booking_id)
        if existing:
            return existing

        # Lấy booking
        result = await db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            raise ValueError("Booking không tồn tại")

        payment = Payment(
            booking_id=booking_id,
            amount=booking.total_amount,
            method="CASH",
            status=PaymentStatus.PENDING
        )
        db.add(payment)
        await db.flush()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def process_payment(
        db: AsyncSession,
        payment_id: UUID,
        success: bool = True,
        actor_type: ActorType = ActorType.CUSTOMER,
        actor_id: Optional[UUID] = None
    ) -> Payment:
        """Xử lý thanh toán - mô phỏng"""
        payment = await PaymentService.get_payment_by_id(db, payment_id)
        if not payment:
            raise ValueError("Payment không tồn tại")

        if payment.status != PaymentStatus.PENDING:
            raise ValueError("Payment đã được xử lý")

        if success:
            payment.status = PaymentStatus.PAID
            payment.paid_at = datetime.utcnow()

            # Cập nhật booking thành CONFIRMED
            result = await db.execute(
                select(Booking).where(Booking.id == payment.booking_id)
            )
            booking = result.scalar_one_or_none()
            if booking:
                booking.status = BookingStatus.CONFIRMED

            # Tạo audit log
            await AuditService.create_log(
                db,
                actor_type=actor_type,
                actor_id=actor_id,
                action="PAYMENT_SUCCESS",
                entity_type="Payment",
                entity_id=payment_id,
                description=f"Thanh toán thành công cho booking {booking.booking_code if booking else payment.booking_id}",
                metadata={"amount": payment.amount}
            )
        else:
            payment.status = PaymentStatus.FAILED

            # Tạo audit log
            await AuditService.create_log(
                db,
                actor_type=actor_type,
                actor_id=actor_id,
                action="PAYMENT_FAILED",
                entity_type="Payment",
                entity_id=payment_id,
                description=f"Thanh toán thất bại cho booking",
                metadata={"amount": payment.amount}
            )

        await db.flush()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def get_pending_payments_count(db: AsyncSession) -> int:
        """Đếm số payment đang chờ"""
        result = await db.execute(
            select(Payment).where(Payment.status == PaymentStatus.PENDING)
        )
        return len(result.scalars().all())
