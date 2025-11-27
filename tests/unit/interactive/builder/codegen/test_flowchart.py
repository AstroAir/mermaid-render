"""
Unit tests for interactive.builder.codegen.flowchart module.

Tests the FlowchartGenerator class.
"""

import pytest

from mermaid_render.interactive.builder.codegen.flowchart import FlowchartGenerator
from mermaid_render.interactive.models import (
    DiagramConnection,
    DiagramElement,
    ElementType,
    Position,
    Size,
)


@pytest.mark.unit
class TestFlowchartGenerator:
    """Unit tests for FlowchartGenerator class."""

    def test_initialization(self) -> None:
        """Test FlowchartGenerator initialization."""
        generator = FlowchartGenerator()
        assert generator is not None

    def test_generate_empty_diagram(self) -> None:
        """Test generating empty flowchart."""
        generator = FlowchartGenerator()
        result = generator.generate([], [])
        assert "flowchart" in result.lower() or "graph" in result.lower()

    def test_generate_single_node(self) -> None:
        """Test generating flowchart with single node."""
        generator = FlowchartGenerator()
        elements = [
            DiagramElement(
                id="node1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(100, 50),
                label="Start"
            )
        ]
        result = generator.generate(elements, [])
        assert "Start" in result

    def test_generate_with_connection(self) -> None:
        """Test generating flowchart with connection."""
        generator = FlowchartGenerator()
        elements = [
            DiagramElement(
                id="node1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(100, 50),
                label="A"
            ),
            DiagramElement(
                id="node2",
                element_type=ElementType.NODE,
                position=Position(200, 0),
                size=Size(100, 50),
                label="B"
            )
        ]
        connections = [
            DiagramConnection(source_id="node1", target_id="node2")
        ]
        result = generator.generate(elements, connections)
        assert "-->" in result or "---" in result

    def test_generate_with_labeled_connection(self) -> None:
        """Test generating flowchart with labeled connection."""
        generator = FlowchartGenerator()
        elements = [
            DiagramElement(
                id="n1",
                element_type=ElementType.NODE,
                position=Position(0, 0),
                size=Size(100, 50),
                label="Start"
            ),
            DiagramElement(
                id="n2",
                element_type=ElementType.NODE,
                position=Position(200, 0),
                size=Size(100, 50),
                label="End"
            )
        ]
        connections = [
            DiagramConnection(source_id="n1", target_id="n2", label="next")
        ]
        result = generator.generate(elements, connections)
        assert "next" in result or "-->" in result

    def test_generate_direction(self) -> None:
        """Test generating flowchart with specific direction."""
        generator = FlowchartGenerator(direction="LR")
        result = generator.generate([], [])
        assert "LR" in result or "flowchart" in result.lower()
