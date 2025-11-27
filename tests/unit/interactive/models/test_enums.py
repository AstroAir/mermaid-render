"""
Unit tests for interactive.models.enums module.

Tests the ElementType and DiagramType enums.
"""

import pytest

from mermaid_render.interactive.models.enums import DiagramType, ElementType


@pytest.mark.unit
class TestElementType:
    """Unit tests for ElementType enum."""

    def test_node_value(self) -> None:
        """Test NODE enum value."""
        assert ElementType.NODE.value == "node"

    def test_edge_value(self) -> None:
        """Test EDGE enum value."""
        assert ElementType.EDGE.value == "edge"

    def test_container_value(self) -> None:
        """Test CONTAINER enum value."""
        assert ElementType.CONTAINER.value == "container"

    def test_annotation_value(self) -> None:
        """Test ANNOTATION enum value."""
        assert ElementType.ANNOTATION.value == "annotation"

    def test_from_string(self) -> None:
        """Test creating enum from string."""
        assert ElementType("node") == ElementType.NODE
        assert ElementType("edge") == ElementType.EDGE


@pytest.mark.unit
class TestDiagramType:
    """Unit tests for DiagramType enum."""

    def test_flowchart_value(self) -> None:
        """Test FLOWCHART enum value."""
        assert DiagramType.FLOWCHART.value == "flowchart"

    def test_sequence_value(self) -> None:
        """Test SEQUENCE enum value."""
        assert DiagramType.SEQUENCE.value == "sequence"

    def test_class_value(self) -> None:
        """Test CLASS enum value."""
        assert DiagramType.CLASS.value == "class"

    def test_state_value(self) -> None:
        """Test STATE enum value."""
        assert DiagramType.STATE.value == "state"

    def test_er_value(self) -> None:
        """Test ER enum value."""
        assert DiagramType.ER.value == "er"

    def test_from_string(self) -> None:
        """Test creating enum from string."""
        assert DiagramType("flowchart") == DiagramType.FLOWCHART
        assert DiagramType("sequence") == DiagramType.SEQUENCE
