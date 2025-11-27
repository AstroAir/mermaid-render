"""
Flowchart code generator for the interactive diagram builder.

This module provides Mermaid code generation for flowchart diagrams.
"""

from typing import Any

from ...models import DiagramConnection, DiagramElement, ElementType
from .base import CodeGenerator


class FlowchartGenerator(CodeGenerator):
    """
    Generates Mermaid code for flowchart diagrams.

    Supports various node shapes and connection types.
    """

    # Node shape syntax mappings
    SHAPE_SYNTAX: dict[str, tuple[str, str]] = {
        "rectangle": ("[", "]"),
        "rounded": ("(", ")"),
        "circle": ("((", "))"),
        "diamond": ("{", "}"),
        "hexagon": ("{{", "}}"),
        "stadium": ("([", "])"),
        "subroutine": ("[[", "]]"),
        "cylinder": ("[(", ")]"),
        "asymmetric": (">", "]"),
        "parallelogram": ("[/", "/]"),
        "parallelogram_alt": ("[\\", "\\]"),
        "trapezoid": ("[/", "\\]"),
        "trapezoid_alt": ("[\\", "/]"),
    }

    # Arrow syntax mappings
    ARROW_SYNTAX: dict[str, str] = {
        "default": "-->",
        "dotted": "-.-",
        "thick": "==>",
        "invisible": "~~~",
        "line": "---",
        "arrow_open": "---",
        "arrow_circle": "--o",
        "arrow_cross": "--x",
    }

    def generate(
        self,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        metadata: dict[str, Any],
    ) -> str:
        """
        Generate flowchart Mermaid code.

        Args:
            elements: Dictionary of diagram elements
            connections: Dictionary of diagram connections
            metadata: Diagram metadata

        Returns:
            Generated Mermaid flowchart code
        """
        direction = metadata.get("direction", "TD")
        lines = [f"flowchart {direction}"]

        # Add title if present
        self._add_title_comment(lines, metadata)

        # Add nodes
        for element in elements.values():
            if element.element_type == ElementType.NODE:
                shape = element.properties.get("shape", "rectangle")
                node_syntax = self._get_node_syntax(element.id, element.label, shape)
                lines.append(f"    {node_syntax}")

        if elements:
            lines.append("")

        # Add connections
        for connection in connections.values():
            arrow = self._get_arrow_syntax(connection.connection_type)
            if connection.label:
                lines.append(
                    f"    {connection.source_id} {arrow}|{connection.label}| {connection.target_id}"
                )
            else:
                lines.append(
                    f"    {connection.source_id} {arrow} {connection.target_id}"
                )

        return "\n".join(lines)

    def _get_node_syntax(self, node_id: str, label: str, shape: str) -> str:
        """
        Get flowchart node syntax for shape.

        Args:
            node_id: Node identifier
            label: Node label
            shape: Shape type

        Returns:
            Mermaid node syntax
        """
        if shape in self.SHAPE_SYNTAX:
            open_bracket, close_bracket = self.SHAPE_SYNTAX[shape]
            return f"{node_id}{open_bracket}{label}{close_bracket}"
        # Default to rectangle
        return f"{node_id}[{label}]"

    def _get_arrow_syntax(self, connection_type: str) -> str:
        """
        Get flowchart arrow syntax for connection type.

        Args:
            connection_type: Type of connection

        Returns:
            Mermaid arrow syntax
        """
        return self.ARROW_SYNTAX.get(connection_type, "-->")
