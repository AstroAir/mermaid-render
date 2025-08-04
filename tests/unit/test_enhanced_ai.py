"""
Unit tests for enhanced AI module features.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from mermaid_render.ai import (
    # Enhanced providers
    OpenRouterProvider,
    CustomProvider,
    ProviderManager,

    # Configuration classes
    ProviderConfig,
    CustomProviderConfig,
    GenerationResponse,

    # Exceptions
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,

    # Factory and utilities
    ProviderFactory,
    create_provider_from_config,
    setup_multi_provider_generation,
    create_default_provider_manager,
)


class TestProviderConfig:
    """Test ProviderConfig class."""

    def test_provider_config_creation(self):
        """Test basic provider config creation."""
        config = ProviderConfig(
            api_key="test-key",
            model="test-model",
            timeout=30,
            max_retries=3
        )

        assert config.api_key == "test-key"
        assert config.model == "test-model"
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_provider_config_validation(self):
        """Test provider config validation."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            ProviderConfig(timeout=0)

        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            ProviderConfig(max_retries=-1)


class TestCustomProviderConfig:
    """Test CustomProviderConfig class."""

    def test_custom_provider_config_creation(self):
        """Test custom provider config creation."""
        config = CustomProviderConfig(
            name="test-provider",
            base_url="https://api.test.com",
            api_key="test-key",
            auth_type="bearer",
            request_format="openai"
        )

        assert config.name == "test-provider"
        assert config.base_url == "https://api.test.com"
        assert config.api_key == "test-key"
        assert config.auth_type == "bearer"
        assert config.request_format == "openai"

    def test_custom_provider_config_validation(self):
        """Test custom provider config validation."""
        with pytest.raises(ValueError, match="Provider name is required"):
            CustomProviderConfig(name="", base_url="https://api.test.com")

        with pytest.raises(ValueError, match="Base URL is required"):
            CustomProviderConfig(name="test", base_url="")


class TestGenerationResponse:
    """Test GenerationResponse class."""

    def test_generation_response_creation(self):
        """Test generation response creation."""
        response = GenerationResponse(
            content="test content",
            model="test-model",
            provider="test-provider",
            usage={"tokens": 100},
            metadata={"test": "data"}
        )

        assert response.content == "test content"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.usage == {"tokens": 100}
        assert response.metadata == {"test": "data"}


class TestOpenRouterProvider:
    """Test OpenRouterProvider class."""

    def test_openrouter_provider_creation(self):
        """Test OpenRouter provider creation."""
        config = ProviderConfig(
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-3.5-turbo"
        )

        provider = OpenRouterProvider(config)

        assert provider.config.api_key == "test-key"
        assert provider.config.base_url == "https://openrouter.ai/api/v1"
        assert provider.config.model == "openai/gpt-3.5-turbo"
        assert provider.provider_name == "openrouter"

    def test_openrouter_provider_availability(self):
        """Test OpenRouter provider availability check."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)
        assert provider.is_available() is True

        config_no_key = ProviderConfig(api_key=None)
        provider_no_key = OpenRouterProvider(config_no_key)
        assert provider_no_key.is_available() is False

    def test_openrouter_supported_models(self):
        """Test OpenRouter supported models."""
        provider = OpenRouterProvider()
        models = provider.get_supported_models()

        assert isinstance(models, list)
        assert len(models) > 0
        assert "openai/gpt-3.5-turbo" in models
        assert "anthropic/claude-3-sonnet" in models

    @patch('requests.post')
    def test_openrouter_generate_text_success(self, mock_post):
        """Test successful text generation with OpenRouter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "test response"}}],
            "model": "openai/gpt-3.5-turbo",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "id": "test-id"
        }
        mock_post.return_value = mock_response

        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        response = provider.generate_text("test prompt")

        assert isinstance(response, GenerationResponse)
        assert response.content == "test response"
        assert response.model == "openai/gpt-3.5-turbo"
        assert response.provider == "openrouter"
        assert response.usage["total_tokens"] == 15

    @patch('requests.post')
    def test_openrouter_generate_text_auth_error(self, mock_post):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        config = ProviderConfig(api_key="invalid-key")
        provider = OpenRouterProvider(config)

        with pytest.raises(AuthenticationError):
            provider.generate_text("test prompt")


class TestCustomProvider:
    """Test CustomProvider class."""

    def test_custom_provider_creation(self):
        """Test custom provider creation."""
        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.test.com",
            api_key="test-key"
        )

        provider = CustomProvider(config)

        assert provider.custom_config.name == "test-api"
        assert provider.provider_name == "test-api"
        assert provider.config.base_url == "https://api.test.com"

    def test_custom_provider_availability(self):
        """Test custom provider availability."""
        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.test.com",
            api_key="test-key"
        )
        provider = CustomProvider(config)
        assert provider.is_available() is True

        config_no_key = CustomProviderConfig(
            name="test-api",
            base_url="https://api.test.com",
            auth_type="none"
        )
        provider_no_key = CustomProvider(config_no_key)
        assert provider_no_key.is_available() is True

    def test_custom_provider_headers(self):
        """Test custom provider header preparation."""
        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.test.com",
            api_key="test-key",
            auth_type="bearer",
            auth_header="Authorization",
            auth_prefix="Bearer"
        )

        provider = CustomProvider(config)
        headers = provider._prepare_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-key"


class TestProviderFactory:
    """Test ProviderFactory class."""

    def test_create_openai_provider(self):
        """Test creating OpenAI provider via factory."""
        config = ProviderConfig(api_key="test-key")
        provider = ProviderFactory.create_provider("openai", config)

        assert provider.__class__.__name__ == "OpenAIProvider"
        assert provider.config.api_key == "test-key"

    def test_create_openrouter_provider(self):
        """Test creating OpenRouter provider via factory."""
        config = ProviderConfig(api_key="test-key")
        provider = ProviderFactory.create_provider("openrouter", config)

        assert provider.__class__.__name__ == "OpenRouterProvider"
        assert provider.config.api_key == "test-key"

    def test_create_custom_provider(self):
        """Test creating custom provider via factory."""
        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.test.com",
            api_key="test-key"
        )
        provider = ProviderFactory.create_provider("custom", config)

        assert provider.__class__.__name__ == "CustomProvider"
        assert provider.custom_config.name == "test-api"

    def test_unsupported_provider_type(self):
        """Test error for unsupported provider type."""
        with pytest.raises(ValueError, match="Unsupported provider type"):
            ProviderFactory.create_provider("unsupported", ProviderConfig())

    def test_get_available_providers(self):
        """Test getting available provider types."""
        providers = ProviderFactory.get_available_providers()

        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "openrouter" in providers
        assert "custom" in providers


class TestProviderManager:
    """Test ProviderManager class."""

    def test_provider_manager_creation(self):
        """Test provider manager creation."""
        manager = ProviderManager()

        assert len(manager.providers) == 0
        assert manager.primary_provider is None

    def test_add_provider(self):
        """Test adding providers to manager."""
        manager = ProviderManager()

        provider1 = Mock()
        provider1.provider_name = "provider1"
        provider1.is_available.return_value = True

        provider2 = Mock()
        provider2.provider_name = "provider2"
        provider2.is_available.return_value = True

        manager.add_provider(provider1, primary=True)
        manager.add_provider(provider2)

        assert len(manager.providers) == 2
        assert manager.primary_provider == provider1
        assert manager.providers[0] == provider1
        assert manager.providers[1] == provider2

    def test_generate_text_with_fallback(self):
        """Test text generation with provider fallback."""
        manager = ProviderManager()

        # First provider fails
        provider1 = Mock()
        provider1.provider_name = "provider1"
        provider1.is_available.return_value = True
        provider1.generate_text.side_effect = ProviderError("Provider 1 failed")

        # Second provider succeeds
        provider2 = Mock()
        provider2.provider_name = "provider2"
        provider2.is_available.return_value = True
        provider2.generate_text.return_value = GenerationResponse(
            content="success",
            provider="provider2"
        )

        manager.add_provider(provider1)
        manager.add_provider(provider2)

        response = manager.generate_text("test prompt")

        assert response.content == "success"
        assert response.provider == "provider2"

    def test_generate_text_all_providers_fail(self):
        """Test when all providers fail."""
        manager = ProviderManager()

        provider = Mock()
        provider.provider_name = "provider1"
        provider.is_available.return_value = True
        provider.generate_text.side_effect = ProviderError("Failed")

        manager.add_provider(provider)

        with pytest.raises(ProviderError):
            manager.generate_text("test prompt")


class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_provider_from_config(self):
        """Test creating provider from config dictionary."""
        config_dict = {
            "api_key": "test-key",
            "model": "test-model",
            "timeout": 30
        }

        provider = create_provider_from_config("openai", config_dict)

        assert provider.__class__.__name__ == "OpenAIProvider"
        assert provider.config.api_key == "test-key"
        assert provider.config.model == "test-model"

    def test_setup_multi_provider_generation(self):
        """Test setting up multi-provider generation."""
        provider_configs = [
            {"type": "local", "config": {}},
        ]

        manager = setup_multi_provider_generation(provider_configs)

        assert isinstance(manager, ProviderManager)
        assert len(manager.providers) >= 1  # At least local provider

    @patch.dict('os.environ', {}, clear=True)
    def test_create_default_provider_manager_no_keys(self):
        """Test creating default provider manager without API keys."""
        manager = create_default_provider_manager()

        assert isinstance(manager, ProviderManager)
        # Should have at least one provider (local fallback should always be added)
        assert len(manager.providers) >= 1

        # The local provider should be available
        available_providers = manager.get_available_providers()
        assert len(available_providers) >= 1

        # Check that we have a local model provider
        local_providers = [
            p for p in manager.providers if "local" in p.provider_name.lower()]
        assert len(local_providers) >= 1
        assert local_providers[0].is_available() is True
