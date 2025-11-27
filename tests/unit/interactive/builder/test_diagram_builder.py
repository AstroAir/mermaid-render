"""
Unit tests for interactive.builder.diagram_builder module.

Tests the DiagramBuilder class for managing diagram elements and connections.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mermaid_render.interactive.builder.diagram_builder import DiagramBuilder
from mermaid_render.interactive.models import (
    DiagramElement,
    DiagramConnection,
    DiagramType,
    ElementType,
    Position,
    Size,
)


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
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test Node"
        )
        
        builder.add_element(element)
        
        assert len(builder.elements) == 1
        assert builder.get_element(element.id) == element

    def test_remove_element(self) -> None:
        """Test removing element from diagram."""
        builder = DiagramBuilder()
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test Node"
        )
        
        builder.add_element(element)
        builder.remove_element(element.id)
        
        assert len(builder.elements) == 0
        assert builder.get_element(element.id) is None

    def test_add_connection(self) -> None:
        """Test adding connection between elements."""
        builder = DiagramBuilder()
        
        source = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Source"
        )
        target = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(200, 20),
            size=Size(100, 50),
            label="Target"
        )
        
        builder.add_element(source)
        builder.add_element(target)
        
        connection = builder.add_connection(source.id, target.id)
        
        assert len(builder.connections) == 1
        assert connection.source_id == source.id
        assert connection.target_id == target.id

    def test_remove_connection(self) -> None:
        """Test removing connection from diagram."""
        builder = DiagramBuilder()
        
        source = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Source"
        )
        target = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(200, 20),
            size=Size(100, 50),
            label="Target"
        )
        
        builder.add_element(source)
        builder.add_element(target)
        connection = builder.add_connection(source.id, target.id)
        
        builder.remove_connection(connection.id)
        
        assert len(builder.connections) == 0

    def test_clear(self) -> None:
        """Test clearing all elements and connections."""
        builder = DiagramBuilder()
        
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        builder.add_element(element)
        
        builder.clear()
        
        assert len(builder.elements) == 0
        assert len(builder.connections) == 0

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        builder = DiagramBuilder(diagram_type=DiagramType.FLOWCHART)
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        builder.add_element(element)
        
        result = builder.to_dict()
        
        assert result["diagram_type"] == "flowchart"
        assert len(result["elements"]) == 1
        assert len(result["connections"]) == 0

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "diagram_type": "sequence",
            "elements": [
                {
                    "id": "elem1",
                    "element_type": "node",
                    "position": {"x": 10, "y": 20},
                    "size": {"width": 100, "height": 50},
                    "label": "Test",
                    "properties": {},
                    "style": {}
                }
            ],
            "connections": []
        }
        
        builder = DiagramBuilder.from_dict(data)
        
        assert builder.diagram_type == DiagramType.SEQUENCE
        assert len(builder.elements) == 1

    def test_generate_code(self) -> None:
        """Test Mermaid code generation."""
        builder = DiagramBuilder(diagram_type=DiagramType.FLOWCHART)
        
        source = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Start"
        )
        target = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(200, 20),
            size=Size(100, 50),
            label="End"
        )
        
        builder.add_element(source)
        builder.add_element(target)
        builder.add_connection(source.id, target.id)
        
        code = builder.generate_code()
        
        assert "flowchart" in code.lower() or "graph" in code.lower()
