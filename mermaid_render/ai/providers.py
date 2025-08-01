"""AI provider implementations for diagram generation."""

from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI API."""
        try:
            import openai

            if not self._client:
                self._client = openai.OpenAI(api_key=self.api_key)

            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
            )

            return response.choices[0].message.content

        except ImportError:
            return self._fallback_generation(prompt)
        except Exception:
            return self._fallback_generation(prompt)

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            import openai

            return self.api_key is not None
        except ImportError:
            return False

    def _fallback_generation(self, prompt: str) -> str:
        """Fallback generation when OpenAI is not available."""
        # Simple template-based generation
        if "flowchart" in prompt.lower():
            return """flowchart TD
    A[Start] --> B[Process]
    B --> C[Decision]
    C -->|Yes| D[Action]
    C -->|No| E[Alternative]
    D --> F[End]
    E --> F"""
        else:
            return "flowchart TD\n    A[Generated Diagram] --> B[End]"


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"
    ):
        self.api_key = api_key
        self.model = model
        self._client = None

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic API."""
        try:
            import anthropic

            if not self._client:
                self._client = anthropic.Anthropic(api_key=self.api_key)

            response = self._client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text

        except ImportError:
            return self._fallback_generation(prompt)
        except Exception:
            return self._fallback_generation(prompt)

    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        try:
            import anthropic

            return self.api_key is not None
        except ImportError:
            return False

    def _fallback_generation(self, prompt: str) -> str:
        """Fallback generation when Anthropic is not available."""
        return OpenAIProvider()._fallback_generation(prompt)


class LocalModelProvider(AIProvider):
    """Local model provider for offline generation."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using local model."""
        # Placeholder for local model implementation
        return self._template_generation(prompt)

    def is_available(self) -> bool:
        """Check if local model is available."""
        return True  # Always available as fallback

    def _template_generation(self, prompt: str) -> str:
        """Template-based generation."""
        prompt_lower = prompt.lower()

        if "sequence" in prompt_lower:
            return """sequenceDiagram
    participant A as User
    participant B as System
    A->>B: Request
    B-->>A: Response"""

        elif "class" in prompt_lower:
            return """classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }"""

        else:  # Default to flowchart
            return """flowchart TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Action]
    C -->|No| E[End]
    D --> E"""
