"""
Unit tests for interactive.builder.element_manager module.

Tests the ElementManager class for managing diagram elements.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.builder.element_manager import ElementManager
from mermaid_render.interactive.models import (
    DiagramElement,
    ElementType,
    Position,
    Size,
)


@pytest.mark.unit
class TestElementManager:
    """Unit tests for ElementManager class."""

    def test_initialization(self) -> None:
        """Test ElementManager initialization."""
        manager = ElementManager()
        
        assert len(manager.elements) == 0

    def test_add_element(self) -> None:
        """Test adding element."""
        manager = ElementManager()
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        
        manager.add(element)
        
        assert len(manager.elements) == 1
        assert manager.get(element.id) == element

    def test_remove_element(self) -> None:
        """Test removing element."""
        manager = ElementManager()
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        
        manager.add(element)
        manager.remove(element.id)
        
        assert len(manager.elements) == 0

    def test_get_element_not_found(self) -> None:
        """Test getting non-existent element."""
        manager = ElementManager()
        
        result = manager.get("nonexistent")
        
        assert result is None

    def test_update_element(self) -> None:
        """Test updating element."""
        manager = ElementManager()
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        
        manager.add(element)
        manager.update(element.id, position=Position(30, 40))
        
        updated = manager.get(element.id)
        assert updated.position.x == 30
        assert updated.position.y == 40

    def test_get_elements_by_type(self) -> None:
        """Test getting elements by type."""
        manager = ElementManager()
        
        node = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Node"
        )
        container = DiagramElement(
            element_type=ElementType.CONTAINER,
            position=Position(100, 100),
            size=Size(200, 200),
            label="Container"
        )
        
        manager.add(node)
        manager.add(container)
        
        nodes = manager.get_by_type(ElementType.NODE)
        
        assert len(nodes) == 1
        assert nodes[0].label == "Node"

    def test_clear(self) -> None:
        """Test clearing all elements."""
        manager = ElementManager()
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        
        manager.add(element)
        manager.clear()
        
        assert len(manager.elements) == 0

    def test_find_at_position(self) -> None:
        """Test finding element at position."""
        manager = ElementManager()
        element = DiagramElement(
            element_type=ElementType.NODE,
            position=Position(10, 20),
            size=Size(100, 50),
            label="Test"
        )
        
        manager.add(element)
        
        # Point inside element
        found = manager.find_at_position(Position(50, 40))
        assert found == element
        
        # Point outside element
        not_found = manager.find_at_position(Position(200, 200))
        assert not_found is None
