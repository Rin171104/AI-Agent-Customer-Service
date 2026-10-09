"""
Authorized Tool Wrapper

Wrapper layer thêm authorization checks vào tool calls.

Usage:
    from src.ai.security.authorized_tools import AuthorizedToolMixin

    class MyTools(AuthorizedToolMixin):
        def __init__(self, user_context: UserContext):
            self._user_context = user_context
            # Initialize actual tools...

        async def create_booking(self, db, ...):
            # Guard check được tự động thêm vào
            self._check_tool_authorization("create_booking")
            # ... actual implementation
"""
from collections.abc import Callable
from functools import wraps
from typing import Any

from src.ai.security.context import UserContext
from src.ai.security.tool_guard import AuthorizationResult, get_tool_guard
from src.utils.logger import logger


class AuthorizationError(Exception):
    """Exception raised when tool call is not authorized"""
    def __init__(self, tool_name: str, reason: str):
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(f"Authorization denied for tool '{tool_name}': {reason}")


class AuthorizedToolMixin:
    """
    Mixin class thêm authorization checks vào tools.

    Usage:
        class MyBookingTools(AuthorizedToolMixin):
            def __init__(self, user_context: UserContext):
                self._user_context = user_context
                self._guard = get_tool_guard()

            async def create_booking(self, db, user_id, trip_id, seat_count):
                # Authorization check được thêm tự động
                self._check_tool_authorization("create_booking")
                # ... actual implementation
    """

    def __init__(self, user_context: UserContext, **kwargs):
        """
        Initialize với user context.

        Args:
            user_context: UserContext từ authenticated request
        """
        super().__init__(**kwargs)
        self._user_context = user_context
        self._guard = get_tool_guard()

    def _check_tool_authorization(
        self,
        tool_name: str,
        raise_on_denied: bool = True
    ) -> AuthorizationResult:
        """
        Kiểm tra authorization cho tool call.

        Args:
            tool_name: Tên tool cần gọi
            raise_on_denied: Nếu True, raise AuthorizationError khi denied

        Returns:
            AuthorizationResult

        Raises:
            AuthorizationError: Khi tool không được phép và raise_on_denied=True
        """
        result = self._guard.authorize(
            tool_name=tool_name,
            user_role=self._user_context.role,
        )

        if not result.is_allowed:
            logger.warning(
                f"Authorization denied: tool={tool_name}, "
                f"role={self._user_context.role.value}, "
                f"reason={result.reason}, "
                f"user_id={self._user_context.user_id}"
            )

            if raise_on_denied:
                raise AuthorizationError(tool_name, result.reason)

        return result

    def _log_tool_call(self, tool_name: str, category: str) -> None:
        """Log tool call"""
        logger.info(
            f"Tool call authorized: tool={tool_name}, "
            f"category={category}, "
            f"user_id={self._user_context.user_id}, "
            f"role={self._user_context.role.value}"
        )


def require_tool_authorization(tool_name: str):
    """
    Decorator để thêm authorization check vào async method.

    Usage:
        class MyTools:
            def __init__(self, user_context):
                self._user_context = user_context

            @require_tool_authorization("create_booking")
            async def create_booking(self, db, ...):
                # Tool call được kiểm tra authorization
                ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check authorization
            if hasattr(self, "_user_context"):
                result = self._check_tool_authorization(tool_name)
                if not result.is_allowed:
                    raise AuthorizationError(tool_name, result.reason)

                # Log authorized call
                category = get_tool_guard().get_tool_category(tool_name)
                self._log_tool_call(tool_name, category)

            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


class AuthorizedTripTools:
    """
    TripTools với authorization checks.

    Wrap TripTools để thêm authorization.
    """

    def __init__(self, user_context: UserContext):
        self._user_context = user_context
        self._guard = get_tool_guard()
        # Import actual tools
        from src.ai.tools.trip_tools import TripTools as BaseTripTools
        self._base = BaseTripTools()

    async def search_trips(self, db: Any, origin=None, destination=None, status=None) -> dict[str, Any]:
        """Tìm kiếm chuyến xe"""
        self._check_tool_authorization("search_trips")
        return await self._base.search_trips(db, origin, destination, status)

    async def get_trip(self, db: Any, trip_id: str) -> dict[str, Any]:
        """Lấy thông tin chuyến xe"""
        self._check_tool_authorization("get_trip")
        return await self._base.get_trip(db, trip_id)

    async def check_available_seats(self, db: Any, trip_id: str, seat_count: int = 1) -> dict[str, Any]:
        """Kiểm tra ghế trống"""
        self._check_tool_authorization("check_available_seats")
        return await self._base.check_available_seats(db, trip_id, seat_count)

    async def get_available_trips_summary(self, db: Any, origin=None, destination=None, min_seats=1) -> dict[str, Any]:
        """Lấy danh sách chuyến xe còn ghế"""
        self._check_tool_authorization("get_available_trips_summary")
        return await self._base.get_available_trips_summary(db, origin, destination, min_seats)


class AuthorizedBookingTools:
    """
    BookingTools với authorization checks.
    """

    def __init__(self, user_context: UserContext):
        self._user_context = user_context
        self._guard = get_tool_guard()
        from src.ai.tools.booking_tools import BookingTools as BaseBookingTools
        self._base = BaseBookingTools()

    async def create_booking(self, db: Any, user_id: str, trip_id: str, seat_count: int) -> dict[str, Any]:
        """Tạo booking mới"""
        self._check_tool_authorization("create_booking")
        return await self._base.create_booking(db, user_id, trip_id, seat_count)

    async def get_booking(self, db: Any, booking_id: str | None = None, booking_code: str | None = None) -> dict[str, Any]:
        """Lấy thông tin booking"""
        self._check_tool_authorization("get_booking")
        return await self._base.get_booking(db, booking_id, booking_code)

    async def get_user_bookings(self, db: Any, user_id: str) -> dict[str, Any]:
        """Lấy danh sách booking của user"""
        self._check_tool_authorization("get_user_bookings")
        return await self._base.get_user_bookings(db, user_id)

    async def cancel_booking(self, db: Any, booking_id: str, user_id: str) -> dict[str, Any]:
        """Hủy booking"""
        self._check_tool_authorization("cancel_booking")
        return await self._base.cancel_booking(db, booking_id, user_id)

    async def get_all_bookings(self, db: Any, status: str | None = None) -> dict[str, Any]:
        """Lấy tất cả bookings (owner only)"""
        self._check_tool_authorization("get_all_bookings")
        return await self._base.get_all_bookings(db, status)


class AuthorizedPaymentTools:
    """
    PaymentTools với authorization checks.
    """

    def __init__(self, user_context: UserContext):
        self._user_context = user_context
        self._guard = get_tool_guard()
        from src.ai.tools.payment_tools import PaymentTools as BasePaymentTools
        self._base = BasePaymentTools()

    async def create_payment(self, db: Any, booking_id: str, actor_id: str | None = None, actor_type: str = "CUSTOMER") -> dict[str, Any]:
        """Tạo payment"""
        self._check_tool_authorization("create_payment")
        return await self._base.create_payment(db, booking_id, actor_id, actor_type)

    async def get_payment(self, db: Any, payment_id: str | None = None, booking_id: str | None = None) -> dict[str, Any]:
        """Lấy thông tin payment"""
        self._check_tool_authorization("get_payment")
        return await self._base.get_payment(db, payment_id, booking_id)

    async def process_payment(self, db: Any, payment_id: str, success: bool = True, actor_id: str | None = None, actor_type: str = "CUSTOMER") -> dict[str, Any]:
        """
        Xử lý payment (owner/internal only - sẽ bị DENY cho AI Agent).
        """
        self._check_tool_authorization("process_payment")
        return await self._base.process_payment(db, payment_id, success, actor_id, actor_type)


class AuthorizedComplaintTools:
    """
    ComplaintTools với authorization checks.
    """

    def __init__(self, user_context: UserContext):
        self._user_context = user_context
        self._guard = get_tool_guard()
        from src.ai.tools.complaint_tools import ComplaintTools as BaseComplaintTools
        self._base = BaseComplaintTools()

    async def create_complaint(
        self,
        db: Any,
        customer_id: str,
        complaint_type: str,
        description: str,
        booking_id: str | None = None,
        priority: str = "MEDIUM"
    ) -> dict[str, Any]:
        """Tạo khiếu nại"""
        self._check_tool_authorization("create_complaint")
        return await self._base.create_complaint(db, customer_id, complaint_type, description, booking_id, priority)

    async def get_complaint(self, db: Any, complaint_id: str) -> dict[str, Any]:
        """Lấy thông tin khiếu nại"""
        self._check_tool_authorization("get_complaint")
        return await self._base.get_complaint(db, complaint_id)

    async def get_customer_complaints(self, db: Any, customer_id: str) -> dict[str, Any]:
        """Lấy khiếu nại của customer"""
        self._check_tool_authorization("get_customer_complaints")
        return await self._base.get_customer_complaints(db, customer_id)

    async def get_all_complaints(self, db: Any, status: str | None = None, priority: str | None = None) -> dict[str, Any]:
        """Lấy tất cả khiếu nại (owner only)"""
        self._check_tool_authorization("get_all_complaints")
        return await self._base.get_all_complaints(db, status, priority)

    async def resolve_complaint(self, db: Any, complaint_id: str, owner_id: str, owner_note: str) -> dict[str, Any]:
        """
        Giải quyết khiếu nại (owner/internal only - sẽ bị DENY cho AI Agent).
        """
        self._check_tool_authorization("resolve_complaint")
        return await self._base.resolve_complaint(db, complaint_id, owner_id, owner_note)


class AuthorizedRefundTools:
    """
    RefundTools với authorization checks.
    """

    def __init__(self, user_context: UserContext):
        self._user_context = user_context
        self._guard = get_tool_guard()
        from src.ai.tools.refund_tools import RefundTools as BaseRefundTools
        self._base = BaseRefundTools()

    async def create_refund_request(
        self,
        db: Any,
        customer_id: str,
        booking_id: str,
        amount: int,
        bank_name: str,
        account_number: str,
        account_holder: str,
        complaint_id: str | None = None,
        reason: str | None = None
    ) -> dict[str, Any]:
        """Tạo yêu cầu hoàn tiền"""
        self._check_tool_authorization("create_refund_request")
        return await self._base.create_refund_request(
            db, customer_id, booking_id, amount, bank_name, account_number, account_holder, complaint_id, reason
        )

    async def get_refund(self, db: Any, refund_id: str) -> dict[str, Any]:
        """Lấy thông tin refund"""
        self._check_tool_authorization("get_refund")
        return await self._base.get_refund(db, refund_id)

    async def get_customer_refunds(self, db: Any, customer_id: str) -> dict[str, Any]:
        """Lấy refunds của customer"""
        self._check_tool_authorization("get_customer_refunds")
        return await self._base.get_customer_refunds(db, customer_id)

    async def get_all_refunds(self, db: Any, status: str | None = None) -> dict[str, Any]:
        """Lấy tất cả refunds (owner only)"""
        self._check_tool_authorization("get_all_refunds")
        return await self._base.get_all_refunds(db, status)

    async def approve_refund(self, db: Any, refund_id: str, owner_id: str) -> dict[str, Any]:
        """
        Phê duyệt refund (owner/internal only - sẽ bị DENY cho AI Agent).
        """
        self._check_tool_authorization("approve_refund")
        return await self._base.approve_refund(db, refund_id, owner_id)

    async def reject_refund(self, db: Any, refund_id: str, owner_id: str, note: str) -> dict[str, Any]:
        """
        Từ chối refund (owner/internal only - sẽ bị DENY cho AI Agent).
        """
        self._check_tool_authorization("reject_refund")
        return await self._base.reject_refund(db, refund_id, owner_id, note)

    async def mark_as_refunded(self, db: Any, refund_id: str, owner_id: str) -> dict[str, Any]:
        """
        Đánh dấu đã hoàn tiền (owner/internal only - sẽ bị DENY cho AI Agent).
        """
        self._check_tool_authorization("mark_as_refunded")
        return await self._base.mark_as_refunded(db, refund_id, owner_id)
