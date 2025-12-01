"""
Rendering engines for the Mermaid Render library.

This module provides various rendering backends for converting Mermaid diagrams
to different output formats. It includes both the original renderers and the
new plugin-based architecture.
"""

# Original renderers (for backward compatibility)
# Plugin architecture components
from .base import (
    BaseRenderer,
    RendererCapability,
    RendererConfigurationError,
    RendererError,
    RendererInfo,
    RendererNotAvailableError,
    RendererPriority,
    RenderResult,
)
from .config_manager import RendererConfigManager, get_global_config_manager

# Enhanced architecture components
from .error_handler import (
    ErrorContext,
    ErrorDetails,
    ErrorHandler,
    get_global_error_handler,
)
from .graphviz_renderer import GraphvizRenderer
from .manager import RendererManager
from .nodejs_renderer import NodeJSRenderer
from .pdf_renderer import PDFRenderer

# New renderer implementations
from .playwright_renderer import PlaywrightRenderer
from .png_renderer import PNGRenderer
from .registry import RendererRegistry, get_global_registry, register_renderer
from .svg_renderer import SVGRenderer

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
    # New renderers
    "PlaywrightRenderer",
    "NodeJSRenderer",
    "GraphvizRenderer",
    # Plugin architecture components
    "ErrorHandler",
    "ErrorContext",
    "ErrorDetails",
    "get_global_error_handler",
    "RendererConfigManager",
    "get_global_config_manager",
]
