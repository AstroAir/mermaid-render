"""
Unit tests for mcp.resources.extended module.

Tests for extended resources (syntax, best practices, capabilities, etc.).
"""

from unittest.mock import MagicMock

import pytest

from diagramaid.mcp.resources.extended import (
    get_best_practices,
    get_capabilities,
    get_changelog,
    get_shortcuts_reference,
    get_syntax_reference,
)


@pytest.mark.unit
class TestGetSyntaxReference:
    """Tests for get_syntax_reference function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_syntax_reference(ctx, "flowchart")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_syntax_reference(ctx, "flowchart")
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_flowchart_syntax(self):
        """Test flowchart syntax reference."""
        import json

        ctx = MagicMock()
        result = await get_syntax_reference(ctx, "flowchart")
        data = json.loads(result)
        assert data["name"] == "Flowchart"

    @pytest.mark.asyncio
    async def test_sequence_syntax(self):
        """Test sequence diagram syntax reference."""
        import json

        ctx = MagicMock()
        result = await get_syntax_reference(ctx, "sequence")
        data = json.loads(result)
        assert data["name"] == "Sequence Diagram"

    @pytest.mark.asyncio
    async def test_class_syntax(self):
        """Test class diagram syntax reference."""
        import json

        ctx = MagicMock()
        result = await get_syntax_reference(ctx, "class")
        data = json.loads(result)
        assert data["name"] == "Class Diagram"

    @pytest.mark.asyncio
    async def test_includes_declaration(self):
        """Test syntax reference includes declaration."""
        import json

        ctx = MagicMock()
        result = await get_syntax_reference(ctx, "flowchart")
        data = json.loads(result)
        assert "declaration" in data

    @pytest.mark.asyncio
    async def test_includes_examples(self):
        """Test syntax reference includes examples."""
        import json

        ctx = MagicMock()
        result = await get_syntax_reference(ctx, "flowchart")
        data = json.loads(result)
        assert "examples" in data

    @pytest.mark.asyncio
    async def test_nonexistent_type_raises(self):
        """Test nonexistent diagram type raises error."""
        from diagramaid.mcp.resources.base import ResourceError

        ctx = MagicMock()
        with pytest.raises(ResourceError):
            await get_syntax_reference(ctx, "nonexistent_type")


@pytest.mark.unit
class TestGetBestPractices:
    """Tests for get_best_practices function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_best_practices(ctx)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_best_practices(ctx)
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_general(self):
        """Test result includes general best practices."""
        import json

        ctx = MagicMock()
        result = await get_best_practices(ctx)
        data = json.loads(result)
        assert "general" in data

    @pytest.mark.asyncio
    async def test_includes_flowchart(self):
        """Test result includes flowchart best practices."""
        import json

        ctx = MagicMock()
        result = await get_best_practices(ctx)
        data = json.loads(result)
        assert "flowchart" in data

    @pytest.mark.asyncio
    async def test_includes_sequence(self):
        """Test result includes sequence best practices."""
        import json

        ctx = MagicMock()
        result = await get_best_practices(ctx)
        data = json.loads(result)
        assert "sequence" in data

    @pytest.mark.asyncio
    async def test_practice_has_title(self):
        """Test practice has title."""
        import json

        ctx = MagicMock()
        result = await get_best_practices(ctx)
        data = json.loads(result)
        assert "title" in data["general"]


@pytest.mark.unit
class TestGetCapabilities:
    """Tests for get_capabilities function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_capabilities(ctx)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_capabilities(ctx)
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_server(self):
        """Test result includes server info."""
        import json

        ctx = MagicMock()
        result = await get_capabilities(ctx)
        data = json.loads(result)
        assert "server" in data

    @pytest.mark.asyncio
    async def test_includes_diagram_types(self):
        """Test result includes diagram types."""
        import json

        ctx = MagicMock()
        result = await get_capabilities(ctx)
        data = json.loads(result)
        assert "diagram_types" in data

    @pytest.mark.asyncio
    async def test_includes_output_formats(self):
        """Test result includes output formats."""
        import json

        ctx = MagicMock()
        result = await get_capabilities(ctx)
        data = json.loads(result)
        assert "output_formats" in data

    @pytest.mark.asyncio
    async def test_includes_tools(self):
        """Test result includes tools."""
        import json

        ctx = MagicMock()
        result = await get_capabilities(ctx)
        data = json.loads(result)
        assert "tools" in data

    @pytest.mark.asyncio
    async def test_includes_prompts(self):
        """Test result includes prompts."""
        import json

        ctx = MagicMock()
        result = await get_capabilities(ctx)
        data = json.loads(result)
        assert "prompts" in data

    @pytest.mark.asyncio
    async def test_includes_resources(self):
        """Test result includes resources."""
        import json

        ctx = MagicMock()
        result = await get_capabilities(ctx)
        data = json.loads(result)
        assert "resources" in data


@pytest.mark.unit
class TestGetChangelog:
    """Tests for get_changelog function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_changelog(ctx)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_changelog(ctx)
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_current_version(self):
        """Test result includes current version."""
        import json

        ctx = MagicMock()
        result = await get_changelog(ctx)
        data = json.loads(result)
        assert "current_version" in data

    @pytest.mark.asyncio
    async def test_includes_releases(self):
        """Test result includes releases."""
        import json

        ctx = MagicMock()
        result = await get_changelog(ctx)
        data = json.loads(result)
        assert "releases" in data
        assert isinstance(data["releases"], list)


@pytest.mark.unit
class TestGetShortcutsReference:
    """Tests for get_shortcuts_reference function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_shortcuts_reference(ctx)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_shortcuts_reference(ctx)
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_quick_start(self):
        """Test result includes quick start."""
        import json

        ctx = MagicMock()
        result = await get_shortcuts_reference(ctx)
        data = json.loads(result)
        assert "quick_start" in data

    @pytest.mark.asyncio
    async def test_includes_common_patterns(self):
        """Test result includes common patterns."""
        import json

        ctx = MagicMock()
        result = await get_shortcuts_reference(ctx)
        data = json.loads(result)
        assert "common_patterns" in data

    @pytest.mark.asyncio
    async def test_includes_styling_shortcuts(self):
        """Test result includes styling shortcuts."""
        import json

        ctx = MagicMock()
        result = await get_shortcuts_reference(ctx)
        data = json.loads(result)
        assert "styling_shortcuts" in data
