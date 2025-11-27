"""
Unit tests for mcp.prompts.optimization module.

Tests for diagram optimization prompts.
"""

import pytest

from mermaid_render.mcp.prompts.optimization import (
    optimize_layout_prompt,
    simplify_diagram_prompt,
)


@pytest.mark.unit
class TestSimplifyDiagramPrompt:
    """Tests for simplify_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = simplify_diagram_prompt("flowchart TD\n    A --> B --> C --> D")
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A --> B --> C"
        result = simplify_diagram_prompt(code)
        assert "A --> B" in result

    def test_simple_target_complexity(self):
        """Test simple target complexity."""
        result = simplify_diagram_prompt(
            "flowchart TD\n    A --> B", target_complexity="simple"
        )
        assert "simple" in result.lower() or "3-5" in result

    def test_moderate_target_complexity(self):
        """Test moderate target complexity."""
        result = simplify_diagram_prompt(
            "flowchart TD\n    A --> B", target_complexity="moderate"
        )
        assert isinstance(result, str)

    def test_with_preserve_elements(self):
        """Test with elements to preserve."""
        result = simplify_diagram_prompt(
            "flowchart TD\n    A --> B",
            preserve_elements=["Start node", "End node"],
        )
        assert "Start node" in result
        assert "End node" in result

    def test_requests_simplified_version(self):
        """Test prompt requests simplified version."""
        result = simplify_diagram_prompt("flowchart TD\n    A --> B")
        assert "simplif" in result.lower()


@pytest.mark.unit
class TestOptimizeLayoutPrompt:
    """Tests for optimize_layout_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = optimize_layout_prompt(
            "flowchart TD\n    A --> B", ["Reduce crossing lines"]
        )
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A --> B"
        result = optimize_layout_prompt(code, ["Goal 1"])
        assert "A --> B" in result

    def test_includes_optimization_goals(self):
        """Test prompt includes optimization goals."""
        goals = ["Reduce crossing lines", "Improve readability"]
        result = optimize_layout_prompt("flowchart TD\n    A --> B", goals)
        for goal in goals:
            assert goal in result

    def test_requests_layout_analysis(self):
        """Test prompt requests layout analysis."""
        result = optimize_layout_prompt(
            "flowchart TD\n    A --> B", ["Goal"]
        )
        assert "layout" in result.lower()

    def test_requests_optimized_version(self):
        """Test prompt requests optimized version."""
        result = optimize_layout_prompt(
            "flowchart TD\n    A --> B", ["Goal"]
        )
        assert "optimiz" in result.lower()
