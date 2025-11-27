"""
Sequence diagram code generator for the interactive diagram builder.

This module provides Mermaid code generation for sequence diagrams.
"""

from typing import Any

from ...models import DiagramConnection, DiagramElement
from .base import CodeGenerator


class SequenceDiagramGenerator(CodeGenerator):
    """
    Generates Mermaid code for sequence diagrams.

    Supports participants, messages, and various arrow types.
    """

    # Arrow syntax mappings
    ARROW_SYNTAX: dict[str, str] = {
        "default": "->>",
        "sync": "->>",
        "async": "-->>",
        "dotted": "-->>",
        "return": "-->>",
        "solid": "->",
        "dotted_open": "-->",
        "cross": "-x",
        "dotted_cross": "--x",
    }

    def generate(
        self,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        metadata: dict[str, Any],
    ) -> str:
        """
        Generate sequence diagram Mermaid code.

        Args:
            elements: Dictionary of diagram elements
            connections: Dictionary of diagram connections
            metadata: Diagram metadata

        Returns:
            Generated Mermaid sequence diagram code
        """
        lines = ["sequenceDiagram"]

        # Add title if present
        if metadata.get("title"):
            lines.append(f"    title {metadata['title']}")
            lines.append("")

        # Collect participants
        participants: set[str] = set()

        # Process elements to find participants
        for element in elements.values():
            if element.properties.get("type") == "participant":
                participants.add(element.id)

        # Add participant declarations
        for participant in sorted(participants):
            participant_element = next(
                (e for e in elements.values() if e.id == participant), None
            )
            if participant_element and participant_element.label != participant:
                lines.append(
                    f"    participant {participant} as {participant_element.label}"
                )
            else:
                lines.append(f"    participant {participant}")

        if participants:
            lines.append("")

        # Process connections as messages
        for connection in connections.values():
            source = connection.source_id
            target = connection.target_id
            label = connection.label or "message"

            # Determine message type based on connection type
            arrow = self._get_arrow_syntax(connection.connection_type)

            if connection.label:
                lines.append(f"    {source}{arrow}{target}: {label}")
            else:
                lines.append(f"    {source}{arrow}{target}: ")

        return "\n".join(lines)

    def _get_arrow_syntax(self, connection_type: str) -> str:
        """
        Get sequence diagram arrow syntax for connection type.

        Args:
            connection_type: Type of connection

        Returns:
            Mermaid arrow syntax
        """
        return self.ARROW_SYNTAX.get(connection_type, "->>")
