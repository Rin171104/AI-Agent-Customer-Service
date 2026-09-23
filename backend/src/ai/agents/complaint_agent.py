"""
Complaint & Refund Agent

Xử lý các nghiệp vụ:
    - Tạo khiếu nại
    - Xem khiếu nại của mình
    - Yêu cầu hoàn tiền
    - Xem trạng thái hoàn tiền

Kiến trúc:
    Customer -> Orchestrator -> ComplaintAgent -> Tools -> Services -> Database

Quyền:
    - Customer: Tạo complaint, xem complaint của mình, tạo refund request, xem refund của mình
    - Owner: Duyệt/refund (NOT trong scope của Agent này)
"""
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from src.ai.tools.complaint_tools import ComplaintTools
from src.ai.tools.refund_tools import RefundTools
from src.ai.tools.booking_tools import BookingTools
from src.ai.tools.payment_tools import PaymentTools
from src.utils.logger import logger


@dataclass
class ComplaintState:
    """State cho Complaint Agent"""
    user_id: str
    session_id: str = ""
    intent: Optional[str] = None
    booking_id: Optional[str] = None
    complaint_id: Optional[str] = None
    refund_id: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    final_status: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str):
        """Thêm message vào history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })

    def add_tool_result(self, tool: str, result: Dict[str, Any]):
        """Thêm tool result"""
        self.tool_results.append({
            "tool": tool,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })


class ComplaintAgent:
    """
    Complaint & Refund Agent

    Agent này xử lý các yêu cầu liên quan đến:
    - Khiếu nại
    - Hoàn tiền
    """

    # Intent patterns - đặc hiệu hơn để tránh overlap
    INTENT_PATTERNS = {
        "create_complaint": [
            r"^tôi\s+muốn\s+khiếu\s*nại",
            r"^khiếu\s*nại",
            r"^có\s+vấn\s*đề",
            r"^phàn\s*nàn",
            r"complaint",
            r"báo\s*cáo\s*sự\s*cố",
        ],
        "get_complaint": [
            r"^xem\s+khiếu\s*nại",
            r"^khiếu\s*nại\s+của",
            r"^trạng\s*thái\s+khiếu\s*nại",
            r"xem\s+chi\s*tiết\s+khiếu\s*nại",
        ],
        "get_my_complaints": [
            r"^danh\s*sách\s+khiếu\s*nại",
            r"^các\s+khiếu\s*nại",
            r"liệt\s*kê\s+khiếu\s*nại",
        ],
        "request_refund": [
            r"^tôi\s+muốn\s+hoàn\s*tiền",
            r"^yêu\s*cầu\s+hoàn\s*tiền",
            r"^hoàn\s*tiền\s+",
            r"^xin\s+hoàn\s*tiền",
            r"refund",
        ],
        "get_refund": [
            r"^xem\s+hoàn\s*tiền",
            r"^hoàn\s*tiền\s+của",
            r"^trạng\s*thái\s+hoàn\s*tiền",
            r"xem\s+chi\s*tiết\s+hoàn\s*tiền",
        ],
        "get_my_refunds": [
            r"^danh\s*sách\s+hoàn\s*tiền",
            r"^các\s+yêu\s*cầu\s+hoàn",
            r"liệt\s*kê\s+hoàn\s*tiền",
        ],
    }

    # Complaint types mapping
    COMPLAINT_TYPE_KEYWORDS = {
        "WRONG_SEAT": ["sai ghế", "ghế sai", "sai chỗ"],
        "LATE": ["muộn", "trễ", "đến muộn", "đón muộn"],
        "DRIVER": ["tài xế", "lái xe", "lái", "tài xế"],
        "LOST_ITEM": ["mất đồ", "quên đồ", "mất vật"],
        "PAYMENT": ["thanh toán", "tiền", "payment"],
        "BOOKING_ERROR": ["sai thông tin", "sai booking", "lỗi đặt"],
        "REFUND": ["hoàn tiền", "refund"],
        "OTHER": [],
    }

    def __init__(self):
        self.complaint_tools = ComplaintTools()
        self.refund_tools = RefundTools()
        self.booking_tools = BookingTools()
        self.payment_tools = PaymentTools()
        self.logger = logger

    def detect_intent(self, message: str) -> str:
        """Nhận diện intent từ message"""
        message_lower = message.lower()

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent

        return "unknown"

    def extract_complaint_type(self, message: str) -> Optional[str]:
        """Trích xuất complaint type từ message"""
        message_lower = message.lower()

        for ctype, keywords in self.COMPLAINT_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return ctype

        return "OTHER"

    def extract_entities(self, message: str) -> Dict[str, Any]:
        """Trích xuất entities từ message"""
        entities = {
            "booking_id": None,
            "booking_code": None,
            "complaint_id": None,
            "refund_id": None,
            "complaint_type": None,
            "description": None,
            "priority": "MEDIUM",
            # Refund related
            "amount": None,
            "bank_name": None,
            "account_number": None,
            "account_holder": None,
            "reason": None,
        }

        message_lower = message.lower()

        # Booking code patterns
        booking_patterns = [
            r"(?:booking|mã|vé)[:\s]*([A-Z0-9]{6,})",
            r"BK([0-9]{6,})",
        ]
        for pattern in booking_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entities["booking_code"] = match.group(1).upper()

        # Complaint ID
        complaint_pattern = r"(?:complaint|khiếu\s*nại)[:\s]*([a-z0-9-]+)"
        match = re.search(complaint_pattern, message_lower)
        if match:
            entities["complaint_id"] = match.group(1)

        # Priority
        if "khẩn" in message_lower or "gấp" in message_lower or "cao" in message_lower:
            entities["priority"] = "HIGH"
        elif "thấp" in message_lower:
            entities["priority"] = "LOW"

        return entities

    async def process(
        self,
        db: Any,
        user_id: str,
        message: str,
        state: Optional[ComplaintState] = None
    ) -> Dict[str, Any]:
        """
        Xử lý message từ customer.

        Args:
            db: Database session
            user_id: ID của user
            message: Message từ customer
            state: State hiện tại

        Returns:
            Dict với response và updated state
        """
        if state is None:
            state = ComplaintState(user_id=user_id, session_id=str(datetime.utcnow().timestamp()))

        state.add_message("customer", message)

        intent = self.detect_intent(message)
        state.intent = intent

        entities = self.extract_entities(message)
        state.context.update(entities)

        self.logger.info(f"ComplaintAgent - intent: {intent}, entities: {entities}")

        try:
            if intent == "create_complaint":
                result = await self._handle_create_complaint(db, state, entities, message)
            elif intent == "get_complaint":
                result = await self._handle_get_complaint(db, state, entities)
            elif intent == "get_my_complaints":
                result = await self._handle_get_my_complaints(db, state)
            elif intent == "request_refund":
                result = await self._handle_request_refund(db, state, entities, message)
            elif intent == "get_refund":
                result = await self._handle_get_refund(db, state, entities)
            elif intent == "get_my_refunds":
                result = await self._handle_get_my_refunds(db, state)
            else:
                result = await self._handle_unknown(state, message)

        except Exception as e:
            self.logger.error(f"Error processing intent {intent}: {e}")
            result = {
                "success": False,
                "response": "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.",
                "error": str(e)
            }

        if "tool_result" in result:
            state.add_tool_result(intent, result["tool_result"])

        state.add_message("agent", result.get("response", ""))

        return {
            "response": result.get("response", ""),
            "success": result.get("success", False),
            "state": state,
            "data": result.get("data"),
            "next_action": result.get("next_action"),
            "requires_human": result.get("requires_human", False),
            "human_action": result.get("human_action"),
        }

    async def _handle_create_complaint(
        self,
        db: Any,
        state: ComplaintState,
        entities: Dict[str, Any],
        message: str
    ) -> Dict[str, Any]:
        """Xử lý tạo khiếu nại"""
        booking_id = entities.get("booking_id") or state.booking_id
        booking_code = entities.get("booking_code") or state.context.get("booking_code")

        # Lấy booking_id từ code nếu có
        if booking_code and not booking_id:
            booking_result = await self.booking_tools.get_booking(
                db=db,
                booking_code=booking_code
            )
            if booking_result.get("success"):
                booking_id = booking_result.get("booking", {}).get("id")

        # Extract complaint type
        complaint_type = entities.get("complaint_type") or self.extract_complaint_type(message)

        # Extract description (phần mô tả sau từ khóa khiếu nại)
        description = entities.get("description") or message

        # Nếu booking_id không có, vẫn cho phép tạo complaint không có booking
        if booking_id:
            # Verify booking thuộc customer
            booking_result = await self.booking_tools.get_booking(db=db, booking_id=booking_id)
            if booking_result.get("success"):
                booking = booking_result.get("booking", {})
                if booking.get("user_id") != state.user_id:
                    return {
                        "success": False,
                        "response": "Bạn không có quyền tạo khiếu nại cho booking này.",
                    }

        # Tạo complaint
        result = await self.complaint_tools.create_complaint(
            db=db,
            customer_id=state.user_id,
            complaint_type=complaint_type,
            description=description,
            booking_id=booking_id,
            priority=entities.get("priority", "MEDIUM")
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tạo được khiếu nại: {result.get('error')}",
                "tool_result": result
            }

        complaint = result.get("complaint", {})
        state.complaint_id = complaint.get("id")

        response = f"✓ Đã tiếp nhận khiếu nại của bạn!\n\n"
        response += f"- Mã khiếu nại: {complaint.get('complaint_code')}\n"
        response += f"- Loại: {self._format_complaint_type(complaint.get('type'))}\n"
        response += f"- Trạng thái: Đang xử lý\n"
        response += f"- Mức ưu tiên: {complaint.get('priority')}\n\n"
        response += "Nhà xe sẽ xem xét và phản hồi sớm nhất có thể."

        return {
            "success": True,
            "response": response,
            "data": {"complaint": complaint},
            "tool_result": result
        }

    async def _handle_get_complaint(
        self,
        db: Any,
        state: ComplaintState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý xem chi tiết khiếu nại"""
        complaint_id = entities.get("complaint_id") or state.complaint_id

        if not complaint_id:
            # Thử lấy từ context
            if state.context.get("last_complaint"):
                complaint_id = state.context["last_complaint"].get("id")

        if not complaint_id:
            return {
                "success": True,
                "response": "Bạn muốn xem khiếu nại nào? Vui lòng cung cấp mã khiếu nại.",
                "next_action": "ask_complaint_id"
            }

        result = await self.complaint_tools.get_complaint(db=db, complaint_id=complaint_id)

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm được khiếu nại: {result.get('error')}",
                "tool_result": result
            }

        complaint = result.get("complaint", {})

        # Authorization check - chỉ customer tạo mới được xem
        if complaint.get("customer_id") != state.user_id:
            return {
                "success": False,
                "response": "Bạn không có quyền xem khiếu nại này."
            }

        state.complaint_id = complaint.get("id")
        state.context["last_complaint"] = complaint

        response = f"Thông tin khiếu nại:\n"
        response += f"- Mã: {complaint.get('complaint_code')}\n"
        response += f"- Loại: {self._format_complaint_type(complaint.get('type'))}\n"
        response += f"- Mô tả: {complaint.get('description')}\n"
        response += f"- Trạng thái: {self._format_complaint_status(complaint.get('status'))}\n"
        response += f"- Mức ưu tiên: {complaint.get('priority')}\n"

        if complaint.get("owner_note"):
            response += f"- Phản hồi: {complaint.get('owner_note')}\n"

        if complaint.get("booking"):
            booking = complaint["booking"]
            response += f"\nBooking liên quan:\n"
            response += f"- Mã: {booking.get('booking_code')}\n"

        return {
            "success": True,
            "response": response,
            "data": {"complaint": complaint},
            "tool_result": result
        }

    async def _handle_get_my_complaints(
        self,
        db: Any,
        state: ComplaintState
    ) -> Dict[str, Any]:
        """Xử lý xem danh sách khiếu nại của mình"""
        result = await self.complaint_tools.get_customer_complaints(
            db=db,
            customer_id=state.user_id
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không lấy được danh sách: {result.get('error')}",
                "tool_result": result
            }

        complaints = result.get("complaints", [])

        if not complaints:
            return {
                "success": True,
                "response": "Bạn chưa có khiếu nại nào.",
                "data": {"complaints": []}
            }

        complaint_list = []
        for c in complaints:
            status_icon = "🔴" if c["status"] == "OPEN" else "🟡" if c["status"] == "IN_PROGRESS" else "🟢"
            item = f"{status_icon} {c['complaint_code']}: {self._format_complaint_type(c['type'])} - {self._format_complaint_status(c['status'])}"
            complaint_list.append(item)

        response = f"Bạn có {len(complaints)} khiếu nại:\n\n" + "\n".join(complaint_list)
        response += "\n\nBạn muốn xem chi tiết khiếu nại nào?"

        return {
            "success": True,
            "response": response,
            "data": {"complaints": complaints},
            "tool_result": result
        }

    async def _handle_request_refund(
        self,
        db: Any,
        state: ComplaintState,
        entities: Dict[str, Any],
        message: str
    ) -> Dict[str, Any]:
        """
        Xử lý yêu cầu hoàn tiền.

        IMPORTANT: Agent KHÔNG tự approve/refund.
        Agent chỉ tạo refund request → WAITING_OWNER_APPROVAL.
        Owner mới là người approve/reject/mark_as_refunded.
        """
        booking_id = entities.get("booking_id") or state.booking_id
        booking_code = entities.get("booking_code") or state.context.get("booking_code")

        # Lấy booking_id từ code nếu có
        if booking_code and not booking_id:
            booking_result = await self.booking_tools.get_booking(
                db=db,
                booking_code=booking_code
            )
            if booking_result.get("success"):
                booking_id = booking_result.get("booking", {}).get("id")

        if not booking_id:
            # Thử lấy từ context (handoff)
            if state.context.get("last_booking_id"):
                booking_id = state.context["last_booking_id"]

        if not booking_id:
            return {
                "success": True,
                "response": "Bạn muốn hoàn tiền cho booking nào? Vui lòng cung cấp mã booking (BKxxxxxx).",
                "next_action": "ask_booking_code"
            }

        # Lấy thông tin booking
        booking_result = await self.booking_tools.get_booking(db=db, booking_id=booking_id)

        if not booking_result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm thấy booking: {booking_result.get('error')}",
                "tool_result": booking_result
            }

        booking = booking_result.get("booking", {})

        # Authorization check
        if booking.get("user_id") != state.user_id:
            return {
                "success": False,
                "response": "Bạn không có quyền yêu cầu hoàn tiền cho booking này."
            }

        # Kiểm tra booking đã bị hủy chưa
        if booking.get("status") == "CANCELLED":
            return {
                "success": False,
                "response": "Booking đã bị hủy trước đó, không thể yêu cầu hoàn tiền."
            }

        # Extract refund info từ message
        amount = entities.get("amount") or booking.get("total_amount")
        bank_name = entities.get("bank_name")
        account_number = entities.get("account_number")
        account_holder = entities.get("account_holder")
        reason = entities.get("reason")

        # Nếu thiếu thông tin, yêu cầu cung cấp
        if not bank_name or not account_number or not account_holder:
            response = f"Để yêu cầu hoàn tiền cho booking {booking.get('booking_code')}, vui lòng cung cấp:\n"
            response += f"- Số tiền muốn hoàn (mặc định: {amount:,} VND)\n"
            response += f"- Tên ngân hàng\n"
            response += f"- Số tài khoản\n"
            response += f"- Tên chủ tài khoản\n"
            response += f"\nVí dụ: 'Hoàn tiền BK123456, 200000 VND, Vietcombank, 1234567890, Nguyễn Văn A'"

            return {
                "success": True,
                "response": response,
                "data": {
                    "booking": booking,
                    "missing_info": {
                        "amount": amount,
                        "bank_name": not bool(bank_name),
                        "account_number": not bool(account_number),
                        "account_holder": not bool(account_holder),
                    }
                },
                "next_action": "provide_bank_info"
            }

        # Tạo refund request
        refund_result = await self.refund_tools.create_refund_request(
            db=db,
            customer_id=state.user_id,
            booking_id=booking_id,
            amount=amount,
            bank_name=bank_name,
            account_number=account_number,
            account_holder=account_holder,
            reason=reason
        )

        if not refund_result.get("success"):
            return {
                "success": False,
                "response": f"Không tạo được yêu cầu hoàn tiền: {refund_result.get('error')}",
                "tool_result": refund_result
            }

        refund = refund_result.get("refund", {})
        state.refund_id = refund.get("id")
        state.context["last_refund"] = refund

        response = f"✓ Đã tạo yêu cầu hoàn tiền!\n\n"
        response += f"- Mã hoàn tiền: {refund.get('refund_code')}\n"
        response += f"- Booking: {booking.get('booking_code')}\n"
        response += f"- Số tiền: {refund.get('amount'):,} VND\n"
        response += f"- Ngân hàng: {refund.get('bank_name')}\n"
        response += f"- STK: {refund.get('account_number')}\n"
        response += f"- Trạng thái: Chờ phê duyệt\n\n"
        response += "Yêu cầu của bạn đang chờ nhà xe xem xét và phê duyệt.\n"
        response += "Bạn sẽ được thông báo khi có kết quả."

        # IMPORTANT: requires_human = true vì Owner cần approve
        return {
            "success": True,
            "response": response,
            "data": {
                "refund": refund,
                "booking": booking
            },
            "tool_result": refund_result,
            "requires_human": True,
            "human_action": "approve_refund",
            "final_status": "WAITING_OWNER_APPROVAL"
        }

    async def _handle_get_refund(
        self,
        db: Any,
        state: ComplaintState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý xem chi tiết refund"""
        refund_id = entities.get("refund_id") or state.refund_id

        if not refund_id:
            if state.context.get("last_refund"):
                refund_id = state.context["last_refund"].get("id")

        if not refund_id:
            return {
                "success": True,
                "response": "Bạn muốn xem yêu cầu hoàn tiền nào? Vui lòng cung cấp mã hoàn tiền.",
                "next_action": "ask_refund_id"
            }

        result = await self.refund_tools.get_refund(db=db, refund_id=refund_id)

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm thấy yêu cầu hoàn tiền: {result.get('error')}",
                "tool_result": result
            }

        refund = result.get("refund", {})
        state.refund_id = refund.get("id")
        state.context["last_refund"] = refund

        response = f"Thông tin hoàn tiền:\n"
        response += f"- Mã: {refund.get('refund_code')}\n"
        response += f"- Số tiền: {refund.get('amount'):,} VND\n"
        response += f"- Ngân hàng: {refund.get('bank_name')}\n"
        response += f"- STK: {refund.get('account_number')}\n"
        response += f"- Trạng thái: {self._format_refund_status(refund.get('status'))}\n"

        if refund.get("owner_note"):
            response += f"- Ghi chú: {refund.get('owner_note')}\n"

        if refund.get("booking"):
            response += f"\nBooking: {refund['booking'].get('booking_code')}"

        return {
            "success": True,
            "response": response,
            "data": {"refund": refund},
            "tool_result": result
        }

    async def _handle_get_my_refunds(
        self,
        db: Any,
        state: ComplaintState
    ) -> Dict[str, Any]:
        """Xử lý xem danh sách refund của mình"""
        result = await self.refund_tools.get_customer_refunds(
            db=db,
            customer_id=state.user_id
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không lấy được danh sách: {result.get('error')}",
                "tool_result": result
            }

        refunds = result.get("refunds", [])

        if not refunds:
            return {
                "success": True,
                "response": "Bạn chưa có yêu cầu hoàn tiền nào.",
                "data": {"refunds": []}
            }

        refund_list = []
        for r in refunds:
            status_icon = "⏳" if r["status"] == "WAITING_OWNER_APPROVAL" else "✅" if r["status"] in ["APPROVED", "REFUNDED"] else "❌"
            item = f"{status_icon} {r['refund_code']}: {r['amount']:,} VND - {self._format_refund_status(r['status'])}"
            refund_list.append(item)

        response = f"Bạn có {len(refunds)} yêu cầu hoàn tiền:\n\n" + "\n".join(refund_list)
        response += "\n\nBạn muốn xem chi tiết yêu cầu nào?"

        return {
            "success": True,
            "response": response,
            "data": {"refunds": refunds},
            "tool_result": result
        }

    async def _handle_unknown(
        self,
        state: ComplaintState,
        message: str
    ) -> Dict[str, Any]:
        """Xử lý intent không xác định"""
        return {
            "success": True,
            "response": "Tôi có thể giúp bạn:\n"
                       "- Tạo khiếu nại: 'Tôi muốn khiếu nại về chuyến xe'\n"
                       "- Xem khiếu nại: 'Xem khiếu nại của tôi'\n"
                       "- Yêu cầu hoàn tiền: 'Tôi muốn hoàn tiền booking BK001'\n"
                       "- Xem hoàn tiền: 'Xem trạng thái hoàn tiền'\n\n"
                       "Bạn cần hỗ trợ gì?",
            "next_action": "help"
        }

    def _format_complaint_type(self, ctype: str) -> str:
        """Format complaint type"""
        type_map = {
            "WRONG_SEAT": "Sai ghế",
            "LATE": "Xe đến muộn",
            "DRIVER": "Vấn đề tài xế",
            "LOST_ITEM": "Mất đồ",
            "PAYMENT": "Vấn đề thanh toán",
            "BOOKING_ERROR": "Lỗi đặt vé",
            "REFUND": "Yêu cầu hoàn tiền",
            "OTHER": "Khác",
        }
        return type_map.get(ctype, ctype)

    def _format_complaint_status(self, status: str) -> str:
        """Format complaint status"""
        status_map = {
            "OPEN": "Đang mở",
            "IN_PROGRESS": "Đang xử lý",
            "RESOLVED": "Đã giải quyết",
        }
        return status_map.get(status, status)

    def _format_refund_status(self, status: str) -> str:
        """Format refund status"""
        status_map = {
            "REQUESTED": "Đã yêu cầu",
            "WAITING_OWNER_APPROVAL": "Chờ phê duyệt",
            "APPROVED": "Đã duyệt",
            "REJECTED": "Từ chối",
            "REFUNDED": "Đã hoàn tiền",
        }
        return status_map.get(status, status)
