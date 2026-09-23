"""
Orchestrator - Route messages tới appropriate Agent

Nhiệm vụ:
    - Nhận message từ Customer
    - Xác định domain/intent
    - Route tới Agent phù hợp
    - Duy trì conversation state
    - Hỗ trợ handoff giữa các Agents

Không phải Agent - chỉ là routing layer.
"""
import re
from typing import Dict, Any, Optional
from enum import Enum

from src.ai.orchestrator.state import ConversationState
from src.utils.logger import logger


class Domain(str, Enum):
    """Các domain được hỗ trợ"""
    BOOKING = "BOOKING"
    COMPLAINT = "COMPLAINT"
    UNKNOWN = "UNKNOWN"


class Orchestrator:
    """
    Orchestrator - Workflow/Routing Layer

    Nhận message và route tới Agent phù hợp.

    Sử dụng rule-based intent detection cho MVP.
    Không cần LLM cho việc routing đơn giản.
    """

    # Booking domain patterns
    BOOKING_PATTERNS = [
        # Tìm chuyến
        r"tìm.*chuyến",
        r"tìm.*xe",
        r"xe.*đi",
        r"có.*xe.*nào",
        r"lịch.*xe",
        r"chuyến.*nào",
        r"đi.*từ.*đến",
        r"(hà nội|hcm|sài gòn|đà lạt|tà xùa|nha trang)",
        r"ngày.*mai.*xe",
        r"xe.*ngày",

        # Thông tin chuyến
        r"thông tin.*chuyến",
        r"chi tiết.*chuyến",
        r"xem.*chuyến",

        # Ghế
        r"còn.*ghế",
        r"ghế.*trống",
        r"có.*ghế.*không",
        r"check.*seat",
        r"seat.*available",

        # Đặt vé
        r"đặt.*vé",
        r"đặt.*chỗ",
        r"book.*ticket",
        r"mua.*vé",
        r"giữ.*vé",
        r"tôi.*muốn.*đi",
        r"cho.*tôi.*đặt",
        r"đặt\s+\d+\s*vé",
        r"đặt\s+\d+\s*ghế",

        # Xem vé/booking
        r"xem.*booking",
        r"xem.*vé",
        r"vé.*của.*tôi",
        r"booking.*của.*tôi",
        r"mã.*booking",
        r"tra.*cứu.*vé",
        r"danh.*sách.*vé",
        r"lịch.*sử.*đặt",
        r"vé.*đã.*đặt",
        r"các.*vé",

        # Hủy vé
        r"hủy.*vé",
        r"hủy.*booking",
        r"xóa.*đặt",
        r"không.*đi.*nữa",
        r"hủy.*chuyến",

        # Thanh toán
        r"thanh.*toán",
        r"payment",
        r"pay",
        r"chuyển.*khoản",
        r"nạp.*tiền",
        r"trạng thái.*thanh.*toán",
        r"thanh.*toán.*chưa",
        r"đã.*thanh.*toán.*chưa",
        r"payment.*status",
    ]

    # Complaint domain patterns (placeholder - chưa implement)
    COMPLAINT_PATTERNS = [
        r"khiếu.*nại",
        r"complaint",
        r"phàn.*nàn",
        r"báo.*cáo",
        r"phản.*hồi",
        r"không.*hài.*lòng",
    ]

    def __init__(self):
        self.logger = logger
        self._agents = {}

    def register_agent(self, name: str, agent):
        """Register an agent"""
        self._agents[name] = agent
        self.logger.info(f"Registered agent: {name}")

    def detect_domain(self, message: str) -> Domain:
        """
        Detect domain từ message.

        Args:
            message: Tin nhắn từ customer

        Returns:
            Domain enum
        """
        message_lower = message.lower()

        # Check booking patterns
        for pattern in self.BOOKING_PATTERNS:
            if re.search(pattern, message_lower):
                return Domain.BOOKING

        # Check complaint patterns
        for pattern in self.COMPLAINT_PATTERNS:
            if re.search(pattern, message_lower):
                return Domain.COMPLAINT

        return Domain.UNKNOWN

    async def process(
        self,
        db: Any,
        user_id: str,
        message: str,
        state: Optional[ConversationState] = None
    ) -> Dict[str, Any]:
        """
        Process message và route tới appropriate agent.

        Args:
            db: Database session
            user_id: ID của user
            message: Tin nhắn từ customer
            state: Conversation state hiện tại (optional)

        Returns:
            Dict với response và updated state
        """
        # Initialize state nếu chưa có
        if state is None:
            state = ConversationState(user_id=user_id)

        # Add customer message
        state.add_message("customer", message)

        # Detect domain
        domain = self.detect_domain(message)

        self.logger.info(f"Detected domain: {domain} for message: {message[:50]}...")

        # Route based on domain
        if domain == Domain.BOOKING:
            return await self._handle_booking(db, message, state)
        elif domain == Domain.COMPLAINT:
            return await self._handle_complaint(db, message, state)
        else:
            return await self._handle_unknown(message, state)

    async def _handle_booking(
        self,
        db: Any,
        message: str,
        state: ConversationState
    ) -> Dict[str, Any]:
        """Handle booking domain - route to BookingAgent"""
        # Import here để tránh circular import
        from src.ai.agents.booking_agent import BookingAgent

        # Create or get booking agent
        if "booking" not in self._agents:
            self.register_agent("booking", BookingAgent())

        agent = self._agents["booking"]
        state.current_agent = "booking_agent"

        try:
            # Convert state to BookingState format
            from src.ai.agents.booking_agent import BookingState as BookingAgentState

            # Create booking state from conversation state
            booking_state = BookingAgentState(
                user_id=state.user_id,
                session_id=state.session_id,
                intent=state.intent,
                trip_id=state.trip_id,
                booking_id=state.booking_id,
                payment_id=state.payment_id,
                messages=[m for m in state.messages if m.get("role") in ["customer", "agent"]],
                context={
                    "complaint_id": state.complaint_id,
                    "refund_id": state.refund_id,
                }
            )

            # Process với booking agent
            result = await agent.process(
                db=db,
                user_id=state.user_id,
                message=message,
                state=booking_state
            )

            # Update conversation state from result
            if result.get("state"):
                result_state = result["state"]
                state.intent = result_state.intent
                state.trip_id = result_state.trip_id
                state.booking_id = result_state.booking_id
                state.payment_id = result_state.payment_id
                state.final_status = result_state.final_status

                # Copy messages back
                state.messages = result_state.messages

                # Copy tool results
                for tr in result_state.tool_results:
                    state.add_tool_result("booking_agent", tr.get("tool", "unknown"), tr.get("result", {}))

            # Add agent response
            state.add_message("agent", result.get("response", ""))

            return {
                "success": result.get("success", False),
                "response": result.get("response", ""),
                "state": state,
                "domain": Domain.BOOKING,
                "data": result.get("data"),
                "next_action": result.get("next_action"),
            }

        except Exception as e:
            self.logger.error(f"Error in booking agent: {e}")
            return {
                "success": False,
                "response": "Đã có lỗi xảy ra. Vui lòng thử lại.",
                "state": state,
                "domain": Domain.BOOKING,
                "error": str(e),
            }

    async def _handle_complaint(
        self,
        db: Any,
        message: str,
        state: ConversationState
    ) -> Dict[str, Any]:
        """Handle complaint domain - route to ComplaintAgent"""
        from src.ai.agents.complaint_agent import ComplaintAgent

        # Create or get complaint agent
        if "complaint" not in self._agents:
            self.register_agent("complaint", ComplaintAgent())

        agent = self._agents["complaint"]
        state.current_agent = "complaint_agent"

        try:
            # Convert state to ComplaintState format
            from src.ai.agents.complaint_agent import ComplaintState as ComplaintAgentState

            complaint_state = ComplaintAgentState(
                user_id=state.user_id,
                session_id=state.session_id,
                intent=state.intent,
                booking_id=state.booking_id,
                complaint_id=state.complaint_id,
                refund_id=state.refund_id,
                messages=[m for m in state.messages if m.get("role") in ["customer", "agent"]],
                context={
                    "trip_id": state.trip_id,
                    "payment_id": state.payment_id,
                }
            )

            # Process với complaint agent
            result = await agent.process(
                db=db,
                user_id=state.user_id,
                message=message,
                state=complaint_state
            )

            # Update conversation state from result
            if result.get("state"):
                result_state = result["state"]
                state.intent = result_state.intent
                state.booking_id = result_state.booking_id
                state.complaint_id = result_state.complaint_id
                state.refund_id = result_state.refund_id
                state.final_status = result_state.final_status

                # Copy messages back
                state.messages = result_state.messages

                # Copy tool results
                for tr in result_state.tool_results:
                    state.add_tool_result("complaint_agent", tr.get("tool", "unknown"), tr.get("result", {}))

            # Record handoff if this is the first complaint handling
            if not any(h.get("to_agent") == "complaint_agent" for h in state.handoff_history):
                state.add_handoff(
                    from_agent="orchestrator",
                    to_agent="complaint_agent",
                    reason="complaint_request",
                    context_keys=["user_id", "booking_id", "complaint_id"]
                )

            # Add agent response
            state.add_message("agent", result.get("response", ""))

            return {
                "success": result.get("success", False),
                "response": result.get("response", ""),
                "state": state,
                "domain": Domain.COMPLAINT,
                "data": result.get("data"),
                "next_action": result.get("next_action"),
                "requires_human": result.get("requires_human", False),
                "human_action": result.get("human_action"),
            }

        except Exception as e:
            self.logger.error(f"Error in complaint agent: {e}")
            return {
                "success": False,
                "response": "Đã có lỗi xảy ra. Vui lòng thử lại.",
                "state": state,
                "domain": Domain.COMPLAINT,
                "error": str(e),
            }

    async def _handle_unknown(
        self,
        message: str,
        state: ConversationState
    ) -> Dict[str, Any]:
        """Handle unknown intent"""
        state.current_agent = None

        # Check if it's a greeting or casual message
        greeting_patterns = [
            r"^(xin\s+)?chào",
            r"^(hi|hello|hey)",
            r"cảm\s*ơn",
            r"thanks",
            r"bye",
            r"tạm\s*biệt",
            r"help",
            r"trợ\s*giúp",
        ]

        for pattern in greeting_patterns:
            if re.search(pattern, message.lower()):
                return {
                    "success": True,
                    "response": "Xin chào! Tôi có thể giúp bạn:\n"
                               "- Tìm chuyến xe: 'tìm xe đi Đà Lạt'\n"
                               "- Đặt vé: 'đặt 2 vé đi Tà Xùa'\n"
                               "- Xem booking: 'xem vé của tôi'\n"
                               "- Thanh toán: 'thanh toán'\n"
                               "- Hủy vé: 'hủy vé'\n\n"
                               "Bạn cần hỗ trợ gì?",
                    "state": state,
                    "domain": Domain.UNKNOWN,
                }

        # Unknown intent - need clarification
        return {
            "success": False,
            "status": "NEEDS_CLARIFICATION",
            "response": "Tôi chưa xác định được yêu cầu của bạn. "
                       "Bạn có thể:\n"
                       "- Tìm chuyến xe: 'tìm xe đi Đà Lạt'\n"
                       "- Đặt vé: 'đặt 2 vé đi Tà Xùa'\n"
                       "- Xem vé: 'xem vé của tôi'\n"
                       "- Thanh toán: 'thanh toán'\n"
                       "- Hủy vé: 'hủy vé'\n\n"
                       "Bạn cần hỗ trợ gì?",
            "state": state,
            "domain": Domain.UNKNOWN,
        }

    def handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context_keys: Optional[list] = None,
        state: Optional[ConversationState] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Chuyển context giữa các agents.

        Args:
            from_agent: Agent đang xử lý
            to_agent: Agent cần chuyển tới
            reason: Lý do handoff
            context_keys: Keys cần truyền trong context
            state: Conversation state hiện tại

        Returns:
            Handoff context dict hoặc None
        """
        if state is None:
            return None

        state.add_handoff(from_agent, to_agent, reason, context_keys)

        return {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "context": {
                key: getattr(state, key, None)
                for key in (context_keys or [])
                if hasattr(state, key)
            }
        }
