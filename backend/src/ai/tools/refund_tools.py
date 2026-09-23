"""
Refund Tools - AI Tools cho domain hoàn tiền

Kết nối: Agent -> RefundTools -> RefundService -> Database
"""
from typing import Dict, Any, Optional
from uuid import UUID

from src.services.refund_service import RefundService
from src.services.booking_service import BookingService
from src.models import RefundStatus, ActorType
from src.schemas import RefundCreate
from src.services.audit_service import AuditService
from src.utils.logger import logger


class RefundTools:
    """AI Tools cho hoàn tiền - kết nối thật với RefundService"""

    def __init__(self):
        self.logger = logger

    async def create_refund_request(
        self,
        db: Any,
        customer_id: str,
        booking_id: str,
        amount: int,
        bank_name: str,
        account_number: str,
        account_holder: str,
        complaint_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tạo yêu cầu hoàn tiền.

        Args:
            db: Database session
            customer_id: ID của khách hàng
            booking_id: ID của booking
            amount: Số tiền muốn hoàn
            bank_name: Tên ngân hàng
            account_number: Số tài khoản
            account_holder: Tên chủ tài khoản
            complaint_id: ID của khiếu nại liên quan (nếu có)
            reason: Lý do hoàn tiền

        Returns:
            Dict với thông tin refund
        """
        try:
            try:
                customer_uuid = UUID(customer_id)
                booking_uuid = UUID(booking_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            # Validate amount
            if amount < 1000:
                return {
                    "success": False,
                    "error": "Số tiền hoàn phải lớn hơn 1000 VND"
                }

            # Kiểm tra booking tồn tại
            booking = await BookingService.get_booking_by_id(db, booking_uuid)
            if not booking:
                return {
                    "success": False,
                    "error": "Booking không tồn tại"
                }

            # Kiểm tra booking thuộc về customer
            if booking.user_id != customer_uuid:
                return {
                    "success": False,
                    "error": "Bạn không có quyền yêu cầu hoàn tiền cho booking này"
                }

            # Validate complaint_id nếu có
            complaint_uuid = None
            if complaint_id:
                try:
                    complaint_uuid = UUID(complaint_id)
                except ValueError:
                    return {
                        "success": False,
                        "error": "ID khiếu nại không hợp lệ"
                    }

            # Tạo refund request
            refund_data = RefundCreate(
                complaint_id=complaint_uuid,
                booking_id=booking_uuid,
                amount=amount,
                bank_name=bank_name,
                account_number=account_number,
                account_holder=account_holder,
                reason=reason
            )

            refund = await RefundService.create_refund(db, customer_uuid, refund_data)

            # Tạo audit log
            await AuditService.create_log(
                db=db,
                actor_type=ActorType.CUSTOMER,
                actor_id=customer_uuid,
                action="AI_CREATE_REFUND",
                entity_type="RefundRequest",
                entity_id=refund.id,
                description=f"Tạo yêu cầu hoàn tiền {refund.refund_code} qua AI",
                metadata={
                    "booking_id": str(booking_id),
                    "amount": amount,
                    "bank": bank_name,
                }
            )

            return {
                "success": True,
                "refund": {
                    "id": str(refund.id),
                    "refund_code": refund.refund_code,
                    "booking_id": str(refund.booking_id),
                    "amount": refund.amount,
                    "bank_name": refund.bank_name,
                    "account_number": refund.account_number,
                    "account_holder": refund.account_holder,
                    "status": refund.status.value,
                    "reason": refund.reason,
                    "created_at": refund.created_at.isoformat() if refund.created_at else None,
                },
                "message": f"Yêu cầu hoàn tiền đã được tạo. Mã: {refund.refund_code}. Vui lòng chờ owner phê duyệt."
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi tạo yêu cầu hoàn tiền: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_refund(
        self,
        db: Any,
        refund_id: str
    ) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết refund.

        Args:
            db: Database session
            refund_id: ID của refund

        Returns:
            Dict với thông tin refund
        """
        try:
            try:
                refund_uuid = UUID(refund_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID refund không hợp lệ"
                }

            refund = await RefundService.get_refund_by_id(db, refund_uuid)

            if not refund:
                return {
                    "success": False,
                    "error": "Không tìm thấy yêu cầu hoàn tiền"
                }

            result = {
                "id": str(refund.id),
                "refund_code": refund.refund_code,
                "complaint_id": str(refund.complaint_id) if refund.complaint_id else None,
                "booking_id": str(refund.booking_id),
                "amount": refund.amount,
                "bank_name": refund.bank_name,
                "account_number": refund.account_number,
                "account_holder": refund.account_holder,
                "reason": refund.reason,
                "status": refund.status.value,
                "owner_note": refund.owner_note,
                "created_at": refund.created_at.isoformat() if refund.created_at else None,
                "updated_at": refund.updated_at.isoformat() if refund.updated_at else None,
            }

            # Include booking info if loaded
            if refund.booking:
                result["booking"] = {
                    "id": str(refund.booking.id),
                    "booking_code": refund.booking.booking_code,
                    "total_amount": refund.booking.total_amount,
                    "status": refund.booking.status.value,
                }

            # Include complaint info if loaded
            if refund.complaint:
                result["complaint"] = {
                    "id": str(refund.complaint.id),
                    "complaint_code": refund.complaint.complaint_code,
                    "type": refund.complaint.type.value,
                    "status": refund.complaint.status.value,
                }

            return {
                "success": True,
                "refund": result
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy thông tin refund: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_customer_refunds(
        self,
        db: Any,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Lấy danh sách refund của khách hàng.

        Args:
            db: Database session
            customer_id: ID của khách hàng

        Returns:
            Dict với danh sách refunds
        """
        try:
            try:
                customer_uuid = UUID(customer_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID customer không hợp lệ"
                }

            refunds = await RefundService.get_refunds_by_customer(db, customer_uuid)

            refund_list = []
            for refund in refunds:
                refund_list.append({
                    "id": str(refund.id),
                    "refund_code": refund.refund_code,
                    "booking_id": str(refund.booking_id),
                    "amount": refund.amount,
                    "bank_name": refund.bank_name,
                    "status": refund.status.value,
                    "created_at": refund.created_at.isoformat() if refund.created_at else None,
                })

            return {
                "success": True,
                "count": len(refund_list),
                "refunds": refund_list
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách refund: {e}")
            return {
                "success": False,
                "error": str(e),
                "refunds": []
            }

    async def get_all_refunds(
        self,
        db: Any,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy tất cả refunds (cho owner).

        Args:
            db: Database session
            status: Filter theo status

        Returns:
            Dict với danh sách refunds
        """
        try:
            refund_status = None
            if status:
                try:
                    refund_status = RefundStatus(status.upper())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Status không hợp lệ: {status}"
                    }

            refunds = await RefundService.get_all_refunds(db, status=refund_status)

            refund_list = []
            for refund in refunds:
                item = {
                    "id": str(refund.id),
                    "refund_code": refund.refund_code,
                    "booking_id": str(refund.booking_id),
                    "amount": refund.amount,
                    "bank_name": refund.bank_name,
                    "account_number": refund.account_number,
                    "account_holder": refund.account_holder,
                    "status": refund.status.value,
                    "reason": refund.reason,
                    "created_at": refund.created_at.isoformat() if refund.created_at else None,
                }
                if refund.booking:
                    item["booking_code"] = refund.booking.booking_code
                refund_list.append(item)

            return {
                "success": True,
                "count": len(refund_list),
                "refunds": refund_list
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách refunds: {e}")
            return {
                "success": False,
                "error": str(e),
                "refunds": []
            }

    async def approve_refund(
        self,
        db: Any,
        refund_id: str,
        owner_id: str
    ) -> Dict[str, Any]:
        """
        Owner phê duyệt refund.

        Args:
            db: Database session
            refund_id: ID của refund
            owner_id: ID của owner

        Returns:
            Dict với kết quả
        """
        try:
            try:
                refund_uuid = UUID(refund_id)
                owner_uuid = UUID(owner_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            refund = await RefundService.get_refund_by_id(db, refund_uuid)
            if not refund:
                return {
                    "success": False,
                    "error": "Không tìm thấy yêu cầu hoàn tiền"
                }

            if refund.status != RefundStatus.WAITING_OWNER_APPROVAL:
                return {
                    "success": False,
                    "error": f"Refund đang ở trạng thái {refund.status.value}, không thể duyệt"
                }

            updated = await RefundService.approve_refund(db, refund_uuid, owner_uuid)

            return {
                "success": True,
                "message": "Đã phê duyệt yêu cầu hoàn tiền",
                "refund": {
                    "id": str(updated.id),
                    "refund_code": updated.refund_code,
                    "status": updated.status.value,
                    "amount": updated.amount,
                    "account_holder": updated.account_holder,
                },
                "next_step": "Vui lòng thực hiện hoàn tiền và đánh dấu đã hoàn tiền"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Lỗi khi duyệt refund: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def reject_refund(
        self,
        db: Any,
        refund_id: str,
        owner_id: str,
        note: str
    ) -> Dict[str, Any]:
        """
        Owner từ chối refund.

        Args:
            db: Database session
            refund_id: ID của refund
            owner_id: ID của owner
            note: Lý do từ chối

        Returns:
            Dict với kết quả
        """
        try:
            try:
                refund_uuid = UUID(refund_id)
                owner_uuid = UUID(owner_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            if not note or len(note.strip()) == 0:
                return {
                    "success": False,
                    "error": "Cần cung cấp lý do từ chối"
                }

            refund = await RefundService.get_refund_by_id(db, refund_uuid)
            if not refund:
                return {
                    "success": False,
                    "error": "Không tìm thấy yêu cầu hoàn tiền"
                }

            if refund.status != RefundStatus.WAITING_OWNER_APPROVAL:
                return {
                    "success": False,
                    "error": f"Refund đang ở trạng thái {refund.status.value}, không thể từ chối"
                }

            updated = await RefundService.reject_refund(db, refund_uuid, owner_uuid, note)

            return {
                "success": True,
                "message": "Đã từ chối yêu cầu hoàn tiền",
                "refund": {
                    "id": str(updated.id),
                    "refund_code": updated.refund_code,
                    "status": updated.status.value,
                    "owner_note": updated.owner_note,
                }
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Lỗi khi từ chối refund: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def mark_as_refunded(
        self,
        db: Any,
        refund_id: str,
        owner_id: str
    ) -> Dict[str, Any]:
        """
        Owner đánh dấu đã hoàn tiền.

        Args:
            db: Database session
            refund_id: ID của refund
            owner_id: ID của owner

        Returns:
            Dict với kết quả
        """
        try:
            try:
                refund_uuid = UUID(refund_id)
                owner_uuid = UUID(owner_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            refund = await RefundService.get_refund_by_id(db, refund_uuid)
            if not refund:
                return {
                    "success": False,
                    "error": "Không tìm thấy yêu cầu hoàn tiền"
                }

            if refund.status != RefundStatus.APPROVED:
                return {
                    "success": False,
                    "error": f"Refund đang ở trạng thái {refund.status.value}, cần duyệt trước"
                }

            updated = await RefundService.mark_as_refunded(db, refund_uuid, owner_uuid)

            return {
                "success": True,
                "message": "Đã đánh dấu hoàn tiền thành công",
                "refund": {
                    "id": str(updated.id),
                    "refund_code": updated.refund_code,
                    "status": updated.status.value,
                    "amount": updated.amount,
                    "account_holder": updated.account_holder,
                }
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Lỗi khi đánh dấu hoàn tiền: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_pending_refunds_count(
        self,
        db: Any
    ) -> Dict[str, Any]:
        """
        Đếm số refund đang chờ duyệt.

        Args:
            db: Database session

        Returns:
            Dict với số lượng
        """
        try:
            count = await RefundService.get_pending_refunds_count(db)

            return {
                "success": True,
                "pending_count": count
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi đếm refund: {e}")
            return {
                "success": False,
                "error": str(e)
            }
