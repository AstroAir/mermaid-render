"""
Unit tests for mcp.resources.docs module.

Tests for documentation resources.
"""

from unittest.mock import MagicMock

import pytest

from diagramaid.mcp.resources.docs import (
    get_diagram_examples,
    get_diagram_types_docs,
)


@pytest.mark.unit
class TestGetDiagramTypesDocs:
    """Tests for get_diagram_types_docs function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_flowchart(self):
        """Test result includes flowchart type."""
        import json

        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        data = json.loads(result)
        assert "flowchart" in data

    @pytest.mark.asyncio
    async def test_includes_sequence(self):
        """Test result includes sequence type."""
        import json

        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        data = json.loads(result)
        assert "sequence" in data

    @pytest.mark.asyncio
    async def test_includes_class(self):
        """Test result includes class type."""
        import json

        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        data = json.loads(result)
        assert "class" in data

    @pytest.mark.asyncio
    async def test_diagram_type_has_name(self):
        """Test diagram type has name."""
        import json

        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        data = json.loads(result)
        assert "name" in data["flowchart"]

    @pytest.mark.asyncio
    async def test_diagram_type_has_description(self):
        """Test diagram type has description."""
        import json

        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        data = json.loads(result)
        assert "description" in data["flowchart"]

    @pytest.mark.asyncio
    async def test_diagram_type_has_syntax(self):
        """Test diagram type has syntax."""
        import json

        ctx = MagicMock()
        result = await get_diagram_types_docs(ctx)
        data = json.loads(result)
        assert "syntax" in data["flowchart"]


@pytest.mark.unit
class TestGetDiagramExamples:
    """Tests for get_diagram_examples function."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Test function returns a string."""
        ctx = MagicMock()
        result = await get_diagram_examples(ctx, "flowchart")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_returns_json(self):
        """Test function returns valid JSON."""
        import json

        ctx = MagicMock()
        result = await get_diagram_examples(ctx, "flowchart")
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_includes_diagram_type(self):
        """Test result includes diagram type."""
        import json

        ctx = MagicMock()
        result = await get_diagram_examples(ctx, "flowchart")
        data = json.loads(result)
        assert "diagram_type" in data
        assert data["diagram_type"] == "flowchart"

    @pytest.mark.asyncio
    async def test_includes_examples(self):
        """Test result includes examples."""
        import json

        ctx = MagicMock()
        result = await get_diagram_examples(ctx, "flowchart")
        data = json.loads(result)
        assert "examples" in data
        assert isinstance(data["examples"], list)

    @pytest.mark.asyncio
    async def test_example_has_title(self):
        """Test example has title."""
        import json

        ctx = MagicMock()
        result = await get_diagram_examples(ctx, "flowchart")
        data = json.loads(result)
        if data["examples"]:
            assert "title" in data["examples"][0]

    @pytest.mark.asyncio
    async def test_example_has_code(self):
        """Test example has code."""
        import json

        ctx = MagicMock()
        result = await get_diagram_examples(ctx, "flowchart")
        data = json.loads(result)
        if data["examples"]:
            assert "code" in data["examples"][0]

    @pytest.mark.asyncio
    async def test_nonexistent_type_raises(self):
        """Test nonexistent diagram type raises error."""
        from diagramaid.mcp.resources.base import ResourceError

        ctx = MagicMock()
        with pytest.raises(ResourceError):
            await get_diagram_examples(ctx, "nonexistent_type")
