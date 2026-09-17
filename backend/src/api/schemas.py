"""
API Schemas - Pydantic models for request/response
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============ Chat ============

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent's response")
    intent: str = Field(..., description="Detected intent")
    requires_human_approval: bool = Field(False, description="Whether human approval is needed")
    agent_trace: List[Dict[str, Any]] = Field(default_factory=list, description="Agent execution trace")


# ============ Booking ============

class BookingRequest(BaseModel):
    trip_id: str
    seat_numbers: List[str]
    customer_name: str
    phone: str
    pickup_point: str
    customer_id: Optional[str] = None


class BookingResponse(BaseModel):
    booking_id: str
    status: str
    message: str
    total_amount: Optional[int] = None


# ============ Payment ============

class PaymentRequest(BaseModel):
    booking_id: str
    amount: int
    payment_method: str = "bank_transfer"


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    message: str
    payment_info: Optional[Dict[str, Any]] = None


# ============ Complaint ============

class ComplaintRequest(BaseModel):
    booking_id: Optional[str] = None
    complaint_type: str
    description: str
    severity: str = "medium"
    customer_id: Optional[str] = None


class ComplaintResponse(BaseModel):
    complaint_id: str
    status: str
    message: str
    severity: Optional[str] = None
    requires_human_review: bool = False


# ============ Approval ============

class ApprovalRequest(BaseModel):
    action: str = Field(..., description="Action to approve/reject")
    approved: bool = Field(..., description="Whether to approve")
    notes: Optional[str] = Field(None, description="Approval notes")


class ApprovalResponse(BaseModel):
    approval_id: str
    status: str
    message: str


# ============ Trip ============

class TripSearch(BaseModel):
    origin: str
    destination: str
    date: str
    time: Optional[str] = None


class TripResponse(BaseModel):
    trip_id: str
    origin: str
    destination: str
    date: str
    departure_time: str
    arrival_time: str
    bus_type: str
    price: int
    available_seats: int


# ============ Agent Run ============

class AgentStep(BaseModel):
    agent: str
    action: str
    status: str
    timestamp: datetime


class AgentRun(BaseModel):
    run_id: str
    user_id: Optional[str]
    intent: str
    status: str
    steps: List[AgentStep]
    created_at: datetime
    updated_at: datetime
