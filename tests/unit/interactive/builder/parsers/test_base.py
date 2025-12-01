"""
Unit tests for interactive.builder.parsers.base module.

Tests the DiagramParser base class.
"""

import pytest

from diagramaid.interactive.builder.parsers.base import DiagramParser


@pytest.mark.unit
class TestDiagramParser:
    """Unit tests for DiagramParser base class."""

    def test_is_abstract(self) -> None:
        """Test that DiagramParser is abstract."""
        with pytest.raises(TypeError):
            DiagramParser()

    def test_subclass_must_implement_parse(self) -> None:
        """Test that subclasses must implement parse method."""

        class IncompleteParser(DiagramParser):
            pass

        with pytest.raises(TypeError):
            IncompleteParser()

    def test_subclass_with_parse(self) -> None:
        """Test that subclass with parse method can be instantiated."""

        class ConcreteParser(DiagramParser):
            def parse(self, code):
                return [], []

        parser = ConcreteParser()
        assert parser is not None

    def test_parse_returns_tuple(self) -> None:
        """Test that parse returns elements and connections."""

        class ConcreteParser(DiagramParser):
            def parse(self, code):
                return [], []

        parser = ConcreteParser()
        elements, connections = parser.parse("graph TD")
        assert isinstance(elements, list)
        assert isinstance(connections, list)
