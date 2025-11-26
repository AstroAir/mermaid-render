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
    EnhancementResult,
    EnhancementType,
    QualityMetrics,
)

# Import compatibility wrappers for backward compatibility
from .compatibility import (
    DiagramOptimizer,
    LayoutOptimizer,
    OptimizationResult,
    OptimizationType,
    StyleOptimizer,
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
from .providers import (
    AIProvider,
    AnthropicProvider,
    AuthenticationError,
    CustomProvider,
    CustomProviderConfig,
    GenerationResponse,
    LocalModelProvider,
    ModelNotFoundError,
    OpenAIProvider,
    OpenRouterProvider,
    ProviderConfig,
    ProviderError,
    ProviderFactory,
    ProviderManager,
    RateLimitError,
    create_default_provider_manager,
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
    batch_generate_diagrams,
    classify_intent,
    compare_provider_performance,
    create_custom_provider_config,
    create_openrouter_provider,
    create_provider_from_config,
    enhance_diagram_all,
    enhance_diagram_layout,
    enhance_diagram_style,
    export_provider_config,
    extract_entities,
    generate_from_text,
    generate_with_multiple_providers,
    get_enhancement_suggestions,
    get_suggestions,
    optimize_diagram,
    setup_multi_provider_generation,
    validate_diagram_with_ai,
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
    # Optimization (backward compatibility)
    "DiagramOptimizer",
    "LayoutOptimizer",
    "StyleOptimizer",
    "OptimizationResult",
    "OptimizationType",
    # Enhancement (new integrated functionality)
    "EnhancementResult",
    "EnhancementType",
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
    "OpenRouterProvider",
    "LocalModelProvider",
    "CustomProvider",
    # Provider configuration and management
    "ProviderConfig",
    "CustomProviderConfig",
    "ProviderFactory",
    "ProviderManager",
    "GenerationResponse",
    "create_default_provider_manager",
    # Provider exceptions
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "ModelNotFoundError",
    # Utilities
    "generate_from_text",
    "optimize_diagram",
    "analyze_diagram",
    "get_suggestions",
    "extract_entities",
    "classify_intent",
    # Enhanced utilities
    "batch_generate_diagrams",
    "compare_provider_performance",
    "create_custom_provider_config",
    "create_openrouter_provider",
    "create_provider_from_config",
    "enhance_diagram_all",
    "enhance_diagram_layout",
    "enhance_diagram_style",
    "export_provider_config",
    "generate_with_multiple_providers",
    "get_enhancement_suggestions",
    "setup_multi_provider_generation",
    "validate_diagram_with_ai",
]
