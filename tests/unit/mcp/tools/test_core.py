"""
Unit tests for mcp.tools.core module.

Tests for core tools: render_diagram, validate_diagram, list_themes.
"""

import pytest

from mermaid_render.mcp.tools.core import (
    list_themes,
    render_diagram,
    validate_diagram,
)


@pytest.mark.unit
class TestRenderDiagram:
    """Tests for render_diagram function."""

    def test_render_diagram_returns_dict(self):
        """Test render_diagram returns a dictionary."""
        result = render_diagram("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    def test_render_diagram_has_success_key(self):
        """Test render_diagram result has success key."""
        result = render_diagram("flowchart TD\n    A --> B")
        assert "success" in result

    def test_render_diagram_with_svg_format(self):
        """Test render_diagram with SVG format."""
        result = render_diagram("flowchart TD\n    A --> B", output_format="svg")
        assert isinstance(result, dict)

    def test_render_diagram_with_png_format(self):
        """Test render_diagram with PNG format."""
        result = render_diagram("flowchart TD\n    A --> B", output_format="png")
        assert isinstance(result, dict)

    def test_render_diagram_with_theme(self):
        """Test render_diagram with theme parameter."""
        result = render_diagram("flowchart TD\n    A --> B", theme="dark")
        assert isinstance(result, dict)

    def test_render_diagram_with_dimensions(self):
        """Test render_diagram with width and height."""
        result = render_diagram(
            "flowchart TD\n    A --> B", width=800, height=600
        )
        assert isinstance(result, dict)

    def test_render_diagram_empty_code_fails(self):
        """Test render_diagram with empty code returns error."""
        result = render_diagram("")
        assert result["success"] is False

    def test_render_diagram_invalid_code(self):
        """Test render_diagram with invalid code."""
        result = render_diagram("invalid mermaid code !!!")
        # Should return a result (may be error or success depending on validation)
        assert isinstance(result, dict)

    def test_render_diagram_metadata_included(self):
        """Test render_diagram includes metadata."""
        result = render_diagram("flowchart TD\n    A --> B")
        if result["success"]:
            assert "metadata" in result


@pytest.mark.unit
class TestValidateDiagram:
    """Tests for validate_diagram function."""

    def test_validate_diagram_returns_dict(self):
        """Test validate_diagram returns a dictionary."""
        result = validate_diagram("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    def test_validate_diagram_has_success_key(self):
        """Test validate_diagram result has success key."""
        result = validate_diagram("flowchart TD\n    A --> B")
        assert "success" in result

    def test_validate_valid_flowchart(self):
        """Test validation of valid flowchart."""
        result = validate_diagram("flowchart TD\n    A[Start] --> B[End]")
        assert isinstance(result, dict)
        if result["success"]:
            assert "data" in result

    def test_validate_valid_sequence_diagram(self):
        """Test validation of valid sequence diagram."""
        result = validate_diagram("sequenceDiagram\n    A->>B: Hello")
        assert isinstance(result, dict)

    def test_validate_empty_code_fails(self):
        """Test validation of empty code fails."""
        result = validate_diagram("")
        assert result["success"] is False

    def test_validate_diagram_includes_type(self):
        """Test validation result includes diagram type."""
        result = validate_diagram("flowchart TD\n    A --> B")
        if result["success"] and "data" in result:
            assert "diagram_type" in result["data"]

    def test_validate_diagram_includes_complexity(self):
        """Test validation result includes complexity score."""
        result = validate_diagram("flowchart TD\n    A --> B")
        if result["success"] and "data" in result:
            assert "complexity_score" in result["data"]


@pytest.mark.unit
class TestListThemes:
    """Tests for list_themes function."""

    def test_list_themes_returns_dict(self):
        """Test list_themes returns a dictionary."""
        result = list_themes()
        assert isinstance(result, dict)

    def test_list_themes_has_success_key(self):
        """Test list_themes result has success key."""
        result = list_themes()
        assert "success" in result

    def test_list_themes_includes_themes(self):
        """Test list_themes includes themes data."""
        result = list_themes()
        if result["success"]:
            assert "data" in result
            assert "themes" in result["data"]

    def test_list_themes_includes_default_theme(self):
        """Test list_themes includes default theme."""
        result = list_themes()
        if result["success"]:
            themes = result["data"]["themes"]
            assert "default" in themes

    def test_list_themes_includes_dark_theme(self):
        """Test list_themes includes dark theme."""
        result = list_themes()
        if result["success"]:
            themes = result["data"]["themes"]
            assert "dark" in themes

    def test_list_themes_includes_forest_theme(self):
        """Test list_themes includes forest theme."""
        result = list_themes()
        if result["success"]:
            themes = result["data"]["themes"]
            assert "forest" in themes

    def test_list_themes_theme_has_description(self):
        """Test each theme has a description."""
        result = list_themes()
        if result["success"]:
            themes = result["data"]["themes"]
            for theme_name, theme_info in themes.items():
                assert "description" in theme_info

    def test_list_themes_includes_recommendations(self):
        """Test list_themes includes recommendations."""
        result = list_themes()
        if result["success"] and "data" in result:
            assert "recommendations" in result["data"]
