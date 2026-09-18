"""
Dashboard Service - thống kê cho owner
"""
from datetime import datetime, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Trip, Booking, Payment, Complaint, RefundRequest
from src.models import BookingStatus, PaymentStatus, ComplaintStatus, RefundStatus


class DashboardService:
    """Service xử lý dashboard statistics"""

    @staticmethod
    async def get_owner_stats(db: AsyncSession) -> dict:
        """Lấy thống kê cho owner dashboard"""
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # Total trips
        total_trips_result = await db.execute(select(func.count(Trip.id)))
        total_trips = total_trips_result.scalar() or 0

        # Today's trips
        today_trips_result = await db.execute(
            select(func.count(Trip.id)).where(Trip.created_at >= today_start)
        )
        today_trips = today_trips_result.scalar() or 0

        # Total bookings
        total_bookings_result = await db.execute(select(func.count(Booking.id)))
        total_bookings = total_bookings_result.scalar() or 0

        # Today's bookings
        today_bookings_result = await db.execute(
            select(func.count(Booking.id)).where(Booking.created_at >= today_start)
        )
        today_bookings = today_bookings_result.scalar() or 0

        # Revenue (tổng payment đã thanh toán)
        revenue_result = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PaymentStatus.PAID
            )
        )
        revenue = revenue_result.scalar() or 0

        # Pending payments
        pending_payments_result = await db.execute(
            select(func.count(Payment.id)).where(Payment.status == PaymentStatus.PENDING)
        )
        pending_payments = pending_payments_result.scalar() or 0

        # Open complaints
        open_complaints_result = await db.execute(
            select(func.count(Complaint.id)).where(
                Complaint.status.in_([ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS])
            )
        )
        open_complaints = open_complaints_result.scalar() or 0

        # Pending refunds
        pending_refunds_result = await db.execute(
            select(func.count(RefundRequest.id)).where(
                RefundRequest.status == RefundStatus.WAITING_OWNER_APPROVAL
            )
        )
        pending_refunds = pending_refunds_result.scalar() or 0

        return {
            "total_trips": total_trips,
            "today_trips": today_trips,
            "total_bookings": total_bookings,
            "today_bookings": today_bookings,
            "revenue": revenue,
            "pending_payments": pending_payments,
            "open_complaints": open_complaints,
            "pending_refunds": pending_refunds
        }
