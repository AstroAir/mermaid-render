"""
Unit tests for interactive.builder.serialization module.

Tests the DiagramSerializer class for diagram serialization/deserialization.
"""

import pytest
import json
from unittest.mock import Mock, patch

from mermaid_render.interactive.builder.serialization import DiagramSerializer
from mermaid_render.interactive.models import (
    DiagramElement,
    DiagramConnection,
    DiagramType,
    ElementType,
    Position,
    Size,
)


@pytest.mark.unit
class TestDiagramSerializer:
    """Unit tests for DiagramSerializer class."""

    def test_serialize_element(self) -> None:
        """Test serializing a single element."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test Node"
        )
        
        result = DiagramSerializer.serialize_element(element)
        
        assert result["element_type"] == "node"
        assert result["position"]["x"] == 10
        assert result["position"]["y"] == 20
        assert result["size"]["width"] == 100
        assert result["size"]["height"] == 50
        assert result["label"] == "Test Node"

    def test_deserialize_element(self) -> None:
        """Test deserializing a single element."""
        data = {
            "id": "elem1",
            "element_type": "node",
            "position": {"x": 15, "y": 25},
            "size": {"width": 80, "height": 60},
            "label": "Deserialized",
            "properties": {},
            "style": {}
        }
        
        element = DiagramSerializer.deserialize_element(data)
        
        assert element.id == "elem1"
        assert element.element_type == ElementType.NODE
        assert element.position.x == 15
        assert element.label == "Deserialized"

    def test_serialize_connection(self) -> None:
        """Test serializing a connection."""
        connection = DiagramConnection(
            source_id="source",
            target_id="target",
            label="connects to"
        )
        
        result = DiagramSerializer.serialize_connection(connection)
        
        assert result["source_id"] == "source"
        assert result["target_id"] == "target"
        assert result["label"] == "connects to"

    def test_deserialize_connection(self) -> None:
        """Test deserializing a connection."""
        data = {
            "id": "conn1",
            "source_id": "src",
            "target_id": "tgt",
            "label": "arrow",
            "properties": {}
        }
        
        connection = DiagramSerializer.deserialize_connection(data)
        
        assert connection.id == "conn1"
        assert connection.source_id == "src"
        assert connection.target_id == "tgt"

    def test_serialize_diagram(self) -> None:
        """Test serializing complete diagram."""
        elements = [
            DiagramElement(
                element_type=ElementType.NODE,
                position=Position(10, 20),
                size=Size(100, 50),
                label="Node 1"
            ),
            DiagramElement(
                element_type=ElementType.NODE,
                position=Position(200, 20),
                size=Size(100, 50),
                label="Node 2"
            )
        ]
        connections = [
            DiagramConnection(
                source_id=elements[0].id,
                target_id=elements[1].id
            )
        ]
        
        result = DiagramSerializer.serialize_diagram(
            diagram_type=DiagramType.FLOWCHART,
            elements=elements,
            connections=connections
        )
        
        assert result["diagram_type"] == "flowchart"
        assert len(result["elements"]) == 2
        assert len(result["connections"]) == 1

    def test_deserialize_diagram(self) -> None:
        """Test deserializing complete diagram."""
        data = {
            "diagram_type": "sequence",
            "elements": [
                {
                    "id": "e1",
                    "element_type": "node",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 50, "height": 50},
                    "label": "A",
                    "properties": {},
                    "style": {}
                }
            ],
            "connections": []
        }
        
        diagram_type, elements, connections = DiagramSerializer.deserialize_diagram(data)
        
        assert diagram_type == DiagramType.SEQUENCE
        assert len(elements) == 1
        assert len(connections) == 0

    def test_to_json(self) -> None:
        """Test converting diagram to JSON string."""
        elements = [
            DiagramElement(
                element_type=ElementType.NODE,
                position=Position(10, 20),
                size=Size(100, 50),
                label="Test"
            )
        ]
        
        json_str = DiagramSerializer.to_json(
            diagram_type=DiagramType.FLOWCHART,
            elements=elements,
            connections=[]
        )
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["diagram_type"] == "flowchart"

    def test_from_json(self) -> None:
        """Test creating diagram from JSON string."""
        json_str = '''
        {
            "diagram_type": "class",
            "elements": [],
            "connections": []
        }
        '''
        
        diagram_type, elements, connections = DiagramSerializer.from_json(json_str)
        
        assert diagram_type == DiagramType.CLASS
        assert len(elements) == 0
        assert len(connections) == 0

    def test_invalid_json(self) -> None:
        """Test handling invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            DiagramSerializer.from_json("invalid json")
