"""
AI Tool Layer - Cầu nối giữa Agent và hệ thống nghiệp vụ

Kiến trúc:
    Agent -> Tool -> Service -> Database

Mỗi Tool có nhiệm vụ:
    - Nhận input
    - Validate input
    - Check authorization
    - Gọi Service hiện tại
    - Trả về kết quả có cấu trúc

Tool KHÔNG được tự viết business logic.
"""

from src.ai.tools.trip_tools import TripTools
from src.ai.tools.booking_tools import BookingTools
from src.ai.tools.payment_tools import PaymentTools
from src.ai.tools.complaint_tools import ComplaintTools
from src.ai.tools.refund_tools import RefundTools

__all__ = [
    "TripTools",
    "BookingTools",
    "PaymentTools",
    "ComplaintTools",
    "RefundTools",
]
