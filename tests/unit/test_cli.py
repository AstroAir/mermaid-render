from typing import Any

"""
Comprehensive unit tests for CLI module.

This module tests all CLI functionality including argument parsing,
file I/O operations, stdin handling, validation mode, error scenarios,
and output formatting.
"""

import sys
from unittest.mock import Mock, patch

import pytest

from mermaid_render.cli import main
from mermaid_render.exceptions import RenderingError, ValidationError


class TestCLIArgumentParsing:
    """Test CLI argument parsing functionality."""

    def test_version_argument(self, capsys: Any) -> None:
        """Test --version argument displays version."""
        with patch.object(sys, "argv", ["mermaid-render", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "mermaid-render" in captured.out

    def test_help_argument(self, capsys: Any) -> None:
        """Test --help argument displays help."""
        with patch.object(sys, "argv", ["mermaid-render", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "Render Mermaid diagrams" in captured.out

    def test_required_input_argument(self, capsys: Any) -> None:
        """Test that input argument is required."""
        with patch.object(sys, "argv", ["mermaid-render"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2  # argparse error code

    def test_format_choices(self, capsys: Any) -> None:
        """Test format argument accepts valid choices."""
        valid_formats = ["svg", "png", "pdf"]

        for format_type in valid_formats:
            with patch.object(
                sys, "argv", ["mermaid-render", "test.mmd", "-f", format_type]
            ):
                with patch("mermaid_render.cli.Path.exists", return_value=True):
                    with patch(
                        "mermaid_render.cli.Path.read_text",
                        return_value="flowchart TD\n    A --> B",
                    ):
                        with patch(
                            "mermaid_render.cli.quick_render",
                            return_value="<svg></svg>",
                        ):
                            result = main()
                            # Should not exit with argument error
                            assert result in [
                                0,
                                1,
                            ]  # May fail on rendering but not on parsing

    def test_invalid_format_choice(self, capsys: Any) -> None:
        """Test invalid format choice raises error."""
        with patch.object(sys, "argv", ["mermaid-render", "test.mmd", "-f", "invalid"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2  # argparse error code


class TestCLIFileOperations:
    """Test CLI file I/O operations."""

    def test_file_input_success(self, temp_dir: Any) -> None:
        """Test successful file input reading."""
        # Create test file
        test_file = temp_dir / "test.mmd"
        test_content = "flowchart TD\n    A --> B"
        test_file.write_text(test_content)

        with patch.object(sys, "argv", ["mermaid-render", str(test_file)]):
            with patch(
                "mermaid_render.cli.quick_render", return_value="<svg></svg>"
            ) as mock_render:
                result = main()

                assert result == 0
                mock_render.assert_called_once()
                args, kwargs = mock_render.call_args
                assert args[0] == test_content

    def test_file_not_found(self, capsys: Any) -> None:
        """Test handling of non-existent input file."""
        with patch.object(sys, "argv", ["mermaid-render", "nonexistent.mmd"]):
            result = main()

            assert result == 1
            captured = capsys.readouterr()
            assert "not found" in captured.err

    def test_empty_file_content(self, temp_dir: Any, capsys: Any) -> None:
        """Test handling of empty file content."""
        # Create empty test file
        test_file = temp_dir / "empty.mmd"
        test_file.write_text("")

        with patch.object(sys, "argv", ["mermaid-render", str(test_file)]):
            result = main()

            assert result == 1
            captured = capsys.readouterr()
            assert "No diagram code provided" in captured.err

    def test_whitespace_only_file(self, temp_dir: Any, capsys: Any) -> None:
        """Test handling of file with only whitespace."""
        # Create whitespace-only test file
        test_file = temp_dir / "whitespace.mmd"
        test_file.write_text("   \n\t  \n  ")

        with patch.object(sys, "argv", ["mermaid-render", str(test_file)]):
            result = main()

            assert result == 1
            captured = capsys.readouterr()
            assert "No diagram code provided" in captured.err

    def test_output_file_creation(self, temp_dir: Any) -> None:
        """Test output file creation."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")
        output_file = temp_dir / "output.svg"

        with patch.object(
            sys, "argv", ["mermaid-render", str(test_file), "-o", str(output_file)]
        ):
            with patch(
                "mermaid_render.cli.quick_render", return_value="<svg></svg>"
            ) as mock_render:
                result = main()

                assert result == 0
                mock_render.assert_called_once()
                args, kwargs = mock_render.call_args
                assert kwargs.get("output_path") == str(output_file)


class TestCLIStdinHandling:
    """Test CLI stdin input handling."""

    def test_stdin_input_success(self, capsys: Any) -> None:
        """Test successful stdin input reading."""
        test_content = "flowchart TD\n    A --> B"

        with patch.object(sys, "argv", ["mermaid-render", "-"]):
            with patch("sys.stdin.read", return_value=test_content):
                with patch(
                    "mermaid_render.cli.quick_render", return_value="<svg></svg>"
                ) as mock_render:
                    result = main()

                    assert result == 0
                    mock_render.assert_called_once()
                    args, kwargs = mock_render.call_args
                    assert args[0] == test_content

    def test_stdin_empty_input(self, capsys: Any) -> None:
        """Test handling of empty stdin input."""
        with patch.object(sys, "argv", ["mermaid-render", "-"]):
            with patch("sys.stdin.read", return_value=""):
                result = main()

                assert result == 1
                captured = capsys.readouterr()
                assert "No diagram code provided" in captured.err

    def test_stdin_with_output_file(self, temp_dir: Any) -> None:
        """Test stdin input with output file."""
        test_content = "flowchart TD\n    A --> B"
        output_file = temp_dir / "output.svg"

        with patch.object(sys, "argv", ["mermaid-render", "-", "-o", str(output_file)]):
            with patch("sys.stdin.read", return_value=test_content):
                with patch(
                    "mermaid_render.cli.quick_render", return_value="<svg></svg>"
                ) as mock_render:
                    result = main()

                    assert result == 0
                    mock_render.assert_called_once()
                    args, kwargs = mock_render.call_args
                    assert kwargs.get("output_path") == str(output_file)


class TestCLIValidationMode:
    """Test CLI validation-only mode."""

    def test_validation_success(self, temp_dir: Any, capsys: Any) -> None:
        """Test successful validation mode."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")

        with patch.object(
            sys, "argv", ["mermaid-render", str(test_file), "--validate-only"]
        ):
            with patch("mermaid_render.utils.validate_mermaid_syntax") as mock_validate:
                mock_result = Mock()
                mock_result.is_valid = True
                mock_validate.return_value = mock_result

                result = main()

                assert result == 0
                captured = capsys.readouterr()
                assert "✅ Diagram is valid" in captured.out

    def test_validation_failure(self, temp_dir: Any, capsys: Any) -> None:
        """Test validation failure mode."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("invalid mermaid syntax")

        with patch.object(
            sys, "argv", ["mermaid-render", str(test_file), "--validate-only"]
        ):
            with patch("mermaid_render.utils.validate_mermaid_syntax") as mock_validate:
                mock_result = Mock()
                mock_result.is_valid = False
                mock_result.errors = ["Syntax error on line 1", "Invalid diagram type"]
                mock_validate.return_value = mock_result

                result = main()

                assert result == 1
                captured = capsys.readouterr()
                assert "❌ Validation failed" in captured.err
                assert "Syntax error on line 1" in captured.err
                assert "Invalid diagram type" in captured.err

    def test_validation_quiet_mode(self, temp_dir: Any, capsys: Any) -> None:
        """Test validation in quiet mode."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")

        with patch.object(
            sys,
            "argv",
            ["mermaid-render", str(test_file), "--validate-only", "--quiet"],
        ):
            with patch("mermaid_render.utils.validate_mermaid_syntax") as mock_validate:
                mock_result = Mock()
                mock_result.is_valid = True
                mock_validate.return_value = mock_result

                result = main()

                assert result == 0
                captured = capsys.readouterr()
                assert captured.out == ""  # No output in quiet mode


class TestCLIErrorScenarios:
    """Test CLI error handling scenarios."""

    def test_rendering_error(self, temp_dir: Any, capsys: Any) -> None:
        """Test handling of rendering errors."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")

        with patch.object(sys, "argv", ["mermaid-render", str(test_file)]):
            with patch(
                "mermaid_render.cli.quick_render",
                side_effect=RenderingError("Rendering failed"),
            ):
                result = main()

                assert result == 1
                captured = capsys.readouterr()
                assert "Rendering failed" in captured.err

    def test_validation_error(self, temp_dir: Any, capsys: Any) -> None:
        """Test handling of validation errors."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")

        with patch.object(sys, "argv", ["mermaid-render", str(test_file)]):
            with patch(
                "mermaid_render.cli.quick_render",
                side_effect=ValidationError("Invalid syntax"),
            ):
                result = main()

                assert result == 1
                captured = capsys.readouterr()
                assert "Invalid syntax" in captured.err

    def test_output_required_for_binary_formats(
        self, temp_dir: Any, capsys: Any
    ) -> None:
        """Test that output file is required for PNG/PDF formats."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")

        # Test PNG format without output
        with patch.object(sys, "argv", ["mermaid-render", str(test_file), "-f", "png"]):
            result = main()

            assert result == 1
            captured = capsys.readouterr()
            assert "Output file required for png format" in captured.err

        # Test PDF format without output
        with patch.object(sys, "argv", ["mermaid-render", str(test_file), "-f", "pdf"]):
            result = main()

            assert result == 1
            captured = capsys.readouterr()
            assert "Output file required for pdf format" in captured.err

    def test_unexpected_exception(self, temp_dir: Any, capsys: Any) -> None:
        """Test handling of unexpected exceptions."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")

        with patch.object(sys, "argv", ["mermaid-render", str(test_file)]):
            with patch(
                "mermaid_render.cli.quick_render",
                side_effect=Exception("Unexpected error"),
            ):
                result = main()

                assert result == 1
                captured = capsys.readouterr()
                assert "Unexpected error" in captured.err


class TestCLIOutputFormatting:
    """Test CLI output formatting."""

    def test_svg_stdout_output(self, temp_dir: Any, capsys: Any) -> None:
        """Test SVG output to stdout."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")
        svg_content = '<svg xmlns="http://www.w3.org/2000/svg">test</svg>'

        with patch.object(sys, "argv", ["mermaid-render", str(test_file)]):
            with patch("mermaid_render.cli.quick_render", return_value=svg_content):
                result = main()

                assert result == 0
                captured = capsys.readouterr()
                assert svg_content in captured.out

    def test_success_message_with_output_file(self, temp_dir: Any, capsys: Any) -> None:
        """Test success message when output file is specified."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")
        output_file = temp_dir / "output.svg"

        with patch.object(
            sys, "argv", ["mermaid-render", str(test_file), "-o", str(output_file)]
        ):
            with patch("mermaid_render.cli.quick_render", return_value="<svg></svg>"):
                result = main()

                assert result == 0
                captured = capsys.readouterr()
                assert f"✅ Diagram rendered to {output_file}" in captured.out

    def test_quiet_mode_suppresses_messages(self, temp_dir: Any, capsys: Any) -> None:
        """Test that quiet mode suppresses success messages."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")
        output_file = temp_dir / "output.svg"

        with patch.object(
            sys,
            "argv",
            ["mermaid-render", str(test_file), "-o", str(output_file), "--quiet"],
        ):
            with patch("mermaid_render.cli.quick_render", return_value="<svg></svg>"):
                result = main()

                assert result == 0
                captured = capsys.readouterr()
                assert captured.out == ""  # No output in quiet mode

    def test_theme_parameter_passed(self, temp_dir: Any) -> None:
        """Test that theme parameter is passed to renderer."""
        test_file = temp_dir / "test.mmd"
        test_file.write_text("flowchart TD\n    A --> B")

        with patch.object(
            sys, "argv", ["mermaid-render", str(test_file), "-t", "dark"]
        ):
            with patch(
                "mermaid_render.cli.quick_render", return_value="<svg></svg>"
            ) as mock_render:
                result = main()

                assert result == 0
                mock_render.assert_called_once()
                args, kwargs = mock_render.call_args
                assert kwargs.get("theme") == "dark"
