"""Utility functions for AI-powered features."""

from typing import Any, Dict, List, Optional

from .analysis import DiagramAnalyzer
from .diagram_generator import DiagramGenerator, GenerationConfig
from .nl_processor import NLProcessor
from .optimization import DiagramOptimizer
from .suggestions import SuggestionEngine


def generate_from_text(
    text: str,
    diagram_type: str = "auto",
    style_preference: str = "clean",
    complexity_level: str = "medium",
) -> Dict[str, Any]:
    """
    Generate diagram from natural language text.

    Args:
        text: Natural language description
        diagram_type: Type of diagram to generate
        style_preference: Style preference (clean, detailed, minimal)
        complexity_level: Complexity level (simple, medium, complex)

    Returns:
        Generation result dictionary
    """
    from .diagram_generator import DiagramType

    config = GenerationConfig(
        diagram_type=DiagramType(diagram_type),
        style_preference=style_preference,
        complexity_level=complexity_level,
    )

    generator = DiagramGenerator()
    result = generator.from_text(text, config)

    return result.to_dict()


def optimize_diagram(
    diagram_code: str,
    optimization_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Optimize diagram using AI-powered optimization.

    Args:
        diagram_code: Mermaid diagram code
        optimization_types: Types of optimization to apply

    Returns:
        List of optimization results
    """
    optimizer = DiagramOptimizer()

    if optimization_types is None:
        optimization_types = ["layout", "style"]

    results = []

    if "layout" in optimization_types:
        layout_result = optimizer.optimize_layout(diagram_code)
        results.append(layout_result.to_dict())

    if "style" in optimization_types:
        style_result = optimizer.optimize_style(diagram_code)
        results.append(style_result.to_dict())

    return results


def analyze_diagram(
    diagram_code: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze diagram quality and complexity.

    Args:
        diagram_code: Mermaid diagram code
        context: Additional context about the diagram

    Returns:
        Analysis report dictionary
    """
    analyzer = DiagramAnalyzer()
    report = analyzer.analyze(diagram_code, context)

    return report.to_dict()


def get_suggestions(
    diagram_code: str,
    suggestion_types: Optional[List[str]] = None,
    priority_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get AI-powered suggestions for diagram improvement.

    Args:
        diagram_code: Mermaid diagram code
        suggestion_types: Types of suggestions to get
        priority_filter: Filter by priority (low, medium, high, critical)

    Returns:
        List of suggestion dictionaries
    """
    from .suggestions import SuggestionPriority, SuggestionType

    engine = SuggestionEngine()

    if suggestion_types:
        suggestions = []
        for suggestion_type in suggestion_types:
            type_suggestions = engine.get_suggestions_by_type(
                diagram_code, SuggestionType(suggestion_type)
            )
            suggestions.extend(type_suggestions)
    else:
        suggestions = engine.get_suggestions(diagram_code)

    # Filter by priority if specified
    if priority_filter:
        priority = SuggestionPriority(priority_filter)
        suggestions = [s for s in suggestions if s.priority == priority]

    return [s.to_dict() for s in suggestions]


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract entities from natural language text.

    Args:
        text: Input text

    Returns:
        Entity extraction result dictionary
    """
    processor = NLProcessor()
    entities = processor.extract_entities(text)

    return entities.to_dict()


def classify_intent(text: str) -> Dict[str, Any]:
    """
    Classify intent of natural language text.

    Args:
        text: Input text

    Returns:
        Intent classification result dictionary
    """
    processor = NLProcessor()
    intent = processor.classify_intent(text)

    return intent.to_dict()


def improve_diagram_with_ai(
    diagram_code: str,
    improvement_request: str,
    style_preference: str = "clean",
) -> Dict[str, Any]:
    """
    Improve existing diagram based on AI suggestions.

    Args:
        diagram_code: Current diagram code
        improvement_request: Description of desired improvements
        style_preference: Style preference for improvements

    Returns:
        Improvement result dictionary
    """
    config = GenerationConfig(style_preference=style_preference)

    generator = DiagramGenerator()
    result = generator.improve_diagram(diagram_code, improvement_request, config)

    return result.to_dict()


def get_diagram_insights(diagram_code: str) -> Dict[str, Any]:
    """
    Get comprehensive insights about a diagram.

    Args:
        diagram_code: Mermaid diagram code

    Returns:
        Comprehensive insights dictionary
    """
    # Analyze diagram
    analyzer = DiagramAnalyzer()
    analysis = analyzer.analyze(diagram_code)

    # Get suggestions
    suggestion_engine = SuggestionEngine()
    suggestions = suggestion_engine.get_suggestions(diagram_code)

    # Get optimization recommendations
    optimizer = DiagramOptimizer()
    optimization_suggestions = optimizer.get_optimization_suggestions(diagram_code)

    return {
        "analysis": analysis.to_dict(),
        "suggestions": [s.to_dict() for s in suggestions],
        "optimization_suggestions": optimization_suggestions,
        "summary": {
            "complexity_level": analysis.complexity.complexity_level,
            "overall_quality": analysis.quality.overall_score,
            "main_issues": analysis.issues[:3],  # Top 3 issues
            "top_recommendations": analysis.recommendations[
                :3
            ],  # Top 3 recommendations
        },
    }


def validate_ai_generated_diagram(diagram_code: str) -> Dict[str, Any]:
    """
    Validate AI-generated diagram for quality and correctness.

    Args:
        diagram_code: Generated diagram code

    Returns:
        Validation result dictionary
    """
    from ..validators import MermaidValidator

    # Basic syntax validation
    validator = MermaidValidator()
    syntax_result = validator.validate(diagram_code)

    # AI quality analysis
    analyzer = DiagramAnalyzer()
    quality_analysis = analyzer.analyze(diagram_code)

    # Determine overall validity
    is_valid = (
        syntax_result.is_valid
        and quality_analysis.quality.overall_score > 0.5
        and len(quality_analysis.issues) < 3
    )

    return {
        "is_valid": is_valid,
        "syntax_validation": {
            "is_valid": syntax_result.is_valid,
            "errors": syntax_result.errors,
            "warnings": syntax_result.warnings,
        },
        "quality_analysis": quality_analysis.to_dict(),
        "validation_score": (
            (1.0 if syntax_result.is_valid else 0.0) * 0.4
            + quality_analysis.quality.overall_score * 0.6
        ),
    }


def generate_diagram_variations(
    base_diagram: str,
    variation_count: int = 3,
) -> List[Dict[str, Any]]:
    """
    Generate variations of a base diagram.

    Args:
        base_diagram: Base diagram code
        variation_count: Number of variations to generate

    Returns:
        List of diagram variations
    """
    generator = DiagramGenerator()
    variations = []

    variation_requests = [
        "Make this diagram more detailed",
        "Simplify this diagram",
        "Improve the visual styling",
        "Add more descriptive labels",
        "Reorganize the layout",
    ]

    for i in range(min(variation_count, len(variation_requests))):
        try:
            result = generator.improve_diagram(base_diagram, variation_requests[i])
            variations.append(
                {
                    "variation_id": i + 1,
                    "description": variation_requests[i],
                    "diagram_code": result.diagram_code,
                    "confidence": result.confidence_score,
                }
            )
        except Exception:
            # Skip failed variations
            continue

    return variations
