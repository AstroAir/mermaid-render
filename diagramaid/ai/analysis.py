"""AI-powered diagram analysis and quality assessment."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EnhancementType(Enum):
    """Types of diagram enhancement."""

    LAYOUT = "layout"
    STYLE = "style"
    CONTENT = "content"
    PERFORMANCE = "performance"


@dataclass
class EnhancementResult:
    """Result of diagram enhancement."""

    original_diagram: str
    enhanced_diagram: str
    enhancement_type: EnhancementType
    improvements: list[str]
    confidence_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_diagram": self.original_diagram,
            "enhanced_diagram": self.enhanced_diagram,
            "enhancement_type": self.enhancement_type.value,
            "improvements": self.improvements,
            "confidence_score": self.confidence_score,
        }


@dataclass
class ComplexityAnalysis:
    """Analysis of diagram complexity."""

    node_count: int
    connection_count: int
    depth_levels: int
    branching_factor: float
    complexity_score: float
    complexity_level: str  # simple, medium, complex

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "connection_count": self.connection_count,
            "depth_levels": self.depth_levels,
            "branching_factor": self.branching_factor,
            "complexity_score": self.complexity_score,
            "complexity_level": self.complexity_level,
        }


@dataclass
class QualityMetrics:
    """Quality metrics for diagram assessment."""

    readability_score: float
    consistency_score: float
    completeness_score: float
    accessibility_score: float
    overall_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "readability_score": self.readability_score,
            "consistency_score": self.consistency_score,
            "completeness_score": self.completeness_score,
            "accessibility_score": self.accessibility_score,
            "overall_score": self.overall_score,
        }


@dataclass
class AnalysisReport:
    """Comprehensive analysis report for a diagram."""

    diagram_code: str
    complexity: ComplexityAnalysis
    quality: QualityMetrics
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagram_code": self.diagram_code,
            "complexity": self.complexity.to_dict(),
            "quality": self.quality.to_dict(),
            "issues": self.issues,
            "recommendations": self.recommendations,
            "strengths": self.strengths,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


class DiagramAnalyzer:
    """AI-powered analyzer for diagram quality and complexity assessment."""

    def __init__(self) -> None:
        self.quality_rules = self._load_quality_rules()

    def analyze(
        self, diagram_code: str, context: dict[str, Any] | None = None
    ) -> AnalysisReport:
        """
        Perform comprehensive analysis of a diagram.

        Args:
            diagram_code: Mermaid diagram code
            context: Additional context about the diagram

        Returns:
            Comprehensive analysis report
        """
        # Analyze complexity
        complexity = self.analyze_complexity(diagram_code)

        # Assess quality
        quality = self.assess_quality(diagram_code)

        # Identify issues and recommendations
        issues = self._identify_issues(diagram_code, complexity, quality)
        recommendations = self._generate_recommendations(
            diagram_code, complexity, quality, issues
        )
        strengths = self._identify_strengths(diagram_code, complexity, quality)

        return AnalysisReport(
            diagram_code=diagram_code,
            complexity=complexity,
            quality=quality,
            issues=issues,
            recommendations=recommendations,
            strengths=strengths,
        )

    def analyze_complexity(self, diagram_code: str) -> ComplexityAnalysis:
        """Analyze diagram complexity."""
        # Count nodes and connections
        node_count = self._count_nodes(diagram_code)
        connection_count = self._count_connections(diagram_code)

        # Analyze structure
        depth_levels = self._calculate_depth(diagram_code)
        branching_factor = self._calculate_branching_factor(diagram_code, node_count)

        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(
            node_count, connection_count, depth_levels, branching_factor
        )

        # Determine complexity level
        if complexity_score < 0.3:
            complexity_level = "simple"
        elif complexity_score < 0.7:
            complexity_level = "medium"
        else:
            complexity_level = "complex"

        return ComplexityAnalysis(
            node_count=node_count,
            connection_count=connection_count,
            depth_levels=depth_levels,
            branching_factor=branching_factor,
            complexity_score=complexity_score,
            complexity_level=complexity_level,
        )

    def assess_quality(self, diagram_code: str) -> QualityMetrics:
        """Assess diagram quality across multiple dimensions."""
        readability_score = self._assess_readability(diagram_code)
        consistency_score = self._assess_consistency(diagram_code)
        completeness_score = self._assess_completeness(diagram_code)
        accessibility_score = self._assess_accessibility(diagram_code)

        # Calculate overall score
        overall_score = (
            readability_score * 0.3
            + consistency_score * 0.25
            + completeness_score * 0.25
            + accessibility_score * 0.2
        )

        return QualityMetrics(
            readability_score=readability_score,
            consistency_score=consistency_score,
            completeness_score=completeness_score,
            accessibility_score=accessibility_score,
            overall_score=overall_score,
        )

    def _count_nodes(self, diagram_code: str) -> int:
        """Count nodes in diagram."""
        # Count different node types
        node_patterns = [
            r"\w+\[.*?\]",  # Rectangle nodes
            r"\w+\(.*?\)",  # Rounded nodes
            r"\w+\{.*?\}",  # Diamond nodes
            r"\w+\(\(.*?\)\)",  # Circle nodes
        ]

        total_nodes = 0
        for pattern in node_patterns:
            matches = re.findall(pattern, diagram_code)
            total_nodes += len(matches)

        return total_nodes

    def _count_connections(self, diagram_code: str) -> int:
        """Count connections in diagram."""
        connection_patterns = [
            r"-->",  # Arrow
            r"---",  # Line
            r"-\.-",  # Dotted line
            r"==>",  # Thick arrow
        ]

        total_connections = 0
        for pattern in connection_patterns:
            total_connections += len(re.findall(pattern, diagram_code))

        return total_connections

    def _calculate_depth(self, diagram_code: str) -> int:
        """Calculate the depth levels of the diagram."""
        # Simple heuristic based on indentation
        lines = diagram_code.split("\n")
        max_depth = 0

        for line in lines:
            if line.strip():
                # Count leading spaces
                depth = (len(line) - len(line.lstrip())) // 4
                max_depth = max(max_depth, depth)

        return max(max_depth, 1)

    def _calculate_branching_factor(self, diagram_code: str, node_count: int) -> float:
        """Calculate average branching factor."""
        if node_count == 0:
            return 0.0

        connection_count = self._count_connections(diagram_code)
        return connection_count / node_count if node_count > 0 else 0.0

    def _calculate_complexity_score(
        self,
        node_count: int,
        connection_count: int,
        depth_levels: int,
        branching_factor: float,
    ) -> float:
        """Calculate overall complexity score."""
        # Normalize factors
        node_factor = min(node_count / 20, 1.0)  # Normalize to 20 nodes
        connection_factor = min(
            connection_count / 30, 1.0
        )  # Normalize to 30 connections
        depth_factor = min(depth_levels / 5, 1.0)  # Normalize to 5 levels
        branching_factor_norm = min(
            branching_factor / 3, 1.0
        )  # Normalize to 3 branches per node

        # Weighted combination
        complexity_score = (
            node_factor * 0.3
            + connection_factor * 0.3
            + depth_factor * 0.2
            + branching_factor_norm * 0.2
        )

        return complexity_score

    def _assess_readability(self, diagram_code: str) -> float:
        """Assess diagram readability."""
        score = 1.0

        # Check for proper spacing
        if not self._has_proper_spacing(diagram_code):
            score -= 0.2

        # Check for clear node labels
        if not self._has_clear_labels(diagram_code):
            score -= 0.3

        # Check for reasonable size
        node_count = self._count_nodes(diagram_code)
        if node_count > 20:
            score -= 0.2

        # Check for direction specification
        if not self._has_direction_specified(diagram_code):
            score -= 0.1

        return max(score, 0.0)

    def _assess_consistency(self, diagram_code: str) -> float:
        """Assess diagram consistency."""
        score = 1.0

        # Check for consistent node naming
        if not self._has_consistent_naming(diagram_code):
            score -= 0.3

        # Check for consistent styling
        if not self._has_consistent_styling(diagram_code):
            score -= 0.2

        # Check for consistent connection types
        if not self._has_consistent_connections(diagram_code):
            score -= 0.2

        return max(score, 0.0)

    def _assess_completeness(self, diagram_code: str) -> float:
        """Assess diagram completeness."""
        score = 1.0

        # Check for start/end nodes in flowcharts
        if "flowchart" in diagram_code and not self._has_start_end_nodes(diagram_code):
            score -= 0.3

        # Check for proper connections
        if not self._has_proper_connections(diagram_code):
            score -= 0.2

        # Check for meaningful content
        if not self._has_meaningful_content(diagram_code):
            score -= 0.3

        return max(score, 0.0)

    def _assess_accessibility(self, diagram_code: str) -> float:
        """Assess diagram accessibility."""
        score = 1.0

        # Check for color-only information
        if self._relies_on_color_only(diagram_code):
            score -= 0.3

        # Check for descriptive labels
        if not self._has_descriptive_labels(diagram_code):
            score -= 0.2

        # Check for reasonable contrast (if styling present)
        if self._has_poor_contrast(diagram_code):
            score -= 0.2

        return max(score, 0.0)

    def _identify_issues(
        self,
        diagram_code: str,
        complexity: ComplexityAnalysis,
        quality: QualityMetrics,
    ) -> list[str]:
        """Identify issues in the diagram."""
        issues = []

        if complexity.complexity_level == "complex":
            issues.append("Diagram is very complex and may be hard to understand")

        if quality.readability_score < 0.6:
            issues.append("Diagram readability could be improved")

        if quality.consistency_score < 0.7:
            issues.append("Diagram lacks consistency in styling or naming")

        if quality.accessibility_score < 0.7:
            issues.append("Diagram may have accessibility issues")

        if not self._has_proper_spacing(diagram_code):
            issues.append("Diagram lacks proper spacing between elements")

        return issues

    def _generate_recommendations(
        self,
        diagram_code: str,
        complexity: ComplexityAnalysis,
        quality: QualityMetrics,
        issues: list[str],
    ) -> list[str]:
        """Generate recommendations for improvement."""
        recommendations = []

        if complexity.complexity_level == "complex":
            recommendations.append(
                "Consider breaking the diagram into smaller, focused diagrams"
            )

        if quality.readability_score < 0.7:
            recommendations.append(
                "Add clear labels and improve spacing for better readability"
            )

        if "classDef" not in diagram_code:
            recommendations.append("Add styling to improve visual hierarchy")

        if not self._has_direction_specified(diagram_code):
            recommendations.append(
                "Specify diagram direction (TD, LR, etc.) for better layout"
            )

        if quality.accessibility_score < 0.7:
            recommendations.append(
                "Improve accessibility by using high contrast colors and descriptive labels"
            )

        return recommendations

    def _identify_strengths(
        self,
        diagram_code: str,
        complexity: ComplexityAnalysis,
        quality: QualityMetrics,
    ) -> list[str]:
        """Identify strengths of the diagram."""
        strengths = []

        if quality.overall_score > 0.8:
            strengths.append("High overall quality")

        if complexity.complexity_level == "simple" and complexity.node_count > 3:
            strengths.append("Good balance of simplicity and completeness")

        if "classDef" in diagram_code:
            strengths.append("Good use of styling for visual hierarchy")

        if self._has_clear_labels(diagram_code):
            strengths.append("Clear and descriptive labels")

        if quality.consistency_score > 0.8:
            strengths.append("Consistent styling and naming conventions")

        return strengths

    def enhance_layout(self, diagram_code: str) -> EnhancementResult:
        """
        Enhance diagram layout for better readability.

        Args:
            diagram_code: Mermaid diagram code to enhance

        Returns:
            EnhancementResult with layout improvements
        """
        improvements = []
        enhanced = diagram_code

        # Add proper spacing
        if not self._has_proper_spacing(diagram_code):
            enhanced = self._enhance_spacing(enhanced)
            improvements.append("Added proper spacing between elements")

        # Optimize node arrangement
        if self._needs_layout_enhancement(diagram_code):
            enhanced = self._enhance_node_layout(enhanced)
            improvements.append("Enhanced node arrangement")

        return EnhancementResult(
            original_diagram=diagram_code,
            enhanced_diagram=enhanced,
            enhancement_type=EnhancementType.LAYOUT,
            improvements=improvements,
            confidence_score=0.8,
        )

    def _enhance_spacing(self, code: str) -> str:
        """Add spacing to diagram for better readability."""
        lines = code.split("\n")
        spaced_lines = []

        for i, line in enumerate(lines):
            spaced_lines.append(line)
            if i == 0 or (line.strip() and not line.strip().startswith("%")):
                if i < len(lines) - 1 and lines[i + 1].strip():
                    spaced_lines.append("")

        return "\n".join(spaced_lines)

    def _needs_layout_enhancement(self, code: str) -> bool:
        """Check if layout needs enhancement."""
        return "TD" not in code and "LR" not in code

    def _enhance_node_layout(self, code: str) -> str:
        """Enhance node layout direction."""
        lines = code.split("\n")
        if lines and "flowchart" in lines[0] and "TD" not in lines[0]:
            lines[0] = lines[0].replace("flowchart", "flowchart TD")
        return "\n".join(lines)

    # Helper methods for quality assessment
    def _has_proper_spacing(self, code: str) -> bool:
        """Check if diagram has proper spacing."""
        return len([line for line in code.split("\n") if line.strip() == ""]) > 0

    def _has_clear_labels(self, code: str) -> bool:
        """Check if diagram has clear labels."""
        # Look for meaningful text in brackets
        labels = re.findall(r"\[(.*?)\]", code)
        return len(labels) > 0 and all(len(label.strip()) > 2 for label in labels)

    def _has_direction_specified(self, code: str) -> bool:
        """Check if flowchart direction is specified."""
        return any(direction in code for direction in ["TD", "LR", "BT", "RL"])

    def _has_consistent_naming(self, code: str) -> bool:
        """Check for consistent node naming."""
        # Simple check for consistent naming patterns
        node_ids = re.findall(r"(\w+)\[", code)
        if len(node_ids) < 2:
            return True

        # Check if naming follows a pattern
        return len({len(node_id) for node_id in node_ids}) <= 2

    def _has_consistent_styling(self, code: str) -> bool:
        """Check for consistent styling."""
        return "classDef" in code or code.count("fill:") <= 1

    def _has_consistent_connections(self, code: str) -> bool:
        """Check for consistent connection types."""
        connection_types = [code.count("-->"), code.count("---"), code.count("-.-")]
        return sum(1 for count in connection_types if count > 0) <= 2

    def _has_start_end_nodes(self, code: str) -> bool:
        """Check for start/end nodes in flowcharts."""
        return any(term in code.lower() for term in ["start", "end", "begin", "finish"])

    def _has_proper_connections(self, code: str) -> bool:
        """Check for proper connections."""
        node_count = self._count_nodes(code)
        connection_count = self._count_connections(code)
        return connection_count >= node_count - 1  # At least a connected graph

    def _has_meaningful_content(self, code: str) -> bool:
        """Check for meaningful content."""
        return self._count_nodes(code) >= 2 and self._count_connections(code) >= 1

    def _relies_on_color_only(self, code: str) -> bool:
        """Check if diagram relies on color only for information."""
        # Simple heuristic: if there are many colors but no labels
        color_count = code.count("fill:")
        label_count = code.count("|")
        return color_count > 3 and label_count == 0

    def _has_descriptive_labels(self, code: str) -> bool:
        """Check for descriptive labels."""
        labels = re.findall(r"\[(.*?)\]", code)
        return len(labels) > 0 and all(len(label.strip()) > 5 for label in labels)

    def _has_poor_contrast(self, code: str) -> bool:
        """Check for poor color contrast."""
        # Simple check for light colors on light backgrounds
        return "#fff" in code and "#f" in code

    def _load_quality_rules(self) -> list[dict[str, Any]]:
        """Load quality assessment rules."""
        return [
            {
                "name": "proper_spacing",
                "weight": 0.2,
                "check": self._has_proper_spacing,
            },
            {
                "name": "clear_labels",
                "weight": 0.3,
                "check": self._has_clear_labels,
            },
            {
                "name": "direction_specified",
                "weight": 0.1,
                "check": self._has_direction_specified,
            },
        ]
