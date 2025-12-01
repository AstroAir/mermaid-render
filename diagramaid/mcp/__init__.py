"""
MCP (Model Context Protocol) server implementation for diagramaid.

This module provides MCP server functionality to expose diagramaid's
capabilities through the Model Context Protocol, allowing AI assistants
and other clients to generate, validate, and manipulate Mermaid diagrams.

The MCP server exposes the following categories of tools:

**Core Tools:**
- render_diagram: Render Mermaid diagrams to SVG/PNG/PDF
- validate_diagram: Validate diagram syntax and structure
- list_themes: List available themes

**AI-Powered Tools:**
- generate_diagram_from_text: Generate diagrams from natural language
- optimize_diagram: Optimize diagram layout and structure
- analyze_diagram: Analyze diagram quality and complexity
- get_diagram_suggestions: Get improvement suggestions

**Template Tools:**
- create_from_template: Create diagrams from templates
- list_available_templates: List available templates
- get_template_details: Get template information
- create_custom_template: Create custom templates

**Extended Tools:**
- convert_diagram_format: Convert between output formats
- merge_diagrams: Merge multiple diagrams
- extract_diagram_elements: Extract nodes and edges
- compare_diagrams: Compare two diagrams
- export_to_markdown: Export with documentation
- transform_diagram_style: Apply style presets
- generate_diagram_variants: Generate layout variants

**Prompts:**
- Generation prompts for all diagram types
- Analysis and optimization prompts
- Documentation and translation prompts

**Resources:**
- Theme and template information
- Syntax references and best practices
- Server capabilities and changelog
"""

from collections.abc import Callable
from typing import Any

try:
    from .server import create_mcp_server, main

    _SERVER_AVAILABLE = True
except ImportError:
    create_mcp_server: Callable[[str, str, str | None], Any] | None = None  # type: ignore[no-redef]
    main: Callable[[], None] | None = None  # type: ignore[no-redef]
    _SERVER_AVAILABLE = False

from .prompts import register_all_prompts, register_extended_prompts
from .resources import register_all_resources, register_extended_resources
from .tools import (
    analyze_diagram,
    compare_diagrams,
    convert_diagram_format,
    create_from_template,
    export_to_markdown,
    extract_diagram_elements,
    generate_diagram_from_text,
    generate_diagram_variants,
    get_diagram_suggestions,
    list_themes,
    merge_diagrams,
    optimize_diagram,
    register_all_tools,
    register_extended_tools,
    render_diagram,
    transform_diagram_style,
    validate_diagram,
)

__all__ = [
    # Core tools
    "render_diagram",
    "validate_diagram",
    "list_themes",
    "generate_diagram_from_text",
    "optimize_diagram",
    "analyze_diagram",
    "get_diagram_suggestions",
    "create_from_template",
    # Extended tools
    "convert_diagram_format",
    "merge_diagrams",
    "extract_diagram_elements",
    "compare_diagrams",
    "export_to_markdown",
    "transform_diagram_style",
    "generate_diagram_variants",
    # Registration functions
    "register_all_tools",
    "register_extended_tools",
    "register_all_prompts",
    "register_extended_prompts",
    "register_all_resources",
    "register_extended_resources",
]

if _SERVER_AVAILABLE:
    __all__.extend(["create_mcp_server", "main"])
