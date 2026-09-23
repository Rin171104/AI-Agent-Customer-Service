"""
Booking & Payment Agent

Xử lý các nghiệp vụ:
    - Tìm chuyến xe
    - Xem thông tin chuyến
    - Kiểm tra ghế
    - Đặt vé
    - Xem booking
    - Hủy booking
    - Tạo payment
    - Kiểm tra trạng thái payment

Kiến trúc:
    Customer -> BookingAgent -> Tools -> Services -> Database
"""
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.ai.tools.trip_tools import TripTools
from src.ai.tools.booking_tools import BookingTools
from src.ai.tools.payment_tools import PaymentTools
from src.utils.logger import logger


@dataclass
class BookingState:
    """State cho Booking Agent"""
    user_id: str
    session_id: str = ""
    intent: Optional[str] = None
    trip_id: Optional[str] = None
    booking_id: Optional[str] = None
    payment_id: Optional[str] = None
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


class BookingAgent:
    """
    Booking & Payment Agent

    Agent này xử lý các yêu cầu liên quan đến:
    - Tìm và đặt chuyến xe
    - Quản lý booking
    - Thanh toán
    """

    # Intent patterns - từ khóa để nhận diện ý định
    INTENT_PATTERNS = {
        "search_trip": [
            r"tìm.*chuyến",
            r"tìm.*xe",
            r"xe.*đi",
            r"có.*xe.*nào",
            r"lịch.*xe",
            r"chuyến.*nào",
            r"đi.*từ.*đến",
            r"(hà nội|hcm|sài gòn|đà lạt|tà xùa).*(hà nội|hcm|sài gòn|đà lạt|tà xùa)",
        ],
        "get_trip_info": [
            r"thông tin.*chuyến",
            r"chi tiết.*chuyến",
            r"xem.*chuyến",
            r"trip.*(id|info|detail)",
        ],
        "check_seats": [
            r"còn.*ghế",
            r"ghế.*trống",
            r"có.*ghế.*không",
            r"check.*seat",
        ],
        "create_booking": [
            r"đặt.*vé",
            r"đặt.*chỗ",
            r"book.*ticket",
            r"mua.*vé",
            r"giữ.*vé",
            r"tôi.*muốn.*đi",
            r"cho.*tôi.*đặt",
        ],
        "get_booking": [
            r"xem.*booking",
            r"xem.*vé",
            r"vé.*của.*tôi",
            r"booking.*của.*tôi",
            r"mã.*booking",
            r"tra.*cứu.*vé",
        ],
        "cancel_booking": [
            r"hủy.*vé",
            r"hủy.*booking",
            r"xóa.*đặt",
            r"không.*đi.*nữa",
            r"hủy.*chuyến",
        ],
        "create_payment": [
            r"thanh.*toán",
            r"pay",
            r"payment",
            r"chuyển.*khoản",
            r"nạp.*tiền",
        ],
        "check_payment": [
            r"trạng thái.*thanh.*toán",
            r"thanh.*toán.*chưa",
            r"đã.*thanh.*toán.*chưa",
            r"payment.*status",
        ],
        "get_my_bookings": [
            r"danh.*sách.*vé",
            r"lịch.*sử.*đặt",
            r"tất.*cả.*booking",
            r"các.*vé.*đã.*đặt",
        ],
    }

    def __init__(self):
        self.trip_tools = TripTools()
        self.booking_tools = BookingTools()
        self.payment_tools = PaymentTools()
        self.logger = logger

    def detect_intent(self, message: str) -> str:
        """
        Nhận diện intent từ message của customer.

        Args:
            message: Tin nhắn từ customer

        Returns:
            Intent string
        """
        message_lower = message.lower()

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    self.logger.info(f"Detected intent: {intent}")
                    return intent

        # Default intent
        return "unknown"

    def extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Trích xuất entities từ message.

        Args:
            message: Tin nhắn từ customer

        Returns:
            Dict chứa các entities
        """
        entities = {
            "origin": None,
            "destination": None,
            "date": None,
            "time": None,
            "seat_count": None,
            "trip_id": None,
            "booking_id": None,
            "booking_code": None,
        }

        message_lower = message.lower()

        # Location patterns
        locations = ["hà nội", "hồ chí minh", "hcm", "sài gòn", "đà nẵng", "đà lạt", "tà xùa", "nha trang", "phan thiết", "vũng tàu"]
        for loc in locations:
            if f"đi {loc}" in message_lower or f"tới {loc}" in message_lower or f"đến {loc}" in message_lower:
                entities["destination"] = loc.title().replace("Hcm", "HCM").replace("Hà Nội", "Hà Nội")
            if f"từ {loc}" in message_lower or f"xuất phát {loc}" in message_lower:
                entities["origin"] = loc.title().replace("Hcm", "HCM").replace("Hà Nội", "Hà Nội")

        # Time patterns
        time_patterns = [
            (r"(\d{1,2})h(\d{0,2})", r"\1:\2"),
            (r"(sáng|chiều|tối|trưa)", r"\1"),
        ]
        for pattern, _ in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                entities["time"] = match.group(0)
                break

        # Seat count
        seat_match = re.search(r"(\d+)\s*(vé|ghế|chỗ)", message_lower)
        if seat_match:
            entities["seat_count"] = int(seat_match.group(1))

        # Trip ID
        trip_match = re.search(r"trip[_\s-]?id[:\s]*([a-z0-9-]+)", message_lower)
        if trip_match:
            entities["trip_id"] = trip_match.group(1)

        # Booking ID/Code
        booking_match = re.search(r"(booking[_\s-]?id|mã[:\s]*)([a-z0-9-]+)", message_lower)
        if booking_match:
            entities["booking_code"] = booking_match.group(2).upper()

        # Date
        date_patterns = [
            (r"ngày\s*(\d{1,2})/(\d{1,2})", r"\1/\2"),
            (r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1"),
            (r"ngày\s*mai", "Ngày mai"),
            (r"ngày\s*kia", "Ngày kia"),
        ]

        return entities

    async def process(
        self,
        db: Any,
        user_id: str,
        message: str,
        state: Optional[BookingState] = None
    ) -> Dict[str, Any]:
        """
        Xử lý message từ customer.

        Args:
            db: Database session
            user_id: ID của user
            message: Message từ customer
            state: State hiện tại (nếu có)

        Returns:
            Dict với response và updated state
        """
        # Initialize or use existing state
        if state is None:
            state = BookingState(user_id=user_id, session_id=str(datetime.utcnow().timestamp()))

        state.add_message("customer", message)

        # Detect intent
        intent = self.detect_intent(message)
        state.intent = intent

        # Extract entities
        entities = self.extract_entities(message)
        state.context.update(entities)

        self.logger.info(f"Processing intent: {intent}, entities: {entities}")

        # Route to handler
        try:
            if intent == "search_trip":
                result = await self._handle_search_trip(db, state, entities)
            elif intent == "get_trip_info":
                result = await self._handle_get_trip_info(db, state, entities)
            elif intent == "check_seats":
                result = await self._handle_check_seats(db, state, entities)
            elif intent == "create_booking":
                result = await self._handle_create_booking(db, state, entities)
            elif intent == "get_booking":
                result = await self._handle_get_booking(db, state, entities)
            elif intent == "cancel_booking":
                result = await self._handle_cancel_booking(db, state, entities)
            elif intent == "create_payment":
                result = await self._handle_create_payment(db, state, entities)
            elif intent == "check_payment":
                result = await self._handle_check_payment(db, state, entities)
            elif intent == "get_my_bookings":
                result = await self._handle_get_my_bookings(db, state)
            else:
                result = await self._handle_unknown(db, state, message)

        except Exception as e:
            self.logger.error(f"Error processing intent {intent}: {e}")
            result = {
                "success": False,
                "response": "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.",
                "error": str(e)
            }

        # Add tool result to state
        if "tool_result" in result:
            state.add_tool_result(intent, result["tool_result"])

        # Add response to state
        state.add_message("agent", result.get("response", ""))

        return {
            "response": result.get("response", ""),
            "success": result.get("success", False),
            "state": state,
            "data": result.get("data"),
            "next_action": result.get("next_action"),
        }

    async def _handle_search_trip(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý tìm kiếm chuyến xe"""
        origin = entities.get("origin")
        destination = entities.get("destination")

        if not origin and not destination:
            return {
                "success": True,
                "response": "Bạn muốn tìm chuyến xe đi đâu? Vui lòng cho tôi biết điểm đi và điểm đến.",
                "next_action": "ask_location"
            }

        result = await self.trip_tools.search_trips(
            db=db,
            origin=origin,
            destination=destination
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm được chuyến xe: {result.get('error', 'Lỗi không xác định')}",
                "tool_result": result
            }

        trips = result.get("trips", [])

        if not trips:
            return {
                "success": True,
                "response": f"Không có chuyến xe nào từ {origin or 'điểm đi'} đến {destination or 'điểm đến'}.",
                "data": {"trips": []},
                "tool_result": result
            }

        # Format response
        trip_list = []
        for trip in trips:
            trip_info = f"- {trip['route']}: {trip['origin']} → {trip['destination']}"
            trip_info += f"\n  Giờ: {trip['departure_time']} - {trip['arrival_time']}"
            trip_info += f"\n  Giá: {trip['price']:,} VND/ghế | Còn {trip['available_seats']} ghế"
            trip_list.append(trip_info)

        response = f"Tìm thấy {len(trips)} chuyến xe:\n\n" + "\n\n".join(trip_list)
        response += "\n\nBạn muốn đặt chuyến nào?"

        # Save first trip for quick booking
        if trips:
            state.context["available_trips"] = trips

        return {
            "success": True,
            "response": response,
            "data": {"trips": trips},
            "tool_result": result
        }

    async def _handle_get_trip_info(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý lấy thông tin chuyến xe"""
        trip_id = entities.get("trip_id") or state.trip_id

        if not trip_id:
            # Try to use from available trips in context
            available_trips = state.context.get("available_trips", [])
            if available_trips and len(available_trips) == 1:
                trip_id = available_trips[0]["id"]
            else:
                return {
                    "success": True,
                    "response": "Bạn muốn xem thông tin chuyến nào? Vui lòng cho tôi biết trip ID.",
                    "next_action": "ask_trip_id"
                }

        result = await self.trip_tools.get_trip(db=db, trip_id=trip_id)

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm được thông tin chuyến xe: {result.get('error', 'Lỗi không xác định')}",
                "tool_result": result
            }

        trip = result.get("trip", {})

        response = f"Thông tin chuyến xe:\n"
        response += f"- Tuyến: {trip['route']}\n"
        response += f"- Lộ trình: {trip['origin']} → {trip['destination']}\n"
        response += f"- Giờ khởi hành: {trip['departure_time']}\n"
        response += f"- Giờ đến: {trip['arrival_time']}\n"
        response += f"- Giá: {trip['price']:,} VND/ghế\n"
        response += f"- Ghế trống: {trip['available_seats']}/{trip['total_seats']}\n"
        response += f"- Trạng thái: {trip['status']}"

        state.trip_id = trip_id

        return {
            "success": True,
            "response": response,
            "data": {"trip": trip},
            "tool_result": result
        }

    async def _handle_check_seats(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý kiểm tra ghế trống"""
        trip_id = entities.get("trip_id") or state.trip_id
        seat_count = entities.get("seat_count") or 1

        if not trip_id:
            # Try to use from context
            available_trips = state.context.get("available_trips", [])
            if available_trips:
                # Ask which trip
                trip_options = "\n".join([f"{i+1}. {t['route']} ({t['departure_time']})" for i, t in enumerate(available_trips)])
                return {
                    "success": True,
                    "response": f"Bạn muốn kiểm tra ghế cho chuyến nào?\n{trip_options}",
                    "next_action": "select_trip"
                }
            return {
                "success": True,
                "response": "Bạn muốn kiểm tra ghế của chuyến nào? Vui lòng cho tôi biết trip ID.",
                "next_action": "ask_trip_id"
            }

        result = await self.trip_tools.check_available_seats(
            db=db,
            trip_id=trip_id,
            seat_count=seat_count
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không kiểm tra được ghế: {result.get('error', 'Lỗi không xác định')}",
                "tool_result": result
            }

        available = result.get("available_seats", 0)
        requested = result.get("requested_seats", seat_count)
        can_book = result.get("can_book", False)

        response = f"Chuyến xe có {available} ghế trống.\n"
        if requested > 1:
            response += f"Bạn yêu cầu {requested} ghế: "
            if can_book:
                response += "✓ Còn đủ ghế"
            else:
                response += "✗ Không đủ ghế"

        if can_book and requested == 1:
            response += "\nSẵn sàng để đặt vé!"

        return {
            "success": True,
            "response": response,
            "data": result,
            "tool_result": result
        }

    async def _handle_create_booking(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý tạo booking - multi-step"""
        trip_id = entities.get("trip_id") or state.trip_id
        seat_count = entities.get("seat_count") or 1

        # Step 1: Xác định trip
        if not trip_id:
            available_trips = state.context.get("available_trips", [])
            if available_trips:
                # Auto select if only one trip
                if len(available_trips) == 1:
                    trip_id = available_trips[0]["id"]
                else:
                    # Ask customer to specify
                    trip_options = "\n".join([
                        f"{i+1}. {t['route']} - {t['departure_time']} - Còn {t['available_seats']} ghế"
                        for i, t in enumerate(available_trips)
                    ])
                    return {
                        "success": True,
                        "response": f"Bạn muốn đặt chuyến nào?\n{trip_options}",
                        "next_action": "select_trip"
                    }
            else:
                return {
                    "success": True,
                    "response": "Bạn muốn đặt chuyến nào? Vui lòng tìm chuyến trước hoặc cung cấp trip ID.",
                    "next_action": "ask_trip"
                }

        # Step 2: Kiểm tra ghế
        seat_result = await self.trip_tools.check_available_seats(
            db=db,
            trip_id=trip_id,
            seat_count=seat_count
        )

        if not seat_result.get("success"):
            return {
                "success": False,
                "response": f"Không kiểm tra được ghế: {seat_result.get('error')}",
                "tool_result": seat_result
            }

        if not seat_result.get("can_book"):
            available = seat_result.get("available_seats", 0)
            return {
                "success": False,
                "response": f"Rất tiếc, chuyến này chỉ còn {available} ghế. Bạn có muốn đặt {available} ghế không?",
                "next_action": "adjust_seats"
            }

        # Step 3: Tạo booking
        booking_result = await self.booking_tools.create_booking(
            db=db,
            user_id=state.user_id,
            trip_id=trip_id,
            seat_count=seat_count
        )

        if not booking_result.get("success"):
            return {
                "success": False,
                "response": f"Không tạo được booking: {booking_result.get('error')}",
                "tool_result": booking_result
            }

        # Success
        booking = booking_result.get("booking", {})
        trip_info = booking_result.get("trip_info", {})

        state.booking_id = booking.get("id")
        state.context["last_booking"] = booking

        response = f"✓ Đặt vé thành công!\n\n"
        response += f"- Mã booking: {booking.get('booking_code')}\n"
        response += f"- Tuyến: {trip_info.get('origin')} → {trip_info.get('destination')}\n"
        response += f"- Giờ khởi hành: {trip_info.get('departure_time')}\n"
        response += f"- Số ghế: {booking.get('seat_count')}\n"
        response += f"- Tổng tiền: {booking.get('total_amount'):,} VND\n"
        response += f"- Trạng thái: Chờ thanh toán\n\n"
        response += "Bạn có muốn thanh toán ngay không?"

        return {
            "success": True,
            "response": response,
            "data": {
                "booking": booking,
                "trip_info": trip_info
            },
            "tool_result": booking_result,
            "next_action": "payment"
        }

    async def _handle_get_booking(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý xem thông tin booking"""
        booking_id = entities.get("booking_id")
        booking_code = entities.get("booking_code")

        # Use last booking if available
        if not booking_id and not booking_code:
            last_booking = state.context.get("last_booking")
            if last_booking:
                booking_id = last_booking.get("id")
            elif state.booking_id:
                booking_id = state.booking_id

        if not booking_id and not booking_code:
            return {
                "success": True,
                "response": "Bạn muốn xem booking nào? Vui lòng cung cấp mã booking (BKxxxxxx) hoặc tôi có thể hiển thị danh sách vé của bạn.",
                "next_action": "ask_booking"
            }

        result = await self.booking_tools.get_booking(
            db=db,
            booking_id=booking_id,
            booking_code=booking_code
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm được booking: {result.get('error')}",
                "tool_result": result
            }

        booking = result.get("booking", {})

        response = f"Thông tin booking:\n"
        response += f"- Mã: {booking.get('booking_code')}\n"
        response += f"- Số ghế: {booking.get('seat_count')}\n"
        response += f"- Tổng tiền: {booking.get('total_amount'):,} VND\n"
        response += f"- Trạng thái: {self._format_booking_status(booking.get('status'))}\n"

        if booking.get("trip"):
            trip = booking["trip"]
            response += f"- Tuyến: {trip.get('origin')} → {trip.get('destination')}\n"
            response += f"- Giờ: {trip.get('departure_time')}\n"

        if booking.get("payment"):
            payment = booking["payment"]
            response += f"\nThanh toán:\n"
            response += f"- Số tiền: {payment.get('amount'):,} VND\n"
            response += f"- Phương thức: {payment.get('method')}\n"
            response += f"- Trạng thái: {self._format_payment_status(payment.get('status'))}"

        state.booking_id = booking.get("id")

        return {
            "success": True,
            "response": response,
            "data": {"booking": booking},
            "tool_result": result
        }

    async def _handle_cancel_booking(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý hủy booking"""
        booking_id = entities.get("booking_id")
        booking_code = entities.get("booking_code")

        # Use last booking if available
        if not booking_id and not booking_code:
            last_booking = state.context.get("last_booking")
            if last_booking:
                booking_id = last_booking.get("id")
            elif state.booking_id:
                booking_id = state.booking_id

        if not booking_id and not booking_code:
            return {
                "success": True,
                "response": "Bạn muốn hủy booking nào? Vui lòng cung cấp mã booking (BKxxxxxx).",
                "next_action": "ask_booking"
            }

        # Verify booking belongs to user first
        verify_result = await self.booking_tools.get_booking(
            db=db,
            booking_id=booking_id,
            booking_code=booking_code
        )

        if not verify_result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm được booking: {verify_result.get('error')}",
                "tool_result": verify_result
            }

        booking = verify_result.get("booking", {})

        # Check if already cancelled
        if booking.get("status") == "CANCELLED":
            return {
                "success": True,
                "response": f"Booking {booking.get('booking_code')} đã được hủy trước đó.",
                "data": {"booking": booking}
            }

        # Check if already confirmed (and paid)
        if booking.get("status") == "CONFIRMED":
            if booking.get("payment", {}).get("status") == "PAID":
                return {
                    "success": True,
                    "response": "Vé đã được thanh toán. Để hủy vé đã thanh toán, bạn cần liên hệ trực tiếp với nhà xe để được hỗ trợ hoàn tiền.",
                    "data": {"booking": booking}
                }

        # Proceed with cancellation
        result = await self.booking_tools.cancel_booking(
            db=db,
            booking_id=booking_id or booking_code,
            user_id=state.user_id
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không hủy được booking: {result.get('error')}",
                "tool_result": result
            }

        cancelled = result.get("booking", {})

        response = f"✓ Hủy booking thành công!\n"
        response += f"- Mã booking: {cancelled.get('booking_code')}\n"
        response += f"- Trạng thái: Đã hủy\n\n"
        response += "Các ghế đã được giải phóng và có thể đặt cho khách khác."

        return {
            "success": True,
            "response": response,
            "data": {"booking": cancelled},
            "tool_result": result
        }

    async def _handle_create_payment(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý tạo payment"""
        booking_id = entities.get("booking_id")

        # Use last booking if available
        if not booking_id:
            last_booking = state.context.get("last_booking")
            if last_booking:
                booking_id = last_booking.get("id")
            elif state.booking_id:
                booking_id = state.booking_id

        if not booking_id:
            return {
                "success": True,
                "response": "Bạn muốn thanh toán booking nào? Vui lòng cung cấp mã booking (BKxxxxxx) hoặc tôi sẽ hiển thị các booking của bạn.",
                "next_action": "ask_booking"
            }

        # Get booking first to verify
        booking_result = await self.booking_tools.get_booking(db=db, booking_id=booking_id)

        if not booking_result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm được booking: {booking_result.get('error')}",
                "tool_result": booking_result
            }

        booking = booking_result.get("booking", {})

        # Check if already paid
        if booking.get("payment", {}).get("status") == "PAID":
            return {
                "success": True,
                "response": f"Booking {booking.get('booking_code')} đã được thanh toán trước đó.",
                "data": {"booking": booking}
            }

        # Check if cancelled
        if booking.get("status") == "CANCELLED":
            return {
                "success": True,
                "response": f"Booking {booking.get('booking_code')} đã bị hủy, không thể thanh toán.",
                "data": {"booking": booking}
            }

        # Create payment
        result = await self.payment_tools.create_payment(
            db=db,
            booking_id=booking_id,
            actor_id=state.user_id,
            actor_type="CUSTOMER"
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tạo được payment: {result.get('error')}",
                "tool_result": result
            }

        payment = result.get("payment", {})
        payment_message = result.get("message", "")

        state.payment_id = payment.get("id")

        response = f"Thông tin thanh toán:\n"
        response += f"- Mã booking: {booking.get('booking_code')}\n"
        response += f"- Số tiền: {payment.get('amount'):,} VND\n"
        response += f"- Phương thức: {payment.get('method')}\n"
        response += f"- Trạng thái: Chờ thanh toán\n\n"
        response += "Vui lòng thanh toán và thông báo cho tôi khi hoàn tất để tôi xác nhận."

        return {
            "success": True,
            "response": response,
            "data": {
                "payment": payment,
                "booking": booking
            },
            "tool_result": result,
            "next_action": "confirm_payment"
        }

    async def _handle_check_payment(
        self,
        db: Any,
        state: BookingState,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xử lý kiểm tra trạng thái payment"""
        booking_id = entities.get("booking_id")

        # Use last booking if available
        if not booking_id:
            last_booking = state.context.get("last_booking")
            if last_booking:
                booking_id = last_booking.get("id")
            elif state.booking_id:
                booking_id = state.booking_id

        if not booking_id:
            return {
                "success": True,
                "response": "Bạn muốn kiểm tra thanh toán của booking nào?",
                "next_action": "ask_booking"
            }

        result = await self.payment_tools.get_payment(db=db, booking_id=booking_id)

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không tìm được thông tin: {result.get('error')}",
                "tool_result": result
            }

        payment = result.get("payment", {})

        response = f"Trạng thái thanh toán:\n"
        response += f"- Số tiền: {payment.get('amount'):,} VND\n"
        response += f"- Phương thức: {payment.get('method')}\n"
        response += f"- Trạng thái: {self._format_payment_status(payment.get('status'))}"

        if payment.get("paid_at"):
            response += f"\n- Đã thanh toán lúc: {payment.get('paid_at')}"

        return {
            "success": True,
            "response": response,
            "data": {"payment": payment},
            "tool_result": result
        }

    async def _handle_get_my_bookings(
        self,
        db: Any,
        state: BookingState
    ) -> Dict[str, Any]:
        """Xử lý lấy danh sách booking của user"""
        result = await self.booking_tools.get_user_bookings(
            db=db,
            user_id=state.user_id
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": f"Không lấy được danh sách: {result.get('error')}",
                "tool_result": result
            }

        bookings = result.get("bookings", [])

        if not bookings:
            return {
                "success": True,
                "response": "Bạn chưa có booking nào.",
                "data": {"bookings": []}
            }

        booking_list = []
        for b in bookings:
            status_icon = "✓" if b["status"] == "CONFIRMED" else "⏳" if b["status"] == "PENDING_PAYMENT" else "✗"
            item = f"{status_icon} {b['booking_code']}: {b['seat_count']} ghế - {b['total_amount']:,} VND - {self._format_booking_status(b['status'])}"
            booking_list.append(item)

        response = f"Bạn có {len(bookings)} booking:\n\n" + "\n".join(booking_list)
        response += "\n\nBạn muốn xem chi tiết hoặc thực hiện thao tác gì?"

        return {
            "success": True,
            "response": response,
            "data": {"bookings": bookings},
            "tool_result": result
        }

    async def _handle_unknown(
        self,
        db: Any,
        state: BookingState,
        message: str
    ) -> Dict[str, Any]:
        """Xử lý khi không nhận diện được intent"""
        # Try to help based on context
        if state.context.get("available_trips"):
            return {
                "success": True,
                "response": "Tôi có thể giúp bạn:\n"
                           "- Đặt vé: cho tôi biết số ghế bạn muốn đặt\n"
                           "- Xem thông tin chuyến\n"
                           "- Kiểm tra ghế trống\n"
                           "- Xem booking của bạn\n"
                           "- Thanh toán vé",
                "next_action": "help"
            }

        return {
            "success": True,
            "response": "Xin chào! Tôi có thể giúp bạn:\n"
                       "- Tìm chuyến xe: 'tìm xe đi Đà Lạt'\n"
                       "- Đặt vé: 'đặt 2 vé đi Tà Xùa'\n"
                       "- Xem booking: 'xem vé của tôi'\n"
                       "- Thanh toán: 'thanh toán'\n"
                       "- Hủy vé: 'hủy vé'\n\n"
                       "Bạn cần hỗ trợ gì?",
            "next_action": "greeting"
        }

    def _format_booking_status(self, status: str) -> str:
        """Format booking status để hiển thị"""
        status_map = {
            "PENDING_PAYMENT": "Chờ thanh toán",
            "CONFIRMED": "Đã xác nhận",
            "CANCELLED": "Đã hủy"
        }
        return status_map.get(status, status)

    def _format_payment_status(self, status: str) -> str:
        """Format payment status để hiển thị"""
        status_map = {
            "PENDING": "Chờ thanh toán",
            "PAID": "Đã thanh toán",
            "FAILED": "Thanh toán thất bại"
        }
        return status_map.get(status, status)
