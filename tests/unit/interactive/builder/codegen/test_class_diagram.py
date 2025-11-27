"""
Unit tests for interactive.builder.codegen.class_diagram module.

Tests the ClassDiagramGenerator class.
"""

import pytest

from mermaid_render.interactive.builder.codegen.class_diagram import ClassDiagramGenerator
from mermaid_render.interactive.models import (
    DiagramConnection,
    DiagramElement,
    ElementType,
    Position,
    Size,
)


@pytest.mark.unit
class TestClassDiagramGenerator:
    """Unit tests for ClassDiagramGenerator class."""

    def test_initialization(self) -> None:
        """Test ClassDiagramGenerator initialization."""
        generator = ClassDiagramGenerator()
        assert generator is not None

    def test_generate_empty_diagram(self) -> None:
        """Test generating empty class diagram."""
        generator = ClassDiagramGenerator()
        result = generator.generate([], [])
        assert "classDiagram" in result

    def test_generate_with_class(self) -> None:
        """Test generating class diagram with class."""
        generator = ClassDiagramGenerator()
        elements = [
            DiagramElement(
                id="c1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(150, 100),
                label="User",
                properties={"methods": ["login()", "logout()"], "attributes": ["name", "email"]}
            )
        ]
        result = generator.generate(elements, [])
        assert "User" in result

    def test_generate_with_inheritance(self) -> None:
        """Test generating class diagram with inheritance."""
        generator = ClassDiagramGenerator()
        elements = [
            DiagramElement(
                id="c1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(150, 100),
                label="Animal"
            ),
            DiagramElement(
                id="c2",
                element_type=ElementType.NODE,
                position=Position(0, 200),
                size=Size(150, 100),
                label="Dog"
            )
        ]
        connections = [
            DiagramConnection(
                source_id="c2",
                target_id="c1",
                properties={"type": "inheritance"}
            )
        ]
        result = generator.generate(elements, connections)
        assert "Animal" in result
        assert "Dog" in result

    def test_generate_with_association(self) -> None:
        """Test generating class diagram with association."""
        generator = ClassDiagramGenerator()
        elements = [
            DiagramElement(
                id="c1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(150, 100),
                label="Order"
            ),
            DiagramElement(
                id="c2",
                element_type=ElementType.NODE,
                position=Position(200, 0),
                size=Size(150, 100),
                label="Product"
            )
        ]
        connections = [
            DiagramConnection(
                source_id="c1",
                target_id="c2",
                label="contains"
            )
        ]
        result = generator.generate(elements, connections)
        assert "Order" in result
        assert "Product" in result
