"""
Rendering engines for the Mermaid Render library.

This module provides various rendering backends for converting Mermaid diagrams
to different output formats. It includes both the original renderers and the
new plugin-based architecture.
"""

# Original renderers (for backward compatibility)
from .pdf_renderer import PDFRenderer
from .png_renderer import PNGRenderer
from .svg_renderer import SVGRenderer

# Plugin architecture components
from .base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
    RendererError,
    RendererNotAvailableError,
    RendererConfigurationError,
)
from .registry import RendererRegistry, get_global_registry, register_renderer
from .manager import RendererManager

# Plugin adapters for existing renderers
from .svg_renderer_plugin import SVGRendererPlugin
from .png_renderer_plugin import PNGRendererPlugin
from .pdf_renderer_plugin import PDFRendererPlugin

# New renderer implementations
from .playwright_renderer import PlaywrightRenderer
from .nodejs_renderer import NodeJSRenderer
from .graphviz_renderer import GraphvizRenderer

# Enhanced architecture components
from .error_handler import ErrorHandler, ErrorContext, ErrorDetails, get_global_error_handler
from .validation import InputValidator, ValidationResult, get_global_validator
from .config_manager import RendererConfigManager, get_global_config_manager
from .logging_config import setup_logging, PerformanceLogger, LoggingContext

__all__ = [
    # Original renderers
    "SVGRenderer",
    "PNGRenderer",
    "PDFRenderer",
    # Plugin architecture
    "BaseRenderer",
    "RendererCapability",
    "RendererInfo",
    "RendererPriority",
    "RenderResult",
    "RendererError",
    "RendererNotAvailableError",
    "RendererConfigurationError",
    "RendererRegistry",
    "RendererManager",
    "get_global_registry",
    "register_renderer",
    # Plugin adapters
    "SVGRendererPlugin",
    "PNGRendererPlugin",
    "PDFRendererPlugin",
    # New renderers
    "PlaywrightRenderer",
    "NodeJSRenderer",
    "GraphvizRenderer",
    # Enhanced architecture components
    "ErrorHandler",
    "ErrorContext",
    "ErrorDetails",
    "get_global_error_handler",
    "InputValidator",
    "ValidationResult",
    "get_global_validator",
    "RendererConfigManager",
    "get_global_config_manager",
    "setup_logging",
    "PerformanceLogger",
    "LoggingContext",
]
