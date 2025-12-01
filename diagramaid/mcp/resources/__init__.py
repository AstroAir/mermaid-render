"""
MCP resources package for diagramaid.

This package provides MCP resource implementations organized into modules:
- base: Base utilities, ResourceError, and FastMCP availability check
- themes: Theme-related resources
- templates: Template-related resources
- config: Configuration resources
- docs: Documentation resources
- extended: Extended resources (syntax, best practices, capabilities, etc.)
"""

from typing import Any

from .base import _FASTMCP_AVAILABLE, ResourceError
from .config import get_config_schema, get_default_config
from .docs import get_diagram_examples, get_diagram_types_docs
from .extended import (
    get_best_practices,
    get_capabilities,
    get_changelog,
    get_shortcuts_reference,
    get_syntax_reference,
)
from .templates import get_template_details, get_templates_resource
from .themes import get_theme_details, get_themes_resource


def register_all_resources(mcp: Any) -> None:
    """
    Register all MCP resources with the FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    # Theme resources
    mcp.resource(
        uri="mermaid://themes",
        name="Available Themes",
        description="List of all available Mermaid themes with descriptions",
        mime_type="application/json",
    )(get_themes_resource)

    mcp.resource(
        uri="mermaid://themes/{theme_name}",
        name="Theme Details",
        description="Detailed information about a specific theme",
        mime_type="application/json",
    )(get_theme_details)

    # Template resources
    mcp.resource(
        uri="mermaid://templates",
        name="Available Templates",
        description="List of all available diagram templates",
        mime_type="application/json",
    )(get_templates_resource)

    mcp.resource(
        uri="mermaid://templates/{template_name}",
        name="Template Details",
        description="Detailed information about a specific template",
        mime_type="application/json",
    )(get_template_details)

    # Configuration resources
    mcp.resource(
        uri="mermaid://config/schema",
        name="Configuration Schema",
        description="JSON schema for diagramaid configuration",
        mime_type="application/json",
    )(get_config_schema)

    mcp.resource(
        uri="mermaid://config/defaults",
        name="Default Configuration",
        description="Default configuration values",
        mime_type="application/json",
    )(get_default_config)

    # Documentation resources
    mcp.resource(
        uri="mermaid://docs/diagram-types",
        name="Diagram Types",
        description="Documentation for all supported diagram types",
        mime_type="application/json",
    )(get_diagram_types_docs)

    mcp.resource(
        uri="mermaid://examples/{diagram_type}",
        name="Diagram Examples",
        description="Example diagrams for each type",
        mime_type="application/json",
    )(get_diagram_examples)


def register_extended_resources(mcp: Any) -> None:
    """
    Register extended MCP resources with the FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    # Syntax reference resource
    mcp.resource(
        uri="mermaid://syntax/{diagram_type}",
        name="Syntax Reference",
        description="Detailed syntax reference for specific diagram types",
        mime_type="application/json",
    )(get_syntax_reference)

    # Best practices resource
    mcp.resource(
        uri="mermaid://best-practices",
        name="Best Practices",
        description="Best practices guide for creating Mermaid diagrams",
        mime_type="application/json",
    )(get_best_practices)

    # Capabilities resource
    mcp.resource(
        uri="mermaid://capabilities",
        name="Server Capabilities",
        description="Server capabilities, features, and supported operations",
        mime_type="application/json",
    )(get_capabilities)

    # Changelog resource
    mcp.resource(
        uri="mermaid://changelog",
        name="Changelog",
        description="Version history and changelog",
        mime_type="application/json",
    )(get_changelog)

    # Shortcuts reference resource
    mcp.resource(
        uri="mermaid://shortcuts",
        name="Quick Reference",
        description="Quick reference for common diagram patterns and shortcuts",
        mime_type="application/json",
    )(get_shortcuts_reference)


__all__ = [
    # Registration functions
    "register_all_resources",
    "register_extended_resources",
    # Base
    "ResourceError",
    # Theme resources
    "get_themes_resource",
    "get_theme_details",
    # Template resources
    "get_templates_resource",
    "get_template_details",
    # Config resources
    "get_config_schema",
    "get_default_config",
    # Documentation resources
    "get_diagram_types_docs",
    "get_diagram_examples",
    # Extended resources
    "get_syntax_reference",
    "get_best_practices",
    "get_capabilities",
    "get_changelog",
    "get_shortcuts_reference",
]
