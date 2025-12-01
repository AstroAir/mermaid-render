"""
Unit tests for interactive.models.elements module.

Tests the DiagramElement and DiagramConnection classes.
"""

import pytest

from diagramaid.interactive.models.elements import DiagramConnection, DiagramElement
from diagramaid.interactive.models.enums import ElementType
from diagramaid.interactive.models.geometry import Position, Size


@pytest.mark.unit
class TestDiagramElement:
    """Unit tests for DiagramElement class."""

    def test_initialization(self) -> None:
        """Test DiagramElement initialization."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        assert element.element_type == ElementType.NODE
        assert element.label == "Test"

    def test_id_generation(self) -> None:
        """Test that ID is auto-generated."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test"
        )
        assert element.id is not None
        assert len(element.id) > 0

    def test_custom_id(self) -> None:
        """Test custom ID assignment."""
        element = DiagramElement(
            id="custom_id",
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test"
        )
        assert element.id == "custom_id"

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        result = element.to_dict()
        assert result["element_type"] == "node"
        assert result["label"] == "Test"

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": "elem1",
            "element_type": "node",
            "position": {"x": 10, "y": 20},
            "size": {"width": 100, "height": 50},
            "label": "Test",
            "properties": {},
            "style": {}
        }
        element = DiagramElement.from_dict(data)
        assert element.id == "elem1"
        assert element.label == "Test"


@pytest.mark.unit
class TestDiagramConnection:
    """Unit tests for DiagramConnection class."""

    def test_initialization(self) -> None:
        """Test DiagramConnection initialization."""
        connection = DiagramConnection(
            id="conn1",
            source_id="source",
            target_id="target",
        )
        assert connection.source_id == "source"
        assert connection.target_id == "target"

    def test_id_generation(self) -> None:
        """Test that ID is auto-generated when empty."""
        connection = DiagramConnection(
            id="",
            source_id="source",
            target_id="target",
        )
        assert connection.id is not None
        assert len(connection.id) > 0

    def test_with_label(self) -> None:
        """Test connection with label."""
        connection = DiagramConnection(
            id="conn1",
            source_id="source",
            target_id="target",
            label="connects",
        )
        assert connection.label == "connects"

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        connection = DiagramConnection(
            id="conn1",
            source_id="source",
            target_id="target",
            label="arrow",
        )
        result = connection.to_dict()
        assert result["source_id"] == "source"
        assert result["target_id"] == "target"
        assert result["label"] == "arrow"

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        from datetime import datetime

        now = datetime.now().isoformat()
        data = {
            "id": "conn1",
            "source_id": "src",
            "target_id": "tgt",
            "label": "link",
            "connection_type": "default",
            "properties": {},
            "style": {},
            "control_points": [],
            "created_at": now,
            "updated_at": now,
        }
        connection = DiagramConnection.from_dict(data)
        assert connection.id == "conn1"
        assert connection.source_id == "src"
        assert connection.target_id == "tgt"
