"""
Unit tests for diagram models.
"""

import pytest

from mermaid_render.exceptions import DiagramError
from mermaid_render.models import FlowchartDiagram, SequenceDiagram
from mermaid_render.models.flowchart import FlowchartEdge, FlowchartNode
from mermaid_render.models.sequence import SequenceMessage, SequenceParticipant


class TestFlowchartDiagram:
    """Test FlowchartDiagram class."""

    def test_init_default(self):
        """Test flowchart initialization with defaults."""
        flowchart = FlowchartDiagram()

        assert flowchart.direction == "TD"
        assert flowchart.get_diagram_type() == "flowchart"
        assert len(flowchart.nodes) == 0
        assert len(flowchart.edges) == 0

    def test_init_custom_direction(self):
        """Test flowchart initialization with custom direction."""
        flowchart = FlowchartDiagram(direction="LR", title="Test Flowchart")

        assert flowchart.direction == "LR"
        assert flowchart.title == "Test Flowchart"

    def test_invalid_direction(self):
        """Test flowchart with invalid direction."""
        with pytest.raises(DiagramError, match="Invalid direction"):
            FlowchartDiagram(direction="INVALID")

    def test_add_node(self):
        """Test adding nodes to flowchart."""
        flowchart = FlowchartDiagram()

        node = flowchart.add_node("A", "Start", shape="circle")

        assert node.id == "A"
        assert node.label == "Start"
        assert node.shape == "circle"
        assert "A" in flowchart.nodes
        assert flowchart.nodes["A"] is node

    def test_add_duplicate_node(self):
        """Test adding duplicate node ID."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "First")

        with pytest.raises(DiagramError, match="already exists"):
            flowchart.add_node("A", "Second")

    def test_add_edge(self):
        """Test adding edges between nodes."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Start")
        flowchart.add_node("B", "End")

        edge = flowchart.add_edge("A", "B", label="Connect")

        assert edge.from_node == "A"
        assert edge.to_node == "B"
        assert edge.label == "Connect"
        assert edge in flowchart.edges

    def test_add_edge_nonexistent_nodes(self):
        """Test adding edge with nonexistent nodes."""
        flowchart = FlowchartDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            flowchart.add_edge("A", "B")

    def test_add_edge_nonexistent_target_node(self):
        """Test adding edge with nonexistent target node."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Start")

        with pytest.raises(DiagramError, match="Target node 'B' does not exist"):
            flowchart.add_edge("A", "B")

    def test_add_subgraph(self):
        """Test adding subgraph."""
        flowchart = FlowchartDiagram()

        subgraph = flowchart.add_subgraph("sub1", title="Subprocess")

        assert subgraph.id == "sub1"
        assert subgraph.title == "Subprocess"
        assert "sub1" in flowchart.subgraphs

    def test_add_node_to_subgraph(self):
        """Test adding node to subgraph."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Node")
        subgraph = flowchart.add_subgraph("sub1")

        flowchart.add_node_to_subgraph("A", "sub1")

        assert "A" in subgraph.nodes

    def test_to_mermaid(self):
        """Test generating Mermaid syntax."""
        flowchart = FlowchartDiagram(direction="LR")
        flowchart.add_node("A", "Start", shape="circle")
        flowchart.add_node("B", "End", shape="circle")
        flowchart.add_edge("A", "B", label="Flow")

        mermaid_code = flowchart.to_mermaid()

        assert "flowchart LR" in mermaid_code
        assert "A((Start))" in mermaid_code
        assert "B((End))" in mermaid_code
        assert "A -->|Flow| B" in mermaid_code


class TestFlowchartNode:
    """Test FlowchartNode class."""

    def test_init_default(self):
        """Test node initialization with defaults."""
        node = FlowchartNode("A", "Label")

        assert node.id == "A"
        assert node.label == "Label"
        assert node.shape == "rectangle"

    def test_init_custom_shape(self):
        """Test node initialization with custom shape."""
        node = FlowchartNode("B", "Circle Node", shape="circle")

        assert node.shape == "circle"

    def test_invalid_shape(self):
        """Test node with invalid shape."""
        with pytest.raises(DiagramError, match="Unknown node shape"):
            FlowchartNode("A", "Label", shape="invalid_shape")

    def test_to_mermaid_rectangle(self):
        """Test Mermaid syntax for rectangle node."""
        node = FlowchartNode("A", "Rectangle", shape="rectangle")

        assert node.to_mermaid() == "A[Rectangle]"

    def test_to_mermaid_circle(self):
        """Test Mermaid syntax for circle node."""
        node = FlowchartNode("B", "Circle", shape="circle")

        assert node.to_mermaid() == "B((Circle))"

    def test_to_mermaid_rhombus(self):
        """Test Mermaid syntax for rhombus node."""
        node = FlowchartNode("C", "Decision", shape="rhombus")

        assert node.to_mermaid() == "C{Decision}"


class TestFlowchartEdge:
    """Test FlowchartEdge class."""

    def test_init_default(self):
        """Test edge initialization with defaults."""
        edge = FlowchartEdge("A", "B")

        assert edge.from_node == "A"
        assert edge.to_node == "B"
        assert edge.arrow_type == "arrow"
        assert edge.label is None

    def test_init_with_label(self):
        """Test edge initialization with label."""
        edge = FlowchartEdge("A", "B", label="Connect", arrow_type="dotted")

        assert edge.label == "Connect"
        assert edge.arrow_type == "dotted"

    def test_invalid_arrow_type(self):
        """Test edge with invalid arrow type."""
        with pytest.raises(DiagramError, match="Unknown arrow type"):
            FlowchartEdge("A", "B", arrow_type="invalid")

    def test_to_mermaid_simple(self):
        """Test Mermaid syntax for simple edge."""
        edge = FlowchartEdge("A", "B")

        assert edge.to_mermaid() == "A --> B"

    def test_to_mermaid_with_label(self):
        """Test Mermaid syntax for edge with label."""
        edge = FlowchartEdge("A", "B", label="Yes", arrow_type="arrow")

        assert edge.to_mermaid() == "A -->|Yes| B"


class TestSequenceDiagram:
    """Test SequenceDiagram class."""

    def test_init_default(self):
        """Test sequence diagram initialization."""
        sequence = SequenceDiagram()

        assert sequence.get_diagram_type() == "sequenceDiagram"
        assert len(sequence.participants) == 0
        assert len(sequence.messages) == 0
        assert sequence.autonumber is False

    def test_init_with_options(self):
        """Test sequence diagram with options."""
        sequence = SequenceDiagram(title="Test Sequence", autonumber=True)

        assert sequence.title == "Test Sequence"
        assert sequence.autonumber is True

    def test_add_participant(self):
        """Test adding participant."""
        sequence = SequenceDiagram()

        participant = sequence.add_participant("A", "Alice")

        assert participant.id == "A"
        assert participant.name == "Alice"
        assert "A" in sequence.participants

    def test_add_message(self):
        """Test adding message between participants."""
        sequence = SequenceDiagram()

        message = sequence.add_message("A", "B", "Hello", "sync")

        assert message.from_participant == "A"
        assert message.to_participant == "B"
        assert message.message == "Hello"
        assert message.message_type == "sync"

        # Should auto-create participants
        assert "A" in sequence.participants
        assert "B" in sequence.participants

    def test_add_note(self):
        """Test adding note."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        note = sequence.add_note("Important note", "A", "right of")

        assert note.text == "Important note"
        assert note.participant == "A"
        assert note.position == "right of"

    def test_to_mermaid(self):
        """Test generating Mermaid syntax."""
        sequence = SequenceDiagram(title="Test", autonumber=True)
        sequence.add_participant("A", "Alice")
        sequence.add_participant("B", "Bob")
        sequence.add_message("A", "B", "Hello", "sync")

        mermaid_code = sequence.to_mermaid()

        assert "sequenceDiagram" in mermaid_code
        assert "title: Test" in mermaid_code
        assert "autonumber" in mermaid_code
        assert "participant A as Alice" in mermaid_code
        assert "A->B: Hello" in mermaid_code


class TestSequenceParticipant:
    """Test SequenceParticipant class."""

    def test_init_default(self):
        """Test participant initialization."""
        participant = SequenceParticipant("A")

        assert participant.id == "A"
        assert participant.name == "A"  # Defaults to ID

    def test_init_with_name(self):
        """Test participant with custom name."""
        participant = SequenceParticipant("A", "Alice")

        assert participant.id == "A"
        assert participant.name == "Alice"

    def test_to_mermaid_simple(self):
        """Test Mermaid syntax for simple participant."""
        participant = SequenceParticipant("A")

        assert participant.to_mermaid() == "participant A"

    def test_to_mermaid_with_name(self):
        """Test Mermaid syntax for participant with name."""
        participant = SequenceParticipant("A", "Alice")

        assert participant.to_mermaid() == "participant A as Alice"


class TestSequenceMessage:
    """Test SequenceMessage class."""

    def test_init_default(self):
        """Test message initialization."""
        message = SequenceMessage("A", "B", "Hello")

        assert message.from_participant == "A"
        assert message.to_participant == "B"
        assert message.message == "Hello"
        assert message.message_type == "sync"

    def test_invalid_message_type(self):
        """Test message with invalid type."""
        with pytest.raises(DiagramError, match="Unknown message type"):
            SequenceMessage("A", "B", "Hello", "invalid_type")

    def test_to_mermaid_simple(self):
        """Test Mermaid syntax for simple message."""
        message = SequenceMessage("A", "B", "Hello", "sync")

        lines = message.to_mermaid()
        assert "A->B: Hello" in lines

    def test_to_mermaid_with_activation(self):
        """Test Mermaid syntax with activation."""
        message = SequenceMessage("A", "B", "Hello", "sync", activate=True)

        lines = message.to_mermaid()
        assert "activate B" in lines
        assert "A->B: Hello" in lines


class TestFlowchartNodeAdditional:
    """Additional tests for FlowchartNode class."""

    def test_invalid_node_shape(self):
        """Test creating node with invalid shape."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.flowchart import FlowchartNode

        with pytest.raises(DiagramError, match="Unknown node shape"):
            FlowchartNode("A", "Test", shape="invalid_shape")

    def test_node_with_style(self):
        """Test creating node with style."""
        from mermaid_render.models.flowchart import FlowchartNode

        style = {"fill": "#ff0000", "stroke": "#000000"}
        node = FlowchartNode("A", "Styled Node", style=style)

        assert node.style == style
        assert node.to_mermaid() == "A[Styled Node]"

    def test_all_node_shapes(self):
        """Test all supported node shapes."""
        from mermaid_render.models.flowchart import FlowchartNode

        shapes_to_test = [
            ("rectangle", "A[Test]"),
            ("rounded", "A(Test)"),
            ("stadium", "A([Test])"),
            ("subroutine", "A[[Test]]"),
            ("cylindrical", "A[(Test)]"),
            ("circle", "A((Test))"),
            ("asymmetric", "A>Test]"),
            ("rhombus", "A{Test}"),
            ("hexagon", "A{{Test}}"),
            ("parallelogram", "A[/Test/]"),
            ("parallelogram_alt", "A[\\Test\\]"),
            ("trapezoid", "A[/Test\\]"),
            ("trapezoid_alt", "A[\\Test/]"),
        ]

        for shape, expected in shapes_to_test:
            node = FlowchartNode("A", "Test", shape=shape)
            assert node.to_mermaid() == expected


class TestFlowchartEdgeAdditional:
    """Additional tests for FlowchartEdge class."""

    def test_invalid_arrow_type(self):
        """Test creating edge with invalid arrow type."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.flowchart import FlowchartEdge

        with pytest.raises(DiagramError, match="Unknown arrow type"):
            FlowchartEdge("A", "B", arrow_type="invalid_arrow")

    def test_edge_without_label(self):
        """Test edge without label using different arrow types."""
        from mermaid_render.models.flowchart import FlowchartEdge

        arrow_types_to_test = [
            ("arrow", "A --> B"),
            ("open", "A --- B"),
            ("dotted", "A -.- B"),
            ("dotted_arrow", "A -.-> B"),
            ("thick", "A ==> B"),
            ("thick_open", "A === B"),
        ]

        for arrow_type, expected in arrow_types_to_test:
            edge = FlowchartEdge("A", "B", arrow_type=arrow_type)
            assert edge.to_mermaid() == expected

    def test_edge_with_style(self):
        """Test creating edge with style."""
        from mermaid_render.models.flowchart import FlowchartEdge

        style = {"stroke": "#ff0000", "stroke-width": "2px"}
        edge = FlowchartEdge("A", "B", label="Test", style=style)

        assert edge.style == style
        assert edge.to_mermaid() == "A -->|Test| B"


class TestFlowchartSubgraph:
    """Test FlowchartSubgraph class."""

    def test_subgraph_creation(self):
        """Test creating a subgraph."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1", "My Subgraph")

        assert subgraph.id == "sub1"
        assert subgraph.title == "My Subgraph"
        assert subgraph.direction is None
        assert len(subgraph.nodes) == 0

    def test_subgraph_with_direction(self):
        """Test creating subgraph with direction."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1", "My Subgraph", direction="LR")

        assert subgraph.direction == "LR"

    def test_add_node_to_subgraph(self):
        """Test adding nodes to subgraph."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1")
        subgraph.add_node("A")
        subgraph.add_node("B")

        assert "A" in subgraph.nodes
        assert "B" in subgraph.nodes
        assert len(subgraph.nodes) == 2

    def test_add_duplicate_node_to_subgraph(self):
        """Test adding duplicate node to subgraph."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1")
        subgraph.add_node("A")
        subgraph.add_node("A")  # Should not add duplicate

        assert len(subgraph.nodes) == 1

    def test_subgraph_to_mermaid_with_title(self):
        """Test subgraph Mermaid generation with title."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1", "My Subgraph")
        subgraph.add_node("A")
        subgraph.add_node("B")

        lines = subgraph.to_mermaid()

        assert "subgraph sub1 [My Subgraph]" in lines
        assert "    A" in lines
        assert "    B" in lines
        assert "end" in lines

    def test_subgraph_to_mermaid_without_title(self):
        """Test subgraph Mermaid generation without title."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1")
        subgraph.add_node("A")

        lines = subgraph.to_mermaid()

        assert "subgraph sub1" in lines
        assert "    A" in lines
        assert "end" in lines

    def test_subgraph_to_mermaid_with_direction(self):
        """Test subgraph Mermaid generation with direction."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1", "My Subgraph", direction="LR")
        subgraph.add_node("A")

        lines = subgraph.to_mermaid()

        assert "subgraph sub1 [My Subgraph]" in lines
        assert "    direction LR" in lines
        assert "    A" in lines
        assert "end" in lines


class TestFlowchartDiagramAdditional:
    """Additional tests for FlowchartDiagram class."""

    def test_duplicate_subgraph_error(self):
        """Test adding duplicate subgraph ID."""
        flowchart = FlowchartDiagram()
        flowchart.add_subgraph("sub1", "First")

        with pytest.raises(DiagramError, match="already exists"):
            flowchart.add_subgraph("sub1", "Second")

    def test_add_node_to_nonexistent_subgraph(self):
        """Test adding node to nonexistent subgraph."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Node A")

        with pytest.raises(DiagramError, match="does not exist"):
            flowchart.add_node_to_subgraph("A", "nonexistent")

    def test_add_nonexistent_node_to_subgraph(self):
        """Test adding nonexistent node to subgraph."""
        flowchart = FlowchartDiagram()
        flowchart.add_subgraph("sub1", "Subgraph")

        with pytest.raises(DiagramError, match="does not exist"):
            flowchart.add_node_to_subgraph("nonexistent", "sub1")

    def test_add_style(self):
        """Test adding style to elements."""
        flowchart = FlowchartDiagram()

        style = {"fill": "#ff0000", "stroke": "#000000"}
        flowchart.add_style("A", style)

        assert "A" in flowchart.styles
        assert flowchart.styles["A"] == style

    def test_to_mermaid_with_title(self):
        """Test Mermaid generation with title."""
        flowchart = FlowchartDiagram(title="My Flowchart")
        flowchart.add_node("A", "Start")

        mermaid_code = flowchart.to_mermaid()

        assert "title: My Flowchart" in mermaid_code

    def test_to_mermaid_with_subgraphs(self):
        """Test Mermaid generation with subgraphs."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Node A")
        flowchart.add_node("B", "Node B")

        flowchart.add_subgraph("sub1", "My Subgraph")
        flowchart.add_node_to_subgraph("A", "sub1")

        mermaid_code = flowchart.to_mermaid()

        assert "subgraph sub1 [My Subgraph]" in mermaid_code
        assert "    A" in mermaid_code
        assert "end" in mermaid_code

    def test_to_mermaid_with_styles(self):
        """Test Mermaid generation with styles."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Styled Node")
        flowchart.add_style("A", {"fill": "#ff0000", "stroke": "#000000"})

        mermaid_code = flowchart.to_mermaid()

        assert "style A fill:#ff0000,stroke:#000000" in mermaid_code


class TestSequenceParticipantAdditional:
    """Additional tests for SequenceParticipant class."""

    def test_participant_with_same_id_and_name(self):
        """Test participant where name equals ID."""
        from mermaid_render.models.sequence import SequenceParticipant

        participant = SequenceParticipant("Alice")

        assert participant.id == "Alice"
        assert participant.name == "Alice"
        assert participant.to_mermaid() == "participant Alice"


class TestSequenceMessageAdditional:
    """Additional tests for SequenceMessage class."""

    def test_message_with_deactivation(self):
        """Test message with deactivation."""
        from mermaid_render.models.sequence import SequenceMessage

        message = SequenceMessage("A", "B", "Hello", "sync", deactivate=True)

        lines = message.to_mermaid()
        assert "A->B: Hello" in lines
        assert "deactivate B" in lines

    def test_all_message_types(self):
        """Test all supported message types."""
        from mermaid_render.models.sequence import SequenceMessage

        message_types_to_test = [
            ("sync", "A->B: Hello"),
            ("async", "A->>B: Hello"),
            ("return", "A-->>B: Hello"),
            ("sync_open", "A-)B: Hello"),
            ("async_open", "A--)B: Hello"),
            ("activate", "A+B: Hello"),
            ("deactivate", "A-B: Hello"),
            ("destroy", "A-xB: Hello"),
        ]

        for msg_type, expected in message_types_to_test:
            message = SequenceMessage("A", "B", "Hello", msg_type)
            lines = message.to_mermaid()
            assert expected in lines


class TestSequenceNote:
    """Test SequenceNote class."""

    def test_note_creation(self):
        """Test creating a note."""
        from mermaid_render.models.sequence import SequenceNote

        note = SequenceNote("Important note", "A", "right of")

        assert note.text == "Important note"
        assert note.participant == "A"
        assert note.position == "right of"

    def test_invalid_note_position(self):
        """Test creating note with invalid position."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.sequence import SequenceNote

        with pytest.raises(DiagramError, match="Unknown note position"):
            SequenceNote("Test", "A", "invalid_position")

    def test_note_over_participants(self):
        """Test note over multiple participants."""
        from mermaid_render.models.sequence import SequenceNote

        note = SequenceNote("Spanning note", "A", "over", ["A", "B", "C"])

        mermaid_syntax = note.to_mermaid()
        assert mermaid_syntax == "note over A,B,C: Spanning note"

    def test_note_positions(self):
        """Test all note positions."""
        from mermaid_render.models.sequence import SequenceNote

        positions_to_test = [
            ("left of", "note left of A: Test"),
            ("right of", "note right of A: Test"),
            ("over", "note over A: Test"),
        ]

        for position, expected in positions_to_test:
            note = SequenceNote("Test", "A", position)
            assert note.to_mermaid() == expected


class TestSequenceLoop:
    """Test SequenceLoop class."""

    def test_loop_creation(self):
        """Test creating a loop."""
        from mermaid_render.models.sequence import SequenceLoop

        loop = SequenceLoop("while condition")

        assert loop.condition == "while condition"
        assert len(loop.messages) == 0
        assert len(loop.notes) == 0

    def test_add_message_to_loop(self):
        """Test adding message to loop."""
        from mermaid_render.models.sequence import SequenceLoop, SequenceMessage

        loop = SequenceLoop("while condition")
        message = SequenceMessage("A", "B", "Hello")

        loop.add_message(message)

        assert len(loop.messages) == 1
        assert loop.messages[0] is message

    def test_add_note_to_loop(self):
        """Test adding note to loop."""
        from mermaid_render.models.sequence import SequenceLoop, SequenceNote

        loop = SequenceLoop("while condition")
        note = SequenceNote("Loop note", "A")

        loop.add_note(note)

        assert len(loop.notes) == 1
        assert loop.notes[0] is note

    def test_loop_to_mermaid(self):
        """Test loop Mermaid generation."""
        from mermaid_render.models.sequence import (
            SequenceLoop,
            SequenceMessage,
            SequenceNote,
        )

        loop = SequenceLoop("while condition")
        message = SequenceMessage("A", "B", "Hello")
        note = SequenceNote("Loop note", "A")

        loop.add_message(message)
        loop.add_note(note)

        lines = loop.to_mermaid()

        assert "loop while condition" in lines
        assert "    A->B: Hello" in lines
        assert "    note right of A: Loop note" in lines
        assert "end" in lines


class TestSequenceDiagramAdditional:
    """Additional tests for SequenceDiagram class."""

    def test_duplicate_participant_error(self):
        """Test adding duplicate participant."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        with pytest.raises(DiagramError, match="already exists"):
            sequence.add_participant("A", "Alice Again")

    def test_add_note_to_nonexistent_participant(self):
        """Test adding note to nonexistent participant."""
        sequence = SequenceDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            sequence.add_note("Test note", "nonexistent")

    def test_add_loop(self):
        """Test adding loop to sequence diagram."""
        sequence = SequenceDiagram()

        loop = sequence.add_loop("while condition")

        assert len(sequence.loops) == 1
        assert sequence.loops[0] is loop
        assert loop.condition == "while condition"

    def test_activate_participant(self):
        """Test activating participant."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        sequence.activate_participant("A")

        assert sequence.activations["A"] is True

    def test_activate_nonexistent_participant(self):
        """Test activating nonexistent participant."""
        sequence = SequenceDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            sequence.activate_participant("nonexistent")

    def test_deactivate_participant(self):
        """Test deactivating participant."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        sequence.deactivate_participant("A")

        assert sequence.activations["A"] is False

    def test_deactivate_nonexistent_participant(self):
        """Test deactivating nonexistent participant."""
        sequence = SequenceDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            sequence.deactivate_participant("nonexistent")

    def test_to_mermaid_with_loops(self):
        """Test Mermaid generation with loops."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")
        sequence.add_participant("B", "Bob")

        loop = sequence.add_loop("while condition")
        message = SequenceMessage("A", "B", "Hello")
        loop.add_message(message)

        mermaid_code = sequence.to_mermaid()

        assert "loop while condition" in mermaid_code
        assert "    A->B: Hello" in mermaid_code
        assert "end" in mermaid_code

    def test_to_mermaid_with_notes(self):
        """Test Mermaid generation with notes."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")
        sequence.add_note("Important note", "A", "right of")

        mermaid_code = sequence.to_mermaid()

        assert "note right of A: Important note" in mermaid_code


class TestClassMethod:
    """Test ClassMethod class."""

    def test_method_creation(self):
        """Test creating a class method."""
        from mermaid_render.models.class_diagram import ClassMethod

        method = ClassMethod("getName", "public", "String", ["id: int"])

        assert method.name == "getName"
        assert method.visibility == "public"
        assert method.return_type == "String"
        assert method.parameters == ["id: int"]
        assert method.is_static is False
        assert method.is_abstract is False

    def test_method_to_mermaid_basic(self):
        """Test basic method Mermaid generation."""
        from mermaid_render.models.class_diagram import ClassMethod

        method = ClassMethod("getName", "public", "String")

        assert method.to_mermaid() == "+getName() String"

    def test_method_to_mermaid_with_parameters(self):
        """Test method with parameters."""
        from mermaid_render.models.class_diagram import ClassMethod

        method = ClassMethod("setName", "public", "void", ["name: String", "id: int"])

        assert method.to_mermaid() == "+setName(name: String, id: int) void"

    def test_method_visibility_symbols(self):
        """Test all visibility symbols."""
        from mermaid_render.models.class_diagram import ClassMethod

        visibilities = [
            ("public", "+"),
            ("private", "-"),
            ("protected", "#"),
            ("package", "~"),
        ]

        for visibility, symbol in visibilities:
            method = ClassMethod("test", visibility)
            assert method.to_mermaid().startswith(symbol)

    def test_method_static_and_abstract(self):
        """Test static and abstract method modifiers."""
        from mermaid_render.models.class_diagram import ClassMethod

        # Static method
        static_method = ClassMethod("getInstance", "public", "MyClass", is_static=True)
        assert static_method.to_mermaid() == "+getInstance() MyClass$"

        # Abstract method
        abstract_method = ClassMethod("process", "public", "void", is_abstract=True)
        assert abstract_method.to_mermaid() == "+process() void*"

        # Both static and abstract
        both_method = ClassMethod(
            "test", "public", "void", is_static=True, is_abstract=True
        )
        assert both_method.to_mermaid() == "+test() void$*"


class TestClassAttribute:
    """Test ClassAttribute class."""

    def test_attribute_creation(self):
        """Test creating a class attribute."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("name", "String", "private", is_static=False)

        assert attr.name == "name"
        assert attr.type == "String"
        assert attr.visibility == "private"
        assert attr.is_static is False

    def test_attribute_to_mermaid_basic(self):
        """Test basic attribute Mermaid generation."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("name", "String", "private")

        assert attr.to_mermaid() == "-name String"

    def test_attribute_without_type(self):
        """Test attribute without type."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("count", visibility="public")

        assert attr.to_mermaid() == "+count"

    def test_attribute_static(self):
        """Test static attribute."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("instance", "MyClass", "private", is_static=True)

        assert attr.to_mermaid() == "-instance MyClass$"

    def test_attribute_visibility_symbols(self):
        """Test all visibility symbols for attributes."""
        from mermaid_render.models.class_diagram import ClassAttribute

        visibilities = [
            ("public", "+"),
            ("private", "-"),
            ("protected", "#"),
            ("package", "~"),
        ]

        for visibility, symbol in visibilities:
            attr = ClassAttribute("test", "String", visibility)
            assert attr.to_mermaid().startswith(symbol)


class TestClassDefinition:
    """Test ClassDefinition class."""

    def test_class_creation(self):
        """Test creating a class definition."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("MyClass")

        assert class_def.name == "MyClass"
        assert class_def.is_abstract is False
        assert class_def.is_interface is False
        assert class_def.stereotype is None
        assert len(class_def.attributes) == 0
        assert len(class_def.methods) == 0

    def test_abstract_class(self):
        """Test creating abstract class."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("AbstractClass", is_abstract=True)

        assert class_def.is_abstract is True

        lines = class_def.to_mermaid()
        assert "class AbstractClass {" in lines
        assert "    <<abstract>>" in lines
        assert "}" in lines

    def test_interface_class(self):
        """Test creating interface."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("MyInterface", is_interface=True)

        assert class_def.is_interface is True

        lines = class_def.to_mermaid()
        assert "class MyInterface {" in lines
        assert "    <<interface>>" in lines
        assert "}" in lines

    def test_class_with_stereotype(self):
        """Test class with stereotype."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("MyClass", stereotype="entity")

        lines = class_def.to_mermaid()
        assert "class MyClass {" in lines
        assert "    <<entity>>" in lines
        assert "}" in lines

    def test_add_attribute_and_method(self):
        """Test adding attributes and methods to class."""
        from mermaid_render.models.class_diagram import (
            ClassAttribute,
            ClassDefinition,
            ClassMethod,
        )

        class_def = ClassDefinition("MyClass")

        attr = ClassAttribute("name", "String", "private")
        method = ClassMethod("getName", "public", "String")

        class_def.add_attribute(attr)
        class_def.add_method(method)

        assert len(class_def.attributes) == 1
        assert len(class_def.methods) == 1
        assert class_def.attributes[0] is attr
        assert class_def.methods[0] is method

    def test_class_to_mermaid_complete(self):
        """Test complete class Mermaid generation."""
        from mermaid_render.models.class_diagram import (
            ClassAttribute,
            ClassDefinition,
            ClassMethod,
        )

        class_def = ClassDefinition("Person")
        class_def.add_attribute(ClassAttribute("name", "String", "private"))
        class_def.add_attribute(ClassAttribute("age", "int", "private"))
        class_def.add_method(ClassMethod("getName", "public", "String"))
        class_def.add_method(ClassMethod("setName", "public", "void", ["name: String"]))

        lines = class_def.to_mermaid()

        assert "class Person {" in lines
        assert "    -name String" in lines
        assert "    -age int" in lines
        assert "    +getName() String" in lines
        assert "    +setName(name: String) void" in lines
        assert "}" in lines


class TestClassRelationship:
    """Test ClassRelationship class."""

    def test_relationship_creation(self):
        """Test creating a class relationship."""
        from mermaid_render.models.class_diagram import ClassRelationship

        rel = ClassRelationship("Dog", "Animal", "inheritance")

        assert rel.from_class == "Dog"
        assert rel.to_class == "Animal"
        assert rel.relationship_type == "inheritance"
        assert rel.label is None
        assert rel.from_cardinality is None
        assert rel.to_cardinality is None

    def test_invalid_relationship_type(self):
        """Test creating relationship with invalid type."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassRelationship

        with pytest.raises(DiagramError, match="Unknown relationship type"):
            ClassRelationship("A", "B", "invalid_type")

    def test_all_relationship_types(self):
        """Test all supported relationship types."""
        from mermaid_render.models.class_diagram import ClassRelationship

        relationships = [
            ("inheritance", "Dog <|-- Animal"),
            ("composition", "Dog *-- Animal"),
            ("aggregation", "Dog o-- Animal"),
            ("association", "Dog --> Animal"),
            ("dependency", "Dog ..> Animal"),
            ("realization", "Dog ..|> Animal"),
        ]

        for rel_type, expected in relationships:
            rel = ClassRelationship("Dog", "Animal", rel_type)
            assert rel.to_mermaid() == expected

    def test_relationship_with_label(self):
        """Test relationship with label."""
        from mermaid_render.models.class_diagram import ClassRelationship

        rel = ClassRelationship("Dog", "Owner", "association", label="belongs to")

        assert rel.to_mermaid() == "Dog --> Owner : belongs to"

    def test_relationship_with_cardinality(self):
        """Test relationship with cardinality."""
        from mermaid_render.models.class_diagram import ClassRelationship

        rel = ClassRelationship(
            "Order", "Item", "composition", from_cardinality="1", to_cardinality="*"
        )

        assert rel.to_mermaid() == 'Order "1" *-- "*" Item'

    def test_relationship_complete(self):
        """Test relationship with all features."""
        from mermaid_render.models.class_diagram import ClassRelationship

        rel = ClassRelationship(
            "Customer",
            "Order",
            "association",
            label="places",
            from_cardinality="1",
            to_cardinality="*",
        )

        assert rel.to_mermaid() == 'Customer "1" --> "*" Order : places'


class TestClassDiagram:
    """Test ClassDiagram class."""

    def test_diagram_creation(self):
        """Test creating a class diagram."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()

        assert diagram.get_diagram_type() == "classDiagram"
        assert len(diagram.classes) == 0
        assert len(diagram.relationships) == 0

    def test_diagram_with_title(self):
        """Test class diagram with title."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram(title="Animal Hierarchy")

        assert diagram.title == "Animal Hierarchy"

    def test_add_class(self):
        """Test adding class to diagram."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        class_def = diagram.add_class("Animal")

        assert len(diagram.classes) == 1
        assert "Animal" in diagram.classes
        assert diagram.classes["Animal"] is class_def
        assert class_def.name == "Animal"

    def test_add_duplicate_class(self):
        """Test adding duplicate class."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Animal")

        with pytest.raises(DiagramError, match="already exists"):
            diagram.add_class("Animal")

    def test_add_class_with_options(self):
        """Test adding class with options."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        class_def = diagram.add_class("Animal", is_abstract=True, stereotype="entity")

        assert class_def.is_abstract is True
        assert class_def.stereotype == "entity"

    def test_add_relationship(self):
        """Test adding relationship between classes."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Dog")
        diagram.add_class("Animal")

        rel = diagram.add_relationship("Dog", "Animal", "inheritance")

        assert len(diagram.relationships) == 1
        assert diagram.relationships[0] is rel
        assert rel.from_class == "Dog"
        assert rel.to_class == "Animal"
        assert rel.relationship_type == "inheritance"

    def test_add_relationship_nonexistent_from_class(self):
        """Test adding relationship with nonexistent from class."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Animal")

        with pytest.raises(DiagramError, match="does not exist"):
            diagram.add_relationship("NonExistent", "Animal", "inheritance")

    def test_add_relationship_nonexistent_to_class(self):
        """Test adding relationship with nonexistent to class."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Dog")

        with pytest.raises(DiagramError, match="does not exist"):
            diagram.add_relationship("Dog", "NonExistent", "inheritance")

    def test_to_mermaid_basic(self):
        """Test basic Mermaid generation."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Animal")

        mermaid_code = diagram.to_mermaid()

        assert "classDiagram" in mermaid_code
        assert "class Animal {" in mermaid_code
        assert "}" in mermaid_code

    def test_to_mermaid_with_title(self):
        """Test Mermaid generation with title."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram(title="Animal Hierarchy")
        diagram.add_class("Animal")

        mermaid_code = diagram.to_mermaid()

        assert "title: Animal Hierarchy" in mermaid_code

    def test_to_mermaid_with_relationships(self):
        """Test Mermaid generation with relationships."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Dog")
        diagram.add_class("Animal")
        diagram.add_relationship("Dog", "Animal", "inheritance")

        mermaid_code = diagram.to_mermaid()

        assert "Dog <|-- Animal" in mermaid_code

    def test_to_mermaid_complete(self):
        """Test complete Mermaid generation with classes and relationships."""
        from mermaid_render.models.class_diagram import (
            ClassAttribute,
            ClassDiagram,
            ClassMethod,
        )

        diagram = ClassDiagram(title="Pet System")

        # Add Animal class
        animal = diagram.add_class("Animal", is_abstract=True)
        animal.add_attribute(ClassAttribute("name", "String", "protected"))
        animal.add_method(ClassMethod("move", "public", "void", is_abstract=True))

        # Add Dog class
        dog = diagram.add_class("Dog")
        dog.add_method(ClassMethod("bark", "public", "void"))

        # Add relationship
        diagram.add_relationship("Dog", "Animal", "inheritance")

        mermaid_code = diagram.to_mermaid()

        assert "classDiagram" in mermaid_code
        assert "title: Pet System" in mermaid_code
        assert "class Animal {" in mermaid_code
        assert "    <<abstract>>" in mermaid_code
        assert "    #name String" in mermaid_code
        assert "    +move() void*" in mermaid_code
        assert "class Dog {" in mermaid_code
        assert "    +bark() void" in mermaid_code
        assert "Dog <|-- Animal" in mermaid_code


class TestERDiagram:
    """Test ERDiagram class."""

    def test_diagram_creation(self):
        """Test creating an ER diagram."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()

        assert diagram.get_diagram_type() == "erDiagram"
        assert len(diagram.entities) == 0
        assert len(diagram.relationships) == 0

    def test_diagram_with_title(self):
        """Test ER diagram with title."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram(title="Customer Database")

        assert diagram.title == "Customer Database"

    def test_add_entity_without_attributes(self):
        """Test adding entity without attributes."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")

        assert len(diagram.entities) == 1
        assert "Customer" in diagram.entities
        assert diagram.entities["Customer"] == {}

    def test_add_entity_with_attributes(self):
        """Test adding entity with attributes."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        attributes = {"id": "int", "name": "string", "email": "string"}
        diagram.add_entity("Customer", attributes)

        assert len(diagram.entities) == 1
        assert "Customer" in diagram.entities
        assert diagram.entities["Customer"] == attributes

    def test_add_relationship(self):
        """Test adding relationship between entities."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")
        diagram.add_entity("Order")
        diagram.add_relationship("Customer", "Order", "||--o{")

        assert len(diagram.relationships) == 1
        assert diagram.relationships[0] == ("Customer", "Order", "||--o{")

    def test_to_mermaid_basic(self):
        """Test basic Mermaid generation."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")

        mermaid_code = diagram.to_mermaid()

        assert "erDiagram" in mermaid_code
        assert "Customer {" in mermaid_code
        assert "}" in mermaid_code

    def test_to_mermaid_with_title(self):
        """Test Mermaid generation with title."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram(title="Customer Database")
        diagram.add_entity("Customer")

        mermaid_code = diagram.to_mermaid()

        assert "title: Customer Database" in mermaid_code

    def test_to_mermaid_with_attributes(self):
        """Test Mermaid generation with entity attributes."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        attributes = {"id": "int", "name": "string", "email": "string"}
        diagram.add_entity("Customer", attributes)

        mermaid_code = diagram.to_mermaid()

        assert "Customer {" in mermaid_code
        assert "int id" in mermaid_code
        assert "string name" in mermaid_code
        assert "string email" in mermaid_code
        assert "}" in mermaid_code

    def test_to_mermaid_with_relationships(self):
        """Test Mermaid generation with relationships."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")
        diagram.add_entity("Order")
        diagram.add_relationship("Customer", "Order", "||--o{")

        mermaid_code = diagram.to_mermaid()

        assert "Customer ||--o{ Order" in mermaid_code

    def test_to_mermaid_complete(self):
        """Test complete Mermaid generation with entities and relationships."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram(title="E-commerce Database")

        # Add Customer entity
        customer_attrs = {"id": "int", "name": "string", "email": "string"}
        diagram.add_entity("Customer", customer_attrs)

        # Add Order entity
        order_attrs = {"id": "int", "date": "date", "total": "decimal"}
        diagram.add_entity("Order", order_attrs)

        # Add Product entity
        product_attrs = {"id": "int", "name": "string", "price": "decimal"}
        diagram.add_entity("Product", product_attrs)

        # Add relationships
        diagram.add_relationship("Customer", "Order", "||--o{")
        diagram.add_relationship("Order", "Product", "}o--||")

        mermaid_code = diagram.to_mermaid()

        assert "erDiagram" in mermaid_code
        assert "title: E-commerce Database" in mermaid_code
        assert "Customer {" in mermaid_code
        assert "int id" in mermaid_code
        assert "string name" in mermaid_code
        assert "Order {" in mermaid_code
        assert "date date" in mermaid_code
        assert "Product {" in mermaid_code
        assert "decimal price" in mermaid_code
        assert "Customer ||--o{ Order" in mermaid_code
        assert "Order }o--|| Product" in mermaid_code
