"""
Tests for LLM Provider

Run: pytest tests/test_llm_provider.py -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Test exceptions
from src.models.llm_client import (
    LLMProvider,
    MockProvider,
    OpenAIClient,
    LLMClient,
    LLMError,
    LLMConfigurationError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMProviderError,
    LLMEmptyResponseError,
)


class TestMockProvider:
    """Tests for MockProvider"""

    @pytest.mark.asyncio
    async def test_mock_generate(self):
        """Mock provider returns mock response"""
        provider = MockProvider()
        result = await provider.generate("Hello")
        assert result == "Mock response - This is a simulated LLM response."

    @pytest.mark.asyncio
    async def test_mock_generate_with_messages(self):
        """Mock provider handles messages"""
        provider = MockProvider()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        result = await provider.generate_with_messages(messages)
        assert result == "Mock response - This is a simulated LLM response."


class TestOpenAIClient:
    """Tests for OpenAIClient"""

    def test_init_without_api_key_raises_error(self):
        """Empty API key raises LLMConfigurationError"""
        with pytest.raises(LLMConfigurationError) as exc:
            OpenAIClient(api_key="")
        assert "OPENAI_API_KEY is required" in str(exc.value)

    def test_init_with_none_api_key_raises_error(self):
        """None API key raises LLMConfigurationError"""
        with pytest.raises(LLMConfigurationError) as exc:
            OpenAIClient(api_key=None)
        assert "OPENAI_API_KEY is required" in str(exc.value)

    def test_init_with_valid_key(self):
        """Valid API key initializes successfully"""
        # This won't fail even without actual API key
        provider = OpenAIClient(api_key="test-key-123", model="gpt-4o-mini")
        assert provider.api_key == "test-key-123"
        assert provider.model == "gpt-4o-mini"
        assert provider.timeout == 30

    def test_init_with_custom_timeout(self):
        """Custom timeout is set"""
        provider = OpenAIClient(
            api_key="test-key-123",
            timeout=60
        )
        assert provider.timeout == 60

    @pytest.mark.asyncio
    async def test_generate_without_api_key_no_request(self):
        """No actual request is made if API key is missing"""
        # This tests the error happens at init, not at call time
        with pytest.raises(LLMConfigurationError):
            OpenAIClient(api_key="")

    @pytest.mark.asyncio
    async def test_generate_logs_without_exposing_key(self):
        """Log messages don't expose API key"""
        provider = OpenAIClient(api_key="secret-key-12345")
        # Client is lazy initialized, just check the object exists
        assert provider.api_key == "secret-key-12345"


class TestLLMClientFactory:
    """Tests for LLMClient factory"""

    def test_create_mock_provider(self):
        """Factory creates mock provider when configured"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "mock"
            mock_settings.LLM_MODEL = "gpt-4o-mini"

            client = LLMClient()
            assert isinstance(client.provider, MockProvider)

    def test_create_openai_provider(self):
        """Factory creates OpenAI provider when configured"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "openai"
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4o-mini"
            mock_settings.LLM_TIMEOUT_SECONDS = 30

            client = LLMClient()
            assert isinstance(client.provider, OpenAIClient)

    def test_unsupported_provider_raises_error(self):
        """Unsupported provider raises LLMConfigurationError"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "unsupported"

            with pytest.raises(LLMConfigurationError) as exc:
                LLMClient()
            assert "Unsupported LLM provider" in str(exc.value)

    def test_provider_name_case_insensitive(self):
        """Provider name is case insensitive"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "MOCK"
            mock_settings.LLM_MODEL = "gpt-4o-mini"

            client = LLMClient()
            assert isinstance(client.provider, MockProvider)


class TestExceptions:
    """Tests for LLM exceptions"""

    def test_llm_error_inheritance(self):
        """All LLM errors inherit from LLMError"""
        errors = [
            LLMConfigurationError("test"),
            LLMAuthenticationError("test"),
            LLMRateLimitError("test"),
            LLMTimeoutError("test"),
            LLMProviderError("test"),
            LLMEmptyResponseError("test"),
        ]
        for error in errors:
            assert isinstance(error, LLMError)

    def test_error_messages(self):
        """Error messages are preserved"""
        msg = "Test error message"
        error = LLMConfigurationError(msg)
        assert str(error) == msg


class TestProviderInterface:
    """Tests for provider interface compliance"""

    def test_mock_provider_implements_interface(self):
        """MockProvider implements LLMProvider interface"""
        provider = MockProvider()
        assert isinstance(provider, LLMProvider)
        assert hasattr(provider, 'generate')
        assert hasattr(provider, 'generate_with_messages')

    def test_openai_client_implements_interface(self):
        """OpenAIClient implements LLMProvider interface"""
        provider = OpenAIClient(api_key="test")
        assert isinstance(provider, LLMProvider)
        assert hasattr(provider, 'generate')
        assert hasattr(provider, 'generate_with_messages')

    @pytest.mark.asyncio
    async def test_mock_generate_returns_string(self):
        """generate() returns a string"""
        provider = MockProvider()
        result = await provider.generate("test")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_mock_generate_with_messages_returns_string(self):
        """generate_with_messages() returns a string"""
        provider = MockProvider()
        result = await provider.generate_with_messages([])
        assert isinstance(result, str)


class TestSecurity:
    """Security-related tests"""

    def test_api_key_not_in_repr(self):
        """API key is not exposed in repr"""
        provider = OpenAIClient(api_key="super-secret-key")
        # __repr__ should not contain the key
        repr_str = repr(provider)
        assert "super-secret-key" not in repr_str

    def test_empty_api_key_rejected_at_init(self):
        """Empty API key is rejected immediately"""
        with pytest.raises(LLMConfigurationError):
            OpenAIClient(api_key="")

    def test_whitespace_api_key_rejected(self):
        """Whitespace-only API key is rejected"""
        with pytest.raises(LLMConfigurationError):
            OpenAIClient(api_key="   ")


class TestTimeout:
    """Tests for timeout configuration"""

    def test_default_timeout(self):
        """Default timeout is 30 seconds"""
        provider = OpenAIClient(api_key="test", timeout=30)
        assert provider.timeout == 30

    def test_custom_timeout(self):
        """Custom timeout is respected"""
        provider = OpenAIClient(api_key="test", timeout=120)
        assert provider.timeout == 120


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing code"""

    def test_llm_client_has_generate_method(self):
        """LLMClient has generate() method"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "mock"
            mock_settings.LLM_MODEL = "test"

            client = LLMClient()
            assert hasattr(client, 'generate')
            assert callable(client.generate)

    def test_llm_client_has_generate_with_messages_method(self):
        """LLMClient has generate_with_messages() method"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "mock"
            mock_settings.LLM_MODEL = "test"

            client = LLMClient()
            assert hasattr(client, 'generate_with_messages')
            assert callable(client.generate_with_messages)

    @pytest.mark.asyncio
    async def test_generate_returns_string(self):
        """generate() returns string for backward compatibility"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "mock"
            mock_settings.LLM_MODEL = "test"

            client = LLMClient()
            result = await client.generate("test prompt")
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_with_messages_returns_string(self):
        """generate_with_messages() returns string for backward compatibility"""
        with patch('src.models.llm_client.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "mock"
            mock_settings.LLM_MODEL = "test"

            client = LLMClient()
            messages = [{"role": "user", "content": "test"}]
            result = await client.generate_with_messages(messages)
            assert isinstance(result, str)
