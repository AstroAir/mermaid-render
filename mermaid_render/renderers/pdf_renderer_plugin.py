"""
PDF renderer plugin adapter for the plugin-based architecture.

This module wraps the existing PDFRenderer to work with the new
plugin-based rendering system.
"""

import time
from typing import Any, Dict, Optional, Set

from .base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
)
from .pdf_renderer import PDFRenderer


class PDFRendererPlugin(BaseRenderer):
    """
    Plugin adapter for the existing PDFRenderer.

    This class wraps the existing PDFRenderer to work with the new
    plugin-based architecture while maintaining all existing functionality.
    """

    def __init__(self, **config: Any) -> None:
        """
        Initialize the PDF renderer plugin.

        Args:
            **config: Configuration options passed to PDFRenderer
        """
        super().__init__(**config)

        # Extract PDFRenderer-specific config
        pdf_config = {
            "page_size": config.get("page_size", "A4"),
            "orientation": config.get("orientation", "portrait"),
        }

        # Create SVGRenderer config for the underlying PDFRenderer
        svg_config = {
            "server_url": config.get("server_url", "https://mermaid.ink"),
            "timeout": config.get("timeout", 30.0),
            "use_local": config.get("use_local", True),
            "cache_enabled": config.get("cache_enabled", True),
        }

        # Remove None values
        svg_config = {k: v for k, v in svg_config.items() if v is not None}

        # Create the underlying PDFRenderer
        from .svg_renderer import SVGRenderer
        svg_renderer = SVGRenderer(**svg_config)
        self._pdf_renderer = PDFRenderer(svg_renderer=svg_renderer, **pdf_config)

    def get_info(self) -> RendererInfo:
        """
        Get renderer information and capabilities.

        Returns:
            RendererInfo object describing the PDF renderer
        """
        return RendererInfo(
            name="pdf",
            description="PDF renderer that converts SVG to PDF format",
            supported_formats={"pdf"},
            capabilities={
                RendererCapability.THEME_SUPPORT,
                RendererCapability.CUSTOM_CONFIG,
                RendererCapability.FALLBACK_SUPPORT,
            },
            priority=RendererPriority.NORMAL,
            version="1.0.0",
            author="Mermaid Render Team",
            dependencies=["cairosvg", "requests"],
            config_schema={
                "type": "object",
                "properties": {
                    "page_size": {"type": "string", "default": "A4"},
                    "orientation": {"type": "string", "enum": ["portrait", "landscape"], "default": "portrait"},
                    "server_url": {"type": "string", "default": "https://mermaid.ink"},
                    "timeout": {"type": "number", "default": 30.0},
                    "use_local": {"type": "boolean", "default": True},
                    "cache_enabled": {"type": "boolean", "default": True},
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
        Render Mermaid code to PDF format.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format (must be 'pdf')
            theme: Optional theme name
            config: Optional configuration dictionary
            **options: Additional rendering options

        Returns:
            RenderResult containing the PDF content and metadata

        Raises:
            UnsupportedFormatError: If format is not 'pdf'
            RenderingError: If rendering fails
        """
        from ..exceptions import UnsupportedFormatError

        if format.lower() != "pdf":
            raise UnsupportedFormatError(
                f"PDF renderer only supports 'pdf' format, got '{format}'")

        start_time = time.time()

        try:
            # Render using the underlying PDFRenderer
            pdf_data = self._pdf_renderer.render(
                mermaid_code=mermaid_code,
                theme=theme,
                config=config,
            )

            render_time = time.time() - start_time

            # Create metadata
            metadata = {
                "pdf_size": len(pdf_data),
                "page_size": self._pdf_renderer.page_size,
                "orientation": self._pdf_renderer.orientation,
            }

            return RenderResult(
                content=pdf_data,
                format="pdf",
                renderer_name="pdf",
                render_time=render_time,
                success=True,
                metadata=metadata,
            )

        except Exception as e:
            render_time = time.time() - start_time

            return RenderResult(
                content=b"",
                format="pdf",
                renderer_name="pdf",
                render_time=render_time,
                success=False,
                error=str(e),
            )

    def is_available(self) -> bool:
        """
        Check if PDF renderer is available.

        Returns:
            True if renderer is available, False otherwise
        """
        try:
            # Check if cairosvg is available (primary dependency)
            import cairosvg

            # Check if underlying SVG renderer is available
            if hasattr(self._pdf_renderer, "svg_renderer"):
                svg_renderer = self._pdf_renderer.svg_renderer
                if hasattr(svg_renderer, "get_server_status"):
                    status = svg_renderer.get_server_status()
                    if isinstance(status, dict):
                        return bool(status.get("available", False))

            return True
        except ImportError:
            return False
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get detailed health status of the PDF renderer.

        Returns:
            Dictionary with health status information
        """
        base_status = super().get_health_status()

        # Check PDF conversion dependencies
        pdf_backends = []

        try:
            import cairosvg
            pdf_backends.append("cairosvg")
        except ImportError:
            pass

        try:
            import weasyprint
            pdf_backends.append("weasyprint")
        except ImportError:
            pass

        try:
            from reportlab.graphics import renderPDF  # type: ignore[import-untyped]
            from svglib.svglib import svg2rlg
            pdf_backends.append("reportlab+svglib")
        except ImportError:
            pass

        base_status["pdf_backends"] = pdf_backends
        base_status["pdf_backend_available"] = len(pdf_backends) > 0

        # Add SVG renderer health if available
        try:
            if hasattr(self._pdf_renderer, "svg_renderer"):
                svg_renderer = self._pdf_renderer.svg_renderer
                if hasattr(svg_renderer, "get_server_status"):
                    base_status["svg_server_status"] = svg_renderer.get_server_status()
        except Exception as e:
            base_status["svg_health_check_error"] = str(e)

        return base_status

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate PDF renderer configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Basic validation for PDF renderer config
        valid_keys = {
            "page_size", "orientation", "server_url", "timeout",
            "use_local", "cache_enabled"
        }

        # Check for unknown keys
        unknown_keys = set(config.keys()) - valid_keys
        if unknown_keys:
            self.logger.warning(f"Unknown config keys for PDF renderer: {unknown_keys}")

        # Validate specific values
        if "orientation" in config:
            if config["orientation"] not in ["portrait", "landscape"]:
                return False

        if "page_size" in config:
            valid_sizes = ["A4", "A3", "A5", "Letter", "Legal"]
            if config["page_size"] not in valid_sizes:
                self.logger.warning(f"Unusual page size: {config['page_size']}")

        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
                return False

        return True

    def cleanup(self) -> None:
        """
        Clean up PDF renderer resources.
        """
        try:
            # Clean up underlying SVG renderer if it has cleanup
            if hasattr(self._pdf_renderer, "svg_renderer"):
                svg_renderer = self._pdf_renderer.svg_renderer
                if hasattr(svg_renderer, "close"):
                    svg_renderer.close()
        except Exception as e:
            self.logger.warning(f"Error during PDF renderer cleanup: {e}")

    def render_to_file(
        self,
        mermaid_code: str,
        output_path: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Render Mermaid code directly to PDF file.

        This method provides direct access to the underlying renderer's
        file output functionality for backward compatibility.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            output_path: Output file path
            theme: Optional theme name
            config: Optional configuration
        """
        self._pdf_renderer.render_to_file(
            mermaid_code=mermaid_code,
            output_path=output_path,
            theme=theme,
            config=config,
        )
