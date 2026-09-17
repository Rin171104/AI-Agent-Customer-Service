"""
Agent State - Shared state management for multi-agent workflow
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class Intent(Enum):
    BOOKING = "booking"
    COMPLAINT = "complaint"
    PAYMENT = "payment"
    FAQ = "faq"
    GENERAL = "general"


class BookingStatus(Enum):
    DRAFT = "draft"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(Enum):
    UNPAID = "unpaid"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class ComplaintStatus(Enum):
    RECEIVED = "received"
    PENDING_REVIEW = "pending_review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    REJECTED = "rejected"


@dataclass
class AgentState:
    """
    Shared state for multi-agent workflow.

    Tracks:
    - User information
    - Current intent
    - Booking details
    - Payment information
    - Complaint information
    - Workflow progress
    - Human approval requirements
    """

    # Session info
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Intent tracking
    intent: Optional[str] = None
    intent_confidence: float = 0.0

    # Booking state
    booking_id: Optional[str] = None
    booking_status: str = BookingStatus.DRAFT.value
    trip_id: Optional[str] = None
    available_trips: List[Dict[str, Any]] = field(default_factory=list)
    seats: List[str] = field(default_factory=list)
    available_seats: List[Dict[str, Any]] = field(default_factory=list)
    hold_id: Optional[str] = None

    # Payment state
    payment_id: Optional[str] = None
    payment_status: str = PaymentStatus.UNPAID.value

    # Complaint state
    complaint_id: Optional[str] = None
    complaint_severity: Optional[str] = None
    complaint_status: str = ComplaintStatus.RECEIVED.value

    # Human approval
    requires_human_approval: bool = False
    human_approval_type: Optional[str] = None
    approval_status: Optional[str] = None  # pending, approved, rejected

    # Context data
    context: Dict[str, Any] = field(default_factory=dict)

    # Agent trace
    agent_trace: List[Dict[str, Any]] = field(default_factory=list)

    # Messages
    messages: List[Dict[str, str]] = field(default_factory=list)

    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new data."""
        self.context.update(updates)
        self.updated_at = datetime.utcnow()

    def add_trace(
        self,
        agent: str,
        action: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an entry to the agent trace."""
        self.agent_trace.append({
            "agent": agent,
            "action": action,
            "status": status,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.updated_at = datetime.utcnow()

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "intent": self.intent,
            "booking_id": self.booking_id,
            "booking_status": self.booking_status,
            "trip_id": self.trip_id,
            "payment_id": self.payment_id,
            "payment_status": self.payment_status,
            "complaint_id": self.complaint_id,
            "complaint_severity": self.complaint_severity,
            "requires_human_approval": self.requires_human_approval,
            "context": self.context,
            "agent_trace": self.agent_trace,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def reset_booking(self) -> None:
        """Reset booking-related state."""
        self.booking_id = None
        self.booking_status = BookingStatus.DRAFT.value
        self.trip_id = None
        self.available_trips = []
        self.seats = []
        self.available_seats = []
        self.hold_id = None

    def reset_payment(self) -> None:
        """Reset payment-related state."""
        self.payment_id = None
        self.payment_status = PaymentStatus.UNPAID.value

    def reset_complaint(self) -> None:
        """Reset complaint-related state."""
        self.complaint_id = None
        self.complaint_severity = None
        self.complaint_status = ComplaintStatus.RECEIVED.value

    def is_terminal_state(self) -> bool:
        """Check if the current state is a terminal state."""
        return (
            self.booking_status == BookingStatus.CONFIRMED.value
            or self.booking_status == BookingStatus.CANCELLED.value
            or self.complaint_status == ComplaintStatus.RESOLVED.value
            or self.complaint_status == ComplaintStatus.REJECTED.value
        )
