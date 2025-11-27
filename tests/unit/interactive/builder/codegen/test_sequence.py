"""
Unit tests for interactive.builder.codegen.sequence module.

Tests the SequenceDiagramGenerator class.
"""

import pytest

from mermaid_render.interactive.builder.codegen.sequence import SequenceDiagramGenerator
from mermaid_render.interactive.models import (
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
        result = generator.generate([], [])
        assert "sequenceDiagram" in result

    def test_generate_with_participants(self) -> None:
        """Test generating sequence diagram with participants."""
        generator = SequenceDiagramGenerator()
        elements = [
            DiagramElement(
                id="p1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(100, 50),
                label="Alice"
            ),
            DiagramElement(
                id="p2",
                element_type=ElementType.NODE,
                position=Position(200, 0),
                size=Size(100, 50),
                label="Bob"
            )
        ]
        result = generator.generate(elements, [])
        assert "Alice" in result
        assert "Bob" in result

    def test_generate_with_message(self) -> None:
        """Test generating sequence diagram with message."""
        generator = SequenceDiagramGenerator()
        elements = [
            DiagramElement(
                id="p1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(100, 50),
                label="Client"
            ),
            DiagramElement(
                id="p2",
                element_type=ElementType.NODE,
                position=Position(200, 0),
                size=Size(100, 50),
                label="Server"
            )
        ]
        connections = [
            DiagramConnection(source_id="p1", target_id="p2", label="Request")
        ]
        result = generator.generate(elements, connections)
        assert "->>" in result or "->>" in result or "->" in result
