"""
MCP tools implementation for mermaid-render.

This module contains all the MCP tool implementations that expose
mermaid-render functionality through the Model Context Protocol.
"""

import base64
import logging
from pathlib import Path
from typing import Any

try:
    from fastmcp import Context, FastMCP
    from pydantic import BaseModel, Field

    _FASTMCP_AVAILABLE = True
except ImportError:
    # Allow importing tools for testing without FastMCP
    FastMCP = None
    Context = None
    _FASTMCP_AVAILABLE = False

    # Create fallback classes for when pydantic is not available
    class BaseModel:  # type: ignore[no-redef]
        """Fallback BaseModel when pydantic is not available."""

        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(**kwargs: Any) -> Any:
        """Fallback Field when pydantic is not available."""
        return kwargs.get("default")


from ..core import MermaidConfig, MermaidRenderer
from ..exceptions import ValidationError
from ..validators import MermaidValidator

logger = logging.getLogger(__name__)


# Enhanced error handling and response formatting
class ErrorCategory:
    """Error categories for better error classification."""

    VALIDATION = "ValidationError"
    RENDERING = "RenderingError"
    CONFIGURATION = "ConfigurationError"
    TEMPLATE = "TemplateError"
    FILE_OPERATION = "FileOperationError"
    AI_SERVICE = "AIServiceError"
    SYSTEM = "SystemError"
    NETWORK = "NetworkError"
    CACHE = "CacheError"


def create_success_response(
    data: Any,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
    performance_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized success response."""
    response = {
        "success": True,
        "data": data,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }

    if metadata:
        response["metadata"] = metadata

    if request_id:
        response["request_id"] = request_id

    if performance_metrics:
        response["performance"] = performance_metrics

    return response


def create_error_response(
    error: Exception,
    error_category: str = ErrorCategory.SYSTEM,
    context: dict[str, Any] | None = None,
    request_id: str | None = None,
    suggestions: list[str] | None = None,
) -> dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "error_category": error_category,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }

    if context:
        response["context"] = context

    if request_id:
        response["request_id"] = request_id

    if suggestions:
        response["suggestions"] = suggestions

    return response


def measure_performance(func: Any) -> Any:
    """Decorator to measure function performance."""
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()

            # Add performance metrics to successful responses
            if isinstance(result, dict) and result.get("success"):
                if "performance" not in result:
                    result["performance"] = {}
                result["performance"]["execution_time_ms"] = round(
                    (end_time - start_time) * 1000, 2
                )
                result["performance"]["function_name"] = func.__name__

            return result
        except Exception as e:
            end_time = time.time()
            # Add performance info to error context
            {
                "execution_time_ms": round((end_time - start_time) * 1000, 2),
                "function_name": func.__name__,
            }
            raise e

    return wrapper


# Enhanced parameter validation models with enums and better constraints
if _FASTMCP_AVAILABLE:
    from enum import Enum

    class OutputFormat(str, Enum):
        """Supported output formats."""

        SVG = "svg"
        PNG = "png"
        PDF = "pdf"

    class ThemeName(str, Enum):
        """Available theme names."""

        DEFAULT = "default"
        DARK = "dark"
        FOREST = "forest"
        NEUTRAL = "neutral"
        BASE = "base"

    class DiagramType(str, Enum):
        """Supported diagram types."""

        AUTO = "auto"
        FLOWCHART = "flowchart"
        SEQUENCE = "sequence"
        CLASS = "class"
        STATE = "state"
        ER = "er"
        JOURNEY = "journey"
        GANTT = "gantt"
        PIE = "pie"
        GITGRAPH = "gitgraph"
        MINDMAP = "mindmap"
        TIMELINE = "timeline"

    class StylePreference(str, Enum):
        """Style preferences for diagram generation."""

        CLEAN = "clean"
        DETAILED = "detailed"
        MINIMAL = "minimal"

    class ComplexityLevel(str, Enum):
        """Complexity levels for diagram generation."""

        SIMPLE = "simple"
        MEDIUM = "medium"
        COMPLEX = "complex"

    class OptimizationType(str, Enum):
        """Types of diagram optimization."""

        LAYOUT = "layout"
        STYLE = "style"
        STRUCTURE = "structure"
        PERFORMANCE = "performance"

    class RenderDiagramParams(BaseModel):  # type: ignore[misc]
        """Parameters for render_diagram tool."""

        diagram_code: str = Field(
            description="Mermaid diagram code to render",
            min_length=1,
            max_length=50000,
            json_schema_extra={"example": "flowchart TD\n    A[Start] --> B[End]"},
        )
        output_format: OutputFormat = Field(
            default=OutputFormat.SVG,
            description="Output format for the rendered diagram",
        )
        theme: ThemeName | None = Field(
            default=None, description="Theme to apply to the diagram"
        )
        width: int | None = Field(
            default=None, description="Output width in pixels", ge=100, le=4096
        )
        height: int | None = Field(
            default=None, description="Output height in pixels", ge=100, le=4096
        )
        background_color: str | None = Field(
            default=None,
            description="Background color (hex format like #ffffff or named color)",
            pattern=r"^(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|[a-zA-Z]+)$",
        )
        scale: float | None = Field(
            default=None, description="Scale factor for output", ge=0.1, le=10.0
        )

    class ValidateDiagramParams(BaseModel):  # type: ignore[misc]
        """Parameters for validate_diagram tool."""

        diagram_code: str = Field(
            description="Mermaid diagram code to validate",
            min_length=1,
            max_length=50000,
            json_schema_extra={"example": "flowchart TD\n    A[Start] --> B[End]"},
        )

    class ListThemesParams(BaseModel):  # type: ignore[misc]
        """Parameters for list_themes tool (no parameters needed)."""

        pass

    class GenerateDiagramParams(BaseModel):  # type: ignore[misc]
        """Parameters for generate_diagram_from_text tool."""

        text_description: str = Field(
            description="Natural language description of the diagram to generate",
            min_length=10,
            max_length=5000,
            json_schema_extra={
                "example": "A user login process with authentication and error handling"
            },
        )
        diagram_type: DiagramType = Field(
            default=DiagramType.AUTO, description="Type of diagram to generate"
        )
        style_preference: StylePreference = Field(
            default=StylePreference.CLEAN,
            description="Style preference for the generated diagram",
        )
        complexity_level: ComplexityLevel = Field(
            default=ComplexityLevel.MEDIUM,
            description="Complexity level for the generated diagram",
        )

    class OptimizeDiagramParams(BaseModel):  # type: ignore[misc]
        """Parameters for optimize_diagram tool."""

        diagram_code: str = Field(
            description="Mermaid diagram code to optimize",
            min_length=1,
            max_length=50000,
            json_schema_extra={"example": "flowchart TD\n    A[Start] --> B[End]"},
        )
        optimization_type: OptimizationType = Field(
            default=OptimizationType.LAYOUT,
            description="Type of optimization to perform",
        )

    class AnalyzeDiagramParams(BaseModel):  # type: ignore[misc]
        """Parameters for analyze_diagram tool."""

        diagram_code: str = Field(
            description="Mermaid diagram code to analyze",
            min_length=1,
            max_length=50000,
            json_schema_extra={"example": "flowchart TD\n    A[Start] --> B[End]"},
        )
        include_suggestions: bool = Field(
            default=True,
            description="Include AI-powered improvement suggestions in the analysis",
        )

    class CreateFromTemplateParams(BaseModel):  # type: ignore[misc]
        """Parameters for create_from_template tool."""

        template_name: str = Field(
            description="Name or ID of the template to use",
            min_length=1,
            max_length=100,
            json_schema_extra={"example": "software_architecture"},
        )
        parameters: dict[str, Any] = Field(
            description="Template parameters as key-value pairs",
            json_schema_extra={
                "example": {"title": "My System", "services": ["API", "Database"]}
            },
        )
        validate_params: bool = Field(
            default=True, description="Validate template parameters against schema"
        )

    # New parameter models for additional tools
    class ConfigurationParams(BaseModel):  # type: ignore[misc]
        """Parameters for configuration management tools."""

        key: str | None = Field(
            default=None,
            description="Configuration key to get/set (if None, returns all config)",
            max_length=100,
        )
        value: Any | None = Field(
            default=None,
            description="Configuration value to set (only for update operations)",
        )
        section: str | None = Field(
            default=None,
            description="Configuration section to filter by",
            max_length=50,
        )

    class TemplateManagementParams(BaseModel):  # type: ignore[misc]
        """Parameters for template management tools."""

        template_name: str | None = Field(
            default=None, description="Template name to filter by", max_length=100
        )
        category: str | None = Field(
            default=None, description="Template category to filter by", max_length=50
        )
        include_builtin: bool = Field(
            default=True, description="Include built-in templates"
        )
        include_custom: bool = Field(
            default=True, description="Include custom templates"
        )

    class DiagramTypeParams(BaseModel):  # type: ignore[misc]
        """Parameters for diagram type information tools."""

        diagram_type: DiagramType | None = Field(
            default=None, description="Specific diagram type to get information for"
        )
        include_examples: bool = Field(
            default=True, description="Include example code for each diagram type"
        )

    class FileOperationParams(BaseModel):  # type: ignore[misc]
        """Parameters for file operation tools."""

        file_path: str = Field(
            description="File path for save/load operations",
            min_length=1,
            max_length=500,
        )
        create_directories: bool = Field(
            default=True, description="Create parent directories if they don't exist"
        )
        overwrite: bool = Field(default=False, description="Overwrite existing files")

    class BatchRenderParams(BaseModel):  # type: ignore[misc]
        """Parameters for batch rendering operations."""

        diagrams: list[dict[str, Any]] = Field(
            description="List of diagrams to render, each with 'code' and optional 'format', 'theme'",
            min_length=1,
            max_length=50,
        )
        output_format: OutputFormat = Field(
            default=OutputFormat.SVG,
            description="Default output format for all diagrams",
        )
        theme: ThemeName | None = Field(
            default=None, description="Default theme for all diagrams"
        )
        parallel: bool = Field(
            default=True,
            description="Process diagrams in parallel for better performance",
        )
        max_workers: int = Field(
            default=4, ge=1, le=16, description="Maximum number of parallel workers"
        )

    class CacheManagementParams(BaseModel):  # type: ignore[misc]
        """Parameters for cache management operations."""

        operation: str = Field(
            description="Cache operation to perform",
            pattern=r"^(clear|stats|info|cleanup)$",
        )
        cache_type: str | None = Field(
            default=None,
            description="Type of cache to operate on (render, template, config)",
            pattern=r"^(render|template|config|all)$",
        )

else:
    # Fallback classes for testing without FastMCP
    class RenderDiagramParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class ValidateDiagramParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class ListThemesParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            pass

    class GenerateDiagramParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class OptimizeDiagramParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class AnalyzeDiagramParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class CreateFromTemplateParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    # Fallback classes for new parameter models
    class ConfigurationParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class TemplateManagementParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class DiagramTypeParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class FileOperationParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class BatchRenderParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class CacheManagementParams:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)


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

    logger.info("Registered all MCP tools")


@measure_performance
def render_diagram(
    diagram_code: str,
    output_format: str = "svg",
    theme: str | None = None,
    width: int | None = None,
    height: int | None = None,
    background_color: str | None = None,
    scale: float | None = None,
) -> dict[str, Any]:
    """
    Render a Mermaid diagram to the specified format.

    This tool provides comprehensive diagram rendering with support for multiple
    output formats, themes, and customization options. It includes automatic
    validation, error handling, and detailed metadata in responses.

    Args:
        diagram_code: Mermaid diagram code to render
        output_format: Output format (svg, png, pdf)
        theme: Theme name (default, dark, forest, neutral, base)
        width: Output width in pixels (100-4096)
        height: Output height in pixels (100-4096)
        background_color: Background color (hex format or named color)
        scale: Scale factor for output (0.1-10.0)

    Returns:
        Dictionary containing rendered diagram data and comprehensive metadata

    Example:
        >>> result = render_diagram(
        ...     "flowchart TD\\n    A[Start] --> B[End]",
        ...     output_format="svg",
        ...     theme="dark"
        ... )
        >>> print(result["success"])  # True
        >>> print(result["data"])     # SVG content
    """
    try:
        # Validate parameters with enhanced validation
        params = RenderDiagramParams(
            diagram_code=diagram_code,
            output_format=output_format,
            theme=theme,
            width=width,
            height=height,
            background_color=background_color,
            scale=scale,
        )

        # Create configuration
        config = MermaidConfig()

        # Prepare rendering options
        options: dict[str, Any] = {}
        if params.width:
            options["width"] = params.width
        if params.height:
            options["height"] = params.height
        if params.background_color:
            options["background_color"] = params.background_color
        if params.scale:
            options["scale"] = params.scale

        # Create renderer with theme
        renderer = MermaidRenderer(config=config, theme=params.theme)

        # Render diagram
        result = renderer.render_raw(
            params.diagram_code, params.output_format.value, **options
        )

        # Convert result to string if it's bytes (for consistent handling)
        if isinstance(result, bytes):
            # For binary formats, we'll encode as base64 for JSON serialization
            data = base64.b64encode(result).decode("utf-8")
            is_binary = True
        else:
            data = result
            is_binary = False

        # Enhanced metadata
        metadata = {
            "theme": params.theme.value if params.theme else "default",
            "width": params.width,
            "height": params.height,
            "background_color": params.background_color,
            "scale": params.scale,
            "size_bytes": len(result) if isinstance(result, (str, bytes)) else 0,
            "diagram_type": _detect_diagram_type(params.diagram_code),
            "line_count": len(params.diagram_code.splitlines()),
            "character_count": len(params.diagram_code),
            "encoding": "base64" if is_binary else "utf-8",
        }

        return create_success_response(
            data={
                "format": params.output_format.value,
                "content": data,
                "is_binary": is_binary,
            },
            metadata=metadata,
        )

    except ValidationError as e:
        logger.error(f"Validation error in render_diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.VALIDATION,
            context={"diagram_code_length": len(diagram_code) if diagram_code else 0},
            suggestions=[
                "Check diagram syntax",
                "Verify parameter values are within valid ranges",
            ],
        )
    except Exception as e:
        logger.error(f"Error rendering diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.RENDERING,
            context={
                "output_format": output_format,
                "theme": theme,
                "diagram_type": (
                    _detect_diagram_type(diagram_code) if diagram_code else None
                ),
            },
        )


@measure_performance
def validate_diagram(diagram_code: str) -> dict[str, Any]:
    """
    Validate Mermaid diagram syntax and structure.

    This tool provides comprehensive validation of Mermaid diagram code,
    including syntax checking, structure analysis, and detailed error reporting
    with line-by-line feedback and improvement suggestions.

    Args:
        diagram_code: Mermaid diagram code to validate

    Returns:
        Dictionary containing detailed validation results and metadata

    Example:
        >>> result = validate_diagram("flowchart TD\\n    A[Start] --> B[End]")
        >>> print(result["data"]["valid"])  # True
        >>> print(result["data"]["diagram_type"])  # "flowchart"
    """
    try:
        # Validate parameters with enhanced validation
        params = ValidateDiagramParams(diagram_code=diagram_code)

        # Validate syntax using MermaidValidator
        validator = MermaidValidator()
        result = validator.validate(params.diagram_code)

        # Enhanced validation data
        validation_data = {
            "valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "line_errors": result.line_errors,
            "diagram_type": _detect_diagram_type(params.diagram_code),
            "complexity_score": _calculate_complexity_score(params.diagram_code),
            "quality_score": _calculate_quality_score(result, params.diagram_code),
        }

        # Enhanced metadata
        metadata = {
            "line_count": len(params.diagram_code.splitlines()),
            "character_count": len(params.diagram_code),
            "word_count": len(params.diagram_code.split()),
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "validation_timestamp": __import__("datetime").datetime.now().isoformat(),
        }

        # Add suggestions for improvement if there are issues
        suggestions = []
        if not result.is_valid:
            suggestions.extend(
                [
                    "Check syntax against Mermaid documentation",
                    "Verify diagram type declaration",
                    "Ensure proper node and edge syntax",
                ]
            )
        if result.warnings:
            suggestions.append("Review warnings for potential improvements")

        return create_success_response(data=validation_data, metadata=metadata)

    except ValidationError as e:
        logger.error(f"Validation error in validate_diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.VALIDATION,
            context={"diagram_code_length": len(diagram_code) if diagram_code else 0},
            suggestions=[
                "Ensure diagram code is not empty",
                "Check for valid UTF-8 encoding",
            ],
        )
    except Exception as e:
        logger.error(f"Error validating diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            context={
                "diagram_type": (
                    _detect_diagram_type(diagram_code) if diagram_code else None
                )
            },
        )


@measure_performance
def list_themes() -> dict[str, Any]:
    """
    List all available Mermaid themes with detailed information.

    This tool provides comprehensive information about all available themes,
    including built-in themes and any custom themes that have been configured.
    Each theme includes description, color palette information, and usage examples.

    Returns:
        Dictionary containing detailed theme information and metadata

    Example:
        >>> result = list_themes()
        >>> print(result["data"]["themes"]["dark"]["description"])
        >>> print(result["data"]["default_theme"])  # "default"
    """
    try:
        # Enhanced theme information with more details
        themes = {
            "default": {
                "name": "Default",
                "description": "Default theme with light background and standard colors",
                "background": "light",
                "primary_color": "#0066cc",
                "suitable_for": ["presentations", "documentation", "general use"],
                "contrast": "high",
            },
            "dark": {
                "name": "Dark",
                "description": "Dark theme with dark background for low-light environments",
                "background": "dark",
                "primary_color": "#66b3ff",
                "suitable_for": ["night work", "dark interfaces", "reduced eye strain"],
                "contrast": "high",
            },
            "forest": {
                "name": "Forest",
                "description": "Forest theme with green color palette for nature-inspired designs",
                "background": "light",
                "primary_color": "#228B22",
                "suitable_for": [
                    "environmental topics",
                    "organic processes",
                    "natural systems",
                ],
                "contrast": "medium",
            },
            "base": {
                "name": "Base",
                "description": "Minimal base theme with clean, simple styling",
                "background": "light",
                "primary_color": "#333333",
                "suitable_for": [
                    "minimalist designs",
                    "technical documentation",
                    "clean layouts",
                ],
                "contrast": "medium",
            },
            "neutral": {
                "name": "Neutral",
                "description": "Neutral theme with gray color palette for professional appearance",
                "background": "light",
                "primary_color": "#666666",
                "suitable_for": [
                    "business documents",
                    "professional presentations",
                    "formal reports",
                ],
                "contrast": "medium",
            },
        }

        # Try to get custom themes from theme manager if available
        custom_themes = {}
        try:
            from ..config import ThemeManager

            theme_manager = ThemeManager()
            available_themes = theme_manager.get_available_themes()

            for theme_name in available_themes:
                if theme_name not in themes:  # Custom theme
                    try:
                        theme_config = theme_manager.get_theme(theme_name)
                        custom_themes[theme_name] = {
                            "name": theme_name.title(),
                            "description": f"Custom theme: {theme_name}",
                            "background": "unknown",
                            "primary_color": theme_config.get(
                                "primaryColor", "#000000"
                            ),
                            "suitable_for": ["custom use cases"],
                            "contrast": "unknown",
                            "custom": True,
                        }
                    except Exception:
                        pass  # Skip themes that can't be loaded
        except ImportError:
            pass  # Theme manager not available

        # Combine built-in and custom themes
        all_themes = {**themes, **custom_themes}

        # Enhanced metadata
        metadata = {
            "total_themes": len(all_themes),
            "builtin_themes": len(themes),
            "custom_themes": len(custom_themes),
            "default_theme": "default",
            "theme_categories": {
                "light_background": [
                    name
                    for name, info in all_themes.items()
                    if info.get("background") == "light"
                ],
                "dark_background": [
                    name
                    for name, info in all_themes.items()
                    if info.get("background") == "dark"
                ],
                "custom": [
                    name
                    for name, info in all_themes.items()
                    if info.get("custom", False)
                ],
            },
        }

        return create_success_response(
            data={
                "themes": all_themes,
                "default_theme": "default",
                "recommendations": {
                    "presentations": ["default", "neutral"],
                    "dark_mode": ["dark"],
                    "nature_topics": ["forest"],
                    "minimal_design": ["base"],
                    "professional": ["neutral", "base"],
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error listing themes: {e}")
        return create_error_response(
            e,
            ErrorCategory.CONFIGURATION,
            suggestions=[
                "Check theme configuration",
                "Verify theme manager is properly initialized",
            ],
        )


def _detect_diagram_type(diagram_code: str) -> str | None:
    """
    Detect the type of Mermaid diagram from the code.

    Args:
        diagram_code: Mermaid diagram code

    Returns:
        Detected diagram type or None
    """
    code_lower = diagram_code.lower().strip()

    if code_lower.startswith("graph"):
        return "flowchart"
    elif code_lower.startswith("flowchart"):
        return "flowchart"
    elif code_lower.startswith("sequencediagram"):
        return "sequence"
    elif code_lower.startswith("classdiagram"):
        return "class"
    elif code_lower.startswith("statediagram"):
        return "state"
    elif code_lower.startswith("erdiagram"):
        return "er"
    elif code_lower.startswith("gantt"):
        return "gantt"
    elif code_lower.startswith("pie"):
        return "pie"
    elif code_lower.startswith("journey"):
        return "user_journey"
    elif code_lower.startswith("gitgraph"):
        return "git_graph"
    elif code_lower.startswith("mindmap"):
        return "mindmap"
    elif code_lower.startswith("timeline"):
        return "timeline"

    return None


def _calculate_complexity_score(diagram_code: str) -> float:
    """
    Calculate a complexity score for the diagram.

    Args:
        diagram_code: Mermaid diagram code

    Returns:
        Complexity score from 0.0 to 10.0
    """
    lines = diagram_code.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    # Basic metrics
    line_count = len(non_empty_lines)
    arrow_count = sum(
        line.count("-->") + line.count("->") + line.count("->>")
        for line in non_empty_lines
    )
    node_count = sum(
        1 for line in non_empty_lines if "[" in line or "(" in line or "{" in line
    )

    # Calculate complexity based on various factors
    complexity = 0.0
    complexity += min(line_count * 0.1, 3.0)  # Line count contribution (max 3.0)
    complexity += min(arrow_count * 0.2, 3.0)  # Connection complexity (max 3.0)
    complexity += min(node_count * 0.15, 2.0)  # Node complexity (max 2.0)

    # Additional complexity factors
    if "subgraph" in diagram_code.lower():
        complexity += 1.0
    if any(
        keyword in diagram_code.lower() for keyword in ["note", "class", "interface"]
    ):
        complexity += 0.5

    return min(complexity, 10.0)


def _calculate_quality_score(validation_result: Any, diagram_code: str) -> float:
    """
    Calculate a quality score for the diagram.

    Args:
        validation_result: Validation result object
        diagram_code: Mermaid diagram code

    Returns:
        Quality score from 0.0 to 10.0
    """
    if not validation_result.is_valid:
        return 0.0

    score = 10.0

    # Deduct for warnings
    score -= len(validation_result.warnings) * 0.5

    # Check for good practices
    lines = diagram_code.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    # Deduct for very short or very long lines (readability)
    for line in non_empty_lines:
        if len(line) > 100:
            score -= 0.1
        elif len(line) < 5 and "-->" not in line:
            score -= 0.1

    # Bonus for good structure
    if any(line.strip().startswith("%%") for line in lines):  # Has comments
        score += 0.5

    return max(score, 0.0)


def generate_diagram_from_text(
    text_description: str,
    diagram_type: str = "auto",
    style_preference: str = "clean",
    complexity_level: str = "medium",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Generate a Mermaid diagram from natural language text using AI.

    Args:
        text_description: Natural language description of the diagram
        diagram_type: Type of diagram to generate (auto, flowchart, sequence, class, etc.)
        style_preference: Style preference (clean, detailed, minimal)
        complexity_level: Complexity level (simple, medium, complex)
        ctx: MCP context (optional)

    Returns:
        Dictionary containing generated diagram and metadata
    """
    try:
        # Validate parameters
        params = GenerateDiagramParams(
            text_description=text_description,
            diagram_type=diagram_type,
            style_preference=style_preference,
            complexity_level=complexity_level,
        )

        # Check if AI module is available
        try:
            from ..ai import AIdiagramType, DiagramGenerator, GenerationConfig
        except ImportError:
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install mermaid-render[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        # Create generation configuration
        config = GenerationConfig(
            diagram_type=AIdiagramType(params.diagram_type),
            style_preference=params.style_preference,
            complexity_level=params.complexity_level,
        )

        # Generate diagram
        generator = DiagramGenerator()
        result = generator.from_text(params.text_description, config)

        return {
            "success": True,
            "diagram_code": result.diagram_code,
            "diagram_type": result.diagram_type.value,
            "confidence_score": result.confidence_score,
            "suggestions": (
                [
                    s.to_dict() if hasattr(s, "to_dict") else str(s)
                    for s in result.suggestions
                ]
                if result.suggestions
                else []
            ),
            "metadata": result.metadata,
            "request_id": ctx.request_id if ctx else None,
        }

    except Exception as e:
        logger.error(f"Error generating diagram from text: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


def optimize_diagram(
    diagram_code: str,
    optimization_type: str = "layout",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Optimize a Mermaid diagram for better readability and performance using AI.

    Args:
        diagram_code: Mermaid diagram code to optimize
        optimization_type: Type of optimization (layout, style, structure)
        ctx: MCP context (optional)

    Returns:
        Dictionary containing optimized diagram and changes made
    """
    try:
        # Validate parameters
        params = OptimizeDiagramParams(
            diagram_code=diagram_code, optimization_type=optimization_type
        )

        # Check if AI module is available
        try:
            from ..ai import DiagramOptimizer, OptimizationType  # noqa: F401
        except ImportError:
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install mermaid-render[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        # Optimize diagram
        optimizer = DiagramOptimizer()
        results = optimizer.optimize_all(params.diagram_code)
        # Use the first result for backward compatibility
        result = results[0] if results else None

        if result:
            return {
                "success": True,
                "original_diagram": params.diagram_code,
                "optimized_diagram": result.optimized_diagram,
                "optimization_type": params.optimization_type,
                "changes_made": result.improvements,
                "improvement_score": result.confidence_score,
                "metadata": {"optimization_type": result.optimization_type.value},
                "request_id": ctx.request_id if ctx else None,
            }
        else:
            return {
                "success": False,
                "error": "No optimization results available",
                "request_id": ctx.request_id if ctx else None,
            }

    except Exception as e:
        logger.error(f"Error optimizing diagram: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


def analyze_diagram(
    diagram_code: str,
    include_suggestions: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Analyze a Mermaid diagram and provide metrics, insights, and quality assessment.

    Args:
        diagram_code: Mermaid diagram code to analyze
        include_suggestions: Include improvement suggestions
        ctx: MCP context (optional)

    Returns:
        Dictionary containing analysis results and insights
    """
    try:
        # Validate parameters
        params = AnalyzeDiagramParams(
            diagram_code=diagram_code, include_suggestions=include_suggestions
        )

        # Check if AI module is available
        try:
            from ..ai import DiagramAnalyzer
        except ImportError:
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install mermaid-render[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        # Analyze diagram
        analyzer = DiagramAnalyzer()
        result = analyzer.analyze(params.diagram_code)

        response = {
            "success": True,
            "complexity": result.complexity.to_dict(),
            "quality": result.quality.to_dict(),
            "issues": result.issues,
            "recommendations": result.recommendations,
            "diagram_type": _detect_diagram_type(params.diagram_code),
            "metadata": {
                "line_count": len(params.diagram_code.splitlines()),
                "character_count": len(params.diagram_code),
                "node_count": result.complexity.node_count,
                "connection_count": result.complexity.connection_count,
            },
            "request_id": ctx.request_id if ctx else None,
        }

        if params.include_suggestions:
            from ..ai import SuggestionEngine

            suggestion_engine = SuggestionEngine()
            suggestions = suggestion_engine.get_suggestions(params.diagram_code)
            response["suggestions"] = [s.to_dict() for s in suggestions]

        return response

    except Exception as e:
        logger.error(f"Error analyzing diagram: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


def get_diagram_suggestions(
    diagram_code: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Get AI-powered suggestions for improving a Mermaid diagram.

    Args:
        diagram_code: Mermaid diagram code to analyze
        ctx: MCP context (optional)

    Returns:
        Dictionary containing improvement suggestions
    """
    try:
        # Check if AI module is available
        try:
            from ..ai import SuggestionEngine
        except ImportError:
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install mermaid-render[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        # Get suggestions
        suggestion_engine = SuggestionEngine()
        suggestions = suggestion_engine.get_suggestions(diagram_code)

        return {
            "success": True,
            "suggestions": [s.to_dict() for s in suggestions],
            "total_suggestions": len(suggestions),
            "high_priority_count": len(
                [
                    s
                    for s in suggestions
                    if hasattr(s, "priority")
                    and hasattr(s.priority, "value")
                    and str(s.priority.value) == "high"
                ]
            ),
            "diagram_type": _detect_diagram_type(diagram_code),
            "request_id": ctx.request_id if ctx else None,
        }

    except Exception as e:
        logger.error(f"Error getting diagram suggestions: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


def create_from_template(
    template_name: str,
    parameters: dict[str, Any],
    validate_params: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Create a Mermaid diagram from a template with provided data.

    Args:
        template_name: Name of the template to use
        parameters: Template parameters
        validate_params: Validate template parameters
        ctx: MCP context (optional)

    Returns:
        Dictionary containing generated diagram from template
    """
    try:
        # Validate parameters
        params = CreateFromTemplateParams(
            template_name=template_name,
            parameters=parameters,
            validate_params=validate_params,
        )

        # Check if templates module is available
        try:
            from ..templates import TemplateManager
        except ImportError:
            return {
                "success": False,
                "error": "Template functionality not available. Install with: pip install mermaid-render[templates]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        # Create template manager and generate diagram
        template_manager = TemplateManager()
        diagram_code = template_manager.generate(
            params.template_name,
            params.parameters,
            validate_params=params.validate_params,
        )

        # Get template info for metadata
        template = template_manager.get_template_by_name(params.template_name)

        return {
            "success": True,
            "diagram_code": diagram_code,
            "template_name": params.template_name,
            "parameters_used": params.parameters,
            "template_info": {
                "id": template.id if template else None,
                "description": template.description if template else None,
                "diagram_type": template.diagram_type if template else None,
                "author": template.author if template else None,
                "tags": template.tags if template else [],
            },
            "request_id": ctx.request_id if ctx else None,
        }

    except Exception as e:
        logger.error(f"Error creating diagram from template: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


# New tool implementations


@measure_performance
def get_configuration(
    key: str | None = None,
    section: str | None = None,
) -> dict[str, Any]:
    """
    Get current configuration settings with optional filtering.

    This tool provides access to the current mermaid-render configuration,
    allowing retrieval of all settings or filtering by specific keys or sections.
    Includes detailed information about each setting and its current value.

    Args:
        key: Specific configuration key to retrieve (if None, returns all)
        section: Configuration section to filter by (e.g., 'rendering', 'themes')

    Returns:
        Dictionary containing configuration data and metadata

    Example:
        >>> result = get_configuration()
        >>> print(result["data"]["timeout"])  # Current timeout setting
        >>> result = get_configuration(key="default_theme")
        >>> print(result["data"]["value"])  # Current default theme
    """
    try:
        # Validate parameters
        params = ConfigurationParams(key=key, section=section)

        # Get configuration from MermaidConfig
        config = MermaidConfig()
        all_config = config.to_dict()

        if params.key:
            # Return specific key
            if params.key in all_config:
                config_data = {
                    "key": params.key,
                    "value": all_config[params.key],
                    "type": type(all_config[params.key]).__name__,
                    "description": _get_config_description(params.key),
                }
            else:
                return create_error_response(
                    ValueError(f"Configuration key '{params.key}' not found"),
                    ErrorCategory.CONFIGURATION,
                    context={"available_keys": list(all_config.keys())},
                    suggestions=[
                        f"Use one of the available keys: {', '.join(list(all_config.keys())[:5])}..."
                    ],
                )
        else:
            # Return all configuration or filtered by section
            if params.section:
                # Filter by section (basic implementation)
                section_keys = _get_section_keys(params.section)
                filtered_config = {
                    k: v for k, v in all_config.items() if k in section_keys
                }
                config_data = {
                    "section": params.section,
                    "settings": {
                        k: {
                            "value": v,
                            "type": type(v).__name__,
                            "description": _get_config_description(k),
                        }
                        for k, v in filtered_config.items()
                    },
                }
            else:
                # Return all configuration
                config_data = {
                    "settings": {
                        k: {
                            "value": v,
                            "type": type(v).__name__,
                            "description": _get_config_description(k),
                        }
                        for k, v in all_config.items()
                    }
                }

        # Enhanced metadata
        metadata = {
            "total_settings": len(all_config),
            "filtered_settings": (
                len(config_data.get("settings", {})) if "settings" in config_data else 1
            ),
            "available_sections": ["rendering", "themes", "cache", "ai", "validation"],
            "config_source": "MermaidConfig",
        }

        return create_success_response(data=config_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        return create_error_response(
            e,
            ErrorCategory.CONFIGURATION,
            suggestions=["Check configuration system is properly initialized"],
        )


def _get_config_description(key: str) -> str:
    """Get description for a configuration key."""
    descriptions = {
        "server_url": "URL for the Mermaid rendering server",
        "timeout": "Timeout in seconds for rendering operations",
        "retries": "Number of retry attempts for failed operations",
        "default_theme": "Default theme to use for diagrams",
        "default_format": "Default output format for rendered diagrams",
        "validate_syntax": "Whether to validate diagram syntax before rendering",
        "cache_enabled": "Whether to enable caching for improved performance",
        "cache_dir": "Directory path for storing cached files",
        "use_plugin_system": "Whether to use the plugin-based rendering system",
        "fallback_enabled": "Whether to enable fallback rendering methods",
        "max_fallback_attempts": "Maximum number of fallback attempts",
    }
    return descriptions.get(key, f"Configuration setting: {key}")


def _get_section_keys(section: str) -> list[str]:
    """Get configuration keys for a specific section."""
    sections = {
        "rendering": [
            "server_url",
            "timeout",
            "retries",
            "default_format",
            "use_plugin_system",
        ],
        "themes": ["default_theme"],
        "cache": ["cache_enabled", "cache_dir"],
        "validation": ["validate_syntax"],
        "fallback": ["fallback_enabled", "max_fallback_attempts"],
    }
    return sections.get(section, [])


def _validate_config_value(key: str, value: Any) -> bool:
    """Validate a configuration value for a specific key."""
    from collections.abc import Callable

    validations: dict[str, Callable[[Any], bool]] = {
        "timeout": lambda v: isinstance(v, (int, float)) and v > 0,
        "retries": lambda v: isinstance(v, int) and v >= 0,
        "default_theme": lambda v: isinstance(v, str)
        and v in ["default", "dark", "forest", "neutral", "base"],
        "default_format": lambda v: isinstance(v, str) and v in ["svg", "png", "pdf"],
        "validate_syntax": lambda v: isinstance(v, bool),
        "cache_enabled": lambda v: isinstance(v, bool),
        "use_plugin_system": lambda v: isinstance(v, bool),
        "fallback_enabled": lambda v: isinstance(v, bool),
        "max_fallback_attempts": lambda v: isinstance(v, int) and v >= 0,
        "server_url": lambda v: isinstance(v, str)
        and v.startswith(("http://", "https://")),
    }

    validator = validations.get(key)
    if validator:
        return validator(value)

    # Default validation - just check it's not None
    return value is not None


# Helper functions from additional_tools.py


def _generate_template_usage_instructions(template: Any) -> str:
    """Generate usage instructions for a template."""
    instructions = f"To use the '{template.name}' template:\n\n"
    instructions += (
        f"1. Call create_from_template with template_name='{template.name}'\n"
    )
    instructions += "2. Provide the following parameters:\n"

    for param_name, param_info in template.parameters.items():
        param_type = (
            param_info.get("type", "any") if isinstance(param_info, dict) else "any"
        )
        instructions += f"   - {param_name} ({param_type})\n"

    instructions += f"\n3. The template will generate a {template.diagram_type} diagram"
    return instructions


def _extract_parameter_schema(parameters: dict[str, Any]) -> dict[str, Any]:
    """Extract parameter schema from template parameters."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    for param_name, param_info in parameters.items():
        if isinstance(param_info, dict):
            schema["properties"][param_name] = param_info
            if param_info.get("required", False):
                schema["required"].append(param_name)
        else:
            schema["properties"][param_name] = {"type": "string"}

    return schema


def _assess_template_complexity(template: Any) -> str:
    """Assess template complexity level."""
    content = template.template_content
    param_count = len(template.parameters)

    if param_count <= 2 and len(content) < 200:
        return "simple"
    elif param_count <= 5 and len(content) < 500:
        return "medium"
    else:
        return "complex"


def _generate_template_usage_example(template: Any) -> str:
    """Generate a usage example for a template."""
    example_params: dict[str, Any] = {}
    for param_name, param_info in template.parameters.items():
        if isinstance(param_info, dict):
            param_type = param_info.get("type", "string")
            if param_type == "string":
                example_params[param_name] = f"example_{param_name}"
            elif param_type == "list":
                example_params[param_name] = ["item1", "item2"]
            elif param_type == "number":
                example_params[param_name] = 42
            else:
                example_params[param_name] = f"example_{param_name}"
        else:
            example_params[param_name] = f"example_{param_name}"

    return f"create_from_template('{template.name}', {example_params})"


def _get_diagram_example(diagram_type: str) -> str:
    """Get example code for a specific diagram type."""
    examples = {
        "flowchart": """flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]
    D --> E""",
        "sequence": """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B-->>A: Hello Alice!
    A->>B: How are you?
    B-->>A: I'm good, thanks!""",
        "class": """classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog""",
        "state": """stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Success : complete
    Processing --> Error : fail
    Success --> [*]
    Error --> Idle : retry""",
        "er": """erDiagram
    CUSTOMER {
        int customer_id PK
        string name
        string email
    }
    ORDER {
        int order_id PK
        int customer_id FK
        date order_date
    }
    CUSTOMER ||--o{ ORDER : places""",
        "journey": """journey
    title User Shopping Journey
    section Discovery
        Visit website: 5: User
        Browse products: 4: User
    section Purchase
        Add to cart: 3: User
        Checkout: 2: User
        Payment: 1: User""",
        "gantt": """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Planning
        Requirements: 2024-01-01, 5d
        Design: 2024-01-06, 3d
    section Development
        Coding: 2024-01-09, 10d
        Testing: 2024-01-19, 5d""",
        "pie": """pie title Sample Data
    "Category A" : 42.5
    "Category B" : 30.0
    "Category C" : 17.5
    "Category D" : 10.0""",
        "gitgraph": """gitgraph
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit""",
        "mindmap": """mindmap
  root((Project))
    Planning
      Requirements
      Timeline
    Development
      Frontend
      Backend
    Testing
      Unit Tests
      Integration""",
        "timeline": """timeline
    title History of Programming
    1940s : ENIAC
         : First Computer
    1950s : FORTRAN
         : First High-level Language
    1970s : C Language
         : System Programming""",
    }

    return examples.get(diagram_type, f"# Example for {diagram_type} not available")


def _get_diagram_best_practices(diagram_type: str) -> list[str]:
    """Get best practices for a specific diagram type."""
    practices = {
        "flowchart": [
            "Use clear, descriptive labels for nodes",
            "Keep the flow direction consistent (top-down or left-right)",
            "Use appropriate shapes: rectangles for processes, diamonds for decisions",
            "Ensure all decision paths are clearly labeled",
            "Group related processes using subgraphs when appropriate",
        ],
        "sequence": [
            "Define all participants at the beginning",
            "Use consistent arrow types for different message types",
            "Add activation boxes for long-running operations",
            "Include notes for complex interactions",
            "Keep message labels concise but descriptive",
        ],
        "class": [
            "Show only relevant attributes and methods",
            "Use proper visibility indicators (+, -, #)",
            "Group related classes together",
            "Use inheritance and composition relationships appropriately",
            "Keep class names and method names clear and consistent",
        ],
        "state": [
            "Use clear state names that describe the system condition",
            "Label transitions with triggering events",
            "Include guard conditions when necessary",
            "Use composite states for complex state hierarchies",
            "Ensure all states have clear entry and exit paths",
        ],
    }

    return practices.get(
        diagram_type,
        [
            "Use clear and descriptive labels",
            "Keep the diagram simple and focused",
            "Follow Mermaid syntax guidelines",
            "Test the diagram for readability",
        ],
    )


def _get_syntax_guide(diagram_type: str) -> dict[str, str]:
    """Get syntax guide for a specific diagram type."""
    guides = {
        "flowchart": {
            "start": "flowchart TD (top-down) or flowchart LR (left-right)",
            "nodes": "[text] for rectangles, {text} for diamonds, ((text)) for circles",
            "connections": "--> for arrows, --- for lines, -.-> for dotted arrows",
            "labels": "A-->|label|B for labeled connections",
            "subgraphs": "subgraph title ... end for grouping",
        },
        "sequence": {
            "start": "sequenceDiagram",
            "participants": "participant A as Alice",
            "messages": "A->>B for sync calls, A-->>B for responses",
            "activation": "activate A ... deactivate A",
            "notes": "note over A: Note text",
        },
        "class": {
            "start": "classDiagram",
            "classes": "class ClassName { attributes methods }",
            "relationships": "<|-- inheritance, *-- composition, o-- aggregation",
            "visibility": "+ public, - private, # protected",
            "types": ": type after attribute/method names",
        },
    }

    return guides.get(
        diagram_type, {"info": "Syntax guide not available for this diagram type"}
    )


def _get_common_patterns(diagram_type: str) -> list[dict[str, str]]:
    """Get common patterns for a specific diagram type."""
    patterns = {
        "flowchart": [
            {
                "name": "Decision Tree",
                "description": "Branching logic with yes/no decisions",
            },
            {
                "name": "Process Flow",
                "description": "Sequential steps with start and end points",
            },
            {
                "name": "Parallel Processing",
                "description": "Multiple paths that converge later",
            },
        ],
        "sequence": [
            {
                "name": "Request-Response",
                "description": "Simple client-server interaction",
            },
            {
                "name": "Authentication Flow",
                "description": "Login process with validation",
            },
            {
                "name": "Error Handling",
                "description": "Exception and error response patterns",
            },
        ],
        "class": [
            {
                "name": "Inheritance Hierarchy",
                "description": "Parent-child class relationships",
            },
            {
                "name": "Composition Pattern",
                "description": "Classes containing other classes",
            },
            {
                "name": "Interface Implementation",
                "description": "Classes implementing interfaces",
            },
        ],
    }

    return patterns.get(diagram_type, [])


def _get_quick_reference_guide() -> dict[str, str]:
    """Get quick reference guide for all diagram types."""
    return {
        "flowchart": "flowchart TD; A[Start] --> B{Decision} --> C[End]",
        "sequence": "sequenceDiagram; A->>B: Message; B-->>A: Response",
        "class": "classDiagram; class A { +method() }; A <|-- B",
        "state": "stateDiagram-v2; [*] --> A; A --> B; B --> [*]",
        "er": "erDiagram; A { id int }; A ||--o{ B : has",
        "journey": "journey; title: Journey; section: Step; Task: 5: Actor",
        "gantt": "gantt; title: Project; Task: 2024-01-01, 5d",
        "pie": "pie title: Data; 'A': 50; 'B': 30; 'C': 20",
        "gitgraph": "gitgraph; commit; branch dev; commit; merge dev",
        "mindmap": "mindmap; root((Topic)); Branch1; Branch2",
        "timeline": "timeline; title: Events; 2024: Event1: Description",
    }


@measure_performance
def update_configuration(
    key: str,
    value: Any,
) -> dict[str, Any]:
    """
    Update configuration settings with validation.

    This tool allows updating mermaid-render configuration settings with
    comprehensive validation to ensure the new values are valid and safe.
    Provides detailed feedback about the changes made.

    Args:
        key: Configuration key to update
        value: New value for the configuration key

    Returns:
        Dictionary containing update results and metadata

    Example:
        >>> result = update_configuration("default_theme", "dark")
        >>> print(result["data"]["updated"])  # True
        >>> print(result["data"]["old_value"])  # Previous value
    """
    try:
        # Validate parameters
        params = ConfigurationParams(key=key, value=value)

        # Get current configuration
        config = MermaidConfig()
        all_config = config.to_dict()

        if params.key not in all_config:
            return create_error_response(
                ValueError(f"Configuration key '{params.key}' not found"),
                ErrorCategory.CONFIGURATION,
                context={"available_keys": list(all_config.keys())},
                suggestions=[
                    f"Use one of the available keys: {', '.join(list(all_config.keys())[:5])}..."
                ],
            )

        # Store old value
        old_value = all_config[params.key]
        old_type = type(old_value).__name__

        # Validate new value type compatibility
        if not _validate_config_value(params.key, params.value):
            return create_error_response(
                ValueError(
                    f"Invalid value type for '{params.key}'. Expected {old_type}, got {type(params.value).__name__}"
                ),
                ErrorCategory.VALIDATION,
                context={
                    "expected_type": old_type,
                    "provided_type": type(params.value).__name__,
                },
                suggestions=[f"Provide a value of type {old_type}"],
            )

        # Update configuration
        config.set(params.key, params.value)

        # Prepare response data
        update_data = {
            "updated": True,
            "key": params.key,
            "old_value": old_value,
            "new_value": params.value,
            "value_type": type(params.value).__name__,
            "description": _get_config_description(params.key),
        }

        # Enhanced metadata
        metadata = {
            "update_timestamp": __import__("datetime").datetime.now().isoformat(),
            "config_source": "MermaidConfig",
            "validation_passed": True,
        }

        return create_success_response(data=update_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return create_error_response(
            e,
            ErrorCategory.CONFIGURATION,
            suggestions=[
                "Check configuration key and value are valid",
                "Verify configuration system is writable",
            ],
        )


@measure_performance
def list_available_templates(
    template_name: str | None = None,
    category: str | None = None,
    include_builtin: bool = True,
    include_custom: bool = True,
) -> dict[str, Any]:
    """
    List all available diagram templates with filtering and categorization.

    This tool provides comprehensive information about all available templates,
    including built-in and custom templates, with filtering capabilities and
    detailed metadata about each template.

    Args:
        template_name: Filter by specific template name
        category: Filter by template category
        include_builtin: Include built-in templates in results
        include_custom: Include custom templates in results

    Returns:
        Dictionary containing template list and metadata

    Example:
        >>> result = list_available_templates()
        >>> print(result["data"]["templates"])  # List of all templates
        >>> result = list_available_templates(category="flowchart")
        >>> print(result["data"]["filtered_count"])  # Number of flowchart templates
    """
    try:
        # Validate parameters
        params = TemplateManagementParams(
            template_name=template_name,
            category=category,
            include_builtin=include_builtin,
            include_custom=include_custom,
        )

        # Check if templates module is available
        try:
            from ..templates import TemplateManager
        except ImportError:
            return create_error_response(
                ImportError("Template functionality not available"),
                ErrorCategory.TEMPLATE,
                suggestions=[
                    "Install template support with: pip install mermaid-render[templates]"
                ],
            )

        # Get templates
        template_manager = TemplateManager()
        all_templates = []

        # Get built-in templates
        if params.include_builtin:
            try:
                from ..templates.library import BuiltInTemplates

                builtin_lib = BuiltInTemplates()
                builtin_templates = builtin_lib.get_all_templates()
                for template in builtin_templates:
                    template["source"] = "builtin"
                    all_templates.append(template)
            except Exception as e:
                logger.warning(f"Could not load built-in templates: {e}")

        # Get custom templates
        if params.include_custom:
            try:
                custom_templates = template_manager.list_templates()
                for template in custom_templates:  # type: ignore[assignment]
                    if hasattr(template, "to_dict"):
                        template_dict = template.to_dict()
                        template_dict["source"] = "custom"
                        all_templates.append(template_dict)
                    elif isinstance(template, dict):
                        template_dict = template.copy()
                        template_dict["source"] = "custom"
                        all_templates.append(template_dict)
                    else:
                        # Skip non-dict, non-template objects
                        pass
            except Exception as e:
                logger.warning(f"Could not load custom templates: {e}")

        # Apply filters
        filtered_templates = all_templates

        if params.template_name:
            filtered_templates = [
                t
                for t in filtered_templates
                if params.template_name.lower() in t.get("name", "").lower()
            ]

        if params.category:
            filtered_templates = [
                t
                for t in filtered_templates
                if t.get("diagram_type") == params.category
            ]

        # Enhanced metadata
        metadata = {
            "total_templates": len(all_templates),
            "filtered_count": len(filtered_templates),
            "builtin_count": len(
                [t for t in all_templates if t.get("source") == "builtin"]
            ),
            "custom_count": len(
                [t for t in all_templates if t.get("source") == "custom"]
            ),
            "categories": list(
                {t.get("diagram_type", "unknown") for t in all_templates}
            ),
            "filters_applied": {
                "template_name": params.template_name,
                "category": params.category,
                "include_builtin": params.include_builtin,
                "include_custom": params.include_custom,
            },
        }

        return create_success_response(
            data={
                "templates": filtered_templates,
                "summary": {
                    "total": len(filtered_templates),
                    "by_category": {
                        cat: len(
                            [
                                t
                                for t in filtered_templates
                                if t.get("diagram_type") == cat
                            ]
                        )
                        for cat in {
                            t.get("diagram_type", "unknown") for t in filtered_templates
                        }
                    },
                    "by_source": {
                        src: len(
                            [t for t in filtered_templates if t.get("source") == src]
                        )
                        for src in {
                            t.get("source", "unknown") for t in filtered_templates
                        }
                    },
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return create_error_response(
            e,
            ErrorCategory.TEMPLATE,
            suggestions=[
                "Check template system is properly configured",
                "Verify template directories are accessible",
            ],
        )


# Remaining tool implementations (basic versions)


@measure_performance
def get_system_information() -> dict[str, Any]:
    """
    Get system capabilities, version information, and available features.

    This tool provides comprehensive information about the mermaid-render system,
    including version details, available features, system capabilities, and
    configuration status.

    Returns:
        Dictionary containing system information and capabilities

    Example:
        >>> result = get_system_information()
        >>> print(result["data"]["version"])  # mermaid-render version
        >>> print(result["data"]["features"])  # Available features
    """
    try:
        import platform
        import sys

        from .. import __version__ as mermaid_version

        # Collect system information
        system_info = {
            "mermaid_render_version": mermaid_version,
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
        }

        # Check available features
        features = {
            "ai_support": False,
            "template_support": False,
            "cache_support": True,
            "interactive_support": False,
            "pdf_rendering": True,
            "png_rendering": True,
            "svg_rendering": True,
        }

        # Check AI support
        try:
            from ..ai import DiagramGenerator  # noqa: F401

            features["ai_support"] = True
        except ImportError:
            pass

        # Check template support
        try:
            from ..templates import TemplateManager  # noqa: F401

            features["template_support"] = True
        except ImportError:
            pass

        # Check interactive support
        try:
            from ..interactive import InteractiveServer  # noqa: F401

            features["interactive_support"] = True
        except ImportError:
            pass

        # Get renderer capabilities
        from ..renderers import RendererRegistry

        registry = RendererRegistry()
        available_renderers = registry.list_renderers()

        # Enhanced metadata
        metadata = {
            "system_check_timestamp": __import__("datetime").datetime.now().isoformat(),
            "feature_count": len([f for f in features.values() if f]),
            "renderer_count": len(available_renderers),
            "python_executable": sys.executable,
        }

        return create_success_response(
            data={
                "system": system_info,
                "features": features,
                "renderers": available_renderers,
                "capabilities": {
                    "max_diagram_size": "50KB",
                    "supported_formats": ["svg", "png", "pdf"],
                    "concurrent_renders": 10,
                    "cache_enabled": True,
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error getting system information: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            suggestions=[
                "Check system configuration",
                "Verify all dependencies are installed",
            ],
        )


@measure_performance
def save_diagram_to_file(
    diagram_code: str,
    file_path: str,
    output_format: str = "svg",
    theme: str | None = None,
    create_directories: bool = True,
    overwrite: bool = False,
) -> dict[str, Any]:
    """
    Save rendered diagram content to a file with path validation.

    This tool renders a diagram and saves it directly to a file with comprehensive
    path validation, directory creation, and error handling.

    Args:
        diagram_code: Mermaid diagram code to render and save
        file_path: File path where to save the diagram
        output_format: Output format (svg, png, pdf)
        theme: Theme to apply to the diagram
        create_directories: Create parent directories if they don't exist
        overwrite: Overwrite existing files

    Returns:
        Dictionary containing save operation results

    Example:
        >>> result = save_diagram_to_file(
        ...     "flowchart TD\\n    A[Start] --> B[End]",
        ...     "/path/to/diagram.svg",
        ...     "svg"
        ... )
        >>> print(result["data"]["saved"])  # True
        >>> print(result["data"]["file_size"])  # File size in bytes
    """
    try:
        # Validate parameters
        params = FileOperationParams(
            file_path=file_path,
            create_directories=create_directories,
            overwrite=overwrite,
        )

        # Validate file path
        file_path_obj = Path(params.file_path)

        # Check if file exists and overwrite is not allowed
        if file_path_obj.exists() and not params.overwrite:
            return create_error_response(
                FileExistsError(f"File already exists: {params.file_path}"),
                ErrorCategory.FILE_OPERATION,
                context={"file_path": params.file_path, "exists": True},
                suggestions=[
                    "Use overwrite=True to replace existing file",
                    "Choose a different file path",
                ],
            )

        # Create directories if needed
        if params.create_directories:
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Render the diagram first
        render_result = render_diagram(
            diagram_code=diagram_code, output_format=output_format, theme=theme
        )

        if not render_result.get("success"):
            return create_error_response(
                RuntimeError("Failed to render diagram"),
                ErrorCategory.RENDERING,
                context={"render_error": render_result.get("error")},
                suggestions=["Check diagram syntax", "Verify rendering parameters"],
            )

        # Get rendered content
        content = render_result["data"]["content"]
        is_binary = render_result["data"]["is_binary"]

        # Save to file
        if is_binary:
            import base64

            with open(file_path_obj, "wb") as f:
                f.write(base64.b64decode(content))
        else:
            with open(file_path_obj, "w", encoding="utf-8") as f:
                f.write(content)

        # Get file info
        file_size = file_path_obj.stat().st_size

        # Enhanced metadata
        metadata = {
            "save_timestamp": __import__("datetime").datetime.now().isoformat(),
            "file_path": str(file_path_obj.absolute()),
            "file_size_bytes": file_size,
            "output_format": output_format,
            "theme_used": theme or "default",
            "directories_created": params.create_directories,
        }

        return create_success_response(
            data={
                "saved": True,
                "file_path": str(file_path_obj.absolute()),
                "file_size": file_size,
                "format": output_format,
                "encoding": "binary" if is_binary else "utf-8",
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error saving diagram to file: {e}")
        return create_error_response(
            e,
            ErrorCategory.FILE_OPERATION,
            context={"file_path": file_path, "format": output_format},
            suggestions=[
                "Check file path permissions",
                "Verify directory exists",
                "Check disk space",
            ],
        )


@measure_performance
def batch_render_diagrams(
    diagrams: list[dict[str, Any]],
    parallel: bool = True,
    max_workers: int = 4,
) -> dict[str, Any]:
    """
    Render multiple diagrams efficiently with parallel processing.

    This tool renders multiple diagrams in batch with optional parallel processing
    for improved performance. Provides detailed progress tracking and error handling
    for individual diagrams.

    Args:
        diagrams: List of diagram specifications with code, format, theme, etc.
        parallel: Enable parallel processing for better performance
        max_workers: Maximum number of parallel workers

    Returns:
        Dictionary containing batch render results and statistics

    Example:
        >>> diagrams = [
        ...     {"code": "flowchart TD\\n    A --> B", "format": "svg"},
        ...     {"code": "sequenceDiagram\\n    A->>B: Hello", "format": "png"}
        ... ]
        >>> result = batch_render_diagrams(diagrams)
        >>> print(result["data"]["success_count"])  # Number of successful renders
    """
    try:
        # Validate parameters
        params = BatchRenderParams(
            diagrams=diagrams, parallel=parallel, max_workers=max_workers
        )

        if not params.diagrams:
            return create_error_response(
                ValueError("No diagrams provided for batch rendering"),
                ErrorCategory.VALIDATION,
                suggestions=["Provide at least one diagram specification"],
            )

        results = []
        success_count = 0
        error_count = 0
        start_time = __import__("time").time()

        if params.parallel and len(params.diagrams) > 1:
            # Parallel processing
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=params.max_workers
            ) as executor:
                # Submit all rendering tasks
                future_to_diagram = {
                    executor.submit(
                        render_diagram,
                        diagram_code=diagram.get("code", ""),
                        output_format=diagram.get("format", "svg"),
                        theme=diagram.get("theme"),
                        validate_syntax=diagram.get("validate", True),
                    ): i
                    for i, diagram in enumerate(params.diagrams)
                }

                # Collect results
                for future in concurrent.futures.as_completed(future_to_diagram):
                    diagram_index = future_to_diagram[future]
                    try:
                        result = future.result()
                        results.append(
                            {
                                "index": diagram_index,
                                "success": result.get("success", False),
                                "result": result,
                                "diagram_spec": params.diagrams[diagram_index],
                            }
                        )
                        if result.get("success"):
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        results.append(
                            {
                                "index": diagram_index,
                                "success": False,
                                "error": str(e),
                                "diagram_spec": params.diagrams[diagram_index],
                            }
                        )
                        error_count += 1
        else:
            # Sequential processing
            for i, diagram in enumerate(params.diagrams):
                try:
                    result = render_diagram(
                        diagram_code=diagram.get("code", ""),
                        output_format=diagram.get("format", "svg"),
                        theme=diagram.get("theme"),
                        validate_syntax=diagram.get("validate", True),
                    )
                    results.append(
                        {
                            "index": i,
                            "success": result.get("success", False),
                            "result": result,
                            "diagram_spec": diagram,
                        }
                    )
                    if result.get("success"):
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    results.append(
                        {
                            "index": i,
                            "success": False,
                            "error": str(e),
                            "diagram_spec": diagram,
                        }
                    )
                    error_count += 1

        # Sort results by index to maintain order
        results.sort(key=lambda x: x["index"])

        end_time = __import__("time").time()
        total_time = end_time - start_time

        # Enhanced metadata
        metadata = {
            "batch_timestamp": __import__("datetime").datetime.now().isoformat(),
            "total_diagrams": len(params.diagrams),
            "processing_mode": "parallel" if params.parallel else "sequential",
            "max_workers": params.max_workers if params.parallel else 1,
            "total_time_seconds": total_time,
            "average_time_per_diagram": (
                total_time / len(params.diagrams) if params.diagrams else 0
            ),
        }

        return create_success_response(
            data={
                "results": results,
                "summary": {
                    "total": len(params.diagrams),
                    "success_count": success_count,
                    "error_count": error_count,
                    "success_rate": (
                        success_count / len(params.diagrams) if params.diagrams else 0
                    ),
                    "total_time": total_time,
                    "processing_mode": "parallel" if params.parallel else "sequential",
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error in batch rendering: {e}")
        return create_error_response(
            e,
            ErrorCategory.RENDERING,
            context={"diagram_count": len(diagrams) if diagrams else 0},
            suggestions=[
                "Check diagram specifications",
                "Reduce batch size",
                "Try sequential processing",
            ],
        )


@measure_performance
def manage_cache_operations(
    operation: str,
    cache_key: str | None = None,
) -> dict[str, Any]:
    """
    Manage cache operations including clear, stats, and cleanup.

    This tool provides comprehensive cache management capabilities including
    cache statistics, selective clearing, and maintenance operations with
    detailed reporting.

    Args:
        operation: Cache operation to perform (stats, clear, clear_all, cleanup)
        cache_key: Specific cache key for targeted operations

    Returns:
        Dictionary containing cache operation results and statistics

    Example:
        >>> result = manage_cache_operations("stats")
        >>> print(result["data"]["cache_size"])  # Current cache size
        >>> result = manage_cache_operations("clear", "diagram_abc123")
        >>> print(result["data"]["cleared"])  # True if cleared successfully
    """
    try:
        # Validate parameters
        params = CacheManagementParams(operation=operation, cache_key=cache_key)

        # Get cache manager
        try:
            from ..cache import CacheManager

            cache_manager = CacheManager()
        except ImportError:
            return create_error_response(
                ImportError("Cache functionality not available"),
                ErrorCategory.CACHE,
                suggestions=["Check cache system configuration"],
            )

        operation_result = {}

        if params.operation == "stats":
            # Get cache statistics
            stats = cache_manager.get_stats()
            operation_result = {
                "operation": "stats",
                "cache_enabled": hasattr(cache_manager, "backend")
                and cache_manager.backend is not None,
                "cache_size": stats.get("size", 0),
                "entry_count": stats.get("count", 0),
                "hit_rate": stats.get("hit_rate", 0.0),
                "miss_rate": stats.get("miss_rate", 0.0),
                "cache_directory": (
                    str(cache_manager.cache_dir)
                    if hasattr(cache_manager, "cache_dir")
                    else None
                ),
                "max_size": stats.get("max_size", "unlimited"),
                "last_cleanup": stats.get("last_cleanup", "never"),
            }

        elif params.operation == "clear":
            if params.cache_key:
                # Clear specific cache entry
                cleared = cache_manager.delete(params.cache_key)
                operation_result = {
                    "operation": "clear",
                    "cache_key": params.cache_key,
                    "cleared": cleared,
                    "message": f"Cache key '{params.cache_key}' {'cleared' if cleared else 'not found'}",
                }
            else:
                return create_error_response(
                    ValueError("cache_key required for clear operation"),
                    ErrorCategory.VALIDATION,
                    suggestions=[
                        "Provide cache_key parameter",
                        "Use clear_all to clear entire cache",
                    ],
                )

        elif params.operation == "clear_all":
            # Clear entire cache
            cleared_count = cache_manager.clear()
            operation_result = {
                "operation": "clear_all",
                "cleared_entries": cleared_count,
                "message": f"Cleared {cleared_count} cache entries",
            }

        elif params.operation == "cleanup":
            # Perform cache cleanup (remove expired entries)
            # Use clear with no tags to clean up all entries
            cleaned_count = cache_manager.clear()
            operation_result = {
                "operation": "cleanup",
                "cleaned_entries": cleaned_count,
                "message": f"Cleaned up {cleaned_count} expired cache entries",
            }

        else:
            return create_error_response(
                ValueError(f"Unknown cache operation: {params.operation}"),
                ErrorCategory.VALIDATION,
                context={
                    "supported_operations": ["stats", "clear", "clear_all", "cleanup"]
                },
                suggestions=["Use one of: stats, clear, clear_all, cleanup"],
            )

        # Enhanced metadata
        metadata = {
            "operation_timestamp": __import__("datetime").datetime.now().isoformat(),
            "cache_system": "CacheManager",
            "operation_type": params.operation,
            "cache_enabled": (
                cache_manager.is_enabled()
                if hasattr(cache_manager, "is_enabled")
                else True
            ),
        }

        return create_success_response(data=operation_result, metadata=metadata)

    except Exception as e:
        logger.error(f"Error in cache management: {e}")
        return create_error_response(
            e,
            ErrorCategory.CACHE,
            context={"operation": operation, "cache_key": cache_key},
            suggestions=[
                "Check cache system is properly configured",
                "Verify cache permissions",
            ],
        )


# Additional tools from additional_tools.py


@measure_performance
def get_template_details(
    template_name: str,
) -> dict[str, Any]:
    """
    Get detailed information about a specific template.

    This tool provides comprehensive information about a template including
    its parameters, schema, examples, and usage instructions.

    Args:
        template_name: Name or ID of the template

    Returns:
        Dictionary containing detailed template information

    Example:
        >>> result = get_template_details("software_architecture")
        >>> print(result["data"]["parameters"])  # Template parameters
        >>> print(result["data"]["examples"])    # Usage examples
    """
    try:
        # Check if templates module is available
        try:
            from ..templates import TemplateManager
        except ImportError:
            return create_error_response(
                ImportError("Template functionality not available"),
                ErrorCategory.TEMPLATE,
                suggestions=[
                    "Install template support with: pip install mermaid-render[templates]"
                ],
            )

        # Get template details
        template_manager = TemplateManager()
        template = template_manager.get_template_by_name(template_name)

        if not template:
            # Try by ID
            template = template_manager.get_template(template_name)

        if not template:
            return create_error_response(
                ValueError(f"Template '{template_name}' not found"),
                ErrorCategory.TEMPLATE,
                context={"requested_template": template_name},
                suggestions=[
                    "Check template name spelling",
                    "Use list_available_templates to see available templates",
                ],
            )

        # Get template examples if available
        examples = []
        try:
            from ..templates.utils import get_template_examples

            examples = get_template_examples(template_name, template_manager)
        except Exception as e:
            logger.warning(f"Could not load template examples: {e}")

        # Prepare detailed template information
        template_data = {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "diagram_type": template.diagram_type,
            "parameters": template.parameters,
            "template_content": template.template_content,
            "metadata": template.metadata,
            "version": template.version,
            "author": template.author,
            "tags": template.tags or [],
            "created_at": (
                template.created_at.isoformat() if template.created_at else None
            ),
            "updated_at": (
                template.updated_at.isoformat() if template.updated_at else None
            ),
            "examples": examples,
            "usage_instructions": _generate_template_usage_instructions(template),
            "parameter_schema": _extract_parameter_schema(template.parameters),
        }

        # Enhanced metadata
        metadata = {
            "template_source": (
                "custom"
                if hasattr(template, "id") and template.id.startswith("custom")
                else "builtin"
            ),
            "parameter_count": len(template.parameters),
            "example_count": len(examples),
            "complexity_level": _assess_template_complexity(template),
            "last_accessed": __import__("datetime").datetime.now().isoformat(),
        }

        return create_success_response(data=template_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error getting template details: {e}")
        return create_error_response(
            e, ErrorCategory.TEMPLATE, context={"template_name": template_name}
        )


@measure_performance
def create_custom_template(
    name: str,
    diagram_type: str,
    template_content: str,
    parameters: dict[str, Any],
    description: str = "",
    author: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a new custom template with validation.

    This tool allows creation of custom diagram templates with comprehensive
    validation and automatic parameter schema generation.

    Args:
        name: Template name
        diagram_type: Type of diagram (flowchart, sequence, etc.)
        template_content: Jinja2 template content
        parameters: Parameter definitions
        description: Template description
        author: Template author
        tags: Template tags for categorization

    Returns:
        Dictionary containing created template information

    Example:
        >>> result = create_custom_template(
        ...     "my_flowchart",
        ...     "flowchart",
        ...     "flowchart TD\\n    {{start}} --> {{end}}",
        ...     {"start": {"type": "string"}, "end": {"type": "string"}},
        ...     "Simple flowchart template"
        ... )
        >>> print(result["data"]["template_id"])  # New template ID
    """
    try:
        # Check if templates module is available
        try:
            from ..templates import TemplateManager
        except ImportError:
            return create_error_response(
                ImportError("Template functionality not available"),
                ErrorCategory.TEMPLATE,
                suggestions=[
                    "Install template support with: pip install mermaid-render[templates]"
                ],
            )

        # Validate template content
        if not template_content.strip():
            return create_error_response(
                ValueError("Template content cannot be empty"),
                ErrorCategory.VALIDATION,
                suggestions=[
                    "Provide valid Jinja2 template content with Mermaid syntax"
                ],
            )

        # Create template
        template_manager = TemplateManager()
        template = template_manager.create_template(
            name=name,
            diagram_type=diagram_type,
            template_content=template_content,
            parameters=parameters,
            description=description,
            author=author,
            tags=tags or [],
        )

        # Prepare response data
        template_data = {
            "template_id": template.id,
            "name": template.name,
            "diagram_type": template.diagram_type,
            "description": template.description,
            "parameters": template.parameters,
            "author": template.author,
            "tags": template.tags,
            "created_at": template.created_at.isoformat(),
            "validation_status": "passed",
            "usage_example": _generate_template_usage_example(template),
        }

        # Enhanced metadata
        metadata = {
            "creation_timestamp": template.created_at.isoformat(),
            "parameter_count": len(parameters),
            "template_size_bytes": len(template_content),
            "complexity_score": _assess_template_complexity(template),
            "validation_passed": True,
        }

        return create_success_response(data=template_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error creating custom template: {e}")
        return create_error_response(
            e,
            ErrorCategory.TEMPLATE,
            context={
                "template_name": name,
                "diagram_type": diagram_type,
                "content_length": len(template_content) if template_content else 0,
            },
            suggestions=[
                "Check template syntax",
                "Verify parameter definitions",
                "Ensure diagram type is valid",
            ],
        )


@measure_performance
def list_diagram_types(
    diagram_type: str | None = None,
    include_examples: bool = True,
) -> dict[str, Any]:
    """
    List all supported diagram types with descriptions and capabilities.

    This tool provides comprehensive information about all supported Mermaid
    diagram types, including their capabilities, syntax patterns, and use cases.

    Args:
        diagram_type: Specific diagram type to get information for
        include_examples: Include example code for each diagram type

    Returns:
        Dictionary containing diagram type information and metadata

    Example:
        >>> result = list_diagram_types()
        >>> print(result["data"]["types"]["flowchart"]["description"])
        >>> result = list_diagram_types(diagram_type="sequence")
        >>> print(result["data"]["example_code"])  # Sequence diagram example
    """
    try:
        # Validate parameters
        params = DiagramTypeParams(
            diagram_type=diagram_type, include_examples=include_examples
        )

        # Define comprehensive diagram type information
        diagram_types = {
            "flowchart": {
                "name": "Flowchart",
                "description": "Process flow diagrams showing steps, decisions, and connections",
                "syntax_start": [
                    "flowchart TD",
                    "flowchart LR",
                    "graph TD",
                    "graph LR",
                ],
                "use_cases": [
                    "Process documentation",
                    "Decision trees",
                    "Workflow visualization",
                ],
                "complexity": "simple",
                "node_types": [
                    "rectangles",
                    "diamonds",
                    "circles",
                    "rounded rectangles",
                ],
                "supports_subgraphs": True,
                "supports_styling": True,
            },
            "sequence": {
                "name": "Sequence Diagram",
                "description": "Interaction diagrams showing message exchanges between participants",
                "syntax_start": ["sequenceDiagram"],
                "use_cases": [
                    "API interactions",
                    "System communications",
                    "Protocol documentation",
                ],
                "complexity": "medium",
                "features": [
                    "participants",
                    "messages",
                    "activation boxes",
                    "notes",
                    "loops",
                ],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "class": {
                "name": "Class Diagram",
                "description": "UML class diagrams showing classes, attributes, methods, and relationships",
                "syntax_start": ["classDiagram"],
                "use_cases": [
                    "Software architecture",
                    "Object modeling",
                    "System design",
                ],
                "complexity": "complex",
                "features": [
                    "classes",
                    "attributes",
                    "methods",
                    "relationships",
                    "interfaces",
                ],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "state": {
                "name": "State Diagram",
                "description": "State machine diagrams showing states and transitions",
                "syntax_start": ["stateDiagram", "stateDiagram-v2"],
                "use_cases": ["State machines", "Workflow states", "System behavior"],
                "complexity": "medium",
                "features": [
                    "states",
                    "transitions",
                    "composite states",
                    "choice points",
                ],
                "supports_subgraphs": True,
                "supports_styling": True,
            },
            "er": {
                "name": "Entity Relationship Diagram",
                "description": "Database entity relationship diagrams",
                "syntax_start": ["erDiagram"],
                "use_cases": [
                    "Database design",
                    "Data modeling",
                    "Schema documentation",
                ],
                "complexity": "medium",
                "features": ["entities", "attributes", "relationships", "cardinality"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "journey": {
                "name": "User Journey",
                "description": "User journey mapping diagrams",
                "syntax_start": ["journey"],
                "use_cases": [
                    "User experience design",
                    "Customer journey mapping",
                    "Process analysis",
                ],
                "complexity": "simple",
                "features": ["sections", "tasks", "actors", "satisfaction scores"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "gantt": {
                "name": "Gantt Chart",
                "description": "Project timeline and task scheduling diagrams",
                "syntax_start": ["gantt"],
                "use_cases": [
                    "Project management",
                    "Timeline visualization",
                    "Task scheduling",
                ],
                "complexity": "medium",
                "features": ["tasks", "dependencies", "milestones", "sections"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "pie": {
                "name": "Pie Chart",
                "description": "Pie charts for data visualization",
                "syntax_start": ["pie"],
                "use_cases": ["Data visualization", "Proportion display", "Statistics"],
                "complexity": "simple",
                "features": ["data values", "labels", "percentages"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "gitgraph": {
                "name": "Git Graph",
                "description": "Git branching and merging visualization",
                "syntax_start": ["gitgraph"],
                "use_cases": [
                    "Git workflow documentation",
                    "Branch visualization",
                    "Version control",
                ],
                "complexity": "medium",
                "features": ["branches", "commits", "merges", "tags"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "mindmap": {
                "name": "Mind Map",
                "description": "Hierarchical mind maps for idea organization",
                "syntax_start": ["mindmap"],
                "use_cases": [
                    "Brainstorming",
                    "Idea organization",
                    "Knowledge mapping",
                ],
                "complexity": "simple",
                "features": ["root node", "branches", "sub-branches", "icons"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "timeline": {
                "name": "Timeline",
                "description": "Timeline diagrams for chronological events",
                "syntax_start": ["timeline"],
                "use_cases": [
                    "Historical timelines",
                    "Project milestones",
                    "Event sequences",
                ],
                "complexity": "simple",
                "features": ["periods", "events", "sections"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
        }

        # Filter by specific diagram type if requested
        if params.diagram_type:
            if params.diagram_type.value in diagram_types:
                filtered_types = {
                    params.diagram_type.value: diagram_types[params.diagram_type.value]
                }
            else:
                return create_error_response(
                    ValueError(
                        f"Diagram type '{params.diagram_type.value}' not supported"
                    ),
                    ErrorCategory.VALIDATION,
                    context={"supported_types": list(diagram_types.keys())},
                    suggestions=[f"Use one of: {', '.join(diagram_types.keys())}"],
                )
        else:
            filtered_types = diagram_types

        # Add examples if requested
        if params.include_examples:
            for type_name, type_info in filtered_types.items():
                type_info["example_code"] = _get_diagram_example(type_name)

        # Enhanced metadata
        metadata = {
            "total_types": len(diagram_types),
            "filtered_count": len(filtered_types),
            "complexity_distribution": {
                "simple": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("complexity") == "simple"
                    ]
                ),
                "medium": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("complexity") == "medium"
                    ]
                ),
                "complex": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("complexity") == "complex"
                    ]
                ),
            },
            "features_summary": {
                "supports_subgraphs": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("supports_subgraphs", False)
                    ]
                ),
                "supports_styling": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("supports_styling", False)
                    ]
                ),
            },
        }

        return create_success_response(
            data={
                "types": filtered_types,
                "summary": {
                    "total_supported": len(filtered_types),
                    "by_complexity": {
                        complexity: [
                            name
                            for name, info in filtered_types.items()
                            if info.get("complexity") == complexity
                        ]
                        for complexity in ["simple", "medium", "complex"]
                    },
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error listing diagram types: {e}")
        return create_error_response(
            e, ErrorCategory.SYSTEM, suggestions=["Check system configuration"]
        )


@measure_performance
def get_diagram_examples(
    diagram_type: str | None = None,
) -> dict[str, Any]:
    """
    Get example code and documentation for specific diagram types.

    This tool provides detailed examples and documentation for Mermaid diagram
    types, including syntax patterns, best practices, and common use cases.

    Args:
        diagram_type: Specific diagram type to get examples for

    Returns:
        Dictionary containing examples and documentation

    Example:
        >>> result = get_diagram_examples(diagram_type="flowchart")
        >>> print(result["data"]["example_code"])  # Flowchart example
        >>> print(result["data"]["best_practices"])  # Best practices
    """
    try:
        # Validate parameters
        params = DiagramTypeParams(diagram_type=diagram_type, include_examples=True)

        if params.diagram_type:
            # Get specific diagram type example
            example_code = _get_diagram_example(params.diagram_type.value)
            best_practices = _get_diagram_best_practices(params.diagram_type.value)

            example_data = {
                "diagram_type": params.diagram_type.value,
                "example_code": example_code,
                "best_practices": best_practices,
                "syntax_guide": _get_syntax_guide(params.diagram_type.value),
                "common_patterns": _get_common_patterns(params.diagram_type.value),
            }
        else:
            # Get examples for all diagram types
            all_examples: dict[str, dict[str, str]] = {}
            for dtype in [
                "flowchart",
                "sequence",
                "class",
                "state",
                "er",
                "journey",
                "gantt",
                "pie",
                "gitgraph",
                "mindmap",
                "timeline",
            ]:
                all_examples[dtype] = {
                    "example_code": _get_diagram_example(dtype),
                    "description": f"Example {dtype} diagram",
                }

            example_data = {
                "all_examples": all_examples,  # type: ignore[dict-item]
                "quick_reference": _get_quick_reference_guide(),
            }

        # Enhanced metadata
        metadata = {
            "examples_provided": (
                1
                if params.diagram_type
                else len(all_examples)
                if "all_examples" in locals()
                else 0
            ),
            "includes_best_practices": bool(params.diagram_type),
            "includes_syntax_guide": bool(params.diagram_type),
            "last_updated": "2024-01-01",  # Would be dynamic in real implementation
        }

        return create_success_response(data=example_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error getting diagram examples: {e}")
        return create_error_response(
            e, ErrorCategory.SYSTEM, suggestions=["Check diagram type is valid"]
        )
