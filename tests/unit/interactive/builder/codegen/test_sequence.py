"""
Unit tests for interactive.builder.codegen.sequence module.

Tests the SequenceDiagramGenerator class.
"""

import pytest

from diagramaid.interactive.builder.codegen.sequence import SequenceDiagramGenerator
from diagramaid.interactive.models import (
    DiagramConnection,
    DiagramElement,
    ElementType,
    Position,
    Size,
)


@pytest.mark.unit
class TestSequenceDiagramGenerator:
    """Unit tests for SequenceDiagramGenerator class."""

    def test_initialization(self) -> None:
        """Test SequenceDiagramGenerator initialization."""
        generator = SequenceDiagramGenerator()
        assert generator is not None

    def test_generate_empty_diagram(self) -> None:
        """Test generating empty sequence diagram."""
        generator = SequenceDiagramGenerator()
        result = generator.generate({}, {}, {})
        assert "sequenceDiagram" in result

    def test_generate_with_participants(self) -> None:
        """Test generating sequence diagram with participants."""
        generator = SequenceDiagramGenerator()
        elem1 = DiagramElement(
            id="p1",
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(100, 50),
            label="Alice",
            properties={"type": "participant"},
        )
        elem2 = DiagramElement(
            id="p2",
            element_type=ElementType.NODE,
            position=Position(200, 0),
            size=Size(100, 50),
            label="Bob",
            properties={"type": "participant"},
        )
        elements = {elem1.id: elem1, elem2.id: elem2}
        result = generator.generate(elements, {}, {})
        assert "p1" in result or "Alice" in result
        assert "p2" in result or "Bob" in result

    def test_generate_with_message(self) -> None:
        """Test generating sequence diagram with message."""
        generator = SequenceDiagramGenerator()
        elem1 = DiagramElement(
            id="p1",
            element_type=ElementType.NODE,
            position=Position(0, 0),
            size=Size(100, 50),
            label="Client",
            properties={"type": "participant"},
        )
        elem2 = DiagramElement(
            id="p2",
            element_type=ElementType.NODE,
            position=Position(200, 0),
            size=Size(100, 50),
            label="Server",
            properties={"type": "participant"},
        )
        elements = {elem1.id: elem1, elem2.id: elem2}
        conn = DiagramConnection(id="c1", source_id="p1", target_id="p2", label="Request")
        connections = {conn.id: conn}
        result = generator.generate(elements, connections, {})
        assert "->>" in result or "->" in result
