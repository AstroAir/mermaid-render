"""
Diagram analysis prompts for MCP.

This module provides prompts for analyzing diagram quality and suggesting improvements.
"""

from .base import Context


def analyze_diagram_quality_prompt(
    diagram_code: str,
    diagram_type: str,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for analyzing diagram quality.

    Args:
        diagram_code: The Mermaid diagram code to analyze
        diagram_type: Type of diagram (flowchart, sequence, class, etc.)
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for diagram quality analysis
    """
    prompt = f"""Analyze the following {diagram_type} diagram for quality and best practices:

```mermaid
{diagram_code}
```

Please evaluate the diagram on the following criteria:

**Structure and Syntax:**
- Correct Mermaid syntax
- Proper use of diagram-specific elements
- Logical flow and organization

**Clarity and Readability:**
- Clear and descriptive labels
- Appropriate use of shapes and symbols
- Easy to follow flow or relationships

**Best Practices:**
- Follows {diagram_type} diagram conventions
- Appropriate level of detail
- Good visual hierarchy

**Potential Issues:**
- Syntax errors or warnings
- Unclear or ambiguous elements
- Missing connections or relationships

Provide a detailed analysis with specific recommendations for improvement."""

    return prompt


def suggest_improvements_prompt(
    diagram_code: str,
    current_issues: list[str],
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for suggesting diagram improvements.

    Args:
        diagram_code: The Mermaid diagram code
        current_issues: List of identified issues
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for improvement suggestions
    """
    issues_list = "\n".join([f"- {issue}" for issue in current_issues])

    prompt = f"""Suggest specific improvements for the following Mermaid diagram:

```mermaid
{diagram_code}
```

**Current Issues Identified:**
{issues_list}

Please provide:

1. **Specific Improvements:** Concrete suggestions to address each issue
2. **Enhanced Version:** An improved version of the diagram code
3. **Explanation:** Brief explanation of why each change improves the diagram
4. **Alternative Approaches:** If applicable, suggest alternative ways to represent the same information

Focus on making the diagram clearer, more accurate, and easier to understand while maintaining its core purpose."""

    return prompt
