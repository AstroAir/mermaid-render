"""
AI provider implementations for diagram generation.

This module provides a flexible architecture for integrating various AI providers
with the mermaid-render library, including OpenAI, Anthropic, OpenRouter, and
custom providers.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, cast
from urllib.parse import urljoin

import requests

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for AI providers."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    custom_headers: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


@dataclass
class GenerationResponse:
    """Response from AI provider generation."""

    content: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, provider: str = "unknown", error_code: Optional[str] = None) -> None:
        super().__init__(message)
        self.provider = provider
        self.error_code = error_code


class AuthenticationError(ProviderError):
    """Authentication-related errors."""
    pass


class RateLimitError(ProviderError):
    """Rate limiting errors."""
    pass


class ModelNotFoundError(ProviderError):
    """Model not found errors."""
    pass


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    This class defines the interface that all AI providers must implement
    to be compatible with the mermaid-render AI module.
    """

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        """Initialize the provider with configuration."""
        self.config: ProviderConfig = config or ProviderConfig()
        self._client: Optional[Any] = None
        self.provider_name: str = self.__class__.__name__.replace(
            "Provider", "").lower()

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """
        Generate text from prompt.

        Args:
            prompt: The input prompt for generation
            **kwargs: Additional generation parameters

        Returns:
            GenerationResponse with the generated content

        Raises:
            ProviderError: If generation fails
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available and properly configured.

        Returns:
            True if provider is available, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported models for this provider.

        Returns:
            List of model names/identifiers
        """
        raise NotImplementedError

    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid

        Raises:
            ProviderError: If configuration is invalid
        """
        if not self.config.api_key:
            raise AuthenticationError(
                "API key is required",
                provider=self.provider_name
            )
        return True

    def _handle_http_error(self, response: requests.Response) -> None:
        """Handle HTTP errors from API responses."""
        if response.status_code == 401:
            raise AuthenticationError(
                "Invalid API key or authentication failed",
                provider=self.provider_name,
                error_code="401"
            )
        elif response.status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded",
                provider=self.provider_name,
                error_code="429"
            )
        elif response.status_code == 404:
            raise ModelNotFoundError(
                "Model not found or not available",
                provider=self.provider_name,
                error_code="404"
            )
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("error", {}).get("message", response.text)
            except Exception:
                message = response.text

            raise ProviderError(
                f"HTTP {response.status_code}: {message}",
                provider=self.provider_name,
                error_code=str(response.status_code)
            )

    def _get_fallback_response(self, prompt: str) -> GenerationResponse:
        """Generate fallback response when provider is unavailable."""
        logger.warning(f"Using fallback generation for {self.provider_name}")

        # Simple template-based generation
        if "flowchart" in prompt.lower():
            content = """flowchart TD
    A[Start] --> B[Process]
    B --> C[Decision]
    C -->|Yes| D[Action]
    C -->|No| E[Alternative]
    D --> F[End]
    E --> F"""
        elif "sequence" in prompt.lower():
            content = """sequenceDiagram
    participant A as User
    participant B as System
    A->>B: Request
    B-->>A: Response"""
        elif "class" in prompt.lower():
            content = """classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }"""
        else:
            content = "flowchart TD\n    A[Generated Diagram] --> B[End]"

        return GenerationResponse(
            content=content,
            provider="fallback",
            metadata={"fallback": True, "original_provider": self.provider_name}
        )


class OpenAIProvider(AIProvider):
    """
    OpenAI GPT provider with enhanced error handling and configuration.

    Supports all OpenAI models including GPT-3.5, GPT-4, and newer variants.
    """

    def __init__(self, config: Optional[ProviderConfig] = None, model: str = "gpt-3.5-turbo") -> None:
        """Initialize OpenAI provider."""
        if config is None:
            config = ProviderConfig(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=model
            )
        elif config.model is None:
            config.model = model

        super().__init__(config)
        self._client: Optional[Any] = None

    @property
    def api_key(self) -> Optional[str]:
        """Get the API key."""
        return self.config.api_key

    @property
    def model(self) -> Optional[str]:
        """Get the model name."""
        return self.config.model

    def generate_text(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generate text using OpenAI API."""
        try:
            import openai
        except ImportError:
            logger.warning("OpenAI library not installed, using fallback")
            return self._get_fallback_response(prompt)

        try:
            if not self._client:
                if not self.config.api_key:
                    raise AuthenticationError(
                        "OpenAI API key not provided",
                        provider=self.provider_name
                    )
                # Create client
                self._client = openai.OpenAI(
                    api_key=self.config.api_key,
                    timeout=self.config.timeout
                )

            # Prepare messages
            raw_messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
            messages: List[Dict[str, Any]]
            if isinstance(raw_messages, str):
                messages = [{"role": "user", "content": raw_messages}]
            else:
                messages = cast(List[Dict[str, Any]], raw_messages)

            # Make API call with retry logic
            for attempt in range(self.config.max_retries + 1):
                try:
                    assert self._client is not None  # for type checker
                    response = self._client.chat.completions.create(
                        model=self.config.model or "gpt-3.5-turbo",
                        messages=messages,  # SDK accepts dicts
                        max_tokens=cast(int, kwargs.get("max_tokens", 1000)),
                        temperature=cast(float, kwargs.get("temperature", 0.7)),
                        top_p=cast(float, kwargs.get("top_p", 1.0)),
                        frequency_penalty=cast(
                            float, kwargs.get("frequency_penalty", 0.0)),
                        presence_penalty=cast(
                            float, kwargs.get("presence_penalty", 0.0)),
                        stop=kwargs.get("stop"),
                        stream=cast(bool, kwargs.get("stream", False)),
                    )

                    content = getattr(response.choices[0].message, "content", "") or ""

                    return GenerationResponse(
                        content=content,
                        model=getattr(response, "model", None),
                        usage=({
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens,
                        } if getattr(response, "usage", None) else None),
                        provider=self.provider_name,
                        metadata={
                            "finish_reason": response.choices[0].finish_reason,
                            "response_id": response.id,
                        }
                    )

                except openai.RateLimitError as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise RateLimitError(str(e), provider=self.provider_name)

                except openai.AuthenticationError as e:
                    raise AuthenticationError(str(e), provider=self.provider_name)

                except openai.NotFoundError as e:
                    raise ModelNotFoundError(str(e), provider=self.provider_name)

                except Exception as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"API error, retrying in {wait_time}s: {e}")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise ProviderError(
                        f"OpenAI API error: {e}", provider=self.provider_name)

            # This should never be reached due to the loop structure, but add for safety
            raise ProviderError("Max retries exceeded", provider=self.provider_name)

        except (AuthenticationError, RateLimitError, ModelNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {e}")
            return self._get_fallback_response(prompt)

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            import openai  # noqa: F401
            return self.config.api_key is not None
        except ImportError:
            return False

    def get_supported_models(self) -> List[str]:
        """Get list of supported OpenAI models."""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ]

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        super().validate_config()

        if self.config.model not in self.get_supported_models():
            logger.warning(f"Model {self.config.model} may not be supported")

        return True


class AnthropicProvider(AIProvider):
    """
    Anthropic Claude provider with enhanced error handling and configuration.

    Supports Claude 3 models including Haiku, Sonnet, and Opus variants.
    """

    def __init__(self, config: Optional[ProviderConfig] = None, model: str = "claude-3-5-sonnet-20241022") -> None:
        """Initialize Anthropic provider."""
        if config is None:
            config = ProviderConfig(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model=model
            )
        elif config.model is None:
            config.model = model

        super().__init__(config)
        self._client: Optional[Any] = None

    @property
    def api_key(self) -> Optional[str]:
        """Get the API key."""
        return self.config.api_key

    @property
    def model(self) -> Optional[str]:
        """Get the model name."""
        return self.config.model

    def generate_text(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generate text using Anthropic API."""
        try:
            import anthropic
        except ImportError:
            logger.warning("Anthropic library not installed, using fallback")
            return self._get_fallback_response(prompt)

        try:
            if not self._client:
                if not self.config.api_key:
                    raise AuthenticationError(
                        "Anthropic API key not provided",
                        provider=self.provider_name
                    )
                self._client = anthropic.Anthropic(
                    api_key=self.config.api_key,
                    timeout=self.config.timeout
                )

            # Prepare messages
            raw_messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
            messages: List[Dict[str, Any]]
            if isinstance(raw_messages, str):
                messages = [{"role": "user", "content": raw_messages}]
            else:
                messages = cast(List[Dict[str, Any]], raw_messages)

            for attempt in range(self.config.max_retries + 1):
                try:
                    assert self._client is not None
                    response = self._client.messages.create(
                        model=self.config.model or "claude-3-5-sonnet-20241022",
                        max_tokens=cast(int, kwargs.get("max_tokens", 1000)),
                        messages=messages,
                        temperature=cast(float, kwargs.get("temperature", 0.7)),
                        top_p=cast(float, kwargs.get("top_p", 1.0)),
                        stop_sequences=cast(Optional[List[str]], kwargs.get("stop")),
                        stream=cast(bool, kwargs.get("stream", False)),
                    )

                    # Extract content
                    content = ""
                    if getattr(response, "content", None):
                        for block in response.content:
                            if hasattr(block, 'text'):
                                content += getattr(block, 'text', "")

                    return GenerationResponse(
                        content=content,
                        model=getattr(response, "model", None),
                        usage=({
                            "prompt_tokens": response.usage.input_tokens,
                            "completion_tokens": response.usage.output_tokens,
                            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                        } if getattr(response, "usage", None) else None),
                        provider=self.provider_name,
                        metadata={
                            "finish_reason": getattr(response, "stop_reason", None),
                            "response_id": getattr(response, "id", None),
                        }
                    )

                except anthropic.RateLimitError as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise RateLimitError(str(e), provider=self.provider_name)

                except anthropic.AuthenticationError as e:
                    raise AuthenticationError(str(e), provider=self.provider_name)

                except anthropic.NotFoundError as e:
                    raise ModelNotFoundError(str(e), provider=self.provider_name)

                except Exception as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"API error, retrying in {wait_time}s: {e}")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise ProviderError(
                        f"Anthropic API error: {e}", provider=self.provider_name)

            # This should never be reached due to the loop structure, but add for safety
            raise ProviderError("Max retries exceeded", provider=self.provider_name)

        except (AuthenticationError, RateLimitError, ModelNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic provider: {e}")
            return self._get_fallback_response(prompt)

    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        try:
            import anthropic  # noqa: F401
            return self.config.api_key is not None
        except ImportError:
            return False

    def get_supported_models(self) -> List[str]:
        """Get list of supported Anthropic models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    def validate_config(self) -> bool:
        """Validate Anthropic configuration."""
        super().validate_config()

        if self.config.model not in self.get_supported_models():
            logger.warning(f"Model {self.config.model} may not be supported")

        return True


class LocalModelProvider(AIProvider):
    """
    Local model provider for offline generation.

    This provider serves as a fallback when other providers are unavailable
    and can be extended to support local AI models.
    """

    def __init__(self, config: Optional[ProviderConfig] = None, model_path: Optional[str] = None) -> None:
        """Initialize local model provider."""
        if config is None:
            config = ProviderConfig(model="local-template")

        super().__init__(config)
        self.model_path = model_path or "/tmp/local_model"  # Default path
        self.model: Optional[Any] = None

    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.config.model or "local-template"

    def generate_text(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generate text using local model or templates."""
        # For now, use template-based generation
        # This can be extended to support actual local models
        content = self._template_generation(prompt)

        return GenerationResponse(
            content=content,
            model="local-template",
            provider=self.provider_name,
            metadata={
                "template_based": True,
                "model_path": self.model_path
            }
        )

    def is_available(self) -> bool:
        """Check if local model is available."""
        return True  # Always available as fallback

    def get_supported_models(self) -> List[str]:
        """Get list of supported local models."""
        return ["local-template"]

    def _template_generation(self, prompt: str) -> str:
        """Template-based generation with improved logic."""
        prompt_lower = prompt.lower()

        # Analyze prompt for diagram type hints
        if any(word in prompt_lower for word in ["sequence", "interaction", "message", "actor"]):
            return """sequenceDiagram
    participant A as User
    participant B as System
    A->>B: Request
    B-->>A: Response"""

        elif any(word in prompt_lower for word in ["class", "object", "inheritance", "method"]):
            return """classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }"""

        elif any(word in prompt_lower for word in ["state", "transition", "status"]):
            return """stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Complete : finish
    Complete --> [*]"""

        elif any(word in prompt_lower for word in ["entity", "relationship", "database", "table"]):
            return """erDiagram
    USER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int user_id FK
        date created
    }
    USER ||--o{ ORDER : places"""

        elif any(word in prompt_lower for word in ["gantt", "timeline", "schedule", "project"]):
            return """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Planning
    Task 1 :a1, 2024-01-01, 30d
    Task 2 :after a1, 20d"""

        else:  # Default to flowchart
            return """flowchart TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Action]
    C -->|No| E[End]
    D --> E"""


class OpenRouterProvider(AIProvider):
    """
    OpenRouter provider for accessing multiple AI models through a unified API.

    OpenRouter provides access to hundreds of AI models from various providers
    through a single endpoint with automatic fallbacks and cost optimization.
    """

    def __init__(self, config: Optional[ProviderConfig] = None, model: str = "openai/gpt-3.5-turbo") -> None:
        """Initialize OpenRouter provider."""
        if config is None:
            config = ProviderConfig(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                model=model
            )
        elif config.base_url is None:
            config.base_url = "https://openrouter.ai/api/v1"
        elif config.model is None:
            config.model = model

        super().__init__(config)

    def generate_text(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generate text using OpenRouter API."""
        try:
            if not self.config.api_key:
                raise AuthenticationError(
                    "OpenRouter API key not provided",
                    provider=self.provider_name
                )

            # Prepare headers
            headers: Dict[str, str] = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": cast(str, kwargs.get("site_url", "https://mermaid-render.dev")),
                "X-Title": cast(str, kwargs.get("site_name", "Mermaid Render")),
            }

            # Add custom headers if provided
            if self.config.custom_headers:
                headers.update(self.config.custom_headers)

            # Prepare messages
            raw_messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
            messages: List[Dict[str, Any]]
            if isinstance(raw_messages, str):
                messages = [{"role": "user", "content": raw_messages}]
            else:
                messages = cast(List[Dict[str, Any]], raw_messages)

            # Prepare request body
            request_body: Dict[str, Any] = {
                "model": self.config.model or "openai/gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
                "stream": kwargs.get("stream", False),
            }

            # Add optional parameters
            if kwargs.get("stop") is not None:
                request_body["stop"] = kwargs["stop"]
            if kwargs.get("seed") is not None:
                request_body["seed"] = kwargs["seed"]
            if kwargs.get("top_k") is not None:
                request_body["top_k"] = kwargs["top_k"]
            if kwargs.get("repetition_penalty") is not None:
                request_body["repetition_penalty"] = kwargs["repetition_penalty"]

            # OpenRouter-specific parameters
            if kwargs.get("models"):  # Model routing
                request_body["models"] = kwargs["models"]
            if kwargs.get("route"):
                request_body["route"] = kwargs["route"]
            if kwargs.get("provider_preferences"):
                request_body["provider"] = kwargs["provider_preferences"]
            if kwargs.get("transforms"):
                request_body["transforms"] = kwargs["transforms"]

            # Make API call with retry logic
            base = self.config.base_url or "https://openrouter.ai/api/v1"
            url = urljoin(base, "/chat/completions")

            for attempt in range(self.config.max_retries + 1):
                try:
                    response = requests.post(
                        url,
                        headers=headers,
                        json=request_body,
                        timeout=self.config.timeout
                    )

                    # Handle HTTP errors
                    if response.status_code != 200:
                        self._handle_http_error(response)

                    # Parse response
                    response_data = response.json()

                    if not response_data.get("choices"):
                        raise ProviderError(
                            "No choices in response",
                            provider=self.provider_name
                        )

                    choice = response_data["choices"][0]
                    content = choice.get("message", {}).get("content", "")

                    return GenerationResponse(
                        content=content,
                        model=response_data.get("model"),
                        usage=response_data.get("usage"),
                        provider=self.provider_name,
                        metadata={
                            "finish_reason": choice.get("finish_reason"),
                            "response_id": response_data.get("id"),
                            "created": response_data.get("created"),
                            "system_fingerprint": response_data.get("system_fingerprint"),
                        }
                    )

                except requests.exceptions.Timeout:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request timeout, retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise ProviderError(
                        "Request timeout",
                        provider=self.provider_name,
                        error_code="timeout"
                    )

                except requests.exceptions.RequestException as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request error, retrying in {wait_time}s: {e}")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise ProviderError(
                        f"Request error: {e}",
                        provider=self.provider_name
                    )

            # This should never be reached due to the loop structure, but add for safety
            raise ProviderError("Max retries exceeded", provider=self.provider_name)

        except (AuthenticationError, RateLimitError, ModelNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenRouter provider: {e}")
            return self._get_fallback_response(prompt)

    def is_available(self) -> bool:
        """Check if OpenRouter is available."""
        return self.config.api_key is not None

    def get_supported_models(self) -> List[str]:
        """
        Get list of popular supported OpenRouter models.

        Note: OpenRouter supports hundreds of models. This returns a subset
        of popular ones. Use the list_models() method for a complete list.
        """
        return [
            # OpenAI models
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",

            # Anthropic models
            "anthropic/claude-3-5-sonnet",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",

            # Google models
            "google/gemini-pro",
            "google/gemini-pro-vision",

            # Meta models
            "meta-llama/llama-3.1-405b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct",

            # Mistral models
            "mistralai/mistral-large",
            "mistralai/mistral-medium",
            "mistralai/mistral-small",

            # Other popular models
            "cohere/command-r-plus",
            "perplexity/llama-3.1-sonar-large-128k-online",
        ]

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Get complete list of available models from OpenRouter API.

        Returns:
            List of model dictionaries with details
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
            }

            base = self.config.base_url or "https://openrouter.ai/api/v1"
            url = urljoin(base, "/models")
            response = requests.get(url, headers=headers, timeout=self.config.timeout)

            if response.status_code != 200:
                self._handle_http_error(response)

            data = response.json().get("data", [])
            if isinstance(data, list):
                return cast(List[Dict[str, Any]], data)
            return []

        except Exception as e:
            logger.error(f"Failed to fetch models from OpenRouter: {e}")
            return []

    def validate_config(self) -> bool:
        """Validate OpenRouter configuration."""
        super().validate_config()

        if not self.config.base_url:
            raise ProviderError(
                "Base URL is required for OpenRouter",
                provider=self.provider_name
            )

        return True


@dataclass
class CustomProviderConfig:
    """Configuration for custom AI providers."""

    name: str
    base_url: str
    api_key: Optional[str] = None
    auth_type: str = "bearer"  # bearer, api_key, basic, custom, none
    auth_header: str = "Authorization"
    auth_prefix: str = "Bearer"
    request_format: str = "openai"  # openai, anthropic, custom
    response_format: str = "openai"  # openai, anthropic, custom
    timeout: int = 30
    max_retries: int = 3
    custom_headers: Optional[Dict[str, str]] = None
    model_mapping: Optional[Dict[str, str]] = None
    parameter_mapping: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.name:
            raise ValueError("Provider name is required")
        if not self.base_url:
            raise ValueError("Base URL is required")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


class CustomProvider(AIProvider):
    """
    Flexible custom provider that can adapt to various AI API formats.

    This provider allows users to integrate with any AI API by configuring
    the request/response format, authentication, and parameter mappings.
    """

    def __init__(self, custom_config: CustomProviderConfig) -> None:
        """Initialize custom provider with specific configuration."""
        # Convert to standard ProviderConfig
        config = ProviderConfig(
            api_key=custom_config.api_key,
            base_url=custom_config.base_url,
            timeout=custom_config.timeout,
            max_retries=custom_config.max_retries,
            custom_headers=custom_config.custom_headers,
        )

        super().__init__(config)
        self.custom_config = custom_config
        self.provider_name = custom_config.name.lower()

    def generate_text(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """Generate text using custom provider API."""
        try:
            # Prepare headers
            headers = self._prepare_headers()

            # Prepare request body based on format
            request_body = self._prepare_request_body(prompt, **kwargs)

            # Make API call with retry logic
            url = self._get_endpoint_url()

            for attempt in range(self.config.max_retries + 1):
                try:
                    response = requests.post(
                        url,
                        headers=headers,
                        json=request_body,
                        timeout=self.config.timeout
                    )

                    # Handle HTTP errors
                    if response.status_code != 200:
                        self._handle_http_error(response)

                    # Parse response based on format
                    return self._parse_response(response.json())

                except requests.exceptions.Timeout:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request timeout, retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise ProviderError(
                        "Request timeout",
                        provider=self.provider_name,
                        error_code="timeout"
                    )

                except requests.exceptions.RequestException as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request error, retrying in {wait_time}s: {e}")
                        import time
                        time.sleep(wait_time)
                        continue
                    raise ProviderError(
                        f"Request error: {e}",
                        provider=self.provider_name
                    )

            # This should never be reached due to the loop structure, but add for safety
            raise ProviderError("Max retries exceeded", provider=self.provider_name)

        except (AuthenticationError, RateLimitError, ModelNotFoundError):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in custom provider {self.provider_name}: {e}")
            return self._get_fallback_response(prompt)

    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare request headers based on auth configuration."""
        headers: Dict[str, str] = {"Content-Type": "application/json"}

        # Add authentication
        if self.custom_config.auth_type == "bearer" and self.config.api_key:
            headers[self.custom_config.auth_header] = f"{self.custom_config.auth_prefix} {self.config.api_key}"
        elif self.custom_config.auth_type == "api_key" and self.config.api_key:
            headers[self.custom_config.auth_header] = self.config.api_key
        elif self.custom_config.auth_type == "basic" and self.config.api_key:
            import base64
            encoded = base64.b64encode(f":{self.config.api_key}".encode()).decode()
            headers[self.custom_config.auth_header] = f"Basic {encoded}"
        elif self.custom_config.auth_type == "none":
            pass  # No auth header

        # Add custom headers
        if self.config.custom_headers:
            headers.update(self.config.custom_headers)

        return headers

    def _prepare_request_body(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Prepare request body based on format configuration."""
        # Prepare messages
        raw_messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
        if isinstance(raw_messages, str):
            messages: List[Dict[str, Any]] = [{"role": "user", "content": raw_messages}]
        else:
            messages = cast(List[Dict[str, Any]], raw_messages)

        if self.custom_config.request_format == "openai":
            return self._prepare_openai_request(messages, **kwargs)
        elif self.custom_config.request_format == "anthropic":
            return self._prepare_anthropic_request(messages, **kwargs)
        else:
            return self._prepare_custom_request(messages, **kwargs)

    def _prepare_openai_request(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Prepare OpenAI-format request."""
        request_body: Dict[str, Any] = {
            "model": self._map_model(cast(str, kwargs.get("model", "default"))),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "stream": kwargs.get("stream", False),
        }

        # Add optional parameters
        if kwargs.get("stop") is not None:
            request_body["stop"] = kwargs["stop"]
        if kwargs.get("seed") is not None:
            request_body["seed"] = kwargs["seed"]

        return self._map_parameters(request_body)

    def _prepare_anthropic_request(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Prepare Anthropic-format request."""
        request_body: Dict[str, Any] = {
            "model": self._map_model(cast(str, kwargs.get("model", "default"))),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": kwargs.get("stream", False),
        }

        # Add optional parameters
        if kwargs.get("stop") is not None:
            request_body["stop_sequences"] = kwargs["stop"]

        return self._map_parameters(request_body)

    def _prepare_custom_request(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Prepare custom format request - override in subclasses."""
        # Default to OpenAI format for custom providers
        return self._prepare_openai_request(messages, **kwargs)

    def _map_model(self, model: str) -> str:
        """Map model name using configuration."""
        if self.custom_config.model_mapping:
            return self.custom_config.model_mapping.get(model, model)
        return model

    def _map_parameters(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Map parameter names using configuration."""
        if not self.custom_config.parameter_mapping:
            return request_body

        mapped_body: Dict[str, Any] = {}
        for key, value in request_body.items():
            mapped_key = self.custom_config.parameter_mapping.get(key, key)
            mapped_body[mapped_key] = value

        return mapped_body

    def _get_endpoint_url(self) -> str:
        """Get the API endpoint URL."""
        base_url = (self.config.base_url or "").rstrip('/')
        if not base_url:
            raise ProviderError("Base URL missing", provider=self.provider_name)

        if self.custom_config.request_format == "openai":
            return f"{base_url}/chat/completions"
        elif self.custom_config.request_format == "anthropic":
            return f"{base_url}/messages"
        else:
            # For custom format, assume the base_url is the complete endpoint
            return base_url

    def _parse_response(self, response_data: Dict[str, Any]) -> GenerationResponse:
        """Parse response based on format configuration."""
        if self.custom_config.response_format == "openai":
            return self._parse_openai_response(response_data)
        elif self.custom_config.response_format == "anthropic":
            return self._parse_anthropic_response(response_data)
        else:
            return self._parse_custom_response(response_data)

    def _parse_openai_response(self, response_data: Dict[str, Any]) -> GenerationResponse:
        """Parse OpenAI-format response."""
        if not response_data.get("choices"):
            raise ProviderError(
                "No choices in response",
                provider=self.provider_name
            )

        choice = response_data["choices"][0]
        content = choice.get("message", {}).get("content", "")

        return GenerationResponse(
            content=content,
            model=response_data.get("model"),
            usage=response_data.get("usage"),
            provider=self.provider_name,
            metadata={
                "finish_reason": choice.get("finish_reason"),
                "response_id": response_data.get("id"),
                "created": response_data.get("created"),
            }
        )

    def _parse_anthropic_response(self, response_data: Dict[str, Any]) -> GenerationResponse:
        """Parse Anthropic-format response."""
        content = ""
        if response_data.get("content"):
            for block in response_data["content"]:
                if isinstance(block, dict) and block.get("type") == "text":
                    content += block.get("text", "")
                elif isinstance(block, str):
                    content += block

        return GenerationResponse(
            content=content,
            model=response_data.get("model"),
            usage=response_data.get("usage"),
            provider=self.provider_name,
            metadata={
                "finish_reason": response_data.get("stop_reason"),
                "response_id": response_data.get("id"),
            }
        )

    def _parse_custom_response(self, response_data: Dict[str, Any]) -> GenerationResponse:
        """Parse custom format response - override in subclasses."""
        # Default to trying OpenAI format first, then simple text extraction
        try:
            return self._parse_openai_response(response_data)
        except Exception:
            # Fallback: try to extract text from common fields
            content = (
                response_data.get("text") or
                response_data.get("content") or
                response_data.get("output") or
                response_data.get("response") or
                str(response_data)
            )

            return GenerationResponse(
                content=content,
                provider=self.provider_name,
                metadata={"raw_response": response_data}
            )

    def is_available(self) -> bool:
        """Check if custom provider is available."""
        return (
            self.config.base_url is not None and
            (self.config.api_key is not None or self.custom_config.auth_type == "none")
        )

    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        if self.custom_config.model_mapping:
            return list(self.custom_config.model_mapping.keys())
        return ["default"]

    def validate_config(self) -> bool:
        """Validate custom provider configuration."""
        if not self.custom_config.base_url:
            raise ProviderError(
                "Base URL is required for custom provider",
                provider=self.provider_name
            )

        if self.custom_config.auth_type != "none" and not self.config.api_key:
            raise AuthenticationError(
                "API key is required for this authentication type",
                provider=self.provider_name
            )

        return True


class ProviderFactory:
    """Factory for creating AI providers."""

    _providers: Dict[str, Any] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "openrouter": OpenRouterProvider,
        "local": LocalModelProvider,
        "custom": CustomProvider,
    }

    @classmethod
    def create_provider(
        cls,
        provider_type: str,
        config: Optional[Union[ProviderConfig, CustomProviderConfig]] = None,
        **kwargs: Any
    ) -> AIProvider:
        """
        Create an AI provider instance.

        Args:
            provider_type: Type of provider (openai, anthropic, openrouter, local, custom)
            config: Provider configuration
            **kwargs: Additional arguments for provider initialization

        Returns:
            AIProvider instance

        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = provider_type.lower()

        if provider_type not in cls._providers:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        provider_class = cls._providers[provider_type]

        if provider_type == "custom":
            if not isinstance(config, CustomProviderConfig):
                raise ValueError("CustomProviderConfig required for custom provider")
            return cast(AIProvider, provider_class(config))
        else:
            if isinstance(config, CustomProviderConfig):
                raise ValueError(
                    f"ProviderConfig required for {provider_type} provider")
            return cast(AIProvider, provider_class(config, **kwargs))

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """Register a new provider type."""
        if not issubclass(provider_class, AIProvider):
            raise ValueError("Provider class must inherit from AIProvider")
        cls._providers[name.lower()] = provider_class

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider types."""
        return list(cls._providers.keys())


class ProviderManager:
    """Manager for handling multiple AI providers with fallback support."""

    def __init__(self, providers: Optional[List[AIProvider]] = None) -> None:
        """Initialize provider manager."""
        self.providers: List[AIProvider] = providers or []
        self.primary_provider: Optional[AIProvider] = None

        if self.providers:
            self.primary_provider = self.providers[0]

    def add_provider(self, provider: AIProvider, primary: bool = False) -> None:
        """Add a provider to the manager."""
        if primary or not self.providers:
            self.providers.insert(0, provider)
            self.primary_provider = provider
        else:
            self.providers.append(provider)

    def remove_provider(self, provider: AIProvider) -> None:
        """Remove a provider from the manager."""
        if provider in self.providers:
            self.providers.remove(provider)
            if self.primary_provider == provider:
                self.primary_provider = self.providers[0] if self.providers else None

    def generate_text(self, prompt: str, **kwargs: Any) -> GenerationResponse:
        """
        Generate text using providers with automatic fallback.

        Tries providers in order until one succeeds or all fail.
        """
        if not self.providers:
            raise ProviderError("No providers available")

        last_error: Optional[Exception] = None

        for provider in self.providers:
            if not provider.is_available():
                logger.debug(
                    f"Provider {provider.provider_name} not available, skipping")
                continue

            try:
                logger.debug(f"Trying provider: {provider.provider_name}")
                response = provider.generate_text(prompt, **kwargs)
                logger.debug(
                    f"Successfully generated text with {provider.provider_name}")
                return response

            except (AuthenticationError, ModelNotFoundError) as e:
                logger.warning(f"Provider {provider.provider_name} failed: {e}")
                last_error = e
                continue

            except (RateLimitError, ProviderError) as e:
                logger.warning(f"Provider {provider.provider_name} failed: {e}")
                last_error = e
                continue

            except Exception as e:
                logger.error(
                    f"Unexpected error with provider {provider.provider_name}: {e}")
                last_error = e
                continue

        # All providers failed
        if last_error:
            raise last_error
        else:
            raise ProviderError("All providers failed or unavailable")

    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available providers."""
        return [p for p in self.providers if p.is_available()]

    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {p.provider_name: p.is_available() for p in self.providers}


def create_default_provider_manager() -> ProviderManager:
    """Create a default provider manager with common providers."""
    manager = ProviderManager()

    # Try to add providers based on available API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            provider = ProviderFactory.create_provider(
                "openai",
                ProviderConfig(api_key=openai_key)
            )
            manager.add_provider(provider)
        except Exception as e:
            logger.debug(f"Failed to create OpenAI provider: {e}")

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            provider = ProviderFactory.create_provider(
                "anthropic",
                ProviderConfig(api_key=anthropic_key)
            )
            manager.add_provider(provider)
        except Exception as e:
            logger.debug(f"Failed to create Anthropic provider: {e}")

    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            provider = ProviderFactory.create_provider(
                "openrouter",
                ProviderConfig(api_key=openrouter_key)
            )
            manager.add_provider(provider)
        except Exception as e:
            logger.debug(f"Failed to create OpenRouter provider: {e}")

    # Always add local provider as fallback
    try:
        local_provider = ProviderFactory.create_provider("local")
        manager.add_provider(local_provider)
    except Exception as e:
        logger.debug(f"Failed to create local provider: {e}")

    return manager
