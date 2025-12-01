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
    >>> from diagramaid.interactive import DiagramBuilder, start_server
    >>>
    >>> # Start interactive server
    >>> builder = DiagramBuilder()
    >>> start_server(builder, host="localhost", port=8080)
    >>>
    >>> # Access at http://localhost:8080
    >>> # Build diagrams visually and export code
"""

# Core builder class and sub-components - from new builder package
from .builder import (
    ClassDiagramGenerator,
    CodeGenerator,
    ConnectionManager,
    DiagramBuilder,
    DiagramParser,
    DiagramSerializer,
    ElementManager,
    EventManager,
    FlowchartGenerator,
    FlowchartParser,
    SequenceDiagramGenerator,
)
from .export import ExportFormat, ExportManager
from .models import (
    DiagramConnection,
    DiagramElement,
    DiagramType,
    ElementType,
    Position,
    Size,
)
from .routes import (
    create_elements_router,
    create_preview_router,
    create_sessions_router,
)
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
from .utils import (
    create_interactive_session,
    export_diagram_code,
    get_available_components,
    load_diagram_from_code,
    validate_diagram_live,
)
from .websocket import (
    BroadcastService,
    DiagramSession,
    MessageDispatcher,
    SessionManager,
    WebSocketHandler,
)

__all__ = [
    # Core classes
    "DiagramBuilder",
    "DiagramElement",
    "DiagramConnection",
    # Builder sub-components
    "ElementManager",
    "ConnectionManager",
    "EventManager",
    "DiagramSerializer",
    "CodeGenerator",
    "FlowchartGenerator",
    "SequenceDiagramGenerator",
    "ClassDiagramGenerator",
    "DiagramParser",
    "FlowchartParser",
    # WebSocket sub-components
    "SessionManager",
    "BroadcastService",
    "MessageDispatcher",
    # Model types
    "DiagramType",
    "ElementType",
    "Position",
    "Size",
    # Server components
    "InteractiveServer",
    "start_server",
    "create_app",
    "WebSocketHandler",
    "DiagramSession",
    # Route factories
    "create_sessions_router",
    "create_elements_router",
    "create_preview_router",
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
    # Utilities
    "create_interactive_session",
    "load_diagram_from_code",
    "export_diagram_code",
    "validate_diagram_live",
    "get_available_components",
]
