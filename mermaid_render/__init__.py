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


# Import convenience functions
from .convenience import quick_render, render_to_file
# Backward compatibility alias
render = quick_render
