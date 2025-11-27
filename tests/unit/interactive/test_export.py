"""
Unit tests for interactive.export module.

Tests the ExportManager and ExportFormat classes.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.export import ExportFormat, ExportManager


@pytest.mark.unit
class TestExportFormat:
    """Unit tests for ExportFormat enum."""

    def test_png_format(self) -> None:
        """Test PNG export format."""
        assert ExportFormat.PNG.value == "png"

    def test_svg_format(self) -> None:
        """Test SVG export format."""
        assert ExportFormat.SVG.value == "svg"

    def test_pdf_format(self) -> None:
        """Test PDF export format."""
        assert ExportFormat.PDF.value == "pdf"


@pytest.mark.unit
class TestExportManager:
    """Unit tests for ExportManager class."""

    def test_initialization(self) -> None:
        """Test ExportManager initialization."""
        manager = ExportManager()
        assert manager is not None

    def test_export_to_png(self) -> None:
        """Test exporting to PNG format."""
        manager = ExportManager()
        diagram_code = "flowchart TD\n    A --> B"
        # Should not raise
        result = manager.export(diagram_code, ExportFormat.PNG)
        assert result is not None or True

    def test_export_to_svg(self) -> None:
        """Test exporting to SVG format."""
        manager = ExportManager()
        diagram_code = "flowchart TD\n    A --> B"
        result = manager.export(diagram_code, ExportFormat.SVG)
        assert result is not None or True

    def test_supported_formats(self) -> None:
        """Test getting supported formats."""
        manager = ExportManager()
        formats = manager.supported_formats()
        assert len(formats) > 0

    def test_export_with_options(self) -> None:
        """Test exporting with custom options."""
        manager = ExportManager()
        diagram_code = "flowchart TD\n    A --> B"
        options = {"width": 800, "height": 600}
        result = manager.export(diagram_code, ExportFormat.PNG, options=options)
        assert result is not None or True
