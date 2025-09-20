"""
MCP prompts implementation for mermaid-render.

This module provides MCP (Model Context Protocol) prompt implementations
that provide reusable templates for diagram generation and analysis.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from fastmcp import FastMCP, Context
    from fastmcp.prompts.prompt import Message, PromptMessage, TextContent
    _FASTMCP_AVAILABLE = True
except ImportError:
    # Allow importing for testing without FastMCP
    FastMCP = None
    Context = None
    Message = None
    PromptMessage = None
    TextContent = None
    _FASTMCP_AVAILABLE = False

logger = logging.getLogger(__name__)


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
        tags={"generation", "flowchart"}
    )(generate_flowchart_prompt)
    
    mcp.prompt(
        name="generate_sequence",
        description="Generate a sequence diagram from an interaction description",
        tags={"generation", "sequence"}
    )(generate_sequence_prompt)
    
    mcp.prompt(
        name="generate_class_diagram",
        description="Generate a class diagram from a system description",
        tags={"generation", "class"}
    )(generate_class_diagram_prompt)
    
    # Analysis prompts
    mcp.prompt(
        name="analyze_diagram_quality",
        description="Analyze a diagram for quality and best practices",
        tags={"analysis", "quality"}
    )(analyze_diagram_quality_prompt)
    
    mcp.prompt(
        name="suggest_improvements",
        description="Suggest improvements for a diagram",
        tags={"analysis", "suggestions"}
    )(suggest_improvements_prompt)
    
    # Optimization prompts
    mcp.prompt(
        name="optimize_layout",
        description="Optimize diagram layout for better readability",
        tags={"optimization", "layout"}
    )(optimize_layout_prompt)
    
    mcp.prompt(
        name="simplify_diagram",
        description="Simplify a complex diagram while preserving key information",
        tags={"optimization", "simplification"}
    )(simplify_diagram_prompt)
    
    # Documentation prompts
    mcp.prompt(
        name="explain_diagram",
        description="Generate an explanation of what a diagram represents",
        tags={"documentation", "explanation"}
    )(explain_diagram_prompt)
    
    mcp.prompt(
        name="create_diagram_documentation",
        description="Create comprehensive documentation for a diagram",
        tags={"documentation", "comprehensive"}
    )(create_diagram_documentation_prompt)
    
    logger.info("Registered all MCP prompts")


def generate_flowchart_prompt(
    process_description: str,
    complexity_level: str = "medium",
    include_decision_points: bool = True,
    ctx: Optional[Context] = None,
) -> str:
    """
    Generate a prompt for creating a flowchart diagram.
    
    Args:
        process_description: Description of the process to diagram
        complexity_level: Complexity level (simple, medium, complex)
        include_decision_points: Whether to include decision points
        ctx: MCP context (optional)
        
    Returns:
        Formatted prompt for flowchart generation
    """
    decision_guidance = ""
    if include_decision_points:
        decision_guidance = """
- Include decision points (diamond shapes) where the process branches
- Use clear Yes/No or condition-based labels on decision branches
- Ensure all decision paths lead to appropriate outcomes"""
    
    complexity_guidance = {
        "simple": "Keep the flowchart simple with 3-7 main steps",
        "medium": "Include 5-12 steps with some decision points and parallel processes",
        "complex": "Create a detailed flowchart with multiple decision points, parallel processes, and sub-processes"
    }
    
    prompt = f"""Create a Mermaid flowchart diagram for the following process:

**Process Description:** {process_description}

**Requirements:**
- Use flowchart TD (top-down) or LR (left-right) direction as appropriate
- {complexity_guidance.get(complexity_level, complexity_guidance["medium"])}
- Use appropriate node shapes:
  - Rectangles [text] for process steps
  - Diamonds {{text}} for decisions
  - Rounded rectangles ([text]) for start/end points
  - Circles ((text)) for connectors if needed{decision_guidance}
- Use clear, concise labels for each step
- Ensure the flow is logical and easy to follow

Please generate only the Mermaid code without additional explanation."""
    
    return prompt


def generate_sequence_prompt(
    interaction_description: str,
    participants: List[str],
    include_notes: bool = False,
    ctx: Optional[Context] = None,
) -> str:
    """
    Generate a prompt for creating a sequence diagram.
    
    Args:
        interaction_description: Description of the interactions
        participants: List of participants/actors
        include_notes: Whether to include explanatory notes
        ctx: MCP context (optional)
        
    Returns:
        Formatted prompt for sequence diagram generation
    """
    participants_list = "\n".join([f"- {p}" for p in participants])
    
    notes_guidance = ""
    if include_notes:
        notes_guidance = """
- Add notes to explain complex interactions or important details
- Use 'note over' or 'note left/right of' as appropriate"""
    
    prompt = f"""Create a Mermaid sequence diagram for the following interaction:

**Interaction Description:** {interaction_description}

**Participants:**
{participants_list}

**Requirements:**
- Start with 'sequenceDiagram'
- Define all participants at the beginning
- Use appropriate arrow types:
  - ->> for synchronous calls
  - -->> for responses
  - -x for calls that don't return
  - --x for responses that don't return
- Show the sequence of interactions chronologically
- Include activation boxes where appropriate{notes_guidance}
- Use clear, descriptive message labels

Please generate only the Mermaid code without additional explanation."""
    
    return prompt


def generate_class_diagram_prompt(
    system_description: str,
    include_methods: bool = True,
    include_relationships: bool = True,
    ctx: Optional[Context] = None,
) -> str:
    """
    Generate a prompt for creating a class diagram.
    
    Args:
        system_description: Description of the system to model
        include_methods: Whether to include methods in classes
        include_relationships: Whether to show relationships between classes
        ctx: MCP context (optional)
        
    Returns:
        Formatted prompt for class diagram generation
    """
    methods_guidance = ""
    if include_methods:
        methods_guidance = """
- Include key methods for each class
- Use appropriate visibility indicators: + (public), - (private), # (protected)"""
    
    relationships_guidance = ""
    if include_relationships:
        relationships_guidance = """
- Show relationships between classes:
  - <|-- for inheritance
  - *-- for composition
  - o-- for aggregation
  - --> for association
  - ..> for dependency"""
    
    prompt = f"""Create a Mermaid class diagram for the following system:

**System Description:** {system_description}

**Requirements:**
- Start with 'classDiagram'
- Define classes with their attributes
- Use proper syntax: class ClassName {{ attributes and methods }}{methods_guidance}{relationships_guidance}
- Use clear, meaningful class and attribute names
- Group related classes logically

Please generate only the Mermaid code without additional explanation."""
    
    return prompt


def analyze_diagram_quality_prompt(
    diagram_code: str,
    diagram_type: str,
    ctx: Optional[Context] = None,
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


def simplify_diagram_prompt(
    diagram_code: str,
    target_complexity: str = "simple",
    preserve_elements: Optional[List[str]] = None,
    ctx: Optional[Context] = None,
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
        "moderate": "Reduce to 5-8 main elements, group related processes, simplify complex relationships"
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


def explain_diagram_prompt(
    diagram_code: str,
    audience_level: str = "general",
    ctx: Optional[Context] = None,
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
        "general": "Use accessible language, balance detail with clarity"
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
    ctx: Optional[Context] = None,
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


def suggest_improvements_prompt(
    diagram_code: str,
    current_issues: List[str],
    ctx: Optional[Context] = None,
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


def optimize_layout_prompt(
    diagram_code: str,
    optimization_goals: List[str],
    ctx: Optional[Context] = None,
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
