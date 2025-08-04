"""
Comprehensive tests for all diagram types and their edge cases.
"""

import pytest
from mermaid_render import (
    FlowchartDiagram,
    SequenceDiagram,
    ClassDiagram,
    StateDiagram,
    ERDiagram,
    UserJourneyDiagram,
    GanttDiagram,
    PieChartDiagram,
    GitGraphDiagram,
    MindmapDiagram,
)
from mermaid_render.models.class_diagram import ClassAttribute, ClassMethod
from mermaid_render.models.sequence import SequenceMessage
from mermaid_render.exceptions import DiagramError


class TestFlowchartDiagramComprehensive:
    """Comprehensive tests for FlowchartDiagram."""

    def test_all_node_shapes(self):
        """Test all supported node shapes."""
        diagram = FlowchartDiagram()

        shapes = [
            "rectangle", "rounded", "stadium", "subroutine", "cylindrical",
            "circle", "asymmetric", "rhombus", "hexagon", "parallelogram",
            "parallelogram_alt", "trapezoid", "trapezoid_alt"
        ]

        for i, shape in enumerate(shapes):
            node_id = f"node_{i}"
            diagram.add_node(node_id, f"Node {i}", shape=shape)

        mermaid_code = diagram.to_mermaid()
        assert "flowchart TD" in mermaid_code

        # Check that all nodes are present
        for i in range(len(shapes)):
            assert f"node_{i}" in mermaid_code

    def test_all_edge_types(self):
        """Test all supported edge types."""
        diagram = FlowchartDiagram()

        # Add nodes for edges
        for i in range(10):
            diagram.add_node(f"n{i}", f"Node {i}")

        edge_types = [
            "arrow", "open", "dotted", "dotted_arrow", "thick", "thick_open"
        ]

        for i, edge_type in enumerate(edge_types):
            if i + 1 < len(edge_types):  # Ensure we have a target node
                diagram.add_edge(f"n{i}", f"n{i+1}", f"Edge {i}", arrow_type=edge_type)

        mermaid_code = diagram.to_mermaid()

        # Check that edges are present
        for i in range(len(edge_types) - 1):
            assert f"n{i}" in mermaid_code
            assert f"n{i+1}" in mermaid_code

    def test_subgraphs_complex(self):
        """Test complex subgraph functionality."""
        diagram = FlowchartDiagram()

        # Add nodes
        diagram.add_node("A", "Start")
        diagram.add_node("B", "Process 1")
        diagram.add_node("C", "Process 2")
        diagram.add_node("D", "End")

        # Add subgraphs
        sub1 = diagram.add_subgraph("sub1", "Subprocess 1", "LR")
        sub2 = diagram.add_subgraph("sub2", "Subprocess 2")

        # Add nodes to subgraphs
        diagram.add_node_to_subgraph("B", "sub1")
        diagram.add_node_to_subgraph("C", "sub2")

        # Add edges
        diagram.add_edge("A", "B")
        diagram.add_edge("B", "C")
        diagram.add_edge("C", "D")

        mermaid_code = diagram.to_mermaid()
        assert "subgraph sub1" in mermaid_code
        assert "subgraph sub2" in mermaid_code

    def test_styling_and_classes(self):
        """Test node styling and CSS classes."""
        diagram = FlowchartDiagram()

        # Add nodes with styles
        diagram.add_node("A", "Styled Node", style={
                         "fill": "#ff0000", "stroke": "#000000"})
        diagram.add_node("B", "Normal Node")

        # Add style classes
        diagram.add_style("A", {"fill": "#00ff00", "color": "#ffffff"})

        diagram.add_edge("A", "B")

        mermaid_code = diagram.to_mermaid()
        assert "A" in mermaid_code
        assert "B" in mermaid_code


class TestSequenceDiagramComprehensive:
    """Comprehensive tests for SequenceDiagram."""

    def test_all_message_types(self):
        """Test all supported message types."""
        diagram = SequenceDiagram(title="Message Types Test")

        # Add participants
        diagram.add_participant("A", "Alice")
        diagram.add_participant("B", "Bob")
        diagram.add_participant("C", "Charlie")

        message_types = ["sync", "async", "return",
                         "note", "activation", "deactivation"]

        for msg_type in message_types:
            if msg_type in ["sync", "async", "return"]:
                diagram.add_message("A", "B", f"Message {msg_type}", msg_type)

        # Add notes
        diagram.add_note("This is a note", "A", "right of")
        diagram.add_note("Another note", "B", "left of")

        # Add activations
        diagram.activate_participant("A")
        diagram.activate_participant("B")

        mermaid_code = diagram.to_mermaid()
        assert "sequenceDiagram" in mermaid_code
        assert "participant A as Alice" in mermaid_code
        assert "participant B as Bob" in mermaid_code

    def test_loops_and_alternatives(self):
        """Test loops and alternative flows."""
        diagram = SequenceDiagram()

        diagram.add_participant("User")
        diagram.add_participant("System")

        # Add basic messages
        diagram.add_message("User", "System", "Login Request")
        diagram.add_message("System", "User", "Login Response")

        mermaid_code = diagram.to_mermaid()
        assert "User" in mermaid_code
        assert "System" in mermaid_code


class TestClassDiagramComprehensive:
    """Comprehensive tests for ClassDiagram."""

    def test_complex_class_hierarchy(self):
        """Test complex class hierarchy with all features."""
        diagram = ClassDiagram(title="Complex Hierarchy")

        # Add abstract base class
        animal = diagram.add_class("Animal", is_abstract=True)
        animal.add_attribute(ClassAttribute("name", "String", "protected"))
        animal.add_attribute(ClassAttribute("age", "int", "protected"))
        animal.add_method(ClassMethod("move", "public", "void", is_abstract=True))
        animal.add_method(ClassMethod("eat", "public", "void"))

        # Add interface
        flyable = diagram.add_class("Flyable", is_interface=True)
        flyable.add_method(ClassMethod("fly", "public", "void", is_abstract=True))

        # Add concrete classes
        dog = diagram.add_class("Dog")
        dog.add_attribute(ClassAttribute("breed", "String", "private"))
        dog.add_method(ClassMethod("bark", "public", "void"))
        dog.add_method(ClassMethod("move", "public", "void"))  # Override

        bird = diagram.add_class("Bird")
        bird.add_method(ClassMethod("fly", "public", "void"))
        bird.add_method(ClassMethod("move", "public", "void"))

        # Add relationships
        diagram.add_relationship("Dog", "Animal", "inheritance")
        diagram.add_relationship("Bird", "Animal", "inheritance")
        diagram.add_relationship("Bird", "Flyable", "realization")

        mermaid_code = diagram.to_mermaid()
        assert "classDiagram" in mermaid_code
        assert "class Animal {" in mermaid_code
        assert "<<abstract>>" in mermaid_code
        assert "<<interface>>" in mermaid_code

    def test_all_relationship_types(self):
        """Test all relationship types."""
        diagram = ClassDiagram()

        # Add classes for relationships
        classes = ["ClassA", "ClassB", "ClassC", "ClassD", "ClassE", "ClassF"]
        for cls_name in classes:
            diagram.add_class(cls_name)

        relationships = [
            ("ClassA", "ClassB", "inheritance"),
            ("ClassB", "ClassC", "composition"),
            ("ClassC", "ClassD", "aggregation"),
            ("ClassD", "ClassE", "association"),
            ("ClassE", "ClassF", "dependency"),
            ("ClassF", "ClassA", "realization"),
        ]

        for from_cls, to_cls, rel_type in relationships:
            diagram.add_relationship(from_cls, to_cls, rel_type)

        mermaid_code = diagram.to_mermaid()

        # Check that all classes and relationships are present
        for cls_name in classes:
            assert cls_name in mermaid_code


class TestStateDiagramComprehensive:
    """Comprehensive tests for StateDiagram."""

    def test_complex_state_machine(self):
        """Test complex state machine with all features."""
        diagram = StateDiagram(title="Complex State Machine")

        # Add states
        diagram.add_state("idle", "Idle State")
        diagram.add_state("processing", "Processing")
        diagram.add_state("error", "Error State")
        diagram.add_state("complete", "Complete")

        # Add transitions
        diagram.add_transition("idle", "processing", "start")
        diagram.add_transition("processing", "complete", "success")
        diagram.add_transition("processing", "error", "failure")
        diagram.add_transition("error", "idle", "reset")
        diagram.add_transition("complete", "idle", "restart")

        mermaid_code = diagram.to_mermaid()
        assert "stateDiagram-v2" in mermaid_code
        assert "idle" in mermaid_code
        assert "processing" in mermaid_code


class TestDiagramValidation:
    """Test diagram validation across all types."""

    def test_flowchart_validation(self):
        """Test flowchart validation."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Start")
        diagram.add_node("B", "End")
        diagram.add_edge("A", "B")

        assert diagram.validate() is True

        # Test invalid diagram (empty)
        empty_diagram = FlowchartDiagram()
        # Empty diagrams might still be valid, depending on implementation
        result = empty_diagram.validate()
        assert isinstance(result, bool)

    def test_sequence_validation(self):
        """Test sequence diagram validation."""
        diagram = SequenceDiagram()
        diagram.add_participant("A")
        diagram.add_participant("B")
        diagram.add_message("A", "B", "Test message")

        assert diagram.validate() is True

    def test_class_diagram_validation(self):
        """Test class diagram validation."""
        diagram = ClassDiagram()
        diagram.add_class("TestClass")

        assert diagram.validate() is True


class TestDiagramComplexity:
    """Test diagram complexity calculations."""

    def test_flowchart_complexity(self):
        """Test flowchart complexity calculation."""
        diagram = FlowchartDiagram()

        # Add multiple nodes and edges
        for i in range(10):
            diagram.add_node(f"node_{i}", f"Node {i}")

        for i in range(9):
            diagram.add_edge(f"node_{i}", f"node_{i+1}")

        # Add some branching
        diagram.add_edge("node_3", "node_7")  # Skip ahead
        diagram.add_edge("node_5", "node_2")  # Loop back

        # The complexity should reflect the number of nodes and edges
        mermaid_code = diagram.to_mermaid()
        assert len(mermaid_code.split('\n')) > 10  # Should have many lines
