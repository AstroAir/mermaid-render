"""
Unit tests for interactive.templates module.

Tests the InteractiveTemplate and TemplateLibrary classes.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.templates import InteractiveTemplate, TemplateLibrary


@pytest.mark.unit
class TestInteractiveTemplate:
    """Unit tests for InteractiveTemplate class."""

    def test_initialization(self) -> None:
        """Test InteractiveTemplate initialization."""
        template = InteractiveTemplate(
            name="Basic Flowchart",
            code="flowchart TD\n    A --> B"
        )
        assert template.name == "Basic Flowchart"
        assert "flowchart" in template.code

    def test_template_has_name(self) -> None:
        """Test that template has name."""
        template = InteractiveTemplate(name="Test", code="graph TD")
        assert template.name == "Test"

    def test_template_has_code(self) -> None:
        """Test that template has code."""
        template = InteractiveTemplate(name="Test", code="sequenceDiagram")
        assert template.code == "sequenceDiagram"

    def test_template_to_dict(self) -> None:
        """Test template serialization."""
        template = InteractiveTemplate(
            name="Test",
            code="flowchart LR",
            description="A test template"
        )
        result = template.to_dict()
        assert result["name"] == "Test"
        assert result["code"] == "flowchart LR"


@pytest.mark.unit
class TestTemplateLibrary:
    """Unit tests for TemplateLibrary class."""

    def test_initialization(self) -> None:
        """Test TemplateLibrary initialization."""
        library = TemplateLibrary()
        assert library is not None

    def test_get_templates(self) -> None:
        """Test getting all templates."""
        library = TemplateLibrary()
        templates = library.get_templates()
        assert isinstance(templates, list)

    def test_get_template_by_name(self) -> None:
        """Test getting template by name."""
        library = TemplateLibrary()
        # Add a template first
        template = InteractiveTemplate(name="Test", code="graph TD")
        library.add_template(template)
        
        retrieved = library.get_template("Test")
        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_add_template(self) -> None:
        """Test adding template to library."""
        library = TemplateLibrary()
        template = InteractiveTemplate(name="New", code="flowchart TD")
        library.add_template(template)
        
        assert library.get_template("New") is not None

    def test_remove_template(self) -> None:
        """Test removing template from library."""
        library = TemplateLibrary()
        template = InteractiveTemplate(name="ToRemove", code="graph LR")
        library.add_template(template)
        library.remove_template("ToRemove")
        
        assert library.get_template("ToRemove") is None

    def test_get_templates_by_category(self) -> None:
        """Test getting templates by category."""
        library = TemplateLibrary()
        templates = library.get_templates_by_category("flowchart")
        assert isinstance(templates, list)

    def test_template_count(self) -> None:
        """Test template count."""
        library = TemplateLibrary()
        initial_count = library.template_count()
        
        template = InteractiveTemplate(name="Count Test", code="graph TD")
        library.add_template(template)
        
        assert library.template_count() >= initial_count
