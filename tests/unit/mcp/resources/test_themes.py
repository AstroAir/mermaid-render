"""
Unit tests for mcp.resources.themes module.

Tests for theme resources.
"""

from unittest.mock import MagicMock

import pytest

from mermaid_render.mcp.resources.themes import (
    get_theme_details,
    get_themes_resource,
)


@pytest.mark.unit
class TestGetThemesResource:
    """Tests for get_themes_resource function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_themes_resource(ctx)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_themes_resource(ctx)
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_themes(self):
        """Test result includes themes."""
        import json

        ctx = MagicMock()
        result = await get_themes_resource(ctx)
        data = json.loads(result)
        assert "themes" in data

    @pytest.mark.asyncio
    async def test_includes_default_theme(self):
        """Test result includes default theme."""
        import json

        ctx = MagicMock()
        result = await get_themes_resource(ctx)
        data = json.loads(result)
        assert "default" in data["themes"]

    @pytest.mark.asyncio
    async def test_includes_dark_theme(self):
        """Test result includes dark theme."""
        import json

        ctx = MagicMock()
        result = await get_themes_resource(ctx)
        data = json.loads(result)
        assert "dark" in data["themes"]

    @pytest.mark.asyncio
    async def test_includes_total_count(self):
        """Test result includes total count."""
        import json

        ctx = MagicMock()
        result = await get_themes_resource(ctx)
        data = json.loads(result)
        assert "total_count" in data


@pytest.mark.unit
class TestGetThemeDetails:
    """Tests for get_theme_details function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_theme_details(ctx, "default")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_theme_details(ctx, "default")
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_default_theme_details(self):
        """Test default theme details."""
        import json

        ctx = MagicMock()
        result = await get_theme_details(ctx, "default")
        data = json.loads(result)
        assert data["name"] == "default"

    @pytest.mark.asyncio
    async def test_dark_theme_details(self):
        """Test dark theme details."""
        import json

        ctx = MagicMock()
        result = await get_theme_details(ctx, "dark")
        data = json.loads(result)
        assert data["name"] == "dark"

    @pytest.mark.asyncio
    async def test_includes_colors(self):
        """Test theme details include colors."""
        import json

        ctx = MagicMock()
        result = await get_theme_details(ctx, "default")
        data = json.loads(result)
        assert "colors" in data

    @pytest.mark.asyncio
    async def test_includes_description(self):
        """Test theme details include description."""
        import json

        ctx = MagicMock()
        result = await get_theme_details(ctx, "default")
        data = json.loads(result)
        assert "description" in data

    @pytest.mark.asyncio
    async def test_nonexistent_theme_raises(self):
        """Test nonexistent theme raises error."""
        from mermaid_render.mcp.resources.base import ResourceError

        ctx = MagicMock()
        with pytest.raises(ResourceError):
            await get_theme_details(ctx, "nonexistent_theme")
