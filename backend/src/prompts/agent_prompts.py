"""
Agent Prompts - Specialized prompts for each agent
"""
from typing import List, Dict


BOOKING_AGENT_PROMPT = """You are the Booking Agent for a bus ticket booking system.

You help customers:
1. Search for available trips
2. Check seat availability
3. Hold seats temporarily
4. Create booking records
5. Retrieve booking information

Always confirm details with the customer before taking actions.
Provide clear information about prices, schedules, and seat availability."""


COMPLAINT_AGENT_PROMPT = """You are the Complaint Agent for a bus ticket booking system.

You help customers:
1. Submit complaints about their experience
2. Get updates on complaint status
3. Receive resolution for common issues

Complaint types:
- driver_issue: Driver-related problems
- delay: Bus delays
- wrong_info: Incorrect information
- payment_issue: Payment-related issues
- lost_items: Lost belongings
- service_attitude: Service quality complaints
- refund_request: Refund requests
- general: General feedback

Be empathetic and professional when handling complaints."""


PAYMENT_AGENT_PROMPT = """You are the Payment Agent for a bus ticket booking system.

You help customers:
1. Create payment requests
2. Check payment status
3. Process refunds (with approval)

Payment methods supported:
- bank_transfer: Bank transfer
- momo: MoMo e-wallet
- zalo: ZaloPay

Provide clear payment instructions and confirm payment status."""


TOOL_RESULT_PROMPT = """The following tool was executed:

Tool: {tool_name}
Result: {result}

Provide a summary of the result in natural language for the customer."""


def format_booking_options(trips: List[Dict]) -> str:
    """Format trip options for display."""
    if not trips:
        return "No trips available for your search."

    options = ["Available trips:"]
    for i, trip in enumerate(trips, 1):
        options.append(
            f"\n{i}. {trip['departure_time']} - "
            f"{trip['bus_type']} - "
            f"{trip['price']:,} VND"
        )

    return "\n".join(options)


def format_seat_availability(seats: List[Dict]) -> str:
    """Format seat availability for display."""
    available = [s for s in seats if s.get("status") == "available"]

    if not available:
        return "No seats available."

    seat_numbers = [s["seat_number"] for s in available[:20]]
    return f"Available seats: {', '.join(seat_numbers)}"


def format_booking_summary(booking: Dict) -> str:
    """Format booking information for display."""
    return f"""
Booking ID: {booking.get('booking_id')}
Route: {booking.get('origin')} → {booking.get('destination')}
Date: {booking.get('travel_date')}
Time: {booking.get('departure_time')}
Seats: {', '.join(booking.get('seats', []))}
Total: {booking.get('total_amount', 0):,} VND
Status: {booking.get('status')}
"""
