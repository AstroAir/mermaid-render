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
        result = generator.generate({}, {}, {})
        assert "classDiagram" in result

    def test_generate_with_class(self) -> None:
        """Test generating class diagram with class."""
        generator = ClassDiagramGenerator()
        elem = DiagramElement(
            id="c1",
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(150, 100),
            label="User",
            properties={
                "type": "class",
                "methods": ["login()", "logout()"],
                "attributes": ["name", "email"],
            },
        )
        elements = {elem.id: elem}
        result = generator.generate(elements, {}, {})
        assert "c1" in result or "User" in result

    def test_generate_with_inheritance(self) -> None:
        """Test generating class diagram with inheritance."""
        generator = ClassDiagramGenerator()
        elem1 = DiagramElement(
            id="c1",
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(150, 100),
            label="Animal",
            properties={"type": "class"},
        )
        elem2 = DiagramElement(
            id="c2",
            element_type=ElementType.NODE,
            position=Position(0, 200),
            size=Size(150, 100),
            label="Dog",
            properties={"type": "class"},
        )
        elements = {elem1.id: elem1, elem2.id: elem2}
        conn = DiagramConnection(
            id="conn1",
            source_id="c2",
            target_id="c1",
            connection_type="inheritance",
        )
        connections = {conn.id: conn}
        result = generator.generate(elements, connections, {})
        assert "c1" in result or "Animal" in result
        assert "c2" in result or "Dog" in result

    def test_generate_with_association(self) -> None:
        """Test generating class diagram with association."""
        generator = ClassDiagramGenerator()
        elem1 = DiagramElement(
            id="c1",
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(150, 100),
            label="Order",
            properties={"type": "class"},
        )
        elem2 = DiagramElement(
            id="c2",
            element_type=ElementType.NODE,
            position=Position(200, 0),
            size=Size(150, 100),
            label="Product",
            properties={"type": "class"},
        )
        elements = {elem1.id: elem1, elem2.id: elem2}
        conn = DiagramConnection(
            id="conn1",
            source_id="c1",
            target_id="c2",
            label="contains",
        )
        connections = {conn.id: conn}
        result = generator.generate(elements, connections, {})
        assert "c1" in result or "Order" in result
        assert "c2" in result or "Product" in result
