"""
UI components for the interactive diagram builder.

This module provides the building blocks for the web-based interface
including toolboxes, property panels, and editor components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class UIComponent(ABC):
    """Base class for UI components."""

    component_id: str
    component_type: str
    properties: Dict[str, Any]

    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """Render component to dictionary representation."""
        pass


@dataclass
class NodeComponent(UIComponent):
    """Node component for diagram elements."""

    def __init__(self, node_type: str, label: str, **properties: Any) -> None:
        super().__init__(
            component_id=f"node_{node_type}",
            component_type="node",
            properties={"node_type": node_type, "label": label, **properties},
        )

    def render(self) -> Dict[str, Any]:
        return {
            "id": self.component_id,
            "type": self.component_type,
            "properties": self.properties,
            "template": "node_component.html",
        }


@dataclass
class EdgeComponent(UIComponent):
    """Edge component for connections."""

    def __init__(self, edge_type: str, **properties: Any) -> None:
        super().__init__(
            component_id=f"edge_{edge_type}",
            component_type="edge",
            properties={"edge_type": edge_type, **properties},
        )

    def render(self) -> Dict[str, Any]:
        return {
            "id": self.component_id,
            "type": self.component_type,
            "properties": self.properties,
            "template": "edge_component.html",
        }


class ToolboxComponent(UIComponent):
    """Toolbox component with available tools."""

    def __init__(self) -> None:
        super().__init__(
            component_id="toolbox", component_type="toolbox", properties={}
        )
        self.tools: List[Dict[str, Any]] = self._get_default_tools()

    def render(self) -> Dict[str, Any]:
        return {
            "id": self.component_id,
            "type": self.component_type,
            "tools": self.tools,
            "template": "toolbox.html",
        }

    def _get_default_tools(self) -> List[Dict[str, Any]]:
        return [
            {"id": "select", "name": "Select", "icon": "cursor"},
            {"id": "rectangle", "name": "Rectangle", "icon": "square"},
            {"id": "circle", "name": "Circle", "icon": "circle"},
            {"id": "diamond", "name": "Diamond", "icon": "diamond"},
            {"id": "connection", "name": "Connection", "icon": "arrow-right"},
        ]


class PropertiesPanel(UIComponent):
    """Properties panel for editing element properties."""

    def __init__(self) -> None:
        super().__init__(
            component_id="properties", component_type="properties", properties={}
        )
        self.selected_element: Optional[Dict[str, Any]] = None

    def render(self) -> Dict[str, Any]:
        return {
            "id": self.component_id,
            "type": self.component_type,
            "selected_element": self.selected_element,
            "template": "properties_panel.html",
        }

    def set_selected_element(self, element: Dict[str, Any]) -> None:
        self.selected_element = element


class CodeEditor(UIComponent):
    """Code editor component for Mermaid code."""

    def __init__(self) -> None:
        super().__init__(
            component_id="code_editor",
            component_type="code_editor",
            properties={"language": "mermaid", "theme": "default"},
        )
        self.code: str = ""

    def render(self) -> Dict[str, Any]:
        return {
            "id": self.component_id,
            "type": self.component_type,
            "code": self.code,
            "properties": self.properties,
            "template": "code_editor.html",
        }

    def set_code(self, code: str) -> None:
        self.code = code


class PreviewPanel(UIComponent):
    """Preview panel for rendered diagrams."""

    def __init__(self) -> None:
        super().__init__(
            component_id="preview",
            component_type="preview",
            properties={"format": "svg", "auto_update": True},
        )
        self.preview_content: str = ""

    def render(self) -> Dict[str, Any]:
        return {
            "id": self.component_id,
            "type": self.component_type,
            "content": self.preview_content,
            "properties": self.properties,
            "template": "preview_panel.html",
        }

    def set_preview_content(self, content: str) -> None:
        self.preview_content = content
