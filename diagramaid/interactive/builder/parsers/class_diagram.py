"""
Class diagram parser for the interactive diagram builder.

This module provides Mermaid code parsing for class diagrams.
"""

from ...models import DiagramConnection, DiagramElement, ElementType, Position, Size
from .base import DiagramParser


class ClassDiagramParser(DiagramParser):
    """
    Parses Mermaid class diagram code into diagram elements.

    Supports class definitions and relationships.
    """

    def parse(
        self, lines: list[str]
    ) -> tuple[dict[str, DiagramElement], dict[str, DiagramConnection]]:
        """
        Parse class diagram Mermaid code.

        Args:
            lines: Lines of Mermaid code (excluding diagram declaration)

        Returns:
            Tuple of (elements dict, connections dict)
        """
        elements: dict[str, DiagramElement] = {}
        connections: dict[str, DiagramConnection] = {}

        current_y = 50
        current_x = 100

        for line in lines:
            line = line.strip()
            if self._skip_line(line):
                continue

            # Simple class parsing (class ClassName)
            if line.startswith("class"):
                parts = line.split()
                if len(parts) >= 2:
                    class_name = parts[1].rstrip("{")

                    element = DiagramElement(
                        id=class_name,
                        element_type=ElementType.NODE,
                        label=class_name,
                        position=Position(current_x, current_y),
                        size=Size(150, 100),
                        properties={"shape": "rectangle", "type": "class"},
                    )
                    elements[class_name] = element
                    current_x += 200
                    if current_x > 600:
                        current_x = 100
                        current_y += 150

            # Parse relationships
            elif any(rel in line for rel in ["--|>", "--*", "--o", "-->", "..>", "..|>", "--", ".."]):
                self._parse_relationship(line, elements, connections, current_x, current_y)

        return elements, connections

    def _parse_relationship(
        self,
        line: str,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        current_x: int,
        current_y: int,
    ) -> None:
        """Parse a relationship line and create connection."""
        # Relationship patterns (order matters - longer patterns first)
        relationship_patterns = [
            ("--|>", "inheritance"),
            ("..|>", "realization"),
            ("--*", "composition"),
            ("--o", "aggregation"),
            ("..>", "dependency"),
            ("-->", "association"),
            ("--", "link"),
            ("..", "dashed"),
        ]

        for pattern, rel_type in relationship_patterns:
            if pattern in line:
                parts = line.split(pattern)
                if len(parts) == 2:
                    source = parts[0].strip()
                    target_and_label = parts[1].strip()

                    # Split target and label
                    if ":" in target_and_label:
                        target, label = target_and_label.split(":", 1)
                        target = target.strip()
                        label = label.strip()
                    else:
                        target = target_and_label
                        label = ""

                    # Ensure classes exist
                    for class_name in [source, target]:
                        if class_name not in elements:
                            element = DiagramElement(
                                id=class_name,
                                element_type=ElementType.NODE,
                                label=class_name,
                                position=Position(current_x, current_y),
                                size=Size(150, 100),
                                properties={"shape": "rectangle", "type": "class"},
                            )
                            elements[class_name] = element

                    # Create connection
                    connection = DiagramConnection(
                        id=f"rel_{source}_{target}_{len(connections)}",
                        source_id=source,
                        target_id=target,
                        label=label,
                        connection_type=rel_type,
                    )
                    connections[connection.id] = connection
                break
