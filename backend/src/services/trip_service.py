"""
Trip Service - xử lý nghiệp vụ chuyến xe
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Trip, TripStatus
from src.schemas import TripCreate, TripUpdate


class TripService:
    """Service xử lý chuyến xe"""

    @staticmethod
    async def get_all_trips(
        db: AsyncSession,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        status: Optional[TripStatus] = None
    ) -> List[Trip]:
        """Lấy danh sách tất cả chuyến xe với filter"""
        query = select(Trip)

        conditions = []
        if origin:
            conditions.append(Trip.origin.ilike(f"%{origin}%"))
        if destination:
            conditions.append(Trip.destination.ilike(f"%{destination}%"))
        if status:
            conditions.append(Trip.status == status)
        else:
            # Mặc định chỉ lấy chuyến ACTIVE
            conditions.append(Trip.status == TripStatus.ACTIVE)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Trip.departure_time)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_trip_by_id(db: AsyncSession, trip_id: UUID) -> Optional[Trip]:
        """Lấy chuyến xe theo ID"""
        result = await db.execute(select(Trip).where(Trip.id == trip_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_trip(db: AsyncSession, data: TripCreate) -> Trip:
        """Tạo chuyến xe mới"""
        trip = Trip(
            route=data.route,
            origin=data.origin,
            destination=data.destination,
            departure_time=data.departure_time,
            arrival_time=data.arrival_time,
            price=data.price,
            total_seats=data.total_seats,
            available_seats=data.total_seats,
            status=TripStatus.ACTIVE
        )
        db.add(trip)
        await db.flush()
        await db.refresh(trip)
        return trip

    @staticmethod
    async def update_trip(db: AsyncSession, trip_id: UUID, data: TripUpdate) -> Optional[Trip]:
        """Cập nhật chuyến xe"""
        trip = await TripService.get_trip_by_id(db, trip_id)
        if not trip:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(trip, field, value)

        await db.flush()
        await db.refresh(trip)
        return trip

    @staticmethod
    async def cancel_trip(db: AsyncSession, trip_id: UUID) -> Optional[Trip]:
        """Hủy chuyến xe"""
        trip = await TripService.get_trip_by_id(db, trip_id)
        if not trip:
            return None

        trip.status = TripStatus.CANCELLED
        await db.flush()
        await db.refresh(trip)
        return trip

    @staticmethod
    async def check_available_seats(db: AsyncSession, trip_id: UUID, seat_count: int) -> bool:
        """Kiểm tra số ghế còn trống"""
        trip = await TripService.get_trip_by_id(db, trip_id)
        if not trip:
            return False
        return trip.available_seats >= seat_count

    @staticmethod
    async def reserve_seats(db: AsyncSession, trip_id: UUID, seat_count: int) -> bool:
        """Đặt giữ ghế - giảm available_seats"""
        trip = await TripService.get_trip_by_id(db, trip_id)
        if not trip:
            return False
        if trip.available_seats < seat_count:
            return False

        trip.available_seats -= seat_count
        await db.flush()
        return True

    @staticmethod
    async def release_seats(db: AsyncSession, trip_id: UUID, seat_count: int) -> bool:
        """Giải phóng ghế - tăng available_seats"""
        trip = await TripService.get_trip_by_id(db, trip_id)
        if not trip:
            return False

        trip.available_seats += seat_count
        if trip.available_seats > trip.total_seats:
            trip.available_seats = trip.total_seats

        await db.flush()
        return True
