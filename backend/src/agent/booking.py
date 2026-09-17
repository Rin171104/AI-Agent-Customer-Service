"""
Booking Agent - Handles ticket booking operations
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.agent.state import AgentState
from src.models.llm_client import LLMClient
from src.prompts.agent_prompts import BOOKING_AGENT_PROMPT
from src.tools.booking_tools import BookingTools


@dataclass
class BookingAgent:
    """
    Booking Agent handles ticket booking operations.

    Capabilities:
    - Search available trips by route and date
    - Check seat availability
    - Hold seats temporarily
    - Collect passenger information
    - Create booking draft
    - Retrieve booking status
    """

    llm_client: LLMClient
    booking_tools: BookingTools

    def __post_init__(self):
        self.name = "Booking Agent"

    async def process(self, state: AgentState) -> Dict[str, Any]:
        """
        Process booking request based on current state.

        Args:
            state: Current workflow state

        Returns:
            Result dict with booking information
        """
        action = state.context.get("action", "search_trips")

        if action == "search_trips":
            return await self._search_trips(state)
        elif action == "check_seats":
            return await self._check_seats(state)
        elif action == "hold_seats":
            return await self._hold_seats(state)
        elif action == "create_booking":
            return await self._create_booking(state)
        elif action == "get_booking":
            return await self._get_booking(state)
        elif action == "cancel_booking":
            return await self._cancel_booking(state)

        return {"action": "unknown", "message": "Unknown booking action"}

    async def _search_trips(self, state: AgentState) -> Dict[str, Any]:
        """Search available trips based on route and date."""
        origin = state.context.get("origin")
        destination = state.context.get("destination")
        date = state.context.get("travel_date")

        if not all([origin, destination, date]):
            return {
                "action": "search_trips",
                "status": "missing_info",
                "message": "Please provide origin, destination, and travel date.",
            }

        # Call booking tool
        trips = await self.booking_tools.search_trip(
            origin=origin,
            destination=destination,
            date=date,
        )

        if not trips:
            return {
                "action": "search_trips",
                "status": "no_trips",
                "message": f"No trips available from {origin} to {destination} on {date}.",
            }

        # Format trip options
        trip_options = self._format_trip_options(trips)

        state.trip_id = trips[0].get("trip_id")
        state.available_trips = trips

        return {
            "action": "search_trips",
            "status": "success",
            "trips": trips,
            "message": f"Found {len(trips)} trips. {trip_options}",
        }

    async def _check_seats(self, state: AgentState) -> Dict[str, Any]:
        """Check seat availability for a specific trip."""
        trip_id = state.trip_id or state.context.get("trip_id")

        if not trip_id:
            return {
                "action": "check_seats",
                "status": "missing_info",
                "message": "Please select a trip first.",
            }

        seats = await self.booking_tools.check_seat(trip_id)
        available_seats = [s for s in seats if s.get("status") == "available"]

        state.available_seats = available_seats

        return {
            "action": "check_seats",
            "status": "success",
            "seats": available_seats,
            "message": f"Available seats: {', '.join([s['seat_number'] for s in available_seats])}",
        }

    async def _hold_seats(self, state: AgentState) -> Dict[str, Any]:
        """Hold selected seats temporarily."""
        trip_id = state.trip_id
        seat_numbers = state.context.get("seats", [])

        if not trip_id or not seat_numbers:
            return {
                "action": "hold_seats",
                "status": "missing_info",
                "message": "Please select seats first.",
            }

        result = await self.booking_tools.hold_seat(
            trip_id=trip_id,
            seat_numbers=seat_numbers,
            customer_id=state.user_id,
        )

        if result.get("success"):
            state.hold_id = result.get("hold_id")
            return {
                "action": "hold_seats",
                "status": "success",
                "hold_id": result.get("hold_id"),
                "message": f"Seats {', '.join(seat_numbers)} are now held for you.",
            }

        return {
            "action": "hold_seats",
            "status": "failed",
            "message": result.get("message", "Failed to hold seats."),
        }

    async def _create_booking(self, state: AgentState) -> Dict[str, Any]:
        """Create booking draft."""
        required_fields = ["customer_name", "phone", "pickup_point"]

        # Check if all required fields are present
        missing = [f for f in required_fields if not state.context.get(f)]
        if missing:
            return {
                "action": "create_booking",
                "status": "missing_info",
                "missing_fields": missing,
                "message": f"Please provide: {', '.join(missing)}",
            }

        booking = await self.booking_tools.create_booking(
            trip_id=state.trip_id,
            seat_numbers=state.context.get("seats", []),
            customer_name=state.context.get("customer_name"),
            phone=state.context.get("phone"),
            pickup_point=state.context.get("pickup_point"),
            customer_id=state.user_id,
        )

        state.booking_id = booking.get("booking_id")
        state.booking_status = "DRAFT"

        return {
            "action": "create_booking",
            "status": "success",
            "booking_id": booking.get("booking_id"),
            "total_amount": booking.get("total_amount"),
            "message": f"Booking created: {booking.get('booking_id')}. Total: {booking.get('total_amount')} VND",
        }

    async def _get_booking(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve booking information."""
        booking_id = state.booking_id or state.context.get("booking_id")

        if not booking_id:
            return {
                "action": "get_booking",
                "status": "missing_info",
                "message": "Please provide a booking ID.",
            }

        booking = await self.booking_tools.get_booking(booking_id)

        return {
            "action": "get_booking",
            "status": "success",
            "booking": booking,
        }

    async def _cancel_booking(self, state: AgentState) -> Dict[str, Any]:
        """Cancel a booking."""
        booking_id = state.booking_id or state.context.get("booking_id")

        if not booking_id:
            return {
                "action": "cancel_booking",
                "status": "missing_info",
                "message": "Please provide a booking ID.",
            }

        result = await self.booking_tools.cancel_booking(booking_id)

        return {
            "action": "cancel_booking",
            "status": "success" if result.get("success") else "failed",
            "message": result.get("message", ""),
        }

    def _format_trip_options(self, trips: List[Dict]) -> str:
        """Format trip options for display."""
        options = []
        for i, trip in enumerate(trips[:5], 1):
            options.append(
                f"{i}. {trip.get('departure_time')} - "
                f"{trip.get('bus_type')} - "
                f"{trip.get('price')} VND"
            )
        return "\n".join(options)
