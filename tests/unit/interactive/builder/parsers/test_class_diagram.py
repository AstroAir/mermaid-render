"""
Unit tests for interactive.builder.parsers.class_diagram module.

Tests the ClassDiagramParser class.
"""

import pytest

from mermaid_render.interactive.builder.parsers.class_diagram import ClassDiagramParser


@pytest.mark.unit
class TestClassDiagramParser:
    """Unit tests for ClassDiagramParser class."""

    def test_initialization(self) -> None:
        """Test ClassDiagramParser initialization."""
        parser = ClassDiagramParser()
        assert parser is not None

    def test_parse_empty_diagram(self) -> None:
        """Test parsing empty class diagram."""
        parser = ClassDiagramParser()
        elements, connections = parser.parse("classDiagram")
        assert isinstance(elements, list)
        assert isinstance(connections, list)

    def test_parse_single_class(self) -> None:
        """Test parsing class diagram with single class."""
        parser = ClassDiagramParser()
        code = """classDiagram
            class User"""
        elements, connections = parser.parse(code)
        assert len(elements) >= 1

    def test_parse_class_with_members(self) -> None:
        """Test parsing class with members."""
        parser = ClassDiagramParser()
        code = """classDiagram
            class User {
                +String name
                +login()
            }"""
        elements, connections = parser.parse(code)
        assert len(elements) >= 1

    def test_parse_inheritance(self) -> None:
        """Test parsing class inheritance."""
        parser = ClassDiagramParser()
        code = """classDiagram
            Animal <|-- Dog"""
        elements, connections = parser.parse(code)
        assert len(connections) >= 1

    def test_parse_association(self) -> None:
        """Test parsing class association."""
        parser = ClassDiagramParser()
        code = """classDiagram
            Order --> Product"""
        elements, connections = parser.parse(code)
        assert len(connections) >= 1

    def test_parse_composition(self) -> None:
        """Test parsing class composition."""
        parser = ClassDiagramParser()
        code = """classDiagram
            Car *-- Engine"""
        elements, connections = parser.parse(code)
        assert len(connections) >= 1

    def test_parse_aggregation(self) -> None:
        """Test parsing class aggregation."""
        parser = ClassDiagramParser()
        code = """classDiagram
            Library o-- Book"""
        elements, connections = parser.parse(code)
        assert len(connections) >= 1
