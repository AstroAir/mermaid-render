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

    def test_init_default(self) -> None:
        """Test flowchart initialization with defaults."""
        flowchart = FlowchartDiagram()

        assert flowchart.direction == "TD"
        assert flowchart.get_diagram_type() == "flowchart"
        assert len(flowchart.nodes) == 0
        assert len(flowchart.edges) == 0

    def test_init_custom_direction(self) -> None:
        """Test flowchart initialization with custom direction."""
        flowchart = FlowchartDiagram(direction="LR", title="Test Flowchart")

        assert flowchart.direction == "LR"
        assert flowchart.title == "Test Flowchart"

    def test_invalid_direction(self) -> None:
        """Test flowchart with invalid direction."""
        with pytest.raises(DiagramError, match="Invalid direction"):
            FlowchartDiagram(direction="INVALID")

    def test_add_node(self) -> None:
        """Test adding nodes to flowchart."""
        flowchart = FlowchartDiagram()

        node = flowchart.add_node("A", "Start", shape="circle")

        assert node.id == "A"
        assert node.label == "Start"
        assert node.shape == "circle"
        assert "A" in flowchart.nodes
        assert flowchart.nodes["A"] is node

    def test_add_duplicate_node(self) -> None:
        """Test adding duplicate node ID."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "First")

        with pytest.raises(DiagramError, match="already exists"):
            flowchart.add_node("A", "Second")

    def test_add_edge(self) -> None:
        """Test adding edges between nodes."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Start")
        flowchart.add_node("B", "End")

        edge = flowchart.add_edge("A", "B", label="Connect")

        assert edge.from_node == "A"
        assert edge.to_node == "B"
        assert edge.label == "Connect"
        assert edge in flowchart.edges

    def test_add_edge_nonexistent_nodes(self) -> None:
        """Test adding edge with nonexistent nodes."""
        flowchart = FlowchartDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            flowchart.add_edge("A", "B")

    def test_add_edge_nonexistent_target_node(self) -> None:
        """Test adding edge with nonexistent target node."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Start")

        with pytest.raises(DiagramError, match="Target node 'B' does not exist"):
            flowchart.add_edge("A", "B")

    def test_add_subgraph(self) -> None:
        """Test adding subgraph."""
        flowchart = FlowchartDiagram()

        subgraph = flowchart.add_subgraph("sub1", title="Subprocess")

        assert subgraph.id == "sub1"
        assert subgraph.title == "Subprocess"
        assert "sub1" in flowchart.subgraphs

    def test_add_node_to_subgraph(self) -> None:
        """Test adding node to subgraph."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Node")
        subgraph = flowchart.add_subgraph("sub1")

        flowchart.add_node_to_subgraph("A", "sub1")

        assert "A" in subgraph.nodes

    def test_to_mermaid(self) -> None:
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

    def test_init_default(self) -> None:
        """Test node initialization with defaults."""
        node = FlowchartNode("A", "Label")

        assert node.id == "A"
        assert node.label == "Label"
        assert node.shape == "rectangle"

    def test_init_custom_shape(self) -> None:
        """Test node initialization with custom shape."""
        node = FlowchartNode("B", "Circle Node", shape="circle")

        assert node.shape == "circle"

    def test_invalid_shape(self) -> None:
        """Test node with invalid shape."""
        with pytest.raises(DiagramError, match="Unknown node shape"):
            FlowchartNode("A", "Label", shape="invalid_shape")

    def test_to_mermaid_rectangle(self) -> None:
        """Test Mermaid syntax for rectangle node."""
        node = FlowchartNode("A", "Rectangle", shape="rectangle")

        assert node.to_mermaid() == "A[Rectangle]"

    def test_to_mermaid_circle(self) -> None:
        """Test Mermaid syntax for circle node."""
        node = FlowchartNode("B", "Circle", shape="circle")

        assert node.to_mermaid() == "B((Circle))"

    def test_to_mermaid_rhombus(self) -> None:
        """Test Mermaid syntax for rhombus node."""
        node = FlowchartNode("C", "Decision", shape="rhombus")

        assert node.to_mermaid() == "C{Decision}"


class TestFlowchartEdge:
    """Test FlowchartEdge class."""

    def test_init_default(self) -> None:
        """Test edge initialization with defaults."""
        edge = FlowchartEdge("A", "B")

        assert edge.from_node == "A"
        assert edge.to_node == "B"
        assert edge.arrow_type == "arrow"
        assert edge.label is None

    def test_init_with_label(self) -> None:
        """Test edge initialization with label."""
        edge = FlowchartEdge("A", "B", label="Connect", arrow_type="dotted")

        assert edge.label == "Connect"
        assert edge.arrow_type == "dotted"

    def test_invalid_arrow_type(self) -> None:
        """Test edge with invalid arrow type."""
        with pytest.raises(DiagramError, match="Unknown arrow type"):
            FlowchartEdge("A", "B", arrow_type="invalid")

    def test_to_mermaid_simple(self) -> None:
        """Test Mermaid syntax for simple edge."""
        edge = FlowchartEdge("A", "B")

        assert edge.to_mermaid() == "A --> B"

    def test_to_mermaid_with_label(self) -> None:
        """Test Mermaid syntax for edge with label."""
        edge = FlowchartEdge("A", "B", label="Yes", arrow_type="arrow")

        assert edge.to_mermaid() == "A -->|Yes| B"


class TestSequenceDiagram:
    """Test SequenceDiagram class."""

    def test_init_default(self) -> None:
        """Test sequence diagram initialization."""
        sequence = SequenceDiagram()

        assert sequence.get_diagram_type() == "sequenceDiagram"
        assert len(sequence.participants) == 0
        assert len(sequence.messages) == 0
        assert sequence.autonumber is False

    def test_init_with_options(self) -> None:
        """Test sequence diagram with options."""
        sequence = SequenceDiagram(title="Test Sequence", autonumber=True)

        assert sequence.title == "Test Sequence"
        assert sequence.autonumber is True

    def test_add_participant(self) -> None:
        """Test adding participant."""
        sequence = SequenceDiagram()

        participant = sequence.add_participant("A", "Alice")

        assert participant.id == "A"
        assert participant.name == "Alice"
        assert "A" in sequence.participants

    def test_add_message(self) -> None:
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

    def test_add_note(self) -> None:
        """Test adding note."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        note = sequence.add_note("Important note", "A", "right of")

        assert note.text == "Important note"
        assert note.participant == "A"
        assert note.position == "right of"

    def test_to_mermaid(self) -> None:
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

    def test_init_default(self) -> None:
        """Test participant initialization."""
        participant = SequenceParticipant("A")

        assert participant.id == "A"
        assert participant.name == "A"  # Defaults to ID

    def test_init_with_name(self) -> None:
        """Test participant with custom name."""
        participant = SequenceParticipant("A", "Alice")

        assert participant.id == "A"
        assert participant.name == "Alice"

    def test_to_mermaid_simple(self) -> None:
        """Test Mermaid syntax for simple participant."""
        participant = SequenceParticipant("A")

        assert participant.to_mermaid() == "participant A"

    def test_to_mermaid_with_name(self) -> None:
        """Test Mermaid syntax for participant with name."""
        participant = SequenceParticipant("A", "Alice")

        assert participant.to_mermaid() == "participant A as Alice"


class TestSequenceMessage:
    """Test SequenceMessage class."""

    def test_init_default(self) -> None:
        """Test message initialization."""
        message = SequenceMessage("A", "B", "Hello")

        assert message.from_participant == "A"
        assert message.to_participant == "B"
        assert message.message == "Hello"
        assert message.message_type == "sync"

    def test_invalid_message_type(self) -> None:
        """Test message with invalid type."""
        with pytest.raises(DiagramError, match="Unknown message type"):
            SequenceMessage("A", "B", "Hello", "invalid_type")

    def test_to_mermaid_simple(self) -> None:
        """Test Mermaid syntax for simple message."""
        message = SequenceMessage("A", "B", "Hello", "sync")

        lines = message.to_mermaid()
        assert "A->B: Hello" in lines

    def test_to_mermaid_with_activation(self) -> None:
        """Test Mermaid syntax with activation."""
        message = SequenceMessage("A", "B", "Hello", "sync", activate=True)

        lines = message.to_mermaid()
        assert "activate B" in lines
        assert "A->B: Hello" in lines


class TestFlowchartNodeAdditional:
    """Additional tests for FlowchartNode class."""

    def test_invalid_node_shape(self) -> None:
        """Test creating node with invalid shape."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.flowchart import FlowchartNode

        with pytest.raises(DiagramError, match="Unknown node shape"):
            FlowchartNode("A", "Test", shape="invalid_shape")

    def test_node_with_style(self) -> None:
        """Test creating node with style."""
        from mermaid_render.models.flowchart import FlowchartNode

        style = {"fill": "#ff0000", "stroke": "#000000"}
        node = FlowchartNode("A", "Styled Node", style=style)

        assert node.style == style
        assert node.to_mermaid() == "A[Styled Node]"

    def test_all_node_shapes(self) -> None:
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

    def test_invalid_arrow_type(self) -> None:
        """Test creating edge with invalid arrow type."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.flowchart import FlowchartEdge

        with pytest.raises(DiagramError, match="Unknown arrow type"):
            FlowchartEdge("A", "B", arrow_type="invalid_arrow")

    def test_edge_without_label(self) -> None:
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

    def test_edge_with_style(self) -> None:
        """Test creating edge with style."""
        from mermaid_render.models.flowchart import FlowchartEdge

        style = {"stroke": "#ff0000", "stroke-width": "2px"}
        edge = FlowchartEdge("A", "B", label="Test", style=style)

        assert edge.style == style
        assert edge.to_mermaid() == "A -->|Test| B"


class TestFlowchartSubgraph:
    """Test FlowchartSubgraph class."""

    def test_subgraph_creation(self) -> None:
        """Test creating a subgraph."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1", "My Subgraph")

        assert subgraph.id == "sub1"
        assert subgraph.title == "My Subgraph"
        assert subgraph.direction is None
        assert len(subgraph.nodes) == 0

    def test_subgraph_with_direction(self) -> None:
        """Test creating subgraph with direction."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1", "My Subgraph", direction="LR")

        assert subgraph.direction == "LR"

    def test_add_node_to_subgraph(self) -> None:
        """Test adding nodes to subgraph."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1")
        subgraph.add_node("A")
        subgraph.add_node("B")

        assert "A" in subgraph.nodes
        assert "B" in subgraph.nodes
        assert len(subgraph.nodes) == 2

    def test_add_duplicate_node_to_subgraph(self) -> None:
        """Test adding duplicate node to subgraph."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1")
        subgraph.add_node("A")
        subgraph.add_node("A")  # Should not add duplicate

        assert len(subgraph.nodes) == 1

    def test_subgraph_to_mermaid_with_title(self) -> None:
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

    def test_subgraph_to_mermaid_without_title(self) -> None:
        """Test subgraph Mermaid generation without title."""
        from mermaid_render.models.flowchart import FlowchartSubgraph

        subgraph = FlowchartSubgraph("sub1")
        subgraph.add_node("A")

        lines = subgraph.to_mermaid()

        assert "subgraph sub1" in lines
        assert "    A" in lines
        assert "end" in lines

    def test_subgraph_to_mermaid_with_direction(self) -> None:
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

    def test_duplicate_subgraph_error(self) -> None:
        """Test adding duplicate subgraph ID."""
        flowchart = FlowchartDiagram()
        flowchart.add_subgraph("sub1", "First")

        with pytest.raises(DiagramError, match="already exists"):
            flowchart.add_subgraph("sub1", "Second")

    def test_add_node_to_nonexistent_subgraph(self) -> None:
        """Test adding node to nonexistent subgraph."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Node A")

        with pytest.raises(DiagramError, match="does not exist"):
            flowchart.add_node_to_subgraph("A", "nonexistent")

    def test_add_nonexistent_node_to_subgraph(self) -> None:
        """Test adding nonexistent node to subgraph."""
        flowchart = FlowchartDiagram()
        flowchart.add_subgraph("sub1", "Subgraph")

        with pytest.raises(DiagramError, match="does not exist"):
            flowchart.add_node_to_subgraph("nonexistent", "sub1")

    def test_add_style(self) -> None:
        """Test adding style to elements."""
        flowchart = FlowchartDiagram()

        style = {"fill": "#ff0000", "stroke": "#000000"}
        flowchart.add_style("A", style)

        assert "A" in flowchart.styles
        assert flowchart.styles["A"] == style

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        flowchart = FlowchartDiagram(title="My Flowchart")
        flowchart.add_node("A", "Start")

        mermaid_code = flowchart.to_mermaid()

        assert "title: My Flowchart" in mermaid_code

    def test_to_mermaid_with_subgraphs(self) -> None:
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

    def test_to_mermaid_with_styles(self) -> None:
        """Test Mermaid generation with styles."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Styled Node")
        flowchart.add_style("A", {"fill": "#ff0000", "stroke": "#000000"})

        mermaid_code = flowchart.to_mermaid()

        assert "style A fill:#ff0000,stroke:#000000" in mermaid_code


class TestSequenceParticipantAdditional:
    """Additional tests for SequenceParticipant class."""

    def test_participant_with_same_id_and_name(self) -> None:
        """Test participant where name equals ID."""
        from mermaid_render.models.sequence import SequenceParticipant

        participant = SequenceParticipant("Alice")

        assert participant.id == "Alice"
        assert participant.name == "Alice"
        assert participant.to_mermaid() == "participant Alice"


class TestSequenceMessageAdditional:
    """Additional tests for SequenceMessage class."""

    def test_message_with_deactivation(self) -> None:
        """Test message with deactivation."""
        from mermaid_render.models.sequence import SequenceMessage

        message = SequenceMessage("A", "B", "Hello", "sync", deactivate=True)

        lines = message.to_mermaid()
        assert "A->B: Hello" in lines
        assert "deactivate B" in lines

    def test_all_message_types(self) -> None:
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

    def test_note_creation(self) -> None:
        """Test creating a note."""
        from mermaid_render.models.sequence import SequenceNote

        note = SequenceNote("Important note", "A", "right of")

        assert note.text == "Important note"
        assert note.participant == "A"
        assert note.position == "right of"

    def test_invalid_note_position(self) -> None:
        """Test creating note with invalid position."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.sequence import SequenceNote

        with pytest.raises(DiagramError, match="Unknown note position"):
            SequenceNote("Test", "A", "invalid_position")

    def test_note_over_participants(self) -> None:
        """Test note over multiple participants."""
        from mermaid_render.models.sequence import SequenceNote

        note = SequenceNote("Spanning note", "A", "over", ["A", "B", "C"])

        mermaid_syntax = note.to_mermaid()
        assert mermaid_syntax == "note over A,B,C: Spanning note"

    def test_note_positions(self) -> None:
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

    def test_loop_creation(self) -> None:
        """Test creating a loop."""
        from mermaid_render.models.sequence import SequenceLoop

        loop = SequenceLoop("while condition")

        assert loop.condition == "while condition"
        assert len(loop.messages) == 0
        assert len(loop.notes) == 0

    def test_add_message_to_loop(self) -> None:
        """Test adding message to loop."""
        from mermaid_render.models.sequence import SequenceLoop, SequenceMessage

        loop = SequenceLoop("while condition")
        message = SequenceMessage("A", "B", "Hello")

        loop.add_message(message)

        assert len(loop.messages) == 1
        assert loop.messages[0] is message

    def test_add_note_to_loop(self) -> None:
        """Test adding note to loop."""
        from mermaid_render.models.sequence import SequenceLoop, SequenceNote

        loop = SequenceLoop("while condition")
        note = SequenceNote("Loop note", "A")

        loop.add_note(note)

        assert len(loop.notes) == 1
        assert loop.notes[0] is note

    def test_loop_to_mermaid(self) -> None:
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

    def test_duplicate_participant_error(self) -> None:
        """Test adding duplicate participant."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        with pytest.raises(DiagramError, match="already exists"):
            sequence.add_participant("A", "Alice Again")

    def test_add_note_to_nonexistent_participant(self) -> None:
        """Test adding note to nonexistent participant."""
        sequence = SequenceDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            sequence.add_note("Test note", "nonexistent")

    def test_add_loop(self) -> None:
        """Test adding loop to sequence diagram."""
        sequence = SequenceDiagram()

        loop = sequence.add_loop("while condition")

        assert len(sequence.loops) == 1
        assert sequence.loops[0] is loop
        assert loop.condition == "while condition"

    def test_activate_participant(self) -> None:
        """Test activating participant."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        sequence.activate_participant("A")

        assert sequence.activations["A"] is True

    def test_activate_nonexistent_participant(self) -> None:
        """Test activating nonexistent participant."""
        sequence = SequenceDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            sequence.activate_participant("nonexistent")

    def test_deactivate_participant(self) -> None:
        """Test deactivating participant."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")

        sequence.deactivate_participant("A")

        assert sequence.activations["A"] is False

    def test_deactivate_nonexistent_participant(self) -> None:
        """Test deactivating nonexistent participant."""
        sequence = SequenceDiagram()

        with pytest.raises(DiagramError, match="does not exist"):
            sequence.deactivate_participant("nonexistent")

    def test_to_mermaid_with_loops(self) -> None:
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

    def test_to_mermaid_with_notes(self) -> None:
        """Test Mermaid generation with notes."""
        sequence = SequenceDiagram()
        sequence.add_participant("A", "Alice")
        sequence.add_note("Important note", "A", "right of")

        mermaid_code = sequence.to_mermaid()

        assert "note right of A: Important note" in mermaid_code


class TestGanttDiagram:
    """Test GanttDiagram class."""

    def test_diagram_creation(self) -> None:
        """Test creating a Gantt diagram."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram()

        assert diagram.get_diagram_type() == "gantt"
        assert diagram.date_format == "%Y-%m-%d"
        assert len(diagram.sections) == 0
        assert len(diagram.tasks) == 0

    def test_diagram_with_title_and_format(self) -> None:
        """Test Gantt diagram with title and custom date format."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram(title="Project Timeline", date_format="%m/%d/%Y")

        assert diagram.title == "Project Timeline"
        assert diagram.date_format == "%m/%d/%Y"

    def test_add_section(self) -> None:
        """Test adding sections to Gantt diagram."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram()
        diagram.add_section("Planning")
        diagram.add_section("Development")

        assert len(diagram.sections) == 2
        assert "Planning" in diagram.sections
        assert "Development" in diagram.sections

    def test_add_task(self) -> None:
        """Test adding tasks to Gantt diagram."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram()
        diagram.add_task("Task 1", "2024-01-01", "5d", "active")
        diagram.add_task("Task 2", "2024-01-06", "3d", "done")

        assert len(diagram.tasks) == 2
        assert diagram.tasks[0] == ("Task 1", "2024-01-01", "5d", "active")
        assert diagram.tasks[1] == ("Task 2", "2024-01-06", "3d", "done")

    def test_add_task_defaults(self) -> None:
        """Test adding task with default values."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram()
        diagram.add_task("Simple Task")

        assert len(diagram.tasks) == 1
        assert diagram.tasks[0] == ("Simple Task", None, None, "active")

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram()
        diagram.add_task("Task 1", "2024-01-01", "5d")

        mermaid_code = diagram.to_mermaid()

        assert "gantt" in mermaid_code
        assert "dateFormat %Y-%m-%d" in mermaid_code
        assert "Task 1 :active, 2024-01-01, 5d" in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram(title="Project Timeline")
        diagram.add_task("Task 1", "2024-01-01", "5d")

        mermaid_code = diagram.to_mermaid()

        assert "title Project Timeline" in mermaid_code

    def test_to_mermaid_with_sections(self) -> None:
        """Test Mermaid generation with sections."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram()
        diagram.add_section("Planning")
        diagram.add_task("Plan Task", "2024-01-01", "3d")
        diagram.add_section("Development")
        diagram.add_task("Dev Task", "2024-01-04", "5d")

        mermaid_code = diagram.to_mermaid()

        assert "section Planning" in mermaid_code
        assert "section Development" in mermaid_code
        assert "Plan Task :active, 2024-01-01, 3d" in mermaid_code
        assert "Dev Task :active, 2024-01-04, 5d" in mermaid_code

    def test_to_mermaid_with_task_status(self) -> None:
        """Test Mermaid generation with task status."""
        from mermaid_render.models.gantt import GanttDiagram

        diagram = GanttDiagram()
        diagram.add_task("Done Task", "2024-01-01", "3d", "done")
        diagram.add_task("Active Task", "2024-01-04", "5d", "active")
        diagram.add_task("Critical Task", "2024-01-09", "2d", "crit")

        mermaid_code = diagram.to_mermaid()

        assert "Done Task :done, 2024-01-01, 3d" in mermaid_code
        assert "Active Task :active, 2024-01-04, 5d" in mermaid_code
        assert "Critical Task :crit, 2024-01-09, 2d" in mermaid_code


class TestGitGraphDiagram:
    """Test GitGraphDiagram class."""

    def test_diagram_creation(self) -> None:
        """Test creating a Git graph diagram."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram()

        assert diagram.get_diagram_type() == "gitgraph"
        assert len(diagram.commits) == 0
        assert len(diagram.branches) == 0
        assert len(diagram.merges) == 0

    def test_diagram_with_title(self) -> None:
        """Test Git graph diagram with title."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram(title="Version Control Flow")

        assert diagram.title == "Version Control Flow"

    def test_add_commit(self) -> None:
        """Test adding commits to Git graph."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram()
        diagram.add_commit("Initial commit", "main")
        diagram.add_commit("Add feature", "feature")

        assert len(diagram.commits) == 2
        assert diagram.commits[0] == ("commit", "Initial commit", "main")
        assert diagram.commits[1] == ("commit", "Add feature", "feature")

    def test_add_commit_default_branch(self) -> None:
        """Test adding commit with default branch."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram()
        diagram.add_commit("Default branch commit")

        assert len(diagram.commits) == 1
        assert diagram.commits[0] == ("commit", "Default branch commit", "main")

    def test_add_branch(self) -> None:
        """Test adding branches to Git graph."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram()
        diagram.add_branch("feature")
        diagram.add_branch("hotfix")

        assert len(diagram.branches) == 2
        assert "feature" in diagram.branches
        assert "hotfix" in diagram.branches

    def test_add_merge(self) -> None:
        """Test adding merges to Git graph."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram()
        diagram.add_merge("feature", "main")
        diagram.add_merge("hotfix", "main")

        assert len(diagram.merges) == 2
        assert diagram.merges[0] == ("feature", "main")
        assert diagram.merges[1] == ("hotfix", "main")

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram()
        diagram.add_commit("Initial commit")

        mermaid_code = diagram.to_mermaid()

        assert "gitgraph" in mermaid_code
        assert "commit id: \"Initial commit\"" in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram(title="Git Flow")
        diagram.add_commit("Initial commit")

        mermaid_code = diagram.to_mermaid()

        assert "title: Git Flow" in mermaid_code

    def test_to_mermaid_with_branches_and_merges(self) -> None:
        """Test Mermaid generation with branches and merges."""
        from mermaid_render.models.git_graph import GitGraphDiagram

        diagram = GitGraphDiagram()
        diagram.add_commit("Initial commit", "main")
        diagram.add_branch("feature")
        diagram.add_commit("Feature work", "feature")
        diagram.add_merge("feature", "main")

        mermaid_code = diagram.to_mermaid()

        assert "gitgraph" in mermaid_code
        assert "commit id: \"Initial commit\"" in mermaid_code
        assert "branch feature" in mermaid_code
        assert "commit id: \"Feature work\"" in mermaid_code
        assert "merge feature" in mermaid_code


class TestMindmapDiagram:
    """Test MindmapDiagram class."""

    def test_diagram_creation(self) -> None:
        """Test creating a mindmap diagram."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram()

        assert diagram.get_diagram_type() == "mindmap"
        assert diagram.root.id == "root"
        assert diagram.root.text == "Root"
        assert len(diagram.root.children) == 0

    def test_diagram_with_title_and_root(self) -> None:
        """Test mindmap diagram with title and custom root."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram(title="Project Planning", root_text="Web App")

        assert diagram.title == "Project Planning"
        assert diagram.root.text == "Web App"

    def test_add_node_to_root(self) -> None:
        """Test adding nodes to root."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram()
        node1 = diagram.add_node("root", "frontend", "Frontend")
        node2 = diagram.add_node("root", "backend", "Backend")

        assert len(diagram.root.children) == 2
        assert node1.id == "frontend"
        assert node1.text == "Frontend"
        assert node2.id == "backend"
        assert node2.text == "Backend"

    def test_add_node_with_shape(self) -> None:
        """Test adding node with custom shape."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram()
        node = diagram.add_node("root", "important", "Important", shape="circle")

        assert node.shape == "circle"

    def test_add_nested_nodes(self) -> None:
        """Test adding nested nodes."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram()
        diagram.add_node("root", "frontend", "Frontend")
        diagram.add_node("frontend", "react", "React")
        diagram.add_node("frontend", "vue", "Vue")

        frontend_node = diagram.root.children[0]
        assert len(frontend_node.children) == 2
        assert frontend_node.children[0].text == "React"
        assert frontend_node.children[1].text == "Vue"

    def test_find_node(self) -> None:
        """Test finding nodes in the tree."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram()
        diagram.add_node("root", "frontend", "Frontend")
        diagram.add_node("frontend", "react", "React")

        # Test finding existing node
        frontend_node = diagram._find_node(diagram.root, "frontend")
        assert frontend_node is not None
        assert frontend_node.text == "Frontend"

        # Test finding non-existent node
        missing_node = diagram._find_node(diagram.root, "nonexistent")
        assert missing_node is None

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram(root_text="Central Idea")
        diagram.add_node("root", "branch1", "Branch 1")

        mermaid_code = diagram.to_mermaid()

        assert "mindmap" in mermaid_code
        assert "Central Idea" in mermaid_code
        assert "Branch 1" in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram(title="My Mindmap", root_text="Central")
        diagram.add_node("root", "branch1", "Branch 1")

        mermaid_code = diagram.to_mermaid()

        assert "title: My Mindmap" in mermaid_code

    def test_to_mermaid_with_shapes(self) -> None:
        """Test Mermaid generation with different shapes."""
        from mermaid_render.models.mindmap import MindmapDiagram

        diagram = MindmapDiagram(root_text="Root")
        diagram.add_node("root", "circle", "Circle Node", shape="circle")
        diagram.add_node("root", "bang", "Bang Node", shape="bang")
        diagram.add_node("root", "cloud", "Cloud Node", shape="cloud")

        mermaid_code = diagram.to_mermaid()

        assert "((Circle Node))" in mermaid_code
        assert ")Bang Node((" in mermaid_code
        assert "))Cloud Node(((" in mermaid_code


class TestPieChartDiagram:
    """Test PieChartDiagram class."""

    def test_diagram_creation(self) -> None:
        """Test creating a pie chart diagram."""
        from mermaid_render.models.pie_chart import PieChartDiagram

        diagram = PieChartDiagram()

        assert diagram.get_diagram_type() == "pie"
        assert diagram.show_data is True
        assert len(diagram.data) == 0

    def test_diagram_with_options(self) -> None:
        """Test pie chart diagram with options."""
        from mermaid_render.models.pie_chart import PieChartDiagram

        diagram = PieChartDiagram(title="Data Distribution", show_data=False)

        assert diagram.title == "Data Distribution"
        assert diagram.show_data is False

    def test_add_slice(self) -> None:
        """Test adding slices to pie chart."""
        from mermaid_render.models.pie_chart import PieChartDiagram

        diagram = PieChartDiagram()
        diagram.add_slice("Category A", 35.5)
        diagram.add_slice("Category B", 28.2)
        diagram.add_slice("Category C", 36.3)

        assert len(diagram.data) == 3
        assert diagram.data["Category A"] == 35.5
        assert diagram.data["Category B"] == 28.2
        assert diagram.data["Category C"] == 36.3

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.pie_chart import PieChartDiagram

        diagram = PieChartDiagram()
        diagram.add_slice("A", 50)
        diagram.add_slice("B", 30)
        diagram.add_slice("C", 20)

        mermaid_code = diagram.to_mermaid()

        assert "pie" in mermaid_code
        assert "showData" in mermaid_code
        assert '"A" : 50' in mermaid_code
        assert '"B" : 30' in mermaid_code
        assert '"C" : 20' in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.pie_chart import PieChartDiagram

        diagram = PieChartDiagram(title="Sales Data")
        diagram.add_slice("Q1", 25)

        mermaid_code = diagram.to_mermaid()

        assert "title Sales Data" in mermaid_code

    def test_to_mermaid_without_show_data(self) -> None:
        """Test Mermaid generation without show data."""
        from mermaid_render.models.pie_chart import PieChartDiagram

        diagram = PieChartDiagram(show_data=False)
        diagram.add_slice("A", 50)

        mermaid_code = diagram.to_mermaid()

        assert "pie" in mermaid_code
        assert "showData" not in mermaid_code
        assert '"A" : 50' in mermaid_code


class TestStateDiagram:
    """Test StateDiagram class."""

    def test_diagram_creation(self) -> None:
        """Test creating a state diagram."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram()

        assert diagram.get_diagram_type() == "stateDiagram-v2"
        assert len(diagram.states) == 0
        assert len(diagram.transitions) == 0

    def test_diagram_with_title(self) -> None:
        """Test state diagram with title."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram(title="State Machine")

        assert diagram.title == "State Machine"

    def test_add_state(self) -> None:
        """Test adding states to diagram."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram()
        diagram.add_state("idle", "Idle State")
        diagram.add_state("active")

        assert len(diagram.states) == 2
        assert diagram.states["idle"] == "Idle State"
        assert diagram.states["active"] == "active"

    def test_add_transition(self) -> None:
        """Test adding transitions between states."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram()
        diagram.add_transition("idle", "active", "start")
        diagram.add_transition("active", "idle")

        assert len(diagram.transitions) == 2
        assert diagram.transitions[0] == ("idle", "active", "start")
        assert diagram.transitions[1] == ("active", "idle", None)

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram()
        diagram.add_state("idle")
        diagram.add_transition("idle", "active")

        mermaid_code = diagram.to_mermaid()

        assert "stateDiagram-v2" in mermaid_code
        assert "idle --> active" in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram(title="State Machine")
        diagram.add_state("idle")

        mermaid_code = diagram.to_mermaid()

        assert "title: State Machine" in mermaid_code

    def test_to_mermaid_with_state_labels(self) -> None:
        """Test Mermaid generation with state labels."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram()
        diagram.add_state("idle", "Idle State")
        diagram.add_state("active", "Active State")

        mermaid_code = diagram.to_mermaid()

        assert "idle : Idle State" in mermaid_code
        assert "active : Active State" in mermaid_code

    def test_to_mermaid_with_transition_labels(self) -> None:
        """Test Mermaid generation with transition labels."""
        from mermaid_render.models.state import StateDiagram

        diagram = StateDiagram()
        diagram.add_transition("idle", "active", "start")
        diagram.add_transition("active", "idle", "stop")

        mermaid_code = diagram.to_mermaid()

        assert "idle --> active : start" in mermaid_code
        assert "active --> idle : stop" in mermaid_code


class TestUserJourneyDiagram:
    """Test UserJourneyDiagram class."""

    def test_diagram_creation(self) -> None:
        """Test creating a user journey diagram."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram()

        assert diagram.get_diagram_type() == "journey"
        assert len(diagram.sections) == 0
        assert len(diagram.tasks) == 0

    def test_diagram_with_title(self) -> None:
        """Test user journey diagram with title."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram(title="Customer Journey")

        assert diagram.title == "Customer Journey"

    def test_add_section(self) -> None:
        """Test adding sections to user journey."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram()
        diagram.add_section("Discovery")
        diagram.add_section("Purchase")

        assert len(diagram.sections) == 2
        assert diagram.sections[0] == ("section", "Discovery")
        assert diagram.sections[1] == ("section", "Purchase")

    def test_add_task(self) -> None:
        """Test adding tasks to user journey."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram()
        diagram.add_task("Search products", ["Customer", "Support"], 5)
        diagram.add_task("Add to cart", ["Customer"], 3)

        assert len(diagram.tasks) == 2
        assert diagram.tasks[0] == ("Search products", ["Customer", "Support"], 5)
        assert diagram.tasks[1] == ("Add to cart", ["Customer"], 3)

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram()
        diagram.add_task("Browse", ["Customer"], 4)

        mermaid_code = diagram.to_mermaid()

        assert "journey" in mermaid_code
        assert "Browse: 4: Customer" in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram(title="Shopping Journey")
        diagram.add_task("Browse", ["Customer"], 4)

        mermaid_code = diagram.to_mermaid()

        assert "title Shopping Journey" in mermaid_code

    def test_to_mermaid_with_sections(self) -> None:
        """Test Mermaid generation with sections."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram()
        diagram.add_section("Discovery")
        diagram.add_task("Search", ["Customer"], 5)
        diagram.add_section("Purchase")
        diagram.add_task("Buy", ["Customer", "Payment"], 3)

        mermaid_code = diagram.to_mermaid()

        assert "section Discovery" in mermaid_code
        assert "section Purchase" in mermaid_code
        assert "Search: 5: Customer" in mermaid_code
        assert "Buy: 3: Customer : Payment" in mermaid_code

    def test_to_mermaid_multiple_actors(self) -> None:
        """Test Mermaid generation with multiple actors."""
        from mermaid_render.models.user_journey import UserJourneyDiagram

        diagram = UserJourneyDiagram()
        diagram.add_task("Complex task", ["Customer", "Support", "Admin"], 4)

        mermaid_code = diagram.to_mermaid()

        assert "Complex task: 4: Customer : Support : Admin" in mermaid_code


class TestMindmapNode:
    """Test MindmapNode class."""

    def test_node_creation(self) -> None:
        """Test creating a mindmap node."""
        from mermaid_render.models.mindmap import MindmapNode

        node = MindmapNode("test", "Test Node")

        assert node.id == "test"
        assert node.text == "Test Node"
        assert node.shape == "default"
        assert len(node.children) == 0

    def test_node_with_shape(self) -> None:
        """Test creating node with custom shape."""
        from mermaid_render.models.mindmap import MindmapNode

        node = MindmapNode("test", "Test Node", shape="circle")

        assert node.shape == "circle"

    def test_add_child(self) -> None:
        """Test adding child nodes."""
        from mermaid_render.models.mindmap import MindmapNode

        parent = MindmapNode("parent", "Parent")
        child1 = MindmapNode("child1", "Child 1")
        child2 = MindmapNode("child2", "Child 2")

        parent.add_child(child1)
        parent.add_child(child2)

        assert len(parent.children) == 2
        assert parent.children[0] is child1
        assert parent.children[1] is child2

    def test_to_mermaid_default_shape(self) -> None:
        """Test Mermaid generation for default shape."""
        from mermaid_render.models.mindmap import MindmapNode

        node = MindmapNode("test", "Test Node")
        lines = node.to_mermaid()

        assert lines == ["Test Node"]

    def test_to_mermaid_circle_shape(self) -> None:
        """Test Mermaid generation for circle shape."""
        from mermaid_render.models.mindmap import MindmapNode

        node = MindmapNode("test", "Circle Node", shape="circle")
        lines = node.to_mermaid()

        assert lines == ["((Circle Node))"]

    def test_to_mermaid_with_children(self) -> None:
        """Test Mermaid generation with children."""
        from mermaid_render.models.mindmap import MindmapNode

        parent = MindmapNode("parent", "Parent")
        child = MindmapNode("child", "Child")
        parent.add_child(child)

        lines = parent.to_mermaid()

        assert "Parent" in lines
        assert "  Child" in lines

    def test_to_mermaid_nested_levels(self) -> None:
        """Test Mermaid generation with multiple nesting levels."""
        from mermaid_render.models.mindmap import MindmapNode

        root = MindmapNode("root", "Root")
        level1 = MindmapNode("l1", "Level 1")
        level2 = MindmapNode("l2", "Level 2")

        root.add_child(level1)
        level1.add_child(level2)

        lines = root.to_mermaid()

        assert "Root" in lines
        assert "  Level 1" in lines
        assert "    Level 2" in lines

    def test_to_mermaid_all_shapes(self) -> None:
        """Test Mermaid generation for all supported shapes."""
        from mermaid_render.models.mindmap import MindmapNode

        shapes_to_test = [
            ("default", "Default", "Default"),
            ("circle", "Circle", "((Circle))"),
            ("bang", "Bang", ")Bang(("),
            ("cloud", "Cloud", "))Cloud((("),
            ("hexagon", "Hexagon", ")Hexagon(("),
        ]

        for shape, text, expected in shapes_to_test:
            node = MindmapNode("test", text, shape=shape)
            lines = node.to_mermaid()
            assert expected in lines[0]


class TestClassMethod:
    """Test ClassMethod class."""

    def test_method_creation(self) -> None:
        """Test creating a class method."""
        from mermaid_render.models.class_diagram import ClassMethod

        method = ClassMethod("getName", "public", "String", ["id: int"])

        assert method.name == "getName"
        assert method.visibility == "public"
        assert method.return_type == "String"
        assert method.parameters == ["id: int"]
        assert method.is_static is False
        assert method.is_abstract is False

    def test_method_to_mermaid_basic(self) -> None:
        """Test basic method Mermaid generation."""
        from mermaid_render.models.class_diagram import ClassMethod

        method = ClassMethod("getName", "public", "String")

        assert method.to_mermaid() == "+getName() String"

    def test_method_to_mermaid_with_parameters(self) -> None:
        """Test method with parameters."""
        from mermaid_render.models.class_diagram import ClassMethod

        method = ClassMethod("setName", "public", "void", ["name: String", "id: int"])

        assert method.to_mermaid() == "+setName(name: String, id: int) void"

    def test_method_visibility_symbols(self) -> None:
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

    def test_method_static_and_abstract(self) -> None:
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

    def test_attribute_creation(self) -> None:
        """Test creating a class attribute."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("name", "String", "private", is_static=False)

        assert attr.name == "name"
        assert attr.type == "String"
        assert attr.visibility == "private"
        assert attr.is_static is False

    def test_attribute_to_mermaid_basic(self) -> None:
        """Test basic attribute Mermaid generation."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("name", "String", "private")

        assert attr.to_mermaid() == "-name String"

    def test_attribute_without_type(self) -> None:
        """Test attribute without type."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("count", visibility="public")

        assert attr.to_mermaid() == "+count"

    def test_attribute_static(self) -> None:
        """Test static attribute."""
        from mermaid_render.models.class_diagram import ClassAttribute

        attr = ClassAttribute("instance", "MyClass", "private", is_static=True)

        assert attr.to_mermaid() == "-instance MyClass$"

    def test_attribute_visibility_symbols(self) -> None:
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

    def test_class_creation(self) -> None:
        """Test creating a class definition."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("MyClass")

        assert class_def.name == "MyClass"
        assert class_def.is_abstract is False
        assert class_def.is_interface is False
        assert class_def.stereotype is None
        assert len(class_def.attributes) == 0
        assert len(class_def.methods) == 0

    def test_abstract_class(self) -> None:
        """Test creating abstract class."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("AbstractClass", is_abstract=True)

        assert class_def.is_abstract is True

        lines = class_def.to_mermaid()
        assert "class AbstractClass {" in lines
        assert "    <<abstract>>" in lines
        assert "}" in lines

    def test_interface_class(self) -> None:
        """Test creating interface."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("MyInterface", is_interface=True)

        assert class_def.is_interface is True

        lines = class_def.to_mermaid()
        assert "class MyInterface {" in lines
        assert "    <<interface>>" in lines
        assert "}" in lines

    def test_class_with_stereotype(self) -> None:
        """Test class with stereotype."""
        from mermaid_render.models.class_diagram import ClassDefinition

        class_def = ClassDefinition("MyClass", stereotype="entity")

        lines = class_def.to_mermaid()
        assert "class MyClass {" in lines
        assert "    <<entity>>" in lines
        assert "}" in lines

    def test_add_attribute_and_method(self) -> None:
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

    def test_class_to_mermaid_complete(self) -> None:
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

    def test_relationship_creation(self) -> None:
        """Test creating a class relationship."""
        from mermaid_render.models.class_diagram import ClassRelationship

        rel = ClassRelationship("Dog", "Animal", "inheritance")

        assert rel.from_class == "Dog"
        assert rel.to_class == "Animal"
        assert rel.relationship_type == "inheritance"
        assert rel.label is None
        assert rel.from_cardinality is None
        assert rel.to_cardinality is None

    def test_invalid_relationship_type(self) -> None:
        """Test creating relationship with invalid type."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassRelationship

        with pytest.raises(DiagramError, match="Unknown relationship type"):
            ClassRelationship("A", "B", "invalid_type")

    def test_all_relationship_types(self) -> None:
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

    def test_relationship_with_label(self) -> None:
        """Test relationship with label."""
        from mermaid_render.models.class_diagram import ClassRelationship

        rel = ClassRelationship("Dog", "Owner", "association", label="belongs to")

        assert rel.to_mermaid() == "Dog --> Owner : belongs to"

    def test_relationship_with_cardinality(self) -> None:
        """Test relationship with cardinality."""
        from mermaid_render.models.class_diagram import ClassRelationship

        rel = ClassRelationship(
            "Order", "Item", "composition", from_cardinality="1", to_cardinality="*"
        )

        assert rel.to_mermaid() == 'Order "1" *-- "*" Item'

    def test_relationship_complete(self) -> None:
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

    def test_diagram_creation(self) -> None:
        """Test creating a class diagram."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()

        assert diagram.get_diagram_type() == "classDiagram"
        assert len(diagram.classes) == 0
        assert len(diagram.relationships) == 0

    def test_diagram_with_title(self) -> None:
        """Test class diagram with title."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram(title="Animal Hierarchy")

        assert diagram.title == "Animal Hierarchy"

    def test_add_class(self) -> None:
        """Test adding class to diagram."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        class_def = diagram.add_class("Animal")

        assert len(diagram.classes) == 1
        assert "Animal" in diagram.classes
        assert diagram.classes["Animal"] is class_def
        assert class_def.name == "Animal"

    def test_add_duplicate_class(self) -> None:
        """Test adding duplicate class."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Animal")

        with pytest.raises(DiagramError, match="already exists"):
            diagram.add_class("Animal")

    def test_add_class_with_options(self) -> None:
        """Test adding class with options."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        class_def = diagram.add_class("Animal", is_abstract=True, stereotype="entity")

        assert class_def.is_abstract is True
        assert class_def.stereotype == "entity"

    def test_add_relationship(self) -> None:
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

    def test_add_relationship_nonexistent_from_class(self) -> None:
        """Test adding relationship with nonexistent from class."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Animal")

        with pytest.raises(DiagramError, match="does not exist"):
            diagram.add_relationship("NonExistent", "Animal", "inheritance")

    def test_add_relationship_nonexistent_to_class(self) -> None:
        """Test adding relationship with nonexistent to class."""
        from mermaid_render.exceptions import DiagramError
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Dog")

        with pytest.raises(DiagramError, match="does not exist"):
            diagram.add_relationship("Dog", "NonExistent", "inheritance")

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Animal")

        mermaid_code = diagram.to_mermaid()

        assert "classDiagram" in mermaid_code
        assert "class Animal {" in mermaid_code
        assert "}" in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram(title="Animal Hierarchy")
        diagram.add_class("Animal")

        mermaid_code = diagram.to_mermaid()

        assert "title: Animal Hierarchy" in mermaid_code

    def test_to_mermaid_with_relationships(self) -> None:
        """Test Mermaid generation with relationships."""
        from mermaid_render.models.class_diagram import ClassDiagram

        diagram = ClassDiagram()
        diagram.add_class("Dog")
        diagram.add_class("Animal")
        diagram.add_relationship("Dog", "Animal", "inheritance")

        mermaid_code = diagram.to_mermaid()

        assert "Dog <|-- Animal" in mermaid_code

    def test_to_mermaid_complete(self) -> None:
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

    def test_diagram_creation(self) -> None:
        """Test creating an ER diagram."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()

        assert diagram.get_diagram_type() == "erDiagram"
        assert len(diagram.entities) == 0
        assert len(diagram.relationships) == 0

    def test_diagram_with_title(self) -> None:
        """Test ER diagram with title."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram(title="Customer Database")

        assert diagram.title == "Customer Database"

    def test_add_entity_without_attributes(self) -> None:
        """Test adding entity without attributes."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")

        assert len(diagram.entities) == 1
        assert "Customer" in diagram.entities
        assert diagram.entities["Customer"] == {}

    def test_add_entity_with_attributes(self) -> None:
        """Test adding entity with attributes."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        attributes = {"id": "int", "name": "string", "email": "string"}
        diagram.add_entity("Customer", attributes)

        assert len(diagram.entities) == 1
        assert "Customer" in diagram.entities
        assert diagram.entities["Customer"] == attributes

    def test_add_relationship(self) -> None:
        """Test adding relationship between entities."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")
        diagram.add_entity("Order")
        diagram.add_relationship("Customer", "Order", "||--o{")

        assert len(diagram.relationships) == 1
        assert diagram.relationships[0] == ("Customer", "Order", "||--o{")

    def test_to_mermaid_basic(self) -> None:
        """Test basic Mermaid generation."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")

        mermaid_code = diagram.to_mermaid()

        assert "erDiagram" in mermaid_code
        assert "Customer {" in mermaid_code
        assert "}" in mermaid_code

    def test_to_mermaid_with_title(self) -> None:
        """Test Mermaid generation with title."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram(title="Customer Database")
        diagram.add_entity("Customer")

        mermaid_code = diagram.to_mermaid()

        assert "title: Customer Database" in mermaid_code

    def test_to_mermaid_with_attributes(self) -> None:
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

    def test_to_mermaid_with_relationships(self) -> None:
        """Test Mermaid generation with relationships."""
        from mermaid_render.models.er_diagram import ERDiagram

        diagram = ERDiagram()
        diagram.add_entity("Customer")
        diagram.add_entity("Order")
        diagram.add_relationship("Customer", "Order", "||--o{")

        mermaid_code = diagram.to_mermaid()

        assert "Customer ||--o{ Order" in mermaid_code

    def test_to_mermaid_complete(self) -> None:
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
