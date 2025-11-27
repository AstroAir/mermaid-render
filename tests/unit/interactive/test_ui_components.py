"""
Unit tests for interactive.ui_components module.

Tests the UI component classes.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.ui_components import (
    CodeEditor,
    EdgeComponent,
    NodeComponent,
    PreviewPanel,
    PropertiesPanel,
    ToolboxComponent,
    UIComponent,
)


@pytest.mark.unit
class TestUIComponent:
    """Unit tests for UIComponent base class."""

    def test_initialization(self) -> None:
        """Test UIComponent initialization."""
        component = UIComponent(component_id="test")
        assert component.component_id == "test"

    def test_render(self) -> None:
        """Test component rendering."""
        component = UIComponent(component_id="test")
        html = component.render()
        assert html is not None


@pytest.mark.unit
class TestNodeComponent:
    """Unit tests for NodeComponent class."""

    def test_initialization(self) -> None:
        """Test NodeComponent initialization."""
        node = NodeComponent(node_id="node1", label="Test Node")
        assert node.node_id == "node1"
        assert node.label == "Test Node"

    def test_render(self) -> None:
        """Test node rendering."""
        node = NodeComponent(node_id="node1", label="Test")
        html = node.render()
        assert html is not None


@pytest.mark.unit
class TestEdgeComponent:
    """Unit tests for EdgeComponent class."""

    def test_initialization(self) -> None:
        """Test EdgeComponent initialization."""
        edge = EdgeComponent(source="node1", target="node2")
        assert edge.source == "node1"
        assert edge.target == "node2"

    def test_render(self) -> None:
        """Test edge rendering."""
        edge = EdgeComponent(source="a", target="b")
        html = edge.render()
        assert html is not None


@pytest.mark.unit
class TestToolboxComponent:
    """Unit tests for ToolboxComponent class."""

    def test_initialization(self) -> None:
        """Test ToolboxComponent initialization."""
        toolbox = ToolboxComponent()
        assert toolbox is not None

    def test_get_tools(self) -> None:
        """Test getting available tools."""
        toolbox = ToolboxComponent()
        tools = toolbox.get_tools()
        assert isinstance(tools, list)


@pytest.mark.unit
class TestPropertiesPanel:
    """Unit tests for PropertiesPanel class."""

    def test_initialization(self) -> None:
        """Test PropertiesPanel initialization."""
        panel = PropertiesPanel()
        assert panel is not None

    def test_set_element(self) -> None:
        """Test setting element for properties panel."""
        panel = PropertiesPanel()
        mock_element = Mock()
        panel.set_element(mock_element)
        assert panel.current_element == mock_element


@pytest.mark.unit
class TestCodeEditor:
    """Unit tests for CodeEditor class."""

    def test_initialization(self) -> None:
        """Test CodeEditor initialization."""
        editor = CodeEditor()
        assert editor is not None

    def test_set_code(self) -> None:
        """Test setting code in editor."""
        editor = CodeEditor()
        editor.set_code("flowchart TD\n    A --> B")
        assert editor.get_code() == "flowchart TD\n    A --> B"

    def test_get_code(self) -> None:
        """Test getting code from editor."""
        editor = CodeEditor()
        editor.set_code("graph LR")
        code = editor.get_code()
        assert code == "graph LR"


@pytest.mark.unit
class TestPreviewPanel:
    """Unit tests for PreviewPanel class."""

    def test_initialization(self) -> None:
        """Test PreviewPanel initialization."""
        panel = PreviewPanel()
        assert panel is not None

    def test_update_preview(self) -> None:
        """Test updating preview."""
        panel = PreviewPanel()
        panel.update_preview("flowchart TD\n    A --> B")
        # Should not raise
        assert True
