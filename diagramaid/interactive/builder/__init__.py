"""
Builder package for the interactive diagram builder.

This package provides the core diagram building functionality with
support for visual elements, connections, and real-time updates.
The builder is split into smaller components for better maintainability.
"""

from .codegen import (
    ClassDiagramGenerator,
    CodeGenerator,
    FlowchartGenerator,
    SequenceDiagramGenerator,
)
from .connection_manager import ConnectionManager
from .diagram_builder import DiagramBuilder
from .element_manager import ElementManager
from .event_manager import EventManager
from .parsers import (
    ClassDiagramParser,
    DiagramParser,
    ERDiagramParser,
    FlowchartParser,
    SequenceDiagramParser,
    StateDiagramParser,
)
from .serialization import DiagramSerializer

__all__ = [
    # Main builder
    "DiagramBuilder",
    # Managers
    "ElementManager",
    "ConnectionManager",
    "EventManager",
    # Serialization
    "DiagramSerializer",
    # Code generation
    "CodeGenerator",
    "FlowchartGenerator",
    "SequenceDiagramGenerator",
    "ClassDiagramGenerator",
    # Parsers
    "DiagramParser",
    "FlowchartParser",
    "SequenceDiagramParser",
    "ClassDiagramParser",
    "StateDiagramParser",
    "ERDiagramParser",
]
