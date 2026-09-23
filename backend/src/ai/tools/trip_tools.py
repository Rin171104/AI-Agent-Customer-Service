"""
Trip Tools - AI Tools cho domain chuyến xe

Kết nối: Agent -> TripTools -> TripService -> Database
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.services.trip_service import TripService
from src.models import TripStatus
from src.schemas import TripResponse
from src.utils.logger import logger


class TripTools:
    """AI Tools cho chuyến xe - kết nối thật với TripService"""

    def __init__(self):
        self.logger = logger

    async def search_trips(
        self,
        db: Any,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        status: Optional[TripStatus] = TripStatus.ACTIVE
    ) -> Dict[str, Any]:
        """
        Tìm kiếm chuyến xe theo điểm đi, điểm đến.

        Args:
            db: Database session
            origin: Điểm đi (search gần đúng)
            destination: Điểm đến (search gần đúng)
            status: Trạng thái chuyến xe (mặc định: ACTIVE)

        Returns:
            Dict với danh sách trips hoặc lỗi
        """
        try:
            trips = await TripService.get_all_trips(
                db=db,
                origin=origin,
                destination=destination,
                status=status
            )

            trip_list = []
            for trip in trips:
                trip_list.append({
                    "id": str(trip.id),
                    "route": trip.route,
                    "origin": trip.origin,
                    "destination": trip.destination,
                    "departure_time": trip.departure_time,
                    "arrival_time": trip.arrival_time,
                    "price": trip.price,
                    "total_seats": trip.total_seats,
                    "available_seats": trip.available_seats,
                    "status": trip.status.value,
                })

            return {
                "success": True,
                "count": len(trip_list),
                "trips": trip_list
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi tìm kiếm chuyến xe: {e}")
            return {
                "success": False,
                "error": str(e),
                "trips": []
            }

    async def get_trip(
        self,
        db: Any,
        trip_id: str
    ) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết một chuyến xe.

        Args:
            db: Database session
            trip_id: ID của chuyến xe

        Returns:
            Dict với thông tin trip hoặc lỗi
        """
        try:
            # Validate trip_id format
            try:
                trip_uuid = UUID(trip_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID chuyến xe không hợp lệ"
                }

            trip = await TripService.get_trip_by_id(db, trip_uuid)

            if not trip:
                return {
                    "success": False,
                    "error": "Không tìm thấy chuyến xe"
                }

            return {
                "success": True,
                "trip": {
                    "id": str(trip.id),
                    "route": trip.route,
                    "origin": trip.origin,
                    "destination": trip.destination,
                    "departure_time": trip.departure_time,
                    "arrival_time": trip.arrival_time,
                    "price": trip.price,
                    "total_seats": trip.total_seats,
                    "available_seats": trip.available_seats,
                    "status": trip.status.value,
                    "created_at": trip.created_at.isoformat() if trip.created_at else None,
                }
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy thông tin chuyến xe: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def check_available_seats(
        self,
        db: Any,
        trip_id: str,
        seat_count: int = 1
    ) -> Dict[str, Any]:
        """
        Kiểm tra số ghế còn trống cho một chuyến xe.

        ĐÂY LÀ DỮ LIỆU REALTIME - phải lấy từ Database.

        Args:
            db: Database session
            trip_id: ID của chuyến xe
            seat_count: Số ghế cần đặt (mặc định: 1)

        Returns:
            Dict với thông tin ghế còn trống
        """
        try:
            # Validate inputs
            try:
                trip_uuid = UUID(trip_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID chuyến xe không hợp lệ"
                }

            if seat_count < 1:
                return {
                    "success": False,
                    "error": "Số ghế phải lớn hơn 0"
                }

            # Lấy thông tin trip
            trip = await TripService.get_trip_by_id(db, trip_uuid)

            if not trip:
                return {
                    "success": False,
                    "error": "Không tìm thấy chuyến xe"
                }

            # Kiểm tra số ghế
            is_available = await TripService.check_available_seats(db, trip_uuid, seat_count)

            return {
                "success": True,
                "trip_id": str(trip.id),
                "requested_seats": seat_count,
                "available_seats": trip.available_seats,
                "total_seats": trip.total_seats,
                "is_available": is_available,
                "can_book": trip.available_seats >= seat_count,
                "message": f"Còn {trip.available_seats} ghế trống" if trip.available_seats > 0 else "Hết ghế trống"
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi kiểm tra ghế: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_available_trips_summary(
        self,
        db: Any,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        min_seats: int = 1
    ) -> Dict[str, Any]:
        """
        Lấy danh sách chuyến xe còn ghế trống.

        Args:
            db: Database session
            origin: Điểm đi
            destination: Điểm đến
            min_seats: Số ghế tối thiểu cần có

        Returns:
            Dict với danh sách trips có thể đặt
        """
        try:
            # Lấy tất cả chuyến active
            trips = await TripService.get_all_trips(
                db=db,
                origin=origin,
                destination=destination,
                status=TripStatus.ACTIVE
            )

            # Filter các chuyến có đủ ghế
            available_trips = []
            for trip in trips:
                if trip.available_seats >= min_seats:
                    available_trips.append({
                        "id": str(trip.id),
                        "route": trip.route,
                        "origin": trip.origin,
                        "destination": trip.destination,
                        "departure_time": trip.departure_time,
                        "arrival_time": trip.arrival_time,
                        "price": trip.price,
                        "available_seats": trip.available_seats,
                    })

            return {
                "success": True,
                "count": len(available_trips),
                "trips": available_trips
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách chuyến xe: {e}")
            return {
                "success": False,
                "error": str(e),
                "trips": []
            }
