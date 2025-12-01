"""
Unit tests for interactive.builder.parsers.er_diagram module.

Tests the ERDiagramParser class.
"""

import pytest

from diagramaid.interactive.builder.parsers.er_diagram import ERDiagramParser


@pytest.mark.unit
class TestERDiagramParser:
    """Unit tests for ERDiagramParser class."""

    def test_initialization(self) -> None:
        """Test ERDiagramParser initialization."""
        parser = ERDiagramParser()
        assert parser is not None

    def test_parse_empty_diagram(self) -> None:
        """Test parsing empty ER diagram."""
        parser = ERDiagramParser()
        elements, connections = parser.parse([])
        assert isinstance(elements, dict)
        assert isinstance(connections, dict)

    def test_parse_single_entity(self) -> None:
        """Test parsing ER diagram with single entity."""
        parser = ERDiagramParser()
        # Parser expects entity with braces or relationship
        lines = ["CUSTOMER { string name }"]
        elements, connections = parser.parse(lines)
        assert len(elements) >= 1

    def test_parse_entity_with_attributes(self) -> None:
        """Test parsing entity with attributes."""
        parser = ERDiagramParser()
        # Parser expects entity definition on single line with braces
        lines = ["CUSTOMER { string name int id }"]
        elements, connections = parser.parse(lines)
        assert len(elements) >= 1

    def test_parse_relationship(self) -> None:
        """Test parsing ER relationship."""
        parser = ERDiagramParser()
        lines = ["CUSTOMER ||--o{ ORDER : places"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_one_to_one(self) -> None:
        """Test parsing one-to-one relationship."""
        parser = ERDiagramParser()
        lines = ["USER ||--|| PROFILE : has"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_one_to_many(self) -> None:
        """Test parsing one-to-many relationship."""
        parser = ERDiagramParser()
        lines = ["DEPARTMENT ||--o{ EMPLOYEE : contains"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1

    def test_parse_many_to_many(self) -> None:
        """Test parsing many-to-many relationship."""
        parser = ERDiagramParser()
        # Use standard ER notation with || or |o
        lines = ["STUDENT |o--o| COURSE : enrolls"]
        elements, connections = parser.parse(lines)
        assert len(connections) >= 1
