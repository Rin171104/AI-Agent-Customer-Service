"""
Tests cho Orchestrator

Test cases:
1. Message tìm chuyến → BookingAgent
2. Message hỏi ghế → BookingAgent
3. Message đặt vé → BookingAgent
4. Message xem booking → BookingAgent
5. Message hủy booking → BookingAgent
6. Message thanh toán → BookingAgent
7. Message không rõ intent → NEEDS_CLARIFICATION
8. Kiểm tra state được giữ
9. Kiểm tra user_id được truyền đúng
10. Kiểm tra handoff context có thể lưu
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.ai.orchestrator import Orchestrator, ConversationState
from src.ai.orchestrator.orchestrator import Domain


class TestOrchestratorRouting:
    """Test routing logic của Orchestrator"""

    def setup_method(self):
        """Setup cho mỗi test"""
        self.orchestrator = Orchestrator()

    def test_detect_domain_booking_search(self):
        """Test: Message tìm chuyến → BOOKING"""
        message = "Ngày mai có xe Hà Nội đi Tà Xùa không?"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.BOOKING

    def test_detect_domain_booking_seats(self):
        """Test: Message hỏi ghế → BOOKING"""
        message = "Còn 5 ghế chuyến 8h không?"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.BOOKING

    def test_detect_domain_booking_create(self):
        """Test: Message đặt vé → BOOKING"""
        message = "Tôi muốn đặt 2 vé đi Đà Lạt"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.BOOKING

    def test_detect_domain_booking_get(self):
        """Test: Message xem booking → BOOKING"""
        message = "Tôi muốn xem vé của tôi"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.BOOKING

    def test_detect_domain_booking_cancel(self):
        """Test: Message hủy booking → BOOKING"""
        message = "Tôi muốn hủy vé"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.BOOKING

    def test_detect_domain_booking_payment(self):
        """Test: Message thanh toán → BOOKING"""
        message = "Tôi đã thanh toán chưa?"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.BOOKING

    def test_detect_domain_complaint(self):
        """Test: Message khiếu nại → COMPLAINT"""
        message = "Tôi muốn khiếu nại về chuyến xe"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.COMPLAINT

    def test_detect_domain_unknown(self):
        """Test: Message không rõ → UNKNOWN"""
        message = "Đây là gì vậy?"
        domain = self.orchestrator.detect_domain(message)
        assert domain == Domain.UNKNOWN

    def test_detect_domain_greeting(self):
        """Test: Message chào hỏi → UNKNOWN (sẽ được handle như greeting)"""
        message = "Xin chào"
        domain = self.orchestrator.detect_domain(message)
        # Greeting được detect là UNKNOWN nhưng sẽ được handle đặc biệt


class TestOrchestratorState:
    """Test state management của Orchestrator"""

    def test_conversation_state_init(self):
        """Test: State được khởi tạo đúng"""
        state = ConversationState(user_id="user-123")
        assert state.user_id == "user-123"
        assert state.session_id != ""
        assert state.current_agent is None
        assert state.messages == []

    def test_conversation_state_add_message(self):
        """Test: Thêm message vào state"""
        state = ConversationState(user_id="user-123")
        state.add_message("customer", "Tôi muốn đặt vé")
        state.add_message("agent", "OK, bạn muốn đặt khi nào?")

        assert len(state.messages) == 2
        assert state.messages[0]["role"] == "customer"
        assert state.messages[1]["role"] == "agent"

    def test_conversation_state_entity_ids(self):
        """Test: Set và get entity IDs"""
        state = ConversationState(user_id="user-123")
        state.set_entity_id("trip", "trip-456")
        state.set_entity_id("booking", "booking-789")

        assert state.get_entity_id("trip") == "trip-456"
        assert state.get_entity_id("booking") == "booking-789"
        assert state.get_entity_id("payment") is None

    def test_conversation_state_handoff(self):
        """Test: Handoff được ghi nhận"""
        state = ConversationState(user_id="user-123")
        state.add_handoff(
            from_agent="booking_agent",
            to_agent="complaint_agent",
            reason="refund_request",
            context_keys=["user_id", "booking_id"]
        )

        assert len(state.handoff_history) == 1
        assert state.handoff_history[0]["from_agent"] == "booking_agent"
        assert state.handoff_history[0]["to_agent"] == "complaint_agent"
        assert state.handoff_history[0]["reason"] == "refund_request"

    def test_conversation_state_to_dict(self):
        """Test: Convert state to dict"""
        state = ConversationState(user_id="user-123")
        state.set_entity_id("booking", "booking-789")
        state.add_message("customer", "Hello")

        state_dict = state.to_dict()

        assert state_dict["user_id"] == "user-123"
        assert state_dict["booking_id"] == "booking-789"
        assert len(state_dict["messages"]) == 1

    def test_conversation_state_from_dict(self):
        """Test: Create state from dict"""
        data = {
            "user_id": "user-123",
            "session_id": "session-456",
            "booking_id": "booking-789",
            "messages": [{"role": "customer", "content": "Hello"}],
        }

        state = ConversationState.from_dict(data)

        assert state.user_id == "user-123"
        assert state.session_id == "session-456"
        assert state.booking_id == "booking-789"
        assert len(state.messages) == 1


class TestOrchestratorProcess:
    """Test process() method của Orchestrator"""

    def setup_method(self):
        """Setup cho mỗi test"""
        self.orchestrator = Orchestrator()

    @pytest.mark.asyncio
    async def test_process_booking_message(self):
        """Test: Message đặt vé được route tới BookingAgent"""
        mock_db = AsyncMock()

        # Mock BookingAgent.process để không cần database thật
        with patch("src.ai.agents.booking_agent.BookingAgent") as MockAgent:
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = {
                "success": True,
                "response": "Bạn muốn đặt chuyến nào?",
                "state": MagicMock(
                    intent="create_booking",
                    trip_id=None,
                    booking_id=None,
                    payment_id=None,
                    messages=[],
                    tool_results=[],
                    final_status=None,
                ),
            }
            MockAgent.return_value = mock_agent_instance

            result = await self.orchestrator.process(
                db=mock_db,
                user_id="user-123",
                message="Tôi muốn đặt 2 vé đi Đà Lạt"
            )

            assert result["domain"] == Domain.BOOKING
            assert result["success"] == True

    @pytest.mark.asyncio
    async def test_process_unknown_message(self):
        """Test: Message không rõ → NEEDS_CLARIFICATION"""
        mock_db = AsyncMock()

        result = await self.orchestrator.process(
            db=mock_db,
            user_id="user-123",
            message="Đây là gì vậy?"
        )

        assert result["status"] == "NEEDS_CLARIFICATION"
        assert result["success"] == False

    @pytest.mark.asyncio
    async def test_process_greeting_message(self):
        """Test: Message chào hỏi → greeting response"""
        mock_db = AsyncMock()

        result = await self.orchestrator.process(
            db=mock_db,
            user_id="user-123",
            message="Xin chào"
        )

        assert result["success"] == True
        assert "chào" in result["response"].lower() or "help" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_process_complaint_routed(self):
        """Test: Complaint domain được route tới ComplaintAgent"""
        mock_db = AsyncMock()

        with patch("src.ai.agents.complaint_agent.ComplaintAgent") as MockAgent:
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = {
                "success": True,
                "response": "Tôi đã tiếp nhận khiếu nại của bạn.",
                "state": MagicMock(
                    intent="create_complaint",
                    booking_id=None,
                    complaint_id=None,
                    refund_id=None,
                    messages=[],
                    tool_results=[],
                    final_status=None,
                ),
            }
            MockAgent.return_value = mock_agent_instance

            result = await self.orchestrator.process(
                db=mock_db,
                user_id="user-123",
                message="Tôi muốn khiếu nại"
            )

            assert result["domain"] == Domain.COMPLAINT
            assert result["success"] == True

    @pytest.mark.asyncio
    async def test_process_preserves_user_id(self):
        """Test: user_id được truyền đúng qua state"""
        mock_db = AsyncMock()

        with patch("src.ai.agents.booking_agent.BookingAgent") as MockAgent:
            mock_agent_instance = AsyncMock()
            mock_agent_instance.process.return_value = {
                "success": True,
                "response": "OK",
                "state": MagicMock(
                    intent="search_trip",
                    trip_id=None,
                    booking_id=None,
                    payment_id=None,
                    messages=[],
                    tool_results=[],
                    final_status=None,
                ),
            }
            MockAgent.return_value = mock_agent_instance

            result = await self.orchestrator.process(
                db=mock_db,
                user_id="user-123",
                message="Tìm xe đi Đà Lạt"
            )

            # State phải giữ user_id
            assert result["state"].user_id == "user-123"


class TestOrchestratorHandoff:
    """Test handoff functionality"""

    def setup_method(self):
        """Setup cho mỗi test"""
        self.orchestrator = Orchestrator()

    def test_handoff_creates_context(self):
        """Test: Handoff tạo context đúng"""
        state = ConversationState(user_id="user-123")
        state.set_entity_id("booking", "booking-456")

        handoff = self.orchestrator.handoff(
            from_agent="booking_agent",
            to_agent="complaint_agent",
            reason="refund_request",
            context_keys=["user_id", "booking_id"],
            state=state
        )

        assert handoff is not None
        assert handoff["from_agent"] == "booking_agent"
        assert handoff["to_agent"] == "complaint_agent"
        assert handoff["context"]["user_id"] == "user-123"
        assert handoff["context"]["booking_id"] == "booking-456"

    def test_handoff_records_in_state(self):
        """Test: Handoff được ghi vào state"""
        state = ConversationState(user_id="user-123")
        state.set_entity_id("booking", "booking-456")

        self.orchestrator.handoff(
            from_agent="booking_agent",
            to_agent="complaint_agent",
            reason="refund_request",
            context_keys=["user_id", "booking_id"],
            state=state
        )

        assert len(state.handoff_history) == 1
        assert state.handoff_history[0]["to_agent"] == "complaint_agent"


class TestOrchestratorIntentPatterns:
    """Test các intent patterns cụ thể"""

    def setup_method(self):
        """Setup cho mỗi test"""
        self.orchestrator = Orchestrator()

    def test_intent_search_trip_patterns(self):
        """Test: Các patterns tìm chuyến"""
        patterns = [
            "tìm xe đi đà lạt",
            "có xe nào đi hà nội",
            "xe ngày mai",
            "lịch xe đi tà xùa",
        ]
        for msg in patterns:
            domain = self.orchestrator.detect_domain(msg)
            assert domain == Domain.BOOKING, f"Failed for: {msg}"

    def test_intent_booking_patterns(self):
        """Test: Các patterns đặt vé"""
        patterns = [
            "đặt 2 vé",
            "book ticket",
            "tôi muốn đi đà lạt",
            "cho tôi đặt 1 chỗ",
            "mua vé xe",
        ]
        for msg in patterns:
            domain = self.orchestrator.detect_domain(msg)
            assert domain == Domain.BOOKING, f"Failed for: {msg}"

    def test_intent_payment_patterns(self):
        """Test: Các patterns thanh toán"""
        patterns = [
            "thanh toán",
            "payment",
            "chuyển khoản",
            "trạng thái thanh toán",
            "đã thanh toán chưa",
        ]
        for msg in patterns:
            domain = self.orchestrator.detect_domain(msg)
            assert domain == Domain.BOOKING, f"Failed for: {msg}"

    def test_intent_cancel_patterns(self):
        """Test: Các patterns hủy vé"""
        patterns = [
            "hủy vé",
            "hủy booking",
            "không đi nữa",
            "xóa đặt",
        ]
        for msg in patterns:
            domain = self.orchestrator.detect_domain(msg)
            assert domain == Domain.BOOKING, f"Failed for: {msg}"


# Chạy test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
