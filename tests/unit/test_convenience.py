from typing import Any

"""
Comprehensive unit tests for convenience functions.

This module tests the convenience functions quick_render and render_to_file
with various input scenarios, format detection, error handling, and edge cases.
"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from mermaid_render.convenience import quick_render, render, render_to_file
from mermaid_render.exceptions import (
    ConfigurationError,
    RenderingError,
    UnsupportedFormatError,
    ValidationError,
)


class TestQuickRender:
    """Test quick_render function."""

    def test_basic_svg_rendering(self) -> None:
        """Test basic SVG rendering without output path."""
        diagram_code = "flowchart TD\n    A --> B"
        expected_svg = '<svg xmlns="http://www.w3.org/2000/svg">test</svg>'

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = expected_svg
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(diagram_code)

            assert result == expected_svg
            mock_renderer.render_raw.assert_called_once_with(diagram_code, format="svg")

    def test_png_rendering(self) -> None:
        """Test PNG rendering."""
        diagram_code = "flowchart TD\n    A --> B"
        expected_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = expected_png
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(diagram_code, format="png")

            assert result == expected_png
            mock_renderer.render_raw.assert_called_once_with(diagram_code, format="png")

    def test_pdf_rendering(self) -> None:
        """Test PDF rendering."""
        diagram_code = "flowchart TD\n    A --> B"
        expected_pdf = b"%PDF-1.4\n1 0 obj"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = expected_pdf
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(diagram_code, format="pdf")

            assert result == expected_pdf
            mock_renderer.render_raw.assert_called_once_with(diagram_code, format="pdf")

    def test_with_theme(self) -> None:
        """Test rendering with theme."""
        diagram_code = "flowchart TD\n    A --> B"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>test</svg>"
            mock_renderer_class.return_value = mock_renderer

            quick_render(diagram_code, theme="dark")

            mock_renderer.set_theme.assert_called_once_with("dark")

    def test_with_custom_config(self) -> None:
        """Test rendering with custom configuration."""
        diagram_code = "flowchart TD\n    A --> B"
        config = {"timeout": 60, "validate_syntax": True}

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>test</svg>"
            mock_renderer_class.return_value = mock_renderer

            quick_render(diagram_code, config=config)

            # The config is passed to MermaidConfig, not directly to MermaidRenderer
            mock_renderer_class.assert_called_once()

    def test_with_output_path(self, temp_dir: Any) -> None:
        """Test rendering with output path."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"
        expected_svg = "<svg>test</svg>"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            with patch("builtins.open", mock_open()) as mock_file:
                mock_renderer = Mock()
                mock_renderer.render_raw.return_value = expected_svg
                mock_renderer_class.return_value = mock_renderer

                result = quick_render(diagram_code, output_path=output_path)

                assert result == expected_svg
                mock_file.assert_called_once_with(output_path, "w")
                # Verify render_raw was called
                mock_renderer.render_raw.assert_called_once_with(
                    diagram_code, format="svg"
                )

    def test_empty_diagram_code(self) -> None:
        """Test handling of empty diagram code."""
        with pytest.raises(ValidationError, match="Empty diagram code"):
            quick_render("")

    def test_whitespace_only_diagram_code(self) -> None:
        """Test handling of whitespace-only diagram code."""
        with pytest.raises(ValidationError, match="Empty diagram code"):
            quick_render("   \n\t  \n  ")

    def test_invalid_format(self) -> None:
        """Test handling of invalid format."""
        diagram_code = "flowchart TD\n    A --> B"

        # Use legacy mode to get direct UnsupportedFormatError
        # Plugin system wraps errors in RenderingError
        with pytest.raises((UnsupportedFormatError, RenderingError)):
            quick_render(diagram_code, format="invalid", use_plugin_system=False)

    def test_rendering_error_propagation(self) -> None:
        """Test that rendering errors are properly propagated."""
        diagram_code = "flowchart TD\n    A --> B"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            # quick_render calls render_raw, not render
            mock_renderer.render_raw.side_effect = RenderingError("Rendering failed")
            mock_renderer_class.return_value = mock_renderer

            with pytest.raises(RenderingError, match="Rendering failed"):
                quick_render(diagram_code)

    def test_configuration_error_propagation(self) -> None:
        """Test that configuration errors are properly propagated."""
        diagram_code = "flowchart TD\n    A --> B"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer_class.side_effect = ConfigurationError("Invalid config")

            with pytest.raises(ConfigurationError, match="Invalid config"):
                quick_render(diagram_code)

    def test_path_object_handling(self, temp_dir: Any) -> None:
        """Test handling of Path objects for output_path."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = Path(temp_dir) / "test.svg"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>test</svg>"
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(diagram_code, output_path=output_path)

            # Verify render_raw was called
            mock_renderer.render_raw.assert_called_once_with(diagram_code, format="svg")

            # Verify file was written
            assert output_path.exists()
            assert output_path.read_text() == "<svg>test</svg>"

            # Verify return value
            assert result == "<svg>test</svg>"

    def test_string_path_handling(self, temp_dir: Any) -> None:
        """Test handling of string paths for output_path."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = str(temp_dir / "test.svg")

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>test</svg>"
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(diagram_code, output_path=output_path)

            # Verify render_raw was called
            mock_renderer.render_raw.assert_called_once_with(diagram_code, format="svg")

            # Verify file was written
            output_path_obj = Path(output_path)
            assert output_path_obj.exists()
            assert output_path_obj.read_text() == "<svg>test</svg>"

            # Verify return value
            assert result == "<svg>test</svg>"

    def test_complex_diagram_code(self) -> None:
        """Test rendering with complex diagram code."""
        complex_diagram = """
        flowchart TD
            A[Start] --> B{Decision}
            B -->|Yes| C[Process 1]
            B -->|No| D[Process 2]
            C --> E[End]
            D --> E

            style A fill:#f9f,stroke:#333,stroke-width:4px
            style E fill:#bbf,stroke:#333,stroke-width:2px
        """

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>complex</svg>"
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(complex_diagram)

            assert result == "<svg>complex</svg>"
            mock_renderer.render_raw.assert_called_once_with(
                complex_diagram, format="svg"
            )

    def test_unicode_diagram_code(self) -> None:
        """Test rendering with Unicode characters in diagram code."""
        unicode_diagram = """
        flowchart TD
            A[开始] --> B{决定}
            B -->|是| C[处理 1]
            B -->|否| D[处理 2]
            C --> E[结束]
            D --> E
        """

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>unicode</svg>"
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(unicode_diagram)

            assert result == "<svg>unicode</svg>"
            mock_renderer.render_raw.assert_called_once_with(
                unicode_diagram, format="svg"
            )


class TestRenderToFile:
    """Test render_to_file function."""

    def test_basic_file_rendering(self, temp_dir: Any) -> None:
        """Test basic file rendering."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            result = render_to_file(diagram_code, output_path)

            assert result is True
            mock_quick_render.assert_called_once_with(
                diagram_code=diagram_code,
                format="svg",
                theme=None,
                config=None,
                output_path=output_path,
                use_plugin_system=True,
            )

    def test_format_auto_detection_svg(self, temp_dir: Any) -> None:
        """Test automatic format detection for SVG files."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            render_to_file(diagram_code, output_path)

            args, kwargs = mock_quick_render.call_args
            assert kwargs["format"] == "svg"

    def test_format_auto_detection_png(self, temp_dir: Any) -> None:
        """Test automatic format detection for PNG files."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.png"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = b"png_data"

            render_to_file(diagram_code, output_path)

            args, kwargs = mock_quick_render.call_args
            assert kwargs["format"] == "png"

    def test_format_auto_detection_pdf(self, temp_dir: Any) -> None:
        """Test automatic format detection for PDF files."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.pdf"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = b"pdf_data"

            render_to_file(diagram_code, output_path)

            args, kwargs = mock_quick_render.call_args
            assert kwargs["format"] == "pdf"

    def test_format_auto_detection_unknown_extension(self, temp_dir: Any) -> None:
        """Test format auto-detection with unknown extension defaults to SVG."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.unknown"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            render_to_file(diagram_code, output_path)

            args, kwargs = mock_quick_render.call_args
            assert kwargs["format"] == "svg"

    def test_explicit_format_override(self, temp_dir: Any) -> None:
        """Test explicit format parameter overrides auto-detection."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"  # SVG extension

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = b"png_data"

            render_to_file(diagram_code, output_path, format="png")  # Override to PNG

            args, kwargs = mock_quick_render.call_args
            assert kwargs["format"] == "png"

    def test_with_theme_parameter(self, temp_dir: Any) -> None:
        """Test render_to_file with theme parameter."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            render_to_file(diagram_code, output_path, theme="dark")

            args, kwargs = mock_quick_render.call_args
            assert kwargs["theme"] == "dark"

    def test_with_config_parameter(self, temp_dir: Any) -> None:
        """Test render_to_file with config parameter."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"
        config = {"timeout": 60}

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            render_to_file(diagram_code, output_path, config=config)

            args, kwargs = mock_quick_render.call_args
            assert kwargs["config"] == config

    def test_exception_handling_returns_false(self, temp_dir: Any) -> None:
        """Test that exceptions are caught and False is returned."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.side_effect = RenderingError("Rendering failed")

            result = render_to_file(diagram_code, output_path)

            assert result is False

    def test_string_path_conversion(self, temp_dir: Any) -> None:
        """Test conversion of string paths to Path objects."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = str(temp_dir / "test.svg")

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            render_to_file(diagram_code, output_path)

            args, kwargs = mock_quick_render.call_args
            assert kwargs["output_path"] == output_path

    def test_case_insensitive_extension(self, temp_dir: Any) -> None:
        """Test case-insensitive file extension handling."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.SVG"  # Uppercase extension

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            render_to_file(diagram_code, output_path)

            args, kwargs = mock_quick_render.call_args
            assert kwargs["format"] == "svg"


class TestBackwardCompatibility:
    """Test backward compatibility features."""

    def test_render_alias(self) -> None:
        """Test that render is an alias for quick_render."""
        from mermaid_render.convenience import quick_render, render

        assert render is quick_render

    def test_render_alias_functionality(self) -> None:
        """Test that render alias works identically to quick_render."""
        diagram_code = "flowchart TD\n    A --> B"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>test</svg>"
            mock_renderer_class.return_value = mock_renderer

            result = render(diagram_code)

            assert result == "<svg>test</svg>"
            mock_renderer.render_raw.assert_called_once_with(diagram_code, format="svg")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_diagram_code(self) -> None:
        """Test handling of very long diagram code."""
        # Create a very long diagram with many nodes
        nodes = [
            f"    {chr(65+i)} --> {chr(65+i+1)}" for i in range(25)
        ]  # A->B, B->C, etc.
        long_diagram = "flowchart TD\n" + "\n".join(nodes)

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>long</svg>"
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(long_diagram)

            assert result == "<svg>long</svg>"
            mock_renderer.render_raw.assert_called_once_with(long_diagram, format="svg")

    def test_special_characters_in_path(self, temp_dir: Any) -> None:
        """Test handling of special characters in file paths."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test with spaces & symbols!.svg"

        with patch("mermaid_render.convenience.quick_render") as mock_quick_render:
            mock_quick_render.return_value = "<svg>test</svg>"

            result = render_to_file(diagram_code, output_path)

            assert result is True
            mock_quick_render.assert_called_once()

    def test_none_values_handling(self) -> None:
        """Test handling of None values for optional parameters."""
        diagram_code = "flowchart TD\n    A --> B"

        with patch("mermaid_render.convenience.MermaidRenderer") as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render_raw.return_value = "<svg>test</svg>"
            mock_renderer_class.return_value = mock_renderer

            result = quick_render(diagram_code, theme=None, config=None)

            assert result == "<svg>test</svg>"
            # The convenience function creates a MermaidConfig even when config=None
            mock_renderer_class.assert_called_once()
            # Verify that set_theme is not called when theme=None
            mock_renderer.set_theme.assert_not_called()
