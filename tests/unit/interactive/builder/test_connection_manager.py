"""
Unit tests for interactive.builder.connection_manager module.

Tests the ConnectionManager class for managing diagram connections.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.builder.connection_manager import ConnectionManager
from mermaid_render.interactive.models import DiagramConnection


@pytest.mark.unit
class TestConnectionManager:
    """Unit tests for ConnectionManager class."""

    def test_initialization(self) -> None:
        """Test ConnectionManager initialization."""
        manager = ConnectionManager()
        
        assert len(manager.connections) == 0

    def test_add_connection(self) -> None:
        """Test adding connection."""
        manager = ConnectionManager()
        
        connection = manager.add("source_id", "target_id")
        
        assert len(manager.connections) == 1
        assert connection.source_id == "source_id"
        assert connection.target_id == "target_id"

    def test_remove_connection(self) -> None:
        """Test removing connection."""
        manager = ConnectionManager()
        connection = manager.add("source_id", "target_id")
        
        manager.remove(connection.id)
        
        assert len(manager.connections) == 0

    def test_get_connection(self) -> None:
        """Test getting connection by ID."""
        manager = ConnectionManager()
        connection = manager.add("source_id", "target_id")
        
        result = manager.get(connection.id)
        
        assert result == connection

    def test_get_connection_not_found(self) -> None:
        """Test getting non-existent connection."""
        manager = ConnectionManager()
        
        result = manager.get("nonexistent")
        
        assert result is None

    def test_get_connections_from_source(self) -> None:
        """Test getting connections from source element."""
        manager = ConnectionManager()
        
        manager.add("source1", "target1")
        manager.add("source1", "target2")
        manager.add("source2", "target3")
        
        connections = manager.get_from_source("source1")
        
        assert len(connections) == 2

    def test_get_connections_to_target(self) -> None:
        """Test getting connections to target element."""
        manager = ConnectionManager()
        
        manager.add("source1", "target1")
        manager.add("source2", "target1")
        manager.add("source3", "target2")
        
        connections = manager.get_to_target("target1")
        
        assert len(connections) == 2

    def test_remove_connections_for_element(self) -> None:
        """Test removing all connections for an element."""
        manager = ConnectionManager()
        
        manager.add("elem1", "elem2")
        manager.add("elem2", "elem3")
        manager.add("elem3", "elem1")
        
        manager.remove_for_element("elem1")
        
        # Should remove connections where elem1 is source or target
        assert len(manager.connections) == 1

    def test_clear(self) -> None:
        """Test clearing all connections."""
        manager = ConnectionManager()
        
        manager.add("source1", "target1")
        manager.add("source2", "target2")
        
        manager.clear()
        
        assert len(manager.connections) == 0

    def test_update_connection_label(self) -> None:
        """Test updating connection label."""
        manager = ConnectionManager()
        connection = manager.add("source_id", "target_id")
        
        manager.update(connection.id, label="New Label")
        
        updated = manager.get(connection.id)
        assert updated.label == "New Label"

    def test_connection_exists(self) -> None:
        """Test checking if connection exists."""
        manager = ConnectionManager()
        
        manager.add("source", "target")
        
        assert manager.exists("source", "target")
        assert not manager.exists("target", "source")
        assert not manager.exists("other", "target")
