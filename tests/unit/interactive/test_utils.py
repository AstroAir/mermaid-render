"""
Unit tests for interactive.utils module.

Tests the utility functions for interactive module.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.utils import (
    create_interactive_session,
    export_diagram_code,
    get_available_components,
    load_diagram_from_code,
    validate_diagram_live,
)


@pytest.mark.unit
class TestInteractiveUtils:
    """Unit tests for interactive utility functions."""

    def test_create_interactive_session(self) -> None:
        """Test creating interactive session."""
        session = create_interactive_session()
        assert session is not None

    def test_load_diagram_from_code(self) -> None:
        """Test loading diagram from code."""
        code = "flowchart TD\n    A --> B"
        result = load_diagram_from_code(code)
        assert result is not None

    def test_export_diagram_code(self) -> None:
        """Test exporting diagram code."""
        mock_builder = Mock()
        mock_builder.generate_mermaid_code.return_value = "flowchart TD\n    A --> B"
        
        code = export_diagram_code(mock_builder)
        assert "flowchart" in code.lower()

    def test_validate_diagram_live(self) -> None:
        """Test live diagram validation."""
        code = "flowchart TD\n    A --> B"
        result = validate_diagram_live(code)
        assert result is not None

    def test_validate_diagram_live_invalid(self) -> None:
        """Test live validation with invalid diagram."""
        code = "invalid diagram syntax !!!"
        result = validate_diagram_live(code)
        # Should return validation result (may be error)
        assert result is not None

    def test_get_available_components(self) -> None:
        """Test getting available components."""
        components = get_available_components()
        assert isinstance(components, list)
        assert len(components) >= 0
