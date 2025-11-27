"""
AI-powered MCP tools for mermaid-render.

This module provides AI-powered diagram generation and analysis tools.
"""

import logging
from typing import Any

try:
    from fastmcp import Context

    _FASTMCP_AVAILABLE = True
except ImportError:
    Context = None
    _FASTMCP_AVAILABLE = False

from .helpers import _detect_diagram_type
from .params import AnalyzeDiagramParams, GenerateDiagramParams, OptimizeDiagramParams

logger = logging.getLogger(__name__)


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
            from ...ai import AIdiagramType, DiagramGenerator, GenerationConfig
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
            from ...ai import DiagramOptimizer, OptimizationType  # noqa: F401
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
            from ...ai import DiagramAnalyzer
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
            from ...ai import SuggestionEngine

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
            from ...ai import SuggestionEngine
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
