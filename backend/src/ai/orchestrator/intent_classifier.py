"""
Intent Classifier - LLM-based intent classification for Hiền Hựu Bus

Sử dụng LLM Provider để phân loại intent từ tin nhắn khách hàng.
Chỉ phân loại intent, không thực hiện nghiệp vụ.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.models.llm_client import (
    LLMClient,
    MockProvider,
    LLMConfigurationError,
    LLMError,
    LLMTimeoutError,
    LLMProviderError,
)
from src.ai.orchestrator.structured_output import (
    StructuredOutputParser,
    INTENT_CLASSIFIER_SCHEMA,
)
from src.utils.logger import logger


class Intent(str, Enum):
    """Các intent được hỗ trợ"""
    # Booking domain
    SEARCH_TRIP = "SEARCH_TRIP"
    TRIP_INFO = "TRIP_INFO"
    CHECK_SEATS = "CHECK_SEATS"
    BOOK_TICKET = "BOOK_TICKET"
    VIEW_BOOKING = "VIEW_BOOKING"
    CANCEL_BOOKING = "CANCEL_BOOKING"
    PAYMENT_STATUS = "PAYMENT_STATUS"

    # Complaint domain
    COMPLAINT = "COMPLAINT"
    REQUEST_REFUND = "REQUEST_REFUND"

    # General
    GREETING = "GREETING"
    UNKNOWN = "UNKNOWN"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"


class Domain(str, Enum):
    """Domain mapping từ intent"""
    BOOKING = "BOOKING"
    COMPLAINT = "COMPLAINT"
    UNKNOWN = "UNKNOWN"


# Confidence threshold - below this, classify as NEEDS_CLARIFICATION
CONFIDENCE_THRESHOLD = 0.7

# System instruction for classification
SYSTEM_INSTRUCTION = """Bạn là Intent Classifier cho hệ thống Hiền Hựu Bus Customer Service.

Phân loại tin nhắn của khách hàng vào một trong các intent sau:

**BOOKING Domain:**
- SEARCH_TRIP: Tìm kiếm chuyến xe (điểm đi, điểm đến, ngày)
- TRIP_INFO: Hỏi thông tin chi tiết chuyến xe
- CHECK_SEATS: Kiểm tra số ghế còn trống
- BOOK_TICKET: Đặt vé/đặt chỗ
- VIEW_BOOKING: Xem thông tin vé đã đặt, tra cứu booking
- CANCEL_BOOKING: Hủy vé/hủy booking
- PAYMENT_STATUS: Hỏi trạng thái thanh toán

**COMPLAINT Domain:**
- COMPLAINT: Phản ánh/khiếu nại về dịch vụ
- REQUEST_REFUND: Yêu cầu hoàn tiền

**General:**
- GREETING: Chào hỏi, cảm ơn, tạm biệt
- UNKNOWN: Không xác định được intent
- NEEDS_CLARIFICATION: Intent không rõ ràng, cần hỏi thêm

Trả lời JSON với format:
{
    "intent": "INTENT_NAME",
    "confidence": 0.0-1.0,
    "reasoning": "giải thích ngắn",
    "needs_clarification": true/false,
    "missing_info": ["thông tin cần hỏi thêm"]
}

Chỉ trả JSON, không giải thích thêm."""


@dataclass
class IntentClassification:
    """
    Kết quả phân loại intent.

    Attributes:
        intent: Intent đã phân loại
        domain: Domain tương ứng
        confidence: Mức độ tin cậy (0.0-1.0)
        reasoning: Lý do phân loại
        needs_clarification: Cần hỏi thêm khách hàng
        missing_info: Danh sách thông tin cần hỏi
    """
    intent: Intent
    domain: Domain
    confidence: float
    reasoning: str
    needs_clarification: bool
    missing_info: list[str]

    def to_dict(self) -> dict:
        """Convert to dict"""
        return {
            "intent": self.intent.value,
            "domain": self.domain.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "needs_clarification": self.needs_clarification,
            "missing_info": self.missing_info,
        }


class IntentClassifier:
    """
    LLM-based Intent Classifier.

    Sử dụng LLM Provider để phân loại intent từ tin nhắn.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Khởi tạo classifier.

        Args:
            llm_client: LLM Client (optional, sẽ tạo mới nếu không cung cấp)
        """
        self._llm_client = llm_client

    @property
    def llm_client(self) -> LLMClient:
        """Lazy initialization của LLM client"""
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    async def classify(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None
    ) -> IntentClassification:
        """
        Phân loại intent từ tin nhắn.

        Args:
            message: Tin nhắn của khách hàng
            conversation_history: Lịch sử hội thoại (tùy chọn)

        Returns:
            IntentClassification result
        """
        # Build messages for LLM
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION}
        ]

        # Add conversation history if available (last 3 messages)
        if conversation_history:
            recent = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            for msg in recent:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "customer"]:
                    messages.append({"role": "user", "content": content})

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            # Call LLM
            response = await self.llm_client.generate_with_messages(messages)

            # Parse response using StructuredOutputParser
            return self._parse_response(response, message)

        except LLMConfigurationError as e:
            logger.warning(f"LLM configuration error in classifier: {e}")
            return self._fallback_classification(message, "LLM configuration error")
        except LLMTimeoutError as e:
            logger.warning(f"LLM timeout in classifier: {e}")
            return self._fallback_classification(message, "LLM timeout")
        except LLMProviderError as e:
            logger.warning(f"LLM provider error in classifier: {e}")
            return self._fallback_classification(message, "LLM provider error")
        except Exception as e:
            logger.error(f"Unexpected error in intent classifier: {e}")
            return self._fallback_classification(message, str(e))

    def _parse_response(
        self,
        response: str,
        original_message: str
    ) -> IntentClassification:
        """Parse LLM response thành IntentClassification."""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse(response)

        if not result.is_success:
            logger.warning(f"Parse failed ({result.status.value}): {result.error_message}")
            return self._fallback_classification(original_message, f"Parse error: {result.status.value}")

        data = result.data
        intent_str = data.get("intent", "UNKNOWN")
        confidence = data.get("confidence", 0.5)
        reasoning = data.get("reasoning", "")
        needs_clarification = data.get("needs_clarification", False)
        missing_info = data.get("missing_info", [])

        try:
            intent = Intent(intent_str)
        except ValueError:
            intent = Intent.UNKNOWN

        domain = self._intent_to_domain(intent)

        if confidence < CONFIDENCE_THRESHOLD:
            needs_clarification = True
            if intent == Intent.UNKNOWN:
                intent = Intent.NEEDS_CLARIFICATION

        return IntentClassification(
            intent=intent, domain=domain, confidence=confidence,
            reasoning=reasoning, needs_clarification=needs_clarification,
            missing_info=missing_info if isinstance(missing_info, list) else [],
        )

    def _intent_to_domain(self, intent: Intent) -> Domain:
        """Map intent to domain"""
        booking_intents = {
            Intent.SEARCH_TRIP, Intent.TRIP_INFO, Intent.CHECK_SEATS,
            Intent.BOOK_TICKET, Intent.VIEW_BOOKING, Intent.CANCEL_BOOKING,
            Intent.PAYMENT_STATUS,
        }
        complaint_intents = {Intent.COMPLAINT, Intent.REQUEST_REFUND}

        if intent in booking_intents:
            return Domain.BOOKING
        elif intent in complaint_intents:
            return Domain.COMPLAINT
        else:
            return Domain.UNKNOWN

    def _fallback_classification(
        self,
        message: str,
        error_reason: str
    ) -> IntentClassification:
        """Fallback classification khi LLM fails."""
        message_lower = message.lower()

        booking_keywords = ["tìm", "xe", "chuyến", "đặt", "vé", "booking", "ghế", "thanh toán", "hủy", "tra cứu"]
        complaint_keywords = ["khiếu", "nại", "khiếu nại", "complaint", "phàn nàn", "hoàn tiền", "refund", "hài lòng", "phản ánh"]
        greeting_keywords = ["chào", "hi", "hello", "hey", "cảm ơn", "thanks", "bye"]

        for kw in greeting_keywords:
            if kw in message_lower:
                return IntentClassification(
                    intent=Intent.GREETING, domain=Domain.UNKNOWN, confidence=0.9,
                    reasoning=f"Fallback: detected greeting '{kw}'",
                    needs_clarification=False, missing_info=[],
                )

        if "khiếu nại" in message_lower or "phàn nàn" in message_lower or "complaint" in message_lower:
            return IntentClassification(
                intent=Intent.COMPLAINT, domain=Domain.COMPLAINT, confidence=0.6,
                reasoning=f"Fallback: detected complaint keyword. Error: {error_reason}",
                needs_clarification=True, missing_info=["Mô tả chi tiết vấn đề"],
            )

        booking_score = sum(1 for kw in booking_keywords if kw in message_lower)
        complaint_score = sum(1 for kw in complaint_keywords if kw in message_lower)

        if booking_score > complaint_score and booking_score >= 2:
            return IntentClassification(
                intent=Intent.UNKNOWN, domain=Domain.BOOKING, confidence=0.5,
                reasoning=f"Fallback: booking domain (score={booking_score}). Error: {error_reason}",
                needs_clarification=True, missing_info=["Xác định rõ yêu cầu cụ thể"],
            )
        elif complaint_score >= 1:
            return IntentClassification(
                intent=Intent.COMPLAINT, domain=Domain.COMPLAINT, confidence=0.6,
                reasoning=f"Fallback: complaint domain (score={complaint_score}). Error: {error_reason}",
                needs_clarification=True, missing_info=["Mô tả chi tiết vấn đề"],
            )

        return IntentClassification(
            intent=Intent.UNKNOWN, domain=Domain.UNKNOWN, confidence=0.3,
            reasoning=f"Fallback: cannot determine intent. Error: {error_reason}",
            needs_clarification=True, missing_info=["Xác định rõ yêu cầu của bạn"],
        )

    def classify_sync(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None
    ) -> IntentClassification:
        """Synchronous wrapper for classify."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.classify(message, conversation_history))


# Singleton instance
_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get singleton IntentClassifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier
