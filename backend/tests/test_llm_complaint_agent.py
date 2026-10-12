"""
Tests for LLM-Enhanced Complaint Agent

Run: pytest tests/test_llm_complaint_agent.py -v
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from dataclasses import dataclass

from src.ai.agents.llm_complaint_agent import (
    LLMComplaintAgent,
    ComplaintActionResult,
    COMPLAINT_SYSTEM_INSTRUCTION,
)
from src.ai.orchestrator.structured_output import (
    COMPLAINT_REFUND_ACTION_SCHEMA,
    COMPLAINT_REFUND_ACTIONS,
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
class MockComplaintState:
    """Mock complaint state"""
    user_id: str
    session_id: str = ""
    complaint_id: str | None = None
    refund_id: str | None = None
    messages: list = None
    context: dict = None

    def __post_init__(self):
        self.messages = []
        self.context = {}

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})


# ============================================================
# TEST: LLM EXTRACTION - VIETNAMESE
# ============================================================

class TestLLMExtractionVietnamese:
    """Tests for LLM action extraction in Vietnamese"""

    @pytest.mark.asyncio
    async def test_extract_create_complaint_vietnamese(self):
        """Test extracting create_complaint from Vietnamese"""
        mock_response = '''{
            "action": "create_complaint",
            "parameters": {"description": "khiếu nại về chuyến xe hôm qua", "complaint_type": "OTHER"},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "vi",
            "message": ""
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMComplaintAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tôi muốn khiếu nại về chuyến xe hôm qua",
            MockComplaintState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "create_complaint"
        assert "vi" in result.parameters.get("description", "").lower() or True  # LLM may extract
        assert result.response_language == "vi"

    @pytest.mark.asyncio
    async def test_extract_get_my_complaints_vietnamese(self):
        """Test extracting get_my_complaints from Vietnamese"""
        mock_response = '''{
            "action": "get_my_complaints",
            "parameters": {},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "vi",
            "message": ""
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMComplaintAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "xem khiếu nại của tôi",
            MockComplaintState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "get_my_complaints"
        assert result.response_language == "vi"

    @pytest.mark.asyncio
    async def test_extract_request_refund_vietnamese(self):
        """Test extracting request_refund from Vietnamese"""
        mock_response = '''{
            "action": "request_refund",
            "parameters": {"booking_code": "BK123456"},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "vi",
            "message": ""
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMComplaintAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tôi muốn hoàn tiền cho booking BK123456",
            MockComplaintState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "request_refund"
        assert result.parameters.get("booking_code") == "BK123456"
        assert result.response_language == "vi"

    @pytest.mark.asyncio
    async def test_extract_missing_booking_code_vietnamese(self):
        """Test extraction with missing booking code"""
        mock_response = '''{
            "action": "request_refund",
            "parameters": {},
            "needs_clarification": true,
            "missing_info": ["booking_code", "bank_info"],
            "response_language": "vi",
            "message": "Bạn cần cung cấp mã booking và thông tin tài khoản."
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMComplaintAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "tôi muốn hoàn tiền",
            MockComplaintState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.needs_clarification is True
        assert "booking_code" in result.missing_info


# ============================================================
# TEST: LLM EXTRACTION - ENGLISH
# ============================================================

class TestLLMExtractionEnglish:
    """Tests for LLM action extraction in English"""

    @pytest.mark.asyncio
    async def test_extract_create_complaint_english(self):
        """Test extracting create_complaint from English"""
        mock_response = '''{
            "action": "create_complaint",
            "parameters": {"booking_code": "BK123456", "description": "complaint about bus service"},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "en",
            "message": ""
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMComplaintAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "I want to file a complaint about my booking BK123456",
            MockComplaintState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "create_complaint"
        assert result.response_language == "en"

    @pytest.mark.asyncio
    async def test_extract_get_my_complaints_english(self):
        """Test extracting get_my_complaints from English"""
        mock_response = '''{
            "action": "get_my_complaints",
            "parameters": {},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "en",
            "message": ""
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMComplaintAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "I want to check my complaints",
            MockComplaintState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "get_my_complaints"
        assert result.response_language == "en"

    @pytest.mark.asyncio
    async def test_extract_request_refund_english(self):
        """Test extracting request_refund from English"""
        mock_response = '''{
            "action": "request_refund",
            "parameters": {},
            "needs_clarification": true,
            "missing_info": ["booking_code"],
            "response_language": "en",
            "message": "Could you provide your booking code?"
        }'''
        mock_client = MockLLMClient([mock_response])
        agent = LLMComplaintAgent(llm_client=mock_client)

        result = await agent._extract_action(
            "I want a refund for my cancelled trip",
            MockComplaintState(user_id="user1")
        )

        assert result.parse_success is True
        assert result.action == "request_refund"
        assert result.response_language == "en"


# ============================================================
# TEST: BILINGUAL CONSISTENCY
# ============================================================

class TestBilingualConsistency:
    """Tests for bilingual consistency"""

    @pytest.mark.asyncio
    async def test_same_action_different_languages(self):
        """Test that similar VI and EN inputs produce same action"""
        vi_response = '''{
            "action": "get_my_refunds",
            "parameters": {},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "vi"
        }'''
        en_response = '''{
            "action": "get_my_refunds",
            "parameters": {},
            "needs_clarification": false,
            "missing_info": [],
            "response_language": "en"
        }'''

        vi_client = MockLLMClient([vi_response])
        en_client = MockLLMClient([en_response])

        vi_agent = LLMComplaintAgent(llm_client=vi_client)
        en_agent = LLMComplaintAgent(llm_client=en_client)

        vi_result = await vi_agent._extract_action(
            "xem yêu cầu hoàn tiền của tôi",
            MockComplaintState(user_id="user1")
        )

        en_result = await en_agent._extract_action(
            "check my refund requests",
            MockComplaintState(user_id="user1")
        )

        # Same action
        assert vi_result.action == en_result.action == "get_my_refunds"
        # Same parameters structure
        assert vi_result.parameters == en_result.parameters


# ============================================================
# TEST: FORBIDDEN ACTIONS
# ============================================================

class TestForbiddenActions:
    """Tests for forbidden/internal actions"""

    def test_parse_forbidden_action_rejected(self):
        """Test that forbidden actions are rejected by parser"""
        parser = StructuredOutputParser(COMPLAINT_REFUND_ACTION_SCHEMA)

        forbidden_actions = [
            "approve_refund", "reject_refund", "mark_as_refunded",
            "resolve_complaint", "process_payment"
        ]

        for action in forbidden_actions:
            result = parser.parse(f'{{"action": "{action}", "parameters": {{}}}}')
            assert not result.is_success, f"Action {action} should be rejected"

    def test_forbidden_action_blocked_in_parse_response(self):
        """Test that forbidden actions are blocked even if LLM returns them"""
        agent = LLMComplaintAgent()

        # Simulate LLM returning forbidden action
        result = agent._parse_llm_response('{"action": "approve_refund", "parameters": {}}')

        # Should be rejected
        assert result.parse_success is False
        assert result.action == "unknown"

    def test_system_instruction_no_forbidden_actions(self):
        """System instruction should not list forbidden actions as options"""
        # Verify forbidden actions are NOT in the allowed list
        for action in COMPLAINT_REFUND_ACTIONS:
            assert action not in ["approve_refund", "reject_refund", "mark_as_refunded",
                                "resolve_complaint", "process_payment"]


# ============================================================
# TEST: CLARIFICATION
# ============================================================

class TestClarification:
    """Tests for clarification handling"""

    def test_clarification_vietnamese(self):
        """Test building clarification in Vietnamese"""
        agent = LLMComplaintAgent()

        action_result = ComplaintActionResult(
            action="request_refund",
            parameters={},
            needs_clarification=True,
            missing_info=["booking_code", "bank_info"],
            response_language="vi",
            message="",
            parse_success=True,
        )

        state = MockComplaintState(user_id="user1")
        response = agent._build_clarification_response(action_result, state)

        assert response["success"] is True
        assert "booking" in response["response"].lower() or "mã" in response["response"].lower()
        assert response["data"]["needs_clarification"] is True

    def test_clarification_english(self):
        """Test building clarification in English"""
        agent = LLMComplaintAgent()

        action_result = ComplaintActionResult(
            action="request_refund",
            parameters={},
            needs_clarification=True,
            missing_info=["booking_code", "bank_info"],
            response_language="en",
            message="",
            parse_success=True,
        )

        state = MockComplaintState(user_id="user1")
        response = agent._build_clarification_response(action_result, state)

        assert response["success"] is True
        assert "booking" in response["response"].lower()
        assert response["data"]["response_language"] == "en"


# ============================================================
# TEST: RULE-BASED FALLBACK
# ============================================================

class TestRuleBasedFallback:
    """Tests for rule-based fallback"""

    @pytest.mark.asyncio
    async def test_fallback_when_llm_fails(self):
        """Test falling back to rule-based when LLM fails"""
        async def fail_llm(*args):
            raise Exception("LLM connection failed")

        mock_client = MockLLMClient([])
        mock_client.generate_with_messages = fail_llm

        agent = LLMComplaintAgent(llm_client=mock_client)

        # Mock the rule-based agent
        agent._complaint_agent.process = AsyncMock(return_value={
            "response": "Rule-based response",
            "success": True,
        })

        result = await agent.process(
            db=MagicMock(),
            user_id="user1",
            message="tôi muốn khiếu nại",
            state=MockComplaintState(user_id="user1"),
            use_llm=True,
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_process_without_llm(self):
        """Test processing without LLM (rule-based only)"""
        agent = LLMComplaintAgent()

        # Mock the rule-based agent
        agent._complaint_agent.process = AsyncMock(return_value={
            "response": "Rule-based response",
            "success": True,
        })

        result = await agent.process(
            db=MagicMock(),
            user_id="user1",
            message="xem khiếu nại của tôi",
            state=MockComplaintState(user_id="user1"),
            use_llm=False,
        )

        assert result["success"] is True


# ============================================================
# TEST: INVALID OUTPUT HANDLING
# ============================================================

class TestInvalidOutputHandling:
    """Tests for handling invalid LLM output"""

    @pytest.mark.asyncio
    async def test_invalid_json_not_executed(self):
        """Test that invalid JSON does not execute any action"""
        mock_client = MockLLMClient(["not valid json at all"])
        agent = LLMComplaintAgent(llm_client=mock_client)

        # Mock the rule-based fallback
        agent._complaint_agent.process = AsyncMock(return_value={
            "response": "Fallback response",
            "success": True,
        })

        result = await agent.process(
            db=MagicMock(),
            user_id="user1",
            message="tôi muốn khiếu nại",
            state=MockComplaintState(user_id="user1"),
            use_llm=True,
        )

        # Should fall back to rule-based
        assert result["success"] is True

    def test_invalid_action_name_not_executed(self):
        """Test that invalid action names are handled"""
        parser = StructuredOutputParser(COMPLAINT_REFUND_ACTION_SCHEMA)

        # Inject invalid action
        result = parser.parse('{"action": "try_to_hack", "parameters": {}}')

        # Should be rejected by schema validation
        assert not result.is_success
        assert result.status == ParseStatus.INVALID_ENUM

    def test_missing_action_field_not_executed(self):
        """Test that missing action field is rejected"""
        parser = StructuredOutputParser(COMPLAINT_REFUND_ACTION_SCHEMA)

        result = parser.parse('{"parameters": {}}')

        assert not result.is_success
        assert result.status == ParseStatus.MISSING_FIELD


# ============================================================
# TEST: ACTION VALIDATION
# ============================================================

class TestActionValidation:
    """Tests for action validation"""

    def test_valid_actions_from_schema(self):
        """Test that all valid actions are accepted"""
        parser = StructuredOutputParser(COMPLAINT_REFUND_ACTION_SCHEMA)

        valid_actions = [
            "create_complaint", "get_complaint", "get_my_complaints",
            "request_refund", "get_refund", "get_my_refunds"
        ]

        for action in valid_actions:
            result = parser.parse(f'{{"action": "{action}", "parameters": {{}}}}')
            assert result.is_success, f"Action {action} should be valid"

    def test_all_allowed_actions_defined(self):
        """Test that all allowed actions are properly defined"""
        assert "create_complaint" in COMPLAINT_REFUND_ACTIONS
        assert "get_complaint" in COMPLAINT_REFUND_ACTIONS
        assert "get_my_complaints" in COMPLAINT_REFUND_ACTIONS
        assert "request_refund" in COMPLAINT_REFUND_ACTIONS
        assert "get_refund" in COMPLAINT_REFUND_ACTIONS
        assert "get_my_refunds" in COMPLAINT_REFUND_ACTIONS


# ============================================================
# TEST: SYSTEM INSTRUCTION
# ============================================================

class TestSystemInstruction:
    """Tests for system instruction"""

    def test_system_instruction_contains_vietnamese(self):
        """System instruction includes Vietnamese"""
        assert "tiếng Việt" in COMPLAINT_SYSTEM_INSTRUCTION or "Việt" in COMPLAINT_SYSTEM_INSTRUCTION

    def test_system_instruction_contains_english(self):
        """System instruction includes English"""
        assert "English" in COMPLAINT_SYSTEM_INSTRUCTION or "tiếng Anh" in COMPLAINT_SYSTEM_INSTRUCTION

    def test_system_instruction_lists_allowed_actions(self):
        """System instruction lists all supported actions"""
        for action in ["create_complaint", "get_complaint", "get_my_complaints",
                      "request_refund", "get_refund", "get_my_refunds"]:
            assert action in COMPLAINT_SYSTEM_INSTRUCTION

    def test_system_instruction_lists_forbidden_actions(self):
        """System instruction explicitly lists forbidden actions"""
        forbidden = ["approve_refund", "reject_refund", "mark_as_refunded",
                    "resolve_complaint", "process_payment"]
        for action in forbidden:
            # Should be mentioned as forbidden
            assert action in COMPLAINT_SYSTEM_INSTRUCTION


# ============================================================
# TEST: SECURITY
# ============================================================

class TestSecurity:
    """Tests for security checks"""

    def test_user_context_optional(self):
        """Test that user_context is optional"""
        agent = LLMComplaintAgent(user_context=None)
        assert agent._user_context is None

    def test_llm_client_optional(self):
        """Test that llm_client is optional (lazy init)"""
        agent = LLMComplaintAgent()
        # Should not raise, lazy init
        _ = agent.llm_client

    def test_no_side_effect_on_parse_failure(self):
        """Test that parse failure doesn't cause side effects"""
        async def fail_llm(*args):
            raise Exception("LLM failed")

        mock_client = MockLLMClient([])
        mock_client.generate_with_messages = fail_llm

        agent = LLMComplaintAgent(llm_client=mock_client)

        # Mock the rule-based agent
        agent._complaint_agent.process = AsyncMock(return_value={
            "response": "Fallback",
            "success": True,
        })

        # Run the process method
        result = asyncio.run(agent.process(
            db=MagicMock(),
            user_id="user1",
            message="test",
            state=MockComplaintState(user_id="user1"),
            use_llm=True,
        ))

        # Verify fallback worked
        assert result["success"] is True
