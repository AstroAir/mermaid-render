"""
ER diagram parser for the interactive diagram builder.

This module provides Mermaid code parsing for ER diagrams.
"""

import re

from ...models import DiagramConnection, DiagramElement, ElementType, Position, Size
from .base import DiagramParser


class ERDiagramParser(DiagramParser):
    """
    Parses Mermaid ER diagram code into diagram elements.

    Supports entity definitions and relationships.
    """

    def parse(
        self, lines: list[str]
    ) -> tuple[dict[str, DiagramElement], dict[str, DiagramConnection]]:
        """
        Parse ER diagram Mermaid code.

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

            # Parse entity definitions (ENTITY_NAME { ... })
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
                    elements[entity_match] = element
                    current_x += 200
                    if current_x > 600:
                        current_x = 100
                        current_y += 150

            # Parse relationships (ENTITY1 ||--o{ ENTITY2 : relationship)
            elif any(rel in line for rel in ["||", "|o", "o|", "}|", "|{", "o{", "}o"]):
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
        """Parse an ER relationship line and create connection."""
        # ER relationship patterns
        # Format: ENTITY1 cardinality--cardinality ENTITY2 : label
        relationship_pattern = re.compile(
            r"(\w+)\s+([|o}{]+)--([|o}{]+)\s+(\w+)(?:\s*:\s*(.+))?"
        )

        match = relationship_pattern.match(line)
        if match:
            source = match.group(1)
            left_cardinality = match.group(2)
            right_cardinality = match.group(3)
            target = match.group(4)
            label = match.group(5) or ""

            # Ensure entities exist
            for entity_name in [source, target]:
                if entity_name not in elements:
                    element = DiagramElement(
                        id=entity_name,
                        element_type=ElementType.NODE,
                        label=entity_name,
                        position=Position(current_x, current_y),
                        size=Size(150, 100),
                        properties={"shape": "rectangle", "type": "entity"},
                    )
                    elements[entity_name] = element

            # Create connection with cardinality info
            connection = DiagramConnection(
                id=f"rel_{source}_{target}_{len(connections)}",
                source_id=source,
                target_id=target,
                label=label.strip(),
                connection_type="er_relationship",
                properties={
                    "left_cardinality": left_cardinality,
                    "right_cardinality": right_cardinality,
                },
            )
            connections[connection.id] = connection
