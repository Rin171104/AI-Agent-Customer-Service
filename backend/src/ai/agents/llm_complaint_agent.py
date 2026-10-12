"""
LLM-Enhanced Complaint & Refund Agent

Integrates LLM with ComplaintAgent for natural language understanding.
Supports both Vietnamese and English inputs.

Architecture:
    Customer message
           |
           v
    LLMComplaintAgent.process()
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
           v (if valid) -> ComplaintAgent handlers
           | (if clarification) -> Clarification response
           | (if invalid) -> Rule-based fallback
           |
           v
    Customer response

IMPORTANT: Agent CANNOT:
- approve_refund
- reject_refund
- mark_as_refunded
- resolve_complaint
- process_payment

Agent can ONLY create requests and read own data.
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
    COMPLAINT_REFUND_ACTION_SCHEMA,
    COMPLAINT_REFUND_ACTIONS,
    ParseStatus,
)
from src.ai.agents.complaint_agent import ComplaintAgent, ComplaintState
from src.ai.security.context import UserContext
from src.utils.logger import logger


# System instruction for complaint/refund action extraction
COMPLAINT_SYSTEM_INSTRUCTION = """Bạn là Complaint & Refund Action Extractor cho hệ thống Hiền Hựu Bus.

Nhiệm vụ: Trích xuất action và parameters từ câu của khách hàng về khiếu nại và hoàn tiền.

**Hỗ trợ cả tiếng Việt và tiếng Anh.**

**Actions (CHỈ chọn một trong các actions sau):**
- create_complaint: Tạo khiếu nại mới
- get_complaint: Xem chi tiết một khiếu nại cụ thể
- get_my_complaints: Xem danh sách tất cả khiếu nại của mình
- request_refund: Yêu cầu hoàn tiền cho booking đã hủy
- get_refund: Xem chi tiết một yêu cầu hoàn tiền cụ thể
- get_my_refunds: Xem danh sách tất cả yêu cầu hoàn tiền của mình

**CÁC ACTION CẤM (KHÔNG BAO GIỜ được phép):**
- approve_refund: PHÊ DUYỆT hoàn tiền - CHỈ OWNER làm được
- reject_refund: TỪ CHỐI hoàn tiền - CHỈ OWNER làm được
- mark_as_refunded: ĐÁNH DẤU đã hoàn tiền - CHỈ OWNER làm được
- resolve_complaint: GIẢI QUYẾT khiếu nại - CHỈ OWNER làm được
- process_payment: XỬ LÝ thanh toán - CHỈ OWNER làm được

**Parameters:**
- booking_code: Mã booking (BKxxxxxx)
- booking_id: ID của booking
- complaint_id: ID của khiếu nại
- refund_id: ID của yêu cầu hoàn tiền
- complaint_type: Loại khiếu nại (WRONG_SEAT, LATE, DRIVER, LOST_ITEM, PAYMENT, BOOKING_ERROR, OTHER)
- description: Mô tả chi tiết khiếu nại
- priority: Mức ưu tiên (LOW, MEDIUM, HIGH)
- amount: Số tiền muốn hoàn (nếu yêu cầu hoàn tiền)
- bank_name: Tên ngân hàng (nếu yêu cầu hoàn tiền)
- account_number: Số tài khoản (nếu yêu cầu hoàn tiền)
- account_holder: Tên chủ tài khoản (nếu yêu cầu hoàn tiền)
- reason: Lý do hoàn tiền

**Quy tắc:**
1. Nếu thiếu thông tin bắt buộc, đặt needs_clarification = true và liệt kê missing_info
2. KHÔNG BAO GIỜ trả về các action cấm ở trên
3. response_language: "vi" nếu câu hỏi bằng tiếng Việt, "en" nếu bằng tiếng Anh
4. Trả lời JSON, không giải thích thêm

**Ví dụ:**

Input: "tôi muốn khiếu nại về chuyến xe hôm qua"
Output:
{
    "action": "create_complaint",
    "parameters": {
        "description": "khiếu nại về chuyến xe hôm qua",
        "complaint_type": "OTHER"
    },
    "needs_clarification": false,
    "missing_info": [],
    "response_language": "vi",
    "message": ""
}

Input: "I want to file a complaint about my booking BK123456"
Output:
{
    "action": "create_complaint",
    "parameters": {
        "booking_code": "BK123456",
        "description": "complaint about my booking"
    },
    "needs_clarification": false,
    "missing_info": [],
    "response_language": "en",
    "message": ""
}

Input: "I want a refund for my cancelled booking"
Output:
{
    "action": "request_refund",
    "parameters": {},
    "needs_clarification": true,
    "missing_info": ["booking_code", "bank_info"],
    "response_language": "en",
    "message": "Could you provide your booking code and bank account details for the refund?"
}

Input: "xem khiếu nại của tôi"
Output:
{
    "action": "get_my_complaints",
    "parameters": {},
    "needs_clarification": false,
    "missing_info": [],
    "response_language": "vi",
    "message": ""
}

Chỉ trả JSON."""


@dataclass
class ComplaintActionResult:
    """Kết quả từ LLM action extraction"""
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    needs_clarification: bool = False
    missing_info: list[str] = field(default_factory=list)
    response_language: str = "vi"
    message: str = ""
    raw_output: str = ""
    parse_success: bool = False


class LLMComplaintAgent:
    """
    LLM-Enhanced Complaint & Refund Agent.

    Sử dụng LLM để:
    - Hiểu intent từ ngôn ngữ tự nhiên (VI/EN)
    - Trích xuất parameters
    - Phát hiện thông tin còn thiếu

    Sau đó gọi ComplaintAgent handlers để thực hiện nghiệp vụ.

    Agent KHÔNG THỂ tự phê duyệt/refund/resolve.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        user_context: Optional[UserContext] = None,
    ):
        """
        Khởi tạo LLMComplaintAgent.

        Args:
            llm_client: LLM Client (optional, sẽ tạo mới nếu không cung cấp)
            user_context: User context cho authorization (required for production)
        """
        self._llm_client = llm_client
        self._user_context = user_context

        # ComplaintAgent for actual business logic
        self._complaint_agent = ComplaintAgent()

        # Parser for LLM output
        self._parser = StructuredOutputParser(COMPLAINT_REFUND_ACTION_SCHEMA)

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
        state: ComplaintState | None = None,
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
            state = ComplaintState(user_id=user_id, session_id=str(datetime.utcnow().timestamp()))

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
        state: ComplaintState,
    ) -> ComplaintActionResult:
        """
        Trích xuất action từ message sử dụng LLM.

        Args:
            message: Tin nhắn customer
            state: Current state

        Returns:
            ComplaintActionResult
        """
        # Build messages for LLM
        messages = [
            {"role": "system", "content": COMPLAINT_SYSTEM_INSTRUCTION}
        ]

        # Add context from state if available
        if state.context.get("last_complaint"):
            complaint = state.context["last_complaint"]
            messages.append({
                "role": "assistant",
                "content": f"Last complaint: {complaint.get('complaint_code', 'N/A')}"
            })

        if state.context.get("last_refund"):
            refund = state.context["last_refund"]
            messages.append({
                "role": "assistant",
                "content": f"Last refund: {refund.get('refund_code', 'N/A')}"
            })

        messages.append({"role": "user", "content": message})

        try:
            # Call LLM
            response = await self.llm_client.generate_with_messages(messages)

            # Parse response
            return self._parse_llm_response(response)

        except (LLMConfigurationError, LLMProviderError, LLMTimeoutError) as e:
            logger.warning(f"LLM error in complaint agent: {e}")
            return ComplaintActionResult(
                action="unknown",
                parse_success=False,
                raw_output=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error in complaint agent: {e}")
            return ComplaintActionResult(
                action="unknown",
                parse_success=False,
                raw_output=str(e),
            )

    def _parse_llm_response(self, response: str) -> ComplaintActionResult:
        """
        Parse LLM response thành ComplaintActionResult.

        Args:
            response: Raw response từ LLM

        Returns:
            ComplaintActionResult
        """
        result = self._parser.parse(response)

        if not result.is_success:
            logger.warning(f"Failed to parse LLM response: {result.error_message}")
            return ComplaintActionResult(
                action="unknown",
                parse_success=False,
                raw_output=response,
            )

        data = result.data

        # Additional security check: ensure action is not in forbidden list
        action = data.get("action", "unknown")
        forbidden_actions = [
            "approve_refund", "reject_refund", "mark_as_refunded",
            "resolve_complaint", "process_payment"
        ]

        if action in forbidden_actions:
            logger.warning(f"LLM returned forbidden action: {action}")
            return ComplaintActionResult(
                action="unknown",
                parse_success=False,
                raw_output=response,
            )

        return ComplaintActionResult(
            action=action,
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
        action_result: ComplaintActionResult,
        state: ComplaintState,
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
                missing_text = self._format_missing_info_vi(missing)
                clarification = f"Để {self._get_action_display(action_result.action, lang)}, tôi cần thêm: {missing_text}."
            else:
                clarification = action_result.message or "Bạn có thể cho tôi biết thêm thông tin không?"
        else:  # English
            if missing:
                missing_text = self._format_missing_info_en(missing)
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

    def _format_missing_info_vi(self, missing: list[str]) -> str:
        """Format missing info for Vietnamese"""
        display_map = {
            "booking_code": "mã booking (BKxxxxxx)",
            "booking_id": "ID booking",
            "complaint_id": "mã khiếu nại",
            "refund_id": "mã hoàn tiền",
            "description": "mô tả chi tiết",
            "bank_info": "thông tin tài khoản ngân hàng",
            "bank_name": "tên ngân hàng",
            "account_number": "số tài khoản",
            "account_holder": "tên chủ tài khoản",
            "amount": "số tiền muốn hoàn",
        }
        return ", ".join(display_map.get(m, m) for m in missing)

    def _format_missing_info_en(self, missing: list[str]) -> str:
        """Format missing info for English"""
        display_map = {
            "booking_code": "booking code (BKxxxxxx)",
            "booking_id": "booking ID",
            "complaint_id": "complaint ID",
            "refund_id": "refund ID",
            "description": "detailed description",
            "bank_info": "bank account information",
            "bank_name": "bank name",
            "account_number": "account number",
            "account_holder": "account holder name",
            "amount": "refund amount",
        }
        return ", ".join(display_map.get(m, m) for m in missing)

    def _get_action_display(self, action: str, lang: str) -> str:
        """Get display name for action"""
        display_map = {
            "create_complaint": {"vi": "tạo khiếu nại", "en": "file a complaint"},
            "get_complaint": {"vi": "xem khiếu nại", "en": "check complaint details"},
            "get_my_complaints": {"vi": "xem danh sách khiếu nại", "en": "view your complaints"},
            "request_refund": {"vi": "yêu cầu hoàn tiền", "en": "request a refund"},
            "get_refund": {"vi": "xem yêu cầu hoàn tiền", "en": "check refund details"},
            "get_my_refunds": {"vi": "xem danh sách hoàn tiền", "en": "view your refund requests"},
        }
        return display_map.get(action, {}).get(lang, action)

    async def _execute_action(
        self,
        db: Any,
        user_id: str,
        action_result: ComplaintActionResult,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """
        Thực thi action thông qua ComplaintAgent handlers.

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
            "create_complaint": self._handle_create_complaint,
            "get_complaint": self._handle_get_complaint,
            "get_my_complaints": self._handle_get_my_complaints,
            "request_refund": self._handle_request_refund,
            "get_refund": self._handle_get_refund,
            "get_my_refunds": self._handle_get_my_refunds,
        }

        handler = handler_map.get(action)
        if not handler:
            return await self._handle_unknown(db, user_id, action, state)

        # Check authorization before executing
        auth_check = self._check_authorization(action)
        if not auth_check["allowed"]:
            logger.warning(f"Authorization denied for action '{action}': {auth_check['reason']}")
            lang = action_result.response_language
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
            lang = action_result.response_language
            return {
                "success": False,
                "response": "Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại." if lang == "vi" else "An error occurred. Please try again.",
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
            "create_complaint": "create_complaint",
            "get_complaint": "get_complaint",
            "get_my_complaints": "get_customer_complaints",
            "request_refund": "create_refund_request",
            "get_refund": "get_refund",
            "get_my_refunds": "get_customer_refunds",
        }

        tool_name = action_to_tool.get(action)
        if not tool_name:
            return {
                "allowed": False,
                "reason": "UNKNOWN_ACTION",
                "response": "Action không được hỗ trợ."
            }

        # If no user_context, only allow public read-only operations
        if self._user_context is None:
            # Public operations that don't expose user data
            public_actions = set()  # Complaint/refund operations always require auth
            if action in public_actions:
                return {
                    "allowed": True,
                    "reason": "NO_CONTEXT_PUBLIC_OPERATION",
                    "response": "",
                }
            else:
                # Require authentication for complaint/refund access
                return {
                    "allowed": False,
                    "reason": "AUTHENTICATION_REQUIRED",
                    "response": "Vui lòng đăng nhập để thực hiện chức năng này." if True else "Please log in to access this feature.",
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

    async def _handle_create_complaint(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Handle create_complaint action"""
        return await self._complaint_agent._handle_create_complaint(
            db, state, params, params.get("description", "")
        )

    async def _handle_get_complaint(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Handle get_complaint action"""
        return await self._complaint_agent._handle_get_complaint(
            db, state, params
        )

    async def _handle_get_my_complaints(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Handle get_my_complaints action"""
        return await self._complaint_agent._handle_get_my_complaints(db, state)

    async def _handle_request_refund(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Handle request_refund action"""
        return await self._complaint_agent._handle_request_refund(
            db, state, params, ""
        )

    async def _handle_get_refund(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Handle get_refund action"""
        return await self._complaint_agent._handle_get_refund(db, state, params)

    async def _handle_get_my_refunds(
        self,
        db: Any,
        user_id: str,
        params: dict,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Handle get_my_refunds action"""
        return await self._complaint_agent._handle_get_my_refunds(db, state)

    async def _handle_unknown(
        self,
        db: Any,
        user_id: str,
        action: str,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Handle unknown action"""
        return await self._complaint_agent._handle_unknown(state, action)

    async def _process_rule_based(
        self,
        db: Any,
        user_id: str,
        message: str,
        state: ComplaintState,
    ) -> dict[str, Any]:
        """Fallback to rule-based processing"""
        return await self._complaint_agent.process(db, user_id, message, state)
