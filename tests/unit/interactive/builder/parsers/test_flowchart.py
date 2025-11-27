"""
Unit tests for interactive.builder.parsers.flowchart module.

Tests the FlowchartParser class.
"""

import pytest

from mermaid_render.interactive.builder.parsers.flowchart import FlowchartParser


@pytest.mark.unit
class TestFlowchartParser:
    """Unit tests for FlowchartParser class."""

    def test_initialization(self) -> None:
        """Test FlowchartParser initialization."""
        parser = FlowchartParser()
        assert parser is not None

    def test_parse_empty_diagram(self) -> None:
        """Test parsing empty flowchart."""
        parser = FlowchartParser()
        elements, connections = parser.parse("flowchart TD")
        assert isinstance(elements, list)
        assert isinstance(connections, list)

    def test_parse_single_node(self) -> None:
        """Test parsing flowchart with single node."""
        parser = FlowchartParser()
        code = """flowchart TD
            A[Start]"""
        elements, connections = parser.parse(code)
        assert len(elements) >= 1

    def test_parse_with_connection(self) -> None:
        """Test parsing flowchart with connection."""
        parser = FlowchartParser()
        code = """flowchart TD
            A[Start] --> B[End]"""
        elements, connections = parser.parse(code)
        assert len(elements) >= 2
        assert len(connections) >= 1

    def test_parse_with_labeled_connection(self) -> None:
        """Test parsing flowchart with labeled connection."""
        parser = FlowchartParser()
        code = """flowchart TD
            A[Start] -->|next| B[End]"""
        elements, connections = parser.parse(code)
        assert len(connections) >= 1

    def test_parse_graph_syntax(self) -> None:
        """Test parsing graph syntax (alternative to flowchart)."""
        parser = FlowchartParser()
        code = """graph LR
            A --> B"""
        elements, connections = parser.parse(code)
        assert len(elements) >= 2

    def test_parse_different_node_shapes(self) -> None:
        """Test parsing different node shapes."""
        parser = FlowchartParser()
        code = """flowchart TD
            A[Rectangle]
            B(Rounded)
            C{Diamond}
            D([Stadium])"""
        elements, connections = parser.parse(code)
        assert len(elements) >= 4

    def test_parse_subgraph(self) -> None:
        """Test parsing flowchart with subgraph."""
        parser = FlowchartParser()
        code = """flowchart TD
            subgraph Group
                A --> B
            end"""
        elements, connections = parser.parse(code)
        assert len(elements) >= 2
