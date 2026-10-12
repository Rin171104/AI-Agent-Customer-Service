"""
Tests for Intent Classifier

Run: pytest tests/test_intent_classifier.py -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.ai.orchestrator.intent_classifier import (
    IntentClassifier,
    IntentClassification,
    Intent,
    Domain,
    CONFIDENCE_THRESHOLD,
    get_intent_classifier,
)


class TestIntentClassifierMock:
    """Tests using MockProvider"""

    @pytest.fixture
    def classifier(self):
        """Create classifier with mock LLM"""
        from src.models.llm_client import MockProvider
        mock_provider = MockProvider()
        mock_client = MagicMock()
        mock_client.provider = mock_provider
        mock_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "SEARCH_TRIP", "confidence": 0.9, "reasoning": "User wants to find a trip", "needs_clarification": false, "missing_info": []}'
        )
        return IntentClassifier(llm_client=mock_client)

    @pytest.mark.asyncio
    async def test_classify_search_trip(self, classifier):
        """Search trip intent is classified correctly"""
        result = await classifier.classify("tìm xe đi Đà Lạt ngày mai")

        assert result.intent == Intent.SEARCH_TRIP
        assert result.domain == Domain.BOOKING
        assert result.confidence == 0.9
        assert result.needs_clarification is False

    @pytest.mark.asyncio
    async def test_classify_book_ticket(self, classifier):
        """Book ticket intent is classified correctly"""
        mock_client = classifier._llm_client
        mock_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "BOOK_TICKET", "confidence": 0.85, "reasoning": "User wants to book", "needs_clarification": false, "missing_info": []}'
        )

        result = await classifier.classify("tôi muốn đặt 2 vé")

        assert result.intent == Intent.BOOK_TICKET
        assert result.domain == Domain.BOOKING

    @pytest.mark.asyncio
    async def test_classify_complaint(self, classifier):
        """Complaint intent is classified correctly"""
        mock_client = classifier._llm_client
        mock_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "COMPLAINT", "confidence": 0.9, "reasoning": "User has a complaint", "needs_clarification": false, "missing_info": []}'
        )

        result = await classifier.classify("tôi muốn khiếu nại về chuyến xe")

        assert result.intent == Intent.COMPLAINT
        assert result.domain == Domain.COMPLAINT

    @pytest.mark.asyncio
    async def test_classify_greeting(self, classifier):
        """Greeting intent is classified correctly"""
        mock_client = classifier._llm_client
        mock_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "GREETING", "confidence": 0.95, "reasoning": "User is greeting", "needs_clarification": false, "missing_info": []}'
        )

        result = await classifier.classify("xin chào")

        assert result.intent == Intent.GREETING

    @pytest.mark.asyncio
    async def test_classify_with_conversation_history(self, classifier):
        """Classifier uses conversation history"""
        history = [
            {"role": "customer", "content": "tìm xe đi Đà Lạt"},
            {"role": "agent", "content": "Có các chuyến..."},
        ]

        await classifier.classify("còn chuyến nào khác không?", history)

        # Verify history was passed to LLM
        mock_client = classifier._llm_client
        call_args = mock_client.generate_with_messages.call_args
        messages = call_args[0][0]
        assert len(messages) >= 3  # system + history + current


class TestIntentClassifierFallback:
    """Tests for fallback behavior when LLM fails"""

    @pytest.fixture
    def classifier_with_failing_llm(self):
        """Create classifier with failing LLM"""
        from src.models.llm_client import LLMProviderError
        mock_client = MagicMock()
        mock_client.generate_with_messages = AsyncMock(
            side_effect=LLMProviderError("Connection failed")
        )
        return IntentClassifier(llm_client=mock_client)

    @pytest.mark.asyncio
    async def test_fallback_greeting(self, classifier_with_failing_llm):
        """Fallback detects greeting"""
        result = await classifier_with_failing_llm.classify("xin chào")

        assert result.intent == Intent.GREETING
        assert result.confidence == 0.9
        assert "Fallback" in result.reasoning

    @pytest.mark.asyncio
    async def test_fallback_booking_domain(self, classifier_with_failing_llm):
        """Fallback detects booking domain"""
        result = await classifier_with_failing_llm.classify("tìm xe đi sài gòn đặt 2 vé")

        assert result.domain == Domain.BOOKING
        assert result.confidence == 0.5
        assert result.needs_clarification is True

    @pytest.mark.asyncio
    async def test_fallback_complaint_domain(self, classifier_with_failing_llm):
        """Fallback returns result when LLM fails"""
        # Test that fallback is called and returns something
        result = await classifier_with_failing_llm.classify("tôi muốn phàn nàn")

        # Should not crash, should return a classification
        assert result is not None
        assert isinstance(result.domain, Domain)

    @pytest.mark.asyncio
    async def test_fallback_truly_unknown(self, classifier_with_failing_llm):
        """Fallback returns unknown for unclear messages"""
        result = await classifier_with_failing_llm.classify("xyz abc 123")

        assert result.intent == Intent.UNKNOWN
        assert result.domain == Domain.UNKNOWN
        assert result.needs_clarification is True


class TestIntentClassifierParseErrors:
    """Tests for LLM response parsing robustness"""

    @pytest.fixture
    def classifier_with_mock(self):
        """Create classifier with mock"""
        mock_client = MagicMock()
        mock_client.generate_with_messages = AsyncMock(return_value="")
        return IntentClassifier(llm_client=mock_client)

    @pytest.mark.asyncio
    async def test_empty_response(self, classifier_with_mock):
        """Empty LLM response triggers fallback"""
        result = await classifier_with_mock.classify("tìm xe")

        assert result.domain == Domain.BOOKING
        assert "Fallback" in result.reasoning

    @pytest.mark.asyncio
    async def test_invalid_json(self, classifier_with_mock):
        """Invalid JSON triggers fallback"""
        classifier_with_mock._llm_client.generate_with_messages = AsyncMock(
            return_value="This is not JSON"
        )

        result = await classifier_with_mock.classify("tìm xe")

        assert result.needs_clarification is True

    @pytest.mark.asyncio
    async def test_missing_fields(self, classifier_with_mock):
        """Missing fields use defaults"""
        classifier_with_mock._llm_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "SEARCH_TRIP"}'
        )

        result = await classifier_with_mock.classify("tìm xe")

        assert result.confidence == 0.5  # default
        assert result.needs_clarification is True  # because confidence < threshold

    @pytest.mark.asyncio
    async def test_invalid_confidence(self, classifier_with_mock):
        """Invalid confidence uses default"""
        classifier_with_mock._llm_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "SEARCH_TRIP", "confidence": "high", "reasoning": "test"}'
        )

        result = await classifier_with_mock.classify("tìm xe")

        assert result.confidence == 0.5  # default

    @pytest.mark.asyncio
    async def test_confidence_out_of_range(self, classifier_with_mock):
        """Out-of-range confidence uses default"""
        classifier_with_mock._llm_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "SEARCH_TRIP", "confidence": 1.5, "reasoning": "test"}'
        )

        result = await classifier_with_mock.classify("tìm xe")

        assert result.confidence == 0.5  # default

    @pytest.mark.asyncio
    async def test_invalid_intent(self, classifier_with_mock):
        """Invalid intent becomes UNKNOWN"""
        classifier_with_mock._llm_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "INVALID_INTENT", "confidence": 0.9, "reasoning": "test"}'
        )

        result = await classifier_with_mock.classify("tìm xe")

        assert result.intent == Intent.UNKNOWN

    @pytest.mark.asyncio
    async def test_low_confidence_triggers_clarification(self, classifier_with_mock):
        """Low confidence triggers needs_clarification"""
        classifier_with_mock._llm_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "SEARCH_TRIP", "confidence": 0.5, "reasoning": "unsure"}'
        )

        result = await classifier_with_mock.classify("tìm xe")

        assert result.needs_clarification is True


class TestIntentClassification:
    """Tests for IntentClassification dataclass"""

    def test_to_dict(self):
        """to_dict returns correct structure"""
        classification = IntentClassification(
            intent=Intent.SEARCH_TRIP,
            domain=Domain.BOOKING,
            confidence=0.9,
            reasoning="User wants to find a trip",
            needs_clarification=False,
            missing_info=[],
        )

        d = classification.to_dict()

        assert d["intent"] == "SEARCH_TRIP"
        assert d["domain"] == "BOOKING"
        assert d["confidence"] == 0.9
        assert d["needs_clarification"] is False

    def test_intent_enum_values(self):
        """All expected intents exist"""
        expected = [
            "SEARCH_TRIP", "TRIP_INFO", "CHECK_SEATS", "BOOK_TICKET",
            "VIEW_BOOKING", "CANCEL_BOOKING", "PAYMENT_STATUS",
            "COMPLAINT", "REQUEST_REFUND", "GREETING", "UNKNOWN", "NEEDS_CLARIFICATION"
        ]
        for intent_name in expected:
            assert hasattr(Intent, intent_name)


class TestDomainMapping:
    """Tests for intent to domain mapping"""

    @pytest.fixture
    def classifier(self):
        mock_client = MagicMock()
        mock_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "SEARCH_TRIP", "confidence": 0.9, "reasoning": "test"}'
        )
        return IntentClassifier(llm_client=mock_client)

    @pytest.mark.asyncio
    async def test_booking_intents_map_to_booking_domain(self, classifier):
        """Booking intents map to BOOKING domain"""
        booking_intents = [
            Intent.SEARCH_TRIP, Intent.TRIP_INFO, Intent.CHECK_SEATS,
            Intent.BOOK_TICKET, Intent.VIEW_BOOKING, Intent.CANCEL_BOOKING,
            Intent.PAYMENT_STATUS
        ]

        for intent in booking_intents:
            classifier._llm_client.generate_with_messages = AsyncMock(
                return_value=f'{{"intent": "{intent.value}", "confidence": 0.9, "reasoning": "test"}}'
            )
            result = await classifier.classify("test")
            assert result.domain == Domain.BOOKING, f"{intent} should map to BOOKING"

    @pytest.mark.asyncio
    async def test_complaint_intents_map_to_complaint_domain(self, classifier):
        """Complaint intents map to COMPLAINT domain"""
        classifier._llm_client.generate_with_messages = AsyncMock(
            return_value='{"intent": "COMPLAINT", "confidence": 0.9, "reasoning": "test"}'
        )
        result = await classifier.classify("test")
        assert result.domain == Domain.COMPLAINT

    @pytest.mark.asyncio
    async def test_other_intents_map_to_unknown_domain(self, classifier):
        """Other intents map to UNKNOWN domain"""
        other_intents = [Intent.GREETING, Intent.UNKNOWN, Intent.NEEDS_CLARIFICATION]

        for intent in other_intents:
            classifier._llm_client.generate_with_messages = AsyncMock(
                return_value=f'{{"intent": "{intent.value}", "confidence": 0.9, "reasoning": "test"}}'
            )
            result = await classifier.classify("test")
            assert result.domain == Domain.UNKNOWN, f"{intent} should map to UNKNOWN"


class TestLLMConfigurationError:
    """Tests for LLM configuration error handling"""

    @pytest.mark.asyncio
    async def test_openai_not_configured_raises(self):
        """OpenAI provider without key raises at init"""
        from src.models.llm_client import OpenAIClient, LLMConfigurationError

        with pytest.raises(LLMConfigurationError):
            OpenAIClient(api_key="")


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_classifier_with_mock_provider_directly(self):
        """Classifier works with MockProvider directly"""
        from src.models.llm_client import MockProvider, LLMClient

        # Mock LLMClient with MockProvider
        mock_llm = MagicMock(spec=LLMClient)
        mock_llm.provider = MockProvider()
        mock_llm.generate_with_messages = AsyncMock(
            return_value='{"intent": "SEARCH_TRIP", "confidence": 0.9, "reasoning": "test", "needs_clarification": false, "missing_info": []}'
        )

        classifier = IntentClassifier(llm_client=mock_llm)
        result = await classifier.classify("tìm xe đi đà lạt")

        assert result.intent == Intent.SEARCH_TRIP
        assert result.domain == Domain.BOOKING

    def test_get_intent_classifier_singleton(self):
        """get_intent_classifier returns singleton"""
        # Reset singleton
        import src.ai.orchestrator.intent_classifier as module
        module._classifier = None

        classifier1 = get_intent_classifier()
        classifier2 = get_intent_classifier()

        assert classifier1 is classifier2
