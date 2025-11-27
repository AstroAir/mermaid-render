"""
Connection management for the interactive diagram builder.

This module provides connection CRUD operations and arrow type mappings.
"""

import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from ..models import DiagramConnection


class ConnectionManager:
    """
    Manages diagram connections with CRUD operations.

    Handles connection creation, updates, removal, and provides
    arrow type mappings for different diagram types.
    """

    # Arrow type mappings for flowcharts
    FLOWCHART_ARROWS: dict[str, str] = {
        "default": "-->",
        "dotted": "-.-",
        "thick": "==>",
        "invisible": "~~~",
        "line": "---",
    }

    # Arrow type mappings for sequence diagrams
    SEQUENCE_ARROWS: dict[str, str] = {
        "default": "->>",
        "sync": "->>",
        "async": "-->>",
        "dotted": "-->>",
        "return": "-->>",
    }

    # Relationship mappings for class diagrams
    CLASS_RELATIONSHIPS: dict[str, str] = {
        "default": "-->",
        "inheritance": "--|>",
        "composition": "--*",
        "aggregation": "--o",
        "association": "-->",
        "dependency": "..>",
        "realization": "..|>",
    }

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.connections: dict[str, DiagramConnection] = {}

        # Event handlers
        self._connection_added_handlers: list[Callable[[DiagramConnection], None]] = []
        self._connection_updated_handlers: list[
            Callable[[DiagramConnection], None]
        ] = []
        self._connection_removed_handlers: list[
            Callable[[DiagramConnection], None]
        ] = []

    def add_connection(
        self,
        source_id: str,
        target_id: str,
        label: str = "",
        connection_type: str = "default",
        style: dict[str, Any] | None = None,
        properties: dict[str, Any] | None = None,
        connection_id: str | None = None,
    ) -> DiagramConnection:
        """
        Add a connection between elements.

        Args:
            source_id: Source element ID
            target_id: Target element ID
            label: Connection label
            connection_type: Type of connection
            style: Connection styling
            properties: Connection properties
            connection_id: Optional custom connection ID

        Returns:
            Created connection
        """
        connection = DiagramConnection(
            id=connection_id or str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            label=label,
            connection_type=connection_type,
            style=style or {},
            properties=properties or {},
        )

        self.connections[connection.id] = connection

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

        # Notify handlers
        for handler in self._connection_updated_handlers:
            handler(connection)

        return True

    def remove_connection(self, connection_id: str) -> DiagramConnection | None:
        """
        Remove a connection from the diagram.

        Args:
            connection_id: ID of connection to remove

        Returns:
            Removed connection or None if not found
        """
        if connection_id not in self.connections:
            return None

        connection = self.connections.pop(connection_id)

        # Notify handlers
        for handler in self._connection_removed_handlers:
            handler(connection)

        return connection

    def remove_connections_for_element(self, element_id: str) -> list[str]:
        """
        Remove all connections involving an element.

        Args:
            element_id: Element ID to remove connections for

        Returns:
            List of removed connection IDs
        """
        connections_to_remove = [
            conn_id
            for conn_id, conn in self.connections.items()
            if conn.source_id == element_id or conn.target_id == element_id
        ]

        for conn_id in connections_to_remove:
            self.remove_connection(conn_id)

        return connections_to_remove

    def get_connection(self, connection_id: str) -> DiagramConnection | None:
        """Get connection by ID."""
        return self.connections.get(connection_id)

    def get_all_connections(self) -> list[DiagramConnection]:
        """Get all connections."""
        return list(self.connections.values())

    def get_connections_from(self, element_id: str) -> list[DiagramConnection]:
        """Get all connections originating from an element."""
        return [
            conn for conn in self.connections.values() if conn.source_id == element_id
        ]

    def get_connections_to(self, element_id: str) -> list[DiagramConnection]:
        """Get all connections targeting an element."""
        return [
            conn for conn in self.connections.values() if conn.target_id == element_id
        ]

    def has_connection(self, connection_id: str) -> bool:
        """Check if connection exists."""
        return connection_id in self.connections

    def clear(self) -> None:
        """Remove all connections."""
        self.connections.clear()

    def get_flowchart_arrow(self, connection_type: str) -> str:
        """Get flowchart arrow syntax for connection type."""
        return self.FLOWCHART_ARROWS.get(connection_type, "-->")

    def get_sequence_arrow(self, connection_type: str) -> str:
        """Get sequence diagram arrow syntax for connection type."""
        return self.SEQUENCE_ARROWS.get(connection_type, "->>")

    def get_class_relationship(self, connection_type: str) -> str:
        """Get class diagram relationship syntax for connection type."""
        return self.CLASS_RELATIONSHIPS.get(connection_type, "-->")

    # Event handler registration
    def on_connection_added(
        self, handler: Callable[[DiagramConnection], None]
    ) -> None:
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
