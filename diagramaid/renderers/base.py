"""
Base renderer interface for the Mermaid Render library.

This module defines the abstract base class and interfaces that all renderers
must implement to be part of the plugin-based rendering system.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RendererCapability(Enum):
    """Enumeration of renderer capabilities."""

    CACHING = "caching"
    VALIDATION = "validation"
    BATCH_PROCESSING = "batch_processing"
    THEME_SUPPORT = "theme_support"
    CUSTOM_CONFIG = "custom_config"
    FALLBACK_SUPPORT = "fallback_support"
    LOCAL_RENDERING = "local_rendering"
    REMOTE_RENDERING = "remote_rendering"


class RendererPriority(Enum):
    """Enumeration of renderer priority levels."""

    HIGHEST = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    LOWEST = 5


@dataclass
class RendererInfo:
    """Information about a renderer."""

    name: str
    description: str
    supported_formats: set[str]
    capabilities: set[RendererCapability]
    priority: RendererPriority = RendererPriority.NORMAL
    version: str = "1.0.0"
    author: str = "Unknown"
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] | None = None


@dataclass
class RenderResult:
    """Result of a rendering operation."""

    content: str | bytes
    format: str
    renderer_name: str
    render_time: float
    success: bool = True
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseRenderer(ABC):
    """
    Abstract base class for all Mermaid renderers.

    This class defines the common interface that all renderers must implement
    to be part of the plugin-based rendering system. It provides a standardized
    way to render Mermaid diagrams while allowing for renderer-specific
    optimizations and capabilities.

    Attributes:
        logger (logging.Logger): Logger instance for the renderer
        _info (RendererInfo): Renderer information and capabilities
    """

    def __init__(self, **config: Any) -> None:
        """
        Initialize the renderer.

        Args:
            **config: Renderer-specific configuration options
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._config = config
        self._info: RendererInfo | None = None

    @abstractmethod
    def get_info(self) -> RendererInfo:
        """
        Get renderer information and capabilities.

        Returns:
            RendererInfo object describing the renderer
        """
        pass

    @abstractmethod
    def render(
        self,
        mermaid_code: str,
        format: str,
        theme: str | None = None,
        config: dict[str, Any] | None = None,
        **options: Any,
    ) -> RenderResult:
        """
        Render Mermaid code to the specified format.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format (svg, png, pdf, etc.)
            theme: Optional theme name
            config: Optional configuration dictionary
            **options: Additional rendering options

        Returns:
            RenderResult containing the rendered content and metadata

        Raises:
            RenderingError: If rendering fails
            UnsupportedFormatError: If format is not supported
        """
        pass

    def supports_format(self, format: str) -> bool:
        """
        Check if renderer supports the specified format.

        Args:
            format: Output format to check

        Returns:
            True if format is supported, False otherwise
        """
        info = self.get_info()
        return format.lower() in info.supported_formats

    def has_capability(self, capability: RendererCapability) -> bool:
        """
        Check if renderer has the specified capability.

        Args:
            capability: Capability to check

        Returns:
            True if capability is supported, False otherwise
        """
        info = self.get_info()
        return capability in info.capabilities

    def get_supported_formats(self) -> set[str]:
        """
        Get set of supported output formats.

        Returns:
            Set of supported format strings
        """
        info = self.get_info()
        return info.supported_formats.copy()

    def get_capabilities(self) -> set[RendererCapability]:
        """
        Get set of renderer capabilities.

        Returns:
            Set of supported capabilities
        """
        info = self.get_info()
        return info.capabilities.copy()

    def validate_config(self, config: dict[str, Any]) -> bool:
        """
        Validate renderer-specific configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Default implementation - subclasses can override
        return True

    def get_config_schema(self) -> dict[str, Any] | None:
        """
        Get JSON schema for renderer configuration.

        Returns:
            JSON schema dictionary or None if no schema is defined
        """
        info = self.get_info()
        return info.config_schema

    def cleanup(self) -> None:  # noqa: B027
        """
        Clean up renderer resources.

        This method should be called when the renderer is no longer needed
        to free up any resources (connections, temporary files, etc.).
        """
        # Default implementation - subclasses can override
        pass

    def __enter__(self) -> "BaseRenderer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.cleanup()


class RendererError(Exception):
    """Base exception for renderer-related errors."""

    def __init__(
        self,
        message: str,
        renderer_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.renderer_name = renderer_name
        self.context = context or {}


class RendererNotAvailableError(RendererError):
    """Raised when a renderer is not available."""

    pass


class RendererConfigurationError(RendererError):
    """Raised when renderer configuration is invalid."""

    pass
