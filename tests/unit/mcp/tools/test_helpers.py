"""
Unit tests for mcp.tools.helpers module.

Tests for helper functions used across tools.
"""

import pytest

from diagramaid.mcp.tools.helpers import (
    _calculate_complexity_score,
    _calculate_quality_score,
    _detect_diagram_type,
    _extract_edges,
    _extract_nodes,
    _get_config_description,
    _get_diagram_example,
)


@pytest.mark.unit
class TestDetectDiagramType:
    """Tests for _detect_diagram_type function."""

    def test_detect_flowchart_td(self):
        """Test detection of flowchart TD."""
        code = "flowchart TD\n    A --> B"
        assert _detect_diagram_type(code) == "flowchart"

    def test_detect_flowchart_lr(self):
        """Test detection of flowchart LR."""
        code = "flowchart LR\n    A --> B"
        assert _detect_diagram_type(code) == "flowchart"

    def test_detect_graph(self):
        """Test detection of graph (alias for flowchart)."""
        code = "graph TD\n    A --> B"
        result = _detect_diagram_type(code)
        assert result in ["flowchart", "graph"]

    def test_detect_sequence_diagram(self):
        """Test detection of sequence diagram."""
        code = "sequenceDiagram\n    A->>B: Hello"
        assert _detect_diagram_type(code) == "sequence"

    def test_detect_class_diagram(self):
        """Test detection of class diagram."""
        code = "classDiagram\n    class Animal"
        assert _detect_diagram_type(code) == "class"

    def test_detect_state_diagram(self):
        """Test detection of state diagram."""
        code = "stateDiagram-v2\n    [*] --> Idle"
        assert _detect_diagram_type(code) == "state"

    def test_detect_er_diagram(self):
        """Test detection of ER diagram."""
        code = "erDiagram\n    CUSTOMER ||--o{ ORDER : places"
        assert _detect_diagram_type(code) == "er"

    def test_detect_gantt(self):
        """Test detection of Gantt chart."""
        code = "gantt\n    title Project\n    Task : a1, 2024-01-01, 1d"
        assert _detect_diagram_type(code) == "gantt"

    def test_detect_pie(self):
        """Test detection of pie chart."""
        code = 'pie\n    "A" : 50'
        assert _detect_diagram_type(code) == "pie"

    def test_detect_mindmap(self):
        """Test detection of mindmap."""
        code = "mindmap\n    root((Topic))"
        assert _detect_diagram_type(code) == "mindmap"

    def test_detect_timeline(self):
        """Test detection of timeline."""
        code = "timeline\n    2024 : Event"
        assert _detect_diagram_type(code) == "timeline"

    def test_detect_gitgraph(self):
        """Test detection of gitgraph."""
        code = "gitgraph\n    commit"
        result = _detect_diagram_type(code)
        assert result in ["gitgraph", "git_graph"]

    def test_detect_unknown(self):
        """Test detection returns None for unknown type."""
        code = "unknown diagram type"
        result = _detect_diagram_type(code)
        assert result is None or result == "unknown"

    def test_detect_empty_code(self):
        """Test detection handles empty code."""
        result = _detect_diagram_type("")
        assert result is None or result == "unknown"


@pytest.mark.unit
class TestExtractNodes:
    """Tests for _extract_nodes function."""

    def test_extract_simple_nodes(self):
        """Test extraction of simple nodes."""
        code = "flowchart TD\n    A[Start] --> B[End]"
        nodes = _extract_nodes(code)
        assert len(nodes) >= 2

    def test_extract_nodes_with_labels(self):
        """Test extraction preserves node labels."""
        code = "flowchart TD\n    A[Start Node] --> B[End Node]"
        nodes = _extract_nodes(code)
        # Should find nodes with their labels
        node_ids = [n.get("id") for n in nodes]
        assert "A" in node_ids or any("Start" in str(n) for n in nodes)

    def test_extract_nodes_empty_code(self):
        """Test extraction handles empty code."""
        nodes = _extract_nodes("")
        assert isinstance(nodes, list)


@pytest.mark.unit
class TestExtractEdges:
    """Tests for _extract_edges function."""

    def test_extract_simple_edges(self):
        """Test extraction of simple edges."""
        code = "flowchart TD\n    A --> B"
        edges = _extract_edges(code)
        assert len(edges) >= 1

    def test_extract_multiple_edges(self):
        """Test extraction of multiple edges."""
        code = "flowchart TD\n    A --> B\n    B --> C\n    C --> D"
        edges = _extract_edges(code)
        assert len(edges) >= 3

    def test_extract_edges_empty_code(self):
        """Test extraction handles empty code."""
        edges = _extract_edges("")
        assert isinstance(edges, list)


@pytest.mark.unit
class TestCalculateComplexityScore:
    """Tests for _calculate_complexity_score function."""

    def test_simple_diagram_low_complexity(self):
        """Test simple diagram has low complexity."""
        code = "flowchart TD\n    A --> B"
        score = _calculate_complexity_score(code)
        assert isinstance(score, (int, float))
        assert score >= 0

    def test_complex_diagram_higher_complexity(self):
        """Test complex diagram has higher complexity."""
        simple_code = "flowchart TD\n    A --> B"
        complex_code = """flowchart TD
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    subgraph sub1
        G --> H
        H --> I
    end
    F --> G
"""
        simple_score = _calculate_complexity_score(simple_code)
        complex_score = _calculate_complexity_score(complex_code)
        assert complex_score >= simple_score


@pytest.mark.unit
class TestCalculateQualityScore:
    """Tests for _calculate_quality_score function."""

    def test_quality_score_returns_number(self):
        """Test quality score returns a number."""
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_result.errors = []
        mock_result.warnings = []

        code = "flowchart TD\n    A --> B"
        score = _calculate_quality_score(mock_result, code)
        assert isinstance(score, (int, float))


@pytest.mark.unit
class TestGetConfigDescription:
    """Tests for _get_config_description function."""

    def test_known_config_key(self):
        """Test description for known config key."""
        desc = _get_config_description("timeout")
        assert isinstance(desc, str)

    def test_unknown_config_key(self):
        """Test description for unknown config key."""
        desc = _get_config_description("unknown_key_xyz")
        assert isinstance(desc, str)


@pytest.mark.unit
class TestGetDiagramExample:
    """Tests for _get_diagram_example function."""

    def test_flowchart_example(self):
        """Test flowchart example is returned."""
        example = _get_diagram_example("flowchart")
        assert isinstance(example, str)
        assert "flowchart" in example.lower() or "-->" in example

    def test_sequence_example(self):
        """Test sequence diagram example is returned."""
        example = _get_diagram_example("sequence")
        assert isinstance(example, str)

    def test_unknown_type_example(self):
        """Test unknown type returns some example."""
        example = _get_diagram_example("unknown_type")
        assert isinstance(example, str)
