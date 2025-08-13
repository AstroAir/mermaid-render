"""
Base renderer interface for the Mermaid Render library.

This module defines the abstract base class and interfaces that all renderers
must implement to be part of the plugin-based rendering system.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union


class RendererCapability(Enum):
    """Enumeration of renderer capabilities."""

    CACHING = "caching"
    VALIDATION = "validation"
    BATCH_PROCESSING = "batch_processing"
    THEME_SUPPORT = "theme_support"
    CUSTOM_CONFIG = "custom_config"
    PERFORMANCE_METRICS = "performance_metrics"
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
    supported_formats: Set[str]
    capabilities: Set[RendererCapability]
    priority: RendererPriority = RendererPriority.NORMAL
    version: str = "1.0.0"
    author: str = "Unknown"
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None


@dataclass
class RenderResult:
    """Result of a rendering operation."""

    content: Union[str, bytes]
    format: str
    renderer_name: str
    render_time: float
    success: bool = True
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


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
        self._info: Optional[RendererInfo] = None

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
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
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

    def get_supported_formats(self) -> Set[str]:
        """
        Get set of supported output formats.

        Returns:
            Set of supported format strings
        """
        info = self.get_info()
        return info.supported_formats.copy()

    def get_capabilities(self) -> Set[RendererCapability]:
        """
        Get set of renderer capabilities.

        Returns:
            Set of supported capabilities
        """
        info = self.get_info()
        return info.capabilities.copy()

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate renderer-specific configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Default implementation - subclasses can override
        return True

    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get JSON schema for renderer configuration.

        Returns:
            JSON schema dictionary or None if no schema is defined
        """
        info = self.get_info()
        return info.config_schema

    def is_available(self) -> bool:
        """
        Check if renderer is available and ready to use.

        This method should check for required dependencies, network connectivity,
        or any other prerequisites needed for the renderer to function.

        Returns:
            True if renderer is available, False otherwise
        """
        # Default implementation - subclasses should override
        return True

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get detailed health status of the renderer.

        Returns:
            Dictionary with health status information
        """
        return {
            "available": self.is_available(),
            "name": self.get_info().name,
            "supported_formats": list(self.get_supported_formats()),
            "capabilities": [cap.value for cap in self.get_capabilities()],
        }

    def cleanup(self) -> None:
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
        renderer_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
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
