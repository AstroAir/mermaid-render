"""
Core diagram builder for interactive diagram creation.

This module provides the main diagram building functionality with
support for visual elements, connections, and real-time updates.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..exceptions import DiagramError


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


@dataclass
class Position:
    """2D position for visual elements."""

    x: float
    y: float

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Position":
        return cls(x=data["x"], y=data["y"])


@dataclass
class Size:
    """Size dimensions for visual elements."""

    width: float
    height: float

    def to_dict(self) -> Dict[str, float]:
        return {"width": self.width, "height": self.height}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Size":
        return cls(width=data["width"], height=data["height"])


@dataclass
class DiagramElement:
    """
    Represents a visual element in the diagram builder.

    Provides a visual representation of diagram components with
    position, styling, and interaction capabilities.
    """

    id: str
    element_type: ElementType
    label: str
    position: Position
    size: Size
    properties: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())

    def update_position(self, x: float, y: float) -> None:
        """Update element position."""
        self.position.x = x
        self.position.y = y
        self.updated_at = datetime.now()

    def update_size(self, width: float, height: float) -> None:
        """Update element size."""
        self.size.width = width
        self.size.height = height
        self.updated_at = datetime.now()

    def update_properties(self, properties: Dict[str, Any]) -> None:
        """Update element properties."""
        self.properties.update(properties)
        self.updated_at = datetime.now()

    def update_style(self, style: Dict[str, Any]) -> None:
        """Update element styling."""
        self.style.update(style)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "element_type": self.element_type.value,
            "label": self.label,
            "position": self.position.to_dict(),
            "size": self.size.to_dict(),
            "properties": self.properties,
            "style": self.style,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagramElement":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            element_type=ElementType(data["element_type"]),
            label=data["label"],
            position=Position.from_dict(data["position"]),
            size=Size.from_dict(data["size"]),
            properties=data.get("properties", {}),
            style=data.get("style", {}),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class DiagramConnection:
    """
    Represents a connection between diagram elements.

    Provides visual and logical connections between elements
    with styling and labeling capabilities.
    """

    id: str
    source_id: str
    target_id: str
    label: str = ""
    connection_type: str = "default"
    style: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    control_points: List[Position] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())

    def update_label(self, label: str) -> None:
        """Update connection label."""
        self.label = label
        self.updated_at = datetime.now()

    def update_style(self, style: Dict[str, Any]) -> None:
        """Update connection styling."""
        self.style.update(style)
        self.updated_at = datetime.now()

    def add_control_point(self, position: Position) -> None:
        """Add control point for connection routing."""
        self.control_points.append(position)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "label": self.label,
            "connection_type": self.connection_type,
            "style": self.style,
            "properties": self.properties,
            "control_points": [cp.to_dict() for cp in self.control_points],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagramConnection":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            label=data.get("label", ""),
            connection_type=data.get("connection_type", "default"),
            style=data.get("style", {}),
            properties=data.get("properties", {}),
            control_points=[
                Position.from_dict(cp) for cp in data.get("control_points", [])
            ],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


class DiagramBuilder:
    """
    Main diagram builder for interactive diagram creation.

    Provides a high-level interface for building diagrams visually
    with real-time updates and code generation.
    """

    def __init__(self, diagram_type: DiagramType = DiagramType.FLOWCHART):
        """
        Initialize diagram builder.

        Args:
            diagram_type: Type of diagram to build
        """
        self.diagram_type = diagram_type
        self.elements: Dict[str, DiagramElement] = {}
        self.connections: Dict[str, DiagramConnection] = {}
        self.metadata: Dict[str, Any] = {
            "title": "",
            "description": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Event handlers
        self._element_added_handlers: List[Callable] = []
        self._element_updated_handlers: List[Callable] = []
        self._element_removed_handlers: List[Callable] = []
        self._connection_added_handlers: List[Callable] = []
        self._connection_updated_handlers: List[Callable] = []
        self._connection_removed_handlers: List[Callable] = []

    def add_element(
        self,
        element_type: ElementType,
        label: str,
        position: Position,
        size: Optional[Size] = None,
        properties: Optional[Dict[str, Any]] = None,
        style: Optional[Dict[str, Any]] = None,
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
        if size is None:
            size = self._get_default_size(element_type)

        element = DiagramElement(
            id=str(uuid.uuid4()),
            element_type=element_type,
            label=label,
            position=position,
            size=size,
            properties=properties or {},
            style=style or {},
        )

        self.elements[element.id] = element
        self._update_metadata()

        # Notify handlers
        for handler in self._element_added_handlers:
            handler(element)

        return element

    def update_element(
        self,
        element_id: str,
        label: Optional[str] = None,
        position: Optional[Position] = None,
        size: Optional[Size] = None,
        properties: Optional[Dict[str, Any]] = None,
        style: Optional[Dict[str, Any]] = None,
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
        if element_id not in self.elements:
            return False

        element = self.elements[element_id]

        if label is not None:
            element.label = label
        if position is not None:
            element.position = position
        if size is not None:
            element.size = size
        if properties is not None:
            element.update_properties(properties)
        if style is not None:
            element.update_style(style)

        element.updated_at = datetime.now()
        self._update_metadata()

        # Notify handlers
        for handler in self._element_updated_handlers:
            handler(element)

        return True

    def remove_element(self, element_id: str) -> bool:
        """
        Remove an element from the diagram.

        Args:
            element_id: ID of element to remove

        Returns:
            True if element was removed
        """
        if element_id not in self.elements:
            return False

        element = self.elements[element_id]

        # Remove associated connections
        connections_to_remove = [
            conn_id
            for conn_id, conn in self.connections.items()
            if conn.source_id == element_id or conn.target_id == element_id
        ]

        for conn_id in connections_to_remove:
            self.remove_connection(conn_id)

        # Remove element
        del self.elements[element_id]
        self._update_metadata()

        # Notify handlers
        for handler in self._element_removed_handlers:
            handler(element)

        return True

    def add_connection(
        self,
        source_id: str,
        target_id: str,
        label: str = "",
        connection_type: str = "default",
        style: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[DiagramConnection]:
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
        if source_id not in self.elements or target_id not in self.elements:
            return None

        connection = DiagramConnection(
            id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            label=label,
            connection_type=connection_type,
            style=style or {},
            properties=properties or {},
        )

        self.connections[connection.id] = connection
        self._update_metadata()

        # Notify handlers
        for handler in self._connection_added_handlers:
            handler(connection)

        return connection

    def update_connection(
        self,
        connection_id: str,
        label: Optional[str] = None,
        connection_type: Optional[str] = None,
        style: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
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
        if connection_id not in self.connections:
            return False

        connection = self.connections[connection_id]

        if label is not None:
            connection.label = label
        if connection_type is not None:
            connection.connection_type = connection_type
        if style is not None:
            connection.update_style(style)
        if properties is not None:
            connection.properties.update(properties)

        connection.updated_at = datetime.now()
        self._update_metadata()

        # Notify handlers
        for handler in self._connection_updated_handlers:
            handler(connection)

        return True

    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove a connection from the diagram.

        Args:
            connection_id: ID of connection to remove

        Returns:
            True if connection was removed
        """
        if connection_id not in self.connections:
            return False

        connection = self.connections[connection_id]
        del self.connections[connection_id]
        self._update_metadata()

        # Notify handlers
        for handler in self._connection_removed_handlers:
            handler(connection)

        return True

    def generate_mermaid_code(self) -> str:
        """
        Generate Mermaid diagram code from current state.

        Returns:
            Generated Mermaid code
        """
        if self.diagram_type == DiagramType.FLOWCHART:
            return self._generate_flowchart_code()
        elif self.diagram_type == DiagramType.SEQUENCE:
            return self._generate_sequence_code()
        elif self.diagram_type == DiagramType.CLASS:
            return self._generate_class_code()
        else:
            raise DiagramError(
                f"Code generation not implemented for {self.diagram_type}"
            )

    def load_from_mermaid_code(self, code: str) -> None:
        """
        Load diagram from Mermaid code.

        Args:
            code: Mermaid diagram code to parse
        """
        # This would parse Mermaid code and create visual elements
        # For now, this is a placeholder for the parsing logic
        # Mark parameter as intentionally unused to satisfy linters/type-checkers.
        _ = code
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert builder state to dictionary."""
        return {
            "diagram_type": self.diagram_type.value,
            "elements": {eid: elem.to_dict() for eid, elem in self.elements.items()},
            "connections": {
                cid: conn.to_dict() for cid, conn in self.connections.items()
            },
            "metadata": self.metadata,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load builder state from dictionary."""
        self.diagram_type = DiagramType(data["diagram_type"])
        self.elements = {
            eid: DiagramElement.from_dict(elem_data)
            for eid, elem_data in data.get("elements", {}).items()
        }
        self.connections = {
            cid: DiagramConnection.from_dict(conn_data)
            for cid, conn_data in data.get("connections", {}).items()
        }
        self.metadata = data.get("metadata", {})

    def _get_default_size(self, element_type: ElementType) -> Size:
        """Get default size for element type."""
        size_map = {
            ElementType.NODE: Size(120, 60),
            ElementType.CONTAINER: Size(200, 150),
            ElementType.ANNOTATION: Size(100, 40),
        }
        return size_map.get(element_type, Size(100, 50))

    def _update_metadata(self) -> None:
        """Update diagram metadata."""
        self.metadata["updated_at"] = datetime.now().isoformat()
        self.metadata["element_count"] = len(self.elements)
        self.metadata["connection_count"] = len(self.connections)

    def _generate_flowchart_code(self) -> str:
        """Generate flowchart Mermaid code."""
        lines = ["flowchart TD"]

        # Add title if present
        if self.metadata.get("title"):
            lines.append(f"    %% {self.metadata['title']}")
            lines.append("")

        # Add nodes
        for element in self.elements.values():
            if element.element_type == ElementType.NODE:
                shape = element.properties.get("shape", "rectangle")
                node_syntax = self._get_flowchart_node_syntax(
                    element.id, element.label, shape
                )
                lines.append(f"    {node_syntax}")

        lines.append("")

        # Add connections
        for connection in self.connections.values():
            arrow = self._get_flowchart_arrow(connection.connection_type)
            if connection.label:
                lines.append(
                    f"    {connection.source_id} {arrow}|{connection.label}| {connection.target_id}"
                )
            else:
                lines.append(
                    f"    {connection.source_id} {arrow} {connection.target_id}"
                )

        return "\n".join(lines)

    def _get_flowchart_node_syntax(self, node_id: str, label: str, shape: str) -> str:
        """Get flowchart node syntax for shape."""
        shape_map = {
            "rectangle": f"{node_id}[{label}]",
            "rounded": f"{node_id}({label})",
            "circle": f"{node_id}(({label}))",
            "diamond": f"{node_id}{{{label}}}",
            "hexagon": f"{node_id}{{{{{label}}}}}",
        }
        return shape_map.get(shape, f"{node_id}[{label}]")

    def _get_flowchart_arrow(self, connection_type: str) -> str:
        """Get flowchart arrow syntax for connection type."""
        arrow_map = {
            "default": "-->",
            "dotted": "-.-",
            "thick": "==>",
            "invisible": "~~~",
        }
        return arrow_map.get(connection_type, "-->")

    def _generate_sequence_code(self) -> str:
        """Generate sequence diagram Mermaid code."""
        # Placeholder for sequence diagram generation
        return "sequenceDiagram\n    %% Generated from interactive builder"

    def _generate_class_code(self) -> str:
        """Generate class diagram Mermaid code."""
        # Placeholder for class diagram generation
        return "classDiagram\n    %% Generated from interactive builder"

    # Event handler registration methods
    def on_element_added(self, handler: Callable[[DiagramElement], None]) -> None:
        """Register handler for element added events."""
        self._element_added_handlers.append(handler)

    def on_element_updated(self, handler: Callable[[DiagramElement], None]) -> None:
        """Register handler for element updated events."""
        self._element_updated_handlers.append(handler)

    def on_element_removed(self, handler: Callable[[DiagramElement], None]) -> None:
        """Register handler for element removed events."""
        self._element_removed_handlers.append(handler)

    def on_connection_added(self, handler: Callable[[DiagramConnection], None]) -> None:
        """Register handler for connection added events."""
        self._connection_added_handlers.append(handler)

    def on_connection_updated(
        self, handler: Callable[[DiagramConnection], None]
    ) -> None:
        """Register handler for connection updated events."""
        self._connection_updated_handlers.append(handler)

    def on_connection_removed(
        self, handler: Callable[[DiagramConnection], None]
    ) -> None:
        """Register handler for connection removed events."""
        self._connection_removed_handlers.append(handler)
