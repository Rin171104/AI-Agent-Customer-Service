"""
Booking Tools - AI Tools cho domain đặt vé

Kết nối: Agent -> BookingTools -> BookingService -> Database
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.services.booking_service import BookingService
from src.services.trip_service import TripService
from src.models import BookingStatus, ActorType
from src.schemas import BookingCreate
from src.services.audit_service import AuditService
from src.utils.logger import logger


class BookingTools:
    """AI Tools cho đặt vé - kết nối thật với BookingService"""

    def __init__(self):
        self.logger = logger

    async def create_booking(
        self,
        db: Any,
        user_id: str,
        trip_id: str,
        seat_count: int
    ) -> Dict[str, Any]:
        """
        Tạo booking mới cho khách hàng.

        Args:
            db: Database session
            user_id: ID của khách hàng
            trip_id: ID của chuyến xe
            seat_count: Số ghế muốn đặt

        Returns:
            Dict với thông tin booking
        """
        try:
            # Validate inputs
            try:
                user_uuid = UUID(user_id)
                trip_uuid = UUID(trip_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            if seat_count < 1:
                return {
                    "success": False,
                    "error": "Số ghế phải lớn hơn 0"
                }

            # Kiểm tra trip tồn tại và còn ghế
            trip = await TripService.get_trip_by_id(db, trip_uuid)
            if not trip:
                return {
                    "success": False,
                    "error": "Chuyến xe không tồn tại"
                }

            if trip.available_seats < seat_count:
                return {
                    "success": False,
                    "error": f"Không đủ ghế. Chỉ còn {trip.available_seats} ghế"
                }

            # Tạo booking
            booking_data = BookingCreate(trip_id=trip_uuid, seat_count=seat_count)
            booking = await BookingService.create_booking(db, user_uuid, booking_data)

            # Tạo audit log
            await AuditService.create_log(
                db=db,
                actor_type=ActorType.CUSTOMER,
                actor_id=user_uuid,
                action="AI_CREATE_BOOKING",
                entity_type="Booking",
                entity_id=booking.id,
                description=f"Tạo booking {booking.booking_code} qua AI",
                metadata={
                    "trip_id": str(trip_id),
                    "seat_count": seat_count,
                    "total_amount": booking.total_amount
                }
            )

            return {
                "success": True,
                "booking": {
                    "id": str(booking.id),
                    "booking_code": booking.booking_code,
                    "trip_id": str(booking.trip_id),
                    "seat_count": booking.seat_count,
                    "total_amount": booking.total_amount,
                    "status": booking.status.value,
                    "created_at": booking.created_at.isoformat() if booking.created_at else None,
                },
                "trip_info": {
                    "origin": trip.origin,
                    "destination": trip.destination,
                    "departure_time": trip.departure_time,
                    "price_per_seat": trip.price,
                }
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo booking: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_booking(
        self,
        db: Any,
        booking_id: Optional[str] = None,
        booking_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy thông tin booking theo ID hoặc mã booking.

        Args:
            db: Database session
            booking_id: ID của booking
            booking_code: Mã booking (BKxxxxxx)

        Returns:
            Dict với thông tin booking chi tiết
        """
        try:
            booking = None

            if booking_id:
                try:
                    booking_uuid = UUID(booking_id)
                    booking = await BookingService.get_booking_by_id(db, booking_uuid)
                except ValueError:
                    return {
                        "success": False,
                        "error": "ID booking không hợp lệ"
                    }
            elif booking_code:
                booking = await BookingService.get_booking_by_code(db, booking_code.upper())
            else:
                return {
                    "success": False,
                    "error": "Cần cung cấp booking_id hoặc booking_code"
                }

            if not booking:
                return {
                    "success": False,
                    "error": "Không tìm thấy booking"
                }

            result = {
                "id": str(booking.id),
                "booking_code": booking.booking_code,
                "seat_count": booking.seat_count,
                "total_amount": booking.total_amount,
                "status": booking.status.value,
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
            }

            # Include trip info if loaded
            if booking.trip:
                result["trip"] = {
                    "id": str(booking.trip.id),
                    "origin": booking.trip.origin,
                    "destination": booking.trip.destination,
                    "departure_time": booking.trip.departure_time,
                    "arrival_time": booking.trip.arrival_time,
                    "price": booking.trip.price,
                }

            # Include payment info if loaded
            if booking.payment:
                result["payment"] = {
                    "id": str(booking.payment.id),
                    "amount": booking.payment.amount,
                    "method": booking.payment.method,
                    "status": booking.payment.status.value,
                    "paid_at": booking.payment.paid_at.isoformat() if booking.payment.paid_at else None,
                }

            return {
                "success": True,
                "booking": result
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy thông tin booking: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_user_bookings(
        self,
        db: Any,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Lấy danh sách booking của khách hàng.

        Args:
            db: Database session
            user_id: ID của khách hàng

        Returns:
            Dict với danh sách bookings
        """
        try:
            try:
                user_uuid = UUID(user_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID user không hợp lệ"
                }

            bookings = await BookingService.get_bookings_by_user(db, user_uuid)

            booking_list = []
            for booking in bookings:
                booking_list.append({
                    "id": str(booking.id),
                    "booking_code": booking.booking_code,
                    "trip_id": str(booking.trip_id),
                    "seat_count": booking.seat_count,
                    "total_amount": booking.total_amount,
                    "status": booking.status.value,
                    "created_at": booking.created_at.isoformat() if booking.created_at else None,
                })

            return {
                "success": True,
                "count": len(booking_list),
                "bookings": booking_list
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách booking: {e}")
            return {
                "success": False,
                "error": str(e),
                "bookings": []
            }

    async def cancel_booking(
        self,
        db: Any,
        booking_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Hủy booking (chỉ chủ booking hoặc owner).

        Args:
            db: Database session
            booking_id: ID của booking
            user_id: ID của user yêu cầu hủy

        Returns:
            Dict với kết quả hủy booking
        """
        try:
            try:
                booking_uuid = UUID(booking_id)
                user_uuid = UUID(user_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            # Kiểm tra booking tồn tại
            booking = await BookingService.get_booking_by_id(db, booking_uuid)
            if not booking:
                return {
                    "success": False,
                    "error": "Không tìm thấy booking"
                }

            # Kiểm tra quyền hủy
            if booking.user_id != user_uuid:
                return {
                    "success": False,
                    "error": "Bạn không có quyền hủy booking này"
                }

            # Thực hiện hủy
            cancelled_booking = await BookingService.cancel_booking(db, booking_uuid, user_uuid)

            # Tạo audit log
            await AuditService.create_log(
                db=db,
                actor_type=ActorType.CUSTOMER,
                actor_id=user_uuid,
                action="AI_CANCEL_BOOKING",
                entity_type="Booking",
                entity_id=booking_uuid,
                description=f"Hủy booking {booking.booking_code} qua AI",
                metadata={
                    "booking_code": booking.booking_code,
                    "previous_status": booking.status.value
                }
            )

            return {
                "success": True,
                "message": "Đã hủy booking thành công",
                "booking": {
                    "id": str(cancelled_booking.id),
                    "booking_code": cancelled_booking.booking_code,
                    "status": cancelled_booking.status.value,
                }
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Lỗi khi hủy booking: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_all_bookings(
        self,
        db: Any,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy tất cả bookings (cho owner).

        Args:
            db: Database session
            status: Filter theo status

        Returns:
            Dict với danh sách bookings
        """
        try:
            booking_status = None
            if status:
                try:
                    booking_status = BookingStatus(status.upper())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Status không hợp lệ: {status}"
                    }

            bookings = await BookingService.get_all_bookings(db, status=booking_status)

            booking_list = []
            for booking in bookings:
                item = {
                    "id": str(booking.id),
                    "booking_code": booking.booking_code,
                    "user_id": str(booking.user_id),
                    "trip_id": str(booking.trip_id),
                    "seat_count": booking.seat_count,
                    "total_amount": booking.total_amount,
                    "status": booking.status.value,
                    "created_at": booking.created_at.isoformat() if booking.created_at else None,
                }
                if booking.trip:
                    item["trip"] = {
                        "origin": booking.trip.origin,
                        "destination": booking.trip.destination,
                        "departure_time": booking.trip.departure_time,
                    }
                booking_list.append(item)

            return {
                "success": True,
                "count": len(booking_list),
                "bookings": booking_list
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách bookings: {e}")
            return {
                "success": False,
                "error": str(e),
                "bookings": []
            }
