"""
Shared constants for diagram models.

This module provides commonly used constants and mappings that are shared
across multiple diagram types to avoid duplication.
"""


# Visibility mapping for UML elements (class diagrams, etc.)
VISIBILITY_SYMBOLS: dict[str, str] = {
    "public": "+",
    "private": "-",
    "protected": "#",
    "package": "~",
    "derived": "/",
    "static": "$",
}

# Diagram type identifiers
DIAGRAM_TYPES: list[str] = [
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "quadrantChart",
    "requirementDiagram",
    "gitGraph",
    "mindmap",
    "timeline",
    "zenuml",
    "sankey",
]

# Common node shapes for flowcharts
FLOWCHART_SHAPES: dict[str, tuple[str, str]] = {
    "rectangle": ("[", "]"),
    "rounded": ("(", ")"),
    "stadium": ("([", "])"),
    "subroutine": ("[[", "]]"),
    "cylindrical": ("[(", ")]"),
    "circle": ("((", "))"),
    "asymmetric": (">", "]"),
    "rhombus": ("{", "}"),
    "hexagon": ("{{", "}}"),
    "parallelogram": ("[/", "/]"),
    "parallelogram_alt": ("[\\", "\\]"),
    "trapezoid": ("[/", "\\]"),
    "trapezoid_alt": ("[\\", "/]"),
    "double_circle": ("(((", ")))"),
}

# Arrow types for different relationships
ARROW_TYPES: dict[str, str] = {
    # Flowchart-specific arrow types
    "arrow": "-->",  # Standard directional arrow
    "open": "---",  # Open line (no arrow)
    "dotted": "-.->",  # Dotted arrow
    "dotted_arrow": "-.->",  # Alias for dotted (backward compatibility)
    "dotted_line": "-.-",  # Dotted line (no arrow)
    "thick": "==>",  # Thick arrow
    "thick_open": "===",  # Thick open line
    "invisible": "~~~",  # Invisible connection
    "bidirectional": "<-->",  # Bidirectional arrow
    # Additional relationship arrow types
    "normal": "-->",  # Alias for arrow
    "thick_dotted": "==.",  # Thick dotted
    "circle": "--o",  # Circle endpoint
    "cross": "--x",  # Cross endpoint
}

# Common themes
THEMES: list[str] = [
    "default",
    "forest",
    "dark",
    "neutral",
    "base",
]
