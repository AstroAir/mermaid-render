"""
Unit tests for interactive.ui_components module.

Tests the UI component classes.
"""

import pytest

from diagramaid.interactive.ui_components import (
    CodeEditor,
    EdgeComponent,
    NodeComponent,
    PreviewPanel,
    PropertiesPanel,
    ToolboxComponent,
)


@pytest.mark.unit
class TestNodeComponent:
    """Unit tests for NodeComponent class."""

    def test_initialization(self) -> None:
        """Test NodeComponent initialization."""
        node = NodeComponent(node_type="rectangle", label="Test Node")
        assert node.component_type == "node"
        assert node.properties["label"] == "Test Node"

    def test_render(self) -> None:
        """Test node rendering."""
        node = NodeComponent(node_type="rectangle", label="Test")
        result = node.render()
        assert result is not None
        assert result["type"] == "node"


@pytest.mark.unit
class TestEdgeComponent:
    """Unit tests for EdgeComponent class."""

    def test_initialization(self) -> None:
        """Test EdgeComponent initialization."""
        edge = EdgeComponent(edge_type="arrow")
        assert edge.component_type == "edge"
        assert edge.properties["edge_type"] == "arrow"

    def test_render(self) -> None:
        """Test edge rendering."""
        edge = EdgeComponent(edge_type="line")
        result = edge.render()
        assert result is not None
        assert result["type"] == "edge"


@pytest.mark.unit
class TestToolboxComponent:
    """Unit tests for ToolboxComponent class."""

    def test_initialization(self) -> None:
        """Test ToolboxComponent initialization."""
        toolbox = ToolboxComponent()
        assert toolbox is not None
        assert toolbox.component_type == "toolbox"

    def test_has_tools(self) -> None:
        """Test that toolbox has tools."""
        toolbox = ToolboxComponent()
        assert hasattr(toolbox, "tools")
        assert isinstance(toolbox.tools, list)

    def test_render(self) -> None:
        """Test toolbox rendering."""
        toolbox = ToolboxComponent()
        result = toolbox.render()
        assert result is not None
        assert "tools" in result


@pytest.mark.unit
class TestPropertiesPanel:
    """Unit tests for PropertiesPanel class."""

    def test_initialization(self) -> None:
        """Test PropertiesPanel initialization."""
        panel = PropertiesPanel()
        assert panel is not None
        assert panel.component_type == "properties"

    def test_render(self) -> None:
        """Test properties panel rendering."""
        panel = PropertiesPanel()
        result = panel.render()
        assert result is not None


@pytest.mark.unit
class TestCodeEditor:
    """Unit tests for CodeEditor class."""

    def test_initialization(self) -> None:
        """Test CodeEditor initialization."""
        editor = CodeEditor()
        assert editor is not None
        assert editor.component_type == "code_editor"

    def test_render(self) -> None:
        """Test code editor rendering."""
        editor = CodeEditor()
        result = editor.render()
        assert result is not None


@pytest.mark.unit
class TestPreviewPanel:
    """Unit tests for PreviewPanel class."""

    def test_initialization(self) -> None:
        """Test PreviewPanel initialization."""
        panel = PreviewPanel()
        assert panel is not None
        assert panel.component_type == "preview"

    def test_render(self) -> None:
        """Test preview panel rendering."""
        panel = PreviewPanel()
        result = panel.render()
        assert result is not None
