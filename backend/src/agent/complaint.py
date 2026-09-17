"""
Complaint Agent - Handles customer complaints
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from src.agent.state import AgentState
from src.models.llm_client import LLMClient
from src.tools.complaint_tools import ComplaintTools


class ComplaintSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ComplaintAgent:
    """
    Complaint Agent handles customer complaints.

    Capabilities:
    - Receive and classify complaints
    - Retrieve related booking/customer information
    - Assess severity level
    - Recommend resolution
    - Escalate to CSKH when required
    """

    llm_client: LLMClient
    complaint_tools: ComplaintTools

    def __post_init__(self):
        self.name = "Complaint Agent"

    async def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Process complaint request based on current state.

        Args:
            state: Current workflow state

        Returns:
            Result dict with complaint information
        """
        action = state.context.get("action", "receive_complaint")

        if action == "receive_complaint":
            return await self._receive_complaint(state)
        elif action == "get_complaint":
            return await self._get_complaint(state)
        elif action == "update_complaint":
            return await self._update_complaint(state)

        return {"action": "unknown", "message": "Unknown complaint action"}

    async def _receive_complaint(self, state: AgentState) -> Dict[str, Any]:
        """Receive and process a new complaint."""
        complaint_text = state.context.get("complaint_text", "")
        booking_id = state.context.get("booking_id")

        if not complaint_text:
            return {
                "action": "receive_complaint",
                "status": "missing_info",
                "message": "Please describe your complaint.",
            }

        # Classify complaint
        classification = await self._classify_complaint(complaint_text)
        severity = classification.get("severity", "medium")
        complaint_type = classification.get("type", "general")

        # Retrieve booking info if booking_id provided
        booking_info = None
        if booking_id:
            booking_info = await self.complaint_tools.get_related_booking(booking_id)

        # Create complaint record
        complaint = await self.complaint_tools.create_complaint(
            booking_id=booking_id,
            complaint_type=complaint_type,
            description=complaint_text,
            severity=severity,
            customer_id=state.user_id,
            booking_info=booking_info,
        )

        state.complaint_id = complaint.get("complaint_id")
        state.complaint_severity = severity

        # Determine if human approval is needed
        requires_approval = severity in ["high", "medium"]

        # Generate response
        if requires_approval:
            return {
                "action": "receive_complaint",
                "status": "pending_review",
                "complaint_id": complaint.get("complaint_id"),
                "severity": severity,
                "requires_human_review": True,
                "message": f"Your complaint has been received and is being reviewed. "
                           f"Complaint ID: {complaint.get('complaint_id')}",
            }

        # Auto-resolve for low severity
        resolution = await self._generate_resolution(complaint, classification)

        return {
            "action": "receive_complaint",
            "status": "resolved",
            "complaint_id": complaint.get("complaint_id"),
            "severity": severity,
            "resolution": resolution,
            "requires_human_review": False,
            "message": resolution.get("message"),
        }

    async def _classify_complaint(self, complaint_text: str) -> Dict[str, Any]:
        """Classify complaint type and severity."""
        prompt = f"""
Classify this complaint:
"{complaint_text}"

Return JSON with:
- type: one of [driver_issue, delay, wrong_info, payment_issue, lost_items, service_attitude, refund_request, general]
- severity: one of [low, medium, high]
- keywords: list of relevant keywords
"""
        response = await self.llm_client.generate(prompt)

        # TODO: Parse response properly
        # For now, return basic classification
        if any(word in complaint_text.lower() for word in ["hoàn", "refund", "tiền"]):
            return {"type": "refund_request", "severity": "high"}
        elif any(word in complaint_text.lower() for word in ["bỏ", "không đón", "điểm"]):
            return {"type": "driver_issue", "severity": "medium"}
        elif any(word in complaint_text.lower() for word in ["trễ", "chậm", "delay"]):
            return {"type": "delay", "severity": "medium"}

        return {"type": "general", "severity": "low"}

    async def _generate_resolution(
        self,
        complaint: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate resolution for low-severity complaints."""
        complaint_type = classification.get("type")

        resolutions = {
            "general": {
                "action": "acknowledge",
                "message": "We apologize for the inconvenience. Your feedback has been noted and will be used to improve our service.",
            },
            "delay": {
                "action": "partial_refund",
                "message": "We apologize for the delay. A partial refund has been processed for affected passengers.",
            },
            "wrong_info": {
                "action": "correction",
                "message": "We apologize for the incorrect information. The correct details have been noted.",
            },
        }

        resolution = resolutions.get(complaint_type, resolutions["general"])

        # Update complaint with resolution
        await self.complaint_tools.update_complaint(
            complaint_id=complaint.get("complaint_id"),
            resolution=resolution,
            status="resolved",
        )

        return resolution

    async def _get_complaint(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve complaint information."""
        complaint_id = state.complaint_id or state.context.get("complaint_id")

        if not complaint_id:
            return {
                "action": "get_complaint",
                "status": "missing_info",
                "message": "Please provide a complaint ID.",
            }

        complaint = await self.complaint_tools.get_complaint(complaint_id)

        return {
            "action": "get_complaint",
            "status": "success",
            "complaint": complaint,
        }

    async def _update_complaint(self, state: AgentState) -> Dict[str, Any]:
        """Update complaint status or resolution."""
        complaint_id = state.complaint_id
        update_data = state.context.get("update_data", {})

        if not complaint_id:
            return {
                "action": "update_complaint",
                "status": "missing_info",
                "message": "Please provide a complaint ID.",
            }

        result = await self.complaint_tools.update_complaint(
            complaint_id=complaint_id,
            **update_data,
        )

        return {
            "action": "update_complaint",
            "status": "success",
            "message": "Complaint updated successfully.",
        }
