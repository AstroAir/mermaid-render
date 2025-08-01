"""
Flowchart diagram model for the Mermaid Render library.

This module provides an object-oriented interface for creating flowchart diagrams
with support for nodes, edges, subgraphs, and styling.
"""

from typing import Dict, List, Optional

from ..core import MermaidDiagram
from ..exceptions import DiagramError


class FlowchartNode:
    """
    Represents a node in a flowchart diagram.

    A flowchart node is a visual element that represents a step, decision, or
    process in a workflow. Each node has a unique identifier, display label,
    shape, and optional styling.

    The shape of the node conveys semantic meaning:
    - rectangle: Standard process step
    - circle: Start/end points
    - rhombus: Decision points
    - rounded: Subprocess or rounded process
    - parallelogram: Input/output operations

    Attributes:
        SHAPES (Dict[str, Tuple[str, str]]): Available node shapes with their
            Mermaid syntax delimiters
        id (str): Unique identifier for the node
        label (str): Display text shown in the node
        shape (str): Visual shape of the node
        style (Dict[str, str]): CSS-like styling properties

    Example:
        >>> # Create a simple process node
        >>> node = FlowchartNode("process1", "Validate Input", shape="rectangle")
        >>>
        >>> # Create a decision node
        >>> decision = FlowchartNode("check1", "Valid?", shape="rhombus")
        >>>
        >>> # Create a styled node
        >>> start = FlowchartNode("start", "Begin", shape="circle",
        ...                      style={"fill": "#90EE90"})
    """

    SHAPES = {
        "rectangle": ("[", "]"),        # Standard process
        "rounded": ("(", ")"),          # Rounded process
        "stadium": ("([", "])"),        # Stadium shape
        "subroutine": ("[[", "]]"),     # Subroutine/subprocess
        "cylindrical": ("[(", ")]"),    # Database/storage
        "circle": ("((", "))"),         # Start/end point
        "asymmetric": (">", "]"),       # Asymmetric shape
        "rhombus": ("{", "}"),          # Decision point
        "hexagon": ("{{", "}}"),        # Hexagonal process
        "parallelogram": ("[/", "/]"),  # Input/output
        "parallelogram_alt": ("[\\", "\\]"),  # Alternative input/output
        "trapezoid": ("[/", "\\]"),     # Manual operation
        "trapezoid_alt": ("[\\", "/]"), # Alternative manual operation
    }

    def __init__(
        self,
        id: str,
        label: str,
        shape: str = "rectangle",
        style: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize a flowchart node.

        Args:
            id: Unique identifier for the node. Must be unique within the diagram
                and follow Mermaid naming conventions (alphanumeric, no spaces)
            label: Display text for the node. This is what users will see in the
                rendered diagram
            shape: Node shape that determines visual appearance and semantic meaning.
                Must be one of the keys in SHAPES dictionary
            style: Optional CSS-like styling properties such as:
                - fill: Background color
                - stroke: Border color
                - stroke-width: Border width
                - color: Text color

        Raises:
            DiagramError: If the specified shape is not supported

        Example:
            >>> # Basic node
            >>> node = FlowchartNode("step1", "Process Data")
            >>>
            >>> # Decision node with custom styling
            >>> decision = FlowchartNode(
            ...     "decision1",
            ...     "Is Valid?",
            ...     shape="rhombus",
            ...     style={"fill": "#ffeb3b", "stroke": "#f57c00"}
            ... )
        """
        self.id = id
        self.label = label
        self.shape = shape
        self.style = style or {}

        if shape not in self.SHAPES:
            raise DiagramError(f"Unknown node shape: {shape}")

    def to_mermaid(self) -> str:
        """
        Generate Mermaid syntax for this node.

        Returns:
            Mermaid syntax string representing this node

        Example:
            >>> node = FlowchartNode("A", "Start", shape="circle")
            >>> print(node.to_mermaid())
            A((Start))

            >>> process = FlowchartNode("B", "Process Data", shape="rectangle")
            >>> print(process.to_mermaid())
            B[Process Data]
        """
        start, end = self.SHAPES[self.shape]
        return f"{self.id}{start}{self.label}{end}"


class FlowchartEdge:
    """
    Represents an edge (connection) between nodes in a flowchart.

    An edge defines the flow direction and relationship between two nodes in a
    flowchart. Edges can have different visual styles to convey different types
    of relationships or flow conditions.

    Edge types and their meanings:
    - arrow (-->): Standard directional flow
    - open (---): Non-directional connection
    - dotted (-.-): Conditional or optional flow
    - dotted_arrow (-.->): Conditional directional flow
    - thick (==>): Emphasized or primary flow
    - thick_open (===): Emphasized non-directional connection

    Attributes:
        ARROW_TYPES (Dict[str, str]): Available arrow types with their Mermaid syntax
        from_node (str): Source node identifier
        to_node (str): Target node identifier
        label (Optional[str]): Optional text label for the edge
        arrow_type (str): Visual style of the connection
        style (Dict[str, str]): CSS-like styling properties

    Example:
        >>> # Simple connection
        >>> edge = FlowchartEdge("A", "B")
        >>>
        >>> # Labeled decision edge
        >>> yes_edge = FlowchartEdge("decision", "process", label="Yes", arrow_type="arrow")
        >>>
        >>> # Styled edge
        >>> important_edge = FlowchartEdge("start", "critical",
        ...                              arrow_type="thick",
        ...                              style={"stroke": "#ff0000"})
    """

    ARROW_TYPES = {
        "arrow": "-->",         # Standard directional arrow
        "open": "---",          # Open line (no arrow)
        "dotted": "-.-",        # Dotted line
        "dotted_arrow": "-.->", # Dotted arrow
        "thick": "==>",         # Thick arrow
        "thick_open": "===",    # Thick open line
    }

    def __init__(
        self,
        from_node: str,
        to_node: str,
        label: Optional[str] = None,
        arrow_type: str = "arrow",
        style: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize a flowchart edge.

        Args:
            from_node: Source node ID. Must match an existing node's ID
            to_node: Target node ID. Must match an existing node's ID
            label: Optional text label displayed on the edge. Commonly used
                for decision outcomes like "Yes", "No", or conditions
            arrow_type: Type of arrow/connection. Must be one of the keys
                in ARROW_TYPES dictionary
            style: Optional CSS-like styling properties such as:
                - stroke: Line color
                - stroke-width: Line thickness
                - stroke-dasharray: Dash pattern

        Raises:
            DiagramError: If the specified arrow_type is not supported

        Example:
            >>> # Basic edge
            >>> edge = FlowchartEdge("start", "process")
            >>>
            >>> # Decision edge with label
            >>> yes_path = FlowchartEdge("check", "proceed", label="Valid")
            >>> no_path = FlowchartEdge("check", "error", label="Invalid")
            >>>
            >>> # Styled conditional edge
            >>> optional = FlowchartEdge("A", "B", label="Optional",
            ...                         arrow_type="dotted_arrow",
            ...                         style={"stroke": "#888888"})
        """
        self.from_node = from_node
        self.to_node = to_node
        self.label = label
        self.arrow_type = arrow_type
        self.style = style or {}

        if arrow_type not in self.ARROW_TYPES:
            raise DiagramError(f"Unknown arrow type: {arrow_type}")

    def to_mermaid(self) -> str:
        """Generate Mermaid syntax for this edge."""
        arrow = self.ARROW_TYPES[self.arrow_type]

        if self.label:
            # Insert label in the middle of the arrow
            return f"{self.from_node} -->|{self.label}| {self.to_node}"
        else:
            return f"{self.from_node} {arrow} {self.to_node}"


class FlowchartSubgraph:
    """Represents a subgraph (grouped nodes) in a flowchart."""

    def __init__(
        self,
        id: str,
        title: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> None:
        """
        Initialize a subgraph.

        Args:
            id: Unique identifier for the subgraph
            title: Optional title for the subgraph
            direction: Optional flow direction (TD, LR, etc.)
        """
        self.id = id
        self.title = title
        self.direction = direction
        self.nodes: List[str] = []

    def add_node(self, node_id: str) -> None:
        """Add a node to this subgraph."""
        if node_id not in self.nodes:
            self.nodes.append(node_id)

    def to_mermaid(self) -> List[str]:
        """Generate Mermaid syntax for this subgraph."""
        lines = []

        # Start subgraph
        if self.title:
            lines.append(f"subgraph {self.id} [{self.title}]")
        else:
            lines.append(f"subgraph {self.id}")

        # Add direction if specified
        if self.direction:
            lines.append(f"    direction {self.direction}")

        # Add nodes (they should be defined elsewhere)
        for node_id in self.nodes:
            lines.append(f"    {node_id}")

        # End subgraph
        lines.append("end")

        return lines


class FlowchartDiagram(MermaidDiagram):
    """
    Flowchart diagram model with support for nodes, edges, and subgraphs.

    Example:
        >>> flowchart = FlowchartDiagram(direction="TD")
        >>> flowchart.add_node("A", "Start", shape="circle")
        >>> flowchart.add_node("B", "Process", shape="rectangle")
        >>> flowchart.add_edge("A", "B", label="Begin")
        >>> print(flowchart.to_mermaid())
    """

    DIRECTIONS = ["TD", "TB", "BT", "RL", "LR"]

    def __init__(
        self,
        direction: str = "TD",
        title: Optional[str] = None,
    ) -> None:
        """
        Initialize flowchart diagram.

        Args:
            direction: Flow direction (TD, LR, etc.)
            title: Optional diagram title
        """
        super().__init__(title)

        if direction not in self.DIRECTIONS:
            raise DiagramError(f"Invalid direction: {direction}")

        self.direction = direction
        self.nodes: Dict[str, FlowchartNode] = {}
        self.edges: List[FlowchartEdge] = []
        self.subgraphs: Dict[str, FlowchartSubgraph] = {}
        self.styles: Dict[str, Dict[str, str]] = {}

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "flowchart"

    def add_node(
        self,
        id: str,
        label: str,
        shape: str = "rectangle",
        style: Optional[Dict[str, str]] = None,
    ) -> FlowchartNode:
        """
        Add a node to the flowchart.

        Args:
            id: Unique node identifier
            label: Node display text
            shape: Node shape
            style: Optional styling

        Returns:
            The created FlowchartNode
        """
        if id in self.nodes:
            raise DiagramError(f"Node with ID '{id}' already exists")

        node = FlowchartNode(id, label, shape, style)
        self.nodes[id] = node
        return node

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        label: Optional[str] = None,
        arrow_type: str = "arrow",
        style: Optional[Dict[str, str]] = None,
    ) -> FlowchartEdge:
        """
        Add an edge between two nodes.

        Args:
            from_node: Source node ID
            to_node: Target node ID
            label: Optional edge label
            arrow_type: Type of arrow/connection
            style: Optional styling

        Returns:
            The created FlowchartEdge
        """
        if from_node not in self.nodes:
            raise DiagramError(f"Source node '{from_node}' does not exist")
        if to_node not in self.nodes:
            raise DiagramError(f"Target node '{to_node}' does not exist")

        edge = FlowchartEdge(from_node, to_node, label, arrow_type, style)
        self.edges.append(edge)
        return edge

    def add_subgraph(
        self,
        id: str,
        title: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> FlowchartSubgraph:
        """
        Add a subgraph to group nodes.

        Args:
            id: Unique subgraph identifier
            title: Optional subgraph title
            direction: Optional flow direction

        Returns:
            The created FlowchartSubgraph
        """
        if id in self.subgraphs:
            raise DiagramError(f"Subgraph with ID '{id}' already exists")

        subgraph = FlowchartSubgraph(id, title, direction)
        self.subgraphs[id] = subgraph
        return subgraph

    def add_node_to_subgraph(self, node_id: str, subgraph_id: str) -> None:
        """Add a node to a subgraph."""
        if node_id not in self.nodes:
            raise DiagramError(f"Node '{node_id}' does not exist")
        if subgraph_id not in self.subgraphs:
            raise DiagramError(f"Subgraph '{subgraph_id}' does not exist")

        self.subgraphs[subgraph_id].add_node(node_id)

    def add_style(self, element_id: str, style: Dict[str, str]) -> None:
        """Add styling to a node or edge."""
        self.styles[element_id] = style

    def to_mermaid(self) -> str:
        """Generate complete Mermaid syntax for the flowchart."""
        lines = []

        # Start with diagram type and direction
        lines.append(f"flowchart {self.direction}")

        # Add title if present
        if self.title:
            lines.append(f"    title: {self.title}")

        # Add nodes
        for node in self.nodes.values():
            lines.append(f"    {node.to_mermaid()}")

        # Add edges
        for edge in self.edges:
            lines.append(f"    {edge.to_mermaid()}")

        # Add subgraphs
        for subgraph in self.subgraphs.values():
            subgraph_lines = subgraph.to_mermaid()
            for line in subgraph_lines:
                lines.append(f"    {line}")

        # Add styles
        for element_id, style in self.styles.items():
            style_str = ",".join([f"{k}:{v}" for k, v in style.items()])
            lines.append(f"    style {element_id} {style_str}")

        return "\n".join(lines)
