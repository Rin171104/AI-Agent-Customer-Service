"""
Payment Agent - Handles payment processing
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from src.agent.state import AgentState
from src.models.llm_client import LLMClient
from src.tools.payment_tools import PaymentTools


class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class PaymentAgent:
    """
    Payment Agent handles payment processing.

    Capabilities:
    - Create payment request
    - Send payment information to customer
    - Check transaction status
    - Confirm payment completion
    - Update booking status

    Note: Payment Agent is typically a downstream specialist,
    activated after customer confirms booking.
    """

    llm_client: LLMClient
    payment_tools: PaymentTools

    def __post_init__(self):
        self.name = "Payment Agent"

    async def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Process payment request based on current state.

        Args:
            state: Current workflow state

        Returns:
            Result dict with payment information
        """
        action = state.context.get("action", "create_payment")

        if action == "create_payment":
            return await self._create_payment(state)
        elif action == "check_payment":
            return await self._check_payment(state)
        elif action == "confirm_payment":
            return await self._confirm_payment(state)
        elif action == "refund":
            return await self._process_refund(state)

        return {"action": "unknown", "message": "Unknown payment action"}

    async def _create_payment(self, state: AgentState) -> Dict[str, Any]:
        """Create a new payment request."""
        booking_id = state.booking_id or state.context.get("booking_id")
        amount = state.context.get("total_amount") or state.context.get("amount")

        if not booking_id:
            return {
                "action": "create_payment",
                "status": "missing_info",
                "message": "No booking found. Please complete booking first.",
            }

        if not amount:
            return {
                "action": "create_payment",
                "status": "missing_info",
                "message": "Payment amount is missing.",
            }

        # Create payment request
        payment = await self.payment_tools.create_payment(
            booking_id=booking_id,
            amount=amount,
            customer_id=state.user_id,
        )

        state.payment_id = payment.get("payment_id")
        state.payment_status = "PENDING"

        # Generate payment instructions
        payment_info = self._generate_payment_info(payment)

        return {
            "action": "create_payment",
            "status": "pending",
            "payment_id": payment.get("payment_id"),
            "amount": amount,
            "payment_info": payment_info,
            "message": f"Payment request created. Amount: {amount:,} VND. {payment_info}",
        }

    async def _check_payment(self, state: AgentState) -> Dict[str, Any]:
        """Check payment status."""
        payment_id = state.payment_id or state.context.get("payment_id")

        if not payment_id:
            return {
                "action": "check_payment",
                "status": "missing_info",
                "message": "Please provide a payment ID.",
            }

        payment_status = await self.payment_tools.check_payment_status(payment_id)

        status = payment_status.get("status")
        state.payment_status = status

        if status == "paid":
            # Payment successful - trigger booking confirmation
            await self._confirm_booking_after_payment(state)

            return {
                "action": "check_payment",
                "status": "success",
                "payment_status": "PAID",
                "message": "Payment received. Your booking is now confirmed!",
            }

        return {
            "action": "check_payment",
            "status": "pending",
            "payment_status": status,
            "message": f"Payment status: {status}",
        }

    async def _confirm_payment(self, state: AgentState) -> Dict[str, Any]:
        """Confirm payment and update booking status."""
        payment_id = state.payment_id or state.context.get("payment_id")

        if not payment_id:
            return {
                "action": "confirm_payment",
                "status": "missing_info",
                "message": "Please provide a payment ID.",
            }

        # Confirm payment
        result = await self.payment_tools.confirm_payment(payment_id)

        if result.get("success"):
            state.payment_status = "PAID"
            # Confirm booking
            await self._confirm_booking_after_payment(state)

            return {
                "action": "confirm_payment",
                "status": "success",
                "message": "Payment confirmed. Booking is now confirmed!",
            }

        return {
            "action": "confirm_payment",
            "status": "failed",
            "message": result.get("message", "Payment confirmation failed."),
        }

    async def _confirm_booking_after_payment(self, state: AgentState) -> None:
        """Confirm booking after successful payment."""
        booking_id = state.booking_id
        if booking_id:
            from src.tools.booking_tools import BookingTools
            booking_tools = BookingTools()
            await booking_tools.update_booking_status(booking_id, "CONFIRMED")
            state.booking_status = "CONFIRMED"

    async def _process_refund(self, state: AgentState) -> Dict[str, Any]:
        """Process refund request (requires HITL)."""
        booking_id = state.booking_id or state.context.get("booking_id")
        amount = state.context.get("refund_amount")

        if not booking_id:
            return {
                "action": "refund",
                "status": "missing_info",
                "message": "Please provide a booking ID.",
            }

        # Refunds require human approval
        return {
            "action": "refund",
            "status": "requires_approval",
            "booking_id": booking_id,
            "requested_amount": amount,
            "requires_human_approval": True,
            "message": f"Refund request for {amount:,} VND requires CSKH approval.",
        }

    def _generate_payment_info(self, payment: Dict[str, Any]) -> str:
        """Generate payment instructions for customer."""
        payment_method = payment.get("payment_method", "bank_transfer")

        if payment_method == "bank_transfer":
            return (
                "Please transfer to:\n"
                f"  Account: {payment.get('account_number', 'XXX')}\n"
                f"  Bank: {payment.get('bank_name', 'XXX')}\n"
                f"  Content: {payment.get('transfer_content', 'XXX')}"
            )
        elif payment_method == "momo":
            return f"Pay via MoMo to: {payment.get('mom_number', 'XXX')}"

        return "Please complete payment using the provided instructions."
