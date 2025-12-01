"""
State diagram parser for the interactive diagram builder.

This module provides Mermaid code parsing for state diagrams.
"""

from ...models import DiagramConnection, DiagramElement, ElementType, Position, Size
from .base import DiagramParser


class StateDiagramParser(DiagramParser):
    """
    Parses Mermaid state diagram code into diagram elements.

    Supports state definitions and transitions.
    """

    def parse(
        self, lines: list[str]
    ) -> tuple[dict[str, DiagramElement], dict[str, DiagramConnection]]:
        """
        Parse state diagram Mermaid code.

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

            # Parse state transitions (State1 --> State2)
            if "-->" in line:
                parts = line.split("-->")
                if len(parts) == 2:
                    source = parts[0].strip()
                    target_and_label = parts[1].strip()

                    # Check for label (State1 --> State2 : label)
                    if ":" in target_and_label:
                        target, label = target_and_label.split(":", 1)
                        target = target.strip()
                        label = label.strip()
                    else:
                        target = target_and_label
                        label = ""

                    # Create states if they don't exist
                    for state_id in [source, target]:
                        if state_id not in elements:
                            # Handle special states
                            if state_id == "[*]":
                                shape = "circle"
                                display_label = ""
                            else:
                                shape = "rounded"
                                display_label = state_id

                            element = DiagramElement(
                                id=state_id,
                                element_type=ElementType.NODE,
                                label=display_label or state_id,
                                position=Position(current_x, current_y),
                                size=Size(120, 60),
                                properties={"shape": shape, "type": "state"},
                            )
                            elements[state_id] = element
                            current_x += 200
                            if current_x > 600:
                                current_x = 100
                                current_y += 100

                    # Create connection
                    connection = DiagramConnection(
                        id=f"trans_{source}_{target}_{len(connections)}",
                        source_id=source,
                        target_id=target,
                        label=label,
                        connection_type="default",
                    )
                    connections[connection.id] = connection

            # Parse state declarations (state "Description" as StateName)
            elif line.startswith("state"):
                parts = line.split()
                if len(parts) >= 2:
                    # Handle quoted description
                    if '"' in line:
                        import re
                        match = re.search(r'state\s+"([^"]+)"\s+as\s+(\w+)', line)
                        if match:
                            description = match.group(1)
                            state_id = match.group(2)
                        else:
                            continue
                    else:
                        state_id = parts[1]
                        description = state_id

                    if state_id not in elements:
                        element = DiagramElement(
                            id=state_id,
                            element_type=ElementType.NODE,
                            label=description,
                            position=Position(current_x, current_y),
                            size=Size(120, 60),
                            properties={"shape": "rounded", "type": "state"},
                        )
                        elements[state_id] = element
                        current_x += 200
                        if current_x > 600:
                            current_x = 100
                            current_y += 100

        return elements, connections
