"""
PDF renderer for the Mermaid Render library.

This module provides PDF rendering functionality by converting SVG to PDF.
"""

import re
from typing import Any, Dict, Optional

from ..exceptions import RenderingError, UnsupportedFormatError
from .svg_renderer import SVGRenderer


class PDFRenderer:
    """
    PDF renderer that converts SVG to PDF.

    This renderer first generates SVG using SVGRenderer, then converts
    it to PDF format. Requires additional dependencies for PDF conversion.
    """

    def __init__(
        self,
        svg_renderer: Optional[SVGRenderer] = None,
        page_size: str = "A4",
        orientation: str = "portrait",
    ) -> None:
        """
        Initialize PDF renderer.

        Args:
            svg_renderer: Optional SVG renderer instance
            page_size: PDF page size (A4, Letter, etc.)
            orientation: Page orientation (portrait, landscape)
        """
        self.svg_renderer = svg_renderer or SVGRenderer()
        self.page_size = page_size
        self.orientation = orientation

    def render(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Render Mermaid code to PDF.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration dictionary

        Returns:
            PDF data as bytes

        Raises:
            RenderingError: If rendering fails
            UnsupportedFormatError: If PDF conversion is not available
        """
        try:
            # First, render to SVG
            svg_content = self.svg_renderer.render(mermaid_code, theme, config)

            # Convert SVG to PDF
            return self._svg_to_pdf(svg_content)

        except UnsupportedFormatError:
            # Bubble up as-is
            raise
        except Exception as e:
            raise RenderingError(f"PDF rendering failed: {str(e)}") from e

    def render_from_svg(self, svg_content: str) -> bytes:
        """
        Render PDF directly from SVG content.

        Args:
            svg_content: SVG content as string

        Returns:
            PDF data as bytes

        Raises:
            RenderingError: If rendering fails
        """
        try:
            return self._svg_to_pdf(svg_content)
        except UnsupportedFormatError:
            raise
        except Exception as e:
            raise RenderingError(f"PDF rendering from SVG failed: {str(e)}") from e

    def _clean_svg_content(self, svg_content: str) -> str:
        """
        Clean SVG content to ensure it's well-formed XML without corrupting entities.

        Args:
            svg_content: Raw SVG content

        Returns:
            Cleaned SVG content
        """
        # Remove any invalid control characters (keep valid XML content intact)
        svg_content = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", svg_content)

        # Ensure proper XML declaration if missing
        stripped = svg_content.lstrip()
        if not stripped.startswith("<?xml"):
            svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

        return svg_content

    def _svg_to_pdf(self, svg_content: str) -> bytes:
        """
        Convert SVG content to PDF.

        Args:
            svg_content: SVG content as string

        Returns:
            PDF data as bytes
        """
        # Clean the SVG content first
        cleaned_svg = self._clean_svg_content(svg_content)

        # Backend 1: cairosvg
        try:
            import cairosvg  # type: ignore

            pdf_data = cairosvg.svg2pdf(
                bytestring=cleaned_svg.encode("utf-8"),
                output_width=None,  # Preserve original dimensions
                output_height=None,
            )
            return (
                pdf_data
                if isinstance(pdf_data, (bytes, bytearray))
                else bytes(pdf_data or b"")
            )
        except ImportError:
            pass

        # Backend 2: weasyprint
        try:
            from io import BytesIO
            import weasyprint  # type: ignore

            # Wrap SVG in HTML so WeasyPrint can render it
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        html, body {{ margin: 0; padding: 0; }}
        body {{ padding: 20px; }}
        svg {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
{cleaned_svg}
</body>
</html>"""

            html_doc = weasyprint.HTML(string=html_content)
            pdf_buffer = BytesIO()
            html_doc.write_pdf(target=pdf_buffer)
            data = pdf_buffer.getvalue()
            return data if isinstance(data, (bytes, bytearray)) else bytes(data or b"")
        except ImportError:
            pass

        # Backend 3: reportlab + svglib
        try:
            from io import BytesIO
            from tempfile import NamedTemporaryFile

            # svglib converts SVG to a ReportLab drawing
            from svglib.svglib import svg2rlg  # type: ignore
            from reportlab.graphics import renderPDF  # type: ignore

            # Convert SVG string to a drawing
            svg_bytes = cleaned_svg.encode("utf-8")
            drawing = svg2rlg(BytesIO(svg_bytes))
            if drawing is None:
                raise RenderingError("Failed to parse SVG content for PDF conversion.")

            # renderPDF doesn't provide a stable drawToString across versions,
            # so use a temporary file for broad compatibility.
            with NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
                renderPDF.drawToFile(drawing, tmp.name)
                tmp.seek(0)
                data = tmp.read()

            return data if isinstance(data, (bytes, bytearray)) else bytes(data or b"")
        except ImportError:
            raise UnsupportedFormatError(
                "PDF rendering requires one of: cairosvg, weasyprint, or reportlab+svglib. "
                "Install with: pip install cairosvg"
            )

    def render_to_file(
        self,
        mermaid_code: str,
        output_path: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Render Mermaid code to PDF file.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            output_path: Output file path
            theme: Optional theme name
            config: Optional configuration
        """
        pdf_data = self.render(mermaid_code, theme, config)

        with open(output_path, "wb") as f:
            f.write(pdf_data)

    def get_supported_themes(self) -> list[str]:
        """Get list of supported themes."""
        themes = self.svg_renderer.get_supported_themes()
        return list(themes.keys()) if isinstance(themes, dict) else themes

    def validate_theme(self, theme: str) -> bool:
        """Validate if theme is supported."""
        return self.svg_renderer.validate_theme(theme)

    def get_supported_page_sizes(self) -> list[str]:
        """Get list of supported page sizes."""
        return ["A4", "A3", "A5", "Letter", "Legal", "Tabloid"]

    def set_page_options(self, page_size: str, orientation: str) -> None:
        """
        Set PDF page options.

        Args:
            page_size: Page size (A4, Letter, etc.)
            orientation: Page orientation (portrait, landscape)
        """
        if page_size not in self.get_supported_page_sizes():
            raise RenderingError(f"Unsupported page size: {page_size}")

        if orientation not in ["portrait", "landscape"]:
            raise RenderingError(f"Invalid orientation: {orientation}")

        self.page_size = page_size
        self.orientation = orientation
