"""AI-powered suggestion system for diagram improvements."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SuggestionType(Enum):
    """Types of suggestions."""

    CONTENT = "content"
    STYLE = "style"
    LAYOUT = "layout"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"


class SuggestionPriority(Enum):
    """Priority levels for suggestions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Suggestion:
    """Represents a suggestion for diagram improvement."""

    suggestion_id: str
    suggestion_type: SuggestionType
    priority: SuggestionPriority
    title: str
    description: str
    rationale: str
    implementation: str
    example: Optional[str] = None
    confidence: float = 0.8
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suggestion_id": self.suggestion_id,
            "suggestion_type": self.suggestion_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "implementation": self.implementation,
            "example": self.example,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


class SuggestionEngine:
    """AI-powered suggestion engine for diagram improvements."""

    def __init__(self):
        self.suggestion_rules = self._load_suggestion_rules()
        self.suggestion_counter = 0

    def get_suggestions(
        self, diagram_code: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Suggestion]:
        """
        Get suggestions for improving a diagram.

        Args:
            diagram_code: Mermaid diagram code
            context: Additional context about the diagram

        Returns:
            List of suggestions
        """
        suggestions = []

        # Analyze diagram
        analysis = self._analyze_diagram(diagram_code)

        # Apply suggestion rules
        for rule in self.suggestion_rules:
            if rule["condition"](diagram_code, analysis, context):
                suggestion = self._create_suggestion(rule, diagram_code, analysis)
                suggestions.append(suggestion)

        # Sort by priority and confidence
        suggestions.sort(key=lambda s: (s.priority.value, -s.confidence), reverse=True)

        return suggestions

    def get_suggestions_by_type(
        self,
        diagram_code: str,
        suggestion_type: SuggestionType,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Suggestion]:
        """Get suggestions of a specific type."""
        all_suggestions = self.get_suggestions(diagram_code, context)
        return [s for s in all_suggestions if s.suggestion_type == suggestion_type]

    def get_high_priority_suggestions(
        self,
        diagram_code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Suggestion]:
        """Get high priority suggestions only."""
        all_suggestions = self.get_suggestions(diagram_code, context)
        return [
            s
            for s in all_suggestions
            if s.priority in [SuggestionPriority.HIGH, SuggestionPriority.CRITICAL]
        ]

    def _analyze_diagram(self, diagram_code: str) -> Dict[str, Any]:
        """Analyze diagram for suggestion generation."""
        lines = diagram_code.split("\n")

        analysis = {
            "line_count": len(lines),
            "node_count": self._count_nodes(diagram_code),
            "connection_count": diagram_code.count("-->") + diagram_code.count("---"),
            "has_styling": "classDef" in diagram_code,
            "has_comments": "%" in diagram_code,
            "diagram_type": self._detect_diagram_type(diagram_code),
            "has_direction": any(d in diagram_code for d in ["TD", "LR", "BT", "RL"]),
            "has_labels": "|" in diagram_code,
            "complexity": self._assess_complexity(diagram_code),
        }

        return analysis

    def _create_suggestion(
        self, rule: Dict[str, Any], diagram_code: str, analysis: Dict[str, Any]
    ) -> Suggestion:
        """Create a suggestion from a rule."""
        self.suggestion_counter += 1

        return Suggestion(
            suggestion_id=f"sug_{self.suggestion_counter:04d}",
            suggestion_type=rule["type"],
            priority=rule["priority"],
            title=rule["title"],
            description=rule["description"],
            rationale=rule["rationale"],
            implementation=rule["implementation"],
            example=rule.get("example"),
            confidence=rule.get("confidence", 0.8),
        )

    def _count_nodes(self, diagram_code: str) -> int:
        """Count nodes in diagram."""
        node_patterns = ["[", "(", "{", "((", "{{"]
        count = 0
        for pattern in node_patterns:
            count += diagram_code.count(pattern)
        return count

    def _detect_diagram_type(self, diagram_code: str) -> str:
        """Detect diagram type."""
        first_line = diagram_code.split("\n")[0].strip().lower()

        if first_line.startswith("flowchart") or first_line.startswith("graph"):
            return "flowchart"
        elif first_line.startswith("sequencediagram"):
            return "sequence"
        elif first_line.startswith("classdiagram"):
            return "class"
        else:
            return "unknown"

    def _assess_complexity(self, diagram_code: str) -> str:
        """Assess diagram complexity."""
        node_count = self._count_nodes(diagram_code)
        connection_count = diagram_code.count("-->") + diagram_code.count("---")

        if node_count <= 5 and connection_count <= 5:
            return "simple"
        elif node_count <= 15 and connection_count <= 20:
            return "medium"
        else:
            return "complex"

    def _load_suggestion_rules(self) -> List[Dict[str, Any]]:
        """Load suggestion rules."""
        return [
            {
                "type": SuggestionType.STYLE,
                "priority": SuggestionPriority.MEDIUM,
                "title": "Add Styling",
                "description": "Your diagram would benefit from visual styling to improve readability.",
                "rationale": "Styling helps distinguish different types of elements and improves visual hierarchy.",
                "implementation": "Add classDef statements to define colors and styles for different node types.",
                "example": "classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px",
                "condition": lambda code, analysis, context: not analysis[
                    "has_styling"
                ],
            },
            {
                "type": SuggestionType.LAYOUT,
                "priority": SuggestionPriority.HIGH,
                "title": "Specify Direction",
                "description": "Specify a direction for your flowchart to improve layout.",
                "rationale": "Explicit direction helps with consistent layout and better readability.",
                "implementation": "Add direction (TD, LR, BT, or RL) to your flowchart declaration.",
                "example": "flowchart TD",
                "condition": lambda code, analysis, context: (
                    analysis["diagram_type"] == "flowchart"
                    and not analysis["has_direction"]
                ),
            },
            {
                "type": SuggestionType.CONTENT,
                "priority": SuggestionPriority.MEDIUM,
                "title": "Add Connection Labels",
                "description": "Consider adding labels to connections for better clarity.",
                "rationale": "Connection labels help explain the relationship between elements.",
                "implementation": "Add labels using the |label| syntax on connections.",
                "example": "A -->|yes| B",
                "condition": lambda code, analysis, context: (
                    analysis["connection_count"] > 3 and not analysis["has_labels"]
                ),
            },
            {
                "type": SuggestionType.BEST_PRACTICE,
                "priority": SuggestionPriority.LOW,
                "title": "Add Comments",
                "description": "Consider adding comments to document your diagram.",
                "rationale": "Comments help explain the purpose and context of the diagram.",
                "implementation": "Add comments using %% syntax.",
                "example": "%% This diagram shows the user login process",
                "condition": lambda code, analysis, context: not analysis[
                    "has_comments"
                ],
            },
            {
                "type": SuggestionType.PERFORMANCE,
                "priority": SuggestionPriority.HIGH,
                "title": "Simplify Complex Diagram",
                "description": "Your diagram is quite complex and might be hard to read.",
                "rationale": "Complex diagrams can be overwhelming and hard to understand.",
                "implementation": "Consider breaking the diagram into smaller, focused diagrams.",
                "condition": lambda code, analysis, context: analysis["complexity"]
                == "complex",
            },
            {
                "type": SuggestionType.ACCESSIBILITY,
                "priority": SuggestionPriority.MEDIUM,
                "title": "Improve Color Contrast",
                "description": "Ensure sufficient color contrast for accessibility.",
                "rationale": "Good contrast helps users with visual impairments read the diagram.",
                "implementation": "Use high contrast colors and avoid relying solely on color to convey information.",
                "condition": lambda code, analysis, context: (
                    analysis["has_styling"] and "#ff" in code.lower()
                ),
            },
            {
                "type": SuggestionType.LAYOUT,
                "priority": SuggestionPriority.LOW,
                "title": "Organize Node Layout",
                "description": "Consider organizing nodes in a more logical layout.",
                "rationale": "Well-organized layouts improve comprehension and visual flow.",
                "implementation": "Group related nodes together and use consistent spacing.",
                "condition": lambda code, analysis, context: analysis["node_count"]
                > 10,
            },
        ]
