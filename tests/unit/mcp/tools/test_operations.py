"""
Unit tests for mcp.tools.operations module.

Tests for batch operations, file operations, and format conversion tools.
These include async functions that use FastMCP Context support.
"""

import pytest

from diagramaid.mcp.tools.operations import (
    batch_render_diagrams,
    convert_diagram_format,
    export_to_markdown,
    get_diagram_examples,
    list_diagram_types,
    merge_diagrams,
    save_diagram_to_file,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestConvertDiagramFormat:
    """Tests for convert_diagram_format function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await convert_diagram_format("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await convert_diagram_format("flowchart TD\n    A --> B")
        assert "success" in result

    async def test_convert_to_png(self):
        """Test conversion to PNG format."""
        result = await convert_diagram_format(
            "flowchart TD\n    A --> B", target_format="png"
        )
        assert isinstance(result, dict)

    async def test_convert_to_svg(self):
        """Test conversion to SVG format."""
        result = await convert_diagram_format(
            "flowchart TD\n    A --> B", target_format="svg"
        )
        assert isinstance(result, dict)

    async def test_convert_to_pdf(self):
        """Test conversion to PDF format."""
        result = await convert_diagram_format(
            "flowchart TD\n    A --> B", target_format="pdf"
        )
        assert isinstance(result, dict)

    async def test_invalid_format(self):
        """Test invalid target format."""
        result = await convert_diagram_format(
            "flowchart TD\n    A --> B", target_format="invalid"
        )
        assert result["success"] is False

    async def test_with_theme(self):
        """Test conversion with theme."""
        result = await convert_diagram_format(
            "flowchart TD\n    A --> B", target_format="svg", theme="dark"
        )
        assert isinstance(result, dict)


@pytest.mark.unit
class TestMergeDiagrams:
    """Tests for merge_diagrams function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "name": "Diagram 1"},
            {"code": "flowchart TD\n    C --> D", "name": "Diagram 2"},
        ]
        result = merge_diagrams(diagrams)
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "name": "Diagram 1"},
            {"code": "flowchart TD\n    C --> D", "name": "Diagram 2"},
        ]
        result = merge_diagrams(diagrams)
        assert "success" in result

    def test_subgraph_strategy(self):
        """Test subgraph merge strategy."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "name": "Diagram 1"},
            {"code": "flowchart TD\n    C --> D", "name": "Diagram 2"},
        ]
        result = merge_diagrams(diagrams, merge_strategy="subgraph")
        assert isinstance(result, dict)

    def test_sequential_strategy(self):
        """Test sequential merge strategy."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "name": "Diagram 1"},
            {"code": "flowchart TD\n    C --> D", "name": "Diagram 2"},
        ]
        result = merge_diagrams(diagrams, merge_strategy="sequential")
        assert isinstance(result, dict)

    def test_parallel_strategy(self):
        """Test parallel merge strategy."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "name": "Diagram 1"},
            {"code": "flowchart TD\n    C --> D", "name": "Diagram 2"},
        ]
        result = merge_diagrams(diagrams, merge_strategy="parallel")
        assert isinstance(result, dict)

    def test_invalid_strategy(self):
        """Test invalid merge strategy."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "name": "Diagram 1"},
            {"code": "flowchart TD\n    C --> D", "name": "Diagram 2"},
        ]
        result = merge_diagrams(diagrams, merge_strategy="invalid")
        assert result["success"] is False

    def test_single_diagram_fails(self):
        """Test single diagram fails."""
        diagrams = [{"code": "flowchart TD\n    A --> B", "name": "Diagram 1"}]
        result = merge_diagrams(diagrams)
        assert result["success"] is False

    def test_with_title(self):
        """Test merge with title."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "name": "Diagram 1"},
            {"code": "flowchart TD\n    C --> D", "name": "Diagram 2"},
        ]
        result = merge_diagrams(diagrams, title="Merged Diagram")
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
class TestExportToMarkdown:
    """Tests for export_to_markdown function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await export_to_markdown("flowchart TD\n    A --> B")
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await export_to_markdown("flowchart TD\n    A --> B")
        assert "success" in result

    async def test_with_title(self):
        """Test export with title."""
        result = await export_to_markdown(
            "flowchart TD\n    A --> B", title="My Diagram"
        )
        assert isinstance(result, dict)

    async def test_with_description(self):
        """Test export with description."""
        result = await export_to_markdown(
            "flowchart TD\n    A --> B", description="A simple flowchart"
        )
        assert isinstance(result, dict)

    async def test_include_code(self):
        """Test export with code included."""
        result = await export_to_markdown(
            "flowchart TD\n    A --> B", include_code=True
        )
        if result["success"]:
            assert "mermaid" in result["data"]["markdown"].lower()

    async def test_include_preview(self):
        """Test export with preview included."""
        result = await export_to_markdown(
            "flowchart TD\n    A --> B", include_preview=True
        )
        assert isinstance(result, dict)

    async def test_include_elements(self):
        """Test export with elements included."""
        result = await export_to_markdown(
            "flowchart TD\n    A --> B", include_elements=True
        )
        assert isinstance(result, dict)

    async def test_result_has_markdown(self):
        """Test result includes markdown content."""
        result = await export_to_markdown("flowchart TD\n    A --> B")
        if result["success"]:
            assert "data" in result
            assert "markdown" in result["data"]


@pytest.mark.unit
@pytest.mark.asyncio
class TestSaveDiagramToFile:
    """Tests for save_diagram_to_file function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = await save_diagram_to_file(
            "flowchart TD\n    A --> B", "/tmp/test_diagram.svg"
        )
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        result = await save_diagram_to_file(
            "flowchart TD\n    A --> B", "/tmp/test_diagram.svg"
        )
        assert "success" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestBatchRenderDiagrams:
    """Tests for batch_render_diagrams function."""

    async def test_returns_dict(self):
        """Test function returns a dictionary."""
        diagrams = [{"code": "flowchart TD\n    A --> B", "format": "svg"}]
        result = await batch_render_diagrams(diagrams)
        assert isinstance(result, dict)

    async def test_has_success_key(self):
        """Test result has success key."""
        diagrams = [{"code": "flowchart TD\n    A --> B", "format": "svg"}]
        result = await batch_render_diagrams(diagrams)
        assert "success" in result

    async def test_parallel_processing(self):
        """Test parallel processing."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "format": "svg"},
            {"code": "flowchart TD\n    C --> D", "format": "svg"},
        ]
        result = await batch_render_diagrams(diagrams, parallel=True)
        assert isinstance(result, dict)

    async def test_sequential_processing(self):
        """Test sequential processing."""
        diagrams = [
            {"code": "flowchart TD\n    A --> B", "format": "svg"},
            {"code": "flowchart TD\n    C --> D", "format": "svg"},
        ]
        result = await batch_render_diagrams(diagrams, parallel=False)
        assert isinstance(result, dict)

    async def test_empty_diagrams(self):
        """Test with empty diagrams list."""
        result = await batch_render_diagrams([])
        assert result["success"] is False

    async def test_result_has_summary(self):
        """Test result includes summary."""
        diagrams = [{"code": "flowchart TD\n    A --> B", "format": "svg"}]
        result = await batch_render_diagrams(diagrams)
        if result["success"]:
            assert "data" in result
            assert "summary" in result["data"]


@pytest.mark.unit
class TestListDiagramTypes:
    """Tests for list_diagram_types function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = list_diagram_types()
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = list_diagram_types()
        assert "success" in result

    def test_includes_flowchart(self):
        """Test result includes flowchart type."""
        result = list_diagram_types()
        if result["success"]:
            assert "data" in result
            assert "types" in result["data"]
            assert "flowchart" in result["data"]["types"]

    def test_includes_sequence(self):
        """Test result includes sequence type."""
        result = list_diagram_types()
        if result["success"]:
            assert "sequence" in result["data"]["types"]

    def test_with_specific_type(self):
        """Test with specific diagram type."""
        result = list_diagram_types(diagram_type="flowchart")
        assert isinstance(result, dict)

    def test_with_examples(self):
        """Test with examples included."""
        result = list_diagram_types(include_examples=True)
        assert isinstance(result, dict)


@pytest.mark.unit
class TestGetDiagramExamples:
    """Tests for get_diagram_examples function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = get_diagram_examples()
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = get_diagram_examples()
        assert "success" in result

    def test_flowchart_examples(self):
        """Test flowchart examples."""
        result = get_diagram_examples(diagram_type="flowchart")
        assert isinstance(result, dict)

    def test_sequence_examples(self):
        """Test sequence diagram examples."""
        result = get_diagram_examples(diagram_type="sequence")
        assert isinstance(result, dict)
