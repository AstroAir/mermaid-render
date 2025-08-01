"""
PNG renderer for the Mermaid Render library.

This module provides PNG rendering functionality using the mermaid.ink service.
"""

import base64
import json
from typing import Any, Dict, Optional

import requests

from ..exceptions import NetworkError, RenderingError


class PNGRenderer:
    """
    PNG renderer using mermaid.ink service.

    This renderer converts Mermaid diagram code to PNG format using
    the online mermaid.ink service.
    """

    def __init__(
        self,
        server_url: str = "https://mermaid.ink",
        timeout: float = 30.0,
        width: int = 800,
        height: int = 600,
    ) -> None:
        """
        Initialize PNG renderer.

        Args:
            server_url: Mermaid.ink server URL
            timeout: Request timeout in seconds
            width: Default image width
            height: Default image height
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.default_width = width
        self.default_height = height

    def render(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> bytes:
        """
        Render Mermaid code to PNG.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration dictionary
            width: Image width (defaults to instance default)
            height: Image height (defaults to instance default)

        Returns:
            PNG image data as bytes

        Raises:
            RenderingError: If rendering fails
            NetworkError: If network request fails
        """
        try:
            # Prepare the configuration
            mermaid_config = {}
            if theme:
                mermaid_config["theme"] = theme
            if config:
                mermaid_config.update(config)

            # Add image dimensions
            img_width = width or self.default_width
            img_height = height or self.default_height

            # Create the request payload
            if mermaid_config:
                payload = {"code": mermaid_code, "mermaid": mermaid_config}
                json_str = json.dumps(payload)
                encoded = base64.b64encode(json_str.encode()).decode()
            else:
                encoded = base64.b64encode(mermaid_code.encode()).decode()

            # Build URL with image parameters
            url = f"{self.server_url}/img/{encoded}"
            params = {
                "type": "png",
                "width": img_width,
                "height": img_height,
            }

            # Make the request
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            # Verify we got PNG data
            if not response.content.startswith(b"\x89PNG"):
                raise RenderingError("Response is not valid PNG data")

            return response.content

        except requests.exceptions.Timeout as e:
            raise NetworkError(
                f"Request timeout after {self.timeout}s", url=url, timeout=self.timeout
            ) from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network request failed: {str(e)}", url=url) from e
        except Exception as e:
            raise RenderingError(f"PNG rendering failed: {str(e)}") from e

    def render_to_file(
        self,
        mermaid_code: str,
        output_path: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """
        Render Mermaid code to PNG file.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            output_path: Output file path
            theme: Optional theme name
            config: Optional configuration
            width: Image width
            height: Image height
        """
        png_data = self.render(mermaid_code, theme, config, width, height)

        with open(output_path, "wb") as f:
            f.write(png_data)

    def get_supported_themes(self) -> list[str]:
        """Get list of supported themes."""
        return ["default", "dark", "forest", "neutral", "base"]

    def validate_theme(self, theme: str) -> bool:
        """Validate if theme is supported."""
        return theme in self.get_supported_themes()

    def get_max_dimensions(self) -> tuple[int, int]:
        """Get maximum supported image dimensions."""
        # These are typical limits for mermaid.ink
        return (4000, 4000)

    def validate_dimensions(self, width: int, height: int) -> bool:
        """Validate image dimensions."""
        max_width, max_height = self.get_max_dimensions()
        return 0 < width <= max_width and 0 < height <= max_height
