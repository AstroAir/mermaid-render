"""
Core diagram builder for interactive diagram creation.

This module provides the main diagram building functionality with
support for visual elements, connections, and real-time updates.
"""

import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from ..exceptions import DiagramError
from .models import (
    DiagramConnection,
    DiagramElement,
    DiagramType,
    ElementType,
    Position,
    Size,
)

# Re-export for backward compatibility
__all__ = [
    "DiagramBuilder",
    "DiagramConnection",
    "DiagramElement",
    "DiagramType",
    "ElementType",
    "Position",
    "Size",
]


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
        self.elements: dict[str, DiagramElement] = {}
        self.connections: dict[str, DiagramConnection] = {}
        self.metadata: dict[str, Any] = {
            "title": "",
            "description": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Event handlers
        self._element_added_handlers: list[Callable[..., Any]] = []
        self._element_updated_handlers: list[Callable[..., Any]] = []
        self._element_removed_handlers: list[Callable[..., Any]] = []
        self._connection_added_handlers: list[Callable[..., Any]] = []
        self._connection_updated_handlers: list[Callable[..., Any]] = []
        self._connection_removed_handlers: list[Callable[..., Any]] = []

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
        # Clear existing elements and connections
        self.elements.clear()
        self.connections.clear()

        # Parse the code
        lines = [line.strip() for line in code.strip().split("\n") if line.strip()]
        if not lines:
            return

        # Determine diagram type from first line
        first_line = lines[0].lower()
        if first_line.startswith("flowchart") or first_line.startswith("graph"):
            self.diagram_type = DiagramType.FLOWCHART
            self._parse_flowchart(lines)
        elif first_line.startswith("sequencediagram"):
            self.diagram_type = DiagramType.SEQUENCE
            self._parse_sequence_diagram(lines)
        elif first_line.startswith("classdiagram"):
            self.diagram_type = DiagramType.CLASS
            self._parse_class_diagram(lines)
        elif first_line.startswith("statediagram"):
            self.diagram_type = DiagramType.STATE
            self._parse_state_diagram(lines)
        elif first_line.startswith("erdiagram"):
            self.diagram_type = DiagramType.ER
            self._parse_er_diagram(lines)
        else:
            # Default to flowchart
            self.diagram_type = DiagramType.FLOWCHART
            self._parse_flowchart(lines)

        self._update_metadata()

    def to_dict(self) -> dict[str, Any]:
        """Convert builder state to dictionary."""
        return {
            "diagram_type": self.diagram_type.value,
            "elements": {eid: elem.to_dict() for eid, elem in self.elements.items()},
            "connections": {
                cid: conn.to_dict() for cid, conn in self.connections.items()
            },
            "metadata": self.metadata,
        }

    def from_dict(self, data: dict[str, Any]) -> None:
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
        lines = ["sequenceDiagram"]

        # Add title if present
        if self.metadata.get("title"):
            lines.append(f"    title {self.metadata['title']}")
            lines.append("")

        # Collect participants
        participants: set[str] = set()

        # Process elements to find participants
        for element in self.elements.values():
            if element.properties.get("type") == "participant":
                participants.add(element.id)

        # Add participant declarations
        for participant in sorted(participants):
            participant_element: DiagramElement | None = next(
                (e for e in self.elements.values() if e.id == participant), None
            )
            if (
                participant_element
                and participant_element.label != participant_element.id
            ):
                lines.append(
                    f"    participant {participant} as {participant_element.label}"
                )
            else:
                lines.append(f"    participant {participant}")

        if participants:
            lines.append("")

        # Process connections as messages
        for connection in self.connections.values():
            source = connection.source_id
            target = connection.target_id
            label = connection.label or "message"

            # Determine message type based on connection type
            arrow = self._get_sequence_arrow(connection.connection_type)

            if connection.label:
                lines.append(f"    {source}{arrow}{target}: {label}")
            else:
                lines.append(f"    {source}{arrow}{target}: ")

        return "\n".join(lines)

    def _generate_class_code(self) -> str:
        """Generate class diagram Mermaid code."""
        lines = ["classDiagram"]

        # Add title if present
        if self.metadata.get("title"):
            lines.append(f"    title {self.metadata['title']}")
            lines.append("")

        # Process elements as classes
        for element in self.elements.values():
            if element.properties.get("type") == "class":
                class_name = element.id

                # Basic class declaration
                lines.append(f"    class {class_name} {{")

                # Add attributes and methods if stored in properties
                attributes = element.properties.get("attributes", [])
                methods = element.properties.get("methods", [])

                for attr in attributes:
                    lines.append(f"        {attr}")

                for method in methods:
                    lines.append(f"        {method}")

                lines.append("    }")
                lines.append("")

        # Process connections as relationships
        for connection in self.connections.values():
            source = connection.source_id
            target = connection.target_id

            # Determine relationship type
            relationship = self._get_class_relationship(connection.connection_type)

            if connection.label:
                lines.append(
                    f"    {source} {relationship} {target} : {connection.label}"
                )
            else:
                lines.append(f"    {source} {relationship} {target}")

        return "\n".join(lines)

    def _get_sequence_arrow(self, connection_type: str) -> str:
        """Get sequence diagram arrow syntax for connection type."""
        arrow_map = {
            "default": "->>",
            "sync": "->>",
            "async": "-->>",
            "dotted": "-->>",
            "return": "-->>",
        }
        return arrow_map.get(connection_type, "->>")

    def _get_class_relationship(self, connection_type: str) -> str:
        """Get class diagram relationship syntax for connection type."""
        relationship_map = {
            "default": "-->",
            "inheritance": "--|>",
            "composition": "--*",
            "aggregation": "--o",
            "association": "-->",
            "dependency": "..>",
            "realization": "..|>",
        }
        return relationship_map.get(connection_type, "-->")

    def _parse_flowchart(self, lines: list[str]) -> None:
        """Parse flowchart Mermaid code and create elements."""
        import re

        # Skip the first line (diagram declaration)
        content_lines = lines[1:] if len(lines) > 1 else []

        # Track positions for auto-layout
        current_y = 50
        node_positions = {}

        for line in content_lines:
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            # Parse node definitions (e.g., "A[Start]", "B(Process)", "C{Decision}")
            node_match = re.match(
                r"^\s*([A-Za-z0-9_]+)(\[.*?\]|\(.*?\)|\{.*?\}|\(\(.*?\)\)|{{.*?}})",
                line,
            )
            if node_match:
                node_id = node_match.group(1)
                node_def = node_match.group(2)

                # Determine shape and label from definition
                shape, label = self._parse_node_definition(node_def)

                # Create position if not exists
                if node_id not in node_positions:
                    node_positions[node_id] = Position(100, current_y)
                    current_y += 100

                # Create element
                element = DiagramElement(
                    id=node_id,
                    element_type=ElementType.NODE,
                    label=label,
                    position=node_positions[node_id],
                    size=self._get_default_size(ElementType.NODE),
                    properties={"shape": shape},
                )
                self.elements[node_id] = element
                continue

            # Parse connections (e.g., "A --> B", "A -->|label| B")
            connection_match = re.match(
                r"^\s*([A-Za-z0-9_]+)\s*(-->|---|-\.-|==>|~~~)\s*(?:\|([^|]+)\|\s*)?([A-Za-z0-9_]+)",
                line,
            )
            if connection_match:
                source_id = connection_match.group(1)
                arrow_type = connection_match.group(2)
                label = connection_match.group(3) or ""
                target_id = connection_match.group(4)

                # Map arrow types to connection types
                connection_type_map = {
                    "-->": "default",
                    "---": "line",
                    "-.-": "dotted",
                    "==>": "thick",
                    "~~~": "invisible",
                }
                connection_type = connection_type_map.get(arrow_type, "default")

                # Ensure both nodes exist
                for node_id in [source_id, target_id]:
                    if node_id not in self.elements:
                        if node_id not in node_positions:
                            node_positions[node_id] = Position(100, current_y)
                            current_y += 100

                        element = DiagramElement(
                            id=node_id,
                            element_type=ElementType.NODE,
                            label=node_id,
                            position=node_positions[node_id],
                            size=self._get_default_size(ElementType.NODE),
                            properties={"shape": "rectangle"},
                        )
                        self.elements[node_id] = element

                # Create connection
                connection = DiagramConnection(
                    id=f"conn_{source_id}_{target_id}_{len(self.connections)}",
                    source_id=source_id,
                    target_id=target_id,
                    label=label,
                    connection_type=connection_type,
                )
                self.connections[connection.id] = connection

    def _parse_node_definition(self, node_def: str) -> tuple[str, str]:
        """Parse node definition to extract shape and label."""
        node_def = node_def.strip()

        if node_def.startswith("[") and node_def.endswith("]"):
            # Rectangle: [label]
            return "rectangle", node_def[1:-1]
        elif node_def.startswith("(") and node_def.endswith(")"):
            if node_def.startswith("((") and node_def.endswith("))"):
                # Circle: ((label))
                return "circle", node_def[2:-2]
            else:
                # Rounded rectangle: (label)
                return "rounded", node_def[1:-1]
        elif node_def.startswith("{") and node_def.endswith("}"):
            if node_def.startswith("{{") and node_def.endswith("}}"):
                # Hexagon: {{label}}
                return "hexagon", node_def[2:-2]
            else:
                # Diamond: {label}
                return "diamond", node_def[1:-1]
        else:
            # Default to rectangle
            return "rectangle", node_def

    def _parse_sequence_diagram(self, lines: list[str]) -> None:
        """Parse sequence diagram Mermaid code and create elements."""
        # Placeholder implementation for sequence diagrams
        # This would parse participant declarations and message flows
        current_y = 50
        participant_x = 100

        for line in lines[1:]:  # Skip first line
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            # Simple participant parsing (participant A as Alice)
            if line.startswith("participant"):
                parts = line.split()
                if len(parts) >= 2:
                    participant_id = parts[1]
                    label = participant_id
                    if "as" in parts:
                        as_index = parts.index("as")
                        if as_index + 1 < len(parts):
                            label = " ".join(parts[as_index + 1 :])

                    element = DiagramElement(
                        id=participant_id,
                        element_type=ElementType.NODE,
                        label=label,
                        position=Position(participant_x, current_y),
                        size=Size(120, 60),
                        properties={"shape": "rectangle", "type": "participant"},
                    )
                    self.elements[participant_id] = element
                    participant_x += 200

    def _parse_class_diagram(self, lines: list[str]) -> None:
        """Parse class diagram Mermaid code and create elements."""
        # Placeholder implementation for class diagrams
        # This would parse class definitions and relationships
        current_y = 50
        current_x = 100

        for line in lines[1:]:  # Skip first line
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            # Simple class parsing (class ClassName)
            if line.startswith("class"):
                parts = line.split()
                if len(parts) >= 2:
                    class_name = parts[1]

                    element = DiagramElement(
                        id=class_name,
                        element_type=ElementType.NODE,
                        label=class_name,
                        position=Position(current_x, current_y),
                        size=Size(150, 100),
                        properties={"shape": "rectangle", "type": "class"},
                    )
                    self.elements[class_name] = element
                    current_x += 200
                    if current_x > 600:
                        current_x = 100
                        current_y += 150

    def _parse_state_diagram(self, lines: list[str]) -> None:
        """Parse state diagram Mermaid code and create elements."""
        # Placeholder implementation for state diagrams
        current_y = 50
        current_x = 100

        for line in lines[1:]:  # Skip first line
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            # Simple state parsing
            if "-->" in line:
                parts = line.split("-->")
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()

                    # Create states if they don't exist
                    for state_id in [source, target]:
                        if state_id not in self.elements:
                            element = DiagramElement(
                                id=state_id,
                                element_type=ElementType.NODE,
                                label=state_id,
                                position=Position(current_x, current_y),
                                size=Size(120, 60),
                                properties={"shape": "rounded", "type": "state"},
                            )
                            self.elements[state_id] = element
                            current_x += 200
                            if current_x > 600:
                                current_x = 100
                                current_y += 100

    def _parse_er_diagram(self, lines: list[str]) -> None:
        """Parse ER diagram Mermaid code and create elements."""
        # Placeholder implementation for ER diagrams
        current_y = 50
        current_x = 100

        for line in lines[1:]:  # Skip first line
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            # Simple entity parsing
            if "{" in line and "}" in line:
                entity_match = line.split("{")[0].strip()
                if entity_match:
                    element = DiagramElement(
                        id=entity_match,
                        element_type=ElementType.NODE,
                        label=entity_match,
                        position=Position(current_x, current_y),
                        size=Size(150, 100),
                        properties={"shape": "rectangle", "type": "entity"},
                    )
                    self.elements[entity_match] = element
                    current_x += 200
                    if current_x > 600:
                        current_x = 100
                        current_y += 150

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
