"""
MCP prompts package for mermaid-render.

This package provides MCP prompt implementations organized into modules:
- base: Base utilities and FastMCP availability check
- generation: Diagram generation prompts (flowchart, sequence, class, etc.)
- analysis: Diagram analysis and quality prompts
- optimization: Layout optimization and simplification prompts
- documentation: Explanation and documentation prompts
- extended: Extended prompts for additional diagram types and operations
"""

from typing import Any

from .analysis import analyze_diagram_quality_prompt, suggest_improvements_prompt
from .base import _FASTMCP_AVAILABLE
from .documentation import (
    create_diagram_documentation_prompt,
    explain_diagram_prompt,
)
from .extended import (
    convert_to_diagram_prompt,
    document_architecture_prompt,
    generate_c4_diagram_prompt,
    generate_er_diagram_prompt,
    generate_gantt_chart_prompt,
    generate_git_graph_prompt,
    generate_mindmap_prompt,
    generate_pie_chart_prompt,
    generate_state_diagram_prompt,
    generate_timeline_prompt,
    refactor_diagram_prompt,
    translate_diagram_prompt,
)
from .generation import (
    generate_class_diagram_prompt,
    generate_flowchart_prompt,
    generate_sequence_prompt,
)
from .optimization import optimize_layout_prompt, simplify_diagram_prompt


def register_all_prompts(mcp: Any) -> None:
    """
    Register all MCP prompts with the FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    # Diagram generation prompts
    mcp.prompt(
        name="generate_flowchart",
        description="Generate a flowchart diagram from a process description",
        tags={"generation", "flowchart"},
    )(generate_flowchart_prompt)

    mcp.prompt(
        name="generate_sequence",
        description="Generate a sequence diagram from an interaction description",
        tags={"generation", "sequence"},
    )(generate_sequence_prompt)

    mcp.prompt(
        name="generate_class_diagram",
        description="Generate a class diagram from a system description",
        tags={"generation", "class"},
    )(generate_class_diagram_prompt)

    # Analysis prompts
    mcp.prompt(
        name="analyze_diagram_quality",
        description="Analyze a diagram for quality and best practices",
        tags={"analysis", "quality"},
    )(analyze_diagram_quality_prompt)

    mcp.prompt(
        name="suggest_improvements",
        description="Suggest improvements for a diagram",
        tags={"analysis", "suggestions"},
    )(suggest_improvements_prompt)

    # Optimization prompts
    mcp.prompt(
        name="optimize_layout",
        description="Optimize diagram layout for better readability",
        tags={"optimization", "layout"},
    )(optimize_layout_prompt)

    mcp.prompt(
        name="simplify_diagram",
        description="Simplify a complex diagram while preserving key information",
        tags={"optimization", "simplification"},
    )(simplify_diagram_prompt)

    # Documentation prompts
    mcp.prompt(
        name="explain_diagram",
        description="Generate an explanation of what a diagram represents",
        tags={"documentation", "explanation"},
    )(explain_diagram_prompt)

    mcp.prompt(
        name="create_diagram_documentation",
        description="Create comprehensive documentation for a diagram",
        tags={"documentation", "comprehensive"},
    )(create_diagram_documentation_prompt)


def register_extended_prompts(mcp: Any) -> None:
    """
    Register extended MCP prompts with the FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    # ER Diagram prompt
    mcp.prompt(
        name="generate_er_diagram",
        description="Generate an Entity-Relationship diagram from database description",
        tags={"generation", "er", "database"},
    )(generate_er_diagram_prompt)

    # State Diagram prompt
    mcp.prompt(
        name="generate_state_diagram",
        description="Generate a State diagram from state machine description",
        tags={"generation", "state", "fsm"},
    )(generate_state_diagram_prompt)

    # Gantt Chart prompt
    mcp.prompt(
        name="generate_gantt_chart",
        description="Generate a Gantt chart from project description",
        tags={"generation", "gantt", "project"},
    )(generate_gantt_chart_prompt)

    # Mind Map prompt
    mcp.prompt(
        name="generate_mindmap",
        description="Generate a Mind Map from topic description",
        tags={"generation", "mindmap", "brainstorm"},
    )(generate_mindmap_prompt)

    # Timeline prompt
    mcp.prompt(
        name="generate_timeline",
        description="Generate a Timeline diagram from events description",
        tags={"generation", "timeline", "history"},
    )(generate_timeline_prompt)

    # Pie Chart prompt
    mcp.prompt(
        name="generate_pie_chart",
        description="Generate a Pie Chart from data description",
        tags={"generation", "pie", "data"},
    )(generate_pie_chart_prompt)

    # Git Graph prompt
    mcp.prompt(
        name="generate_git_graph",
        description="Generate a Git Graph from workflow description",
        tags={"generation", "git", "version_control"},
    )(generate_git_graph_prompt)

    # C4 Diagram prompt
    mcp.prompt(
        name="generate_c4_diagram",
        description="Generate a C4 architecture diagram from system description",
        tags={"generation", "c4", "architecture"},
    )(generate_c4_diagram_prompt)

    # Refactor Diagram prompt
    mcp.prompt(
        name="refactor_diagram",
        description="Refactor and improve an existing Mermaid diagram",
        tags={"refactoring", "improvement", "optimization"},
    )(refactor_diagram_prompt)

    # Translate Diagram prompt
    mcp.prompt(
        name="translate_diagram",
        description="Translate diagram labels to another language",
        tags={"translation", "localization", "i18n"},
    )(translate_diagram_prompt)

    # Convert to Diagram prompt
    mcp.prompt(
        name="convert_to_diagram",
        description="Convert other formats (JSON, YAML, CSV, text) to Mermaid diagrams",
        tags={"conversion", "import", "transform"},
    )(convert_to_diagram_prompt)

    # Document Architecture prompt
    mcp.prompt(
        name="document_architecture",
        description="Create comprehensive architecture documentation with multiple diagrams",
        tags={"documentation", "architecture", "comprehensive"},
    )(document_architecture_prompt)


__all__ = [
    # Registration functions
    "register_all_prompts",
    "register_extended_prompts",
    # Generation prompts
    "generate_flowchart_prompt",
    "generate_sequence_prompt",
    "generate_class_diagram_prompt",
    # Analysis prompts
    "analyze_diagram_quality_prompt",
    "suggest_improvements_prompt",
    # Optimization prompts
    "optimize_layout_prompt",
    "simplify_diagram_prompt",
    # Documentation prompts
    "explain_diagram_prompt",
    "create_diagram_documentation_prompt",
    # Extended prompts
    "generate_er_diagram_prompt",
    "generate_state_diagram_prompt",
    "generate_gantt_chart_prompt",
    "generate_mindmap_prompt",
    "generate_timeline_prompt",
    "generate_pie_chart_prompt",
    "generate_git_graph_prompt",
    "generate_c4_diagram_prompt",
    "refactor_diagram_prompt",
    "translate_diagram_prompt",
    "convert_to_diagram_prompt",
    "document_architecture_prompt",
]
