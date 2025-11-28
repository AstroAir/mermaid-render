"""
Unit tests for interactive.builder.parsers.state_diagram module.

Tests the StateDiagramParser class.
"""

import pytest

from mermaid_render.interactive.builder.parsers.state_diagram import StateDiagramParser


@pytest.mark.unit
class TestStateDiagramParser:
    """Unit tests for StateDiagramParser class."""

    def test_initialization(self) -> None:
        """Test StateDiagramParser initialization."""
        parser = StateDiagramParser()
        assert parser is not None

    def test_parse_empty_diagram(self) -> None:
        """Test parsing empty state diagram."""
        parser = StateDiagramParser()
        elements, connections = parser.parse([])
        assert isinstance(elements, dict)
        assert isinstance(connections, dict)

    def test_parse_single_state(self) -> None:
        """Test parsing state diagram with single state."""
        parser = StateDiagramParser()
        # Parser only creates states from transitions
        lines = ["[*] --> Idle"]
        elements, connections = parser.parse(lines)
        assert len(elements) >= 1

    def test_parse_transition(self) -> None:
        """Test parsing state transition."""
        parser = StateDiagramParser()
        lines = ["Idle --> Running"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_labeled_transition(self) -> None:
        """Test parsing labeled state transition."""
        parser = StateDiagramParser()
        lines = ["Idle --> Running : start"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_start_state(self) -> None:
        """Test parsing start state."""
        parser = StateDiagramParser()
        lines = ["[*] --> Idle"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_end_state(self) -> None:
        """Test parsing end state."""
        parser = StateDiagramParser()
        lines = ["Running --> [*]"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_composite_state(self) -> None:
        """Test parsing composite state."""
        parser = StateDiagramParser()
        lines = ["state Active {", "[*] --> Running", "Running --> Paused", "}"]
        elements, connections = parser.parse(lines)
        assert len(elements) >= 1
