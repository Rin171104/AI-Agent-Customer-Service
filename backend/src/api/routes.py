"""
API Routes - FastAPI endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.agent.executor import get_executor, AgentExecutor
from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    BookingRequest,
    BookingResponse,
    PaymentRequest,
    PaymentResponse,
    ComplaintRequest,
    ComplaintResponse,
    ApprovalRequest,
    ApprovalResponse,
)


router = APIRouter()


# Dependencies
def get_agent_executor() -> AgentExecutor:
    """Get agent executor instance."""
    return get_executor()


# ============ Chat Endpoint ============

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    executor: AgentExecutor = Depends(get_agent_executor)
):
    """Send a chat message and receive agent response."""
    try:
        result = await executor.execute(
            message=request.message,
            user_id=request.user_id,
        )

        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            requires_human_approval=result.get("requires_human_approval", False),
            agent_trace=result.get("agent_trace", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Booking Endpoints ============

@router.get("/bookings")
async def list_bookings(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
):
    """List bookings with optional filters."""
    # TODO: Implement actual database query
    return {"bookings": [], "total": 0}


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(request: BookingRequest):
    """Create a new booking."""
    # TODO: Implement actual booking creation
    return BookingResponse(
        booking_id="BK-TEMP123",
        status="DRAFT",
        message="Booking created successfully",
    )


@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Get booking details."""
    # TODO: Implement actual database query
    return {
        "booking_id": booking_id,
        "status": "DRAFT",
    }


@router.put("/bookings/{booking_id}")
async def update_booking(booking_id: str, request: BookingRequest):
    """Update booking."""
    # TODO: Implement actual update
    return {"booking_id": booking_id, "status": "DRAFT"}


# ============ Trip Endpoints ============

@router.get("/trips")
async def search_trips(
    origin: str,
    destination: str,
    date: str,
    time: Optional[str] = None,
):
    """Search available trips."""
    # TODO: Implement actual trip search
    return {"trips": [], "total": 0}


@router.get("/trips/{trip_id}/seats")
async def get_trip_seats(trip_id: str):
    """Get seat availability for a trip."""
    # TODO: Implement actual seat query
    return {"trip_id": trip_id, "seats": []}


# ============ Payment Endpoints ============

@router.post("/payments", response_model=PaymentResponse)
async def create_payment(request: PaymentRequest):
    """Create a payment request."""
    # TODO: Implement actual payment creation
    return PaymentResponse(
        payment_id="PAY-TEMP123",
        status="PENDING",
        message="Payment request created",
    )


@router.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    """Get payment details."""
    # TODO: Implement actual query
    return {"payment_id": payment_id, "status": "PENDING"}


@router.post("/payments/{payment_id}/confirm")
async def confirm_payment(payment_id: str):
    """Confirm payment."""
    # TODO: Implement actual confirmation
    return {"payment_id": payment_id, "status": "PAID"}


# ============ Complaint Endpoints ============

@router.get("/complaints")
async def list_complaints(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
):
    """List complaints with optional filters."""
    # TODO: Implement actual database query
    return {"complaints": [], "total": 0}


@router.post("/complaints", response_model=ComplaintResponse)
async def create_complaint(request: ComplaintRequest):
    """Create a new complaint."""
    # TODO: Implement actual complaint creation
    return ComplaintResponse(
        complaint_id="CMPL-TEMP123",
        status="RECEIVED",
        message="Complaint submitted successfully",
    )


@router.get("/complaints/{complaint_id}")
async def get_complaint(complaint_id: str):
    """Get complaint details."""
    # TODO: Implement actual query
    return {"complaint_id": complaint_id, "status": "RECEIVED"}


@router.put("/complaints/{complaint_id}")
async def update_complaint(complaint_id: str, request: ComplaintRequest):
    """Update complaint."""
    # TODO: Implement actual update
    return {"complaint_id": complaint_id, "status": "RECEIVED"}


# ============ Admin / HITL Endpoints ============

@router.get("/admin/pending-approvals")
async def list_pending_approvals(limit: int = 10):
    """List pending human approvals."""
    # TODO: Implement actual query
    return {"approvals": [], "total": 0}


@router.post("/admin/approvals/{approval_id}", response_model=ApprovalResponse)
async def process_approval(
    approval_id: str,
    request: ApprovalRequest,
):
    """Process a human approval."""
    # TODO: Implement actual approval processing
    return ApprovalResponse(
        approval_id=approval_id,
        status="APPROVED",
        message="Approval processed successfully",
    )


# ============ Agent Run Endpoints ============

@router.get("/runs/{run_id}")
async def get_agent_run(run_id: str):
    """Get agent run details."""
    # TODO: Implement actual run retrieval
    return {"run_id": run_id}


@router.get("/runs")
async def list_agent_runs(
    user_id: Optional[str] = None,
    limit: int = 10,
):
    """List recent agent runs."""
    # TODO: Implement actual run listing
    return {"runs": [], "total": 0}
