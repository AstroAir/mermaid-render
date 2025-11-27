"""
Unit tests for mcp.prompts.analysis module.

Tests for diagram analysis prompts.
"""

import pytest

from mermaid_render.mcp.prompts.analysis import (
    analyze_diagram_quality_prompt,
    suggest_improvements_prompt,
)


@pytest.mark.unit
class TestAnalyzeDiagramQualityPrompt:
    """Tests for analyze_diagram_quality_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = analyze_diagram_quality_prompt(
            "flowchart TD\n    A --> B", "flowchart"
        )
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A --> B"
        result = analyze_diagram_quality_prompt(code, "flowchart")
        assert "A --> B" in result

    def test_includes_diagram_type(self):
        """Test prompt includes diagram type."""
        result = analyze_diagram_quality_prompt(
            "flowchart TD\n    A --> B", "flowchart"
        )
        assert "flowchart" in result.lower()

    def test_includes_quality_criteria(self):
        """Test prompt includes quality criteria."""
        result = analyze_diagram_quality_prompt(
            "flowchart TD\n    A --> B", "flowchart"
        )
        assert "quality" in result.lower() or "best practices" in result.lower()

    def test_includes_structure_section(self):
        """Test prompt includes structure section."""
        result = analyze_diagram_quality_prompt(
            "flowchart TD\n    A --> B", "flowchart"
        )
        assert "structure" in result.lower() or "syntax" in result.lower()

    def test_includes_clarity_section(self):
        """Test prompt includes clarity section."""
        result = analyze_diagram_quality_prompt(
            "flowchart TD\n    A --> B", "flowchart"
        )
        assert "clarity" in result.lower() or "readability" in result.lower()


@pytest.mark.unit
class TestSuggestImprovementsPrompt:
    """Tests for suggest_improvements_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = suggest_improvements_prompt(
            "flowchart TD\n    A --> B", ["Unclear labels"]
        )
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A --> B"
        result = suggest_improvements_prompt(code, ["Issue 1"])
        assert "A --> B" in result

    def test_includes_issues(self):
        """Test prompt includes issues."""
        issues = ["Unclear labels", "Missing connections"]
        result = suggest_improvements_prompt("flowchart TD\n    A --> B", issues)
        for issue in issues:
            assert issue in result

    def test_requests_improvements(self):
        """Test prompt requests improvements."""
        result = suggest_improvements_prompt(
            "flowchart TD\n    A --> B", ["Issue"]
        )
        assert "improvement" in result.lower() or "suggest" in result.lower()

    def test_requests_enhanced_version(self):
        """Test prompt requests enhanced version."""
        result = suggest_improvements_prompt(
            "flowchart TD\n    A --> B", ["Issue"]
        )
        assert "enhanced" in result.lower() or "improved" in result.lower()
