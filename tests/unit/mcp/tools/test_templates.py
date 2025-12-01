"""
Unit tests for mcp.tools.templates module.

Tests for template management tools.
These are now async functions with FastMCP Context support.
"""

import pytest

from diagramaid.mcp.tools.templates import (
    create_custom_template,
    create_from_template,
    get_template_details,
    list_available_templates,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestCreateFromTemplate:
    """Tests for create_from_template function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await create_from_template("flowchart_basic", {"title": "Test"})
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await create_from_template("flowchart_basic", {"title": "Test"})
        assert "success" in result

    async def test_with_validation(self):
        """Test with parameter validation enabled."""
        result = await create_from_template(
            "flowchart_basic", {"title": "Test"}, validate_params=True
        )
        assert isinstance(result, dict)

    async def test_without_validation(self):
        """Test with parameter validation disabled."""
        result = await create_from_template(
            "flowchart_basic", {"title": "Test"}, validate_params=False
        )
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
class TestListAvailableTemplates:
    """Tests for list_available_templates function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await list_available_templates()
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await list_available_templates()
        assert "success" in result

    async def test_with_category_filter(self):
        """Test with category filter."""
        result = await list_available_templates(category="flowchart")
        assert isinstance(result, dict)

    async def test_with_template_name_filter(self):
        """Test with template name filter."""
        result = await list_available_templates(template_name="basic")
        assert isinstance(result, dict)

    async def test_include_builtin_only(self):
        """Test with only builtin templates."""
        result = await list_available_templates(include_builtin=True, include_custom=False)
        assert isinstance(result, dict)

    async def test_include_custom_only(self):
        """Test with only custom templates."""
        result = await list_available_templates(include_builtin=False, include_custom=True)
        assert isinstance(result, dict)

    async def test_result_has_templates(self):
        """Test result includes templates data."""
        result = await list_available_templates()
        if result["success"]:
            assert "data" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetTemplateDetails:
    """Tests for get_template_details function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await get_template_details("flowchart_basic")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await get_template_details("flowchart_basic")
        assert "success" in result

    async def test_nonexistent_template(self):
        """Test with nonexistent template."""
        result = await get_template_details("nonexistent_template_xyz")
        # Should return error or empty result
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
class TestCreateCustomTemplate:
    """Tests for create_custom_template function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await create_custom_template(
            name="test_template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{start}} --> {{end}}",
            parameters={"start": {"type": "string"}, "end": {"type": "string"}},
        )
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await create_custom_template(
            name="test_template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{start}} --> {{end}}",
            parameters={"start": {"type": "string"}, "end": {"type": "string"}},
        )
        assert "success" in result

    async def test_with_description(self):
        """Test with description."""
        result = await create_custom_template(
            name="test_template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{start}} --> {{end}}",
            parameters={"start": {"type": "string"}},
            description="A test template",
        )
        assert isinstance(result, dict)

    async def test_with_tags(self):
        """Test with tags."""
        result = await create_custom_template(
            name="test_template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{start}} --> {{end}}",
            parameters={"start": {"type": "string"}},
            tags=["test", "flowchart"],
        )
        assert isinstance(result, dict)

    async def test_empty_content_fails(self):
        """Test empty template content fails."""
        result = await create_custom_template(
            name="test_template",
            diagram_type="flowchart",
            template_content="",
            parameters={},
        )
        assert result["success"] is False
