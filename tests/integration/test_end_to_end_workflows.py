"""
Integration tests for end-to-end workflows.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mermaid_render import (
    MermaidRenderer,
    FlowchartDiagram,
    SequenceDiagram,
    ClassDiagram,
    quick_render,
)
from mermaid_render.exceptions import ValidationError, RenderingError, UnsupportedFormatError


class TestBasicWorkflows:
    """Test basic end-to-end workflows."""

    def test_flowchart_creation_and_rendering(self):
        """Test complete flowchart workflow."""
        # Create diagram
        diagram = FlowchartDiagram()
        diagram.add_node("start", "Start", shape="circle")
        diagram.add_node("process", "Process Data")
        diagram.add_node("end", "End", shape="circle")

        diagram.add_edge("start", "process")
        diagram.add_edge("process", "end")

        # Generate Mermaid code
        mermaid_code = diagram.to_mermaid()
        assert "flowchart" in mermaid_code
        assert "Start" in mermaid_code
        assert "Process Data" in mermaid_code

        # Render diagram
        renderer = MermaidRenderer()

        # Mock the mermaid-py library to avoid actual rendering
        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>test content</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert result == "<svg>test content</svg>"
            mock_mermaid.assert_called_once()

    def test_sequence_diagram_workflow(self):
        """Test sequence diagram workflow."""
        # Create sequence diagram
        diagram = SequenceDiagram()
        diagram.add_participant("user", "User")
        diagram.add_participant("api", "API Server")
        diagram.add_participant("db", "Database")

        diagram.add_message("user", "api", "Login Request")
        diagram.add_message("api", "db", "Validate User")
        diagram.add_message("db", "api", "User Valid")
        diagram.add_message("api", "user", "Login Success")

        # Generate and verify code
        mermaid_code = diagram.to_mermaid()
        assert "sequenceDiagram" in mermaid_code
        assert "Login Request" in mermaid_code

        # Render (PNG not implemented in current version, so test SVG)
        renderer = MermaidRenderer()
        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>sequence diagram</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert result == "<svg>sequence diagram</svg>"

    def test_class_diagram_workflow(self):
        """Test class diagram workflow."""
        # Create class diagram
        diagram = ClassDiagram()
        diagram.add_class("User", ["name: str", "email: str"], ["login()", "logout()"])
        diagram.add_class("Admin", ["permissions: list"], ["manage_users()"])

        diagram.add_relationship("Admin", "User", "inheritance")

        # Generate and verify code
        mermaid_code = diagram.to_mermaid()
        assert "classDiagram" in mermaid_code
        assert "User" in mermaid_code
        assert "Admin" in mermaid_code

        # Render
        renderer = MermaidRenderer()
        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>PDF data</svg>")
            mock_mermaid.return_value = mock_obj

            # For now, only SVG is supported, so test that
            result = renderer.render(diagram, format="svg")
            assert "<svg>" in result

    def test_quick_render_function(self):
        """Test quick render utility function."""
        mermaid_code = "flowchart TD\n    A --> B\n    B --> C"

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>quick render</svg>")
            mock_mermaid.return_value = mock_obj

            result = quick_render(mermaid_code, format="svg")

            assert result == "<svg>quick render</svg>"
            mock_mermaid.assert_called_once()

    def test_file_output_workflow(self):
        """Test rendering to file."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")
        diagram.add_node("B", "Node B")
        diagram.add_edge("A", "B")

        renderer = MermaidRenderer()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_diagram.svg"

            with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
                mock_obj = Mock()
                mock_obj.__str__ = Mock(return_value="<svg>file content</svg>")
                mock_mermaid.return_value = mock_obj

                renderer.save(diagram, str(output_path), format="svg")

                assert output_path.exists()
                content = output_path.read_text()
                assert content == "<svg>file content</svg>"


class TestErrorHandlingWorkflows:
    """Test error handling in workflows."""

    def test_invalid_diagram_validation(self):
        """Test validation error handling."""
        # Create invalid diagram (empty)
        diagram = FlowchartDiagram()

        renderer = MermaidRenderer()

        # Should handle empty diagram gracefully
        mermaid_code = diagram.to_mermaid()
        assert isinstance(mermaid_code, str)

    def test_rendering_failure_handling(self):
        """Test rendering failure handling."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")

        renderer = MermaidRenderer()

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_mermaid.side_effect = RenderingError("Service unavailable")

            with pytest.raises(RenderingError):
                renderer.render(diagram, format="svg")

    def test_unsupported_format_handling(self):
        """Test unsupported format handling."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")

        renderer = MermaidRenderer()

        # Test with unsupported format
        with pytest.raises(Exception):  # Should raise some kind of error
            renderer.render(diagram, format="unsupported_format")

    def test_file_permission_error_handling(self):
        """Test file permission error handling."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")

        renderer = MermaidRenderer()

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>content</svg>")
            mock_mermaid.return_value = mock_obj

            # Try to write to invalid path
            with pytest.raises(PermissionError):
                renderer.save(diagram, "/root/invalid_path.svg", format="svg")


class TestComplexWorkflows:
    """Test complex multi-step workflows."""

    def test_multi_diagram_batch_processing(self):
        """Test processing multiple diagrams."""
        diagrams = []

        # Create multiple diagrams
        for i in range(3):
            diagram = FlowchartDiagram()
            diagram.add_node(f"start_{i}", f"Start {i}")
            diagram.add_node(f"end_{i}", f"End {i}")
            diagram.add_edge(f"start_{i}", f"end_{i}")
            diagrams.append(diagram)

        renderer = MermaidRenderer()
        results = []

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_objects = []
            for i in range(3):
                mock_obj = Mock()
                mock_obj.__str__ = Mock(return_value=f"<svg>diagram {i}</svg>")
                mock_objects.append(mock_obj)
            mock_mermaid.side_effect = mock_objects

            for i, diagram in enumerate(diagrams):
                result = renderer.render(diagram, format="svg")
                results.append(result)
                assert result == f"<svg>diagram {i}</svg>"

        assert len(results) == 3
        assert mock_mermaid.call_count == 3

    def test_diagram_modification_workflow(self):
        """Test modifying and re-rendering diagrams."""
        # Create initial diagram
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Initial Node")

        renderer = MermaidRenderer()

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            # First call
            mock_obj1 = Mock()
            mock_obj1.__str__ = Mock(return_value="<svg>initial</svg>")

            # Second call
            mock_obj2 = Mock()
            mock_obj2.__str__ = Mock(return_value="<svg>modified</svg>")

            mock_mermaid.side_effect = [mock_obj1, mock_obj2]

            # Initial render
            result1 = renderer.render(diagram, format="svg")
            assert result1 == "<svg>initial</svg>"

            # Modify diagram
            diagram.add_node("B", "Added Node")
            diagram.add_edge("A", "B")

            # Re-render
            result2 = renderer.render(diagram, format="svg")
            assert result2 == "<svg>modified</svg>"

            assert mock_mermaid.call_count == 2

    def test_different_format_workflow(self):
        """Test rendering same diagram in different formats."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")
        diagram.add_node("B", "Node B")
        diagram.add_edge("A", "B")

        renderer = MermaidRenderer()

        formats_and_results = [
            ("svg", "<svg>svg content</svg>"),
            ("png", b"PNG binary data"),
            ("pdf", b"PDF binary data"),
        ]

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            for format_type, expected_result in formats_and_results:
                if format_type == "svg":  # Only SVG is currently supported
                    mock_obj = Mock()
                    mock_obj.__str__ = Mock(return_value=expected_result)
                    mock_mermaid.return_value = mock_obj

                    result = renderer.render(diagram, format=format_type)
                    assert result == expected_result
                else:
                    # Other formats should raise RenderingError (wrapping UnsupportedFormatError)
                    with pytest.raises(RenderingError):
                        renderer.render(diagram, format=format_type)

    def test_theme_variation_workflow(self):
        """Test rendering with different themes."""
        diagram = FlowchartDiagram()
        diagram.add_node("A", "Node A")

        renderer = MermaidRenderer()

        themes = ["default", "dark", "forest"]

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_objects = []
            for theme in themes:
                mock_obj = Mock()
                mock_obj.__str__ = Mock(return_value=f"<svg>{theme} theme</svg>")
                mock_objects.append(mock_obj)
            mock_mermaid.side_effect = mock_objects

            for i, theme in enumerate(themes):
                result = renderer.render(diagram, format="svg", theme=theme)
                assert result == f"<svg>{theme} theme</svg>"


class TestPerformanceWorkflows:
    """Test performance-related workflows."""

    def test_large_diagram_handling(self):
        """Test handling of large diagrams."""
        # Create a large flowchart
        diagram = FlowchartDiagram()

        # Add many nodes
        for i in range(50):
            diagram.add_node(f"node_{i}", f"Node {i}")
            if i > 0:
                diagram.add_edge(f"node_{i-1}", f"node_{i}")

        # Generate code
        mermaid_code = diagram.to_mermaid()
        assert len(mermaid_code) > 1000  # Should be substantial

        # Render
        renderer = MermaidRenderer()
        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>large diagram</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert result == "<svg>large diagram</svg>"

    def test_concurrent_rendering_simulation(self):
        """Test simulation of concurrent rendering."""
        diagrams = []
        for i in range(5):
            diagram = FlowchartDiagram()
            diagram.add_node(f"node_{i}", f"Node {i}")
            diagrams.append(diagram)

        renderer = MermaidRenderer()

        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_objects = []
            for i in range(5):
                mock_obj = Mock()
                mock_obj.__str__ = Mock(return_value=f"<svg>result {i}</svg>")
                mock_objects.append(mock_obj)
            mock_mermaid.side_effect = mock_objects

            # Simulate concurrent requests
            results = []
            for i, diagram in enumerate(diagrams):
                result = renderer.render(diagram, format="svg")
                results.append(result)

            assert len(results) == 5
            assert all(f"result {i}" in results[i] for i in range(5))


class TestRegressionWorkflows:
    """Test workflows for regression prevention."""

    def test_empty_diagram_handling(self):
        """Test handling of empty diagrams."""
        diagram = FlowchartDiagram()

        # Should not crash
        mermaid_code = diagram.to_mermaid()
        assert isinstance(mermaid_code, str)

    def test_special_characters_handling(self):
        """Test handling of special characters in diagrams."""
        diagram = FlowchartDiagram()
        diagram.add_node("special", "Node with \"quotes\" & symbols")

        mermaid_code = diagram.to_mermaid()
        assert "quotes" in mermaid_code

        renderer = MermaidRenderer()
        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>special chars</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert result == "<svg>special chars</svg>"

    def test_unicode_content_handling(self):
        """Test handling of Unicode content."""
        diagram = FlowchartDiagram()
        diagram.add_node("unicode", "Node with 中文 and émojis 🚀")

        mermaid_code = diagram.to_mermaid()
        assert "中文" in mermaid_code
        assert "🚀" in mermaid_code

        renderer = MermaidRenderer()
        with patch('mermaid_render.core.md.Mermaid') as mock_mermaid:
            mock_obj = Mock()
            mock_obj.__str__ = Mock(return_value="<svg>unicode content</svg>")
            mock_mermaid.return_value = mock_obj

            result = renderer.render(diagram, format="svg")
            assert result == "<svg>unicode content</svg>"
