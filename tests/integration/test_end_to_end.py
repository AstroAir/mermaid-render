"""
End-to-end integration tests for the Mermaid Render library.
"""

from unittest.mock import Mock, patch

import pytest

from mermaid_render import (
    FlowchartDiagram,
    MermaidRenderer,
    SequenceDiagram,
    export_to_file,
    quick_render,
)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    @patch("mermaid_render.renderers.svg_renderer.md.Mermaid")
    def test_flowchart_creation_and_rendering(self, mock_mermaid, temp_dir):
        """Test complete flowchart workflow."""
        # Mock the mermaid-py library
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>flowchart content</svg>")
        mock_instance.svg_response = Mock()
        mock_instance.svg_response.text = "<svg>flowchart content</svg>"
        mock_mermaid.return_value = mock_instance

        # Create flowchart
        flowchart = FlowchartDiagram(direction="TD", title="Test Process")
        flowchart.add_node("start", "Start", shape="circle")
        flowchart.add_node("process", "Process Data", shape="rectangle")
        flowchart.add_node("decision", "Valid?", shape="rhombus")
        flowchart.add_node("success", "Success", shape="circle")
        flowchart.add_node("error", "Error", shape="circle")

        # Add connections
        flowchart.add_edge("start", "process")
        flowchart.add_edge("process", "decision")
        flowchart.add_edge("decision", "success", label="Yes")
        flowchart.add_edge("decision", "error", label="No")

        # Render to SVG
        renderer = MermaidRenderer()
        svg_content = renderer.render(flowchart, format="svg")

        assert svg_content == '<svg xmlns="http://www.w3.org/2000/svg">flowchart content</svg>'

        # Save to file
        output_path = temp_dir / "flowchart.svg"
        renderer.save(flowchart, output_path)

        assert output_path.exists()
        assert output_path.read_text() == '<svg xmlns="http://www.w3.org/2000/svg">flowchart content</svg>'

    @patch("mermaid_render.renderers.svg_renderer.md.Mermaid")
    def test_sequence_diagram_workflow(self, mock_mermaid, temp_dir):
        """Test complete sequence diagram workflow."""
        # Mock the mermaid-py library
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>sequence content</svg>")
        mock_mermaid.return_value = mock_instance

        # Create sequence diagram
        sequence = SequenceDiagram(title="User Authentication", autonumber=True)
        sequence.add_participant("user", "User")
        sequence.add_participant("app", "Application")
        sequence.add_participant("auth", "Auth Service")
        sequence.add_participant("db", "Database")

        # Add interactions
        sequence.add_message("user", "app", "Login request", "sync")
        sequence.add_message("app", "auth", "Validate credentials", "async")
        sequence.add_message("auth", "db", "Check user", "sync")
        sequence.add_message("db", "auth", "User data", "return")
        sequence.add_message("auth", "app", "Auth token", "return")
        sequence.add_message("app", "user", "Login success", "return")

        # Add note
        sequence.add_note("Token expires in 1 hour", "auth", "right of")

        # Render and save
        renderer = MermaidRenderer(theme="dark")
        output_path = temp_dir / "sequence.svg"
        renderer.save(sequence, output_path)

        assert output_path.exists()

    @patch("mermaid_render.renderers.svg_renderer.md.Mermaid")
    def test_quick_render_function(self, mock_mermaid, temp_dir):
        """Test quick_render convenience function."""
        # Mock the mermaid-py library
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>quick render</svg>")
        mock_mermaid.return_value = mock_instance

        diagram_code = """
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]
    D --> E
"""

        # Test rendering without saving
        result = quick_render(diagram_code, format="svg", theme="forest")
        assert result == "<svg>quick render</svg>"

        # Test rendering with saving
        output_path = temp_dir / "quick.svg"
        result = quick_render(diagram_code, output_path=output_path, format="svg")

        assert output_path.exists()
        assert output_path.read_text() == "<svg>quick render</svg>"

    @patch("mermaid_render.renderers.svg_renderer.md.Mermaid")
    def test_export_to_file_function(self, mock_mermaid, temp_dir):
        """Test export_to_file convenience function."""
        # Mock the mermaid-py library
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>exported content</svg>")
        mock_mermaid.return_value = mock_instance

        # Create a simple diagram
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Node A")
        flowchart.add_node("B", "Node B")
        flowchart.add_edge("A", "B")

        # Export to file
        output_path = temp_dir / "exported.svg"
        export_to_file(flowchart, output_path, theme="neutral")

        assert output_path.exists()
        assert output_path.read_text() == "<svg>exported content</svg>"

    def test_diagram_validation_workflow(self):
        """Test diagram validation workflow."""
        from mermaid_render.utils import validate_mermaid_syntax

        # Valid diagram
        valid_code = """
flowchart TD
    A[Start] --> B[End]
"""

        result = validate_mermaid_syntax(valid_code)
        assert result.is_valid

        # Invalid diagram
        invalid_code = """
flowchart TD
    A[Start --> B[End
"""

        result = validate_mermaid_syntax(invalid_code)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_theme_management_workflow(self, temp_dir):
        """Test theme management workflow."""
        from mermaid_render.config import ThemeManager

        # Create theme manager
        theme_manager = ThemeManager(custom_themes_dir=temp_dir / "themes")

        # Get built-in themes
        built_in = theme_manager.get_built_in_themes()
        assert "default" in built_in
        assert "dark" in built_in

        # Create custom theme
        custom_theme = {
            "theme": "custom",
            "primaryColor": "#ff0000",
            "primaryTextColor": "#ffffff",
            "lineColor": "#000000",
        }

        theme_manager.add_custom_theme("my_theme", custom_theme)

        # Verify custom theme
        available = theme_manager.get_available_themes()
        assert "my_theme" in available

        retrieved = theme_manager.get_theme("my_theme")
        assert retrieved["primaryColor"] == "#ff0000"

    def test_configuration_workflow(self):
        """Test configuration management workflow."""
        from mermaid_render.config import ConfigManager

        # Create config manager
        config_manager = ConfigManager(load_env=False)

        # Test default values
        assert config_manager.get("timeout") == 30.0
        assert config_manager.get("default_theme") == "default"

        # Update configuration
        config_manager.update(
            {"timeout": 60.0, "default_theme": "dark", "custom_setting": "test_value"}
        )

        assert config_manager.get("timeout") == 60.0
        assert config_manager.get("default_theme") == "dark"
        assert config_manager.get("custom_setting") == "test_value"

        # Test validation
        config_manager.validate_config()  # Should not raise

    @patch("mermaid_render.renderers.svg_renderer.md.Mermaid")
    def test_multiple_format_export(self, mock_mermaid, temp_dir):
        """Test exporting to multiple formats."""
        from mermaid_render.utils import export_multiple_formats

        # Mock different format responses
        mock_instance = Mock()
        mock_instance.__str__ = Mock(return_value="<svg>content</svg>")
        mock_mermaid.return_value = mock_instance

        # Create diagram
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Start")
        flowchart.add_node("B", "End")
        flowchart.add_edge("A", "B")

        # Export to multiple formats
        base_path = temp_dir / "diagram"
        formats = ["svg"]  # Only test SVG for now since others need mocking

        paths = export_multiple_formats(flowchart, base_path, formats)

        assert "svg" in paths
        assert paths["svg"].exists()

    def test_error_handling_workflow(self):
        """Test error handling in various scenarios."""
        from mermaid_render.exceptions import DiagramError

        # Test diagram creation errors
        with pytest.raises(DiagramError):
            flowchart = FlowchartDiagram()
            flowchart.add_edge("A", "B")  # Nodes don't exist

        # Test validation errors
        from mermaid_render.utils import validate_mermaid_syntax

        result = validate_mermaid_syntax("invalid diagram code")
        assert not result.is_valid

        # Test theme errors
        from mermaid_render.config import ThemeManager
        from mermaid_render.exceptions import ThemeError

        theme_manager = ThemeManager()
        with pytest.raises(ThemeError):
            theme_manager.get_theme("nonexistent_theme")

    def test_utility_functions_workflow(self):
        """Test utility functions workflow."""
        from mermaid_render.utils import (
            detect_diagram_type,
            get_available_themes,
            get_supported_formats,
            sanitize_filename,
        )

        # Test format utilities
        formats = get_supported_formats()
        assert "svg" in formats
        assert "png" in formats

        # Test theme utilities
        themes = get_available_themes()
        assert "default" in themes
        assert "dark" in themes

        # Test diagram type detection
        flowchart_code = "flowchart TD\n    A --> B"
        assert detect_diagram_type(flowchart_code) == "flowchart"

        sequence_code = "sequenceDiagram\n    A->>B: Message"
        assert detect_diagram_type(sequence_code) == "sequenceDiagram"

        # Test filename sanitization
        unsafe_name = "My Diagram: Version 2.0"
        safe_name = sanitize_filename(unsafe_name)
        assert "/" not in safe_name
        assert ":" not in safe_name
