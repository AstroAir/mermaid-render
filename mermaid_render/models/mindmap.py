"""Mindmap diagram model for the Mermaid Render library."""

from typing import List, Optional

from ..core import MermaidDiagram


class MindmapNode:
    """Represents a node in a mindmap.

    Each node has an ID, display text, an optional shape, and a list of child nodes.
    """

    def __init__(self, id: str, text: str, shape: str = "default") -> None:
        """Initialize a mindmap node.

        Args:
            id: Unique identifier for the node.
            text: Display text for the node.
            shape: Optional Mermaid node shape ('default', 'circle', 'bang', 'cloud', 'hexagon').
        """
        self.id = id
        self.text = text
        self.shape = shape
        self.children: List[MindmapNode] = []

    def add_child(self, child: "MindmapNode") -> None:
        """Add a child node.

        Args:
            child: The MindmapNode to attach as a child.
        """
        self.children.append(child)

    def to_mermaid(self, level: int = 0) -> List[str]:
        """Generate Mermaid syntax lines for this node and its subtree.

        Args:
            level: Current indentation level based on depth in the tree.

        Returns:
            A list of Mermaid lines representing this node and descendants.
        """
        lines = []
        indent = "  " * level

        if self.shape == "circle":
            lines.append(f"{indent}(({self.text}))")
        elif self.shape == "bang":
            lines.append(f"{indent})){self.text}((")
        elif self.shape == "cloud":
            lines.append(f"{indent}))){self.text}(((")
        elif self.shape == "hexagon":
            lines.append(f"{indent})){self.text}((")
        else:
            lines.append(f"{indent}{self.text}")

        for child in self.children:
            lines.extend(child.to_mermaid(level + 1))

        return lines


class MindmapDiagram(MermaidDiagram):
    """Mindmap diagram model for hierarchical information.

    Manages a root node and provides helpers to add/find nodes and render Mermaid text.
    """

    def __init__(self, title: Optional[str] = None, root_text: str = "Root") -> None:
        """Initialize a mindmap diagram with a root node.

        Args:
            title: Optional diagram title.
            root_text: Text for the root node.
        """
        super().__init__(title)
        self.root = MindmapNode("root", root_text)

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "mindmap"

    def add_node(
        self, parent_id: str, node_id: str, text: str, shape: str = "default"
    ) -> MindmapNode:
        """Add a node to the mindmap under the given parent.

        Args:
            parent_id: ID of the parent node ('root' for the root).
            node_id: Unique ID for the new node.
            text: Display text for the new node.
            shape: Optional node shape.

        Returns:
            The created MindmapNode instance.
        """
        node = MindmapNode(node_id, text, shape)

        if parent_id == "root":
            self.root.add_child(node)
        else:
            # Find parent node (simple DFS)
            parent = self._find_node(self.root, parent_id)
            if parent:
                parent.add_child(node)

        return node

    def _find_node(self, current: MindmapNode, node_id: str) -> Optional[MindmapNode]:
        """Find a node by ID in the tree."""
        if current.id == node_id:
            return current

        for child in current.children:
            result = self._find_node(child, node_id)
            if result:
                return result

        return None

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the mindmap."""
        lines = ["mindmap"]

        if self.title:
            lines.append(f"  title: {self.title}")

        lines.extend(self.root.to_mermaid())

        return "\n".join(lines)
