"""
Flowchart diagram model for the Mermaid Render library.

This module provides an object-oriented interface for creating flowchart diagrams
with support for nodes, edges, subgraphs, and styling.
"""

from ..core import MermaidDiagram
from ..exceptions import DiagramError
from ..utils import escape_html
from .constants import ARROW_TYPES as _SHARED_ARROW_TYPES
from .constants import FLOWCHART_SHAPES


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

    # Use shared shapes from constants module
    SHAPES = FLOWCHART_SHAPES

    def __init__(
        self,
        id: str,
        label: str,
        shape: str = "rectangle",
        style: dict[str, str] | None = None,
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
        # Escape HTML entities in label for proper Mermaid rendering
        escaped_label = escape_html(self.label)
        return f"{self.id}{start}{escaped_label}{end}"

    def update_style(self, style_updates: dict[str, str]) -> None:
        """
        Update the node's style properties.

        Args:
            style_updates: Dictionary of style properties to update
        """
        self.style.update(style_updates)

    def clone(self, new_id: str) -> "FlowchartNode":
        """
        Create a copy of this node with a new ID.

        Args:
            new_id: The ID for the cloned node

        Returns:
            A new FlowchartNode instance with the same properties but different ID
        """
        return FlowchartNode(
            id=new_id, label=self.label, shape=self.shape, style=self.style.copy()
        )


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

    # Use shared arrow types from constants module
    ARROW_TYPES = _SHARED_ARROW_TYPES

    # Alias for backward compatibility with tests
    EDGE_TYPES = ARROW_TYPES

    def __init__(
        self,
        from_node: str,
        to_node: str,
        label: str | None = None,
        arrow_type: str = "arrow",
        edge_type: str | None = None,  # Backward compatibility
        style: dict[str, str] | None = None,
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
        # Validate node IDs
        if not from_node or not from_node.strip():
            raise DiagramError("From node cannot be empty")
        if not to_node or not to_node.strip():
            raise DiagramError("To node cannot be empty")

        # Handle backward compatibility with edge_type parameter
        if edge_type is not None:
            arrow_type = edge_type

        self.from_node = from_node
        self.to_node = to_node
        self.label = label
        self.arrow_type = arrow_type
        self.edge_type = arrow_type  # Backward compatibility property
        self.style = style or {}

        if arrow_type not in self.ARROW_TYPES:
            raise DiagramError(f"Invalid edge type: {arrow_type}")

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
        title: str | None = None,
        direction: str = "TB",  # Default direction to match tests
    ) -> None:
        """
        Initialize a subgraph.

        Args:
            id: Unique identifier for the subgraph
            title: Optional title for the subgraph
            direction: Optional flow direction (TD, LR, etc.)
        """
        # Validate direction if provided
        valid_directions = ["TD", "TB", "BT", "RL", "LR"]
        if direction is not None and direction not in valid_directions:
            raise DiagramError(f"Invalid direction: {direction}")

        self.id = id
        self.title = title
        self.direction = direction
        self.nodes: list[str] = []
        self.edges: list[FlowchartEdge] = []  # Add edges support

    def add_node(self, node_id: str) -> None:
        """Add a node to this subgraph."""
        if node_id not in self.nodes:
            self.nodes.append(node_id)

    def add_edge(self, edge: FlowchartEdge) -> None:
        """Add an edge to this subgraph."""
        self.edges.append(edge)

    def to_mermaid(self) -> list[str]:
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
        direction: str = "TB",  # Changed default to TB to match tests
        title: str | None = None,
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
        self.nodes: dict[str, FlowchartNode] = {}
        self.edges: list[FlowchartEdge] = []
        self.subgraphs: dict[str, FlowchartSubgraph] = {}
        self.styles: dict[str, dict[str, str]] = {}

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "flowchart"

    def add_node(
        self,
        id: str,
        label: str,
        shape: str = "rectangle",
        style: dict[str, str] | None = None,
    ) -> FlowchartNode:
        """
        Add a node to the flowchart.

        Creates a new node with the specified properties and adds it to the flowchart.
        Each node must have a unique identifier within the diagram.

        Args:
            id (str): Unique node identifier. Must be unique within the flowchart.
                Should follow Mermaid naming conventions (alphanumeric, underscores).
            label (str): Node display text that will be shown in the rendered diagram.
                Can contain spaces and special characters.
            shape (str, optional): Node shape type. Supported shapes include:
                - "rectangle": Standard rectangular node (default)
                - "circle": Circular node
                - "diamond": Diamond-shaped decision node
                - "rounded": Rounded rectangle
                - "stadium": Stadium-shaped node
                - "subroutine": Subroutine node with side lines
                - "cylindrical": Database/storage node
                - "hexagon": Hexagonal node
                Defaults to "rectangle".
            style (Optional[Dict[str, str]], optional): CSS-style properties for
                custom node styling. Can include properties like:
                - "fill": Background color
                - "stroke": Border color
                - "stroke-width": Border width
                - "color": Text color
                Defaults to None (uses theme defaults).

        Returns:
            FlowchartNode: The created node object, which can be used for further
            customization or reference.

        Raises:
            DiagramError: If a node with the same ID already exists in the flowchart.

        Examples:
            Basic node creation:
            >>> flowchart = FlowchartDiagram()
            >>> start_node = flowchart.add_node("start", "Start Process")
            >>> print(start_node.id)
            start

            Different node shapes:
            >>> flowchart.add_node("decision", "Is Valid?", shape="diamond")
            >>> flowchart.add_node("process", "Process Data", shape="rectangle")
            >>> flowchart.add_node("end", "End", shape="circle")

            Custom styling:
            >>> style = {"fill": "#ff6b6b", "stroke": "#000", "color": "#fff"}
            >>> error_node = flowchart.add_node("error", "Error!", style=style)

            Building a complete workflow:
            >>> workflow = FlowchartDiagram(title="User Registration")
            >>> workflow.add_node("start", "User Submits Form", shape="circle")
            >>> workflow.add_node("validate", "Validate Input", shape="rectangle")
            >>> workflow.add_node("check", "Valid Data?", shape="diamond")
            >>> workflow.add_node("save", "Save User", shape="rectangle")
            >>> workflow.add_node("error", "Show Error", shape="rectangle")
            >>> workflow.add_node("end", "Registration Complete", shape="circle")
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
        label: str | None = None,
        arrow_type: str = "arrow",
        style: dict[str, str] | None = None,
    ) -> FlowchartEdge:
        """
        Add an edge (connection) between two nodes in the flowchart.

        Creates a directed connection from one node to another, optionally with
        a label and custom styling. Both nodes must already exist in the flowchart.

        Args:
            from_node (str): Source node identifier. Must be an existing node ID
                in the flowchart.
            to_node (str): Target node identifier. Must be an existing node ID
                in the flowchart.
            label (Optional[str], optional): Text label to display on the edge.
                Useful for decision branches or process descriptions.
                Defaults to None (no label).
            arrow_type (str, optional): Type of arrow/connection. Supported types:
                - "arrow": Standard arrow (-->)
                - "open": Open arrow (---)
                - "dotted": Dotted line (-.-.)
                - "thick": Thick arrow (==>)
                Defaults to "arrow".
            style (Optional[Dict[str, str]], optional): CSS-style properties for
                custom edge styling. Can include properties like:
                - "stroke": Line color
                - "stroke-width": Line thickness
                - "stroke-dasharray": Dash pattern
                Defaults to None (uses theme defaults).

        Returns:
            FlowchartEdge: The created edge object representing the connection
            between the two nodes.

        Raises:
            DiagramError: If either the source or target node doesn't exist
                in the flowchart.

        Examples:
            Basic edge creation:
            >>> flowchart = FlowchartDiagram()
            >>> flowchart.add_node("A", "Start")
            >>> flowchart.add_node("B", "End")
            >>> edge = flowchart.add_edge("A", "B")

            Edge with label:
            >>> flowchart.add_node("decision", "Valid?", shape="diamond")
            >>> flowchart.add_node("success", "Process")
            >>> flowchart.add_node("error", "Error")
            >>> flowchart.add_edge("decision", "success", label="Yes")
            >>> flowchart.add_edge("decision", "error", label="No")

            Different arrow types:
            >>> flowchart.add_edge("A", "B", arrow_type="dotted")
            >>> flowchart.add_edge("B", "C", arrow_type="thick")

            Custom styling:
            >>> style = {"stroke": "#ff0000", "stroke-width": "3px"}
            >>> flowchart.add_edge("error", "retry", label="Retry", style=style)

            Building a complete flow:
            >>> workflow = FlowchartDiagram(title="Order Processing")
            >>> workflow.add_node("start", "Order Received", shape="circle")
            >>> workflow.add_node("validate", "Validate Order")
            >>> workflow.add_node("check", "Stock Available?", shape="diamond")
            >>> workflow.add_node("fulfill", "Fulfill Order")
            >>> workflow.add_node("backorder", "Create Backorder")
            >>> workflow.add_node("end", "Complete", shape="circle")
            >>>
            >>> workflow.add_edge("start", "validate")
            >>> workflow.add_edge("validate", "check")
            >>> workflow.add_edge("check", "fulfill", label="Yes")
            >>> workflow.add_edge("check", "backorder", label="No")
            >>> workflow.add_edge("fulfill", "end")
            >>> workflow.add_edge("backorder", "end")
        """
        if from_node not in self.nodes:
            raise DiagramError(f"Source node '{from_node}' does not exist")
        if to_node not in self.nodes:
            raise DiagramError(f"Target node '{to_node}' does not exist")

        edge = FlowchartEdge(from_node, to_node, label, arrow_type, style=style)
        self.edges.append(edge)
        return edge

    def add_subgraph(
        self,
        id: str,
        title: str | None = None,
        direction: str = "TB",
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

    def get_node(self, node_id: str) -> FlowchartNode | None:
        """Get a node by its ID."""
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all edges connected to it."""
        if node_id not in self.nodes:
            raise DiagramError(f"Node '{node_id}' does not exist")

        # Remove the node
        del self.nodes[node_id]

        # Remove all edges connected to this node
        self.edges = [
            edge
            for edge in self.edges
            if edge.from_node != node_id and edge.to_node != node_id
        ]

    def add_style(self, element_id: str, style: dict[str, str]) -> None:
        """Add styling to a node or edge."""
        self.styles[element_id] = style

    def validate_diagram(self) -> None:
        """
        Validate the diagram structure.

        Raises:
            DiagramError: If the diagram is invalid
        """
        if not self.nodes:
            raise DiagramError("Diagram must contain at least one node")

        # Validate that all edges reference existing nodes
        for edge in self.edges:
            if edge.from_node not in self.nodes:
                raise DiagramError(
                    f"Edge references non-existent source node: {edge.from_node}"
                )
            if edge.to_node not in self.nodes:
                raise DiagramError(
                    f"Edge references non-existent target node: {edge.to_node}"
                )

    def _generate_mermaid(self) -> str:
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
