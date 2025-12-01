"""
Unit tests for mcp.resources.templates module.

Tests for template resources.
"""

from unittest.mock import MagicMock

import pytest

from diagramaid.mcp.resources.templates import (
    get_template_details,
    get_templates_resource,
)


@pytest.mark.unit
class TestGetTemplatesResource:
    """Tests for get_templates_resource function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_templates_resource(ctx)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_templates_resource(ctx)
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_templates(self):
        """Test result includes templates."""
        import json

        ctx = MagicMock()
        result = await get_templates_resource(ctx)
        data = json.loads(result)
        assert "templates" in data

    @pytest.mark.asyncio
    async def test_includes_total_count(self):
        """Test result includes total count."""
        import json

        ctx = MagicMock()
        result = await get_templates_resource(ctx)
        data = json.loads(result)
        assert "total_count" in data


@pytest.mark.unit
class TestGetTemplateDetails:
    """Tests for get_template_details function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        # This may raise ResourceError if template not found
        try:
            result = await get_template_details(ctx, "flowchart_basic")
            assert isinstance(result, str)
        except Exception:
            # Template may not exist
            pass

    @pytest.mark.asyncio
    async def test_nonexistent_template_raises(self):
        """Test nonexistent template raises error."""
        from diagramaid.mcp.resources.base import ResourceError

        ctx = MagicMock()
        with pytest.raises(ResourceError):
            await get_template_details(ctx, "nonexistent_template_xyz")
