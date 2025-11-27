"""
MCP tools package for mermaid-render.

This package contains all MCP tool implementations organized by functionality:
- base: Common utilities, error handling, response formatting
- params: Parameter models and enums for tool validation
- core: Core rendering and validation tools
- ai: AI-powered diagram generation and analysis tools
- templates: Template management tools
- config: Configuration and system management tools
- analytics: Diagram analysis and comparison tools
- transformations: Style and structure transformation tools
- operations: Batch operations, file operations, format conversion
"""

from typing import Any

from .ai import (
    analyze_diagram,
    generate_diagram_from_text,
    get_diagram_suggestions,
    optimize_diagram,
)
from .analytics import compare_diagrams, extract_diagram_elements
from .base import (
    _FASTMCP_AVAILABLE,
    ErrorCategory,
    create_error_response,
    create_success_response,
    measure_performance,
)
from .config import (
    get_configuration,
    get_system_information,
    manage_cache_operations,
    update_configuration,
)
from .core import list_themes, render_diagram, validate_diagram
from .helpers import (
    _assess_template_complexity,
    _calculate_complexity_score,
    _calculate_quality_score,
    _detect_diagram_type,
    _extract_parameter_schema,
    _generate_template_usage_example,
    _generate_template_usage_instructions,
    _get_common_patterns,
    _get_config_description,
    _get_diagram_best_practices,
    _get_diagram_example,
    _get_quick_reference_guide,
    _get_section_keys,
    _get_syntax_guide,
    _validate_config_value,
)
from .operations import (
    batch_render_diagrams,
    convert_diagram_format,
    export_to_markdown,
    get_diagram_examples,
    list_diagram_types,
    merge_diagrams,
    save_diagram_to_file,
)
from .params import (
    AnalyzeDiagramParams,
    BatchRenderParams,
    CacheManagementParams,
    ConfigurationParams,
    CreateFromTemplateParams,
    DiagramTypeParams,
    FileOperationParams,
    GenerateDiagramParams,
    ListThemesParams,
    OptimizeDiagramParams,
    RenderDiagramParams,
    TemplateManagementParams,
    ValidateDiagramParams,
)
from .templates import (
    create_custom_template,
    create_from_template,
    get_template_details,
    list_available_templates,
)
from .transformations import generate_diagram_variants, transform_diagram_style


def register_all_tools(mcp: Any) -> None:
    """
    Register all MCP tools with the FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    # Core rendering tools
    mcp.tool(
        name="render_diagram",
        description="Render a Mermaid diagram to the specified format (SVG, PNG, PDF)",
    )(render_diagram)

    mcp.tool(
        name="validate_diagram",
        description="Validate Mermaid diagram syntax and structure",
    )(validate_diagram)

    mcp.tool(
        name="list_themes",
        description="List available Mermaid themes and their descriptions",
    )(list_themes)

    # AI-powered tools
    mcp.tool(
        name="generate_diagram_from_text",
        description="Generate a Mermaid diagram from natural language description using AI",
        tags={"ai", "generation"},
    )(generate_diagram_from_text)

    mcp.tool(
        name="optimize_diagram",
        description="Optimize a Mermaid diagram for better readability and performance using AI",
        tags={"ai", "optimization"},
    )(optimize_diagram)

    mcp.tool(
        name="analyze_diagram",
        description="Analyze a Mermaid diagram and provide metrics, insights, and quality assessment",
        tags={"ai", "analysis"},
    )(analyze_diagram)

    mcp.tool(
        name="get_diagram_suggestions",
        description="Get AI-powered suggestions for improving a Mermaid diagram",
        tags={"ai", "suggestions"},
    )(get_diagram_suggestions)

    # Template tools
    mcp.tool(
        name="create_from_template",
        description="Create a Mermaid diagram from a template with provided data",
        tags={"templates", "generation"},
    )(create_from_template)

    # Configuration management tools
    mcp.tool(
        name="get_configuration",
        description="Get current configuration settings with optional filtering by key or section",
        tags={"configuration", "settings"},
    )(get_configuration)

    mcp.tool(
        name="update_configuration",
        description="Update configuration settings with validation and error handling",
        tags={"configuration", "settings", "management"},
    )(update_configuration)

    # Template management tools
    mcp.tool(
        name="list_available_templates",
        description="List all available diagram templates with filtering and categorization",
        tags={"templates", "management"},
    )(list_available_templates)

    # Additional template and diagram tools
    mcp.tool(
        name="get_template_details",
        description="Get detailed information about a specific template including parameters and examples",
        tags={"templates", "information"},
    )(get_template_details)

    mcp.tool(
        name="create_custom_template",
        description="Create a new custom template with validation and parameter schema",
        tags={"templates", "creation", "management"},
    )(create_custom_template)

    # Diagram type information tools
    mcp.tool(
        name="list_diagram_types",
        description="List all supported diagram types with descriptions and capabilities",
        tags={"diagrams", "types", "information"},
    )(list_diagram_types)

    mcp.tool(
        name="get_diagram_examples",
        description="Get example code and documentation for specific diagram types",
        tags={"diagrams", "examples", "documentation"},
    )(get_diagram_examples)

    # System information tools
    mcp.tool(
        name="get_system_information",
        description="Get system capabilities, version information, and available features",
        tags={"system", "information", "capabilities"},
    )(get_system_information)

    # File operation tools
    mcp.tool(
        name="save_diagram_to_file",
        description="Save rendered diagram content to a file with path validation and error handling",
        tags={"files", "save", "export"},
    )(save_diagram_to_file)

    # Batch operation tools
    mcp.tool(
        name="batch_render_diagrams",
        description="Render multiple diagrams efficiently with parallel processing and progress tracking",
        tags={"batch", "rendering", "performance"},
    )(batch_render_diagrams)

    # Cache management tools
    mcp.tool(
        name="manage_cache_operations",
        description="Manage cache operations including clear, stats, and cleanup with detailed reporting",
        tags={"cache", "management", "performance"},
    )(manage_cache_operations)

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Registered all MCP tools")


def register_extended_tools(mcp: Any) -> None:
    """
    Register extended MCP tools with the FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    # Format conversion tool
    mcp.tool(
        name="convert_diagram_format",
        description="Convert a Mermaid diagram between different output formats (SVG, PNG, PDF)",
        tags={"conversion", "format", "rendering"},
    )(convert_diagram_format)

    # Diagram merging tool
    mcp.tool(
        name="merge_diagrams",
        description="Merge multiple Mermaid diagrams into a single diagram using various strategies",
        tags={"merge", "combine", "composition"},
    )(merge_diagrams)

    # Element extraction tool
    mcp.tool(
        name="extract_diagram_elements",
        description="Extract nodes, edges, and other elements from a Mermaid diagram",
        tags={"extraction", "analysis", "parsing"},
    )(extract_diagram_elements)

    # Diagram comparison tool
    mcp.tool(
        name="compare_diagrams",
        description="Compare two Mermaid diagrams and identify structural differences",
        tags={"comparison", "diff", "analysis"},
    )(compare_diagrams)

    # Markdown export tool
    mcp.tool(
        name="export_to_markdown",
        description="Export a Mermaid diagram with documentation to Markdown format",
        tags={"export", "markdown", "documentation"},
    )(export_to_markdown)

    # Style transformation tool
    mcp.tool(
        name="transform_diagram_style",
        description="Transform diagram styling using presets or custom styles",
        tags={"style", "transform", "theming"},
    )(transform_diagram_style)

    # Variant generation tool
    mcp.tool(
        name="generate_diagram_variants",
        description="Generate multiple variants of a diagram with different layouts or styles",
        tags={"variants", "generation", "layout"},
    )(generate_diagram_variants)

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Registered extended MCP tools")


__all__ = [
    # Base utilities
    "ErrorCategory",
    "create_error_response",
    "create_success_response",
    "measure_performance",
    # Core tools
    "render_diagram",
    "validate_diagram",
    "list_themes",
    # AI tools
    "generate_diagram_from_text",
    "optimize_diagram",
    "analyze_diagram",
    "get_diagram_suggestions",
    # Template tools
    "create_from_template",
    "list_available_templates",
    "get_template_details",
    "create_custom_template",
    # Config tools
    "get_configuration",
    "update_configuration",
    "get_system_information",
    "manage_cache_operations",
    # Analytics tools
    "extract_diagram_elements",
    "compare_diagrams",
    # Transformation tools
    "transform_diagram_style",
    "generate_diagram_variants",
    # Operation tools
    "convert_diagram_format",
    "merge_diagrams",
    "export_to_markdown",
    "save_diagram_to_file",
    "batch_render_diagrams",
    "list_diagram_types",
    "get_diagram_examples",
    # Registration functions
    "register_all_tools",
    "register_extended_tools",
    # Helper for detecting diagram type (used by extended_tools)
    "_detect_diagram_type",
]
