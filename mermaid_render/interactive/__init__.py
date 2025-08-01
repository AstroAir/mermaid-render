"""
Interactive diagram builder for Mermaid Render.

This package provides a web-based interactive interface for building
Mermaid diagrams visually with real-time preview, drag-and-drop functionality,
and live code generation.

Features:
- Visual diagram builder with drag-and-drop interface
- Real-time preview and code generation
- Live syntax validation and error highlighting
- Template-based diagram creation
- Collaborative editing capabilities
- Export to multiple formats
- Integration with existing diagram models

Example:
    >>> from mermaid_render.interactive import DiagramBuilder, start_server
    >>>
    >>> # Start interactive server
    >>> builder = DiagramBuilder()
    >>> start_server(builder, host="localhost", port=8080)
    >>>
    >>> # Access at http://localhost:8080
    >>> # Build diagrams visually and export code
"""

from .builder import DiagramBuilder, DiagramConnection, DiagramElement
from .export import ExportFormat, ExportManager
from .server import InteractiveServer, create_app, start_server
from .templates import InteractiveTemplate, TemplateLibrary
from .ui_components import (
    CodeEditor,
    EdgeComponent,
    NodeComponent,
    PreviewPanel,
    PropertiesPanel,
    ToolboxComponent,
    UIComponent,
)

# Convenience functions
from .utils import (
    create_interactive_session,
    export_diagram_code,
    get_available_components,
    load_diagram_from_code,
    validate_diagram_live,
)
from .validation import LiveValidator, ValidationResult
from .websocket_handler import DiagramSession, WebSocketHandler

__all__ = [
    # Core classes
    "DiagramBuilder",
    "DiagramElement",
    "DiagramConnection",
    # Server components
    "InteractiveServer",
    "start_server",
    "create_app",
    "WebSocketHandler",
    "DiagramSession",
    # UI components
    "UIComponent",
    "NodeComponent",
    "EdgeComponent",
    "ToolboxComponent",
    "PropertiesPanel",
    "CodeEditor",
    "PreviewPanel",
    # Templates and export
    "InteractiveTemplate",
    "TemplateLibrary",
    "ExportManager",
    "ExportFormat",
    # Validation
    "LiveValidator",
    "ValidationResult",
    # Utilities
    "create_interactive_session",
    "load_diagram_from_code",
    "export_diagram_code",
    "validate_diagram_live",
    "get_available_components",
]
