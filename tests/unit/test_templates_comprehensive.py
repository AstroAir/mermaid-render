"""
Comprehensive tests for the template system.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import json
import tempfile

from mermaid_render.templates import (
    TemplateManager,
    Template,
    FlowchartGenerator,
    SequenceGenerator,
    ClassDiagramGenerator,
    ArchitectureGenerator,
    ProcessFlowGenerator,
)
from mermaid_render.templates.data_sources import (
    DataSource,
    JSONDataSource,
    CSVDataSource,
    DatabaseDataSource,
    APIDataSource,
)
from mermaid_render.templates.schema import TemplateSchema, validate_template
from mermaid_render.exceptions import TemplateError, DataSourceError


class TestTemplateManager:
    """Test TemplateManager functionality."""

    def test_template_manager_initialization(self):
        """Test TemplateManager initialization."""
        manager = TemplateManager()
        assert manager is not None
        assert hasattr(manager, '_templates')

    def test_create_template(self):
        """Test creating a template."""
        manager = TemplateManager()

        template = manager.create_template(
            name="test_template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{title}}",
            parameters={"title": {"type": "string"}},
            description="Test template"
        )

        assert template.name == "test_template"
        assert template.description == "Test template"
        assert template.diagram_type == "flowchart"

    def test_get_template(self):
        """Test getting a template."""
        manager = TemplateManager()

        # Create a template first
        template = manager.create_template(
            name="custom_template",
            diagram_type="flowchart",
            template_content="flowchart TD\n    A --> B",
            parameters={"title": {"type": "string"}},
            description="Custom template"
        )

        # Retrieve it
        retrieved = manager.get_template(template.id)
        assert retrieved is not None
        assert retrieved.name == "custom_template"

    def test_generate_from_template(self):
        """Test generating diagram from template."""
        manager = TemplateManager()

        template = manager.create_template(
            name="simple_flowchart",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{start}} --> {{end}}",
            parameters={
                "start": {"type": "string"},
                "end": {"type": "string"}
            },
            description="Simple flowchart"
        )

        data = {"start": "Begin", "end": "Finish"}
        result = manager.generate(template.id, data)

        assert "Begin" in result
        assert "Finish" in result
        assert "flowchart TD" in result

    def test_template_validation(self):
        """Test template validation."""
        manager = TemplateManager()

        template = Template(
            name="validated_template",
            description="Template with validation",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{title}}",
            schema={
                "properties": {
                    "title": {"type": "string", "minLength": 1}
                },
                "required": ["title"]
            }
        )

        manager.register_template(template)

        # Valid data should work
        valid_data = {"title": "Valid Title"}
        result = manager.generate_from_template("validated_template", valid_data)
        assert "Valid Title" in result

        # Invalid data should raise error
        with pytest.raises(TemplateError):
            invalid_data = {"title": ""}  # Empty string violates minLength
            manager.generate_from_template("validated_template", invalid_data)


class TestTemplate:
    """Test Template class functionality."""

    def test_template_creation(self):
        """Test template creation."""
        template = Template(
            name="test_template",
            description="Test description",
            diagram_type="sequence",
            template_content="sequenceDiagram\n    A->>B: {{message}}",
            schema={"properties": {"message": {"type": "string"}}}
        )

        assert template.name == "test_template"
        assert template.description == "Test description"
        assert template.diagram_type == "sequence"
        assert "{{message}}" in template.template_content

    def test_template_rendering(self):
        """Test template rendering with data."""
        template = Template(
            name="render_test",
            description="Render test",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{node1}} --> {{node2}}",
            schema={}
        )

        data = {"node1": "Start", "node2": "End"}
        result = template.render(data)

        assert "Start" in result
        assert "End" in result
        assert "flowchart TD" in result

    def test_template_validation_schema(self):
        """Test template schema validation."""
        schema = {
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer", "minimum": 1}
            },
            "required": ["name"]
        }

        template = Template(
            name="validation_test",
            description="Validation test",
            diagram_type="flowchart",
            template_content="flowchart TD\n    {{name}}",
            schema=schema
        )

        # Valid data
        valid_data = {"name": "TestNode", "count": 5}
        assert template.validate_data(valid_data) is True

        # Invalid data - missing required field
        invalid_data = {"count": 5}
        assert template.validate_data(invalid_data) is False

        # Invalid data - wrong type
        invalid_data2 = {"name": "TestNode", "count": "not_a_number"}
        assert template.validate_data(invalid_data2) is False


class TestDataSources:
    """Test data source implementations."""

    def test_json_data_source(self):
        """Test JSON data source."""
        test_data = {"nodes": ["A", "B", "C"], "title": "Test Diagram"}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            source = JSONDataSource(temp_path)
            data = source.load()

            assert data["title"] == "Test Diagram"
            assert len(data["nodes"]) == 3
            assert "A" in data["nodes"]
        finally:
            Path(temp_path).unlink()

    def test_csv_data_source(self):
        """Test CSV data source."""
        csv_content = "name,type,description\nNode A,start,Starting point\nNode B,process,Main process\nNode C,end,End point"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            source = CSVDataSource(temp_path)
            data = source.load()

            assert isinstance(data, list)
            assert len(data) == 3
            assert data[0]["name"] == "Node A"
            assert data[0]["type"] == "start"
        finally:
            Path(temp_path).unlink()

    @patch('mermaid_render.templates.data_sources.requests.get')
    def test_api_data_source(self, mock_get):
        """Test API data source."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success", "data": {"nodes": ["A", "B"]}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        source = APIDataSource("https://api.example.com/data")
        data = source.load()

        assert data["status"] == "success"
        assert "nodes" in data["data"]
        mock_get.assert_called_once_with(
            "https://api.example.com/data", headers=None, params=None)

    def test_data_source_error_handling(self):
        """Test data source error handling."""
        # Test with non-existent file
        with pytest.raises(DataSourceError):
            source = JSONDataSource("/non/existent/file.json")
            source.load()


class TestTemplateGenerators:
    """Test template generator classes."""

    def test_flowchart_generator(self):
        """Test FlowchartGenerator."""
        generator = FlowchartGenerator()

        data = {
            "title": "Process Flow",
            "nodes": [
                {"id": "start", "label": "Start", "type": "circle"},
                {"id": "process", "label": "Process", "type": "rectangle"},
                {"id": "end", "label": "End", "type": "circle"}
            ],
            "edges": [
                {"from": "start", "to": "process", "label": "Begin"},
                {"from": "process", "to": "end", "label": "Complete"}
            ]
        }

        result = generator.generate(data)

        assert "flowchart" in result
        assert "Start" in result
        assert "Process" in result
        assert "End" in result

    def test_sequence_generator(self):
        """Test SequenceGenerator."""
        generator = SequenceGenerator()

        data = {
            "title": "API Call Sequence",
            "participants": ["Client", "Server", "Database"],
            "messages": [
                {"from": "Client", "to": "Server", "message": "Request", "type": "sync"},
                {"from": "Server", "to": "Database", "message": "Query", "type": "sync"},
                {"from": "Database", "to": "Server", "message": "Result", "type": "return"},
                {"from": "Server", "to": "Client", "message": "Response", "type": "return"}
            ]
        }

        result = generator.generate(data)

        assert "sequenceDiagram" in result
        assert "Client" in result
        assert "Server" in result
        assert "Database" in result

    def test_class_diagram_generator(self):
        """Test ClassDiagramGenerator."""
        generator = ClassDiagramGenerator()

        data = {
            "title": "Class Hierarchy",
            "classes": [
                {
                    "name": "Animal",
                    "type": "abstract",
                    "attributes": ["name: String", "age: int"],
                    "methods": ["move(): void", "eat(): void"]
                },
                {
                    "name": "Dog",
                    "type": "class",
                    "attributes": ["breed: String"],
                    "methods": ["bark(): void"]
                }
            ],
            "relationships": [
                {"from": "Dog", "to": "Animal", "type": "inheritance"}
            ]
        }

        result = generator.generate(data)

        assert "classDiagram" in result
        assert "Animal" in result
        assert "Dog" in result

    def test_architecture_generator(self):
        """Test ArchitectureGenerator."""
        generator = ArchitectureGenerator()

        data = {
            "title": "System Architecture",
            "components": [
                {"name": "Frontend", "type": "web"},
                {"name": "Backend", "type": "api"},
                {"name": "Database", "type": "storage"}
            ],
            "connections": [
                {"from": "Frontend", "to": "Backend", "protocol": "HTTP"},
                {"from": "Backend", "to": "Database", "protocol": "SQL"}
            ]
        }

        result = generator.generate(data)

        assert "Frontend" in result
        assert "Backend" in result
        assert "Database" in result


class TestTemplateSchema:
    """Test template schema validation."""

    def test_template_validation(self):
        """Test template validation."""
        # Valid template data
        valid_template_data = {
            "name": "test_template",
            "diagram_type": "flowchart",
            "template_content": "flowchart TD\n    {{title}}",
            "parameters": {
                "title": {"type": "string", "required": True}
            }
        }

        # Should not raise an exception
        try:
            validate_template(valid_template_data)
            validation_passed = True
        except Exception:
            validation_passed = False

        assert validation_passed is True

        # Invalid template data - missing required field
        invalid_template_data = {
            "name": "test_template",
            "diagram_type": "flowchart",
            # Missing template_content
            "parameters": {}
        }

        with pytest.raises(Exception):  # Should raise ValidationError
            validate_template(invalid_template_data)

    def test_template_schema_creation(self):
        """Test TemplateSchema creation and validation."""
        from mermaid_render.templates.schema import ParameterSchema, ParameterType

        # Create parameter schemas
        title_param = ParameterSchema(
            name="title",
            type=ParameterType.STRING,
            description="Diagram title",
            required=True
        )

        nodes_param = ParameterSchema(
            name="nodes",
            type=ParameterType.LIST,
            description="List of nodes",
            required=True
        )

        # Create template schema
        schema = TemplateSchema(
            name="test_template",
            version="1.0",
            diagram_type="flowchart",
            description="Test template",
            parameters=[title_param, nodes_param],
            template_content="flowchart TD\n    {{title}}"
        )

        # Validate schema
        errors = schema.validate()
        assert len(errors) == 0  # Should be valid
