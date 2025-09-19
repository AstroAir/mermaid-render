"""
MCP (Model Context Protocol) server implementation for mermaid-render.

This module provides MCP server functionality to expose mermaid-render's
capabilities through the Model Context Protocol, allowing AI assistants
and other clients to generate, validate, and manipulate Mermaid diagrams.

The MCP server exposes the following categories of tools:
- Core rendering tools (render_diagram, validate_diagram)
- AI-powered tools (generate_diagram_from_text, optimize_diagram)
- Template tools (create_from_template, list_templates)
- Configuration tools (list_themes, get_config)
- Analysis tools (analyze_diagram, get_suggestions)
"""

try:
    from .server import create_mcp_server, main
    _SERVER_AVAILABLE = True
except ImportError:
    create_mcp_server = None
    main = None
    _SERVER_AVAILABLE = False

from .tools import (
    render_diagram,
    validate_diagram,
    list_themes,
    generate_diagram_from_text,
    optimize_diagram,
    analyze_diagram,
    get_diagram_suggestions,
    create_from_template,
)

__all__ = [
    "render_diagram",
    "validate_diagram",
    "list_themes",
    "generate_diagram_from_text",
    "optimize_diagram",
    "analyze_diagram",
    "get_diagram_suggestions",
    "create_from_template",
]

if _SERVER_AVAILABLE:
    __all__.extend(["create_mcp_server", "main"])
