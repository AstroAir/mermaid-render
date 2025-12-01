"""
Unit tests for interactive.builder.codegen.base module.

Tests the CodeGenerator base class.
"""

import pytest

from diagramaid.interactive.builder.codegen.base import CodeGenerator
from diagramaid.interactive.models import DiagramElement, ElementType, Position, Size


@pytest.mark.unit
class TestCodeGenerator:
    """Unit tests for CodeGenerator base class."""

    def test_is_abstract(self) -> None:
        """Test that CodeGenerator is abstract."""
        with pytest.raises(TypeError):
            CodeGenerator()

    def test_subclass_must_implement_generate(self) -> None:
        """Test that subclasses must implement generate method."""

        class IncompleteGenerator(CodeGenerator):
            pass

        with pytest.raises(TypeError):
            IncompleteGenerator()

    def test_subclass_with_generate(self) -> None:
        """Test that subclass with generate method can be instantiated."""

        class ConcreteGenerator(CodeGenerator):
            def generate(self, elements, connections):
                return "graph TD"

        generator = ConcreteGenerator()
        assert generator is not None

    def test_generate_returns_string(self) -> None:
        """Test that generate returns a string."""

        class ConcreteGenerator(CodeGenerator):
            def generate(self, elements, connections):
                return "flowchart LR\n    A --> B"

        generator = ConcreteGenerator()
        result = generator.generate([], [])
        assert isinstance(result, str)
