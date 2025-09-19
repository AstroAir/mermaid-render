"""
Unit tests for templates module.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch, mock_open

import pytest

from mermaid_render.templates import (
    Template,
    TemplateManager,
    FlowchartGenerator,
    SequenceGenerator,
    ClassDiagramGenerator,
    ArchitectureGenerator,
    ProcessFlowGenerator,
    validate_template,
    generate_from_template,
    list_available_templates,
    get_template_info,
)
from mermaid_render.templates.schema import ParameterSchema, TemplateSchema
from mermaid_render.exceptions import ValidationError


class TestTemplate:
    """Test Template class."""

    def test_template_creation(self) -> None:
        """Test basic template creation."""
        now = datetime.now()
        template = Template(
            id="test-id",
            name="Test Template",
            description="A test template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{title}}",
            parameters={"title": "string"},
            metadata={"category": "test"},
            created_at=now,
            updated_at=now,
        )

        assert template.id == "test-id"
        assert template.name == "Test Template"
        assert template.diagram_type == "flowchart"
        assert template.parameters == {"title": "string"}
        assert template.tags == []  # Default empty list

    def test_template_with_tags(self) -> None:
        """Test template creation with tags."""
        now = datetime.now()
        template = Template(
            id="test-id",
            name="Test Template",
            description="A test template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{title}}",
            parameters={"title": "string"},
            metadata={},
            created_at=now,
            updated_at=now,
            tags=["test", "example"],
        )

        assert template.tags == ["test", "example"]

    def test_template_to_dict(self) -> None:
        """Test template serialization to dictionary."""
        now = datetime.now()
        template = Template(
            id="test-id",
            name="Test Template",
            description="A test template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{title}}",
            parameters={"title": "string"},
            metadata={"category": "test"},
            created_at=now,
            updated_at=now,
            author="Test Author",
        )

        template_dict = template.to_dict()

        assert template_dict["id"] == "test-id"
        assert template_dict["name"] == "Test Template"
        assert template_dict["author"] == "Test Author"
        assert isinstance(template_dict["created_at"], str)  # Should be ISO format
        assert isinstance(template_dict["updated_at"], str)


class TestTemplateManager:
    """Test TemplateManager class."""

    def test_template_manager_init(self) -> None:
        """Test template manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = TemplateManager(templates_dir=Path(temp_dir))

            assert manager.templates_dir == Path(temp_dir)
            assert isinstance(manager._templates, dict)

    def test_create_template(self) -> None:
        """Test creating a new template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = TemplateManager(templates_dir=Path(temp_dir))

            template = manager.create_template(
                name="Test Template",
                diagram_type="flowchart",
                template_content="flowchart TD\n    {{title}}",
                parameters={"title": "string"},
                description="A test template",
                author="Test Author",
                tags=["test"],
            )

            assert template.name == "Test Template"
            assert template.diagram_type == "flowchart"
            assert template.author == "Test Author"
            assert template.tags is not None and "test" in template.tags
            assert template.id in manager._templates

    def test_get_template(self) -> None:
        """Test retrieving a template by ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = TemplateManager(templates_dir=Path(temp_dir))

            template = manager.create_template(
                name="Test Template",
                diagram_type="flowchart",
                template_content="flowchart TD\n    {{title}}",
                parameters={"title": "string"},
            )

            retrieved = manager.get_template(template.id)
            assert retrieved is not None
            assert retrieved.name == "Test Template"

            # Test non-existent template
            assert manager.get_template("nonexistent") is None

    def test_get_template_by_name(self) -> None:
        """Test retrieving a template by name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = TemplateManager(templates_dir=Path(temp_dir))

            template = manager.create_template(
                name="Unique Template Name",
                diagram_type="flowchart",
                template_content="flowchart TD\n    {{title}}",
                parameters={"title": "string"},
            )

            retrieved = manager.get_template_by_name("Unique Template Name")
            assert retrieved is not None
            assert retrieved.id == template.id

    def test_list_templates(self) -> None:
        """Test listing all templates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = TemplateManager(templates_dir=Path(
                temp_dir), auto_load_builtin=False)

            # Create multiple templates
            template1 = manager.create_template(
                name="Template 1",
                diagram_type="flowchart",
                template_content="flowchart TD\n    A",
                parameters={},
            )
            template2 = manager.create_template(
                name="Template 2",
                diagram_type="sequence",
                template_content="sequenceDiagram\n    A->>B: Message",
                parameters={},
            )

            templates = manager.list_templates()
            assert len(templates) == 2
            template_names = [t.name for t in templates]
            assert "Template 1" in template_names
            assert "Template 2" in template_names

    def test_generate_from_template(self) -> None:
        """Test generating diagram from template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = TemplateManager(templates_dir=Path(temp_dir))

            template = manager.create_template(
                name="Parameterized Template",
                diagram_type="flowchart",
                template_content="flowchart TD\n    {{start}} --> {{end}}",
                parameters={"start": "string", "end": "string"},
            )

            result = manager.generate(
                template.id,
                {"start": "Begin", "end": "Finish"}
            )

            assert "Begin" in result
            assert "Finish" in result
            assert "-->" in result

    def test_delete_template(self) -> None:
        """Test deleting a template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = TemplateManager(templates_dir=Path(temp_dir))

            template = manager.create_template(
                name="To Delete",
                diagram_type="flowchart",
                template_content="flowchart TD\n    A",
                parameters={},
            )

            # Verify template exists
            assert manager.get_template(template.id) is not None

            # Delete template
            result = manager.delete_template(template.id)
            assert result is True

            # Verify template is gone
            assert manager.get_template(template.id) is None

            # Test deleting non-existent template
            result = manager.delete_template("nonexistent")
            assert result is False


class TestFlowchartGenerator:
    """Test FlowchartGenerator class."""

    def test_basic_flowchart_generation(self) -> None:
        """Test basic flowchart generation."""
        generator = FlowchartGenerator()

        data = {
            "direction": "TD",
            "title": "Test Flowchart",
            "nodes": [
                {"id": "A", "label": "Start", "shape": "circle"},
                {"id": "B", "label": "Process", "shape": "rectangle"},
                {"id": "C", "label": "End", "shape": "circle"},
            ],
            "edges": [
                {"from": "A", "to": "B", "label": "Begin"},
                {"from": "B", "to": "C", "label": "Complete"},
            ],
        }

        result = generator.generate(data)

        assert "flowchart TD" in result
        assert "Start" in result
        assert "Process" in result
        assert "End" in result
        assert "Begin" in result
        assert "Complete" in result

    def test_flowchart_with_styling(self) -> None:
        """Test flowchart generation with styling."""
        generator = FlowchartGenerator()

        data = {
            "nodes": [{"id": "A", "label": "Styled Node"}],
            "styling": {
                "classes": {
                    "highlight": {
                        "fill": "#ff0000",
                        "stroke": "#000000",
                    }
                },
                "node_classes": {"A": "highlight"},
            },
        }

        result = generator.generate(data)

        assert "Styled Node" in result
        assert "classDef" in result or "class" in result

    def test_flowchart_schema(self) -> None:
        """Test flowchart generator schema."""
        generator = FlowchartGenerator()
        schema = generator.get_schema()

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "nodes" in schema["properties"]
        assert "edges" in schema["properties"]


class TestSequenceGenerator:
    """Test SequenceGenerator class."""

    def test_basic_sequence_generation(self) -> None:
        """Test basic sequence diagram generation."""
        generator = SequenceGenerator()

        data = {
            "title": "Test Sequence",
            "participants": [
                {"id": "user", "name": "User"},
                {"id": "api", "name": "API Server"},
            ],
            "messages": [
                {"from": "user", "to": "api", "message": "Request", "type": "sync"},
                {"from": "api", "to": "user", "message": "Response", "type": "sync"},
            ],
        }

        result = generator.generate(data)

        assert "sequenceDiagram" in result
        assert "participant user as User" in result
        assert "participant api as API Server" in result
        assert "user->>api: Request" in result
        assert "api->>user: Response" in result

    def test_sequence_with_notes(self) -> None:
        """Test sequence diagram with notes."""
        generator = SequenceGenerator()

        data = {
            "participants": [{"id": "A", "name": "Actor A"}],
            "messages": [
                {"type": "note", "participant": "A", "message": "Important note"},
            ],
        }

        result = generator.generate(data)

        assert "Note over A: Important note" in result

    def test_sequence_schema(self) -> None:
        """Test sequence generator schema."""
        generator = SequenceGenerator()
        schema = generator.get_schema()

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "participants" in schema["properties"]
        assert "messages" in schema["properties"]


class TestClassDiagramGenerator:
    """Test ClassDiagramGenerator class."""

    def test_basic_class_generation(self) -> None:
        """Test basic class diagram generation."""
        generator = ClassDiagramGenerator()

        data = {
            "title": "Test Classes",
            "classes": [
                {
                    "name": "User",
                    "attributes": [
                        {"name": "name", "type": "string"},
                        {"name": "email", "type": "string"}
                    ],
                    "methods": [
                        {"name": "login"},
                        {"name": "logout"}
                    ],
                },
                {
                    "name": "Admin",
                    "attributes": [
                        {"name": "permissions", "type": "list"}
                    ],
                    "methods": [
                        {"name": "manage"}
                    ],
                },
            ],
            "relationships": [
                {"from": "Admin", "to": "User", "type": "inheritance"},
            ],
        }

        result = generator.generate(data)

        assert "classDiagram" in result
        assert "class User" in result
        assert "class Admin" in result
        assert "name: string" in result
        assert "login()" in result
        assert "Admin --|> User" in result

    def test_class_schema(self) -> None:
        """Test class generator schema."""
        generator = ClassDiagramGenerator()
        schema = generator.get_schema()

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "classes" in schema["properties"]
        assert "relationships" in schema["properties"]


class TestArchitectureGenerator:
    """Test ArchitectureGenerator class."""

    def test_architecture_generation(self) -> None:
        """Test architecture diagram generation."""
        generator = ArchitectureGenerator()

        data = {
            "title": "System Architecture",
            "components": [
                {"id": "api", "name": "API Gateway", "type": "service"},
                {"id": "db", "name": "Database", "type": "database"},
            ],
            "connections": [
                {"from": "api", "to": "db", "label": "queries"},
            ],
        }

        result = generator.generate(data)

        assert "flowchart" in result
        assert "API Gateway" in result
        assert "Database" in result
        assert "queries" in result

    def test_architecture_schema(self) -> None:
        """Test architecture generator schema."""
        generator = ArchitectureGenerator()
        schema = generator.get_schema()

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "components" in schema["properties"]
        assert "connections" in schema["properties"]


class TestProcessFlowGenerator:
    """Test ProcessFlowGenerator class."""

    def test_process_flow_generation(self) -> None:
        """Test process flow diagram generation."""
        generator = ProcessFlowGenerator()

        data = {
            "title": "Business Process",
            "processes": [
                {"id": "start", "label": "Start Process", "type": "start"},
                {"id": "review", "label": "Review", "type": "task"},
                {"id": "end", "label": "End Process", "type": "end"},
            ],
            "flows": [
                {"from": "start", "to": "review"},
                {"from": "review", "to": "end"},
            ],
        }

        result = generator.generate(data)

        assert "flowchart" in result
        assert "Start Process" in result
        assert "Review" in result
        assert "End Process" in result

    def test_process_flow_schema(self) -> None:
        """Test process flow generator schema."""
        generator = ProcessFlowGenerator()
        schema = generator.get_schema()

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "processes" in schema["properties"]
        assert "flows" in schema["properties"]


class TestTemplateValidation:
    """Test template validation functionality."""

    def test_validate_valid_template(self) -> None:
        """Test validation of valid template."""
        template_data = {
            "name": "Valid Template",
            "diagram_type": "flowchart",
            "template_content": "flowchart TD\n    {{title}}",
            "parameters": {"title": "string"},
            "description": "A valid template",
        }

        # Should not raise an exception
        validate_template(template_data)

    def test_validate_missing_required_fields(self) -> None:
        """Test validation with missing required fields."""
        template_data = {
            "name": "Incomplete Template",
            # Missing diagram_type, template_content, parameters
        }

        with pytest.raises(ValidationError):
            validate_template(template_data)

    def test_validate_invalid_diagram_type(self) -> None:
        """Test validation with invalid diagram type."""
        template_data = {
            "name": "Invalid Template",
            "diagram_type": "invalid_type",
            "template_content": "content",
            "parameters": {},
        }

        with pytest.raises(ValidationError):
            validate_template(template_data)


class TestTemplateUtilities:
    """Test template utility functions."""

    def test_generate_from_template_function(self) -> None:
        """Test generate_from_template utility function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the template manager
            with patch('mermaid_render.templates.utils.TemplateManager') as mock_manager_class:
                mock_manager = Mock()
                mock_manager.generate.return_value = "flowchart TD\n    Start --> End"
                mock_manager_class.return_value = mock_manager

                result = generate_from_template("test_template", {"param": "value"})

                assert result == "flowchart TD\n    Start --> End"
                mock_manager.generate.assert_called_once_with(
                    "test_template", {"param": "value"}, True)

    def test_list_available_templates_function(self) -> None:
        """Test list_available_templates utility function."""
        with patch('mermaid_render.templates.utils.TemplateManager') as mock_manager_class:
            mock_template1 = Mock()
            mock_template1.id = "template1"
            mock_template1.name = "Template 1"
            mock_template1.description = "First template"
            mock_template1.diagram_type = "flowchart"
            mock_template1.tags = ["test"]
            mock_template1.author = "Test Author"
            mock_template1.version = "1.0.0"
            mock_template1.created_at.isoformat.return_value = "2023-01-01T00:00:00"
            mock_template1.parameters = {"required": ["param1", "param2"]}

            mock_template2 = Mock()
            mock_template2.id = "template2"
            mock_template2.name = "Template 2"
            mock_template2.description = "Second template"
            mock_template2.diagram_type = "sequence"
            mock_template2.tags = ["test"]
            mock_template2.author = "Test Author"
            mock_template2.version = "1.0.0"
            mock_template2.created_at.isoformat.return_value = "2023-01-01T00:00:00"
            mock_template2.parameters = {"required": ["param1"]}

            mock_manager = Mock()
            mock_manager.list_templates.return_value = [mock_template1, mock_template2]
            mock_manager_class.return_value = mock_manager

            result = list_available_templates()

            assert len(result) == 2
            assert result[0]["name"] == "Template 1"
            assert result[1]["name"] == "Template 2"
            assert result[0]["parameter_count"] == 2
            assert result[1]["parameter_count"] == 1

    def test_get_template_info_function(self) -> None:
        """Test get_template_info utility function."""
        with patch('mermaid_render.templates.utils.TemplateManager') as mock_manager_class:
            mock_template = Mock()
            mock_template.name = "Test Template"
            mock_template.description = "A test template"
            mock_template.diagram_type = "flowchart"
            mock_template.parameters = {"title": "string"}
            mock_template.to_dict.return_value = {
                "name": "Test Template",
                "description": "A test template",
                "diagram_type": "flowchart",
                "parameters": {"title": "string"},
            }

            mock_manager = Mock()
            mock_manager.get_template.return_value = mock_template
            mock_manager_class.return_value = mock_manager

            result = get_template_info("test_template_id")

            assert result is not None
            assert result["name"] == "Test Template"
            assert result["diagram_type"] == "flowchart"
            mock_manager.get_template.assert_called_once_with("test_template_id")
