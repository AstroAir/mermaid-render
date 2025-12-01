"""
AI-powered MCP tools for diagramaid.

This module provides AI-powered diagram generation and analysis tools
with full FastMCP Context support for logging, progress reporting,
and LLM sampling.
"""

import logging
from typing import Annotated, Any

try:
    from fastmcp import Context

    _FASTMCP_AVAILABLE = True
except ImportError:
    Context = None  # type: ignore
    _FASTMCP_AVAILABLE = False

from .helpers import _detect_diagram_type
from .params import AnalyzeDiagramParams, GenerateDiagramParams, OptimizeDiagramParams

logger = logging.getLogger(__name__)


async def generate_diagram_from_text(
    text_description: Annotated[str, "Natural language description of the diagram"],
    diagram_type: Annotated[str, "Type: auto, flowchart, sequence, class, etc."] = "auto",
    style_preference: Annotated[str, "Style: clean, detailed, minimal"] = "clean",
    complexity_level: Annotated[str, "Complexity: simple, medium, complex"] = "medium",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Generate a Mermaid diagram from natural language text using AI.

    Uses FastMCP Context for logging and progress reporting.

    Args:
        text_description: Natural language description of the diagram
        diagram_type: Type of diagram to generate (auto, flowchart, sequence, class, etc.)
        style_preference: Style preference (clean, detailed, minimal)
        complexity_level: Complexity level (simple, medium, complex)
        ctx: FastMCP Context for logging and progress (injected automatically)

    Returns:
        Dictionary containing generated diagram and metadata
    """
    try:
        if ctx:
            await ctx.info(f"Generating {diagram_type} diagram from text description")
            await ctx.report_progress(progress=0, total=100)

        # Validate parameters
        params = GenerateDiagramParams(
            text_description=text_description,
            diagram_type=diagram_type,
            style_preference=style_preference,
            complexity_level=complexity_level,
        )

        if ctx:
            await ctx.debug(f"Parameters validated: type={diagram_type}, style={style_preference}")
            await ctx.report_progress(progress=20, total=100)

        # Check if AI module is available
        try:
            from ...ai import AIdiagramType, DiagramGenerator, GenerationConfig
        except ImportError:
            if ctx:
                await ctx.error("AI functionality not available")
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install diagramaid[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        if ctx:
            await ctx.report_progress(progress=40, total=100)

        # Create generation configuration
        config = GenerationConfig(
            diagram_type=AIdiagramType(params.diagram_type),
            style_preference=params.style_preference,
            complexity_level=params.complexity_level,
        )

        # Generate diagram
        generator = DiagramGenerator()
        result = generator.from_text(params.text_description, config)

        if ctx:
            await ctx.report_progress(progress=90, total=100)
            await ctx.info(f"Generated {result.diagram_type.value} diagram with confidence {result.confidence_score:.2f}")

        response = {
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

        if ctx:
            await ctx.report_progress(progress=100, total=100)

        return response

    except Exception as e:
        logger.error(f"Error generating diagram from text: {e}")
        if ctx:
            await ctx.error(f"Generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


async def optimize_diagram(
    diagram_code: Annotated[str, "Mermaid diagram code to optimize"],
    optimization_type: Annotated[str, "Type: layout, style, structure"] = "layout",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Optimize a Mermaid diagram for better readability and performance using AI.

    Uses FastMCP Context for logging and progress reporting.

    Args:
        diagram_code: Mermaid diagram code to optimize
        optimization_type: Type of optimization (layout, style, structure)
        ctx: FastMCP Context for logging and progress (injected automatically)

    Returns:
        Dictionary containing optimized diagram and changes made
    """
    try:
        if ctx:
            await ctx.info(f"Optimizing diagram with {optimization_type} optimization")
            await ctx.report_progress(progress=0, total=100)

        # Validate parameters
        params = OptimizeDiagramParams(
            diagram_code=diagram_code, optimization_type=optimization_type
        )

        if ctx:
            await ctx.report_progress(progress=20, total=100)

        # Check if AI module is available
        try:
            from ...ai import DiagramOptimizer, OptimizationType  # noqa: F401
        except ImportError:
            if ctx:
                await ctx.error("AI functionality not available")
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install diagramaid[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        if ctx:
            await ctx.report_progress(progress=40, total=100)

        # Optimize diagram
        optimizer = DiagramOptimizer()
        results = optimizer.optimize_all(params.diagram_code)
        # Use the first result for backward compatibility
        result = results[0] if results else None

        if ctx:
            await ctx.report_progress(progress=80, total=100)

        if result:
            if ctx:
                await ctx.info(f"Optimization complete: {len(result.improvements)} improvements")
                await ctx.report_progress(progress=100, total=100)
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
            if ctx:
                await ctx.warning("No optimization results available")
            return {
                "success": False,
                "error": "No optimization results available",
                "request_id": ctx.request_id if ctx else None,
            }

    except Exception as e:
        logger.error(f"Error optimizing diagram: {e}")
        if ctx:
            await ctx.error(f"Optimization failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


async def analyze_diagram(
    diagram_code: Annotated[str, "Mermaid diagram code to analyze"],
    include_suggestions: Annotated[bool, "Include improvement suggestions"] = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Analyze a Mermaid diagram and provide metrics, insights, and quality assessment.

    Uses FastMCP Context for logging and progress reporting.

    Args:
        diagram_code: Mermaid diagram code to analyze
        include_suggestions: Include improvement suggestions
        ctx: FastMCP Context for logging and progress (injected automatically)

    Returns:
        Dictionary containing analysis results and insights
    """
    try:
        if ctx:
            await ctx.info("Analyzing diagram structure and quality")
            await ctx.report_progress(progress=0, total=100)

        # Validate parameters
        params = AnalyzeDiagramParams(
            diagram_code=diagram_code, include_suggestions=include_suggestions
        )

        if ctx:
            await ctx.report_progress(progress=20, total=100)

        # Check if AI module is available
        try:
            from ...ai import DiagramAnalyzer
        except ImportError:
            if ctx:
                await ctx.error("AI functionality not available")
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install diagramaid[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        if ctx:
            await ctx.report_progress(progress=40, total=100)

        # Analyze diagram
        analyzer = DiagramAnalyzer()
        result = analyzer.analyze(params.diagram_code)

        if ctx:
            await ctx.report_progress(progress=70, total=100)

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

        if ctx:
            await ctx.info(f"Analysis complete: {len(result.issues)} issues, {len(result.recommendations)} recommendations")
            await ctx.report_progress(progress=100, total=100)

        return response

    except Exception as e:
        logger.error(f"Error analyzing diagram: {e}")
        if ctx:
            await ctx.error(f"Analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


async def get_diagram_suggestions(
    diagram_code: Annotated[str, "Mermaid diagram code to analyze"],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Get AI-powered suggestions for improving a Mermaid diagram.

    Uses FastMCP Context for logging.

    Args:
        diagram_code: Mermaid diagram code to analyze
        ctx: FastMCP Context for logging (injected automatically)

    Returns:
        Dictionary containing improvement suggestions
    """
    try:
        if ctx:
            await ctx.info("Getting diagram improvement suggestions")

        # Check if AI module is available
        try:
            from ...ai import SuggestionEngine
        except ImportError:
            if ctx:
                await ctx.error("AI functionality not available")
            return {
                "success": False,
                "error": "AI functionality not available. Install with: pip install diagramaid[ai]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        # Get suggestions
        suggestion_engine = SuggestionEngine()
        suggestions = suggestion_engine.get_suggestions(diagram_code)

        if ctx:
            await ctx.info(f"Found {len(suggestions)} suggestions")

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
        if ctx:
            await ctx.error(f"Suggestions failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }
