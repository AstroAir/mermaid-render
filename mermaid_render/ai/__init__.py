"""
AI-powered diagram generation and optimization for Mermaid Render.

This package provides comprehensive AI capabilities including natural language
to diagram conversion, intelligent optimization, automated layout, and smart
suggestions for diagram improvement.

Features:
- Natural language to Mermaid diagram conversion
- Intelligent diagram optimization and layout
- Automated diagram generation from various data sources
- Smart suggestions for diagram improvements
- AI-powered diagram analysis and insights
- Integration with multiple AI providers (OpenAI, Anthropic, etc.)
- Custom model training and fine-tuning capabilities
- Semantic understanding of diagram content

Example:
    >>> from mermaid_render.ai import DiagramGenerator, NLProcessor
    >>>
    >>> # Generate diagram from natural language
    >>> generator = DiagramGenerator()
    >>> diagram = generator.from_text(
    ...     "Create a flowchart showing the user login process"
    ... )
    >>>
    >>> # Optimize existing diagram
    >>> optimizer = DiagramOptimizer()
    >>> optimized = optimizer.optimize_layout(diagram)
    >>>
    >>> # Get AI suggestions
    >>> suggestions = generator.get_suggestions(diagram)
"""

from .analysis import (
    AnalysisReport,
    ComplexityAnalysis,
    DiagramAnalyzer,
    QualityMetrics,
)
from .diagram_generator import (
    DiagramGenerator,
    GenerationConfig,
    GenerationResult,
)
from .diagram_generator import (
    DiagramType as AIdiagramType,
)
from .nl_processor import (
    EntityExtraction,
    IntentClassification,
    NLProcessor,
    TextAnalysis,
)
from .optimization import (
    DiagramOptimizer,
    LayoutOptimizer,
    OptimizationResult,
    StyleOptimizer,
)
from .providers import (
    AIProvider,
    AnthropicProvider,
    LocalModelProvider,
    OpenAIProvider,
)
from .suggestions import (
    Suggestion,
    SuggestionEngine,
    SuggestionPriority,
    SuggestionType,
)

# Convenience functions
from .utils import (
    analyze_diagram,
    classify_intent,
    extract_entities,
    generate_from_text,
    get_suggestions,
    optimize_diagram,
)

__all__ = [
    # Core generation
    "DiagramGenerator",
    "GenerationConfig",
    "GenerationResult",
    "AIdiagramType",
    # Natural language processing
    "NLProcessor",
    "TextAnalysis",
    "EntityExtraction",
    "IntentClassification",
    # Optimization
    "DiagramOptimizer",
    "LayoutOptimizer",
    "StyleOptimizer",
    "OptimizationResult",
    # Suggestions
    "SuggestionEngine",
    "Suggestion",
    "SuggestionType",
    "SuggestionPriority",
    # Analysis
    "DiagramAnalyzer",
    "ComplexityAnalysis",
    "QualityMetrics",
    "AnalysisReport",
    # AI providers
    "AIProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalModelProvider",
    # Utilities
    "generate_from_text",
    "optimize_diagram",
    "analyze_diagram",
    "get_suggestions",
    "extract_entities",
    "classify_intent",
]
