"""
Serialization utilities for the interactive diagram builder.

This module provides serialization and deserialization functionality
for diagram data.
"""

from typing import TYPE_CHECKING, Any

from ..models import DiagramConnection, DiagramElement, DiagramType

if TYPE_CHECKING:
    from .diagram_builder import DiagramBuilder


class DiagramSerializer:
    """
    Handles serialization and deserialization of diagram data.

    Provides methods to convert diagram state to/from dictionaries
    and other formats.
    """

    @staticmethod
    def to_dict(
        diagram_type: DiagramType,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert diagram state to dictionary.

        Args:
            diagram_type: Type of diagram
            elements: Dictionary of elements
            connections: Dictionary of connections
            metadata: Diagram metadata

        Returns:
            Dictionary representation of diagram
        """
        return {
            "diagram_type": diagram_type.value,
            "elements": {eid: elem.to_dict() for eid, elem in elements.items()},
            "connections": {cid: conn.to_dict() for cid, conn in connections.items()},
            "metadata": metadata,
        }

    @staticmethod
    def from_dict(
        data: dict[str, Any],
    ) -> tuple[
        DiagramType,
        dict[str, DiagramElement],
        dict[str, DiagramConnection],
        dict[str, Any],
    ]:
        """
        Load diagram state from dictionary.

        Args:
            data: Dictionary containing diagram data

        Returns:
            Tuple of (diagram_type, elements, connections, metadata)
        """
        diagram_type = DiagramType(data["diagram_type"])

        elements = {
            eid: DiagramElement.from_dict(elem_data)
            for eid, elem_data in data.get("elements", {}).items()
        }

        connections = {
            cid: DiagramConnection.from_dict(conn_data)
            for cid, conn_data in data.get("connections", {}).items()
        }

        metadata = data.get("metadata", {})

        return diagram_type, elements, connections, metadata

    @staticmethod
    def load_into_builder(builder: "DiagramBuilder", data: dict[str, Any]) -> None:
        """
        Load diagram data into an existing builder.

        Args:
            builder: DiagramBuilder instance to load into
            data: Dictionary containing diagram data
        """
        diagram_type, elements, connections, metadata = DiagramSerializer.from_dict(
            data
        )

        builder.diagram_type = diagram_type
        builder._element_manager.elements = elements
        builder._connection_manager.connections = connections
        builder.metadata = metadata

    @staticmethod
    def export_to_json(
        diagram_type: DiagramType,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        metadata: dict[str, Any],
        indent: int = 2,
    ) -> str:
        """
        Export diagram to JSON string.

        Args:
            diagram_type: Type of diagram
            elements: Dictionary of elements
            connections: Dictionary of connections
            metadata: Diagram metadata
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        import json

        data = DiagramSerializer.to_dict(
            diagram_type, elements, connections, metadata
        )
        return json.dumps(data, indent=indent)

    @staticmethod
    def import_from_json(json_str: str) -> tuple[
        DiagramType,
        dict[str, DiagramElement],
        dict[str, DiagramConnection],
        dict[str, Any],
    ]:
        """
        Import diagram from JSON string.

        Args:
            json_str: JSON string containing diagram data

        Returns:
            Tuple of (diagram_type, elements, connections, metadata)
        """
        import json

        data = json.loads(json_str)
        return DiagramSerializer.from_dict(data)
