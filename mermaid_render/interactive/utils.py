"""Utility functions for interactive diagram building."""

from typing import Any, Dict, List

from .builder import DiagramBuilder, DiagramType
from .validation import LiveValidator


def create_interactive_session(diagram_type: str = "flowchart") -> DiagramBuilder:
    """Create new interactive session."""
    return DiagramBuilder(DiagramType(diagram_type))


def load_diagram_from_code(code: str) -> DiagramBuilder:
    """Load diagram from Mermaid code."""
    builder = DiagramBuilder()
    builder.load_from_mermaid_code(code)
    return builder


def export_diagram_code(builder: DiagramBuilder) -> str:
    """Export diagram as Mermaid code."""
    return builder.generate_mermaid_code()


def validate_diagram_live(code: str) -> Dict[str, Any]:
    """Validate diagram code."""
    validator = LiveValidator()
    result = validator.validate(code)
    return result.to_dict()


def get_available_components() -> List[Dict[str, Any]]:
    """Get list of available diagram components."""
    return [
        {"type": "rectangle", "name": "Rectangle", "category": "basic"},
        {"type": "circle", "name": "Circle", "category": "basic"},
        {"type": "diamond", "name": "Diamond", "category": "decision"},
        {"type": "hexagon", "name": "Hexagon", "category": "process"},
    ]
