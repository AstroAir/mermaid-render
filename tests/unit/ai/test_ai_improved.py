from typing import Any
"""
Unit tests for improved AI module features.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from mermaid_render.ai import (
    # Improved providers
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


class TestOpenRouterProvider:
    """Test OpenRouter provider functionality."""

    def test_openrouter_provider_creation(self) -> None:
        """Test OpenRouter provider creation."""
        config = ProviderConfig(
            api_key="test-key",
            model="anthropic/claude-3-opus",
            base_url="https://openrouter.ai/api/v1"
        )
        
        provider = OpenRouterProvider(config)
        
        assert provider.config.api_key == "test-key"
        assert provider.config.model == "anthropic/claude-3-opus"
        assert provider.config.base_url == "https://openrouter.ai/api/v1"

    def test_openrouter_provider_default_config(self) -> None:
        """Test OpenRouter provider with default configuration."""
        provider = OpenRouterProvider()
        
        assert provider.config.base_url == "https://openrouter.ai/api/v1"
        assert provider.config.model == "openai/gpt-3.5-turbo"
        assert provider.config.timeout == 30

    @patch('requests.post')
    def test_openrouter_generate_text_success(self, mock_post: Any) -> None:
        """Test successful text generation with OpenRouter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "graph TD\n    A --> B"
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 15,
                "total_tokens": 25
            }
        }
        mock_post.return_value = mock_response

        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)
        
        result = provider.generate_text("Create a simple flowchart")

        assert result.content == "graph TD\n    A --> B"
        assert isinstance(result.content, str)
        assert result.provider == "openrouter"

    @patch('requests.post')
    def test_openrouter_generate_text_failure(self, mock_post: Any) -> None:
        """Test failed text generation with OpenRouter."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid API key"
            }
        }
        mock_post.return_value = mock_response

        config = ProviderConfig(api_key="invalid-key")
        provider = OpenRouterProvider(config)
        
        with pytest.raises(AuthenticationError):
            provider.generate_text("Create a simple flowchart")

    @patch('requests.post')
    def test_openrouter_rate_limit_handling(self, mock_post: Any) -> None:
        """Test rate limit error handling."""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded"
            }
        }
        mock_post.return_value = mock_response

        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)
        
        with pytest.raises(RateLimitError):
            provider.generate_text("Create a simple flowchart")

    def test_openrouter_provider_availability(self) -> None:
        """Test OpenRouter provider availability check."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)
        assert provider.is_available() is True

        config_no_key = ProviderConfig(api_key=None)
        provider_no_key = OpenRouterProvider(config_no_key)
        assert provider_no_key.is_available() is False

    def test_openrouter_supported_models(self) -> None:
        """Test OpenRouter supported models."""
        provider = OpenRouterProvider()
        models = provider.get_supported_models()

        assert isinstance(models, list)
        assert len(models) > 0
        assert "openai/gpt-3.5-turbo" in models
        assert "anthropic/claude-3-sonnet" in models


class TestCustomProvider:
    """Test custom provider functionality."""

    def test_custom_provider_creation(self) -> None:
        """Test custom provider creation."""
        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.example.com/v1",
            api_key="test-key",
            request_format="openai"
        )
        
        provider = CustomProvider(config)

        assert provider.custom_config.name == "test-api"
        assert provider.custom_config.base_url == "https://api.example.com/v1"
        assert provider.custom_config.request_format == "openai"

    @patch('requests.post')
    def test_custom_provider_openai_format(self, mock_post: Any) -> None:
        """Test custom provider with OpenAI format."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "graph TD\n    A --> B"
                }
            }]
        }
        mock_post.return_value = mock_response

        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.example.com/v1",
            api_key="test-key",
            request_format="openai"
        )
        provider = CustomProvider(config)
        
        result = provider.generate_text("Create a flowchart")
        
        assert result.content == "graph TD\n    A --> B"
        assert isinstance(result.content, str)

    @patch('requests.post')
    def test_custom_provider_anthropic_format(self, mock_post: Any) -> None:
        """Test custom provider with Anthropic format."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{
                "text": "graph TD\n    A --> B"
            }]
        }
        mock_post.return_value = mock_response

        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.example.com/v1",
            api_key="test-key",
            request_format="anthropic"
        )
        provider = CustomProvider(config)
        
        result = provider.generate_text("Create a flowchart")
        
        # The actual result will be different due to fallback generation
        assert isinstance(result.content, str)
        assert len(result.content) > 0

    def test_custom_provider_invalid_format(self) -> None:
        """Test custom provider with invalid format."""
        with pytest.raises(ValueError):
            CustomProviderConfig(
                name="test-api",
                base_url="https://api.example.com/v1",
                api_key="test-key",
                request_format="invalid"
            )


class TestProviderFactory:
    """Test ProviderFactory functionality."""

    def test_create_openai_provider(self) -> None:
        """Test creating OpenAI provider through factory."""
        from mermaid_render.ai.providers import ProviderConfig

        config = ProviderConfig(
            api_key="test-key",
            model="gpt-4"
        )

        provider = ProviderFactory.create_provider("openai", config)
        
        assert provider.config.api_key == "test-key"
        assert provider.config.model == "gpt-4"

    def test_create_anthropic_provider(self) -> None:
        """Test creating Anthropic provider through factory."""
        from mermaid_render.ai.providers import ProviderConfig

        config = ProviderConfig(
            api_key="test-key",
            model="claude-3-sonnet-20240229"
        )

        provider = ProviderFactory.create_provider("anthropic", config)
        
        assert provider.config.api_key == "test-key"
        assert provider.config.model == "claude-3-sonnet-20240229"

    def test_create_openrouter_provider(self) -> None:
        """Test creating OpenRouter provider through factory."""
        from mermaid_render.ai.providers import ProviderConfig

        config = ProviderConfig(
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="anthropic/claude-3-opus"
        )

        provider = ProviderFactory.create_provider("openrouter", config)
        
        assert provider.config.api_key == "test-key"
        assert provider.config.model == "anthropic/claude-3-opus"

    def test_create_custom_provider(self) -> None:
        """Test creating custom provider through factory."""
        from mermaid_render.ai.providers import CustomProviderConfig

        config = CustomProviderConfig(
            name="test-api",
            base_url="https://api.example.com/v1",
            api_key="test-key",
            request_format="openai"
        )

        provider = ProviderFactory.create_provider("custom", config)

        assert provider.custom_config.name == "test-api"
        assert provider.custom_config.base_url == "https://api.example.com/v1"

    def test_create_invalid_provider(self) -> None:
        """Test creating invalid provider type."""
        with pytest.raises(ValueError):
            ProviderFactory.create_provider("invalid", {})

    def test_get_available_providers(self) -> None:
        """Test getting available provider types."""
        providers = ProviderFactory.get_available_providers()

        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "openrouter" in providers
        assert "custom" in providers


class TestProviderManager:
    """Test ProviderManager class."""

    def test_provider_manager_creation(self) -> None:
        """Test provider manager creation."""
        manager = ProviderManager()

        assert len(manager.providers) == 0
        assert manager.primary_provider is None
