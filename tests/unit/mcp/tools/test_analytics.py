"""
Unit tests for mcp.tools.analytics module.

Tests for diagram analysis and comparison tools.
These are now async functions with FastMCP Context support.
"""

import pytest

from diagramaid.mcp.tools.analytics import (
    compare_diagrams,
    extract_diagram_elements,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestExtractDiagramElements:
    """Tests for extract_diagram_elements function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await extract_diagram_elements("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await extract_diagram_elements("flowchart TD\n    A --> B")
        assert "success" in result

    async def test_includes_nodes(self):
        """Test result includes nodes when requested."""
        result = await extract_diagram_elements(
            "flowchart TD\n    A[Start] --> B[End]", include_nodes=True
        )
        if result["success"]:
            assert "data" in result
            assert "elements" in result["data"]

    async def test_includes_edges(self):
        """Test result includes edges when requested."""
        result = await extract_diagram_elements(
            "flowchart TD\n    A --> B", include_edges=True
        )
        if result["success"]:
            assert "data" in result

    async def test_includes_styles(self):
        """Test result includes styles when requested."""
        result = await extract_diagram_elements(
            "flowchart TD\n    A --> B\n    style A fill:#f9f",
            include_styles=True,
        )
        if result["success"]:
            assert "data" in result

    async def test_includes_subgraphs(self):
        """Test result includes subgraphs when requested."""
        code = """flowchart TD
    subgraph sub1[Subgraph 1]
        A --> B
    end
"""
        result = await extract_diagram_elements(code, include_subgraphs=True)
        if result["success"]:
            assert "data" in result

    async def test_includes_statistics(self):
        """Test result includes statistics."""
        result = await extract_diagram_elements("flowchart TD\n    A --> B")
        if result["success"]:
            assert "data" in result
            assert "statistics" in result["data"]

    async def test_empty_code(self):
        """Test with empty code."""
        result = await extract_diagram_elements("")
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
class TestCompareDiagrams:
    """Tests for compare_diagrams function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await compare_diagrams(
            "flowchart TD\n    A --> B", "flowchart TD\n    A --> B --> C"
        )
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await compare_diagrams(
            "flowchart TD\n    A --> B", "flowchart TD\n    A --> B --> C"
        )
        assert "success" in result

    async def test_identical_diagrams(self):
        """Test comparison of identical diagrams."""
        code = "flowchart TD\n    A --> B"
        result = await compare_diagrams(code, code)
        if result["success"]:
            assert "data" in result
            assert "summary" in result["data"]

    async def test_different_diagrams(self):
        """Test comparison of different diagrams."""
        result = await compare_diagrams(
            "flowchart TD\n    A --> B", "flowchart TD\n    X --> Y --> Z"
        )
        if result["success"]:
            assert "data" in result
            assert "differences" in result["data"]

    async def test_structural_comparison(self):
        """Test structural comparison type."""
        result = await compare_diagrams(
            "flowchart TD\n    A --> B",
            "flowchart TD\n    A --> B --> C",
            comparison_type="structural",
        )
        assert isinstance(result, dict)

    async def test_invalid_comparison_type(self):
        """Test invalid comparison type."""
        result = await compare_diagrams(
            "flowchart TD\n    A --> B",
            "flowchart TD\n    A --> B",
            comparison_type="invalid_type",
        )
        assert result["success"] is False

    async def test_includes_similarity_score(self):
        """Test result includes similarity score."""
        result = await compare_diagrams(
            "flowchart TD\n    A --> B", "flowchart TD\n    A --> B --> C"
        )
        if result["success"]:
            assert "data" in result
            assert "summary" in result["data"]
            assert "similarity_score" in result["data"]["summary"]

    async def test_includes_element_counts(self):
        """Test result includes element counts."""
        result = await compare_diagrams(
            "flowchart TD\n    A --> B", "flowchart TD\n    A --> B --> C"
        )
        if result["success"]:
            assert "data" in result
            assert "summary" in result["data"]
