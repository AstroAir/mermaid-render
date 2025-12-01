"""
Element management for the interactive diagram builder.

This module provides element CRUD operations and default size handling.
"""

import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from ..models import DiagramElement, ElementType, Position, Size


class ElementManager:
    """
    Manages diagram elements with CRUD operations.

    Handles element creation, updates, removal, and provides
    default sizing based on element types.
    """

    # Default sizes for different element types
    DEFAULT_SIZES: dict[ElementType, Size] = {
        ElementType.NODE: Size(120, 60),
        ElementType.CONTAINER: Size(200, 150),
        ElementType.ANNOTATION: Size(100, 40),
    }

    def __init__(self) -> None:
        """Initialize element manager."""
        self.elements: dict[str, DiagramElement] = {}

        # Event handlers
        self._element_added_handlers: list[Callable[[DiagramElement], None]] = []
        self._element_updated_handlers: list[Callable[[DiagramElement], None]] = []
        self._element_removed_handlers: list[Callable[[DiagramElement], None]] = []

    def add_element(
        self,
        element_type: ElementType,
        label: str,
        position: Position,
        size: Size | None = None,
        properties: dict[str, Any] | None = None,
        style: dict[str, Any] | None = None,
        element_id: str | None = None,
    ) -> DiagramElement:
        """
        Add a new element to the diagram.

        Args:
            element_type: Type of element to add
            label: Element label
            position: Element position
            size: Element size (default based on type)
            properties: Element properties
            style: Element styling
            element_id: Optional custom element ID

        Returns:
            Created diagram element
        """
        if size is None:
            size = self.get_default_size(element_type)

        element = DiagramElement(
            id=element_id or str(uuid.uuid4()),
            element_type=element_type,
            label=label,
            position=position,
            size=size,
            properties=properties or {},
            style=style or {},
        )

        self.elements[element.id] = element

        # Notify handlers
        for handler in self._element_added_handlers:
            handler(element)

        return element

    def update_element(
        self,
        element_id: str,
        label: str | None = None,
        position: Position | None = None,
        size: Size | None = None,
        properties: dict[str, Any] | None = None,
        style: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update an existing element.

        Args:
            element_id: ID of element to update
            label: New label
            position: New position
            size: New size
            properties: New properties
            style: New styling

        Returns:
            True if element was updated
        """
        if element_id not in self.elements:
            return False

        element = self.elements[element_id]

        if label is not None:
            element.label = label
        if position is not None:
            element.position = position
        if size is not None:
            element.size = size
        if properties is not None:
            element.update_properties(properties)
        if style is not None:
            element.update_style(style)

        element.updated_at = datetime.now()

        # Notify handlers
        for handler in self._element_updated_handlers:
            handler(element)

        return True

    def remove_element(self, element_id: str) -> DiagramElement | None:
        """
        Remove an element from the diagram.

        Args:
            element_id: ID of element to remove

        Returns:
            Removed element or None if not found
        """
        if element_id not in self.elements:
            return None

        element = self.elements.pop(element_id)

        # Notify handlers
        for handler in self._element_removed_handlers:
            handler(element)

        return element

    def get_element(self, element_id: str) -> DiagramElement | None:
        """Get element by ID."""
        return self.elements.get(element_id)

    def get_all_elements(self) -> list[DiagramElement]:
        """Get all elements."""
        return list(self.elements.values())

    def has_element(self, element_id: str) -> bool:
        """Check if element exists."""
        return element_id in self.elements

    def clear(self) -> None:
        """Remove all elements."""
        self.elements.clear()

    def get_default_size(self, element_type: ElementType) -> Size:
        """Get default size for element type."""
        return self.DEFAULT_SIZES.get(element_type, Size(100, 50))

    # Event handler registration
    def on_element_added(
        self, handler: Callable[[DiagramElement], None]
    ) -> None:
        """Register handler for element added events."""
        self._element_added_handlers.append(handler)

    def on_element_updated(
        self, handler: Callable[[DiagramElement], None]
    ) -> None:
        """Register handler for element updated events."""
        self._element_updated_handlers.append(handler)

    def on_element_removed(
        self, handler: Callable[[DiagramElement], None]
    ) -> None:
        """Register handler for element removed events."""
        self._element_removed_handlers.append(handler)
