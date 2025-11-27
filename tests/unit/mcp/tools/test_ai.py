"""
Unit tests for mcp.tools.ai module.

Tests for AI-powered tools.
"""

import pytest

from mermaid_render.mcp.tools.ai import (
    analyze_diagram,
    generate_diagram_from_text,
    get_diagram_suggestions,
    optimize_diagram,
)


@pytest.mark.unit
class TestGenerateDiagramFromText:
    """Tests for generate_diagram_from_text function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = generate_diagram_from_text("A simple login process")
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = generate_diagram_from_text("A simple login process")
        assert "success" in result

    def test_with_diagram_type(self):
        """Test with specific diagram type."""
        result = generate_diagram_from_text(
            "A simple login process", diagram_type="flowchart"
        )
        assert isinstance(result, dict)

    def test_with_style_preference(self):
        """Test with style preference."""
        result = generate_diagram_from_text(
            "A simple login process", style_preference="minimal"
        )
        assert isinstance(result, dict)

    def test_with_complexity_level(self):
        """Test with complexity level."""
        result = generate_diagram_from_text(
            "A simple login process", complexity_level="simple"
        )
        assert isinstance(result, dict)


@pytest.mark.unit
class TestOptimizeDiagram:
    """Tests for optimize_diagram function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = optimize_diagram("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = optimize_diagram("flowchart TD\n    A --> B")
        assert "success" in result

    def test_with_layout_optimization(self):
        """Test with layout optimization type."""
        result = optimize_diagram(
            "flowchart TD\n    A --> B", optimization_type="layout"
        )
        assert isinstance(result, dict)

    def test_with_style_optimization(self):
        """Test with style optimization type."""
        result = optimize_diagram(
            "flowchart TD\n    A --> B", optimization_type="style"
        )
        assert isinstance(result, dict)


@pytest.mark.unit
class TestAnalyzeDiagram:
    """Tests for analyze_diagram function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = analyze_diagram("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = analyze_diagram("flowchart TD\n    A --> B")
        assert "success" in result

    def test_with_suggestions(self):
        """Test with suggestions included."""
        result = analyze_diagram(
            "flowchart TD\n    A --> B", include_suggestions=True
        )
        assert isinstance(result, dict)

    def test_without_suggestions(self):
        """Test without suggestions."""
        result = analyze_diagram(
            "flowchart TD\n    A --> B", include_suggestions=False
        )
        assert isinstance(result, dict)


@pytest.mark.unit
class TestGetDiagramSuggestions:
    """Tests for get_diagram_suggestions function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = get_diagram_suggestions("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = get_diagram_suggestions("flowchart TD\n    A --> B")
        assert "success" in result
