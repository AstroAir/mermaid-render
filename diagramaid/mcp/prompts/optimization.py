"""
Diagram optimization prompts for MCP.

This module provides prompts for optimizing diagram layout and simplification.
"""

from .base import Context


def simplify_diagram_prompt(
    diagram_code: str,
    target_complexity: str = "simple",
    preserve_elements: list[str] | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for simplifying a complex diagram.

    Args:
        diagram_code: The Mermaid diagram code to simplify
        target_complexity: Target complexity level (simple, moderate)
        preserve_elements: List of elements that must be preserved
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for diagram simplification
    """
    preserve_list = ""
    if preserve_elements:
        preserve_list = f"""
**Elements to Preserve:**
{chr(10).join([f"- {element}" for element in preserve_elements])}"""

    complexity_guidance = {
        "simple": "Reduce to 3-5 main elements, combine related steps, remove non-essential details",
        "moderate": "Reduce to 5-8 main elements, group related processes, simplify complex relationships",
    }

    prompt = f"""Simplify the following Mermaid diagram while preserving its core meaning:

```mermaid
{diagram_code}
```

**Target Complexity:** {target_complexity}
**Simplification Guidelines:** {complexity_guidance.get(target_complexity, complexity_guidance["simple"])}{preserve_list}

Please provide:

1. **Simplified Version:** A cleaner, simpler version of the diagram
2. **Simplification Strategy:** Explain what was removed or combined and why
3. **Key Information Preserved:** Confirm that essential information is maintained
4. **Readability Improvements:** Describe how the simplification improves readability

The goal is to make the diagram easier to understand at a glance while retaining its essential purpose."""

    return prompt


def optimize_layout_prompt(
    diagram_code: str,
    optimization_goals: list[str],
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for optimizing diagram layout.

    Args:
        diagram_code: The Mermaid diagram code
        optimization_goals: List of optimization goals
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for layout optimization
    """
    goals_list = "\n".join([f"- {goal}" for goal in optimization_goals])

    prompt = f"""Optimize the layout of the following Mermaid diagram:

```mermaid
{diagram_code}
```

**Optimization Goals:**
{goals_list}

Please provide:

1. **Layout Analysis:** Identify current layout issues or inefficiencies
2. **Optimized Version:** Improved diagram with better layout
3. **Layout Techniques:** Explain the layout techniques used
4. **Visual Improvements:** Describe how the changes improve visual clarity

Focus on creating a more visually appealing and easier to read diagram while preserving all information."""

    return prompt
