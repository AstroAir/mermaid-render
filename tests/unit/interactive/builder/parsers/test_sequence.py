"""
Unit tests for interactive.builder.parsers.sequence module.

Tests the SequenceDiagramParser class.
"""

import pytest

from diagramaid.interactive.builder.parsers.sequence import SequenceDiagramParser


@pytest.mark.unit
class TestSequenceDiagramParser:
    """Unit tests for SequenceDiagramParser class."""

    def test_initialization(self) -> None:
        """Test SequenceDiagramParser initialization."""
        parser = SequenceDiagramParser()
        assert parser is not None

    def test_parse_empty_diagram(self) -> None:
        """Test parsing empty sequence diagram."""
        parser = SequenceDiagramParser()
        elements, connections = parser.parse([])
        assert isinstance(elements, dict)
        assert isinstance(connections, dict)

    def test_parse_with_participants(self) -> None:
        """Test parsing sequence diagram with participants."""
        parser = SequenceDiagramParser()
        lines = ["participant Alice", "participant Bob"]
        elements, connections = parser.parse(lines)
        assert len(elements) >= 2

    def test_parse_with_message(self) -> None:
        """Test parsing sequence diagram with message."""
        parser = SequenceDiagramParser()
        lines = ["Alice->>Bob: Hello"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_with_reply(self) -> None:
        """Test parsing sequence diagram with reply."""
        parser = SequenceDiagramParser()
        lines = ["Alice->>Bob: Request", "Bob-->>Alice: Response"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 2

    def test_parse_with_note(self) -> None:
        """Test parsing sequence diagram with note."""
        parser = SequenceDiagramParser()
        lines = ["Alice->>Bob: Hello", "Note over Alice,Bob: This is a note"]
        elements, connections = parser.parse(lines)
        assert len(elements) >= 2

    def test_parse_with_activation(self) -> None:
        """Test parsing sequence diagram with activation."""
        parser = SequenceDiagramParser()
        lines = ["Alice->>+Bob: Request", "Bob-->>-Alice: Response"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 2
