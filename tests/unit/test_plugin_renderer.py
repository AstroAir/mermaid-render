from typing import Any

"""
Tests for the PluginMermaidRenderer.

This module tests the plugin-based renderer that integrates the plugin-based
architecture with the existing MermaidRenderer interface.
"""

from unittest.mock import Mock, patch

import pytest

from mermaid_render.core import MermaidConfig, MermaidTheme
from mermaid_render.exceptions import ConfigurationError, RenderingError
from mermaid_render.plugin_renderer import PluginMermaidRenderer


class TestPluginMermaidRenderer:
    """Test the PluginMermaidRenderer class."""

    def test_renderer_creation(self) -> None:
        """Test creating a plugin-based renderer."""
        renderer = PluginMermaidRenderer()
        assert isinstance(renderer.config, MermaidConfig)
        assert renderer.fallback_enabled is True
        assert renderer.preferred_renderer is None

    def test_renderer_creation_with_config(self) -> None:
        """Test creating renderer with custom configuration."""
        config = MermaidConfig(timeout=45.0)
        theme = MermaidTheme("dark")

        renderer = PluginMermaidRenderer(
            config=config,
            theme=theme,
            preferred_renderer="playwright",
            fallback_enabled=False,
        )

        assert renderer.config == config
        assert renderer.get_theme() == theme
        assert renderer.preferred_renderer == "playwright"
        assert renderer.fallback_enabled is False

    def test_set_theme_string(self) -> None:
        """Test setting theme with string."""
        renderer = PluginMermaidRenderer()
        renderer.set_theme("dark")

        theme = renderer.get_theme()
        assert theme is not None
        assert theme.name == "dark"

    def test_set_theme_object(self) -> None:
        """Test setting theme with MermaidTheme object."""
        renderer = PluginMermaidRenderer()
        theme = MermaidTheme("forest")
        renderer.set_theme(theme)

        assert renderer.get_theme() == theme

    def test_set_theme_invalid(self) -> None:
        """Test setting invalid theme."""
        renderer = PluginMermaidRenderer()

        with pytest.raises(ConfigurationError):
            renderer.set_theme("123")  # Invalid theme type as string

    @patch("mermaid_render.plugin_renderer.RendererManager")
    def test_render_with_plugin_system(self, mock_manager_class: Any) -> None:
        """Test rendering using the plugin system."""
        # Mock the renderer manager
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = "<svg>test</svg>"
        mock_manager.render.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        renderer = PluginMermaidRenderer()
        result = renderer.render("graph TD\n    A --> B", format="svg")

        assert result == "<svg>test</svg>"
        mock_manager.render.assert_called_once()

    @patch("mermaid_render.plugin_renderer.RendererManager")
    def test_render_failure(self, mock_manager_class: Any) -> None:
        """Test rendering failure handling."""
        # Mock the renderer manager to return failure
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Test error"
        mock_manager.render.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        renderer = PluginMermaidRenderer()

        with pytest.raises(RenderingError, match="Test error"):
            renderer.render("graph TD\n    A --> B", format="svg")

    @patch("mermaid_render.plugin_renderer.RendererManager")
    def test_render_with_diagram_object(self, mock_manager_class: Any) -> None:
        """Test rendering with MermaidDiagram object."""
        # Mock the renderer manager
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = "<svg>test</svg>"
        mock_manager.render.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        # Mock MermaidDiagram
        mock_diagram = Mock()
        mock_diagram.to_mermaid.return_value = "graph TD\n    A --> B"
        mock_diagram.validate.return_value = True

        renderer = PluginMermaidRenderer()
        result = renderer.render(mock_diagram, format="svg")

        assert result == "<svg>test</svg>"
        mock_diagram.to_mermaid.assert_called_once()
        mock_diagram.validate.assert_called_once()

    @patch("mermaid_render.plugin_renderer.RendererManager")
    @patch("pathlib.Path.mkdir")
    @patch("builtins.open")
    @patch("pathlib.Path.stat")
    def test_save_to_file(
        self, mock_stat: Any, mock_open: Any, mock_mkdir: Any, mock_manager_class: Any
    ) -> None:
        """Test saving rendered content to file."""
        # Mock the renderer manager
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = "<svg>test</svg>"
        mock_manager.render.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_stat.return_value.st_size = 100

        renderer = PluginMermaidRenderer()
        result = renderer.save("graph TD\n    A --> B", "test.svg")

        assert result["format"] == "svg"
        assert result["size_bytes"] == 100
        mock_file.write.assert_called_once_with("<svg>test</svg>")

    @patch("mermaid_render.plugin_renderer.RendererManager")
    def test_get_available_renderers(self, mock_manager_class: Any) -> None:
        """Test getting available renderers."""
        # Mock the renderer manager
        mock_manager = Mock()
        mock_manager.registry.list_renderers.return_value = ["svg", "png", "playwright"]
        mock_manager_class.return_value = mock_manager

        renderer = PluginMermaidRenderer()
        renderers = renderer.get_available_renderers()

        assert "svg" in renderers
        assert "png" in renderers
        assert "playwright" in renderers

    @patch("mermaid_render.plugin_renderer.RendererManager")
    def test_test_renderer(self, mock_manager_class: Any) -> None:
        """Test testing a specific renderer."""
        # Mock the renderer manager
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.render_time = 0.5
        mock_result.content = "<svg>test</svg>"
        mock_result.error = None
        mock_manager.render.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        renderer = PluginMermaidRenderer()
        test_result = renderer.test_renderer("playwright")

        assert test_result["renderer"] == "playwright"
        assert test_result["success"] is True
        assert test_result["render_time"] == 0.5
        assert test_result["content_size"] > 0

    @patch("mermaid_render.plugin_renderer.RendererManager")
    def test_benchmark_renderers(self, mock_manager_class: Any) -> None:
        """Test benchmarking all renderers."""
        # Mock the renderer manager
        mock_manager = Mock()
        mock_manager.registry.list_renderers.return_value = ["svg", "playwright"]

        # Mock successful rendering
        mock_result = Mock()
        mock_result.success = True
        mock_result.render_time = 0.3
        mock_result.content = "<svg>test</svg>"
        mock_manager.render.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        renderer = PluginMermaidRenderer()
        benchmark_results = renderer.benchmark_renderers()

        assert "svg" in benchmark_results
        assert "playwright" in benchmark_results

        # Check that each renderer was tested with multiple diagrams and formats
        svg_results = benchmark_results["svg"]
        assert len(svg_results) > 0
        assert all(result["success"] for result in svg_results)

    def test_context_manager(self) -> None:
        """Test context manager functionality."""
        with PluginMermaidRenderer() as renderer:
            assert isinstance(renderer, PluginMermaidRenderer)


class TestBackwardCompatibility:
    """Test backward compatibility with existing MermaidRenderer."""

    @patch("mermaid_render.core.SVGRenderer")
    @patch("mermaid_render.core.PNGRenderer")
    @patch("mermaid_render.core.PDFRenderer")
    def test_legacy_mode_still_works(
        self, mock_pdf: Any, mock_png: Any, mock_svg: Any
    ) -> None:
        """Test that legacy mode still works without plugin system."""
        from mermaid_render.core import MermaidRenderer

        # Mock legacy renderers
        mock_svg.return_value.render.return_value = "<svg>legacy</svg>"
        mock_png.return_value.render.return_value = b"png_data"

        # Create renderer in legacy mode (default)
        renderer = MermaidRenderer()

        # Test SVG rendering
        result = renderer.render_raw("graph TD\n    A --> B", "svg")
        assert result == "<svg>legacy</svg>"

        # Test PNG rendering
        result = renderer.render_raw("graph TD\n    A --> B", "png")
        assert result == b"png_data"

    def test_plugin_mode_integration(self) -> None:
        """Test that plugin mode can be enabled."""
        from mermaid_render.core import MermaidRenderer

        # Create renderer with plugin system enabled
        renderer = MermaidRenderer(use_plugin_system=True)

        assert renderer.use_plugin_system is True
        assert renderer._renderer_manager is not None
        assert renderer._svg_renderer is None  # Legacy renderers not initialized
