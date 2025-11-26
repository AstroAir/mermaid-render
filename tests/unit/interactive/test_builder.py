"""
Comprehensive unit tests for interactive diagram builder.

Tests the core diagram building functionality including elements, connections,
and real-time updates with proper validation and error handling.
"""

import pytest
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock

from mermaid_render.interactive.builder import (
    ElementType,
    DiagramType,
    Position,
    Size,
    DiagramElement,
    DiagramConnection,
    DiagramBuilder,
)
from mermaid_render.exceptions import DiagramError


class TestElementType:
    """Test ElementType enum."""

    def test_enum_values(self) -> None:
        """Test enum values."""
        assert ElementType.NODE.value == "node"
        assert ElementType.EDGE.value == "edge"
        assert ElementType.CONTAINER.value == "container"
        assert ElementType.ANNOTATION.value == "annotation"


class TestDiagramType:
    """Test DiagramType enum."""

    def test_enum_values(self) -> None:
        """Test enum values."""
        assert DiagramType.FLOWCHART.value == "flowchart"
        assert DiagramType.SEQUENCE.value == "sequence"
        assert DiagramType.CLASS.value == "class"
        assert DiagramType.STATE.value == "state"
        assert DiagramType.ER.value == "er"


class TestPosition:
    """Test Position dataclass."""

    def test_initialization(self) -> None:
        """Test position initialization."""
        pos = Position(10.5, 20.3)
        
        assert pos.x == 10.5
        assert pos.y == 20.3

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        pos = Position(10.5, 20.3)
        result = pos.to_dict()
        
        assert result == {"x": 10.5, "y": 20.3}

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {"x": 15.7, "y": 25.9}
        pos = Position.from_dict(data)
        
        assert pos.x == 15.7
        assert pos.y == 25.9

    def test_from_dict_invalid_data(self) -> None:
        """Test creation from invalid dictionary."""
        with pytest.raises(KeyError):
            Position.from_dict({"x": 10})  # Missing y
        
        with pytest.raises(KeyError):
            Position.from_dict({"y": 20})  # Missing x

    def test_equality(self) -> None:
        """Test position equality."""
        pos1 = Position(10, 20)
        pos2 = Position(10, 20)
        pos3 = Position(10, 21)
        
        assert pos1 == pos2
        assert pos1 != pos3

    def test_distance(self) -> None:
        """Test distance calculation between positions."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        
        distance = pos1.distance_to(pos2)
        assert distance == 5.0  # 3-4-5 triangle

    def test_move(self) -> None:
        """Test moving position by offset."""
        pos = Position(10, 20)
        new_pos = pos.move(5, -3)
        
        assert new_pos.x == 15
        assert new_pos.y == 17
        assert pos.x == 10  # Original unchanged
        assert pos.y == 20


class TestSize:
    """Test Size dataclass."""

    def test_initialization(self) -> None:
        """Test size initialization."""
        size = Size(100, 50)
        
        assert size.width == 100
        assert size.height == 50

    def test_initialization_negative_values(self) -> None:
        """Test initialization with negative values."""
        with pytest.raises(ValueError, match="Width must be positive"):
            Size(-10, 50)
        
        with pytest.raises(ValueError, match="Height must be positive"):
            Size(100, -20)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        size = Size(100, 50)
        result = size.to_dict()
        
        assert result == {"width": 100, "height": 50}

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {"width": 120, "height": 80}
        size = Size.from_dict(data)
        
        assert size.width == 120
        assert size.height == 80

    def test_area(self) -> None:
        """Test area calculation."""
        size = Size(10, 20)
        assert size.area() == 200

    def test_aspect_ratio(self) -> None:
        """Test aspect ratio calculation."""
        size = Size(16, 9)
        assert abs(size.aspect_ratio() - 16/9) < 0.001

    def test_scale(self) -> None:
        """Test scaling size."""
        size = Size(100, 50)
        scaled = size.scale(2.0)
        
        assert scaled.width == 200
        assert scaled.height == 100


class TestDiagramElement:
    """Test DiagramElement class."""

    def test_initialization_basic(self) -> None:
        """Test basic element initialization."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test Node"
        )
        
        assert element.element_type == ElementType.NODE
        assert element.position.x == 10
        assert element.position.y == 20
        assert element.size.width == 100
        assert element.size.height == 50
        assert element.label == "Test Node"
        assert element.properties == {}
        assert element.style == {}
        assert isinstance(element.id, str)
        assert len(element.id) > 0

    def test_initialization_with_id(self) -> None:
        """Test element initialization with custom ID."""
        custom_id = "custom_element_id"
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test",
            id=custom_id
        )
        
        assert element.id == custom_id

    def test_initialization_with_properties(self) -> None:
        """Test element initialization with properties."""
        properties = {"shape": "circle", "color": "blue"}
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test",
            properties=properties
        )
        
        assert element.properties == properties

    def test_initialization_with_style(self) -> None:
        """Test element initialization with style."""
        style = {"fill": "#ff0000", "stroke": "#000000"}
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test",
            style=style
        )
        
        assert element.style == style

    def test_initialization_empty_label(self) -> None:
        """Test initialization with empty label."""
        with pytest.raises(DiagramError, match="Element label cannot be empty"):
            DiagramElement(
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(50, 50),
                label=""
            )

    def test_move(self) -> None:
        """Test moving element."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(50, 50),
            label="Test"
        )
        
        element.move(Position(30, 40))
        
        assert element.position.x == 30
        assert element.position.y == 40

    def test_resize(self) -> None:
        """Test resizing element."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test"
        )
        
        element.resize(Size(100, 75))
        
        assert element.size.width == 100
        assert element.size.height == 75

    def test_update_properties(self) -> None:
        """Test updating element properties."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test"
        )
        
        element.update_properties({"shape": "circle"})
        assert element.properties["shape"] == "circle"
        
        element.update_properties({"color": "blue"})
        assert element.properties["shape"] == "circle"  # Should preserve existing
        assert element.properties["color"] == "blue"

    def test_update_style(self) -> None:
        """Test updating element style."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(50, 50),
            label="Test"
        )
        
        element.update_style({"fill": "#ff0000"})
        assert element.style["fill"] == "#ff0000"
        
        element.update_style({"stroke": "#000000"})
        assert element.style["fill"] == "#ff0000"  # Should preserve existing
        assert element.style["stroke"] == "#000000"

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test Node",
            properties={"shape": "circle"},
            style={"fill": "#ff0000"}
        )
        
        result = element.to_dict()
        
        assert result["id"] == element.id
        assert result["element_type"] == "node"
        assert result["position"] == {"x": 10, "y": 20}
        assert result["size"] == {"width": 100, "height": 50}
        assert result["label"] == "Test Node"
        assert result["properties"] == {"shape": "circle"}
        assert result["style"] == {"fill": "#ff0000"}

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {
            "id": "test_id",
            "element_type": "node",
            "position": {"x": 15, "y": 25},
            "size": {"width": 80, "height": 60},
            "label": "From Dict",
            "properties": {"shape": "rectangle"},
            "style": {"stroke": "#000000"}
        }
        
        element = DiagramElement.from_dict(data)
        
        assert element.id == "test_id"
        assert element.element_type == ElementType.NODE
        assert element.position.x == 15
        assert element.position.y == 25
        assert element.size.width == 80
        assert element.size.height == 60
        assert element.label == "From Dict"
        assert element.properties == {"shape": "rectangle"}
        assert element.style == {"stroke": "#000000"}

    def test_bounds(self) -> None:
        """Test element bounds calculation."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        
        bounds = element.bounds()
        
        assert bounds["left"] == 10
        assert bounds["top"] == 20
        assert bounds["right"] == 110
        assert bounds["bottom"] == 70

    def test_contains_point(self) -> None:
        """Test point containment check."""
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        
        # Point inside
        assert element.contains_point(Position(50, 40))
        
        # Point outside
        assert not element.contains_point(Position(5, 15))
        assert not element.contains_point(Position(150, 100))
        
        # Point on edge
        assert element.contains_point(Position(10, 20))  # Top-left corner
        assert element.contains_point(Position(110, 70))  # Bottom-right corner

    def test_overlaps_with(self) -> None:
        """Test overlap detection with another element."""
        element1 = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Element 1"
        )
        
        # Overlapping element
        element2 = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(50, 40),
            size=Size(100, 50),
            label="Element 2"
        )
        
        # Non-overlapping element
        element3 = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(200, 200),
            size=Size(50, 50),
            label="Element 3"
        )
        
        assert element1.overlaps_with(element2)
        assert not element1.overlaps_with(element3)

    def test_clone(self) -> None:
        """Test element cloning."""
        original = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Original",
            properties={"shape": "circle"},
            style={"fill": "#ff0000"}
        )
        
        clone = original.clone()
        
        assert clone.id != original.id  # Should have different ID
        assert clone.element_type == original.element_type
        assert clone.position.x == original.position.x
        assert clone.position.y == original.position.y
        assert clone.size.width == original.size.width
        assert clone.size.height == original.size.height
        assert clone.label == original.label
        assert clone.properties == original.properties
        assert clone.style == original.style
        assert clone is not original  # Should be different objects
