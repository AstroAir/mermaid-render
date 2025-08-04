"""
Unit tests for exception classes.
"""

import pytest

from mermaid_render.exceptions import (
    MermaidRenderError,
    ValidationError,
    RenderingError,
    ConfigurationError,
    UnsupportedFormatError,
    NetworkError,
    ThemeError,
    DiagramError,
    TemplateError,
    DataSourceError,
    CacheError,
)


class TestMermaidRenderError:
    """Test base MermaidRenderError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = MermaidRenderError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details is None

    def test_error_with_details(self):
        """Test error with additional details."""
        details = {"code": 500, "context": "test"}
        error = MermaidRenderError("Test error", details=details)

        assert error.message == "Test error"
        assert error.details == details
        assert "Details: " in str(error)

    def test_error_inheritance(self):
        """Test that error inherits from Exception."""
        error = MermaidRenderError("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, MermaidRenderError)


class TestValidationError:
    """Test ValidationError class."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Invalid syntax")

        assert str(error) == "Invalid syntax"
        assert error.line_number is None
        assert error.errors == []

    def test_validation_error_with_line_number(self):
        """Test validation error with line number."""
        error = ValidationError("Invalid syntax", line_number=5)

        assert error.line_number == 5
        assert "Line 5" in str(error)

    def test_validation_error_with_errors_list(self):
        """Test validation error with multiple errors."""
        errors = ["Missing node", "Invalid arrow"]
        error = ValidationError("Multiple errors", errors=errors)

        assert error.errors == errors
        assert "Missing node" in str(error)
        assert "Invalid arrow" in str(error)

    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance."""
        error = ValidationError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, ValidationError)


class TestRenderingError:
    """Test RenderingError class."""

    def test_basic_rendering_error(self):
        """Test basic rendering error."""
        error = RenderingError("Rendering failed")

        assert str(error) == "Rendering failed"
        assert error.format is None
        assert error.status_code is None

    def test_rendering_error_with_format(self):
        """Test rendering error with format."""
        error = RenderingError("Rendering failed", format="svg")

        assert error.format == "svg"
        assert "svg" in str(error)

    def test_rendering_error_with_status_code(self):
        """Test rendering error with HTTP status code."""
        error = RenderingError("Server error", status_code=500)

        assert error.status_code == 500
        assert "500" in str(error)

    def test_rendering_error_complete(self):
        """Test rendering error with all parameters."""
        error = RenderingError("Request failed", format="svg", status_code=500)

        assert error.format == "svg"
        assert error.status_code == 500
        assert "svg" in str(error)
        assert "500" in str(error)

    def test_rendering_error_inheritance(self):
        """Test RenderingError inheritance."""
        error = RenderingError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, RenderingError)


class TestConfigurationError:
    """Test ConfigurationError class."""

    def test_basic_configuration_error(self):
        """Test basic configuration error."""
        error = ConfigurationError("Invalid config")

        assert str(error) == "Invalid config"
        assert error.config_key is None
        assert error.expected_type is None

    def test_configuration_error_with_key(self):
        """Test configuration error with config key."""
        error = ConfigurationError("Invalid value", config_key="timeout")

        assert error.config_key == "timeout"
        assert "timeout" in str(error)

    def test_configuration_error_with_expected_type(self):
        """Test configuration error with expected type."""
        error = ConfigurationError("Type mismatch", expected_type=int)

        assert error.expected_type == int
        assert "int" in str(error)

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inheritance."""
        error = ConfigurationError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, ConfigurationError)


class TestUnsupportedFormatError:
    """Test UnsupportedFormatError class."""

    def test_basic_unsupported_format_error(self):
        """Test basic unsupported format error."""
        error = UnsupportedFormatError("Format not supported")

        assert str(error) == "Format not supported"
        assert error.requested_format is None
        assert error.supported_formats == []

    def test_unsupported_format_error_with_format(self):
        """Test unsupported format error with format."""
        error = UnsupportedFormatError("Format not supported", requested_format="gif")

        assert error.requested_format == "gif"
        assert "gif" in str(error)

    def test_unsupported_format_error_with_supported_formats(self):
        """Test unsupported format error with supported formats list."""
        supported = ["svg", "png", "pdf"]
        error = UnsupportedFormatError(
            "Format not supported", supported_formats=supported)

        assert error.supported_formats == supported
        assert "svg" in str(error)
        assert "png" in str(error)
        assert "pdf" in str(error)

    def test_unsupported_format_error_inheritance(self):
        """Test UnsupportedFormatError inheritance."""
        error = UnsupportedFormatError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, UnsupportedFormatError)


class TestNetworkError:
    """Test NetworkError class."""

    def test_basic_network_error(self):
        """Test basic network error."""
        error = NetworkError("Network failed")

        assert str(error) == "Network failed"
        assert error.url is None
        assert error.timeout is None

    def test_network_error_with_url(self):
        """Test network error with URL."""
        url = "https://mermaid.ink/svg/abc123"
        error = NetworkError("Request failed", url=url)

        assert error.url == url
        assert url in str(error)

    def test_network_error_with_timeout(self):
        """Test network error with timeout."""
        error = NetworkError("Request timeout", timeout=30.0)

        assert error.timeout == 30.0
        assert "30.0" in str(error)

    def test_network_error_inheritance(self):
        """Test NetworkError inheritance."""
        error = NetworkError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, NetworkError)


class TestThemeError:
    """Test ThemeError class."""

    def test_basic_theme_error(self):
        """Test basic theme error."""
        error = ThemeError("Theme not found")

        assert str(error) == "Theme not found"
        assert error.theme_name is None
        assert error.available_themes == []

    def test_theme_error_with_theme_name(self):
        """Test theme error with theme name."""
        error = ThemeError("Theme not found", theme_name="custom")

        assert error.theme_name == "custom"
        assert "custom" in str(error)

    def test_theme_error_with_available_themes(self):
        """Test theme error with available themes list."""
        themes = ["default", "dark", "forest"]
        error = ThemeError("Theme not found", available_themes=themes)

        assert error.available_themes == themes
        assert "default" in str(error)
        assert "dark" in str(error)
        assert "forest" in str(error)

    def test_theme_error_inheritance(self):
        """Test ThemeError inheritance."""
        error = ThemeError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, ThemeError)


class TestDiagramError:
    """Test DiagramError class."""

    def test_basic_diagram_error(self):
        """Test basic diagram error."""
        error = DiagramError("Diagram construction failed")

        assert str(error) == "Diagram construction failed"
        assert error.diagram_type is None
        assert error.element is None

    def test_diagram_error_with_type(self):
        """Test diagram error with diagram type."""
        error = DiagramError("Invalid diagram", diagram_type="flowchart")

        assert error.diagram_type == "flowchart"
        assert "flowchart" in str(error)

    def test_diagram_error_with_element(self):
        """Test diagram error with element."""
        error = DiagramError("Invalid element", element="node_a")

        assert error.element == "node_a"
        assert "node_a" in str(error)

    def test_diagram_error_inheritance(self):
        """Test DiagramError inheritance."""
        error = DiagramError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, DiagramError)


class TestTemplateError:
    """Test TemplateError class."""

    def test_basic_template_error(self):
        """Test basic template error."""
        error = TemplateError("Template not found")

        assert str(error) == "Template not found"
        assert error.template_name is None
        assert error.parameter is None

    def test_template_error_with_name(self):
        """Test template error with template name."""
        error = TemplateError("Template not found", template_name="flowchart_basic")

        assert error.template_name == "flowchart_basic"
        assert "flowchart_basic" in str(error)

    def test_template_error_with_parameter(self):
        """Test template error with parameter."""
        error = TemplateError("Invalid parameter", parameter="steps")

        assert error.parameter == "steps"
        assert "steps" in str(error)

    def test_template_error_inheritance(self):
        """Test TemplateError inheritance."""
        error = TemplateError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, TemplateError)


class TestDataSourceError:
    """Test DataSourceError class."""

    def test_basic_data_source_error(self):
        """Test basic data source error."""
        error = DataSourceError("Data source failed")

        assert str(error) == "Data source failed"
        assert error.source_type is None
        assert error.source_location is None

    def test_data_source_error_with_type(self):
        """Test data source error with source type."""
        error = DataSourceError("Connection failed", source_type="database")

        assert error.source_type == "database"
        assert "database" in str(error)

    def test_data_source_error_with_location(self):
        """Test data source error with source location."""
        location = "postgresql://localhost:5432/mydb"
        error = DataSourceError("Connection failed", source_location=location)

        assert error.source_location == location
        assert location in str(error)

    def test_data_source_error_inheritance(self):
        """Test DataSourceError inheritance."""
        error = DataSourceError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, DataSourceError)


class TestCacheError:
    """Test CacheError class."""

    def test_basic_cache_error(self):
        """Test basic cache error."""
        error = CacheError("Cache operation failed")

        assert str(error) == "Cache operation failed"
        assert error.cache_backend is None
        assert error.cache_key is None

    def test_cache_error_with_backend(self):
        """Test cache error with cache backend."""
        error = CacheError("Backend failed", cache_backend="redis")

        assert error.cache_backend == "redis"
        assert "redis" in str(error)

    def test_cache_error_with_key(self):
        """Test cache error with cache key."""
        error = CacheError("Key operation failed", cache_key="diagram_abc123")

        assert error.cache_key == "diagram_abc123"
        assert "diagram_abc123" in str(error)

    def test_cache_error_inheritance(self):
        """Test CacheError inheritance."""
        error = CacheError("Test error")

        assert isinstance(error, MermaidRenderError)
        assert isinstance(error, CacheError)


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from MermaidRenderError."""
        exception_classes = [
            ValidationError,
            RenderingError,
            ConfigurationError,
            UnsupportedFormatError,
            NetworkError,
            ThemeError,
            DiagramError,
            TemplateError,
            DataSourceError,
            CacheError,
        ]

        for exc_class in exception_classes:
            error = exc_class("Test error")
            assert isinstance(error, MermaidRenderError)
            assert isinstance(error, Exception)

    def test_exception_catching(self):
        """Test that specific exceptions can be caught by base class."""
        try:
            raise ValidationError("Test validation error")
        except MermaidRenderError as e:
            assert isinstance(e, ValidationError)
            assert isinstance(e, MermaidRenderError)

    def test_exception_details_preservation(self):
        """Test that exception details are preserved through inheritance."""
        try:
            raise RenderingError("Test error", format="svg", status_code=500)
        except MermaidRenderError as e:
            assert e.message == "Test error"
            assert hasattr(e, 'format')
            assert hasattr(e, 'status_code')
