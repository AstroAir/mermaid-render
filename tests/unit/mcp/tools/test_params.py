"""
Unit tests for mcp.tools.params module.

Tests for parameter models and enums.
"""

import pytest

from diagramaid.mcp.tools.params import (
    AnalyzeDiagramParams,
    BatchRenderParams,
    CacheManagementParams,
    ConfigurationParams,
    CreateFromTemplateParams,
    DiagramTypeParams,
    FileOperationParams,
    GenerateDiagramParams,
    OptimizeDiagramParams,
    RenderDiagramParams,
    TemplateManagementParams,
    ValidateDiagramParams,
)


@pytest.mark.unit
class TestRenderDiagramParams:
    """Tests for RenderDiagramParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = RenderDiagramParams(
            diagram_code="flowchart TD\n    A --> B", output_format="svg"
        )
        assert params.diagram_code == "flowchart TD\n    A --> B"

    def test_default_output_format(self):
        """Test default output format is svg."""
        params = RenderDiagramParams(diagram_code="flowchart TD\n    A --> B")
        assert params.output_format.value == "svg"

    def test_empty_diagram_code_raises(self):
        """Test empty diagram code raises validation error."""
        with pytest.raises(ValueError):
            RenderDiagramParams(diagram_code="")

    def test_whitespace_only_diagram_code(self):
        """Test whitespace-only diagram code handling."""
        # Whitespace-only code may be accepted by pydantic but fail later
        params = RenderDiagramParams(diagram_code="   ")
        assert params.diagram_code == "   "


@pytest.mark.unit
class TestValidateDiagramParams:
    """Tests for ValidateDiagramParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = ValidateDiagramParams(diagram_code="flowchart TD\n    A --> B")
        assert params.diagram_code == "flowchart TD\n    A --> B"

    def test_empty_diagram_code_raises(self):
        """Test empty diagram code raises validation error."""
        with pytest.raises(ValueError):
            ValidateDiagramParams(diagram_code="")


@pytest.mark.unit
class TestGenerateDiagramParams:
    """Tests for GenerateDiagramParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = GenerateDiagramParams(
            text_description="A simple flowchart showing login process"
        )
        assert "login" in params.text_description.lower()

    def test_default_diagram_type(self):
        """Test default diagram type is auto."""
        params = GenerateDiagramParams(text_description="Test description")
        assert params.diagram_type == "auto"


@pytest.mark.unit
class TestOptimizeDiagramParams:
    """Tests for OptimizeDiagramParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = OptimizeDiagramParams(
            diagram_code="flowchart TD\n    A --> B", optimization_type="layout"
        )
        assert params.optimization_type == "layout"


@pytest.mark.unit
class TestAnalyzeDiagramParams:
    """Tests for AnalyzeDiagramParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = AnalyzeDiagramParams(diagram_code="flowchart TD\n    A --> B")
        assert params.include_suggestions is True  # Default

    def test_include_suggestions_false(self):
        """Test include_suggestions can be set to False."""
        params = AnalyzeDiagramParams(
            diagram_code="flowchart TD\n    A --> B", include_suggestions=False
        )
        assert params.include_suggestions is False


@pytest.mark.unit
class TestCreateFromTemplateParams:
    """Tests for CreateFromTemplateParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = CreateFromTemplateParams(
            template_name="flowchart_basic", parameters={"title": "Test"}
        )
        assert params.template_name == "flowchart_basic"
        assert params.parameters["title"] == "Test"


@pytest.mark.unit
class TestConfigurationParams:
    """Tests for ConfigurationParams model."""

    def test_valid_params_with_key(self):
        """Test valid parameter creation with key."""
        params = ConfigurationParams(key="timeout")
        assert params.key == "timeout"

    def test_valid_params_with_section(self):
        """Test valid parameter creation with section."""
        params = ConfigurationParams(section="rendering")
        assert params.section == "rendering"


@pytest.mark.unit
class TestTemplateManagementParams:
    """Tests for TemplateManagementParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = TemplateManagementParams(category="flowchart")
        assert params.category == "flowchart"

    def test_default_include_flags(self):
        """Test default include flags are True."""
        params = TemplateManagementParams()
        assert params.include_builtin is True
        assert params.include_custom is True


@pytest.mark.unit
class TestDiagramTypeParams:
    """Tests for DiagramTypeParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = DiagramTypeParams(include_examples=True)
        assert params.include_examples is True


@pytest.mark.unit
class TestFileOperationParams:
    """Tests for FileOperationParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = FileOperationParams(file_path="/path/to/file.svg")
        assert params.file_path == "/path/to/file.svg"

    def test_default_flags(self):
        """Test default flags."""
        params = FileOperationParams(file_path="/path/to/file.svg")
        assert params.create_directories is True
        assert params.overwrite is False


@pytest.mark.unit
class TestBatchRenderParams:
    """Tests for BatchRenderParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        diagrams = [{"code": "flowchart TD\n    A --> B", "format": "svg"}]
        params = BatchRenderParams(diagrams=diagrams)
        assert len(params.diagrams) == 1

    def test_default_parallel_flag(self):
        """Test default parallel flag is True."""
        diagrams = [{"code": "flowchart TD\n    A --> B", "format": "svg"}]
        params = BatchRenderParams(diagrams=diagrams)
        assert params.parallel is True


@pytest.mark.unit
class TestCacheManagementParams:
    """Tests for CacheManagementParams model."""

    def test_valid_params(self):
        """Test valid parameter creation."""
        params = CacheManagementParams(operation="stats")
        assert params.operation == "stats"

    def test_valid_operations(self):
        """Test valid cache operations."""
        for op in ["stats", "clear", "info", "cleanup"]:
            params = CacheManagementParams(operation=op)
            assert params.operation == op
