"""
Diagram documentation prompts for MCP.

This module provides prompts for explaining and documenting diagrams.
"""

from .base import Context


def explain_diagram_prompt(
    diagram_code: str,
    audience_level: str = "general",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for explaining what a diagram represents.

    Args:
        diagram_code: The Mermaid diagram code to explain
        audience_level: Target audience level (beginner, intermediate, expert, general)
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for diagram explanation
    """
    audience_guidance = {
        "beginner": "Use simple language, explain technical terms, provide context for concepts",
        "intermediate": "Use standard terminology, focus on key relationships and processes",
        "expert": "Use technical language, focus on implementation details and nuances",
        "general": "Use accessible language, balance detail with clarity",
    }

    prompt = f"""Explain what the following Mermaid diagram represents:

```mermaid
{diagram_code}
```

**Target Audience:** {audience_level}
**Explanation Style:** {audience_guidance.get(audience_level, audience_guidance["general"])}

Please provide:

1. **Overview:** What the diagram shows at a high level
2. **Key Components:** Explanation of main elements and their roles
3. **Relationships/Flow:** How the components interact or connect
4. **Purpose/Use Case:** What this diagram would typically be used for
5. **Important Details:** Any notable features or patterns in the diagram

Make the explanation clear and appropriate for the target audience."""

    return prompt


def create_diagram_documentation_prompt(
    diagram_code: str,
    diagram_title: str,
    context: str = "",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating comprehensive diagram documentation.

    Args:
        diagram_code: The Mermaid diagram code
        diagram_title: Title for the diagram
        context: Additional context about the diagram's purpose
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for comprehensive documentation
    """
    context_section = ""
    if context:
        context_section = f"""
**Context:** {context}"""

    prompt = f"""Create comprehensive documentation for the following Mermaid diagram:

**Title:** {diagram_title}{context_section}

```mermaid
{diagram_code}
```

Please provide complete documentation including:

1. **Executive Summary:** Brief overview of what the diagram represents
2. **Detailed Description:** Comprehensive explanation of all components
3. **Component Glossary:** Definition of each element, symbol, or term used
4. **Process Flow/Relationships:** Step-by-step walkthrough of the flow or relationships
5. **Use Cases:** When and how this diagram would be used
6. **Assumptions and Constraints:** Any assumptions made or limitations
7. **Related Diagrams:** Suggestions for complementary diagrams
8. **Maintenance Notes:** How to keep this diagram current and accurate

Format the documentation in a clear, professional manner suitable for technical documentation."""

    return prompt
