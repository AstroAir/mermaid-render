"""
Unit tests for interactive.builder.element_manager module.

Tests the ElementManager class for managing diagram elements.
"""

import pytest

from mermaid_render.interactive.builder.element_manager import ElementManager
from mermaid_render.interactive.models import ElementType, Position, Size


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
        element = manager.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(10, 20),
            size=Size(100, 50),
        )
        assert len(manager.elements) == 1
        assert manager.get_element(element.id) == element

    def test_remove_element(self) -> None:
        """Test removing element."""
        manager = ElementManager()
        element = manager.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(10, 20),
            size=Size(100, 50),
        )
        manager.remove_element(element.id)
        assert len(manager.elements) == 0

    def test_get_element_not_found(self) -> None:
        """Test getting non-existent element."""
        manager = ElementManager()
        result = manager.get_element("nonexistent")
        assert result is None

    def test_update_element(self) -> None:
        """Test updating element."""
        manager = ElementManager()
        element = manager.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(10, 20),
            size=Size(100, 50),
        )
        manager.update_element(element.id, position=Position(30, 40))
        updated = manager.get_element(element.id)
        assert updated is not None
        assert updated.position.x == 30
        assert updated.position.y == 40

    def test_get_all_elements(self) -> None:
        """Test getting all elements."""
        manager = ElementManager()
        manager.add_element(
            element_type=ElementType.NODE,
            label="Node",
            position=Position(10, 20),
        )
        manager.add_element(
            element_type=ElementType.CONTAINER,
            label="Container",
            position=Position(100, 100),
        )
        all_elements = manager.get_all_elements()
        assert len(all_elements) == 2

    def test_clear(self) -> None:
        """Test clearing all elements."""
        manager = ElementManager()
        manager.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(10, 20),
        )
        manager.clear()
        assert len(manager.elements) == 0

    def test_has_element(self) -> None:
        """Test checking if element exists."""
        manager = ElementManager()
        element = manager.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(10, 20),
        )
        assert manager.has_element(element.id)
        assert not manager.has_element("nonexistent")

    def test_default_size(self) -> None:
        """Test default size for element types."""
        manager = ElementManager()
        node_size = manager.get_default_size(ElementType.NODE)
        assert node_size.width == 120
        assert node_size.height == 60
