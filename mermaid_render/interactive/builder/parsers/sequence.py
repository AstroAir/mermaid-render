"""
Sequence diagram parser for the interactive diagram builder.

This module provides Mermaid code parsing for sequence diagrams.
"""

from ...models import DiagramConnection, DiagramElement, ElementType, Position, Size
from .base import DiagramParser


class SequenceDiagramParser(DiagramParser):
    """
    Parses Mermaid sequence diagram code into diagram elements.

    Supports participants and message flows.
    """

    def parse(
        self, lines: list[str]
    ) -> tuple[dict[str, DiagramElement], dict[str, DiagramConnection]]:
        """
        Parse sequence diagram Mermaid code.

        Args:
            lines: Lines of Mermaid code (excluding diagram declaration)

        Returns:
            Tuple of (elements dict, connections dict)
        """
        elements: dict[str, DiagramElement] = {}
        connections: dict[str, DiagramConnection] = {}

        current_y = 50
        participant_x = 100

        for line in lines:
            line = line.strip()
            if self._skip_line(line):
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
                            label = " ".join(parts[as_index + 1:])

                    element = DiagramElement(
                        id=participant_id,
                        element_type=ElementType.NODE,
                        label=label,
                        position=Position(participant_x, current_y),
                        size=Size(120, 60),
                        properties={"shape": "rectangle", "type": "participant"},
                    )
                    elements[participant_id] = element
                    participant_x += 200

            # Parse actor declarations
            elif line.startswith("actor"):
                parts = line.split()
                if len(parts) >= 2:
                    actor_id = parts[1]
                    label = actor_id
                    if "as" in parts:
                        as_index = parts.index("as")
                        if as_index + 1 < len(parts):
                            label = " ".join(parts[as_index + 1:])

                    element = DiagramElement(
                        id=actor_id,
                        element_type=ElementType.NODE,
                        label=label,
                        position=Position(participant_x, current_y),
                        size=Size(120, 60),
                        properties={"shape": "actor", "type": "participant"},
                    )
                    elements[actor_id] = element
                    participant_x += 200

            # Parse messages (A->>B: message)
            elif "->>" in line or "-->>" in line or "->" in line or "-->" in line:
                self._parse_message(line, elements, connections, participant_x, current_y)

        return elements, connections

    def _parse_message(
        self,
        line: str,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        participant_x: int,
        current_y: int,
    ) -> None:
        """Parse a message line and create connection."""
        # Determine arrow type
        if "-->>" in line:
            arrow = "-->>"
            connection_type = "async"
        elif "->>" in line:
            arrow = "->>"
            connection_type = "sync"
        elif "-->" in line:
            arrow = "-->"
            connection_type = "dotted"
        elif "->" in line:
            arrow = "->"
            connection_type = "solid"
        else:
            return

        parts = line.split(arrow)
        if len(parts) != 2:
            return

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

        # Ensure participants exist
        for pid in [source, target]:
            if pid not in elements:
                element = DiagramElement(
                    id=pid,
                    element_type=ElementType.NODE,
                    label=pid,
                    position=Position(participant_x, current_y),
                    size=Size(120, 60),
                    properties={"shape": "rectangle", "type": "participant"},
                )
                elements[pid] = element

        # Create connection
        connection = DiagramConnection(
            id=f"msg_{source}_{target}_{len(connections)}",
            source_id=source,
            target_id=target,
            label=label,
            connection_type=connection_type,
        )
        connections[connection.id] = connection
