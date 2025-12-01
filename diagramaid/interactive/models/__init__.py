"""
Models package for the interactive diagram builder.

This package contains the core data models used throughout
the interactive diagram building system.
"""

from .elements import DiagramConnection, DiagramElement
from .enums import DiagramType, ElementType
from .geometry import Position, Size

__all__ = [
    # Enums
    "ElementType",
    "DiagramType",
    # Geometry
    "Position",
    "Size",
    # Elements
    "DiagramElement",
    "DiagramConnection",
]
