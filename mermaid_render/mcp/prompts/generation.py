"""
Diagram generation prompts for MCP.

This module provides prompts for generating various diagram types.
"""

from .base import Context


def generate_flowchart_prompt(
    process_description: str,
    complexity_level: str = "medium",
    include_decision_points: bool = True,
    ctx: Context | None = None,
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
        "complex": "Create a detailed flowchart with multiple decision points, parallel processes, and sub-processes",
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
    participants: list[str],
    include_notes: bool = False,
    ctx: Context | None = None,
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
    ctx: Context | None = None,
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
