"""
Dashboard Service - thống kê cho owner
"""
from datetime import datetime, date, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

    @staticmethod
    async def get_chart_data(db: AsyncSession, days: int = 7) -> dict:
        """Lấy dữ liệu chart cho dashboard"""
        today = date.today()
        start_date = today - timedelta(days=days - 1)
        start_datetime = datetime.combine(start_date, datetime.min.time())

        # Bookings by day
        bookings_by_day = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            count_result = await db.execute(
                select(func.count(Booking.id)).where(
                    and_(
                        Booking.created_at >= day_start,
                        Booking.created_at <= day_end
                    )
                )
            )
            count = count_result.scalar() or 0
            bookings_by_day.append({
                "date": day.strftime("%d/%m"),
                "count": count
            })

        # Revenue by day
        revenue_by_day = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            revenue_result = await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    and_(
                        Payment.status == PaymentStatus.PAID,
                        Payment.paid_at >= day_start,
                        Payment.paid_at <= day_end
                    )
                )
            )
            day_revenue = revenue_result.scalar() or 0
            revenue_by_day.append({
                "date": day.strftime("%d/%m"),
                "revenue": day_revenue
            })

        # Bookings by route
        bookings_query = await db.execute(
            select(
                Trip.route,
                Trip.origin,
                Trip.destination,
                func.count(Booking.id).label("count")
            )
            .join(Booking, Booking.trip_id == Trip.id)
            .group_by(Trip.id, Trip.route, Trip.origin, Trip.destination)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
        )
        bookings_by_route = [
            {
                "route": row.route,
                "origin": row.origin,
                "destination": row.destination,
                "count": row.count
            }
            for row in bookings_query.fetchall()
        ]

        # Bookings by status
        status_result = await db.execute(
            select(
                Booking.status,
                func.count(Booking.id).label("count")
            )
            .group_by(Booking.status)
        )
        total_status_count = sum(row.count for row in status_result.fetchall())

        # Re-execute for data
        status_result = await db.execute(
            select(
                Booking.status,
                func.count(Booking.id).label("count")
            )
            .group_by(Booking.status)
        )
        bookings_by_status = []
        for row in status_result.fetchall():
            count = row.count
            percentage = (count / total_status_count * 100) if total_status_count > 0 else 0
            bookings_by_status.append({
                "status": row.status.value if hasattr(row.status, 'value') else str(row.status),
                "count": count,
                "percentage": round(percentage, 1)
            })

        return {
            "bookings_by_day": bookings_by_day,
            "revenue_by_day": revenue_by_day,
            "bookings_by_route": bookings_by_route,
            "bookings_by_status": bookings_by_status
        }
