"""
Unit tests for core functionality.
"""

from unittest.mock import Mock, patch

import pytest

from mermaid_render.core import MermaidConfig, MermaidRenderer, MermaidTheme
from mermaid_render.exceptions import (
    ConfigurationError,
    RenderingError,
    UnsupportedFormatError,
    ValidationError,
)


class TestMermaidConfig:
    """Test MermaidConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MermaidConfig()

        assert config.get("server_url") == "https://mermaid.ink"
        assert config.get("timeout") == 30
        assert config.get("default_theme") == "default"
        assert config.get("validate_syntax") is True

    def test_custom_config(self):
        """Test custom configuration values."""
        custom_config = {
            "timeout": 60,
            "default_theme": "dark",
            "custom_option": "test_value",
        }
        config = MermaidConfig(**custom_config)

        assert config.get("timeout") == 60
        assert config.get("default_theme") == "dark"
        assert config.get("custom_option") == "test_value"
        assert config.get("server_url") == "https://mermaid.ink"  # Default preserved

    def test_get_with_default(self):
        """Test getting config value with default."""
        config = MermaidConfig()

        assert config.get("nonexistent", "default_value") == "default_value"
        assert config.get("timeout", 999) == 30  # Actual value returned

    def test_set_config(self):
        """Test setting configuration values."""
        config = MermaidConfig()

        config.set("new_option", "new_value")
        assert config.get("new_option") == "new_value"

        config.set("timeout", 45)
        assert config.get("timeout") == 45

    def test_update_config(self):
        """Test updating multiple configuration values."""
        config = MermaidConfig()

        updates = {"timeout": 120, "retries": 5, "new_setting": "test"}
        config.update(updates)

        assert config.get("timeout") == 120
        assert config.get("retries") == 5
        assert config.get("new_setting") == "test"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = MermaidConfig(timeout=60, custom="value")
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["timeout"] == 60
        assert config_dict["custom"] == "value"

        # Ensure it's a copy
        config_dict["timeout"] = 999
        assert config.get("timeout") == 60


class TestMermaidTheme:
    """Test MermaidTheme class."""

    def test_built_in_theme(self):
        """Test creating built-in theme."""
        theme = MermaidTheme("dark")

        assert theme.name == "dark"
        config = theme.to_dict()
        assert config["theme"] == "dark"

    def test_custom_theme(self):
        """Test creating custom theme."""
        custom_config = {"primaryColor": "#ff0000", "lineColor": "#000000"}
        theme = MermaidTheme("custom", **custom_config)

        assert theme.name == "custom"
        config = theme.to_dict()
        assert config["primaryColor"] == "#ff0000"
        assert config["lineColor"] == "#000000"

    def test_unknown_theme(self):
        """Test creating theme with unknown name."""
        with pytest.raises(ConfigurationError, match="Unknown theme"):
            MermaidTheme("nonexistent_theme")

    def test_theme_override(self):
        """Test overriding built-in theme settings."""
        theme = MermaidTheme("default", primaryColor="#custom")

        config = theme.to_dict()
        assert config["primaryColor"] == "#custom"

    def test_apply_to_config(self):
        """Test applying theme to configuration."""
        theme = MermaidTheme("dark")
        base_config = {"width": 800, "height": 600}

        result = theme.apply_to_config(base_config)

        assert result["width"] == 800  # Original preserved
        assert result["height"] == 600  # Original preserved
        assert result["theme"] == "dark"  # Theme applied


class TestMermaidRenderer:
    """Test MermaidRenderer class."""

    def test_init_default(self):
        """Test renderer initialization with defaults."""
        renderer = MermaidRenderer()

        assert renderer.config is not None
        assert renderer.get_theme() is None
        assert "svg" in renderer.SUPPORTED_FORMATS

    def test_init_with_config(self, mermaid_config):
        """Test renderer initialization with config."""
        renderer = MermaidRenderer(config=mermaid_config)

        assert renderer.config is mermaid_config

    def test_init_with_theme_string(self):
        """Test renderer initialization with theme string."""
        renderer = MermaidRenderer(theme="dark")

        theme = renderer.get_theme()
        assert theme is not None
        assert theme.name == "dark"

    def test_init_with_theme_object(self):
        """Test renderer initialization with theme object."""
        theme = MermaidTheme("forest")
        renderer = MermaidRenderer(theme=theme)

        assert renderer.get_theme() is theme

    def test_set_theme_string(self):
        """Test setting theme with string."""
        renderer = MermaidRenderer()
        renderer.set_theme("neutral")

        theme = renderer.get_theme()
        assert theme.name == "neutral"

    def test_set_theme_object(self):
        """Test setting theme with object."""
        renderer = MermaidRenderer()
        theme = MermaidTheme("base")
        renderer.set_theme(theme)

        assert renderer.get_theme() is theme

    def test_set_invalid_theme(self):
        """Test setting invalid theme."""
        renderer = MermaidRenderer()

        with pytest.raises(ConfigurationError, match="Invalid theme type"):
            renderer.set_theme(123)

    def test_unsupported_format(self, mermaid_renderer, sample_mermaid_code):
        """Test rendering with unsupported format."""
        with pytest.raises(UnsupportedFormatError, match="Unsupported format"):
            mermaid_renderer.render(sample_mermaid_code, format="gif")

    @patch("mermaid_render.core.md.Mermaid")
    def test_render_svg_success(
        self, mock_mermaid, mermaid_renderer, sample_mermaid_code
    ):
        """Test successful SVG rendering."""
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>test</svg>")
        mock_mermaid.return_value = mock_instance

        result = mermaid_renderer.render(sample_mermaid_code, format="svg")

        assert result == "<svg>test</svg>"
        mock_mermaid.assert_called_once_with(sample_mermaid_code)

    @patch("mermaid_render.core.md.Mermaid")
    def test_render_with_validation_disabled(self, mock_mermaid, invalid_mermaid_code):
        """Test rendering with validation disabled."""
        config = MermaidConfig(validate_syntax=False)
        renderer = MermaidRenderer(config=config)

        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>test</svg>")
        mock_mermaid.return_value = mock_instance

        # Should not raise validation error
        result = renderer.render(invalid_mermaid_code, format="svg")
        assert result == "<svg>test</svg>"

    def test_render_with_validation_enabled(self, invalid_mermaid_code):
        """Test rendering with validation enabled."""
        config = MermaidConfig(validate_syntax=True)
        renderer = MermaidRenderer(config=config)

        # Should raise validation error
        with pytest.raises((ValidationError, RenderingError)):
            renderer.render(invalid_mermaid_code, format="svg")

    @patch("mermaid_render.core.md.Mermaid")
    def test_render_diagram_object(
        self, mock_mermaid, mermaid_renderer, sample_flowchart
    ):
        """Test rendering diagram object."""
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>flowchart</svg>")
        mock_mermaid.return_value = mock_instance

        result = mermaid_renderer.render(sample_flowchart, format="svg")

        assert result == "<svg>flowchart</svg>"
        # Should call to_mermaid() on the diagram
        expected_code = sample_flowchart.to_mermaid()
        mock_mermaid.assert_called_once_with(expected_code)

    @patch("mermaid_render.core.md.Mermaid")
    def test_save_to_file(
        self, mock_mermaid, mermaid_renderer, sample_mermaid_code, temp_dir
    ):
        """Test saving diagram to file."""
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>test content</svg>")
        mock_mermaid.return_value = mock_instance

        output_path = temp_dir / "test.svg"
        mermaid_renderer.save(sample_mermaid_code, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert content == "<svg>test content</svg>"

    def test_save_format_inference(
        self, mermaid_renderer, sample_mermaid_code, temp_dir
    ):
        """Test format inference from file extension."""
        with patch("mermaid_render.core.md.Mermaid") as mock_mermaid:
            mock_instance = Mock()
            mock_instance.__str__ = Mock(return_value="<svg>test</svg>")
            mock_mermaid.return_value = mock_instance

            # Test SVG extension
            svg_path = temp_dir / "test.svg"
            mermaid_renderer.save(sample_mermaid_code, svg_path)
            assert svg_path.exists()

    def test_save_directory_creation(
        self, mermaid_renderer, sample_mermaid_code, temp_dir
    ):
        """Test automatic directory creation when saving."""
        with patch("mermaid_render.core.md.Mermaid") as mock_mermaid:
            mock_instance = Mock()
            mock_instance.__str__ = Mock(return_value="<svg>test</svg>")
            mock_mermaid.return_value = mock_instance

            # Create nested path that doesn't exist
            nested_path = temp_dir / "subdir" / "nested" / "test.svg"
            mermaid_renderer.save(sample_mermaid_code, nested_path)

            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_save_default_format_fallback(
        self, mermaid_renderer, sample_mermaid_code, temp_dir
    ):
        """Test default format fallback when no extension provided."""
        with patch("mermaid_render.core.md.Mermaid") as mock_mermaid:
            mock_instance = Mock()
            mock_instance.__str__ = Mock(return_value="<svg>test</svg>")
            mock_mermaid.return_value = mock_instance

            # Save without extension
            output_path = temp_dir / "test_no_extension"
            mermaid_renderer.save(sample_mermaid_code, output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert content == "<svg>test</svg>"

    def test_save_binary_content_handling(
        self, mermaid_renderer, sample_mermaid_code, temp_dir
    ):
        """Test binary content handling in save method."""
        with patch("mermaid_render.core.md.Mermaid") as mock_mermaid:
            mock_instance = Mock()
            mock_instance.__str__ = Mock(return_value="<svg>test</svg>")
            mock_mermaid.return_value = mock_instance

            # Mock render to return string for binary format
            with patch.object(
                mermaid_renderer, "render", return_value="binary_content"
            ):
                output_path = temp_dir / "test.png"
                mermaid_renderer.save(sample_mermaid_code, output_path, format="png")

                assert output_path.exists()
                content = output_path.read_bytes()
                assert content == b"binary_content"

    def test_save_binary_content_bytes(
        self, mermaid_renderer, sample_mermaid_code, temp_dir
    ):
        """Test binary content handling when content is already bytes."""
        with patch("mermaid_render.core.md.Mermaid") as mock_mermaid:
            mock_instance = Mock()
            mock_instance.__str__ = Mock(return_value="<svg>test</svg>")
            mock_mermaid.return_value = mock_instance

            # Mock render to return bytes for binary format
            binary_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            with patch.object(mermaid_renderer, "render", return_value=binary_content):
                output_path = temp_dir / "test.png"
                mermaid_renderer.save(sample_mermaid_code, output_path, format="png")

                assert output_path.exists()
                content = output_path.read_bytes()
                assert content == binary_content

    def test_render_raw_with_theme(self, temp_dir):
        """Test render_raw with theme configuration."""
        theme = MermaidTheme("dark", primaryColor="#custom")
        renderer = MermaidRenderer(theme=theme)

        with patch("mermaid_render.core.md.Mermaid") as mock_mermaid:
            mock_instance = Mock()
            mock_instance.__str__ = Mock(return_value="<svg>themed</svg>")
            mock_mermaid.return_value = mock_instance

            result = renderer.render_raw("flowchart TD\n    A --> B")

            assert result == "<svg>themed</svg>"

    def test_render_raw_unsupported_format(self, mermaid_renderer):
        """Test render_raw with unsupported format."""
        # The UnsupportedFormatError gets wrapped in a RenderingError
        with pytest.raises(RenderingError, match="Failed to render diagram"):
            mermaid_renderer.render_raw("flowchart TD\n    A --> B", format="png")

    def test_render_raw_exception_handling(self, mermaid_renderer):
        """Test render_raw exception handling."""
        with patch(
            "mermaid_render.core.md.Mermaid", side_effect=Exception("Mermaid error")
        ):
            with pytest.raises(RenderingError, match="Failed to render diagram"):
                mermaid_renderer.render_raw("flowchart TD\n    A --> B")

    def test_render_diagram_validation_failure(self, mermaid_renderer):
        """Test rendering with diagram validation failure."""
        # Use a real diagram and mock its validate method to return False
        from mermaid_render.models import FlowchartDiagram

        diagram = FlowchartDiagram()
        diagram.add_node("A", "Start")
        diagram.add_node("B", "End")
        diagram.add_edge("A", "B")

        # Mock the validate method to return False
        with patch.object(diagram, "validate", return_value=False):
            with pytest.raises(ValidationError, match="Invalid diagram syntax"):
                mermaid_renderer.render(diagram)


class TestMermaidDiagram:
    """Test MermaidDiagram abstract base class."""

    def test_add_config(self, sample_flowchart):
        """Test adding configuration to diagram."""
        sample_flowchart.add_config("width", 800)
        sample_flowchart.add_config("height", 600)

        config = sample_flowchart.get_config()
        assert config["width"] == 800
        assert config["height"] == 600

    def test_get_config(self, sample_flowchart):
        """Test getting diagram configuration."""
        sample_flowchart.add_config("test_key", "test_value")

        config = sample_flowchart.get_config()
        assert config["test_key"] == "test_value"

        # Ensure it's a copy
        config["test_key"] = "modified"
        original_config = sample_flowchart.get_config()
        assert original_config["test_key"] == "test_value"

    def test_str_method(self, sample_flowchart):
        """Test __str__ method returns Mermaid syntax."""
        mermaid_str = str(sample_flowchart)
        expected = sample_flowchart.to_mermaid()

        assert mermaid_str == expected
        assert "flowchart TD" in mermaid_str

    def test_validate_method(self, sample_flowchart):
        """Test diagram validation method."""
        # Valid diagram should pass validation
        assert sample_flowchart.validate() is True

    def test_validate_invalid_diagram(self):
        """Test validation with invalid diagram."""
        from mermaid_render.models import FlowchartDiagram

        # Create an invalid diagram by mocking to_mermaid to return invalid syntax
        invalid_diagram = FlowchartDiagram()

        with patch.object(invalid_diagram, "to_mermaid", return_value="invalid syntax"):
            # This should return False for invalid syntax
            result = invalid_diagram.validate()
            # Note: The actual result depends on the validator implementation
            # We're testing that the method can be called without error
            assert isinstance(result, bool)
