"""
Flowchart parser for the interactive diagram builder.

This module provides Mermaid code parsing for flowchart diagrams.
"""

import re

from ...models import DiagramConnection, DiagramElement, ElementType, Position, Size
from .base import DiagramParser


class FlowchartParser(DiagramParser):
    """
    Parses Mermaid flowchart code into diagram elements.

    Supports various node shapes and connection types.
    """

    # Connection type mappings from arrow syntax
    ARROW_TO_TYPE: dict[str, str] = {
        "-->": "default",
        "---": "line",
        "-.-": "dotted",
        "==>": "thick",
        "~~~": "invisible",
        "--o": "arrow_circle",
        "--x": "arrow_cross",
    }

    def parse(
        self, lines: list[str]
    ) -> tuple[dict[str, DiagramElement], dict[str, DiagramConnection]]:
        """
        Parse flowchart Mermaid code.

        Args:
            lines: Lines of Mermaid code (excluding diagram declaration)

        Returns:
            Tuple of (elements dict, connections dict)
        """
        elements: dict[str, DiagramElement] = {}
        connections: dict[str, DiagramConnection] = {}

        # Track positions for auto-layout
        current_y = 50
        node_positions: dict[str, Position] = {}

        for line in lines:
            line = line.strip()
            if self._skip_line(line):
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
                    size=Size(120, 60),
                    properties={"shape": shape},
                )
                elements[node_id] = element
                continue

            # Parse connections (e.g., "A --> B", "A -->|label| B")
            connection_match = re.match(
                r"^\s*([A-Za-z0-9_]+)\s*(-->|---|-\.-|==>|~~~|--o|--x)\s*(?:\|([^|]+)\|\s*)?([A-Za-z0-9_]+)",
                line,
            )
            if connection_match:
                source_id = connection_match.group(1)
                arrow_type = connection_match.group(2)
                label = connection_match.group(3) or ""
                target_id = connection_match.group(4)

                # Map arrow types to connection types
                connection_type = self.ARROW_TO_TYPE.get(arrow_type, "default")

                # Ensure both nodes exist
                for node_id in [source_id, target_id]:
                    if node_id not in elements:
                        if node_id not in node_positions:
                            node_positions[node_id] = Position(100, current_y)
                            current_y += 100

                        element = DiagramElement(
                            id=node_id,
                            element_type=ElementType.NODE,
                            label=node_id,
                            position=node_positions[node_id],
                            size=Size(120, 60),
                            properties={"shape": "rectangle"},
                        )
                        elements[node_id] = element

                # Create connection
                connection = DiagramConnection(
                    id=f"conn_{source_id}_{target_id}_{len(connections)}",
                    source_id=source_id,
                    target_id=target_id,
                    label=label,
                    connection_type=connection_type,
                )
                connections[connection.id] = connection

        return elements, connections

    def _parse_node_definition(self, node_def: str) -> tuple[str, str]:
        """
        Parse node definition to extract shape and label.

        Args:
            node_def: Node definition string (e.g., "[label]", "(label)")

        Returns:
            Tuple of (shape, label)
        """
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
