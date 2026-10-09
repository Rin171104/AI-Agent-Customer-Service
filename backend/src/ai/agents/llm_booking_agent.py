"""
LLM-Enhanced Booking Agent

Integrates LLM with BookingAgent for natural language understanding.
Supports both Vietnamese and English inputs.

Architecture:
    Customer message
           |
           v
    LLMBookingAgent.process()
           |
           v
    LLM Provider (Task 7.1)
           |
           v
    StructuredOutputParser (Task 7.3)
           |
           v
    Action Validation
           |
           v
    BookingAgent handlers (existing)
           |
           v
    Customer response
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from src.models.llm_client import (
    LLMClient,
    MockProvider,
    LLMConfigurationError,
    LLMProviderError,
    LLMTimeoutError,
)
from src.ai.orchestrator.structured_output import (
    StructuredOutputParser,
    BOOKING_ACTION_SCHEMA,
    BOOKING_ACTIONS,
    ParseStatus,
)
from src.ai.agents.booking_agent import BookingAgent, BookingState
from src.ai.security.context import UserContext
from src.ai.security.authorized_tools import (
    AuthorizedTripTools,
    AuthorizedBookingTools,
    AuthorizedPaymentTools,
)
from src.utils.logger import logger


# System instruction for booking action extraction
BOOKING_SYSTEM_INSTRUCTION = """Bạn là Booking Action Extractor cho hệ thống Hiền Hựu Bus.

Nhiệm vụ: Trích xuất action và parameters từ câu của khách hàng về đặt xe buýt.

**Hỗ trợ cả tiếng Việt và tiếng Anh.**

**Actions (chỉ chọn một trong các actions sau):**
- search_trip: Tìm chuyến xe (điểm đi, điểm đến, ngày)
- get_trip_info: Xem thông tin chuyến xe
- check_seats: Kiểm tra số ghế còn trống
- create_booking: Đặt vé mới
- get_booking: Xem thông tin booking
- cancel_booking: Hủy booking
- create_payment: Tạo thanh toán
- check_payment: Kiểm tra trạng thái thanh toán
- get_my_bookings: Xem danh sách booking của tôi

**Parameters (điền thông tin có sẵn):**
- origin: Điểm đi (hanoi, ho chi minh, da nang, da lat, ta xua, nha trang)
- destination: Điểm đến (cùng danh sách trên)
- date: Ngày khởi hành (YYYY-MM-DD hoặc relative như "tomorrow", "ngày mai")
- trip_id: ID của chuyến xe
- booking_id hoặc booking_code: Mã booking
- seat_count: Số ghế muốn đặt (mặc định 1)

**Quy tắc:**
1. Nếu thiếu thông tin bắt buộc, đặt needs_clarification = true và liệt kê missing_info
2. Không tự đoán ngày nếu không rõ
3. response_language: "vi" nếu câu hỏi bằng tiếng Việt, "en" nếu bằng tiếng Anh
4. Trả lời JSON, không giải thích thêm

**Ví dụ:**

Input: "tôi muốn tìm xe đi Tà Xùa ngày mai"
Output:
{
    "action": "search_trip",
    "parameters": {
        "destination": "ta xua",
        "date": "tomorrow"
    },
    "needs_clarification": false,
    "missing_info": [],
    "response_language": "vi",
    "message": ""
}

Input: "I want to book two tickets from Hanoi to Da Lat"
Output:
{
    "action": "create_booking",
    "parameters": {
        "origin": "hanoi",
        "destination": "da lat",
        "seat_count": 2
    },
    "needs_clarification": true,
    "missing_info": ["date"],
    "response_language": "en",
    "message": "What date would you like to depart?"
}

Input: "xem vé của tôi"
Output:
{
    "action": "get_my_bookings",
    "parameters": {},
    "needs_clarification": false,
    "missing_info": [],
    "response_language": "vi",
    "message": ""
}

Chỉ trả JSON."""


@dataclass
class BookingActionResult:
    """Kết quả từ LLM action extraction"""
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    needs_clarification: bool = False
    missing_info: list[str] = field(default_factory=list)
    response_language: str = "vi"
    message: str = ""
    raw_output: str = ""
    parse_success: bool = False


class LLMBookingAgent:
    """
    LLM-Enhanced Booking Agent.

    Sử dụng LLM để:
    - Hiểu intent từ ngôn ngữ tự nhiên (VI/EN)
    - Trích xuất parameters
    - Phát hiện thông tin còn thiếu

    Sau đó gọi BookingAgent handlers để thực hiện nghiệp vụ.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        user_context: Optional[UserContext] = None,
    ):
        """
        Khởi tạo LLMBookingAgent.

        Args:
            llm_client: LLM Client (optional, sẽ tạo mới nếu không cung cấp)
            user_context: User context cho authorization (required for production)
        """
        self._llm_client = llm_client
        self._user_context = user_context

        # BookingAgent for actual business logic (uses authorized tools if context provided)
        self._booking_agent = BookingAgent()

        # Initialize authorized tools if user_context provided
        if user_context:
            self._authorized_trip_tools = AuthorizedTripTools(user_context)
            self._authorized_booking_tools = AuthorizedBookingTools(user_context)
            self._authorized_payment_tools = AuthorizedPaymentTools(user_context)
        else:
            self._authorized_trip_tools = None
            self._authorized_booking_tools = None
            self._authorized_payment_tools = None

        # Parser for LLM output
        self._parser = StructuredOutputParser(BOOKING_ACTION_SCHEMA)

    @property
    def llm_client(self) -> LLMClient:
        """Lazy initialization của LLM client"""
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    async def process(
        self,
        db: Any,
        user_id: str,
        message: str,
        state: BookingState | None = None,
        use_llm: bool = True,
    ) -> dict[str, Any]:
        """
        Xử lý message từ customer.

        Args:
            db: Database session
            user_id: ID của user
            message: Message từ customer
            state: State hiện tại (nếu có)
            use_llm: Nếu True, sử dụng LLM; False thì dùng rule-based

        Returns:
            Dict với response và updated state
        """
        # Initialize or use existing state
        if state is None:
            state = BookingState(user_id=user_id, session_id=str(datetime.utcnow().timestamp()))

        state.add_message("customer", message)

        if use_llm:
            # Use LLM for understanding
            action_result = await self._extract_action(message, state)

            if not action_result.parse_success:
                # LLM failed, fallback to rule-based
                logger.warning("LLM extraction failed, falling back to rule-based")
                return await self._process_rule_based(db, user_id, message, state)

            # Check if needs clarification
            if action_result.needs_clarification:
                return self._build_clarification_response(action_result, state)

            # Execute action
            return await self._execute_action(
                db, user_id, action_result, state
            )
        else:
            # Rule-based processing
            return await self._process_rule_based(db, user_id, message, state)

    async def _extract_action(
        self,
        message: str,
        state: BookingState,
    ) -> BookingActionResult:
        """
        Trích xuất action từ message sử dụng LLM.

        Args:
            message: Tin nhắn customer
            state: Current state

        Returns:
            BookingActionResult
        """
        # Build messages for LLM
        messages = [
            {"role": "system", "content": BOOKING_SYSTEM_INSTRUCTION}
        ]

        # Add context from state if available
        if state.context.get("available_trips"):
            trips_context = "Previous trips found: " + ", ".join([
                f"{t.get('id', 'N/A')}: {t.get('route', 'N/A')}"
                for t in state.context["available_trips"][:3]
            ])
            messages.append({"role": "assistant", "content": trips_context})

        if state.booking_id:
            messages.append({
                "role": "assistant",
                "content": f"Current booking_id: {state.booking_id}"
            })

        messages.append({"role": "user", "content": message})

        try:
            # Call LLM
            response = await self.llm_client.generate_with_messages(messages)

            # Parse response
            return self._parse_llm_response(response)

        except (LLMConfigurationError, LLMProviderError, LLMTimeoutError) as e:
            logger.warning(f"LLM error in booking agent: {e}")
            return BookingActionResult(
                action="unknown",
                parse_success=False,
                raw_output=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error in booking agent: {e}")
            return BookingActionResult(
                action="unknown",
                parse_success=False,
                raw_output=str(e),
            )

    def _parse_llm_response(self, response: str) -> BookingActionResult:
        """
        Parse LLM response thành BookingActionResult.

        Args:
            response: Raw response từ LLM

        Returns:
            BookingActionResult
        """
        result = self._parser.parse(response)

        if not result.is_success:
            logger.warning(f"Failed to parse LLM response: {result.error_message}")
            return BookingActionResult(
                action="unknown",
                parse_success=False,
                raw_output=response,
            )

        data = result.data

        return BookingActionResult(
            action=data.get("action", "unknown"),
            parameters=data.get("parameters", {}),
            needs_clarification=data.get("needs_clarification", False),
            missing_info=data.get("missing_info", []),
            response_language=data.get("response_language", "vi"),
            message=data.get("message", ""),
            raw_output=response,
            parse_success=True,
        )

    def _build_clarification_response(
        self,
        action_result: BookingActionResult,
        state: BookingState,
    ) -> dict[str, Any]:
        """
        Xây dựng phản hồi yêu cầu làm rõ.

        Args:
            action_result: Kết quả từ LLM
            state: Current state

        Returns:
            Response dict
        """
        lang = action_result.response_language
        missing = action_result.missing_info

        # Build clarification message
        if lang == "vi":
            if missing:
                missing_text = ", ".join(missing)
                clarification = f"Bạn muốn {self._get_action_display(action_result.action, lang)} nhưng tôi cần biết thêm: {missing_text}."
            else:
                clarification = action_result.message or "Bạn có thể cho tôi biết thêm thông tin không?"
        else:  # English
            if missing:
                missing_text = ", ".join(missing)
                clarification = f"To help you with {self._get_action_display(action_result.action, lang)}, I need more information about: {missing_text}."
            else:
                clarification = action_result.message or "Could you please provide more details?"

        return {
            "response": clarification,
            "success": True,
            "state": state,
            "data": {
                "action": action_result.action,
                "needs_clarification": True,
                "missing_info": action_result.missing_info,
                "response_language": lang,
            },
            "next_action": "clarification",
        }

    def _get_action_display(self, action: str, lang: str) -> str:
        """Get display name for action"""
        display_map = {
            "search_trip": {"vi": "tìm chuyến xe", "en": "find a trip"},
            "get_trip_info": {"vi": "xem thông tin chuyến", "en": "get trip info"},
            "check_seats": {"vi": "kiểm tra ghế", "en": "check seats"},
            "create_booking": {"vi": "đặt vé", "en": "book a ticket"},
            "get_booking": {"vi": "xem booking", "en": "view booking"},
            "cancel_booking": {"vi": "hủy booking", "en": "cancel booking"},
            "create_payment": {"vi": "thanh toán", "en": "make payment"},
            "check_payment": {"vi": "kiểm tra thanh toán", "en": "check payment status"},
            "get_my_bookings": {"vi": "xem danh sách vé", "en": "view my bookings"},
        }
        return display_map.get(action, {}).get(lang, action)

    async def _execute_action(
        self,
        db: Any,
        user_id: str,
        action_result: BookingActionResult,
        state: BookingState,
    ) -> dict[str, Any]:
        """
        Thực thi action thông qua BookingAgent handlers.

        Args:
            db: Database session
            user_id: User ID
            action_result: Kết quả từ LLM
            state: Current state

        Returns:
            Response dict
        """
        action = action_result.action
        params = action_result.parameters

        # Update state with extracted entities
        state.context.update(params)

        # Map action to handler
        handler_map = {
            "search_trip": self._handle_search_trip,
            "get_trip_info": self._handle_get_trip_info,
            "check_seats": self._handle_check_seats,
            "create_booking": self._handle_create_booking,
            "get_booking": self._handle_get_booking,
            "cancel_booking": self._handle_cancel_booking,
            "create_payment": self._handle_create_payment,
            "check_payment": self._handle_check_payment,
            "get_my_bookings": self._handle_get_my_bookings,
        }

        handler = handler_map.get(action)
        if not handler:
            return await self._handle_unknown(db, user_id, action, state)

        # Check authorization before executing
        auth_check = self._check_authorization(action)
        if not auth_check["allowed"]:
            logger.warning(f"Authorization denied for action '{action}': {auth_check['reason']}")
            return {
                "success": False,
                "response": auth_check["response"],
                "state": state,
                "error": f"Authorization denied: {auth_check['reason']}",
            }

        try:
            return await handler(db, user_id, params, state)
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {
                "success": False,
                "response": "Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại.",
                "error": str(e),
                "state": state,
            }

    def _check_authorization(self, action: str) -> dict[str, Any]:
        """
        Kiểm tra authorization cho action.

        Returns:
            dict với allowed (bool), reason (str), response (str)
        """
        # Map actions to tool names for authorization
        action_to_tool = {
            "search_trip": "search_trips",
            "get_trip_info": "get_trip",
            "check_seats": "check_available_seats",
            "create_booking": "create_booking",
            "get_booking": "get_booking",
            "cancel_booking": "cancel_booking",
            "create_payment": "create_payment",
            "check_payment": "get_payment",
            "get_my_bookings": "get_user_bookings",
        }

        tool_name = action_to_tool.get(action)
        if not tool_name:
            return {
                "allowed": False,
                "reason": "UNKNOWN_ACTION",
                "response": "Action không được hỗ trợ."
            }

        # If no user_context, use default CUSTOMER role for safety
        if self._user_context is None:
            # No context = assume minimal permissions
            return {
                "allowed": True,
                "reason": "NO_CONTEXT_ASSUME_MINIMAL",
                "response": "",
            }

        # Use ToolGuard to authorize
        from src.ai.security.tool_guard import get_tool_guard
        guard = get_tool_guard()
        result = guard.authorize(
            tool_name=tool_name,
            user_role=self._user_context.role,
        )

        if result.is_allowed:
            return {
                "allowed": True,
                "reason": "OK",
                "response": "",
            }
        else:
            # Build response based on reason
            if result.reason == "UNKNOWN_ROLE":
                response = "Không thể xác định quyền của bạn. Vui lòng đăng nhập lại."
            elif result.reason == "INTERNAL_ONLY_TOOL":
                response = "Hành động này không được phép thực hiện qua hệ thống tự động."
            else:
                response = "Bạn không có quyền thực hiện hành động này."

            return {
                "allowed": False,
                "reason": result.reason,
                "response": response,
            }

    async def _handle_search_trip(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle search_trip action"""
        return await self._booking_agent._handle_search_trip(
            db, state,
            {
                "origin": params.get("origin"),
                "destination": params.get("destination"),
                "date": params.get("date"),
            }
        )

    async def _handle_get_trip_info(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle get_trip_info action"""
        return await self._booking_agent._handle_get_trip_info(
            db, state,
            {"trip_id": params.get("trip_id")}
        )

    async def _handle_check_seats(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle check_seats action"""
        return await self._booking_agent._handle_check_seats(
            db, state,
            {
                "trip_id": params.get("trip_id"),
                "seat_count": params.get("seat_count", 1),
            }
        )

    async def _handle_create_booking(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle create_booking action"""
        return await self._booking_agent._handle_create_booking(
            db, state,
            {
                "trip_id": params.get("trip_id"),
                "seat_count": params.get("seat_count", 1),
            }
        )

    async def _handle_get_booking(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle get_booking action"""
        return await self._booking_agent._handle_get_booking(
            db, state,
            {
                "booking_id": params.get("booking_id"),
                "booking_code": params.get("booking_code"),
            }
        )

    async def _handle_cancel_booking(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle cancel_booking action"""
        return await self._booking_agent._handle_cancel_booking(
            db, state,
            {
                "booking_id": params.get("booking_id"),
                "booking_code": params.get("booking_code"),
            }
        )

    async def _handle_create_payment(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle create_payment action"""
        return await self._booking_agent._handle_create_payment(
            db, state,
            {"booking_id": params.get("booking_id")}
        )

    async def _handle_check_payment(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle check_payment action"""
        return await self._booking_agent._handle_check_payment(
            db, state,
            {"booking_id": params.get("booking_id")}
        )

    async def _handle_get_my_bookings(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle get_my_bookings action"""
        return await self._booking_agent._handle_get_my_bookings(db, state)

    async def _handle_unknown(
        self,
        db: Any,
        user_id: str,
        action: str,
        state: BookingState,
    ) -> dict[str, Any]:
        """Handle unknown action"""
        return await self._booking_agent._handle_unknown(db, state, action)

    async def _process_rule_based(
        self,
        db: Any,
        user_id: str,
        message: str,
        state: BookingState,
    ) -> dict[str, Any]:
        """Fallback to rule-based processing"""
        return await self._booking_agent.process(db, user_id, message, state)
