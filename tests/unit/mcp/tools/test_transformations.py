"""
Unit tests for mcp.tools.transformations module.

Tests for style and structure transformation tools.
"""

import pytest

from mermaid_render.mcp.tools.transformations import (
    generate_diagram_variants,
    transform_diagram_style,
)


@pytest.mark.unit
class TestTransformDiagramStyle:
    """Tests for transform_diagram_style function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = transform_diagram_style("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = transform_diagram_style("flowchart TD\n    A --> B")
        assert "success" in result

    def test_modern_preset(self):
        """Test modern style preset."""
        result = transform_diagram_style(
            "flowchart TD\n    A --> B", style_preset="modern"
        )
        assert isinstance(result, dict)

    def test_classic_preset(self):
        """Test classic style preset."""
        result = transform_diagram_style(
            "flowchart TD\n    A --> B", style_preset="classic"
        )
        assert isinstance(result, dict)

    def test_minimal_preset(self):
        """Test minimal style preset."""
        result = transform_diagram_style(
            "flowchart TD\n    A --> B", style_preset="minimal"
        )
        assert isinstance(result, dict)

    def test_colorful_preset(self):
        """Test colorful style preset."""
        result = transform_diagram_style(
            "flowchart TD\n    A --> B", style_preset="colorful"
        )
        assert isinstance(result, dict)

    def test_dark_preset(self):
        """Test dark style preset."""
        result = transform_diagram_style(
            "flowchart TD\n    A --> B", style_preset="dark"
        )
        assert isinstance(result, dict)

    def test_invalid_preset(self):
        """Test invalid style preset."""
        result = transform_diagram_style(
            "flowchart TD\n    A --> B", style_preset="invalid_preset"
        )
        assert result["success"] is False

    def test_with_custom_color_scheme(self):
        """Test with custom color scheme."""
        result = transform_diagram_style(
            "flowchart TD\n    A --> B",
            style_preset="modern",
            color_scheme="primary:#ff0000",
        )
        assert isinstance(result, dict)

    def test_result_includes_styled_code(self):
        """Test result includes styled code."""
        result = transform_diagram_style("flowchart TD\n    A --> B")
        if result["success"]:
            assert "data" in result
            assert "styled_code" in result["data"]

    def test_result_includes_original_code(self):
        """Test result includes original code."""
        result = transform_diagram_style("flowchart TD\n    A --> B")
        if result["success"]:
            assert "data" in result
            assert "original_code" in result["data"]


@pytest.mark.unit
class TestGenerateDiagramVariants:
    """Tests for generate_diagram_variants function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = generate_diagram_variants("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = generate_diagram_variants("flowchart TD\n    A --> B")
        assert "success" in result

    def test_layout_variation(self):
        """Test layout variation type."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variation_type="layout"
        )
        assert isinstance(result, dict)

    def test_style_variation(self):
        """Test style variation type."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variation_type="style"
        )
        assert isinstance(result, dict)

    def test_structure_variation(self):
        """Test structure variation type."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variation_type="structure"
        )
        assert isinstance(result, dict)

    def test_invalid_variation_type(self):
        """Test invalid variation type."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variation_type="invalid_type"
        )
        assert result["success"] is False

    def test_variant_count(self):
        """Test variant count parameter."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variant_count=3
        )
        if result["success"]:
            assert "data" in result
            assert "variants" in result["data"]

    def test_variant_count_minimum(self):
        """Test minimum variant count."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variant_count=1
        )
        assert isinstance(result, dict)

    def test_variant_count_maximum(self):
        """Test maximum variant count."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variant_count=5
        )
        assert isinstance(result, dict)

    def test_variant_count_out_of_range(self):
        """Test variant count out of range."""
        result = generate_diagram_variants(
            "flowchart TD\n    A --> B", variant_count=10
        )
        assert result["success"] is False

    def test_result_includes_variants(self):
        """Test result includes variants."""
        result = generate_diagram_variants("flowchart TD\n    A --> B")
        if result["success"]:
            assert "data" in result
            assert "variants" in result["data"]
            assert isinstance(result["data"]["variants"], list)
