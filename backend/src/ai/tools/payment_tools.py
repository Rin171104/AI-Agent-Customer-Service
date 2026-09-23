"""
Payment Tools - AI Tools cho domain thanh toán

Kết nối: Agent -> PaymentTools -> PaymentService -> Database
"""
from typing import Dict, Any, Optional
from uuid import UUID

from src.services.payment_service import PaymentService
from src.services.booking_service import BookingService
from src.models import ActorType, PaymentStatus
from src.services.audit_service import AuditService
from src.utils.logger import logger


class PaymentTools:
    """AI Tools cho thanh toán - kết nối thật với PaymentService"""

    def __init__(self):
        self.logger = logger

    async def create_payment(
        self,
        db: Any,
        booking_id: str,
        actor_id: Optional[str] = None,
        actor_type: str = "CUSTOMER"
    ) -> Dict[str, Any]:
        """
        Tạo payment record cho booking.

        Args:
            db: Database session
            booking_id: ID của booking
            actor_id: ID của actor thực hiện
            actor_type: Loại actor (CUSTOMER/OWNER)

        Returns:
            Dict với thông tin payment
        """
        try:
            try:
                booking_uuid = UUID(booking_id)
                actor_uuid = UUID(actor_id) if actor_id else None
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
                    "error": "Booking không tồn tại"
                }

            # Kiểm tra booking đã có payment chưa
            existing_payment = await PaymentService.get_payment_by_booking(db, booking_uuid)
            if existing_payment:
                return {
                    "success": True,
                    "payment": {
                        "id": str(existing_payment.id),
                        "booking_id": str(existing_payment.booking_id),
                        "amount": existing_payment.amount,
                        "method": existing_payment.method,
                        "status": existing_payment.status.value,
                        "created_at": existing_payment.created_at.isoformat() if existing_payment.created_at else None,
                    },
                    "message": "Payment đã tồn tại"
                }

            # Tạo payment mới
            payment = await PaymentService.create_payment(db, booking_uuid)

            # Tạo audit log
            try:
                actor_type_enum = ActorType(actor_type.upper())
            except ValueError:
                actor_type_enum = ActorType.CUSTOMER

            await AuditService.create_log(
                db=db,
                actor_type=actor_type_enum,
                actor_id=actor_uuid,
                action="AI_CREATE_PAYMENT",
                entity_type="Payment",
                entity_id=payment.id,
                description=f"Tạo payment cho booking {booking.booking_code} qua AI",
                metadata={
                    "booking_code": booking.booking_code,
                    "amount": payment.amount
                }
            )

            return {
                "success": True,
                "payment": {
                    "id": str(payment.id),
                    "booking_id": str(payment.booking_id),
                    "amount": payment.amount,
                    "method": payment.method,
                    "status": payment.status.value,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None,
                },
                "booking": {
                    "booking_code": booking.booking_code,
                    "total_amount": booking.total_amount,
                }
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_payment(
        self,
        db: Any,
        payment_id: str,
        success: bool = True,
        actor_id: Optional[str] = None,
        actor_type: str = "CUSTOMER"
    ) -> Dict[str, Any]:
        """
        Xử lý thanh toán (mô phỏng - xác nhận thanh toán thành công/thất bại).

        Args:
            db: Database session
            payment_id: ID của payment
            success: Thanh toán thành công hay thất bại
            actor_id: ID của actor thực hiện
            actor_type: Loại actor

        Returns:
            Dict với kết quả xử lý
        """
        try:
            try:
                payment_uuid = UUID(payment_id)
                actor_uuid = UUID(actor_id) if actor_id else None
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            # Kiểm tra payment tồn tại
            payment = await PaymentService.get_payment_by_id(db, payment_uuid)
            if not payment:
                return {
                    "success": False,
                    "error": "Payment không tồn tại"
                }

            if payment.status != PaymentStatus.PENDING:
                return {
                    "success": False,
                    "error": f"Payment đã ở trạng thái {payment.status.value}, không thể xử lý"
                }

            # Xử lý payment
            try:
                actor_type_enum = ActorType(actor_type.upper())
            except ValueError:
                actor_type_enum = ActorType.CUSTOMER

            updated_payment = await PaymentService.process_payment(
                db=db,
                payment_id=payment_uuid,
                success=success,
                actor_type=actor_type_enum,
                actor_id=actor_uuid
            )

            return {
                "success": True,
                "message": "Thanh toán thành công" if success else "Thanh toán thất bại",
                "payment": {
                    "id": str(updated_payment.id),
                    "amount": updated_payment.amount,
                    "status": updated_payment.status.value,
                    "paid_at": updated_payment.paid_at.isoformat() if updated_payment.paid_at else None,
                }
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_payment(
        self,
        db: Any,
        payment_id: Optional[str] = None,
        booking_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy thông tin payment.

        Args:
            db: Database session
            payment_id: ID của payment
            booking_id: ID của booking (để tìm payment)

        Returns:
            Dict với thông tin payment
        """
        try:
            payment = None

            if payment_id:
                try:
                    payment_uuid = UUID(payment_id)
                    payment = await PaymentService.get_payment_by_id(db, payment_uuid)
                except ValueError:
                    return {
                        "success": False,
                        "error": "ID payment không hợp lệ"
                    }
            elif booking_id:
                try:
                    booking_uuid = UUID(booking_id)
                    payment = await PaymentService.get_payment_by_booking(db, booking_uuid)
                except ValueError:
                    return {
                        "success": False,
                        "error": "ID booking không hợp lệ"
                    }
            else:
                return {
                    "success": False,
                    "error": "Cần cung cấp payment_id hoặc booking_id"
                }

            if not payment:
                return {
                    "success": False,
                    "error": "Không tìm thấy payment"
                }

            return {
                "success": True,
                "payment": {
                    "id": str(payment.id),
                    "booking_id": str(payment.booking_id),
                    "amount": payment.amount,
                    "method": payment.method,
                    "status": payment.status.value,
                    "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None,
                }
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy thông tin payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_pending_payments_count(
        self,
        db: Any
    ) -> Dict[str, Any]:
        """
        Đếm số payment đang chờ xử lý.

        Args:
            db: Database session

        Returns:
            Dict với số lượng
        """
        try:
            count = await PaymentService.get_pending_payments_count(db)

            return {
                "success": True,
                "pending_count": count
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi đếm payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
