"""
Playwright renderer for the Mermaid Render library.

This module provides rendering functionality using Playwright to run
Mermaid.js in a headless browser for high-fidelity diagram rendering.
"""

import json
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Page

from .base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
)


class PlaywrightRenderer(BaseRenderer):
    """
    Renderer using Playwright to run Mermaid.js in headless browser.

    This renderer provides high-fidelity rendering by using the actual
    Mermaid.js library in a controlled browser environment. It supports
    all Mermaid diagram types and provides excellent compatibility.
    """

    def __init__(self, **config: Any) -> None:
        """
        Initialize the Playwright renderer.

        Args:
            **config: Configuration options
        """
        super().__init__(**config)

        self.browser_type = config.get("browser_type", "chromium")
        self.headless = config.get("headless", True)
        self.timeout = config.get("timeout", 30000)  # milliseconds
        self.viewport_width = config.get("viewport_width", 1200)
        self.viewport_height = config.get("viewport_height", 800)
        self.mermaid_version = config.get("mermaid_version", "10.6.1")

        self._browser: Optional["Browser"] = None
        self._context: Optional["BrowserContext"] = None
        self._page: Optional["Page"] = None

    def get_info(self) -> RendererInfo:
        """
        Get renderer information and capabilities.

        Returns:
            RendererInfo object describing the Playwright renderer
        """
        return RendererInfo(
            name="playwright",
            description="High-fidelity renderer using Playwright and Mermaid.js in headless browser",
            supported_formats={"svg", "png", "pdf"},
            capabilities={
                RendererCapability.VALIDATION,
                RendererCapability.THEME_SUPPORT,
                RendererCapability.CUSTOM_CONFIG,
                RendererCapability.LOCAL_RENDERING,
                RendererCapability.PERFORMANCE_METRICS,
            },
            priority=RendererPriority.HIGH,
            version="1.0.0",
            author="Mermaid Render Team",
            dependencies=["playwright"],
            config_schema={
                "type": "object",
                "properties": {
                    "browser_type": {"type": "string", "enum": ["chromium", "firefox", "webkit"], "default": "chromium"},
                    "headless": {"type": "boolean", "default": True},
                    "timeout": {"type": "integer", "default": 30000},
                    "viewport_width": {"type": "integer", "default": 1200},
                    "viewport_height": {"type": "integer", "default": 800},
                    "mermaid_version": {"type": "string", "default": "10.6.1"},
                },
            },
        )

    def render(
        self,
        mermaid_code: str,
        format: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **options: Any,
    ) -> RenderResult:
        """
        Render Mermaid code using Playwright.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format (svg, png, pdf)
            theme: Optional theme name
            config: Optional configuration dictionary
            **options: Additional rendering options

        Returns:
            RenderResult containing the rendered content and metadata
        """
        from ..exceptions import RenderingError, UnsupportedFormatError

        if format.lower() not in {"svg", "png", "pdf"}:
            raise UnsupportedFormatError(
                f"Playwright renderer doesn't support format '{format}'")

        start_time = time.time()

        try:
            # Initialize browser if needed
            self._ensure_browser()

            # Create HTML template with Mermaid.js
            html_content = self._create_html_template(mermaid_code, theme, config)

            # Navigate to the HTML content
            assert self._page is not None  # Guaranteed by _ensure_browser()
            self._page.set_content(html_content)

            # Wait for Mermaid to render
            self._page.wait_for_selector("#mermaid-diagram svg", timeout=self.timeout)

            # Get the rendered content based on format
            content: Union[str, bytes]
            if format.lower() == "svg":
                content = self._extract_svg()
            elif format.lower() == "png":
                content = self._capture_png(options)
            elif format.lower() == "pdf":
                content = self._capture_pdf(options)
            else:
                raise UnsupportedFormatError(f"Unsupported format: {format}")

            render_time = time.time() - start_time

            # Get diagram dimensions
            dimensions = self._get_diagram_dimensions()

            return RenderResult(
                content=content,
                format=format.lower(),
                renderer_name="playwright",
                render_time=render_time,
                success=True,
                metadata={
                    "browser_type": self.browser_type,
                    "mermaid_version": self.mermaid_version,
                    "dimensions": dimensions,
                },
            )

        except Exception as e:
            render_time = time.time() - start_time

            return RenderResult(
                content="" if format.lower() == "svg" else b"",
                format=format.lower(),
                renderer_name="playwright",
                render_time=render_time,
                success=False,
                error=str(e),
            )

    def _ensure_browser(self) -> None:
        """Ensure browser is initialized and ready."""
        from ..exceptions import RenderingError

        if self._page is not None:
            return

        try:
            from playwright.sync_api import sync_playwright

            if not hasattr(self, "_playwright"):
                self._playwright = sync_playwright().start()

            if self._browser is None:
                # Add error handling for browser launch
                try:
                    if self.browser_type == "chromium":
                        self._browser = self._playwright.chromium.launch(
                            headless=self.headless)
                    elif self.browser_type == "firefox":
                        self._browser = self._playwright.firefox.launch(
                            headless=self.headless)
                    elif self.browser_type == "webkit":
                        self._browser = self._playwright.webkit.launch(
                            headless=self.headless)
                    else:
                        raise ValueError(
                            f"Unsupported browser type: {self.browser_type}")
                except Exception as e:
                    raise RenderingError(
                        f"Failed to launch {self.browser_type} browser. "
                        f"Make sure browsers are installed with: playwright install {self.browser_type}. "
                        f"Error: {e}"
                    )

            if self._context is None:
                assert self._browser is not None  # Guaranteed by previous code
                self._context = self._browser.new_context(
                    viewport={"width": self.viewport_width,
                              "height": self.viewport_height}
                )

            if self._page is None:
                assert self._context is not None  # Guaranteed by previous code
                self._page = self._context.new_page()

        except ImportError:
            raise RenderingError(
                "Playwright renderer requires playwright. Install with: pip install playwright && playwright install"
            )

    def _create_html_template(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create HTML template with Mermaid.js."""
        theme_config = ""
        if theme and theme != "default":
            theme_config = f"theme: '{theme}',"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@{self.mermaid_version}/dist/mermaid.min.js"></script>
</head>
<body>
    <div id="mermaid-diagram" class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            {theme_config}
            securityLevel: 'loose'
        }});
    </script>
</body>
</html>"""

    def _extract_svg(self) -> str:
        """Extract SVG content from the rendered page."""
        assert self._page is not None  # Should be guaranteed by caller
        return self._page.locator("#mermaid-diagram svg").inner_html()

    def _capture_png(self, options: Dict[str, Any]) -> bytes:
        """Capture PNG screenshot of the diagram."""
        assert self._page is not None  # Should be guaranteed by caller
        element = self._page.locator("#mermaid-diagram svg")
        return element.screenshot(
            type="png",
            quality=options.get("quality", 90),
        )

    def _capture_pdf(self, options: Dict[str, Any]) -> bytes:
        """Capture PDF of the diagram."""
        assert self._page is not None  # Should be guaranteed by caller
        return self._page.pdf(
            format=options.get("page_size", "A4"),
            landscape=options.get("orientation", "portrait") == "landscape",
        )

    def _get_diagram_dimensions(self) -> Dict[str, Any]:
        """Get dimensions of the rendered diagram."""
        try:
            assert self._page is not None  # Should be guaranteed by caller
            element = self._page.locator("#mermaid-diagram svg")
            box = element.bounding_box()
            return {
                "width": box["width"] if box else 0,
                "height": box["height"] if box else 0,
            }
        except Exception:
            return {"width": 0, "height": 0}

    def is_available(self) -> bool:
        """
        Check if Playwright renderer is available.

        Returns:
            True if Playwright is installed and browsers are available
        """
        try:
            from playwright.sync_api import sync_playwright

            # Try to start playwright
            with sync_playwright() as p:
                # Check if browser is available
                if self.browser_type == "chromium":
                    browser = p.chromium.launch(headless=True)
                elif self.browser_type == "firefox":
                    browser = p.firefox.launch(headless=True)
                elif self.browser_type == "webkit":
                    browser = p.webkit.launch(headless=True)
                else:
                    return False

                browser.close()
                return True

        except ImportError:
            return False
        except Exception:
            return False

    def cleanup(self) -> None:
        """Clean up Playwright resources."""
        try:
            if self._page:
                self._page.close()
                self._page = None

            if self._context:
                self._context.close()
                self._context = None

            if self._browser:
                self._browser.close()
                self._browser = None

            if hasattr(self, "_playwright"):
                self._playwright.stop()
                delattr(self, "_playwright")

        except Exception as e:
            self.logger.warning(f"Error during Playwright cleanup: {e}")
