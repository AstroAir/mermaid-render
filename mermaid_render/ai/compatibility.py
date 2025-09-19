"""
Compatibility layer for backward compatibility with optimization.py classes.

This module provides wrapper classes that maintain the exact same API as the
original optimization classes while delegating to the new integrated functionality.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from .analysis import DiagramAnalyzer, EnhancementResult, EnhancementType
from .suggestions import SuggestionEngine


# Alias for backward compatibility
OptimizationType = EnhancementType


@dataclass
class OptimizationResult:
    """Result of diagram optimization - maintains original API."""

    original_diagram: str
    optimized_diagram: str
    optimization_type: OptimizationType
    improvements: List[str]
    confidence_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_diagram": self.original_diagram,
            "optimized_diagram": self.optimized_diagram,
            "optimization_type": self.optimization_type.value,
            "improvements": self.improvements,
            "confidence_score": self.confidence_score,
        }


class LayoutOptimizer:
    """
    Compatibility wrapper for layout optimization functionality.
    
    This class maintains the exact same API as the original LayoutOptimizer
    while delegating to the integrated DiagramAnalyzer functionality.
    """

    def __init__(self) -> None:
        """Initialize layout optimizer."""
        self._analyzer = DiagramAnalyzer()

    def optimize(self, diagram_code: str) -> OptimizationResult:
        """
        Optimize diagram layout.
        
        Args:
            diagram_code: Mermaid diagram code
            
        Returns:
            OptimizationResult with layout improvements
        """
        # Delegate to the integrated functionality
        result = self._analyzer.enhance_layout(diagram_code)
        
        # Convert EnhancementResult to OptimizationResult for compatibility
        return OptimizationResult(
            original_diagram=result.original_diagram,
            optimized_diagram=result.enhanced_diagram,
            optimization_type=OptimizationType.LAYOUT,
            improvements=result.improvements,
            confidence_score=result.confidence_score,
        )

    def _has_proper_spacing(self, code: str) -> bool:
        """Check if diagram has proper spacing."""
        return self._analyzer._has_proper_spacing(code)

    def _add_spacing(self, code: str) -> str:
        """Add spacing to diagram."""
        return self._analyzer._enhance_spacing(code)

    def _needs_layout_optimization(self, code: str) -> bool:
        """Check if layout needs optimization."""
        return self._analyzer._needs_layout_enhancement(code)

    def _optimize_node_layout(self, code: str) -> str:
        """Optimize node layout direction."""
        return self._analyzer._enhance_node_layout(code)


class StyleOptimizer:
    """
    Compatibility wrapper for style optimization functionality.
    
    This class maintains the exact same API as the original StyleOptimizer
    while delegating to the integrated SuggestionEngine functionality.
    """

    def __init__(self) -> None:
        """Initialize style optimizer."""
        self._engine = SuggestionEngine()

    def optimize(self, diagram_code: str) -> OptimizationResult:
        """
        Optimize diagram styling.
        
        Args:
            diagram_code: Mermaid diagram code
            
        Returns:
            OptimizationResult with style improvements
        """
        # Delegate to the integrated functionality
        result = self._engine.enhance_style(diagram_code)
        
        # Convert EnhancementResult to OptimizationResult for compatibility
        return OptimizationResult(
            original_diagram=result.original_diagram,
            optimized_diagram=result.enhanced_diagram,
            optimization_type=OptimizationType.STYLE,
            improvements=result.improvements,
            confidence_score=result.confidence_score,
        )

    def _add_basic_styling(self, code: str) -> str:
        """Add basic styling to diagram."""
        return self._engine._apply_basic_styling(code)

    def _needs_color_optimization(self, code: str) -> bool:
        """Check if colors need optimization."""
        return self._engine._needs_color_enhancement(code)

    def _optimize_colors(self, code: str) -> str:
        """Optimize color scheme."""
        return self._engine._enhance_colors(code)


class DiagramOptimizer:
    """
    Compatibility wrapper for main diagram optimization functionality.
    
    This class maintains the exact same API as the original DiagramOptimizer
    while delegating to the integrated functionality across multiple modules.
    """

    def __init__(self) -> None:
        """Initialize diagram optimizer."""
        self.layout_optimizer = LayoutOptimizer()
        self.style_optimizer = StyleOptimizer()

    def optimize_layout(self, diagram_code: str) -> OptimizationResult:
        """Optimize diagram layout."""
        return self.layout_optimizer.optimize(diagram_code)

    def optimize_style(self, diagram_code: str) -> OptimizationResult:
        """Optimize diagram styling."""
        return self.style_optimizer.optimize(diagram_code)

    def optimize_all(self, diagram_code: str) -> List[OptimizationResult]:
        """Apply all optimizations."""
        results = []

        # Apply layout optimization
        layout_result = self.optimize_layout(diagram_code)
        results.append(layout_result)

        # Apply style optimization to layout-optimized diagram
        style_result = self.optimize_style(layout_result.optimized_diagram)
        results.append(style_result)

        return results

    def get_optimization_suggestions(self, diagram_code: str) -> List[str]:
        """Get suggestions for diagram optimization."""
        from .utils import get_enhancement_suggestions
        return get_enhancement_suggestions(diagram_code)
