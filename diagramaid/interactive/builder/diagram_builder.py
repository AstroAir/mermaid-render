"""
Core diagram builder for interactive diagram creation.

This module provides the main DiagramBuilder class that orchestrates
element management, connection management, code generation, and parsing.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any

from ...exceptions import DiagramError
from ..models import (
    DiagramConnection,
    DiagramElement,
    DiagramType,
    ElementType,
    Position,
    Size,
)
from .codegen import ClassDiagramGenerator, FlowchartGenerator, SequenceDiagramGenerator
from .connection_manager import ConnectionManager
from .element_manager import ElementManager
from .parsers import (
    ClassDiagramParser,
    ERDiagramParser,
    FlowchartParser,
    SequenceDiagramParser,
    StateDiagramParser,
)
from .serialization import DiagramSerializer


class DiagramBuilder:
    """
    Main diagram builder for interactive diagram creation.

    Provides a high-level interface for building diagrams visually
    with real-time updates and code generation.

    This class orchestrates:
    - ElementManager: Element CRUD operations
    - ConnectionManager: Connection CRUD operations
    - Code generators: Mermaid code generation
    - Parsers: Mermaid code parsing
    """

    def __init__(self, diagram_type: DiagramType = DiagramType.FLOWCHART):
        """
        Initialize diagram builder.

        Args:
            diagram_type: Type of diagram to build
        """
        self.diagram_type = diagram_type

        # Initialize managers
        self._element_manager = ElementManager()
        self._connection_manager = ConnectionManager()

        # Initialize code generators
        self._code_generators = {
            DiagramType.FLOWCHART: FlowchartGenerator(),
            DiagramType.SEQUENCE: SequenceDiagramGenerator(),
            DiagramType.CLASS: ClassDiagramGenerator(),
        }

        # Initialize parsers
        self._parsers = {
            DiagramType.FLOWCHART: FlowchartParser(),
            DiagramType.SEQUENCE: SequenceDiagramParser(),
            DiagramType.CLASS: ClassDiagramParser(),
            DiagramType.STATE: StateDiagramParser(),
            DiagramType.ER: ERDiagramParser(),
        }

        # Metadata
        self.metadata: dict[str, Any] = {
            "title": "",
            "description": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    # ==================== Element Operations ====================

    @property
    def elements(self) -> dict[str, DiagramElement]:
        """Get all elements."""
        return self._element_manager.elements

    def add_element(
        self,
        element_type: ElementType,
        label: str,
        position: Position,
        size: Size | None = None,
        properties: dict[str, Any] | None = None,
        style: dict[str, Any] | None = None,
    ) -> DiagramElement:
        """
        Add a new element to the diagram.

        Args:
            element_type: Type of element to add
            label: Element label
            position: Element position
            size: Element size (default based on type)
            properties: Element properties
            style: Element styling

        Returns:
            Created diagram element
        """
        element = self._element_manager.add_element(
            element_type=element_type,
            label=label,
            position=position,
            size=size,
            properties=properties,
            style=style,
        )
        self._update_metadata()
        return element

    def update_element(
        self,
        element_id: str,
        label: str | None = None,
        position: Position | None = None,
        size: Size | None = None,
        properties: dict[str, Any] | None = None,
        style: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update an existing element.

        Args:
            element_id: ID of element to update
            label: New label
            position: New position
            size: New size
            properties: New properties
            style: New styling

        Returns:
            True if element was updated
        """
        success = self._element_manager.update_element(
            element_id=element_id,
            label=label,
            position=position,
            size=size,
            properties=properties,
            style=style,
        )
        if success:
            self._update_metadata()
        return success

    def remove_element(self, element_id: str) -> bool:
        """
        Remove an element from the diagram.

        Args:
            element_id: ID of element to remove

        Returns:
            True if element was removed
        """
        # Remove associated connections first
        self._connection_manager.remove_connections_for_element(element_id)

        element = self._element_manager.remove_element(element_id)
        if element:
            self._update_metadata()
            return True
        return False

    # ==================== Connection Operations ====================

    @property
    def connections(self) -> dict[str, DiagramConnection]:
        """Get all connections."""
        return self._connection_manager.connections

    def add_connection(
        self,
        source_id: str,
        target_id: str,
        label: str = "",
        connection_type: str = "default",
        style: dict[str, Any] | None = None,
        properties: dict[str, Any] | None = None,
    ) -> DiagramConnection | None:
        """
        Add a connection between elements.

        Args:
            source_id: Source element ID
            target_id: Target element ID
            label: Connection label
            connection_type: Type of connection
            style: Connection styling
            properties: Connection properties

        Returns:
            Created connection or None if invalid
        """
        # Validate that both elements exist
        if not self._element_manager.has_element(source_id):
            return None
        if not self._element_manager.has_element(target_id):
            return None

        connection = self._connection_manager.add_connection(
            source_id=source_id,
            target_id=target_id,
            label=label,
            connection_type=connection_type,
            style=style,
            properties=properties,
        )
        self._update_metadata()
        return connection

    def update_connection(
        self,
        connection_id: str,
        label: str | None = None,
        connection_type: str | None = None,
        style: dict[str, Any] | None = None,
        properties: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update an existing connection.

        Args:
            connection_id: ID of connection to update
            label: New label
            connection_type: New connection type
            style: New styling
            properties: New properties

        Returns:
            True if connection was updated
        """
        success = self._connection_manager.update_connection(
            connection_id=connection_id,
            label=label,
            connection_type=connection_type,
            style=style,
            properties=properties,
        )
        if success:
            self._update_metadata()
        return success

    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove a connection from the diagram.

        Args:
            connection_id: ID of connection to remove

        Returns:
            True if connection was removed
        """
        connection = self._connection_manager.remove_connection(connection_id)
        if connection:
            self._update_metadata()
            return True
        return False

    # ==================== Code Generation ====================

    def generate_mermaid_code(self) -> str:
        """
        Generate Mermaid diagram code from current state.

        Returns:
            Generated Mermaid code
        """
        generator = self._code_generators.get(self.diagram_type)
        if generator:
            return generator.generate(
                self._element_manager.elements,
                self._connection_manager.connections,
                self.metadata,
            )
        raise DiagramError(
            f"Code generation not implemented for {self.diagram_type}"
        )

    # ==================== Parsing ====================

    def load_from_mermaid_code(self, code: str) -> None:
        """
        Load diagram from Mermaid code.

        Args:
            code: Mermaid diagram code to parse
        """
        # Clear existing elements and connections
        self._element_manager.clear()
        self._connection_manager.clear()

        # Parse the code
        lines = [line.strip() for line in code.strip().split("\n") if line.strip()]
        if not lines:
            return

        # Determine diagram type from first line
        first_line = lines[0].lower()
        self._detect_and_set_diagram_type(first_line)

        # Get appropriate parser
        parser = self._parsers.get(self.diagram_type)
        if parser:
            # Skip first line (diagram declaration)
            content_lines = lines[1:] if len(lines) > 1 else []
            elements, connections = parser.parse(content_lines)

            # Load parsed data
            self._element_manager.elements = elements
            self._connection_manager.connections = connections

        self._update_metadata()

    def _detect_and_set_diagram_type(self, first_line: str) -> None:
        """Detect diagram type from first line and set it."""
        if first_line.startswith("flowchart") or first_line.startswith("graph"):
            self.diagram_type = DiagramType.FLOWCHART
        elif first_line.startswith("sequencediagram"):
            self.diagram_type = DiagramType.SEQUENCE
        elif first_line.startswith("classdiagram"):
            self.diagram_type = DiagramType.CLASS
        elif first_line.startswith("statediagram"):
            self.diagram_type = DiagramType.STATE
        elif first_line.startswith("erdiagram"):
            self.diagram_type = DiagramType.ER
        else:
            # Default to flowchart
            self.diagram_type = DiagramType.FLOWCHART

    # ==================== Serialization ====================

    def to_dict(self) -> dict[str, Any]:
        """Convert builder state to dictionary."""
        return DiagramSerializer.to_dict(
            self.diagram_type,
            self._element_manager.elements,
            self._connection_manager.connections,
            self.metadata,
        )

    def from_dict(self, data: dict[str, Any]) -> None:
        """Load builder state from dictionary."""
        DiagramSerializer.load_into_builder(self, data)

    # ==================== Event Handlers ====================

    def on_element_added(self, handler: Callable[[DiagramElement], None]) -> None:
        """Register handler for element added events."""
        self._element_manager.on_element_added(handler)

    def on_element_updated(self, handler: Callable[[DiagramElement], None]) -> None:
        """Register handler for element updated events."""
        self._element_manager.on_element_updated(handler)

    def on_element_removed(self, handler: Callable[[DiagramElement], None]) -> None:
        """Register handler for element removed events."""
        self._element_manager.on_element_removed(handler)

    def on_connection_added(
        self, handler: Callable[[DiagramConnection], None]
    ) -> None:
        """Register handler for connection added events."""
        self._connection_manager.on_connection_added(handler)

    def on_connection_updated(
        self, handler: Callable[[DiagramConnection], None]
    ) -> None:
        """Register handler for connection updated events."""
        self._connection_manager.on_connection_updated(handler)

    def on_connection_removed(
        self, handler: Callable[[DiagramConnection], None]
    ) -> None:
        """Register handler for connection removed events."""
        self._connection_manager.on_connection_removed(handler)

    # ==================== Helper Methods ====================

    def _update_metadata(self) -> None:
        """Update diagram metadata."""
        self.metadata["updated_at"] = datetime.now().isoformat()
        self.metadata["element_count"] = len(self._element_manager.elements)
        self.metadata["connection_count"] = len(self._connection_manager.connections)

    def _get_default_size(self, element_type: ElementType) -> Size:
        """Get default size for element type."""
        return self._element_manager.get_default_size(element_type)
