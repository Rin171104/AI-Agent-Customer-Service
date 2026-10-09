"""
Tests for Tool Permission Guard

Run: pytest tests/test_tool_guard.py -v
"""
import pytest

from src.ai.security.tool_guard import (
    ToolGuard,
    AuthorizationResult,
    AuthorizationStatus,
    Role,
)


class TestToolGuardBasic:
    """Basic authorization tests"""

    def test_customer_search_trips_allowed(self):
        """Customer → search_trips → ALLOW"""
        guard = ToolGuard()
        result = guard.authorize("search_trips", Role.CUSTOMER)
        assert result.is_allowed is True
        assert result.status == AuthorizationStatus.ALLOWED

    def test_customer_create_booking_allowed(self):
        """Customer → create_booking → ALLOW"""
        guard = ToolGuard()
        result = guard.authorize("create_booking", Role.CUSTOMER)
        assert result.is_allowed is True

    def test_customer_create_refund_request_allowed(self):
        """Customer → create_refund_request → ALLOW"""
        guard = ToolGuard()
        result = guard.authorize("create_refund_request", Role.CUSTOMER)
        assert result.is_allowed is True


class TestToolGuardCustomerDenied:
    """Customer trying to access owner-only tools"""

    def test_customer_approve_refund_denied(self):
        """Customer → approve_refund → DENY"""
        guard = ToolGuard()
        result = guard.authorize("approve_refund", Role.CUSTOMER)
        assert result.is_allowed is False
        assert result.status == AuthorizationStatus.DENIED
        assert result.reason in ["TOOL_NOT_IN_ALLOWLIST", "INTERNAL_ONLY_TOOL"]

    def test_customer_reject_refund_denied(self):
        """Customer → reject_refund → DENY"""
        guard = ToolGuard()
        result = guard.authorize("reject_refund", Role.CUSTOMER)
        assert result.is_allowed is False

    def test_customer_mark_as_refunded_denied(self):
        """Customer → mark_as_refunded → DENY"""
        guard = ToolGuard()
        result = guard.authorize("mark_as_refunded", Role.CUSTOMER)
        assert result.is_allowed is False

    def test_customer_process_payment_denied(self):
        """Customer → process_payment → DENY"""
        guard = ToolGuard()
        result = guard.authorize("process_payment", Role.CUSTOMER)
        assert result.is_allowed is False

    def test_customer_resolve_complaint_denied(self):
        """Customer → resolve_complaint → DENY"""
        guard = ToolGuard()
        result = guard.authorize("resolve_complaint", Role.CUSTOMER)
        assert result.is_allowed is False


class TestToolGuardOwner:
    """Owner authorization tests"""

    def test_owner_approve_refund_denied_internal(self):
        """Owner → approve_refund → DENY (internal-only)"""
        guard = ToolGuard()
        result = guard.authorize("approve_refund", Role.OWNER)
        # Even owner cannot call internal-only tools via AI Agent
        assert result.is_allowed is False
        assert result.reason == "INTERNAL_ONLY_TOOL"

    def test_owner_reject_refund_denied_internal(self):
        """Owner → reject_refund → DENY (internal-only)"""
        guard = ToolGuard()
        result = guard.authorize("reject_refund", Role.OWNER)
        assert result.is_allowed is False
        assert result.reason == "INTERNAL_ONLY_TOOL"

    def test_owner_mark_as_refunded_denied_internal(self):
        """Owner → mark_as_refunded → DENY (internal-only)"""
        guard = ToolGuard()
        result = guard.authorize("mark_as_refunded", Role.OWNER)
        assert result.is_allowed is False
        assert result.reason == "INTERNAL_ONLY_TOOL"

    def test_owner_process_payment_denied_internal(self):
        """Owner → process_payment → DENY (internal-only)"""
        guard = ToolGuard()
        result = guard.authorize("process_payment", Role.OWNER)
        assert result.is_allowed is False
        assert result.reason == "INTERNAL_ONLY_TOOL"

    def test_owner_resolve_complaint_denied_internal(self):
        """Owner → resolve_complaint → DENY (internal-only)"""
        guard = ToolGuard()
        result = guard.authorize("resolve_complaint", Role.OWNER)
        assert result.is_allowed is False
        assert result.reason == "INTERNAL_ONLY_TOOL"

    def test_owner_get_all_bookings_allowed(self):
        """Owner → get_all_bookings → ALLOW"""
        guard = ToolGuard()
        result = guard.authorize("get_all_bookings", Role.OWNER)
        assert result.is_allowed is True

    def test_owner_get_all_complaints_allowed(self):
        """Owner → get_all_complaints → ALLOW"""
        guard = ToolGuard()
        result = guard.authorize("get_all_complaints", Role.OWNER)
        assert result.is_allowed is True

    def test_owner_search_trips_allowed(self):
        """Owner → search_trips → ALLOW"""
        guard = ToolGuard()
        result = guard.authorize("search_trips", Role.OWNER)
        assert result.is_allowed is True

    def test_owner_create_booking_allowed(self):
        """Owner → create_booking → ALLOW"""
        guard = ToolGuard()
        result = guard.authorize("create_booking", Role.OWNER)
        assert result.is_allowed is True


class TestToolGuardUnknownRole:
    """Tests for unknown/invalid roles"""

    def test_unknown_role_denied(self):
        """Unknown → any tool → DENY"""
        guard = ToolGuard()
        result = guard.authorize("search_trips", Role.UNKNOWN)
        assert result.is_allowed is False
        assert result.reason == "UNKNOWN_ROLE"


class TestToolGuardInvalidTool:
    """Tests for invalid/unknown tools"""

    def test_unknown_tool_customer_denied(self):
        """Customer → unknown_tool → DENY"""
        guard = ToolGuard()
        result = guard.authorize("unknown_tool", Role.CUSTOMER)
        assert result.is_allowed is False
        assert result.reason == "TOOL_NOT_IN_ALLOWLIST"

    def test_unknown_tool_owner_denied(self):
        """Owner → unknown_tool → DENY"""
        guard = ToolGuard()
        result = guard.authorize("unknown_tool", Role.OWNER)
        assert result.is_allowed is False
        assert result.reason == "TOOL_NOT_IN_ALLOWLIST"

    def test_empty_tool_name_denied(self):
        """Empty → tool → DENY"""
        guard = ToolGuard()
        result = guard.authorize("", Role.CUSTOMER)
        assert result.is_allowed is False
        assert result.reason == "INVALID_TOOL_NAME"

    def test_none_tool_name_denied(self):
        """None → tool → DENY"""
        guard = ToolGuard()
        result = guard.authorize(None, Role.CUSTOMER)
        assert result.is_allowed is False
        assert result.reason == "INVALID_TOOL_NAME"

    def test_whitespace_tool_name_denied(self):
        """Whitespace tool name → DENY"""
        guard = ToolGuard()
        result = guard.authorize("   ", Role.CUSTOMER)
        assert result.is_allowed is False


class TestToolGuardSpoofing:
    """Tests for tool name spoofing attempts"""

    def test_case_manipulation_denied(self):
        """Case manipulation → DENY (case-sensitive)"""
        guard = ToolGuard()
        # Tool names are normalized to lowercase
        result = guard.authorize("APPROVE_REFUND", Role.CUSTOMER)
        # Should be denied because it's not in the customer allowlist
        assert result.is_allowed is False

    def test_injection_attempt_denied(self):
        """Injection attempt → DENY"""
        guard = ToolGuard()
        result = guard.authorize("approve_refund; rm -rf /", Role.CUSTOMER)
        assert result.is_allowed is False

    def test_sql_injection_attempt_denied(self):
        """SQL injection attempt → DENY"""
        guard = ToolGuard()
        result = guard.authorize("approve_refund' OR '1'='1", Role.CUSTOMER)
        assert result.is_allowed is False


class TestToolGuardAuthorizeOrRaise:
    """Tests for authorize_or_raise method"""

    def test_allowed_no_exception(self):
        """ALLOWED → no exception"""
        guard = ToolGuard()
        # Should not raise
        guard.authorize_or_raise("search_trips", Role.CUSTOMER)

    def test_denied_raises_permission_error(self):
        """DENIED → raises PermissionError"""
        guard = ToolGuard()
        with pytest.raises(PermissionError) as exc_info:
            guard.authorize_or_raise("approve_refund", Role.CUSTOMER)
        assert "Authorization denied" in str(exc_info.value)


class TestToolGuardHelpers:
    """Tests for helper methods"""

    def test_get_allowed_tools_customer(self):
        """Customer gets customer tools only"""
        guard = ToolGuard()
        tools = guard.get_allowed_tools(Role.CUSTOMER)
        assert "search_trips" in tools
        assert "create_booking" in tools
        assert "approve_refund" not in tools

    def test_get_allowed_tools_owner(self):
        """Owner gets owner tools (excluding internal-only)"""
        guard = ToolGuard()
        tools = guard.get_allowed_tools(Role.OWNER)
        assert "search_trips" in tools
        assert "get_all_bookings" in tools
        assert "approve_refund" not in tools  # Internal-only

    def test_get_allowed_tools_unknown(self):
        """Unknown role gets no tools"""
        guard = ToolGuard()
        tools = guard.get_allowed_tools(Role.UNKNOWN)
        assert len(tools) == 0

    def test_is_internal_only(self):
        """is_internal_only returns correct value"""
        guard = ToolGuard()
        assert guard.is_internal_only("approve_refund") is True
        assert guard.is_internal_only("reject_refund") is True
        assert guard.is_internal_only("search_trips") is False

    def test_get_tool_category(self):
        """get_tool_category returns correct category"""
        guard = ToolGuard()
        assert guard.get_tool_category("search_trips") == "trip"
        assert guard.get_tool_category("create_booking") == "booking"
        assert guard.get_tool_category("approve_refund") == "internal"
        assert guard.get_tool_category("search_knowledge") == "rag"


class TestAuthorizationResult:
    """Tests for AuthorizationResult dataclass"""

    def test_result_to_dict(self):
        """to_dict returns correct structure"""
        result = AuthorizationResult(
            is_allowed=False,
            status=AuthorizationStatus.DENIED,
            reason="TOOL_NOT_IN_ALLOWLIST",
            tool_name="approve_refund",
            user_role=Role.CUSTOMER,
        )
        d = result.to_dict()
        assert d["allowed"] is False
        assert d["status"] == "DENIED"
        assert d["reason"] == "TOOL_NOT_IN_ALLOWLIST"
        assert d["tool"] == "approve_refund"
        assert d["role"] == "CUSTOMER"

    def test_result_allowed_factory(self):
        """allowed() factory creates correct result"""
        result = AuthorizationResult.allowed("search_trips", Role.CUSTOMER)
        assert result.is_allowed is True
        assert result.status == AuthorizationStatus.ALLOWED

    def test_result_denied_factory(self):
        """denied() factory creates correct result"""
        result = AuthorizationResult.denied("approve_refund", Role.CUSTOMER, "INTERNAL_ONLY_TOOL")
        assert result.is_allowed is False
        assert result.status == AuthorizationStatus.DENIED
        assert result.reason == "INTERNAL_ONLY_TOOL"


class TestCompletePermissionMatrix:
    """Complete permission matrix tests"""

    # Customer tools that should be ALLOWED
    CUSTOMER_ALLOWED = [
        "search_trips",
        "get_trip",
        "check_available_seats",
        "get_available_trips_summary",
        "create_booking",
        "get_booking",
        "get_user_bookings",
        "cancel_booking",
        "create_payment",
        "get_payment",
        "create_complaint",
        "get_complaint",
        "get_customer_complaints",
        "create_refund_request",
        "get_refund",
        "get_customer_refunds",
        "search_knowledge",
        "format_response",
        "should_use_rag",
    ]

    # Tools that should be DENIED for customer
    CUSTOMER_DENIED = [
        "get_all_bookings",
        "get_all_complaints",
        "get_all_refunds",
        "approve_refund",
        "reject_refund",
        "mark_as_refunded",
        "process_payment",
        "resolve_complaint",
    ]

    @pytest.mark.parametrize("tool", CUSTOMER_ALLOWED)
    def test_customer_allowed_tools(self, tool):
        """All customer allowed tools should pass"""
        guard = ToolGuard()
        result = guard.authorize(tool, Role.CUSTOMER)
        assert result.is_allowed is True, f"Tool {tool} should be allowed for customer"

    @pytest.mark.parametrize("tool", CUSTOMER_DENIED)
    def test_customer_denied_tools(self, tool):
        """All customer denied tools should fail"""
        guard = ToolGuard()
        result = guard.authorize(tool, Role.CUSTOMER)
        assert result.is_allowed is False, f"Tool {tool} should be denied for customer"
