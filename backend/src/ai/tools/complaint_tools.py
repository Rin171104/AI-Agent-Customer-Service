"""
Complaint Tools - AI Tools cho domain khiếu nại

Kết nối: Agent -> ComplaintTools -> ComplaintService -> Database
"""
from typing import Dict, Any, List, Optional
from uuid import UUID

from src.services.complaint_service import ComplaintService
from src.services.booking_service import BookingService
from src.models import ComplaintStatus, ComplaintType, ComplaintPriority, ActorType
from src.schemas import ComplaintCreate, ComplaintUpdate
from src.services.audit_service import AuditService
from src.utils.logger import logger


class ComplaintTools:
    """AI Tools cho khiếu nại - kết nối thật với ComplaintService"""

    def __init__(self):
        self.logger = logger

    async def create_complaint(
        self,
        db: Any,
        customer_id: str,
        complaint_type: str,
        description: str,
        booking_id: Optional[str] = None,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Tạo khiếu nại mới.

        Args:
            db: Database session
            customer_id: ID của khách hàng
            complaint_type: Loại khiếu nại (WRONG_SEAT, LATE, DRIVER, etc.)
            description: Mô tả khiếu nại
            booking_id: ID của booking liên quan (nếu có)
            priority: Mức độ ưu tiên (LOW, MEDIUM, HIGH)

        Returns:
            Dict với thông tin khiếu nại
        """
        try:
            try:
                customer_uuid = UUID(customer_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID customer không hợp lệ"
                }

            # Validate complaint_type
            try:
                c_type = ComplaintType(complaint_type.upper())
            except ValueError:
                valid_types = [t.value for t in ComplaintType]
                return {
                    "success": False,
                    "error": f"Loại khiếu nại không hợp lệ: {complaint_type}. Các loại hợp lệ: {', '.join(valid_types)}"
                }

            # Validate priority
            try:
                c_priority = ComplaintPriority(priority.upper())
            except ValueError:
                valid_priorities = [p.value for p in ComplaintPriority]
                return {
                    "success": False,
                    "error": f"Mức ưu tiên không hợp lệ: {priority}. Các mức hợp lệ: {', '.join(valid_priorities)}"
                }

            # Validate booking_id nếu có
            booking_uuid = None
            if booking_id:
                try:
                    booking_uuid = UUID(booking_id)
                    # Kiểm tra booking tồn tại
                    booking = await BookingService.get_booking_by_id(db, booking_uuid)
                    if not booking:
                        return {
                            "success": False,
                            "error": "Booking không tồn tại"
                        }
                except ValueError:
                    return {
                        "success": False,
                        "error": "ID booking không hợp lệ"
                    }

            # Tạo complaint
            complaint_data = ComplaintCreate(
                booking_id=booking_uuid,
                type=c_type,
                description=description,
                priority=c_priority
            )

            complaint = await ComplaintService.create_complaint(db, customer_uuid, complaint_data)

            # Tạo audit log
            await AuditService.create_log(
                db=db,
                actor_type=ActorType.CUSTOMER,
                actor_id=customer_uuid,
                action="AI_CREATE_COMPLAINT",
                entity_type="Complaint",
                entity_id=complaint.id,
                description=f"Tạo khiếu nại {complaint.complaint_code} qua AI",
                metadata={
                    "complaint_type": complaint_type,
                    "booking_id": str(booking_id) if booking_id else None,
                }
            )

            return {
                "success": True,
                "complaint": {
                    "id": str(complaint.id),
                    "complaint_code": complaint.complaint_code,
                    "type": complaint.type.value,
                    "description": complaint.description,
                    "status": complaint.status.value,
                    "priority": complaint.priority.value,
                    "booking_id": str(complaint.booking_id) if complaint.booking_id else None,
                    "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                }
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi tạo khiếu nại: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_complaint(
        self,
        db: Any,
        complaint_id: str
    ) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết khiếu nại.

        Args:
            db: Database session
            complaint_id: ID của khiếu nại

        Returns:
            Dict với thông tin khiếu nại
        """
        try:
            try:
                complaint_uuid = UUID(complaint_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID khiếu nại không hợp lệ"
                }

            complaint = await ComplaintService.get_complaint_by_id(db, complaint_uuid)

            if not complaint:
                return {
                    "success": False,
                    "error": "Không tìm thấy khiếu nại"
                }

            result = {
                "id": str(complaint.id),
                "complaint_code": complaint.complaint_code,
                "customer_id": str(complaint.customer_id),
                "type": complaint.type.value,
                "description": complaint.description,
                "status": complaint.status.value,
                "priority": complaint.priority.value,
                "owner_note": complaint.owner_note,
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
            }

            # Include booking info if loaded
            if complaint.booking:
                result["booking"] = {
                    "id": str(complaint.booking.id),
                    "booking_code": complaint.booking.booking_code,
                    "seat_count": complaint.booking.seat_count,
                    "total_amount": complaint.booking.total_amount,
                    "status": complaint.booking.status.value,
                }

            return {
                "success": True,
                "complaint": result
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy thông tin khiếu nại: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_customer_complaints(
        self,
        db: Any,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Lấy danh sách khiếu nại của khách hàng.

        Args:
            db: Database session
            customer_id: ID của khách hàng

        Returns:
            Dict với danh sách khiếu nại
        """
        try:
            try:
                customer_uuid = UUID(customer_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID customer không hợp lệ"
                }

            complaints = await ComplaintService.get_complaints_by_customer(db, customer_uuid)

            complaint_list = []
            for complaint in complaints:
                complaint_list.append({
                    "id": str(complaint.id),
                    "complaint_code": complaint.complaint_code,
                    "type": complaint.type.value,
                    "description": complaint.description[:100] + "..." if len(complaint.description) > 100 else complaint.description,
                    "status": complaint.status.value,
                    "priority": complaint.priority.value,
                    "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                })

            return {
                "success": True,
                "count": len(complaint_list),
                "complaints": complaint_list
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách khiếu nại: {e}")
            return {
                "success": False,
                "error": str(e),
                "complaints": []
            }

    async def get_all_complaints(
        self,
        db: Any,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy tất cả khiếu nại (cho owner).

        Args:
            db: Database session
            status: Filter theo status
            priority: Filter theo priority

        Returns:
            Dict với danh sách khiếu nại
        """
        try:
            complaint_status = None
            if status:
                try:
                    complaint_status = ComplaintStatus(status.upper())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Status không hợp lệ: {status}"
                    }

            complaint_priority = None
            if priority:
                try:
                    complaint_priority = ComplaintPriority(priority.upper())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Priority không hợp lệ: {priority}"
                    }

            complaints = await ComplaintService.get_all_complaints(
                db,
                status=complaint_status,
                priority=complaint_priority
            )

            complaint_list = []
            for complaint in complaints:
                item = {
                    "id": str(complaint.id),
                    "complaint_code": complaint.complaint_code,
                    "customer_id": str(complaint.customer_id),
                    "type": complaint.type.value,
                    "description": complaint.description[:100] + "..." if len(complaint.description) > 100 else complaint.description,
                    "status": complaint.status.value,
                    "priority": complaint.priority.value,
                    "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                }
                if complaint.booking:
                    item["booking_code"] = complaint.booking.booking_code
                complaint_list.append(item)

            return {
                "success": True,
                "count": len(complaint_list),
                "complaints": complaint_list
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách khiếu nại: {e}")
            return {
                "success": False,
                "error": str(e),
                "complaints": []
            }

    async def resolve_complaint(
        self,
        db: Any,
        complaint_id: str,
        owner_id: str,
        owner_note: str
    ) -> Dict[str, Any]:
        """
        Giải quyết khiếu nại (chỉ owner).

        Args:
            db: Database session
            complaint_id: ID của khiếu nại
            owner_id: ID của owner
            owner_note: Ghi chú của owner

        Returns:
            Dict với kết quả
        """
        try:
            try:
                complaint_uuid = UUID(complaint_id)
                owner_uuid = UUID(owner_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "ID không hợp lệ"
                }

            # Kiểm tra complaint tồn tại
            complaint = await ComplaintService.get_complaint_by_id(db, complaint_uuid)
            if not complaint:
                return {
                    "success": False,
                    "error": "Không tìm thấy khiếu nại"
                }

            # Kiểm tra đã resolved chưa
            if complaint.status == ComplaintStatus.RESOLVED:
                return {
                    "success": False,
                    "error": "Khiếu nại đã được giải quyết"
                }

            # Resolve complaint
            updated = await ComplaintService.resolve_complaint(db, complaint_uuid, owner_note)

            # Tạo audit log
            await AuditService.create_log(
                db=db,
                actor_type=ActorType.OWNER,
                actor_id=owner_uuid,
                action="AI_RESOLVE_COMPLAINT",
                entity_type="Complaint",
                entity_id=complaint_uuid,
                description=f"Giải quyết khiếu nại {complaint.complaint_code} qua AI",
                metadata={
                    "complaint_code": complaint.complaint_code,
                    "owner_note": owner_note
                }
            )

            return {
                "success": True,
                "message": "Đã giải quyết khiếu nại",
                "complaint": {
                    "id": str(updated.id),
                    "complaint_code": updated.complaint_code,
                    "status": updated.status.value,
                    "owner_note": updated.owner_note,
                }
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi giải quyết khiếu nại: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_open_complaints_count(
        self,
        db: Any
    ) -> Dict[str, Any]:
        """
        Đếm số khiếu nại đang mở.

        Args:
            db: Database session

        Returns:
            Dict với số lượng
        """
        try:
            count = await ComplaintService.get_open_complaints_count(db)

            return {
                "success": True,
                "open_count": count
            }

        except Exception as e:
            self.logger.error(f"Lỗi khi đếm khiếu nại: {e}")
            return {
                "success": False,
                "error": str(e)
            }
