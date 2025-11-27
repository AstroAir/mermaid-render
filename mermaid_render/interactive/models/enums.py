"""
Enumeration types for the interactive diagram builder.

This module defines the core enumeration types used throughout
the interactive diagram building system.
"""

from enum import Enum


class ElementType(Enum):
    """Types of diagram elements."""

    NODE = "node"
    EDGE = "edge"
    CONTAINER = "container"
    ANNOTATION = "annotation"


class DiagramType(Enum):
    """Supported diagram types for interactive building."""

    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    STATE = "state"
    ER = "er"
