from typing import Any

"""
Tests for the new renderer implementations.

This module tests the PlaywrightRenderer, NodeJSRenderer, and GraphvizRenderer
implementations to ensure they work correctly within the plugin architecture.
"""

from unittest.mock import Mock, patch

from mermaid_render.renderers.base import RendererCapability
from mermaid_render.renderers.graphviz_renderer import GraphvizRenderer
from mermaid_render.renderers.nodejs_renderer import NodeJSRenderer
from mermaid_render.renderers.playwright_renderer import PlaywrightRenderer


class TestPlaywrightRenderer:
    """Test the PlaywrightRenderer class."""

    def test_renderer_info(self) -> None:
        """Test renderer information."""
        renderer = PlaywrightRenderer()
        info = renderer.get_info()

        assert info.name == "playwright"
        assert "svg" in info.supported_formats
        assert "png" in info.supported_formats
        assert "pdf" in info.supported_formats
        assert RendererCapability.LOCAL_RENDERING in info.capabilities

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        renderer = PlaywrightRenderer()

        # Valid config
        valid_config = {
            "browser_type": "chromium",
            "headless": True,
            "timeout": 30000,
        }
        assert renderer.validate_config(valid_config)

        # Invalid browser type would be caught by schema validation
        # This test ensures the renderer handles config properly
        renderer_with_config = PlaywrightRenderer(**valid_config)
        assert renderer_with_config.browser_type == "chromium"

    @patch("mermaid_render.renderers.playwright_renderer.sync_playwright")
    def test_is_available_with_playwright(self, mock_playwright: Any) -> None:
        """Test availability check when Playwright is available."""
        # Mock Playwright components
        mock_p = Mock()
        mock_browser = Mock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_p

        renderer = PlaywrightRenderer()
        assert renderer.is_available()

        mock_p.chromium.launch.assert_called_once()
        mock_browser.close.assert_called_once()

    def test_is_available_without_playwright(self) -> None:
        """Test availability check when Playwright is not available."""
        with patch(
            "mermaid_render.renderers.playwright_renderer.sync_playwright",
            side_effect=ImportError,
        ):
            renderer = PlaywrightRenderer()
            assert not renderer.is_available()

    @patch("mermaid_render.renderers.playwright_renderer.sync_playwright")
    def test_render_svg(self, mock_playwright: Any) -> None:
        """Test SVG rendering."""
        # Mock Playwright components
        mock_page = Mock()
        mock_page.locator.return_value.inner_html.return_value = "<svg>test</svg>"
        mock_page.locator.return_value.bounding_box.return_value = {
            "width": 100,
            "height": 100,
        }

        mock_context = Mock()
        mock_context.new_page.return_value = mock_page

        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context

        mock_p = Mock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.start.return_value = mock_p

        renderer = PlaywrightRenderer()
        renderer._playwright = mock_p
        renderer._browser = mock_browser
        renderer._context = mock_context
        renderer._page = mock_page

        result = renderer.render("graph TD\n    A --> B", "svg")

        assert result.success
        assert result.format == "svg"
        assert result.renderer_name == "playwright"
        assert "test" in result.content


class TestNodeJSRenderer:
    """Test the NodeJSRenderer class."""

    def test_renderer_info(self) -> None:
        """Test renderer information."""
        renderer = NodeJSRenderer()
        info = renderer.get_info()

        assert info.name == "nodejs"
        assert "svg" in info.supported_formats
        assert "png" in info.supported_formats
        assert "pdf" in info.supported_formats
        assert RendererCapability.LOCAL_RENDERING in info.capabilities

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        renderer = NodeJSRenderer()

        # Valid config
        valid_config = {
            "mmdc_path": "mmdc",
            "timeout": 30.0,
        }
        assert renderer.validate_config(valid_config)

        # Invalid timeout
        invalid_config = {"timeout": -1}
        assert not renderer.validate_config(invalid_config)

    @patch("subprocess.run")
    def test_is_available_with_dependencies(self, mock_run: Any) -> None:
        """Test availability when Node.js and mmdc are available."""
        mock_run.return_value.returncode = 0

        renderer = NodeJSRenderer()
        assert renderer.is_available()

        # Should check both node and mmdc
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_is_available_without_dependencies(self, mock_run: Any) -> None:
        """Test availability when dependencies are missing."""
        mock_run.side_effect = FileNotFoundError()

        renderer = NodeJSRenderer()
        assert not renderer.is_available()

    @patch("subprocess.run")
    @patch("tempfile.TemporaryDirectory")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_render_svg(
        self,
        mock_exists: Any,
        mock_read_text: Any,
        mock_write_text: Any,
        mock_temp_dir: Any,
        mock_run: Any,
    ) -> None:
        """Test SVG rendering with Node.js."""
        # Mock successful subprocess execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        mock_run.return_value.stdout = "Rendering complete"

        # Mock file operations
        mock_exists.return_value = True
        mock_read_text.return_value = "<svg>test content</svg>"

        # Mock temporary directory
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/test"

        renderer = NodeJSRenderer()
        result = renderer.render("graph TD\n    A --> B", "svg")

        assert result.success
        assert result.format == "svg"
        assert result.renderer_name == "nodejs"


class TestGraphvizRenderer:
    """Test the GraphvizRenderer class."""

    def test_renderer_info(self) -> None:
        """Test renderer information."""
        renderer = GraphvizRenderer()
        info = renderer.get_info()

        assert info.name == "graphviz"
        assert "svg" in info.supported_formats
        assert RendererCapability.LOCAL_RENDERING in info.capabilities

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        renderer = GraphvizRenderer()

        # Valid config
        valid_config = {
            "engine": "dot",
            "rankdir": "TB",
            "dpi": 96,
        }
        assert renderer.validate_config(valid_config)

        # Invalid engine
        invalid_config = {"engine": "invalid_engine"}
        assert not renderer.validate_config(invalid_config)

        # Invalid rankdir
        invalid_config = {"rankdir": "INVALID"}
        assert not renderer.validate_config(invalid_config)

    def test_diagram_support_detection(self) -> None:
        """Test diagram type support detection."""
        renderer = GraphvizRenderer()

        # Supported diagrams
        assert renderer._is_diagram_supported("flowchart TD\n    A --> B")
        assert renderer._is_diagram_supported("graph LR\n    A --> B")

        # Unsupported diagrams
        assert not renderer._is_diagram_supported("sequenceDiagram\n    A->>B: Hello")
        assert not renderer._is_diagram_supported("classDiagram\n    class A")

    def test_mermaid_to_dot_conversion(self) -> None:
        """Test conversion from Mermaid to DOT format."""
        renderer = GraphvizRenderer()

        mermaid_code = """flowchart TD
    A[Start] --> B[Process]
    B --> C[End]"""

        dot_code = renderer._convert_to_dot(mermaid_code, None, None)

        assert "digraph G {" in dot_code
        assert 'A [label="Start"]' in dot_code
        assert 'B [label="Process"]' in dot_code
        assert "A -> B" in dot_code
        assert "B -> C" in dot_code

    @patch("builtins.__import__")
    def test_is_available_with_graphviz(self, mock_import: Any) -> None:
        """Test availability when Graphviz is available."""
        # Mock the graphviz module
        mock_graphviz = Mock()
        mock_source = Mock()
        mock_source.pipe.return_value = "<svg>test</svg>"
        mock_graphviz.Source.return_value = mock_source

        def side_effect(name, *args, **kwargs):
            if name == "graphviz":
                return mock_graphviz
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = side_effect

        renderer = GraphvizRenderer()
        assert renderer.is_available()

    @patch("builtins.__import__")
    def test_is_available_without_graphviz(self, mock_import: Any) -> None:
        """Test availability when Graphviz is not available."""

        def side_effect(name, *args, **kwargs):
            if name == "graphviz":
                raise ImportError("No module named 'graphviz'")
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = side_effect

        renderer = GraphvizRenderer()
        assert not renderer.is_available()

    @patch("builtins.__import__")
    def test_render_svg(self, mock_import: Any) -> None:
        """Test SVG rendering with Graphviz."""
        # Mock the graphviz module
        mock_graphviz = Mock()
        mock_source = Mock()
        mock_source.pipe.return_value = "<svg>graphviz content</svg>"
        mock_graphviz.Source.return_value = mock_source

        def side_effect(name, *args, **kwargs):
            if name == "graphviz":
                return mock_graphviz
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = side_effect

        renderer = GraphvizRenderer()
        result = renderer.render("flowchart TD\n    A --> B", "svg")

        assert result.success
        assert result.format == "svg"
        assert result.renderer_name == "graphviz"
        assert "graphviz content" in result.content

    def test_render_unsupported_diagram(self) -> None:
        """Test rendering unsupported diagram type."""
        renderer = GraphvizRenderer()

        result = renderer.render("sequenceDiagram\n    A->>B: Hello", "svg")

        assert not result.success
        assert result.error is not None and "not supported" in result.error
