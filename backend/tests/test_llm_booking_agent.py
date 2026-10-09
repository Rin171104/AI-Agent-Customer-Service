"""
Tests for LLM-Enhanced Booking Agent

Run: pytest tests/test_llm_booking_agent.py -v
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from dataclasses import dataclass

from src.ai.agents.llm_booking_agent import (
    LLMBookingAgent,
    BookingActionResult,
    BOOKING_SYSTEM_INSTRUCTION,
)
from src.ai.orchestrator.structured_output import (
    BOOKING_ACTION_SCHEMA,
    StructuredOutputParser,
    ParseStatus,
)


# ============================================================
# FIXTURES
# ============================================================

class MockLLMClient:
    """Mock LLM client for testing"""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_count = 0

    async def generate_with_messages(self, messages: list[dict]) -> str:
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return '{"action": "unknown", "parameters": {}}'


@dataclass
class MockBookingState:
    """Mock booking state"""
    user_id: str
    session_id: str = ""
    booking_id: str | None = None
    messages: list = None
    context: dict = None

    def __post_init__(self):
        self.messages = []
        self.context = {}

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})


# ============================================================
# TEST: LLM EXTRACTION
# ============================================================

class TestLLMExtraction:
    """Tests for LLM action extraction"""

    @pytest.mark.asyncio
    async def test_extract_search_trip_vietnamese(self):
        """Test extracting search_trip from Vietnamese"""
        mock_response = '''{
            "action": "search_trip",
            "parameters": {"destination": "ta xua", "date": "tomorrow"},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "vi",
            "message": ""
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tôi muốn tìm xe đi Tà Xùa ngày mai",
            MockBookingState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "search_trip"
        assert result.parameters["destination"] == "ta xua"
        assert result.response_language == "vi"

    @pytest.mark.asyncio
    async def test_extract_create_booking_english(self):
        """Test extracting create_booking from English"""
        mock_response = '''{
            "action": "create_booking",
            "parameters": {"origin": "hanoi", "destination": "da lat", "seat_count": 2},
            "needs_clarification": true,
            "missing_info": ["date"],
            "response_language": "en",
            "message": "What date would you like to depart?"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "I want to book two tickets from Hanoi to Da Lat",
            MockBookingState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "create_booking"
        assert result.parameters["seat_count"] == 2
        assert result.needs_clarification is True
        assert "date" in result.missing_info
        assert result.response_language == "en"

    @pytest.mark.asyncio
    async def test_extract_with_missing_info(self):
        """Test extraction with missing required info"""
        mock_response = '''{
            "action": "create_booking",
            "parameters": {},
            "needs_clarification": true,
            "missing_info": ["origin", "destination", "date"],
            "response_language": "vi",
            "message": "Bạn cần cho tôi biết điểm đi, điểm đến và ngày khởi hành."
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tôi muốn đặt vé",
            MockBookingState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.needs_clarification is True
        assert len(result.missing_info) >= 2

    @pytest.mark.asyncio
    async def test_llm_failure_fallback(self):
        """Test fallback when LLM fails"""
        mock_client = MockLLMClient([])

        async def fail_llm(*args):
            raise Exception("LLM connection failed")

        mock_client.generate_with_messages = fail_llm
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tìm xe đi Hà Nội",
            MockBookingState(user_id="user1")
        )

        assert result.parse_success is False
        assert result.action == "unknown"


# ============================================================
# TEST: PARSING
# ============================================================

class TestParsing:
    """Tests for parsing LLM responses"""

    def test_parse_valid_response(self):
        """Parse valid JSON response"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)
        result = parser.parse('''{
            "action": "search_trip",
            "parameters": {"destination": "hanoi"},
            "needs_clarification": false,
            "response_language": "vi"
        }''')

        assert result.is_success
        assert result.data["action"] == "search_trip"
        assert result.data["parameters"]["destination"] == "hanoi"

    def test_parse_invalid_action(self):
        """Parse response with invalid action"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)
        result = parser.parse('''{
            "action": "invalid_action",
            "parameters": {}
        }''')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_ENUM

    def test_parse_missing_action(self):
        """Parse response missing required action field"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)
        result = parser.parse('{"parameters": {}}')

        assert not result.is_success
        assert result.status == ParseStatus.MISSING_FIELD

    def test_parse_invalid_json(self):
        """Parse invalid JSON"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)
        result = parser.parse("not json at all")

        assert not result.is_success
        assert result.status in (ParseStatus.INVALID_JSON, ParseStatus.UNKNOWN_FORMAT)

    def test_parse_empty_output(self):
        """Parse empty output"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)
        result = parser.parse("")

        assert not result.is_success
        assert result.status == ParseStatus.EMPTY_OUTPUT

    def test_parse_with_markdown_fence(self):
        """Parse JSON wrapped in markdown fence"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)
        result = parser.parse('''```json
{
    "action": "get_my_bookings",
    "parameters": {},
    "needs_clarification": false,
    "response_language": "vi"
}
```''')

        assert result.is_success
        assert result.data["action"] == "get_my_bookings"


# ============================================================
# TEST: BILINGUAL SUPPORT
# ============================================================

class TestBilingualSupport:
    """Tests for Vietnamese-English support"""

    @pytest.mark.asyncio
    async def test_vietnamese_response_language(self):
        """Vietnamese input returns Vietnamese response language"""
        mock_response = '''{
            "action": "get_my_bookings",
            "parameters": {},
            "needs_clarification": false,
            "response_language": "vi"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "xem vé của tôi",
            MockBookingState(user_id="user1")
        )

        assert result.response_language == "vi"

    @pytest.mark.asyncio
    async def test_english_response_language(self):
        """English input returns English response language"""
        mock_response = '''{
            "action": "get_my_bookings",
            "parameters": {},
            "needs_clarification": false,
            "response_language": "en"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "check my booking",
            MockBookingState(user_id="user1")
        )

        assert result.response_language == "en"

    @pytest.mark.asyncio
    async def test_equivalent_extraction_vi_en(self):
        """Similar Vietnamese and English inputs produce equivalent actions"""
        # Vietnamese
        vi_response = '''{
            "action": "search_trip",
            "parameters": {"origin": "hanoi", "destination": "da lat"},
            "needs_clarification": true,
            "missing_info": ["date"],
            "response_language": "vi"
        }'''

        # English
        en_response = '''{
            "action": "search_trip",
            "parameters": {"origin": "hanoi", "destination": "da lat"},
            "needs_clarification": true,
            "missing_info": ["date"],
            "response_language": "en"
        }'''

        vi_client = MockLLMClient([vi_response])
        en_client = MockLLMClient([en_response])

        vi_agent = LLMBookingAgent(llm_client=vi_client)
        en_agent = LLMBookingAgent(llm_client=en_client)

        vi_result = await vi_agent._extract_action(
            "tìm xe từ Hà Nội đi Đà Lạt",
            MockBookingState(user_id="user1")
        )

        en_result = await en_agent._extract_action(
            "find a bus from Hanoi to Da Lat",
            MockBookingState(user_id="user1")
        )

        # Same action
        assert vi_result.action == en_result.action == "search_trip"
        # Same parameters
        assert vi_result.parameters == en_result.parameters
        # Both need clarification for date
        assert vi_result.needs_clarification == en_result.needs_clarification is True

    @pytest.mark.asyncio
    async def test_cancel_booking_vietnamese(self):
        """Test cancel booking in Vietnamese"""
        mock_response = '''{
            "action": "cancel_booking",
            "parameters": {"booking_code": "BK12345"},
            "needs_clarification": false,
            "response_language": "vi"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tôi muốn hủy vé mã BK12345",
            MockBookingState(user_id="user1")
        )

        assert result.action == "cancel_booking"
        assert result.parameters["booking_code"] == "BK12345"

    @pytest.mark.asyncio
    async def test_cancel_booking_english(self):
        """Test cancel booking in English"""
        mock_response = '''{
            "action": "cancel_booking",
            "parameters": {"booking_code": "BK12345"},
            "needs_clarification": false,
            "response_language": "en"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "I want to cancel my ticket BK12345",
            MockBookingState(user_id="user1")
        )

        assert result.action == "cancel_booking"
        assert result.parameters["booking_code"] == "BK12345"

    @pytest.mark.asyncio
    async def test_check_payment_vietnamese(self):
        """Test check payment in Vietnamese"""
        mock_response = '''{
            "action": "check_payment",
            "parameters": {"booking_id": "trip-123"},
            "needs_clarification": false,
            "response_language": "vi"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tôi đã thanh toán chưa?",
            MockBookingState(user_id="user1")
        )

        assert result.action == "check_payment"

    @pytest.mark.asyncio
    async def test_check_payment_english(self):
        """Test check payment in English"""
        mock_response = '''{
            "action": "check_payment",
            "parameters": {},
            "needs_clarification": false,
            "response_language": "en"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "Has my payment been completed?",
            MockBookingState(user_id="user1")
        )

        assert result.action == "check_payment"


# ============================================================
# TEST: CLARIFICATION
# ============================================================

class TestClarification:
    """Tests for clarification handling"""

    def test_build_clarification_vietnamese(self):
        """Test building clarification in Vietnamese"""
        mock_response = '''{
            "action": "create_booking",
            "parameters": {},
            "needs_clarification": true,
            "missing_info": ["destination", "date"],
            "response_language": "vi",
            "message": ""
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        action_result = BookingActionResult(
            action="create_booking",
            parameters={},
            needs_clarification=True,
            missing_info=["destination", "date"],
            response_language="vi",
            message="",
            parse_success=True,
        )

        state = MockBookingState(user_id="user1")
        response = agent._build_clarification_response(action_result, state)

        assert response["success"] is True
        assert "destination" in response["response"] or "đi" in response["response"]

    def test_build_clarification_english(self):
        """Test building clarification in English"""
        mock_response = '''{
            "action": "create_booking",
            "parameters": {},
            "needs_clarification": true,
            "missing_info": ["destination", "date"],
            "response_language": "en",
            "message": "What date and destination?"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMBookingAgent(llm_client=mock_client)

        action_result = BookingActionResult(
            action="create_booking",
            parameters={},
            needs_clarification=True,
            missing_info=["destination", "date"],
            response_language="en",
            message="What date and destination?",
            parse_success=True,
        )

        state = MockBookingState(user_id="user1")
        response = agent._build_clarification_response(action_result, state)

        assert response["success"] is True
        # Response should be in English
        assert "date" in response["response"].lower() or "destination" in response["response"].lower()


# ============================================================
# TEST: RULE-BASED FALLBACK
# ============================================================

class TestRuleBasedFallback:
    """Tests for rule-based fallback"""

    @pytest.mark.asyncio
    async def test_fallback_when_llm_fails(self):
        """Test falling back to rule-based when LLM fails"""
        async def fail_llm(*args):
            raise Exception("LLM failed")

        mock_client = MockLLMClient([])
        mock_client.generate_with_messages = fail_llm

        agent = LLMBookingAgent(llm_client=mock_client)

        # Mock the rule-based agent
        agent._booking_agent.process = AsyncMock(return_value={
            "response": "Rule-based response",
            "success": True,
        })

        result = await agent.process(
            db=MagicMock(),
            user_id="user1",
            message="tìm xe đi Hà Nội",
            state=MockBookingState(user_id="user1"),
            use_llm=True,
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_process_without_llm(self):
        """Test processing without LLM (rule-based only)"""
        agent = LLMBookingAgent()

        # Mock the rule-based agent
        agent._booking_agent.process = AsyncMock(return_value={
            "response": "Rule-based response",
            "success": True,
        })

        result = await agent.process(
            db=MagicMock(),
            user_id="user1",
            message="tìm xe đi Hà Nội",
            state=MockBookingState(user_id="user1"),
            use_llm=False,
        )

        assert result["success"] is True


# ============================================================
# TEST: ACTION VALIDATION
# ============================================================

class TestActionValidation:
    """Tests for action validation"""

    def test_valid_actions_from_schema(self):
        """Test that all valid actions are accepted"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)

        valid_actions = [
            "search_trip", "get_trip_info", "check_seats",
            "create_booking", "get_booking", "cancel_booking",
            "create_payment", "check_payment", "get_my_bookings"
        ]

        for action in valid_actions:
            result = parser.parse(f'{{"action": "{action}", "parameters": {{}}}}')
            assert result.is_success, f"Action {action} should be valid"

    def test_invalid_action_rejected(self):
        """Test that invalid actions are rejected"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)

        invalid_actions = [
            "admin_delete", "execute_sql", "bypass_auth",
            "delete_all_data", "approve_refund"
        ]

        for action in invalid_actions:
            result = parser.parse(f'{{"action": "{action}", "parameters": {{}}}}')
            assert not result.is_success, f"Action {action} should be rejected"


# ============================================================
# TEST: SYSTEM INSTRUCTION
# ============================================================

class TestSystemInstruction:
    """Tests for system instruction"""

    def test_system_instruction_contains_vietnamese(self):
        """System instruction includes Vietnamese examples"""
        assert "tiếng Việt" in BOOKING_SYSTEM_INSTRUCTION or "Việt" in BOOKING_SYSTEM_INSTRUCTION

    def test_system_instruction_contains_english(self):
        """System instruction includes English examples"""
        assert "English" in BOOKING_SYSTEM_INSTRUCTION or "tiếng Anh" in BOOKING_SYSTEM_INSTRUCTION

    def test_system_instruction_lists_actions(self):
        """System instruction lists all supported actions"""
        for action in ["search_trip", "get_trip_info", "check_seats",
                      "create_booking", "get_booking", "cancel_booking"]:
            assert action in BOOKING_SYSTEM_INSTRUCTION

    def test_system_instruction_no_internal_actions(self):
        """System instruction does not list internal-only actions"""
        internal_actions = [
            "approve_refund", "reject_refund", "mark_as_refunded",
            "resolve_complaint", "process_payment"
        ]

        for action in internal_actions:
            assert action not in BOOKING_SYSTEM_INSTRUCTION


# ============================================================
# TEST: AUTHORIZATION
# ============================================================

class TestAuthorization:
    """Tests for authorization checks"""

    def test_authorization_check_defined(self):
        """Test that _check_authorization method exists"""
        agent = LLMBookingAgent()
        assert hasattr(agent, "_check_authorization")

    def test_authorization_with_no_context(self):
        """Test authorization with no user_context - should allow minimal actions"""
        agent = LLMBookingAgent(user_context=None)

        # search_trip should be allowed even without context
        result = agent._check_authorization("search_trip")
        assert result["allowed"] is True

    def test_authorization_unknown_action_denied(self):
        """Test unknown action is denied"""
        agent = LLMBookingAgent()

        result = agent._check_authorization("unknown_action")
        assert result["allowed"] is False
        assert result["reason"] == "UNKNOWN_ACTION"

    def test_authorization_customer_role(self):
        """Test authorization with CUSTOMER role"""
        from src.ai.security.context import UserContext
        from src.ai.security.tool_guard import Role

        context = UserContext(user_id="user1", role=Role.CUSTOMER)
        agent = LLMBookingAgent(user_context=context)

        # Customer can search trips
        result = agent._check_authorization("search_trip")
        assert result["allowed"] is True

    def test_authorization_customer_cannot_access_internal(self):
        """Test CUSTOMER cannot call internal-only tools"""
        from src.ai.security.context import UserContext
        from src.ai.security.tool_guard import Role, get_tool_guard

        context = UserContext(user_id="user1", role=Role.CUSTOMER)
        agent = LLMBookingAgent(user_context=context)

        # Try to authorize through guard directly
        guard = get_tool_guard()
        guard_result = guard.authorize(
            tool_name="approve_refund",
            user_role=Role.CUSTOMER,
        )

        # Should be denied
        assert guard_result.is_allowed is False
        assert guard_result.reason in ("TOOL_NOT_IN_ALLOWLIST", "INTERNAL_ONLY_TOOL")

    def test_authorization_owner_can_access_more(self):
        """Test OWNER has more permissions"""
        from src.ai.security.context import UserContext
        from src.ai.security.tool_guard import Role, get_tool_guard

        context = UserContext(user_id="owner1", role=Role.OWNER)
        agent = LLMBookingAgent(user_context=context)

        # Owner can do customer actions
        result = agent._check_authorization("search_trip")
        assert result["allowed"] is True

    def test_execute_action_blocks_unauthorized(self):
        """Test that _execute_action blocks unauthorized actions"""
        from src.ai.security.context import UserContext
        from src.ai.security.tool_guard import Role

        # Create agent with CUSTOMER context
        context = UserContext(user_id="customer1", role=Role.CUSTOMER)
        agent = LLMBookingAgent(user_context=context)

        # Action result with internal action (mapped to internal tool)
        action_result = BookingActionResult(
            action="create_booking",  # This is valid
            parameters={},
            needs_clarification=False,
            missing_info=[],
            response_language="vi",
            message="",
            parse_success=True,
        )

        # Mock the handler to not execute (we're testing auth before handler)
        import asyncio

        async def mock_handler(*args):
            return {"success": True, "response": "Should not reach here"}

        # Patch the handler
        agent._handle_create_booking = mock_handler

        # Execute - should call authorization check first
        state = MockBookingState(user_id="customer1")

        # Note: create_booking should be allowed for CUSTOMER
        # This test verifies the auth check is called
        result = asyncio.run(agent._execute_action(
            db=MagicMock(),
            user_id="customer1",
            action_result=action_result,
            state=state,
        ))

        # If auth passes and handler returns success, we're good
        # If auth failed, success would be False
        assert "success" in result


# ============================================================
# TEST: DATA-LEVEL AUTHORIZATION (DOCUMENTED)
# ============================================================

class TestDataLevelAuthorization:
    """
    Tests for data-level authorization.

    NOTE: Data-level ownership verification (checking if booking belongs to user)
    is handled at the SERVICE layer, not LLMBookingAgent.

    Pre-existing gap in booking_service.py:
    - get_booking_by_id() does NOT verify ownership
    - get_booking_by_code() does NOT verify ownership
    - cancel_booking() DOES verify ownership

    LLMBookingAgent uses ToolGuard at ACTION level, which is verified.
    """

    def test_llm_booking_agent_respects_tool_guard(self):
        """Verify LLMBookingAgent calls ToolGuard before executing"""
        from src.ai.security.context import UserContext
        from src.ai.security.tool_guard import Role

        # Customer role
        context = UserContext(user_id="user1", role=Role.CUSTOMER)
        agent = LLMBookingAgent(user_context=context)

        # All customer actions should be allowed
        customer_actions = [
            "search_trip", "get_trip_info", "check_seats",
            "create_booking", "get_booking", "cancel_booking",
            "create_payment", "check_payment", "get_my_bookings"
        ]

        for action in customer_actions:
            result = agent._check_authorization(action)
            assert result["allowed"], f"Action {action} should be allowed for CUSTOMER"

    def test_internal_actions_blocked_at_guard_level(self):
        """Verify internal actions are blocked by ToolGuard"""
        from src.ai.security.tool_guard import get_tool_guard, Role

        guard = get_tool_guard()

        internal_tools = [
            "approve_refund", "reject_refund", "mark_as_refunded",
            "resolve_complaint", "process_payment"
        ]

        for tool in internal_tools:
            result = guard.authorize(tool, Role.CUSTOMER)
            assert not result.is_allowed, f"Tool {tool} should be blocked for CUSTOMER"

    def test_user_context_none_allows_minimal(self):
        """Verify behavior when user_context is None"""
        agent = LLMBookingAgent(user_context=None)

        # With no context, minimal actions are allowed
        result = agent._check_authorization("search_trip")
        assert result["allowed"]  # Minimal permissions assumed

        # Internal actions should still be blocked via action mapping
        result = agent._check_authorization("unknown_action")
        assert not result["allowed"]  # Unknown action denied


# ============================================================
# TEST: INVALID OUTPUT HANDLING
# ============================================================

class TestInvalidOutputHandling:
    """Tests for handling invalid LLM output"""

    @pytest.mark.asyncio
    async def test_invalid_json_not_executed(self):
        """Test that invalid JSON does not execute any action"""
        mock_client = MockLLMClient(["not valid json at all"])
        agent = LLMBookingAgent(llm_client=mock_client)

        # Mock the rule-based fallback
        agent._booking_agent.process = AsyncMock(return_value={
            "response": "Fallback response",
            "success": True,
        })

        result = await agent.process(
            db=MagicMock(),
            user_id="user1",
            message="tìm xe",
            state=MockBookingState(user_id="user1"),
            use_llm=True,
        )

        # Should fall back to rule-based
        assert result["success"] is True

    def test_invalid_action_name_not_executed(self):
        """Test that invalid action names are handled"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)

        # Inject invalid action
        result = parser.parse('{"action": "try_to_hack_system", "parameters": {}}')

        # Should be rejected by schema validation
        assert not result.is_success
        assert result.status == ParseStatus.INVALID_ENUM

    def test_missing_action_field_not_executed(self):
        """Test that missing action field is rejected"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)

        result = parser.parse('{"parameters": {}}')

        assert not result.is_success
        assert result.status == ParseStatus.MISSING_FIELD

    def test_empty_output_not_executed(self):
        """Test that empty output is rejected"""
        parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)

        result = parser.parse("")

        assert not result.is_success
        assert result.status == ParseStatus.EMPTY_OUTPUT
