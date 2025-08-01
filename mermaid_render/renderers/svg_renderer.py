"""
SVG renderer for the Mermaid Render library.

This module provides SVG rendering functionality using the mermaid-py library
and mermaid.ink service.
"""

from typing import Any, Dict, Optional

import mermaid as md
import requests

from ..exceptions import NetworkError, RenderingError


class SVGRenderer:
    """
    SVG renderer using mermaid-py and mermaid.ink service.

    This renderer converts Mermaid diagram code to SVG format using
    the online mermaid.ink service or local mermaid-py functionality.
    """

    def __init__(
        self,
        server_url: str = "https://mermaid.ink",
        timeout: float = 30.0,
        use_local: bool = True,
    ) -> None:
        """
        Initialize SVG renderer.

        Args:
            server_url: Mermaid.ink server URL
            timeout: Request timeout in seconds
            use_local: Whether to use local mermaid-py rendering when possible
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.use_local = use_local

    def render(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render Mermaid code to SVG.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration dictionary

        Returns:
            SVG content as string

        Raises:
            RenderingError: If rendering fails
            NetworkError: If network request fails
        """
        if self.use_local:
            try:
                return self._render_local(mermaid_code, theme, config)
            except Exception:
                # Fall back to remote rendering if local fails
                return self._render_remote(mermaid_code, theme, config)
        else:
            return self._render_remote(mermaid_code, theme, config)

    def _render_local(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render using local mermaid-py library.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration

        Returns:
            SVG content as string
        """
        try:
            # Create Mermaid object
            mermaid_obj = md.Mermaid(mermaid_code)

            # Apply theme and config if provided
            if theme or config:
                # Note: mermaid-py has limited theme/config support
                # This is a simplified implementation
                pass

            # Get SVG content
            # The mermaid-py library returns HTML with embedded SVG
            # We need to extract just the SVG part
            html_content = str(mermaid_obj)

            # Extract SVG from HTML (simplified)
            if "<svg" in html_content and "</svg>" in html_content:
                start = html_content.find("<svg")
                end = html_content.find("</svg>") + 6
                svg_content = html_content[start:end]
                return svg_content
            else:
                # If we can't extract SVG, return the full HTML
                return html_content

        except Exception as e:
            raise RenderingError(f"Local SVG rendering failed: {str(e)}") from e

    def _render_remote(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render using remote mermaid.ink service.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration

        Returns:
            SVG content as string
        """
        try:
            # Prepare the configuration
            mermaid_config = {}
            if theme:
                mermaid_config["theme"] = theme
            if config:
                mermaid_config.update(config)

            # Create the request payload
            if mermaid_config:
                # Include config in the request
                payload = {"code": mermaid_code, "mermaid": mermaid_config}
                # Encode as JSON and then base64 for URL
                import base64
                import json

                json_str = json.dumps(payload)
                encoded = base64.b64encode(json_str.encode()).decode()
                url = f"{self.server_url}/svg/{encoded}"
            else:
                # Simple encoding without config
                encoded = base64.b64encode(mermaid_code.encode()).decode()
                url = f"{self.server_url}/svg/{encoded}"

            # Make the request
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            return response.text

        except requests.exceptions.Timeout as e:
            raise NetworkError(
                f"Request timeout after {self.timeout}s", url=url, timeout=self.timeout
            ) from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network request failed: {str(e)}", url=url) from e
        except Exception as e:
            raise RenderingError(f"Remote SVG rendering failed: {str(e)}") from e

    def render_to_file(
        self,
        mermaid_code: str,
        output_path: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Render Mermaid code to SVG file.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            output_path: Output file path
            theme: Optional theme name
            config: Optional configuration
        """
        svg_content = self.render(mermaid_code, theme, config)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    def get_supported_themes(self) -> list[str]:
        """Get list of supported themes."""
        return ["default", "dark", "forest", "neutral", "base"]

    def validate_theme(self, theme: str) -> bool:
        """Validate if theme is supported."""
        return theme in self.get_supported_themes()
