"""
Unit tests for interactive.export module.

Tests the ExportManager and ExportFormat classes.
"""

import pytest

from diagramaid.interactive.export import ExportFormat, ExportManager


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

    def test_mermaid_format(self) -> None:
        """Test Mermaid export format."""
        assert ExportFormat.MERMAID.value == "mermaid"

    def test_json_format(self) -> None:
        """Test JSON export format."""
        assert ExportFormat.JSON.value == "json"


@pytest.mark.unit
class TestExportManager:
    """Unit tests for ExportManager class."""

    def test_initialization(self) -> None:
        """Test ExportManager initialization."""
        manager = ExportManager()
        assert manager is not None
        assert manager.renderer is not None

    def test_supported_formats(self) -> None:
        """Test getting supported formats."""
        manager = ExportManager()
        formats = manager.supported_formats
        assert len(formats) > 0
        assert ExportFormat.SVG in formats
        assert ExportFormat.PNG in formats
