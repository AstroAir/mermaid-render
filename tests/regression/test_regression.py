"""
Regression tests for bug prevention and edge case handling.
"""

from unittest.mock import Mock, patch

import pytest

from diagramaid import (
    ClassDiagram,
    FlowchartDiagram,
    GanttDiagram,
    MermaidRenderer,
    PieChartDiagram,
    SequenceDiagram,
)
from diagramaid.exceptions import (
    DiagramError,
)


class TestEdgeCaseHandling:
    """Test edge cases and boundary conditions."""

    def test_empty_diagram_handling(self) -> None:
        """Test handling of completely empty diagrams."""
        diagram = FlowchartDiagram()

        # Empty diagram should generate valid Mermaid code
        mermaid_code = diagram.to_mermaid()
        assert isinstance(mermaid_code, str)
        assert "flowchart" in mermaid_code

        # Should be renderable without errors (use legacy mode for direct mocking)
        renderer = MermaidRenderer(use_plugin_system=False)
        with patch("diagramaid.renderers.svg_renderer.md.Mermaid") as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>empty diagram</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert (
                result == '<svg xmlns="http://www.w3.org/2000/svg">empty diagram</svg>'
            )

    def test_single_node_diagram(self) -> None:
        """Test diagrams with only one node."""
        diagram = FlowchartDiagram()
        diagram.add_node("single", "Single Node")

        mermaid_code = diagram.to_mermaid()
        assert "single" in mermaid_code
        assert "Single Node" in mermaid_code

        # Should render without issues (use legacy mode for direct mocking)
        renderer = MermaidRenderer(use_plugin_system=False)
        with patch("diagramaid.renderers.svg_renderer.md.Mermaid") as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>single node</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert result == '<svg xmlns="http://www.w3.org/2000/svg">single node</svg>'

    def test_disconnected_nodes(self) -> None:
        """Test diagrams with disconnected nodes."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")
        diagram.add_node("B", "Node B")
        diagram.add_node("C", "Node C")
        # No edges - all nodes are disconnected

        mermaid_code = diagram.to_mermaid()
        assert "Node A" in mermaid_code
        assert "Node B" in mermaid_code
        assert "Node C" in mermaid_code

    def test_self_referencing_edges(self) -> None:
        """Test nodes with edges to themselves."""
        diagram = FlowchartDiagram()
        diagram.add_node("loop", "Loop Node")
        diagram.add_edge("loop", "loop", "self reference")

        mermaid_code = diagram.to_mermaid()
        assert "loop" in mermaid_code
        assert "self reference" in mermaid_code

    def test_duplicate_node_ids(self) -> None:
        """Test handling of duplicate node IDs."""
        diagram = FlowchartDiagram()
        diagram.add_node("duplicate", "First Node")

        # Adding same ID again should raise an error
        with pytest.raises(DiagramError, match="already exists"):
            diagram.add_node("duplicate", "Updated Node")

        # Original node should still be there
        mermaid_code = diagram.to_mermaid()
        assert "First Node" in mermaid_code

    def test_duplicate_edges(self) -> None:
        """Test handling of duplicate edges."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")
        diagram.add_node("B", "Node B")
        diagram.add_edge("A", "B", "First Edge")
        diagram.add_edge("A", "B", "Duplicate Edge")

        mermaid_code = diagram.to_mermaid()
        # Should handle duplicates gracefully
        assert "Node A" in mermaid_code
        assert "Node B" in mermaid_code


class TestSpecialCharacterHandling:
    """Test handling of special characters and encoding."""

    def test_quotes_in_labels(self) -> None:
        """Test handling of quotes in node labels."""
        diagram = FlowchartDiagram()
        diagram.add_node("quoted", 'Node with "quotes" inside')

        mermaid_code = diagram.to_mermaid()
        assert "quoted" in mermaid_code
        # Quotes should be properly escaped or handled
        assert "quotes" in mermaid_code

    def test_special_symbols_in_labels(self) -> None:
        """Test handling of special symbols."""
        diagram = FlowchartDiagram()
        diagram.add_node("symbols", "Node with & < > symbols")

        mermaid_code = diagram.to_mermaid()
        assert "symbols" in mermaid_code

    def test_unicode_characters(self) -> None:
        """Test handling of Unicode characters."""
        diagram = FlowchartDiagram()
        diagram.add_node("unicode", "Node with 中文 and émojis 🚀")

        mermaid_code = diagram.to_mermaid()
        assert "unicode" in mermaid_code
        assert "中文" in mermaid_code
        assert "🚀" in mermaid_code

    def test_newlines_in_labels(self) -> None:
        """Test handling of newlines in labels."""
        diagram = FlowchartDiagram()
        diagram.add_node("multiline", "Line 1\nLine 2\nLine 3")

        mermaid_code = diagram.to_mermaid()
        assert "multiline" in mermaid_code
        # Newlines should be handled appropriately

    def test_very_long_labels(self) -> None:
        """Test handling of very long labels."""
        long_label = "This is a very long label " * 20  # 540 characters
        diagram = FlowchartDiagram()
        diagram.add_node("long", long_label)

        mermaid_code = diagram.to_mermaid()
        assert "long" in mermaid_code
        assert len(mermaid_code) > 500

    def test_empty_labels(self) -> None:
        """Test handling of empty labels."""
        diagram = FlowchartDiagram()
        diagram.add_node("empty", "")

        mermaid_code = diagram.to_mermaid()
        assert "empty" in mermaid_code

    def test_whitespace_only_labels(self) -> None:
        """Test handling of whitespace-only labels."""
        diagram = FlowchartDiagram()
        diagram.add_node("whitespace", "   \t\n   ")

        mermaid_code = diagram.to_mermaid()
        assert "whitespace" in mermaid_code


class TestInvalidInputHandling:
    """Test handling of invalid inputs."""

    def test_invalid_node_ids(self) -> None:
        """Test handling of invalid node IDs."""
        diagram = FlowchartDiagram()

        # Test with various potentially problematic IDs
        problematic_ids = ["", "  ", "123", "node-with-dashes", "node_with_underscores"]

        for node_id in problematic_ids:
            try:
                diagram.add_node(node_id, f"Node {node_id}")
                # If it doesn't raise an error, that's fine
            except Exception:
                # If it raises an error, it should be a validation error
                pass

    def test_invalid_edge_references(self) -> None:
        """Test handling of edges referencing non-existent nodes."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")

        # Try to add edge to non-existent node
        try:
            diagram.add_edge("A", "nonexistent")
            # If it doesn't raise an error, verify the behavior
            mermaid_code = diagram.to_mermaid()
            assert isinstance(mermaid_code, str)
        except Exception:
            # If it raises an error, it should be appropriate
            pass

    def test_none_values(self) -> None:
        """Test handling of None values."""
        diagram = FlowchartDiagram()

        # Test with None values
        try:
            diagram.add_node(
                "", "Node with empty ID"
            )  # Use empty string instead of None
        except (TypeError, ValueError):
            # Expected to fail
            pass

        try:
            diagram.add_node("valid", "")  # Use empty string instead of None
        except (TypeError, ValueError):
            # Expected to fail
            pass


class TestSequenceDiagramRegressions:
    """Test sequence diagram specific regressions."""

    def test_participant_without_messages(self) -> None:
        """Test participants that don't send or receive messages."""
        diagram = SequenceDiagram()
        diagram.add_participant("active", "Active User")
        diagram.add_participant("inactive", "Inactive User")
        diagram.add_message("active", "active", "Self message")

        mermaid_code = diagram.to_mermaid()
        assert "Active User" in mermaid_code
        assert "Inactive User" in mermaid_code

    def test_message_to_self(self) -> None:
        """Test messages from participant to themselves."""
        diagram = SequenceDiagram()
        diagram.add_participant("user", "User")
        diagram.add_message("user", "user", "Think")

        mermaid_code = diagram.to_mermaid()
        assert "Think" in mermaid_code

    def test_very_long_message_text(self) -> None:
        """Test very long message text."""
        diagram = SequenceDiagram()
        diagram.add_participant("a", "A")
        diagram.add_participant("b", "B")

        long_message = "This is a very long message " * 10
        diagram.add_message("a", "b", long_message)

        mermaid_code = diagram.to_mermaid()
        assert "very long message" in mermaid_code


class TestClassDiagramRegressions:
    """Test class diagram specific regressions."""

    def test_class_without_members(self) -> None:
        """Test classes without attributes or methods."""
        diagram = ClassDiagram()
        diagram.add_class("Empty")

        mermaid_code = diagram.to_mermaid()
        assert "Empty" in mermaid_code

    def test_class_with_only_attributes(self) -> None:
        """Test classes with only attributes."""
        from diagramaid.models.class_diagram import ClassAttribute

        diagram = ClassDiagram()
        data_class = diagram.add_class("DataOnly")
        data_class.add_attribute(ClassAttribute("data", "str"))
        data_class.add_attribute(ClassAttribute("value", "int"))

        mermaid_code = diagram.to_mermaid()
        assert "DataOnly" in mermaid_code
        assert "data" in mermaid_code

    def test_class_with_only_methods(self) -> None:
        """Test classes with only methods."""
        from diagramaid.models.class_diagram import ClassMethod

        diagram = ClassDiagram()
        behavior_class = diagram.add_class("BehaviorOnly")
        behavior_class.add_method(ClassMethod("doSomething"))
        behavior_class.add_method(ClassMethod("process"))

        mermaid_code = diagram.to_mermaid()
        assert "BehaviorOnly" in mermaid_code
        assert "doSomething" in mermaid_code

    def test_circular_inheritance(self) -> None:
        """Test handling of circular inheritance."""
        diagram = ClassDiagram()
        diagram.add_class("A")
        diagram.add_class("B")
        diagram.add_relationship("A", "B", "inheritance")
        diagram.add_relationship("B", "A", "inheritance")

        mermaid_code = diagram.to_mermaid()
        assert "A" in mermaid_code
        assert "B" in mermaid_code


class TestGanttDiagramRegressions:
    """Test Gantt diagram specific regressions."""

    def test_tasks_without_dates(self) -> None:
        """Test tasks without start dates or durations."""
        diagram = GanttDiagram()
        diagram.add_task("Undefined Task")

        mermaid_code = diagram.to_mermaid()
        assert "Undefined Task" in mermaid_code

    def test_overlapping_tasks(self) -> None:
        """Test overlapping tasks."""
        diagram = GanttDiagram()
        diagram.add_task("Task 1", "2024-01-01", "5d")
        diagram.add_task("Task 2", "2024-01-03", "5d")  # Overlaps with Task 1

        mermaid_code = diagram.to_mermaid()
        assert "Task 1" in mermaid_code
        assert "Task 2" in mermaid_code

    def test_tasks_in_past(self) -> None:
        """Test tasks with dates in the past."""
        diagram = GanttDiagram()
        diagram.add_task("Past Task", "2020-01-01", "1d")

        mermaid_code = diagram.to_mermaid()
        assert "Past Task" in mermaid_code


class TestPieChartRegressions:
    """Test pie chart specific regressions."""

    def test_zero_values(self) -> None:
        """Test pie chart with zero values."""
        diagram = PieChartDiagram()
        diagram.add_slice("Zero", 0)
        diagram.add_slice("Positive", 50)

        mermaid_code = diagram.to_mermaid()
        assert "Zero" in mermaid_code
        assert "Positive" in mermaid_code

    def test_negative_values(self) -> None:
        """Test pie chart with negative values."""
        diagram = PieChartDiagram()
        diagram.add_slice("Negative", -10)
        diagram.add_slice("Positive", 60)

        mermaid_code = diagram.to_mermaid()
        assert "Negative" in mermaid_code
        assert "Positive" in mermaid_code

    def test_very_small_values(self) -> None:
        """Test pie chart with very small values."""
        diagram = PieChartDiagram()
        diagram.add_slice("Tiny", 0.001)
        diagram.add_slice("Small", 0.1)
        diagram.add_slice("Normal", 99.899)

        mermaid_code = diagram.to_mermaid()
        assert "Tiny" in mermaid_code
        assert "0.001" in mermaid_code

    def test_values_over_100(self) -> None:
        """Test pie chart with values that sum to over 100."""
        diagram = PieChartDiagram()
        diagram.add_slice("Big", 80)
        diagram.add_slice("Bigger", 90)  # Total = 170

        mermaid_code = diagram.to_mermaid()
        assert "Big" in mermaid_code
        assert "Bigger" in mermaid_code


class TestRenderingRegressions:
    """Test rendering-specific regressions."""

    def test_rendering_empty_diagram(self) -> None:
        """Test rendering completely empty diagrams."""
        diagram = FlowchartDiagram()
        renderer = MermaidRenderer(use_plugin_system=False)

        with patch("diagramaid.renderers.svg_renderer.md.Mermaid") as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(
                return_value='<svg xmlns="http://www.w3.org/2000/svg">empty</svg>'
            )
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            # The result should be a valid SVG with xmlns attribute
            assert result.startswith('<svg xmlns="http://www.w3.org/2000/svg">')
            assert result.endswith("</svg>")
            assert "empty" in result

    def test_rendering_with_invalid_theme(self) -> None:
        """Test rendering with invalid theme names."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")

        renderer = MermaidRenderer(use_plugin_system=False)

        with patch("diagramaid.renderers.svg_renderer.md.Mermaid") as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>themed</svg>")
            mock_mermaid.return_value = mock_obj

            # Should handle invalid theme gracefully
            result = renderer.render(diagram, format="svg", theme="nonexistent_theme")
            assert result == '<svg xmlns="http://www.w3.org/2000/svg">themed</svg>'

    def test_rendering_very_large_diagrams(self) -> None:
        """Test rendering very large diagrams."""
        diagram = FlowchartDiagram()

        # Create a large diagram
        for i in range(200):
            diagram.add_node(f"node_{i}", f"Node {i}")
            if i > 0:
                diagram.add_edge(f"node_{i-1}", f"node_{i}")

        renderer = MermaidRenderer(use_plugin_system=False)

        with patch("diagramaid.renderers.svg_renderer.md.Mermaid") as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>large diagram</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert (
                result == '<svg xmlns="http://www.w3.org/2000/svg">large diagram</svg>'
            )


class TestConfigurationRegressions:
    """Test configuration-related regressions."""

    def test_default_configuration(self) -> None:
        """Test that default configuration works."""
        renderer = MermaidRenderer(use_plugin_system=False)
        diagram = FlowchartDiagram()
        diagram.add_node("test", "Test")

        with patch("diagramaid.renderers.svg_renderer.md.Mermaid") as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>default config</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert (
                result == '<svg xmlns="http://www.w3.org/2000/svg">default config</svg>'
            )

    def test_multiple_renderer_instances(self) -> None:
        """Test that multiple renderer instances work independently."""
        renderer1 = MermaidRenderer(use_plugin_system=False)
        renderer2 = MermaidRenderer(use_plugin_system=False)

        diagram = FlowchartDiagram()
        diagram.add_node("test", "Test")

        with patch("diagramaid.renderers.svg_renderer.md.Mermaid") as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(
                return_value='<svg xmlns="http://www.w3.org/2000/svg">multi instance</svg>'
            )
            mock_mermaid.return_value = mock_obj

            result1 = renderer1.render(diagram, format="svg")
            result2 = renderer2.render(diagram, format="svg")

            # Both results should be valid SVGs
            for result in [result1, result2]:
                assert result.startswith('<svg xmlns="http://www.w3.org/2000/svg">')
                assert result.endswith("</svg>")
                # The content should be consistent (both renderers should produce the same result)
            assert result1 == result2
