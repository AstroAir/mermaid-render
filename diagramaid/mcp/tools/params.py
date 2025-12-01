"""
Parameter models for MCP tools.

This module provides Pydantic parameter models and enums for tool validation.
"""

from typing import Any

from .base import _FASTMCP_AVAILABLE

if _FASTMCP_AVAILABLE:
    from enum import Enum

    from pydantic import BaseModel, Field

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
        cache_key: str | None = Field(
            default=None,
            description="Specific cache key for targeted operations",
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
