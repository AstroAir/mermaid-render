"""
Unit tests for mcp.prompts.documentation module.

Tests for diagram documentation prompts.
"""

import pytest

from diagramaid.mcp.prompts.documentation import (
    create_diagram_documentation_prompt,
    explain_diagram_prompt,
)


@pytest.mark.unit
class TestExplainDiagramPrompt:
    """Tests for explain_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = explain_diagram_prompt("flowchart TD\n    A --> B")
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A --> B"
        result = explain_diagram_prompt(code)
        assert "A --> B" in result

    def test_beginner_audience(self):
        """Test beginner audience level."""
        result = explain_diagram_prompt(
            "flowchart TD\n    A --> B", audience_level="beginner"
        )
        assert "beginner" in result.lower() or "simple" in result.lower()

    def test_intermediate_audience(self):
        """Test intermediate audience level."""
        result = explain_diagram_prompt(
            "flowchart TD\n    A --> B", audience_level="intermediate"
        )
        assert isinstance(result, str)

    def test_expert_audience(self):
        """Test expert audience level."""
        result = explain_diagram_prompt(
            "flowchart TD\n    A --> B", audience_level="expert"
        )
        assert isinstance(result, str)

    def test_general_audience(self):
        """Test general audience level."""
        result = explain_diagram_prompt(
            "flowchart TD\n    A --> B", audience_level="general"
        )
        assert isinstance(result, str)

    def test_requests_overview(self):
        """Test prompt requests overview."""
        result = explain_diagram_prompt("flowchart TD\n    A --> B")
        assert "overview" in result.lower()

    def test_requests_key_components(self):
        """Test prompt requests key components."""
        result = explain_diagram_prompt("flowchart TD\n    A --> B")
        assert "component" in result.lower() or "element" in result.lower()


@pytest.mark.unit
class TestCreateDiagramDocumentationPrompt:
    """Tests for create_diagram_documentation_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = create_diagram_documentation_prompt(
            "flowchart TD\n    A --> B", "My Diagram"
        )
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A --> B"
        result = create_diagram_documentation_prompt(code, "Title")
        assert "A --> B" in result

    def test_includes_title(self):
        """Test prompt includes title."""
        title = "My Flowchart Diagram"
        result = create_diagram_documentation_prompt(
            "flowchart TD\n    A --> B", title
        )
        assert title in result

    def test_with_context(self):
        """Test with context provided."""
        context = "This diagram shows the login process"
        result = create_diagram_documentation_prompt(
            "flowchart TD\n    A --> B", "Title", context=context
        )
        assert context in result

    def test_requests_executive_summary(self):
        """Test prompt requests executive summary."""
        result = create_diagram_documentation_prompt(
            "flowchart TD\n    A --> B", "Title"
        )
        assert "summary" in result.lower() or "overview" in result.lower()

    def test_requests_glossary(self):
        """Test prompt requests glossary."""
        result = create_diagram_documentation_prompt(
            "flowchart TD\n    A --> B", "Title"
        )
        assert "glossary" in result.lower() or "definition" in result.lower()

    def test_requests_use_cases(self):
        """Test prompt requests use cases."""
        result = create_diagram_documentation_prompt(
            "flowchart TD\n    A --> B", "Title"
        )
        assert "use case" in result.lower() or "when" in result.lower()
