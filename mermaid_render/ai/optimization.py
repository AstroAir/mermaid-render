"""AI-powered diagram optimization."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class OptimizationType(Enum):
    """Types of optimization."""

    LAYOUT = "layout"
    STYLE = "style"
    CONTENT = "content"
    PERFORMANCE = "performance"


@dataclass
class OptimizationResult:
    """Result of diagram optimization."""

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
    """Optimizes diagram layout for better readability."""

    def optimize(self, diagram_code: str) -> OptimizationResult:
        """Optimize diagram layout."""
        improvements = []
        optimized = diagram_code

        # Add proper spacing
        if not self._has_proper_spacing(diagram_code):
            optimized = self._add_spacing(optimized)
            improvements.append("Added proper spacing between elements")

        # Optimize node arrangement
        if self._needs_layout_optimization(diagram_code):
            optimized = self._optimize_node_layout(optimized)
            improvements.append("Optimized node arrangement")

        return OptimizationResult(
            original_diagram=diagram_code,
            optimized_diagram=optimized,
            optimization_type=OptimizationType.LAYOUT,
            improvements=improvements,
            confidence_score=0.8,
        )

    def _has_proper_spacing(self, code: str) -> bool:
        """Check if diagram has proper spacing."""
        lines = code.split("\n")
        return len([line for line in lines if line.strip() == ""]) > 0

    def _add_spacing(self, code: str) -> str:
        """Add spacing to diagram."""
        lines = code.split("\n")
        spaced_lines = []

        for i, line in enumerate(lines):
            spaced_lines.append(line)
            if i == 0 or (line.strip() and not line.strip().startswith("%")):
                if i < len(lines) - 1 and lines[i + 1].strip():
                    spaced_lines.append("")

        return "\n".join(spaced_lines)

    def _needs_layout_optimization(self, code: str) -> bool:
        """Check if layout needs optimization."""
        return "TD" not in code and "LR" not in code

    def _optimize_node_layout(self, code: str) -> str:
        """Optimize node layout direction."""
        lines = code.split("\n")
        if lines and "flowchart" in lines[0] and "TD" not in lines[0]:
            lines[0] = lines[0].replace("flowchart", "flowchart TD")
        return "\n".join(lines)


class StyleOptimizer:
    """Optimizes diagram styling for better appearance."""

    def optimize(self, diagram_code: str) -> OptimizationResult:
        """Optimize diagram styling."""
        improvements = []
        optimized = diagram_code

        # Add basic styling if missing
        if "classDef" not in diagram_code:
            optimized = self._add_basic_styling(optimized)
            improvements.append("Added basic styling")

        # Improve color scheme
        if self._needs_color_optimization(diagram_code):
            optimized = self._optimize_colors(optimized)
            improvements.append("Optimized color scheme")

        return OptimizationResult(
            original_diagram=diagram_code,
            optimized_diagram=optimized,
            optimization_type=OptimizationType.STYLE,
            improvements=improvements,
            confidence_score=0.7,
        )

    def _add_basic_styling(self, code: str) -> str:
        """Add basic styling to diagram."""
        styling = """
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px
    classDef highlight fill:#e1f5fe,stroke:#01579b,stroke-width:2px"""

        return code + styling

    def _needs_color_optimization(self, code: str) -> bool:
        """Check if colors need optimization."""
        return "fill:" in code and "#ff0000" in code  # Avoid harsh red

    def _optimize_colors(self, code: str) -> str:
        """Optimize color scheme."""
        # Replace harsh colors with softer alternatives
        optimized = code.replace("#ff0000", "#f44336")  # Softer red
        optimized = optimized.replace("#00ff00", "#4caf50")  # Softer green
        return optimized


class DiagramOptimizer:
    """Main diagram optimizer combining multiple optimization strategies."""

    def __init__(self):
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
        suggestions = []

        # Check for common issues
        if len(diagram_code.split("\n")) > 50:
            suggestions.append(
                "Consider breaking large diagram into smaller components"
            )

        if diagram_code.count("-->") > 20:
            suggestions.append("Diagram has many connections - consider simplifying")

        if "classDef" not in diagram_code:
            suggestions.append("Add styling to improve visual appeal")

        if not any(direction in diagram_code for direction in ["TD", "LR", "BT", "RL"]):
            suggestions.append("Specify diagram direction for better layout")

        return suggestions
