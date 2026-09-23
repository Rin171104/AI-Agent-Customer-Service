"""
Conversation State - Shared state cho orchestration

State được duy trì xuyên suốt conversation để:
- Lưu context giữa các messages
- Hỗ trợ handoff giữa agents
- Theo dõi conversation history
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ConversationState:
    """
    Shared state cho toàn bộ conversation.

    Attributes:
        user_id: ID của user hiện tại
        session_id: ID của session (dùng để tracking)
        current_agent: Agent đang xử lý
        intent: Intent đã được detect

        trip_id, booking_id, payment_id, complaint_id, refund_id:
            Các IDs được trích xuất trong conversation

        messages: Lịch sử messages
        tool_results: Kết quả từ tools

        handoff_history: Lịch sử chuyển agent
        requires_human: Có cần human approval không
        human_action: Action cần human approval

        final_status: Trạng thái cuối cùng của conversation
    """
    user_id: str
    session_id: str = ""
    current_agent: Optional[str] = None
    intent: Optional[str] = None

    # Entity IDs
    trip_id: Optional[str] = None
    booking_id: Optional[str] = None
    payment_id: Optional[str] = None
    complaint_id: Optional[str] = None
    refund_id: Optional[str] = None

    # Conversation history
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)

    # Handoff tracking
    handoff_history: List[Dict[str, Any]] = field(default_factory=list)

    # Human-in-the-loop
    requires_human: bool = False
    human_action: Optional[str] = None

    # Final status
    final_status: Optional[str] = None

    def __post_init__(self):
        """Khởi tạo session_id nếu chưa có"""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Thêm message vào history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })

    def add_tool_result(self, agent: str, tool: str, result: Dict[str, Any]):
        """Thêm tool result"""
        self.tool_results.append({
            "agent": agent,
            "tool": tool,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

    def add_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context_keys: Optional[List[str]] = None
    ):
        """Ghi nhận handoff giữa các agents"""
        # Lấy relevant context
        context_data = {}
        if context_keys:
            for key in context_keys:
                value = getattr(self, key, None)
                if value:
                    context_data[key] = value

        self.handoff_history.append({
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "context_keys": context_keys or [],
            "context_data": context_data
        })

    def set_entity_id(self, entity_type: str, entity_id: str):
        """Set entity ID"""
        valid_types = ["trip", "booking", "payment", "complaint", "refund"]
        if entity_type in valid_types:
            setattr(self, f"{entity_type}_id", entity_id)

    def get_entity_id(self, entity_type: str) -> Optional[str]:
        """Get entity ID"""
        valid_types = ["trip", "booking", "payment", "complaint", "refund"]
        if entity_type in valid_types:
            return getattr(self, f"{entity_type}_id", None)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dict for serialization"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "current_agent": self.current_agent,
            "intent": self.intent,
            "trip_id": self.trip_id,
            "booking_id": self.booking_id,
            "payment_id": self.payment_id,
            "complaint_id": self.complaint_id,
            "refund_id": self.refund_id,
            "messages": self.messages,
            "tool_results": self.tool_results,
            "handoff_history": self.handoff_history,
            "requires_human": self.requires_human,
            "human_action": self.human_action,
            "final_status": self.final_status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationState":
        """Create state from dict"""
        return cls(
            user_id=data.get("user_id", ""),
            session_id=data.get("session_id", ""),
            current_agent=data.get("current_agent"),
            intent=data.get("intent"),
            trip_id=data.get("trip_id"),
            booking_id=data.get("booking_id"),
            payment_id=data.get("payment_id"),
            complaint_id=data.get("complaint_id"),
            refund_id=data.get("refund_id"),
            messages=data.get("messages", []),
            tool_results=data.get("tool_results", []),
            handoff_history=data.get("handoff_history", []),
            requires_human=data.get("requires_human", False),
            human_action=data.get("human_action"),
            final_status=data.get("final_status"),
        )
