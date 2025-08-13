"""
Mermaid Render - A comprehensive Python library for generating Mermaid diagrams.

This library provides a clean, well-documented interface for creating Mermaid diagrams
with support for multiple output formats, validation, theming, and configuration management.

Example:
    >>> from mermaid_render import MermaidRenderer, FlowchartDiagram
    >>>
    >>> # Create a simple flowchart
    >>> flowchart = FlowchartDiagram()
    >>> flowchart.add_node("A", "Start")
    >>> flowchart.add_node("B", "Process")
    >>> flowchart.add_edge("A", "B")
    >>>
    >>> # Render to SVG
    >>> renderer = MermaidRenderer()
    >>> svg_content = renderer.render(flowchart, format="svg")
    >>>
    >>> # Save to file
    >>> renderer.save(flowchart, "diagram.png", format="png")
"""

from typing import TYPE_CHECKING, Union

# Configuration and themes
from .config import ConfigManager, ThemeManager

# Core classes
from .core import MermaidConfig, MermaidDiagram, MermaidRenderer, MermaidTheme
from .enhanced_renderer import EnhancedMermaidRenderer
from .exceptions import (
    CacheError,
    ConfigurationError,
    DataSourceError,
    DiagramError,
    ErrorAggregator,
    MermaidRenderError,
    RenderingError,
    TemplateError,
    ThemeError,
    UnsupportedFormatError,
    ValidationError,
)

# Diagram models
from .models import (
    ClassDiagram,
    ERDiagram,
    FlowchartDiagram,
    GanttDiagram,
    GitGraphDiagram,
    MindmapDiagram,
    PieChartDiagram,
    SequenceDiagram,
    StateDiagram,
    TimelineDiagram,
    UserJourneyDiagram,
)

# Utilities
from .utils import (
    export_to_file,
    get_available_themes,
    get_supported_formats,
    validate_mermaid_syntax,
)

# Validators
from .validators import MermaidValidator, ValidationResult

# Template system (optional)
try:
    from .templates import (
        ArchitectureGenerator,
        ClassDiagramGenerator,
        FlowchartGenerator,
        ProcessFlowGenerator,
        SequenceGenerator,
        Template,
        TemplateManager,
        generate_from_template,
        get_template_info,
        list_available_templates,
    )

    _TEMPLATES_AVAILABLE = True
except ImportError:
    _TEMPLATES_AVAILABLE = False

# Cache system (optional)
try:
    from .cache import (  # type: ignore[import-not-found]
        CacheManager,
        FileBackend,
        MemoryBackend,
        PerformanceMonitor,
        RedisBackend,
        clear_cache,
        create_cache_manager,
        get_cache_stats,
        optimize_cache,
        warm_cache,
    )

    _CACHE_AVAILABLE = True
except ImportError:
    _CACHE_AVAILABLE = False

# Interactive builder (optional)
try:
    from .interactive import (
        DiagramBuilder,
        InteractiveServer,
        create_interactive_session,
        start_server,
    )

    _INTERACTIVE_AVAILABLE = True
except ImportError:
    _INTERACTIVE_AVAILABLE = False

# Collaboration (optional)
try:
    from .collaboration import (
        CollaborationManager,
        VersionControl,
        commit_diagram_changes,
        create_collaborative_session,
    )

    _COLLABORATION_AVAILABLE = True
except ImportError:
    _COLLABORATION_AVAILABLE = False

# AI-powered features (optional)
try:
    from .ai import (
        DiagramAnalyzer,
        DiagramGenerator,
        DiagramOptimizer,
        NLProcessor,
        SuggestionEngine,
        analyze_diagram,
        generate_from_text,
        get_suggestions,
        optimize_diagram,
    )

    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Dict, List, Optional, Union

__version__ = "1.0.0"
__author__ = "Mermaid Render Team"
__email__ = "contact@mermaid-render.dev"
__license__ = "MIT"

# Public API
__all__ = [
    # Core classes
    "MermaidRenderer",
    "EnhancedMermaidRenderer",
    "MermaidDiagram",
    "MermaidTheme",
    "MermaidConfig",
    # Exceptions
    "MermaidRenderError",
    "ValidationError",
    "RenderingError",
    "ConfigurationError",
    "UnsupportedFormatError",
    "TemplateError",
    "DiagramError",
    "ThemeError",
    "DataSourceError",
    "CacheError",
    "ErrorAggregator",
    # Diagram models
    "FlowchartDiagram",
    "SequenceDiagram",
    "ClassDiagram",
    "StateDiagram",
    "ERDiagram",
    "UserJourneyDiagram",
    "GanttDiagram",
    "PieChartDiagram",
    "GitGraphDiagram",
    "MindmapDiagram",
    "TimelineDiagram",
    # Validators
    "MermaidValidator",
    "ValidationResult",
    # Configuration and themes
    "ThemeManager",
    "ConfigManager",
    # Utilities
    "export_to_file",
    "validate_mermaid_syntax",
    "get_supported_formats",
    "get_available_themes",
    # Template system
    "TemplateManager",
    "Template",
    "generate_from_template",
    "list_available_templates",
    "get_template_info",
    "FlowchartGenerator",
    "SequenceGenerator",
    "ClassDiagramGenerator",
    "ArchitectureGenerator",
    "ProcessFlowGenerator",
    # Cache system
    "CacheManager",
    "MemoryBackend",
    "FileBackend",
    "RedisBackend",
    "PerformanceMonitor",
    "create_cache_manager",
    "warm_cache",
    "clear_cache",
    "get_cache_stats",
    "optimize_cache",
    # Interactive builder
    "DiagramBuilder",
    "InteractiveServer",
    "start_server",
    "create_interactive_session",
    # Collaboration
    "CollaborationManager",
    "VersionControl",
    "create_collaborative_session",
    "commit_diagram_changes",
    # AI-powered features
    "DiagramGenerator",
    "NLProcessor",
    "DiagramOptimizer",
    "SuggestionEngine",
    "DiagramAnalyzer",
    "generate_from_text",
    "optimize_diagram",
    "analyze_diagram",
    "get_suggestions",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]


def quick_render(
    diagram_code: str,
    output_path: "Optional[Union[str, Path]]" = None,
    format: str = "svg",
    theme: "Optional[str]" = None,
    config: "Optional[Dict[str, Any]]" = None,
) -> Union[str, bytes]:
    """
    Quick utility function to render Mermaid diagram code.

    This is a convenience function that provides a simple interface for rendering
    Mermaid diagrams without needing to create renderer instances. It handles
    validation, rendering, and optional file output in a single call.

    Args:
        diagram_code (str): Raw Mermaid diagram syntax. Must be valid Mermaid code
            following the official Mermaid syntax specification.
        output_path (Optional[Union[str, Path]], optional): Path to save the rendered
            diagram. If provided, the diagram will be saved to this file. The file
            extension is ignored - format is determined by the format parameter.
            Defaults to None (no file output).
        format (str, optional): Output format for the rendered diagram. Supported
            formats are:
            - "svg": Scalable Vector Graphics (default, best for web)
            - "png": Portable Network Graphics (good for documents)
            - "pdf": Portable Document Format (best for printing)
            Defaults to "svg".
        theme (Optional[str], optional): Theme name to apply to the diagram.
            Available built-in themes include:
            - "default": Standard Mermaid theme
            - "dark": Dark theme with light text
            - "forest": Green-based theme
            - "neutral": Neutral colors
            - "base": Minimal styling
            Defaults to None (uses default theme).
        config (Optional[Dict[str, Any]], optional): Additional configuration options
            to pass to the renderer. Can include timeout, validation settings, etc.
            Defaults to None.

    Returns:
        Union[str, bytes]: Rendered diagram content. Returns str for SVG format,
        bytes for PNG and PDF formats.

    Raises:
        ValidationError: If the diagram code contains syntax errors or is invalid
            according to Mermaid specifications.
        RenderingError: If the rendering process fails due to network issues,
            server errors, or other rendering problems.
        UnsupportedFormatError: If the specified format is not supported by the
            current installation or configuration.
        FileNotFoundError: If output_path directory doesn't exist.
        PermissionError: If unable to write to the specified output_path.

    Examples:
        Basic SVG rendering:
        >>> svg_content = quick_render('''
        ... flowchart TD
        ...     A[Start] --> B[Process]
        ...     B --> C[End]
        ... ''')
        >>> print(type(svg_content))
        <class 'str'>

        Render with theme and save to file:
        >>> quick_render('''
        ... sequenceDiagram
        ...     Alice->>Bob: Hello Bob!
        ...     Bob-->>Alice: Hello Alice!
        ... ''', output_path="sequence.png", format="png", theme="dark")

        Render with custom configuration:
        >>> config = {"timeout": 60, "validate_syntax": True}
        >>> pdf_content = quick_render('''
        ... classDiagram
        ...     Animal <|-- Duck
        ...     Animal <|-- Fish
        ... ''', format="pdf", config=config)

        Error handling:
        >>> try:
        ...     result = quick_render("invalid mermaid syntax")
        ... except ValidationError as e:
        ...     print(f"Invalid diagram: {e}")
    """
    from .core import MermaidRenderer
    from .validators import MermaidValidator

    # Validate the diagram code
    validator = MermaidValidator()
    validation_result = validator.validate(diagram_code)
    if not validation_result.is_valid:
        raise ValidationError(f"Invalid diagram code: {validation_result.errors}")

    # Create renderer with optional theme and config
    renderer_config = MermaidConfig()
    if config:
        renderer_config.update(config)

    renderer = MermaidRenderer(config=renderer_config)

    if theme:
        renderer.set_theme(theme)

    # Render the diagram
    content = renderer.render_raw(diagram_code, format=format)

    # Save to file if path provided
    if output_path:
        with open(output_path, "w" if format == "svg" else "wb") as f:
            if format == "svg":
                f.write(content)
            else:
                f.write(content.encode() if isinstance(content, str) else content)

    return content


# Convenience function for backward compatibility
render = quick_render
