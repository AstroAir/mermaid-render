"""Utility functions for interactive diagram building."""

from typing import Any, Dict, List

from .builder import DiagramBuilder, DiagramType
from .validation import LiveValidator


def create_interactive_session(diagram_type: str = "flowchart") -> DiagramBuilder:
    """
    Create a new interactive diagram building session.

    Initializes a new DiagramBuilder instance for the specified diagram type,
    enabling interactive creation and editing of diagrams through a programmatic
    interface.

    Args:
        diagram_type: Type of diagram to create ("flowchart", "sequence", etc.)

    Returns:
        DiagramBuilder instance ready for interactive use

    Example:
        >>> builder = create_interactive_session("sequence")
        >>> builder.add_participant("A", "Alice")
        >>> builder.add_participant("B", "Bob")
    """
    return DiagramBuilder(DiagramType(diagram_type))


def load_diagram_from_code(code: str) -> DiagramBuilder:
    """
    Load an existing diagram from Mermaid code for interactive editing.

    Parses the provided Mermaid code and creates a DiagramBuilder instance
    that can be used to interactively modify the diagram.

    Args:
        code: Valid Mermaid diagram code

    Returns:
        DiagramBuilder instance loaded with the parsed diagram

    Example:
        >>> code = "flowchart TD\\n    A[Start] --> B[End]"
        >>> builder = load_diagram_from_code(code)
        >>> builder.add_node("C", "Middle")
    """
    builder = DiagramBuilder()
    builder.load_from_mermaid_code(code)
    return builder


def export_diagram_code(builder: DiagramBuilder) -> str:
    """
    Export the current diagram as Mermaid code.

    Generates the Mermaid syntax representation of the diagram currently
    being built in the DiagramBuilder instance.

    Args:
        builder: DiagramBuilder instance to export

    Returns:
        Generated Mermaid diagram code

    Example:
        >>> builder = create_interactive_session("flowchart")
        >>> builder.add_node("A", "Start")
        >>> code = export_diagram_code(builder)
        >>> print(code)  # "flowchart TD\\n    A[Start]"
    """
    return builder.generate_mermaid_code()


def validate_diagram_live(code: str) -> Dict[str, Any]:
    """
    Validate diagram code with real-time feedback.

    Performs comprehensive validation of Mermaid diagram code, providing
    detailed feedback about syntax errors, warnings, and suggestions for
    improvement.

    Args:
        code: Mermaid diagram code to validate

    Returns:
        Validation result dictionary with errors, warnings, and suggestions

    Example:
        >>> result = validate_diagram_live("flowchart TD\\n    A --> B")
        >>> if result["is_valid"]:
        ...     print("Diagram is valid!")
        >>> else:
        ...     print(f"Errors: {result['errors']}")
    """
    validator = LiveValidator()
    result = validator.validate(code)
    return result.to_dict()


def get_available_components() -> List[Dict[str, Any]]:
    """
    Get a list of available diagram components for interactive building.

    Returns information about all available diagram components that can be
    used in interactive diagram building, including their types, names, and
    categories.

    Returns:
        List of component dictionaries with type, name, and category information

    Example:
        >>> components = get_available_components()
        >>> for comp in components:
        ...     print(f"{comp['name']} ({comp['type']})")
    """
    return [
        {"type": "rectangle", "name": "Rectangle", "category": "basic"},
        {"type": "circle", "name": "Circle", "category": "basic"},
        {"type": "diamond", "name": "Diamond", "category": "decision"},
        {"type": "hexagon", "name": "Hexagon", "category": "process"},
    ]
