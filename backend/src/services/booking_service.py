"""
Booking Service - xử lý nghiệp vụ đặt vé
"""
import random
import string
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Booking, BookingStatus, Trip
from src.schemas import BookingCreate
from src.services.trip_service import TripService


class BookingService:
    """Service xử lý đặt vé"""

    @staticmethod
    def _generate_booking_code() -> str:
        """Tạo mã booking ngẫu nhiên"""
        prefix = "BK"
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{random_part}"

    @staticmethod
    async def get_bookings_by_user(db: AsyncSession, user_id: UUID) -> List[Booking]:
        """Lấy danh sách booking của user"""
        query = select(Booking).where(Booking.user_id == user_id).order_by(Booking.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_bookings(
        db: AsyncSession,
        status: Optional[BookingStatus] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Booking]:
        """Lấy tất cả bookings (cho owner)"""
        query = select(Booking).options(selectinload(Booking.trip))

        conditions = []
        if status:
            conditions.append(Booking.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Booking.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_booking_by_id(db: AsyncSession, booking_id: UUID) -> Optional[Booking]:
        """Lấy booking theo ID"""
        query = select(Booking).options(
            selectinload(Booking.trip),
            selectinload(Booking.payment)
        ).where(Booking.id == booking_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_booking_by_code(db: AsyncSession, booking_code: str) -> Optional[Booking]:
        """Lấy booking theo mã"""
        query = select(Booking).options(
            selectinload(Booking.trip),
            selectinload(Booking.payment)
        ).where(Booking.booking_code == booking_code)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_booking(db: AsyncSession, user_id: UUID, data: BookingCreate) -> Booking:
        """Tạo booking mới"""
        # Lấy trip
        trip = await TripService.get_trip_by_id(db, data.trip_id)
        if not trip:
            raise ValueError("Chuyến xe không tồn tại")

        # Kiểm tra ghế còn trống
        if trip.available_seats < data.seat_count:
            raise ValueError(f"Không đủ ghế. Chỉ còn {trip.available_seats} ghế")

        # Tạo booking
        booking_code = BookingService._generate_booking_code()
        total_amount = trip.price * data.seat_count

        booking = Booking(
            booking_code=booking_code,
            user_id=user_id,
            trip_id=trip.id,
            seat_count=data.seat_count,
            total_amount=total_amount,
            status=BookingStatus.PENDING_PAYMENT
        )
        db.add(booking)

        # Trừ ghế
        await TripService.reserve_seats(db, trip.id, data.seat_count)

        await db.flush()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def update_booking_status(db: AsyncSession, booking_id: UUID, status: BookingStatus) -> Optional[Booking]:
        """Cập nhật trạng thái booking"""
        booking = await BookingService.get_booking_by_id(db, booking_id)
        if not booking:
            return None

        old_status = booking.status
        booking.status = status

        # Nếu hủy booking thì giải phóng ghế
        if status == BookingStatus.CANCELLED and old_status != BookingStatus.CANCELLED:
            await TripService.release_seats(db, booking.trip_id, booking.seat_count)

        await db.flush()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def cancel_booking(db: AsyncSession, booking_id: UUID, user_id: UUID) -> Optional[Booking]:
        """Hủy booking (chỉ chủ booking hoặc owner)"""
        booking = await BookingService.get_booking_by_id(db, booking_id)
        if not booking:
            return None

        if booking.user_id != user_id:
            raise ValueError("Bạn không có quyền hủy booking này")

        if booking.status == BookingStatus.CANCELLED:
            raise ValueError("Booking đã bị hủy")

        if booking.status == BookingStatus.CONFIRMED:
            raise ValueError("Không thể hủy booking đã xác nhận")

        return await BookingService.update_booking_status(db, booking_id, BookingStatus.CANCELLED)
