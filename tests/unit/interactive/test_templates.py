"""
Unit tests for interactive.templates module.

Tests the InteractiveTemplate and TemplateLibrary classes.
"""

import pytest

from diagramaid.interactive.templates import InteractiveTemplate, TemplateLibrary


def create_test_template(
    template_id: str = "test1",
    name: str = "Test Template",
    description: str = "A test template",
) -> InteractiveTemplate:
    """Create a test template with required fields."""
    return InteractiveTemplate(
        id=template_id,
        name=name,
        description=description,
        diagram_type="flowchart",
        elements=[],
        connections=[],
        metadata={},
    )


@pytest.mark.unit
class TestInteractiveTemplate:
    """Unit tests for InteractiveTemplate class."""

    def test_initialization(self) -> None:
        """Test InteractiveTemplate initialization."""
        template = create_test_template(name="Basic Flowchart")
        assert template.name == "Basic Flowchart"
        assert template.diagram_type == "flowchart"

    def test_template_has_name(self) -> None:
        """Test that template has name."""
        template = create_test_template(name="Test")
        assert template.name == "Test"

    def test_template_has_code(self) -> None:
        """Test that template has diagram_type."""
        template = create_test_template()
        template.diagram_type = "sequence"
        assert template.diagram_type == "sequence"

    def test_template_to_dict(self) -> None:
        """Test template serialization."""
        template = create_test_template(name="Test", description="A test template")
        result = template.to_dict()
        assert result["name"] == "Test"
        assert result["description"] == "A test template"


@pytest.mark.unit
class TestTemplateLibrary:
    """Unit tests for TemplateLibrary class."""

    def test_initialization(self) -> None:
        """Test TemplateLibrary initialization."""
        library = TemplateLibrary()
        assert library is not None

    def test_list_templates(self) -> None:
        """Test listing all templates."""
        library = TemplateLibrary()
        templates = library.list_templates()
        assert isinstance(templates, list)

    def test_get_template_by_id(self) -> None:
        """Test getting template by ID."""
        library = TemplateLibrary()
        template = create_test_template(template_id="test1", name="Test")
        library.add_template(template)
        retrieved = library.get_template("test1")
        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_add_template(self) -> None:
        """Test adding template to library."""
        library = TemplateLibrary()
        template = create_test_template(template_id="new1", name="New")
        library.add_template(template)
        assert library.get_template("new1") is not None

    def test_remove_template(self) -> None:
        """Test removing template from library."""
        library = TemplateLibrary()
        template = create_test_template(template_id="remove1", name="ToRemove")
        library.add_template(template)
        result = library.remove_template("remove1")
        assert result is True
        assert library.get_template("remove1") is None

    def test_list_templates_by_category(self) -> None:
        """Test listing templates by category."""
        library = TemplateLibrary()
        templates = library.list_templates(category="flowchart")
        assert isinstance(templates, list)

    def test_get_categories(self) -> None:
        """Test getting template categories."""
        library = TemplateLibrary()
        categories = library.get_categories()
        assert isinstance(categories, list)
