"""
Class diagram code generator for the interactive diagram builder.

This module provides Mermaid code generation for class diagrams.
"""

from typing import Any

from ...models import DiagramConnection, DiagramElement
from .base import CodeGenerator


class ClassDiagramGenerator(CodeGenerator):
    """
    Generates Mermaid code for class diagrams.

    Supports classes, attributes, methods, and relationships.
    """

    # Relationship syntax mappings
    RELATIONSHIP_SYNTAX: dict[str, str] = {
        "default": "-->",
        "inheritance": "--|>",
        "composition": "--*",
        "aggregation": "--o",
        "association": "-->",
        "dependency": "..>",
        "realization": "..|>",
        "link": "--",
        "dashed": "..",
    }

    def generate(
        self,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        metadata: dict[str, Any],
    ) -> str:
        """
        Generate class diagram Mermaid code.

        Args:
            elements: Dictionary of diagram elements
            connections: Dictionary of diagram connections
            metadata: Diagram metadata

        Returns:
            Generated Mermaid class diagram code
        """
        lines = ["classDiagram"]

        # Add title if present
        if metadata.get("title"):
            lines.append(f"    title {metadata['title']}")
            lines.append("")

        # Process elements as classes
        for element in elements.values():
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
        for connection in connections.values():
            source = connection.source_id
            target = connection.target_id

            # Determine relationship type
            relationship = self._get_relationship_syntax(connection.connection_type)

            if connection.label:
                lines.append(f"    {source} {relationship} {target} : {connection.label}")
            else:
                lines.append(f"    {source} {relationship} {target}")

        return "\n".join(lines)

    def _get_relationship_syntax(self, connection_type: str) -> str:
        """
        Get class diagram relationship syntax for connection type.

        Args:
            connection_type: Type of connection

        Returns:
            Mermaid relationship syntax
        """
        return self.RELATIONSHIP_SYNTAX.get(connection_type, "-->")
