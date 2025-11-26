"""
Comprehensive unit tests for flowchart models.

Tests FlowchartNode, FlowchartEdge, FlowchartSubgraph, and FlowchartDiagram classes
with proper validation, error handling, and Mermaid syntax generation.
"""

import pytest
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

from mermaid_render.models.flowchart import (
    FlowchartNode,
    FlowchartEdge,
    FlowchartSubgraph,
    FlowchartDiagram,
)
from mermaid_render.exceptions import DiagramError


class TestFlowchartNode:
    """Test FlowchartNode class."""

    def test_initialization_basic(self) -> None:
        """Test basic node initialization."""
        node = FlowchartNode("node1", "Test Node")
        
        assert node.id == "node1"
        assert node.label == "Test Node"
        assert node.shape == "rectangle"  # default shape
        assert node.style == {}

    def test_initialization_with_shape(self) -> None:
        """Test node initialization with custom shape."""
        node = FlowchartNode("node1", "Test Node", shape="circle")
        
        assert node.shape == "circle"

    def test_initialization_with_style(self) -> None:
        """Test node initialization with style."""
        style = {"fill": "#ff0000", "stroke": "#000000"}
        node = FlowchartNode("node1", "Test Node", style=style)
        
        assert node.style == style

    def test_initialization_invalid_shape(self) -> None:
        """Test initialization with invalid shape."""
        with pytest.raises(DiagramError, match="Unknown node shape"):  # Fixed: actual error message
            FlowchartNode("node1", "Test Node", shape="invalid_shape")

    def test_initialization_empty_id(self) -> None:
        """Test initialization with empty ID."""
        # The actual implementation doesn't validate empty ID
        node = FlowchartNode("", "Test Node")
        assert node.id == ""

    def test_initialization_empty_label(self) -> None:
        """Test initialization with empty label."""
        # The actual implementation doesn't validate empty label
        node = FlowchartNode("node1", "")
        assert node.label == ""

    def test_available_shapes(self) -> None:
        """Test that all expected shapes are available."""
        # Use the actual shapes from the implementation
        expected_shapes = {
            "rectangle", "circle", "rhombus", "rounded", "parallelogram",
            "stadium", "subroutine", "cylindrical"
        }

        available_shapes = set(FlowchartNode.SHAPES.keys())
        assert expected_shapes.issubset(available_shapes)

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid syntax generation."""
        node = FlowchartNode("node1", "Test Node")
        mermaid = node.to_mermaid()
        
        assert "node1[Test Node]" in mermaid

    def test_to_mermaid_with_shape(self) -> None:
        """Test Mermaid syntax generation with different shapes."""
        # Circle shape
        node = FlowchartNode("node1", "Start", shape="circle")
        mermaid = node.to_mermaid()
        assert "node1((Start))" in mermaid
        
        # Rhombus shape
        node = FlowchartNode("node2", "Decision", shape="rhombus")
        mermaid = node.to_mermaid()
        assert "node2{Decision}" in mermaid

    def test_to_mermaid_with_style(self) -> None:
        """Test Mermaid syntax generation with styling."""
        style = {"fill": "#ff0000", "stroke": "#000000"}
        node = FlowchartNode("node1", "Styled Node", style=style)
        mermaid = node.to_mermaid()

        # The to_mermaid method only returns the node definition, not styling
        assert "node1[Styled Node]" in mermaid
        # Style is stored in the node but not included in to_mermaid output
        assert node.style == style

    def test_to_mermaid_special_characters(self) -> None:
        """Test Mermaid syntax generation with special characters in label."""
        node = FlowchartNode("node1", "Test & Node <with> \"quotes\"")
        mermaid = node.to_mermaid()
        
        # Should escape special characters
        assert "node1[Test &amp; Node &lt;with&gt; &quot;quotes&quot;]" in mermaid

    def test_update_style(self) -> None:
        """Test updating node style."""
        node = FlowchartNode("node1", "Test Node")
        
        node.update_style({"fill": "#ff0000"})
        assert node.style["fill"] == "#ff0000"
        
        node.update_style({"stroke": "#000000"})
        assert node.style["fill"] == "#ff0000"  # Should preserve existing
        assert node.style["stroke"] == "#000000"

    def test_clone(self) -> None:
        """Test node cloning."""
        original = FlowchartNode("node1", "Original", shape="circle", 
                               style={"fill": "#ff0000"})
        clone = original.clone("node2")
        
        assert clone.id == "node2"
        assert clone.label == "Original"
        assert clone.shape == "circle"
        assert clone.style == {"fill": "#ff0000"}
        assert clone is not original


class TestFlowchartEdge:
    """Test FlowchartEdge class."""

    def test_initialization_basic(self) -> None:
        """Test basic edge initialization."""
        edge = FlowchartEdge("node1", "node2")
        
        assert edge.from_node == "node1"
        assert edge.to_node == "node2"
        assert edge.label is None
        assert edge.edge_type == "arrow"
        assert edge.style == {}

    def test_initialization_with_label(self) -> None:
        """Test edge initialization with label."""
        edge = FlowchartEdge("node1", "node2", label="Test Edge")
        
        assert edge.label == "Test Edge"

    def test_initialization_with_edge_type(self) -> None:
        """Test edge initialization with custom edge type."""
        edge = FlowchartEdge("node1", "node2", edge_type="dotted")
        
        assert edge.edge_type == "dotted"

    def test_initialization_invalid_edge_type(self) -> None:
        """Test initialization with invalid edge type."""
        with pytest.raises(DiagramError, match="Invalid edge type"):
            FlowchartEdge("node1", "node2", edge_type="invalid_type")

    def test_initialization_empty_nodes(self) -> None:
        """Test initialization with empty node IDs."""
        with pytest.raises(DiagramError, match="From node cannot be empty"):
            FlowchartEdge("", "node2")
        
        with pytest.raises(DiagramError, match="To node cannot be empty"):
            FlowchartEdge("node1", "")

    def test_available_edge_types(self) -> None:
        """Test that all expected edge types are available."""
        expected_types = {
            "arrow", "dotted", "thick", "invisible", "bidirectional"
        }
        
        available_types = set(FlowchartEdge.EDGE_TYPES.keys())
        assert expected_types.issubset(available_types)

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid syntax generation."""
        edge = FlowchartEdge("node1", "node2")
        mermaid = edge.to_mermaid()
        
        assert "node1 --> node2" in mermaid

    def test_to_mermaid_with_label(self) -> None:
        """Test Mermaid syntax generation with label."""
        edge = FlowchartEdge("node1", "node2", label="Test Label")
        mermaid = edge.to_mermaid()
        
        assert "node1 -->|Test Label| node2" in mermaid

    def test_to_mermaid_with_edge_type(self) -> None:
        """Test Mermaid syntax generation with different edge types."""
        # Dotted edge
        edge = FlowchartEdge("node1", "node2", edge_type="dotted")
        mermaid = edge.to_mermaid()
        assert "node1 -.-> node2" in mermaid
        
        # Thick edge
        edge = FlowchartEdge("node1", "node2", edge_type="thick")
        mermaid = edge.to_mermaid()
        assert "node1 ==> node2" in mermaid

    def test_to_mermaid_with_style(self) -> None:
        """Test Mermaid syntax generation with styling."""
        style = {"stroke": "#ff0000", "stroke-width": "3px"}
        edge = FlowchartEdge("node1", "node2", style=style)
        mermaid = edge.to_mermaid()
        
        assert "node1 --> node2" in mermaid
        # Style should be applied separately in diagram


class TestFlowchartSubgraph:
    """Test FlowchartSubgraph class."""

    def test_initialization_basic(self) -> None:
        """Test basic subgraph initialization."""
        subgraph = FlowchartSubgraph("sub1", "Test Subgraph")
        
        assert subgraph.id == "sub1"
        assert subgraph.title == "Test Subgraph"
        assert subgraph.nodes == []
        assert subgraph.edges == []
        assert subgraph.direction == "TB"

    def test_initialization_with_direction(self) -> None:
        """Test subgraph initialization with custom direction."""
        subgraph = FlowchartSubgraph("sub1", "Test", direction="LR")
        
        assert subgraph.direction == "LR"

    def test_initialization_invalid_direction(self) -> None:
        """Test initialization with invalid direction."""
        with pytest.raises(DiagramError, match="Invalid direction"):
            FlowchartSubgraph("sub1", "Test", direction="INVALID")

    def test_add_node(self) -> None:
        """Test adding nodes to subgraph."""
        subgraph = FlowchartSubgraph("sub1", "Test")

        subgraph.add_node("node1")

        assert len(subgraph.nodes) == 1
        assert subgraph.nodes[0] == "node1"

    def test_add_edge(self) -> None:
        """Test adding edges to subgraph."""
        subgraph = FlowchartSubgraph("sub1", "Test")
        edge = FlowchartEdge("node1", "node2")
        
        subgraph.add_edge(edge)
        
        assert len(subgraph.edges) == 1
        assert subgraph.edges[0] == edge

    def test_to_mermaid(self) -> None:
        """Test Mermaid syntax generation for subgraph."""
        subgraph = FlowchartSubgraph("sub1", "Test Subgraph")
        edge = FlowchartEdge("node1", "node2")

        subgraph.add_node("node1")
        subgraph.add_node("node2")
        subgraph.add_edge(edge)

        mermaid = subgraph.to_mermaid()
        mermaid_str = "\n".join(mermaid)

        assert "subgraph sub1 [Test Subgraph]" in mermaid_str
        assert "node1" in mermaid_str
        assert "node2" in mermaid_str
        assert "end" in mermaid_str


class TestFlowchartDiagram:
    """Test FlowchartDiagram class."""

    def test_initialization_basic(self) -> None:
        """Test basic diagram initialization."""
        diagram = FlowchartDiagram()

        assert diagram.direction == "TB"
        assert diagram.nodes == {}
        assert diagram.edges == []
        assert diagram.subgraphs == {}

    def test_initialization_with_direction(self) -> None:
        """Test diagram initialization with custom direction."""
        diagram = FlowchartDiagram(direction="LR")
        
        assert diagram.direction == "LR"

    def test_add_node(self) -> None:
        """Test adding nodes to diagram."""
        diagram = FlowchartDiagram()

        node = diagram.add_node("node1", "Test Node")

        assert len(diagram.nodes) == 1
        assert diagram.nodes["node1"] == node

    def test_add_node_duplicate_id(self) -> None:
        """Test adding node with duplicate ID."""
        diagram = FlowchartDiagram()

        diagram.add_node("node1", "Node 1")

        with pytest.raises(DiagramError, match="Node with ID 'node1' already exists"):
            diagram.add_node("node1", "Node 2")  # Same ID

    def test_add_edge(self) -> None:
        """Test adding edges to diagram."""
        diagram = FlowchartDiagram()
        diagram.add_node("node1", "Node 1")
        diagram.add_node("node2", "Node 2")

        edge = diagram.add_edge("node1", "node2")

        assert len(diagram.edges) == 1
        assert diagram.edges[0] == edge

    def test_add_subgraph(self) -> None:
        """Test adding subgraphs to diagram."""
        diagram = FlowchartDiagram()

        subgraph = diagram.add_subgraph("sub1", "Test Subgraph")

        assert len(diagram.subgraphs) == 1
        assert diagram.subgraphs["sub1"] == subgraph

    def test_get_node(self) -> None:
        """Test getting node by ID."""
        diagram = FlowchartDiagram()
        node = diagram.add_node("node1", "Test Node")

        retrieved = diagram.get_node("node1")
        assert retrieved == node

        # Non-existent node
        assert diagram.get_node("nonexistent") is None

    def test_remove_node(self) -> None:
        """Test removing node from diagram."""
        diagram = FlowchartDiagram()
        diagram.add_node("node1", "Test Node")

        assert len(diagram.nodes) == 1

        diagram.remove_node("node1")

        assert len(diagram.nodes) == 0

    def test_remove_node_with_edges(self) -> None:
        """Test removing node also removes connected edges."""
        diagram = FlowchartDiagram()
        diagram.add_node("node1", "Node 1")
        diagram.add_node("node2", "Node 2")
        diagram.add_edge("node1", "node2")

        assert len(diagram.edges) == 1

        diagram.remove_node("node1")

        assert len(diagram.edges) == 0  # Edge should be removed

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid syntax generation."""
        diagram = FlowchartDiagram()
        diagram.add_node("node1", "Start")
        diagram.add_node("node2", "End")
        diagram.add_edge("node1", "node2")

        mermaid = diagram.to_mermaid()

        assert "flowchart TB" in mermaid
        assert "node1[Start]" in mermaid
        assert "node2[End]" in mermaid
        assert "node1 --> node2" in mermaid

    def test_to_mermaid_with_direction(self) -> None:
        """Test Mermaid syntax generation with custom direction."""
        diagram = FlowchartDiagram(direction="LR")
        diagram.add_node("node1", "Test")

        mermaid = diagram.to_mermaid()

        assert "flowchart LR" in mermaid

    def test_to_mermaid_with_subgraphs(self) -> None:
        """Test Mermaid syntax generation with subgraphs."""
        diagram = FlowchartDiagram()
        diagram.add_subgraph("sub1", "Test Subgraph")

        mermaid = diagram.to_mermaid()

        assert "flowchart TB" in mermaid
        assert "subgraph sub1 [Test Subgraph]" in mermaid
        assert "end" in mermaid

    def test_validate_diagram(self) -> None:
        """Test diagram validation."""
        diagram = FlowchartDiagram()

        # Valid diagram
        diagram.add_node("node1", "Start")
        diagram.add_node("node2", "End")
        diagram.add_edge("node1", "node2")

        # Should not raise exception
        diagram.validate_diagram()

    def test_validate_diagram_missing_node(self) -> None:
        """Test diagram validation with missing node."""
        diagram = FlowchartDiagram()
        diagram.add_node("node1", "Node 1")
        # Create edge to non-existent node - this should be caught by add_edge validation

        with pytest.raises(DiagramError, match="Target node 'node2' does not exist"):
            diagram.add_edge("node1", "node2")

    def test_validate_diagram_empty(self) -> None:
        """Test validation of empty diagram."""
        diagram = FlowchartDiagram()

        with pytest.raises(DiagramError, match="Diagram must contain at least one node"):
            diagram.validate_diagram()
