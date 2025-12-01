"""
Unit tests for mcp.tools.ai module.

Tests for AI-powered tools. These are now async functions with FastMCP Context support.
"""

import pytest

from diagramaid.mcp.tools.ai import (
    analyze_diagram,
    generate_diagram_from_text,
    get_diagram_suggestions,
    optimize_diagram,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestGenerateDiagramFromText:
    """Tests for generate_diagram_from_text function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await generate_diagram_from_text("A simple login process")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await generate_diagram_from_text("A simple login process")
        assert "success" in result

    async def test_with_diagram_type(self):
        """Test with specific diagram type."""
        result = await generate_diagram_from_text(
            "A simple login process", diagram_type="flowchart"
        )
        assert isinstance(result, dict)

    async def test_with_style_preference(self):
        """Test with style preference."""
        result = await generate_diagram_from_text(
            "A simple login process", style_preference="minimal"
        )
        assert isinstance(result, dict)

    async def test_with_complexity_level(self):
        """Test with complexity level."""
        result = await generate_diagram_from_text(
            "A simple login process", complexity_level="simple"
        )
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
class TestOptimizeDiagram:
    """Tests for optimize_diagram function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await optimize_diagram("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await optimize_diagram("flowchart TD\n    A --> B")
        assert "success" in result

    async def test_with_layout_optimization(self):
        """Test with layout optimization type."""
        result = await optimize_diagram(
            "flowchart TD\n    A --> B", optimization_type="layout"
        )
        assert isinstance(result, dict)

    async def test_with_style_optimization(self):
        """Test with style optimization type."""
        result = await optimize_diagram(
            "flowchart TD\n    A --> B", optimization_type="style"
        )
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAnalyzeDiagram:
    """Tests for analyze_diagram function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await analyze_diagram("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await analyze_diagram("flowchart TD\n    A --> B")
        assert "success" in result

    async def test_with_suggestions(self):
        """Test with suggestions included."""
        result = await analyze_diagram(
            "flowchart TD\n    A --> B", include_suggestions=True
        )
        assert isinstance(result, dict)

    async def test_without_suggestions(self):
        """Test without suggestions."""
        result = await analyze_diagram(
            "flowchart TD\n    A --> B", include_suggestions=False
        )
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetDiagramSuggestions:
    """Tests for get_diagram_suggestions function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await get_diagram_suggestions("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await get_diagram_suggestions("flowchart TD\n    A --> B")
        assert "success" in result
