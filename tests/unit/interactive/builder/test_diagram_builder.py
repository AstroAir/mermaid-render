"""
Unit tests for interactive.builder.diagram_builder module.

Tests the DiagramBuilder class for managing diagram elements and connections.
"""

import pytest

from diagramaid.interactive.builder.diagram_builder import DiagramBuilder
from diagramaid.interactive.models import DiagramType, ElementType, Position, Size


@pytest.mark.unit
class TestDiagramBuilder:
    """Unit tests for DiagramBuilder class."""

    def test_initialization(self) -> None:
        """Test DiagramBuilder initialization."""
        builder = DiagramBuilder()
        assert builder.diagram_type == DiagramType.FLOWCHART
        assert len(builder.elements) == 0
        assert len(builder.connections) == 0

    def test_initialization_with_diagram_type(self) -> None:
        """Test DiagramBuilder initialization with specific diagram type."""
        builder = DiagramBuilder(diagram_type=DiagramType.SEQUENCE)
        assert builder.diagram_type == DiagramType.SEQUENCE

    def test_add_element(self) -> None:
        """Test adding element to diagram."""
        builder = DiagramBuilder()
        element = builder.add_element(
            element_type=ElementType.NODE,
            label="Test Node",
            position=Position(10, 20),
            size=Size(100, 50),
        )
        assert len(builder.elements) == 1
        assert builder.elements.get(element.id) == element

    def test_remove_element(self) -> None:
        """Test removing element from diagram."""
        builder = DiagramBuilder()
        element = builder.add_element(
            element_type=ElementType.NODE,
            label="Test Node",
            position=Position(10, 20),
            size=Size(100, 50),
        )
        builder.remove_element(element.id)
        assert len(builder.elements) == 0
        assert builder.elements.get(element.id) is None

    def test_add_connection(self) -> None:
        """Test adding connection between elements."""
        builder = DiagramBuilder()
        source = builder.add_element(
            element_type=ElementType.NODE,
            label="Source",
            position=Position(10, 20),
        )
        target = builder.add_element(
            element_type=ElementType.NODE,
            label="Target",
            position=Position(200, 20),
        )
        connection = builder.add_connection(source.id, target.id)
        assert connection is not None
        assert len(builder.connections) == 1
        assert connection.source_id == source.id
        assert connection.target_id == target.id

    def test_remove_connection(self) -> None:
        """Test removing connection from diagram."""
        builder = DiagramBuilder()
        source = builder.add_element(
            element_type=ElementType.NODE,
            label="Source",
            position=Position(10, 20),
        )
        target = builder.add_element(
            element_type=ElementType.NODE,
            label="Target",
            position=Position(200, 20),
        )
        connection = builder.add_connection(source.id, target.id)
        assert connection is not None
        builder.remove_connection(connection.id)
        assert len(builder.connections) == 0

    def test_clear(self) -> None:
        """Test clearing all elements and connections."""
        builder = DiagramBuilder()
        builder.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(10, 20),
        )
        builder._element_manager.clear()
        builder._connection_manager.clear()
        assert len(builder.elements) == 0
        assert len(builder.connections) == 0

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        builder = DiagramBuilder(diagram_type=DiagramType.FLOWCHART)
        builder.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(10, 20),
            size=Size(100, 50),
        )
        result = builder.to_dict()
        assert result["diagram_type"] == "flowchart"
        assert len(result["elements"]) == 1
        assert len(result["connections"]) == 0

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "diagram_type": "sequence",
            "elements": {
                "elem1": {
                    "id": "elem1",
                    "element_type": "node",
                    "position": {"x": 10, "y": 20},
                    "size": {"width": 100, "height": 50},
                    "label": "Test",
                    "properties": {},
                    "style": {},
                }
            },
            "connections": {},
            "metadata": {},
        }
        builder = DiagramBuilder()
        builder.from_dict(data)
        assert builder.diagram_type == DiagramType.SEQUENCE
        assert len(builder.elements) == 1

    def test_generate_code(self) -> None:
        """Test Mermaid code generation."""
        builder = DiagramBuilder(diagram_type=DiagramType.FLOWCHART)
        source = builder.add_element(
            element_type=ElementType.NODE,
            label="Start",
            position=Position(10, 20),
        )
        target = builder.add_element(
            element_type=ElementType.NODE,
            label="End",
            position=Position(200, 20),
        )
        builder.add_connection(source.id, target.id)
        code = builder.generate_mermaid_code()
        assert "flowchart" in code.lower() or "graph" in code.lower()
