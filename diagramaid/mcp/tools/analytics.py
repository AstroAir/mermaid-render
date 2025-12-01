"""
Analytics MCP tools for diagramaid.

This module provides diagram analysis and comparison tools with
FastMCP Context support for logging.
"""

import logging
from typing import Annotated, Any

try:
    from fastmcp import Context

    _FASTMCP_AVAILABLE = True
except ImportError:
    Context = None  # type: ignore
    _FASTMCP_AVAILABLE = False

from .base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
)
from .helpers import (
    _compare_edge_lists,
    _compare_lists,
    _detect_diagram_type,
    _extract_edges,
    _extract_nodes,
    _extract_styles,
    _extract_subgraphs,
)

logger = logging.getLogger(__name__)


async def extract_diagram_elements(
    diagram_code: Annotated[str, "Mermaid diagram code to analyze"],
    include_nodes: Annotated[bool, "Include node information"] = True,
    include_edges: Annotated[bool, "Include edge/connection information"] = True,
    include_styles: Annotated[bool, "Include style definitions"] = False,
    include_subgraphs: Annotated[bool, "Include subgraph information"] = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Extract nodes, edges, and other elements from a Mermaid diagram.

    This tool parses a Mermaid diagram and extracts its structural elements,
    providing detailed information about nodes, connections, and styling.

    Args:
        diagram_code: Mermaid diagram code to analyze
        include_nodes: Include node information in results
        include_edges: Include edge/connection information
        include_styles: Include style definitions
        include_subgraphs: Include subgraph information

    Returns:
        Dictionary containing extracted diagram elements

    Example:
        >>> result = await extract_diagram_elements("flowchart TD\\n    A[Start] --> B[End]")
        >>> print(result["data"]["nodes"])  # [{"id": "A", "label": "Start"}, ...]
        >>> print(result["data"]["edges"])  # [{"from": "A", "to": "B"}, ...]
    """
    try:
        import datetime

        if ctx:
            await ctx.info("Extracting diagram elements")

        diagram_type = _detect_diagram_type(diagram_code)
        elements: dict[str, Any] = {
            "diagram_type": diagram_type,
        }

        if include_nodes:
            elements["nodes"] = _extract_nodes(diagram_code)

        if include_edges:
            elements["edges"] = _extract_edges(diagram_code)

        if include_styles:
            elements["styles"] = _extract_styles(diagram_code)

        if include_subgraphs:
            elements["subgraphs"] = _extract_subgraphs(diagram_code)

        # Calculate statistics
        statistics = {
            "node_count": len(elements.get("nodes", [])),
            "edge_count": len(elements.get("edges", [])),
            "subgraph_count": len(elements.get("subgraphs", [])),
            "style_count": len(elements.get("styles", [])),
            "line_count": len(diagram_code.splitlines()),
            "character_count": len(diagram_code),
        }

        # Enhanced metadata
        metadata = {
            "extraction_timestamp": datetime.datetime.now().isoformat(),
            "diagram_type": diagram_type,
            "extraction_options": {
                "include_nodes": include_nodes,
                "include_edges": include_edges,
                "include_styles": include_styles,
                "include_subgraphs": include_subgraphs,
            },
        }

        if ctx:
            await ctx.info(f"Extracted {statistics['node_count']} nodes, {statistics['edge_count']} edges")

        return create_success_response(
            data={
                "elements": elements,
                "statistics": statistics,
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error extracting diagram elements: {e}")
        if ctx:
            await ctx.error(f"Extraction failed: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            context={"diagram_type": _detect_diagram_type(diagram_code)},
            suggestions=[
                "Check diagram syntax",
                "Ensure diagram type is supported",
            ],
        )


async def compare_diagrams(
    diagram1: Annotated[str, "First Mermaid diagram code"],
    diagram2: Annotated[str, "Second Mermaid diagram code"],
    comparison_type: Annotated[str, "Type: structural, visual, semantic"] = "structural",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Compare two Mermaid diagrams and identify differences.

    This tool analyzes two diagrams and provides a detailed comparison
    of their structure, nodes, edges, and other elements.

    Args:
        diagram1: First Mermaid diagram code
        diagram2: Second Mermaid diagram code
        comparison_type: Type of comparison (structural, visual, semantic)

    Returns:
        Dictionary containing comparison results and differences

    Example:
        >>> result = await compare_diagrams(
        ...     "flowchart TD\\n    A --> B",
        ...     "flowchart TD\\n    A --> B --> C"
        ... )
        >>> print(result["data"]["differences"])
    """
    try:
        import datetime

        if ctx:
            await ctx.info(f"Comparing diagrams using {comparison_type} comparison")

        valid_types = ["structural", "visual", "semantic"]
        if comparison_type not in valid_types:
            return create_error_response(
                ValueError(f"Invalid comparison type: {comparison_type}"),
                ErrorCategory.VALIDATION,
                context={"valid_types": valid_types},
                suggestions=[f"Use one of: {', '.join(valid_types)}"],
            )

        # Extract elements from both diagrams
        elements1 = {
            "type": _detect_diagram_type(diagram1),
            "nodes": _extract_nodes(diagram1),
            "edges": _extract_edges(diagram1),
            "subgraphs": _extract_subgraphs(diagram1),
        }

        elements2 = {
            "type": _detect_diagram_type(diagram2),
            "nodes": _extract_nodes(diagram2),
            "edges": _extract_edges(diagram2),
            "subgraphs": _extract_subgraphs(diagram2),
        }

        # Compare elements
        differences = {
            "type_match": elements1["type"] == elements2["type"],
            "nodes": _compare_lists(elements1["nodes"], elements2["nodes"], "id"),
            "edges": _compare_edge_lists(elements1["edges"], elements2["edges"]),
            "subgraphs": _compare_lists(
                elements1["subgraphs"], elements2["subgraphs"], "name"
            ),
        }

        # Calculate similarity score
        total_elements = (
            len(elements1["nodes"])
            + len(elements1["edges"])
            + len(elements2["nodes"])
            + len(elements2["edges"])
        )
        common_elements = (
            len(differences["nodes"]["common"]) * 2
            + len(differences["edges"]["common"]) * 2
        )
        similarity_score = (
            (common_elements / total_elements * 100) if total_elements > 0 else 100
        )

        # Summary
        summary = {
            "are_identical": (
                differences["type_match"]
                and not differences["nodes"]["only_in_first"]
                and not differences["nodes"]["only_in_second"]
                and not differences["edges"]["only_in_first"]
                and not differences["edges"]["only_in_second"]
            ),
            "similarity_score": round(similarity_score, 2),
            "diagram1_stats": {
                "nodes": len(elements1["nodes"]),
                "edges": len(elements1["edges"]),
                "subgraphs": len(elements1["subgraphs"]),
            },
            "diagram2_stats": {
                "nodes": len(elements2["nodes"]),
                "edges": len(elements2["edges"]),
                "subgraphs": len(elements2["subgraphs"]),
            },
        }

        # Enhanced metadata
        metadata = {
            "comparison_timestamp": datetime.datetime.now().isoformat(),
            "comparison_type": comparison_type,
            "diagram1_type": elements1["type"],
            "diagram2_type": elements2["type"],
        }

        if ctx:
            await ctx.info(f"Comparison complete: similarity score {similarity_score:.1f}%")

        return create_success_response(
            data={
                "summary": summary,
                "differences": differences,
                "diagram1_elements": elements1,
                "diagram2_elements": elements2,
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error comparing diagrams: {e}")
        if ctx:
            await ctx.error(f"Comparison failed: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            suggestions=[
                "Check both diagrams have valid syntax",
                "Ensure diagrams are of compatible types",
            ],
        )
