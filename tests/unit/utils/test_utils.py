from typing import Any

"""
Unit tests for utility functions.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from diagramaid.exceptions import UnsupportedFormatError
from diagramaid.models import FlowchartDiagram
from diagramaid.utils import (
    detect_diagram_type,
    ensure_directory,
    export_multiple_formats,
    export_to_file,
    get_available_themes,
    get_supported_formats,
    sanitize_filename,
    validate_mermaid_syntax,
)
from diagramaid.utils.export import (
    _detect_format_from_extension,
    _sanitize_filename,
    batch_export,
)
from diagramaid.utils.helpers import _estimate_complexity, get_diagram_stats
from diagramaid.utils.validation import (
    get_validation_errors,
    get_validation_warnings,
    quick_validate,
    suggest_fixes,
    validate_node_id,
)


class TestExportUtils:
    """Test export utility functions."""

    def test_export_to_file_with_diagram_object(self, temp_dir: Any) -> None:
        """Test exporting diagram object to file."""
        flowchart = FlowchartDiagram()
        flowchart.add_node("A", "Start")
        flowchart.add_node("B", "End")
        flowchart.add_edge("A", "B")

        output_path = temp_dir / "test.svg"

        with patch(
            "diagramaid.utils.export.MermaidRenderer"
        ) as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            export_to_file(flowchart, output_path)

            mock_renderer_class.assert_called_once()
            mock_renderer.save.assert_called_once()

    def test_export_to_file_with_string(self, temp_dir: Any) -> None:
        """Test exporting string diagram to file."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"

        with patch(
            "diagramaid.utils.export.MermaidRenderer"
        ) as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            export_to_file(diagram_code, output_path)

            mock_renderer.save.assert_called_once_with(diagram_code, output_path, "svg")

    def test_export_to_file_with_theme(self, temp_dir: Any) -> None:
        """Test exporting with theme."""
        diagram_code = "flowchart TD\n    A --> B"
        output_path = temp_dir / "test.svg"

        with patch(
            "diagramaid.utils.export.MermaidRenderer"
        ) as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            export_to_file(diagram_code, output_path, theme="dark")

            mock_renderer.set_theme.assert_called_once_with("dark")

    def test_export_to_file_format_detection(self, temp_dir: Any) -> None:
        """Test automatic format detection from file extension."""
        diagram_code = "flowchart TD\n    A --> B"

        test_cases = [
            ("test.svg", "svg"),
            ("test.png", "png"),
            ("test.pdf", "pdf"),
        ]

        for filename, expected_format in test_cases:
            output_path = temp_dir / filename

            with patch(
                "diagramaid.utils.export.MermaidRenderer"
            ) as mock_renderer_class:
                mock_renderer = Mock()
                mock_renderer_class.return_value = mock_renderer

                export_to_file(diagram_code, output_path)

                mock_renderer.save.assert_called_with(
                    diagram_code, output_path, expected_format
                )

    def test_export_multiple_formats(self, temp_dir: Any) -> None:
        """Test exporting to multiple formats."""
        diagram_code = "flowchart TD\n    A --> B"
        base_path = temp_dir / "diagram"
        formats = ["svg"]  # Only test svg to avoid rendering issues

        with (
            patch("diagramaid.core.MermaidConfig") as mock_config_class,
            patch("diagramaid.core.MermaidRenderer") as mock_renderer_class,
        ):
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            result = export_multiple_formats(diagram_code, base_path, formats)

            assert len(result) == 1
            assert "svg" in result
            assert result["svg"] == base_path.with_suffix(".svg")
            mock_renderer.save.assert_called_once()

    def test_export_multiple_formats_with_theme(self, temp_dir: Any) -> None:
        """Test exporting multiple formats with theme."""
        diagram_code = "flowchart TD\n    A --> B"
        base_path = temp_dir / "diagram"
        formats = ["svg"]  # Only test svg

        with (
            patch("diagramaid.core.MermaidConfig") as mock_config_class,
            patch("diagramaid.core.MermaidRenderer") as mock_renderer_class,
        ):
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            export_multiple_formats(diagram_code, base_path, formats, theme="dark")

            # Check that set_theme was called
            mock_renderer.set_theme.assert_called_once_with("dark")

    def test_batch_export(self, temp_dir: Any) -> None:
        """Test batch export of multiple diagrams."""
        diagrams: dict[str, str | Any] = {
            "flowchart": "flowchart TD\n    A --> B",
            "sequence": "sequenceDiagram\n    A->>B: Hello",
        }

        with (
            patch("diagramaid.core.MermaidConfig") as mock_config_class,
            patch("diagramaid.core.MermaidRenderer") as mock_renderer_class,
        ):
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            result = batch_export(diagrams, temp_dir, format="svg")

            assert len(result) == 2
            assert "flowchart" in result
            assert "sequence" in result
            assert mock_renderer.save.call_count == 2
            assert temp_dir.exists()

    def test_detect_format_from_extension(self) -> None:
        """Test format detection from file extension."""
        test_cases = [
            ("test.svg", "svg"),
            ("test.png", "png"),
            ("test.pdf", "pdf"),
            ("test.jpg", "png"),  # jpg maps to png
            ("test.jpeg", "png"),  # jpeg maps to png
        ]

        for filename, expected in test_cases:
            path = Path(filename)
            result = _detect_format_from_extension(path)
            assert result == expected

    def test_detect_format_from_extension_no_extension(self) -> None:
        """Test format detection with no extension."""

        path = Path("test")
        with pytest.raises(UnsupportedFormatError, match="No file extension provided"):
            _detect_format_from_extension(path)

    def test_sanitize_filename_export(self) -> None:
        """Test filename sanitization in export module."""
        test_cases = [
            ("normal_name", "normal_name"),
            (
                "name with spaces",
                "name with spaces",
            ),  # export version doesn't replace spaces
            ("name/with\\invalid:chars", "name_with_invalid_chars"),
            ("", "diagram"),  # Empty name
        ]

        for input_name, expected in test_cases:
            result = _sanitize_filename(input_name)
            assert result == expected


class TestHelperUtils:
    """Test helper utility functions."""

    def test_get_supported_formats(self) -> None:
        """Test getting supported formats."""
        formats = get_supported_formats()

        assert isinstance(formats, list)
        assert "svg" in formats
        assert len(formats) > 0

    def test_get_available_themes(self) -> None:
        """Test getting available themes."""
        themes = get_available_themes()

        assert isinstance(themes, list)
        assert "default" in themes
        assert "dark" in themes
        assert len(themes) >= 5  # At least the built-in themes

    def test_detect_diagram_type_flowchart(self) -> None:
        """Test detecting flowchart diagram type."""
        test_cases = [
            ("flowchart TD\n    A --> B", "flowchart"),
            ("flowchart LR\n    A --> B", "flowchart"),
            ("flowchart TB\n    A --> B", "flowchart"),
        ]

        for code, expected in test_cases:
            result = detect_diagram_type(code)
            assert result == expected

    def test_detect_diagram_type_sequence(self) -> None:
        """Test detecting sequence diagram type."""
        code = "sequenceDiagram\n    A->>B: Hello"
        result = detect_diagram_type(code)
        assert result == "sequenceDiagram"

    def test_detect_diagram_type_class(self) -> None:
        """Test detecting class diagram type."""
        code = "classDiagram\n    class Animal"
        result = detect_diagram_type(code)
        assert result == "classDiagram"

    def test_detect_diagram_type_unknown(self) -> None:
        """Test detecting unknown diagram type."""
        code = "unknown diagram type\n    some content"
        result = detect_diagram_type(code)
        assert result is None

    def test_detect_diagram_type_empty(self) -> None:
        """Test detecting diagram type with empty input."""
        result = detect_diagram_type("")
        assert result is None

        result = detect_diagram_type("   ")
        assert result is None

    def test_sanitize_filename(self) -> None:
        """Test filename sanitization."""
        test_cases = [
            ("normal_filename", "normal_filename"),
            ("file with spaces", "file_with_spaces"),
            ("file/with\\invalid:chars", "file_with_invalid_chars"),
            ('file<>:"/\\|?*name', "file_________name"),  # Each invalid char becomes _
            ("", "diagram"),  # Empty filename
            ("a" * 150, "a" * 100),  # Long filename truncation
            ("...leading_dots", "leading_dots"),
            ("trailing_dots...", "trailing_dots"),
        ]

        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected

    def test_ensure_directory(self, temp_dir: Any) -> None:
        """Test directory creation."""
        test_dir = temp_dir / "nested" / "directory"

        ensure_directory(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_ensure_directory_existing(self, temp_dir: Any) -> None:
        """Test ensuring existing directory."""
        # Should not raise error for existing directory
        ensure_directory(temp_dir)
        assert temp_dir.exists()

    def test_get_diagram_stats(self) -> None:
        """Test getting diagram statistics."""
        diagram_code = """flowchart TD
            A[Start] --> B[Process]
            B --> C[End]
            title: My Diagram
        """

        stats = get_diagram_stats(diagram_code)

        assert "line_count" in stats
        assert "non_empty_lines" in stats
        assert "character_count" in stats
        assert "diagram_type" in stats
        assert "has_title" in stats
        assert "estimated_complexity" in stats

        assert stats["diagram_type"] == "flowchart"
        assert stats["has_title"] is True
        assert stats["line_count"] > 0
        assert stats["character_count"] > 0

    def test_estimate_complexity(self) -> None:
        """Test complexity estimation."""
        # Low complexity
        simple_code = "flowchart TD\n    A --> B"
        assert _estimate_complexity(simple_code) == "low"

        # Medium complexity - need more connections (6-15 connections)
        medium_code = "\n".join(
            [
                "flowchart TD",
                "    A --> B",
                "    B --> C",
                "    C --> D",
                "    D --> E",
                "    E --> F",
                "    F --> G",
                "    G --> H",
            ]
        )
        assert _estimate_complexity(medium_code) == "medium"

        # High complexity (many lines and connections)
        high_code = "\n".join([f"    Node{i} --> Node{i+1}" for i in range(30)])
        assert _estimate_complexity(high_code) == "high"


class TestValidationUtils:
    """Test validation utility functions."""

    def test_validate_mermaid_syntax_valid(self) -> None:
        """Test validating valid Mermaid syntax."""
        valid_code = "flowchart TD\n    A[Start] --> B[End]"

        with patch(
            "diagramaid.utils.validation._shared_validator"
        ) as mock_validator:
            mock_result = Mock()
            mock_result.is_valid = True
            mock_result.errors = []
            mock_validator.validate.return_value = mock_result

            result = validate_mermaid_syntax(valid_code)

            assert result.is_valid is True
            mock_validator.validate.assert_called_once_with(valid_code)

    def test_validate_mermaid_syntax_invalid(self) -> None:
        """Test validating invalid Mermaid syntax."""
        invalid_code = "invalid mermaid code"

        with patch(
            "diagramaid.utils.validation.MermaidValidator"
        ) as mock_validator_class:
            mock_validator = Mock()
            mock_result = Mock()
            mock_result.is_valid = False
            mock_result.errors = ["Invalid syntax"]
            mock_validator.validate.return_value = mock_result
            mock_validator_class.return_value = mock_validator

            result = validate_mermaid_syntax(invalid_code)

            assert result.is_valid is False
            assert len(result.errors) > 0

    def test_quick_validate_true(self) -> None:
        """Test quick validation returning True."""
        valid_code = "flowchart TD\n    A --> B"

        with patch(
            "diagramaid.utils.validation._shared_validator"
        ) as mock_validator:
            mock_result = Mock()
            mock_result.is_valid = True
            mock_validator.validate.return_value = mock_result

            result = quick_validate(valid_code)

            assert result is True
            mock_validator.validate.assert_called_once_with(valid_code)

    def test_quick_validate_false(self) -> None:
        """Test quick validation returning False."""
        invalid_code = "invalid code"

        with patch(
            "diagramaid.utils.validation.validate_mermaid_syntax"
        ) as mock_validate:
            mock_result = Mock()
            mock_result.is_valid = False
            mock_validate.return_value = mock_result

            result = quick_validate(invalid_code)

            assert result is False

    def test_get_validation_errors(self) -> None:
        """Test getting validation errors."""
        invalid_code = "invalid code"

        # Test with actual implementation - invalid code should produce errors
        result = get_validation_errors(invalid_code)

        # Should have at least one error for invalid code
        assert len(result) > 0
        assert isinstance(result, list)
        assert all(isinstance(error, str) for error in result)

    def test_get_validation_warnings(self) -> None:
        """Test getting validation warnings."""
        code_with_warnings = "flowchart TD\n    A --> B"

        # Test with actual implementation - valid code should produce no warnings
        result = get_validation_warnings(code_with_warnings)

        # Should return a list (may be empty for valid code)
        assert isinstance(result, list)
        assert all(isinstance(warning, str) for warning in result)

    def test_suggest_fixes(self) -> None:
        """Test getting fix suggestions."""
        broken_code = "broken diagram"

        # Test with actual implementation - invalid code should produce suggestions
        result = suggest_fixes(broken_code)

        # Should return a list of suggestions
        assert isinstance(result, list)
        assert len(result) > 0  # Should have at least one suggestion for invalid code
        assert all(isinstance(suggestion, str) for suggestion in result)

    def test_validate_node_id_valid(self) -> None:
        """Test validating valid node ID."""
        valid_id = "validNodeId123"

        with patch(
            "diagramaid.utils.validation._shared_validator"
        ) as mock_validator:
            mock_validator.validate_node_id.return_value = True

            result = validate_node_id(valid_id)

            assert result is True
            mock_validator.validate_node_id.assert_called_once_with(valid_id)

    def test_validate_node_id_invalid(self) -> None:
        """Test validating invalid node ID."""
        invalid_id = "invalid-node-id!"

        with patch(
            "diagramaid.utils.validation.MermaidValidator"
        ) as mock_validator_class:
            mock_validator = Mock()
            mock_validator.validate_node_id.return_value = False
            mock_validator_class.return_value = mock_validator

            result = validate_node_id(invalid_id)

            assert result is False


class TestUtilsIntegration:
    """Test integration between utility functions."""

    def test_export_with_validation(self, temp_dir: Any) -> None:
        """Test exporting with validation check."""
        # Valid diagram
        valid_diagram = "flowchart TD\n    A[Start] --> B[End]"
        output_path = temp_dir / "valid.svg"

        with patch(
            "diagramaid.utils.validation.MermaidValidator"
        ) as mock_validator_class:
            mock_validator = Mock()
            mock_result = Mock()
            mock_result.is_valid = True
            mock_validator.validate.return_value = mock_result
            mock_validator_class.return_value = mock_validator

            # Validate first
            is_valid = quick_validate(valid_diagram)
            assert is_valid is True

            # Then export
            with patch(
                "diagramaid.utils.export.MermaidRenderer"
            ) as mock_renderer_class:
                mock_renderer = Mock()
                mock_renderer_class.return_value = mock_renderer

                export_to_file(valid_diagram, output_path)
                mock_renderer.save.assert_called_once()

    def test_detect_type_and_export(self, temp_dir: Any) -> None:
        """Test detecting diagram type and exporting."""
        diagram_code = "sequenceDiagram\n    A->>B: Hello"
        output_path = temp_dir / "sequence.svg"

        # Detect type
        diagram_type = detect_diagram_type(diagram_code)
        assert diagram_type == "sequenceDiagram"

        # Export with detected type info
        with patch(
            "diagramaid.utils.export.MermaidRenderer"
        ) as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            export_to_file(diagram_code, output_path)
            mock_renderer.save.assert_called_once()

    def test_sanitize_and_export(self, temp_dir: Any) -> None:
        """Test sanitizing filename and exporting."""
        diagram_code = "flowchart TD\n    A --> B"
        unsafe_name = "My Diagram: Version 2.0"

        # Sanitize filename
        safe_name = sanitize_filename(unsafe_name)
        assert (
            safe_name == "My_Diagram__Version_2.0"
        )  # Colon becomes underscore, spaces become underscores

        # Export with safe filename
        output_path = temp_dir / f"{safe_name}.svg"

        with patch(
            "diagramaid.utils.export.MermaidRenderer"
        ) as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            export_to_file(diagram_code, output_path)
            mock_renderer.save.assert_called_once()

    def test_stats_and_complexity_analysis(self) -> None:
        """Test getting stats and analyzing complexity."""
        complex_diagram = """flowchart TD
            title: Complex Process Flow
            A[Start] --> B{Decision}
            B -->|Yes| C[Process 1]
            B -->|No| D[Process 2]
            C --> E[Merge]
            D --> E
            E --> F[Another Decision]
            F -->|Option 1| G[Path 1]
            F -->|Option 2| H[Path 2]
            F -->|Option 3| I[Path 3]
            G --> J[End]
            H --> J
            I --> J
        """

        # Get stats
        stats = get_diagram_stats(complex_diagram)

        assert stats["diagram_type"] == "flowchart"
        assert stats["has_title"] is True
        assert stats["estimated_complexity"] in ["medium", "high"]
        assert stats["line_count"] > 10
        assert stats["non_empty_lines"] > 5
