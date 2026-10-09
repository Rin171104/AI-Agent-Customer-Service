"""
Tool Permission Guard

Security layer đảm bảo LLM/AI chỉ được gọi tools mà role được phép.

Principles:
1. Fail closed - Unknown tool/role → DENY
2. Exact allowlist - Không dùng pattern matching nguy hiểm
3. Role từ authenticated context - Không tin user input tùy ý
4. Defense in depth - Guard không thay thế Service/Tool authorization

Architecture:
    LLM/Agent → ToolGuard.authorize() → Tool → Service → DB
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AuthorizationStatus(str, Enum):
    """Kết quả authorization"""
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


class Role(str, Enum):
    """User roles"""
    CUSTOMER = "CUSTOMER"
    OWNER = "OWNER"
    UNKNOWN = "UNKNOWN"


# ============================================================
# TOOL ALLOWLISTS
# ============================================================

# Customer tools - AI Agent có thể gọi cho customer
CUSTOMER_TOOLS: frozenset[str] = frozenset([
    # Trip read
    "search_trips",
    "get_trip",
    "check_available_seats",
    "get_available_trips_summary",
    # Booking
    "create_booking",
    "get_booking",
    "get_user_bookings",
    "cancel_booking",
    # Payment
    "create_payment",
    "get_payment",
    # Complaint
    "create_complaint",
    "get_complaint",
    "get_customer_complaints",
    # Refund
    "create_refund_request",
    "get_refund",
    "get_customer_refunds",
    # RAG
    "search_knowledge",
    "format_response",
    "should_use_rag",
])

# Owner tools - AI Agent có thể gọi cho owner
OWNER_TOOLS: frozenset[str] = frozenset([
    # All customer tools
    *CUSTOMER_TOOLS,
    # Owner-only read
    "get_all_bookings",
    "get_all_complaints",
    "get_all_refunds",
    # Owner-only write
    "approve_refund",
    "reject_refund",
    "mark_as_refunded",
    "resolve_complaint",
    "process_payment",
])

# Owner-only tools - KHÔNG BAO GIỜ gọi từ AI Agent (phải qua Owner Dashboard)
INTERNAL_OWNER_ONLY: frozenset[str] = frozenset([
    "approve_refund",
    "reject_refund",
    "mark_as_refunded",
    "process_payment",
    "resolve_complaint",
])


# ============================================================
# AUTHORIZATION RESULT
# ============================================================

@dataclass(frozen=True)
class AuthorizationResult:
    """
    Kết quả authorization check.

    Attributes:
        is_allowed: True nếu được phép gọi
        status: AuthorizationStatus enum
        reason: Mã lý do (for denied)
        tool_name: Tên tool được kiểm tra
        user_role: Role của user
    """
    is_allowed: bool
    status: AuthorizationStatus
    reason: str
    tool_name: str
    user_role: Role

    @staticmethod
    def allowed(tool_name: str, role: Role) -> "AuthorizationResult":
        """Tạo kết quả ALLOWED"""
        return AuthorizationResult(
            is_allowed=True,
            status=AuthorizationStatus.ALLOWED,
            reason="OK",
            tool_name=tool_name,
            user_role=role,
        )

    @staticmethod
    def denied(
        tool_name: str,
        role: Role,
        reason: str
    ) -> "AuthorizationResult":
        """Tạo kết quả DENIED"""
        return AuthorizationResult(
            is_allowed=False,
            status=AuthorizationStatus.DENIED,
            reason=reason,
            tool_name=tool_name,
            user_role=role,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert sang dict để log/debug"""
        return {
            "allowed": self.is_allowed,
            "status": self.status.value,
            "reason": self.reason,
            "tool": self.tool_name,
            "role": self.user_role.value,
        }


# ============================================================
# TOOL GUARD
# ============================================================

class ToolGuard:
    """
    Tool Permission Guard

    Security layer để authorize tool calls từ AI/LLM.

    Usage:
        guard = ToolGuard()
        result = guard.authorize(
            tool_name="approve_refund",
            user_role=Role.CUSTOMER,
        )
        if not result.is_allowed:
            raise PermissionError(f"Denied: {result.reason}")
    """

    def __init__(self):
        self._customer_tools = CUSTOMER_TOOLS
        self._owner_tools = OWNER_TOOLS
        self._internal_only = INTERNAL_OWNER_ONLY

    def authorize(
        self,
        tool_name: str,
        user_role: Role,
    ) -> AuthorizationResult:
        """
        Kiểm tra xem user có được phép gọi tool không.

        Args:
            tool_name: Tên tool cần gọi
            user_role: Role của user (CUSTOMER/OWNER)

        Returns:
            AuthorizationResult với ALLOWED hoặc DENIED
        """
        # === STEP 1: Input Validation ===
        # Empty tool name → DENY
        if not tool_name or not isinstance(tool_name, str):
            return AuthorizationResult.denied(
                tool_name=str(tool_name),
                role=user_role,
                reason="INVALID_TOOL_NAME",
            )

        # Normalize tool name
        normalized_tool = tool_name.strip().lower()

        # === STEP 2: Unknown Role → DENY ===
        if user_role == Role.UNKNOWN:
            return AuthorizationResult.denied(
                tool_name=normalized_tool,
                role=user_role,
                reason="UNKNOWN_ROLE",
            )

        # === STEP 3: Tool not in allowlist → DENY ===
        if user_role == Role.CUSTOMER:
            if normalized_tool not in self._customer_tools:
                return AuthorizationResult.denied(
                    tool_name=normalized_tool,
                    role=user_role,
                    reason="TOOL_NOT_IN_ALLOWLIST",
                )

        elif user_role == Role.OWNER:
            if normalized_tool not in self._owner_tools:
                return AuthorizationResult.denied(
                    tool_name=normalized_tool,
                    role=user_role,
                    reason="TOOL_NOT_IN_ALLOWLIST",
                )

        # === STEP 4: Special check for internal-only tools ===
        # Even owner cannot call these via AI Agent
        if normalized_tool in self._internal_only:
            return AuthorizationResult.denied(
                tool_name=normalized_tool,
                role=user_role,
                reason="INTERNAL_ONLY_TOOL",
            )

        # === STEP 5: ALLOWED ===
        return AuthorizationResult.allowed(
            tool_name=normalized_tool,
            role=user_role,
        )

    def authorize_or_raise(
        self,
        tool_name: str,
        user_role: Role,
    ) -> None:
        """
        Kiểm tra và raise exception nếu denied.

        Args:
            tool_name: Tên tool cần gọi
            user_role: Role của user

        Raises:
            PermissionError: Nếu tool không được phép
        """
        result = self.authorize(tool_name, user_role)
        if not result.is_allowed:
            raise PermissionError(
                f"Authorization denied for tool '{tool_name}': {result.reason}"
            )

    def get_allowed_tools(self, role: Role) -> frozenset[str]:
        """
        Lấy danh sách tools được phép cho role.

        Args:
            role: User role

        Returns:
            FrozenSet chứa các tool names
        """
        if role == Role.CUSTOMER:
            return self._customer_tools
        elif role == Role.OWNER:
            # For owner, exclude internal-only tools from AI access
            return frozenset(t for t in self._owner_tools if t not in self._internal_only)
        else:
            return frozenset()

    def is_internal_only(self, tool_name: str) -> bool:
        """Kiểm tra tool có phải internal-only không"""
        return tool_name.strip().lower() in self._internal_only

    def get_tool_category(self, tool_name: str) -> str:
        """
        Lấy category của tool (for logging).

        Categories:
            - trip: Trip search/read
            - booking: Booking operations
            - payment: Payment operations
            - complaint: Complaint operations
            - refund: Refund operations
            - rag: Knowledge/RAG
            - internal: Owner-internal tools
        """
        normalized = tool_name.strip().lower()

        # Ưu tiên nhóm nội bộ trước nhóm nghiệp vụ.
        if normalized in self._internal_only:
            return "internal"

        trip_tools = {"search_trips", "get_trip", "check_available_seats", "get_available_trips_summary"}
        booking_tools = {"create_booking", "get_booking", "get_user_bookings", "cancel_booking", "get_all_bookings"}
        payment_tools = {"create_payment", "get_payment", "process_payment"}
        complaint_tools = {"create_complaint", "get_complaint", "get_customer_complaints", "get_all_complaints", "resolve_complaint"}
        refund_tools = {"create_refund_request", "get_refund", "get_customer_refunds", "get_all_refunds", "approve_refund", "reject_refund", "mark_as_refunded"}
        rag_tools = {"search_knowledge", "format_response", "should_use_rag"}

        if normalized in trip_tools:
            return "trip"
        elif normalized in booking_tools:
            return "booking"
        elif normalized in payment_tools:
            return "payment"
        elif normalized in complaint_tools:
            return "complaint"
        elif normalized in refund_tools:
            return "refund"
        elif normalized in rag_tools:
            return "rag"
        else:
            return "unknown"


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_tool_guard: ToolGuard | None = None


def get_tool_guard() -> ToolGuard:
    """Get singleton ToolGuard instance"""
    global _tool_guard
    if _tool_guard is None:
        _tool_guard = ToolGuard()
    return _tool_guard
