"""
AI-powered diagram generation from natural language and data sources.

This module provides the core diagram generation capabilities using
various AI models and techniques.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .nl_processor import NLProcessor, TextAnalysis
from .providers import AIProvider, OpenAIProvider


class DiagramType(Enum):
    """Supported diagram types for AI generation."""

    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    STATE = "state"
    ER = "er"
    JOURNEY = "journey"
    GANTT = "gantt"
    PIE = "pie"
    AUTO = "auto"  # Let AI decide


@dataclass
class GenerationConfig:
    """Configuration for diagram generation."""

    diagram_type: DiagramType = DiagramType.AUTO
    max_nodes: int = 20
    max_connections: int = 30
    style_preference: str = "clean"  # clean, detailed, minimal
    include_styling: bool = True
    include_comments: bool = False
    complexity_level: str = "medium"  # simple, medium, complex
    target_audience: str = "general"  # technical, business, general

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "diagram_type": self.diagram_type.value,
            "max_nodes": self.max_nodes,
            "max_connections": self.max_connections,
            "style_preference": self.style_preference,
            "include_styling": self.include_styling,
            "include_comments": self.include_comments,
            "complexity_level": self.complexity_level,
            "target_audience": self.target_audience,
        }


@dataclass
class GenerationResult:
    """Result of diagram generation."""

    diagram_code: str
    diagram_type: DiagramType
    confidence_score: float
    config: Optional[GenerationConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "diagram_code": self.diagram_code,
            "diagram_type": self.diagram_type.value,
            "confidence_score": self.confidence_score,
            "config": self.config.to_dict() if self.config else None,
            "metadata": self.metadata,
            "suggestions": self.suggestions,
            "generated_at": self.generated_at.isoformat(),
        }


class DiagramGenerator:
    """
    AI-powered diagram generator.

    Generates Mermaid diagrams from natural language descriptions,
    data sources, and other inputs using AI models.
    """

    def __init__(
        self,
        ai_provider: Optional[AIProvider] = None,
        nl_processor: Optional[NLProcessor] = None,
    ):
        """
        Initialize diagram generator.

        Args:
            ai_provider: AI provider for generation
            nl_processor: Natural language processor
        """
        self.ai_provider = ai_provider or OpenAIProvider()
        self.nl_processor = nl_processor or NLProcessor()

        # Generation templates and prompts
        self.templates = self._load_generation_templates()
        self.prompts = self._load_generation_prompts()

    def from_text(
        self,
        text: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate diagram from natural language text.

        Args:
            text: Natural language description
            config: Generation configuration

        Returns:
            Generation result with diagram code
        """
        if config is None:
            config = GenerationConfig()

        # Analyze the input text
        analysis = self.nl_processor.analyze_text(text)

        # Determine diagram type if auto
        if config.diagram_type == DiagramType.AUTO:
            config.diagram_type = self._determine_diagram_type(analysis)

        # Generate diagram using AI
        diagram_code = self._generate_with_ai(text, analysis, config)

        # Post-process and validate
        diagram_code = self._post_process_diagram(diagram_code, config)

        # Calculate confidence score
        confidence = self._calculate_confidence(diagram_code, analysis, config)

        # Generate suggestions
        suggestions = self._generate_suggestions(diagram_code, analysis, config)

        return GenerationResult(
            diagram_code=diagram_code,
            diagram_type=config.diagram_type,
            confidence_score=confidence,
            config=config,
            metadata={
                "input_analysis": analysis.to_dict(),
                "generation_config": config.to_dict(),
            },
            suggestions=suggestions,
        )

    def from_data(
        self,
        data: Dict[str, Any],
        data_type: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate diagram from structured data.

        Args:
            data: Structured data
            data_type: Type of data (json, csv, database, etc.)
            config: Generation configuration

        Returns:
            Generation result with diagram code
        """
        if config is None:
            config = GenerationConfig()

        # Convert data to natural language description
        description = self._data_to_description(data, data_type)

        # Generate diagram from description
        return self.from_text(description, config)

    def from_code(
        self,
        code: str,
        language: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate diagram from source code.

        Args:
            code: Source code
            language: Programming language
            config: Generation configuration

        Returns:
            Generation result with diagram code
        """
        if config is None:
            config = GenerationConfig()

        # Analyze code structure
        code_analysis = self._analyze_code_structure(code, language)

        # Convert to natural language description
        description = self._code_to_description(code_analysis, language)

        # Generate diagram
        return self.from_text(description, config)

    def improve_diagram(
        self,
        existing_diagram: str,
        improvement_request: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Improve an existing diagram based on feedback.

        Args:
            existing_diagram: Current diagram code
            improvement_request: Description of desired improvements
            config: Generation configuration

        Returns:
            Improved diagram result
        """
        if config is None:
            config = GenerationConfig()

        # Create improvement prompt
        prompt = self._create_improvement_prompt(
            existing_diagram, improvement_request, config
        )

        # Generate improved diagram (ai_provider returns GenerationResponse)
        ai_response = self.ai_provider.generate_text(prompt)

        # Ensure we work with a string body
        response_text = getattr(ai_response, "text", str(ai_response))

        # Extract code then post-process
        improved_code = self._extract_diagram_code(response_text)

        # Post-process
        improved_code = self._post_process_diagram(improved_code, config)

        # Calculate confidence
        confidence = self._calculate_improvement_confidence(
            existing_diagram, improved_code, improvement_request
        )

        return GenerationResult(
            diagram_code=improved_code,
            diagram_type=self._detect_diagram_type(improved_code),
            confidence_score=confidence,
            config=config,
            metadata={
                "original_diagram": existing_diagram,
                "improvement_request": improvement_request,
            },
        )

    def get_suggestions(
        self, diagram_code: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered suggestions for improving a diagram.

        Args:
            diagram_code: Mermaid diagram code
            context: Additional context about the diagram

        Returns:
            List of suggestions
        """
        from .suggestions import SuggestionEngine

        engine = SuggestionEngine()
        suggestions = engine.get_suggestions(diagram_code, context)

        return [suggestion.to_dict() for suggestion in suggestions]

    def _determine_diagram_type(self, analysis: TextAnalysis) -> DiagramType:
        """Determine the best diagram type for the given analysis."""
        # Simple heuristics based on keywords and intent
        keywords = analysis.keywords
        # intent = analysis.intent.intent if analysis.intent else ""  # TODO: Use intent in future

        # Process-related keywords suggest flowchart
        process_keywords = ["process", "flow", "step", "procedure", "workflow"]
        if any(keyword in keywords for keyword in process_keywords):
            return DiagramType.FLOWCHART

        # Interaction keywords suggest sequence diagram
        interaction_keywords = ["interaction", "communication", "message", "call"]
        if any(keyword in keywords for keyword in interaction_keywords):
            return DiagramType.SEQUENCE

        # Structure keywords suggest class diagram
        structure_keywords = ["class", "object", "inheritance", "relationship"]
        if any(keyword in keywords for keyword in structure_keywords):
            return DiagramType.CLASS

        # State keywords suggest state diagram
        state_keywords = ["state", "status", "condition", "transition"]
        if any(keyword in keywords for keyword in state_keywords):
            return DiagramType.STATE

        # Database keywords suggest ER diagram
        db_keywords = ["database", "table", "entity", "relation"]
        if any(keyword in keywords for keyword in db_keywords):
            return DiagramType.ER

        # Default to flowchart
        return DiagramType.FLOWCHART

    def _generate_with_ai(
        self,
        text: str,
        analysis: TextAnalysis,
        config: GenerationConfig,
    ) -> str:
        """Generate diagram using AI provider."""
        # Create generation prompt
        prompt = self._create_generation_prompt(text, analysis, config)

        # Generate with AI (ai_provider returns GenerationResponse)
        ai_response = self.ai_provider.generate_text(prompt)

        # Normalize to string
        response_text = getattr(ai_response, "text", str(ai_response))

        # Extract diagram code from response text
        diagram_code = self._extract_diagram_code(response_text)

        return diagram_code

    def _create_generation_prompt(
        self,
        text: str,
        analysis: TextAnalysis,
        config: GenerationConfig,
    ) -> str:
        """Create prompt for AI generation."""
        base_prompt = self.prompts.get(
            config.diagram_type.value, self.prompts["default"]
        )

        prompt = f"""
{base_prompt}

Input Description: {text}

Requirements:
- Diagram Type: {config.diagram_type.value}
- Maximum Nodes: {config.max_nodes}
- Maximum Connections: {config.max_connections}
- Style Preference: {config.style_preference}
- Complexity Level: {config.complexity_level}
- Target Audience: {config.target_audience}

Extracted Entities: {', '.join(analysis.entities.entities) if analysis.entities else 'None'}
Key Concepts: {', '.join(analysis.keywords)}

Please generate a valid Mermaid diagram that accurately represents the described process or system.
Include only the diagram code, no additional explanation.
"""

        return prompt.strip()

    def _post_process_diagram(self, diagram_code: str, config: GenerationConfig) -> str:
        """Post-process generated diagram code."""
        # Clean up the code
        diagram_code = self._clean_diagram_code(diagram_code)

        # Validate syntax
        if not self._validate_diagram_syntax(diagram_code):
            # Try to fix common issues
            diagram_code = self._fix_common_issues(diagram_code)

        # Apply styling if requested
        if config.include_styling:
            diagram_code = self._add_styling(diagram_code, config.style_preference)

        # Add comments if requested
        if config.include_comments:
            diagram_code = self._add_comments(diagram_code)

        return diagram_code

    def _clean_diagram_code(self, code: str) -> str:
        """Clean up generated diagram code."""
        # Remove markdown code blocks
        code = re.sub(r"```mermaid\n?", "", code)
        code = re.sub(r"```\n?", "", code)

        # Remove extra whitespace
        lines = [line.strip() for line in code.split("\n") if line.strip()]

        return "\n".join(lines)

    def _validate_diagram_syntax(self, code: str) -> bool:
        """Validate diagram syntax."""
        # Basic validation - check for diagram type declaration
        lines = code.split("\n")
        if not lines:
            return False

        first_line = lines[0].strip()
        valid_starts = [
            "flowchart",
            "graph",
            "sequenceDiagram",
            "classDiagram",
            "stateDiagram",
            "erDiagram",
            "journey",
            "gantt",
            "pie",
        ]

        return any(first_line.startswith(start) for start in valid_starts)

    def _fix_common_issues(self, code: str) -> str:
        """Fix common issues in generated code."""
        lines = code.split("\n")

        # Ensure first line is a valid diagram declaration
        if lines and not self._validate_diagram_syntax(code):
            # Prepend flowchart declaration
            lines.insert(0, "flowchart TD")

        return "\n".join(lines)

    def _add_styling(self, code: str, style_preference: str) -> str:
        """Add styling to diagram based on preference."""
        if style_preference == "clean":
            styling = """
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px
    classDef highlight fill:#e1f5fe,stroke:#01579b,stroke-width:2px
"""
        elif style_preference == "detailed":
            styling = """
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px,color:#000
    classDef process fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef terminal fill:#ffebee,stroke:#f44336,stroke-width:2px
"""
        else:  # minimal
            styling = ""

        if styling:
            code += "\n" + styling

        return code

    def _add_comments(self, code: str) -> str:
        """Add explanatory comments to diagram."""
        lines = code.split("\n")

        # Add header comment
        header_comment = "    %% Generated diagram - modify as needed"
        lines.insert(1, header_comment)

        return "\n".join(lines)

    def _calculate_confidence(
        self,
        diagram_code: str,
        analysis: TextAnalysis,
        config: GenerationConfig,
    ) -> float:
        """Calculate confidence score for generated diagram."""
        score = 0.8  # Base score

        # Adjust based on syntax validity
        if self._validate_diagram_syntax(diagram_code):
            score += 0.1
        else:
            score -= 0.2

        # Adjust based on entity coverage
        if analysis.entities and analysis.entities.entities:
            entity_count = len(analysis.entities.entities)
            node_count = self._count_nodes(diagram_code)

            if node_count >= entity_count * 0.7:  # Good entity coverage
                score += 0.1

        # Adjust based on complexity match
        actual_complexity = self._assess_diagram_complexity(diagram_code)
        if actual_complexity == config.complexity_level:
            score += 0.05

        return min(max(score, 0.0), 1.0)

    def _generate_suggestions(
        self,
        diagram_code: str,
        analysis: TextAnalysis,
        config: GenerationConfig,
    ) -> List[str]:
        """Generate suggestions for diagram improvement."""
        suggestions = []

        # Check node count
        node_count = self._count_nodes(diagram_code)
        if node_count < 3:
            suggestions.append(
                "Consider adding more detail to better represent the process"
            )
        elif node_count > config.max_nodes:
            suggestions.append(
                "Diagram might be too complex - consider breaking into smaller diagrams"
            )

        # Check for styling
        if not config.include_styling and "classDef" not in diagram_code:
            suggestions.append("Add styling to improve visual appeal")

        # Check for labels
        if "-->" in diagram_code and "|" not in diagram_code:
            suggestions.append("Consider adding labels to connections for clarity")

        return suggestions

    def _count_nodes(self, diagram_code: str) -> int:
        """Count nodes in diagram code."""
        # Simple heuristic - count lines with node definitions
        lines = diagram_code.split("\n")
        node_count = 0

        for line in lines:
            line = line.strip()
            if "[" in line and "]" in line:
                node_count += 1
            elif "(" in line and ")" in line:
                node_count += 1

        return node_count

    def _assess_diagram_complexity(self, diagram_code: str) -> str:
        """Assess the complexity level of a diagram."""
        node_count = self._count_nodes(diagram_code)
        connection_count = diagram_code.count("-->")

        if node_count <= 5 and connection_count <= 5:
            return "simple"
        elif node_count <= 15 and connection_count <= 20:
            return "medium"
        else:
            return "complex"

    def _extract_diagram_code(self, response: str) -> str:
        """Extract diagram code from AI response."""
        # Look for code blocks
        code_block_pattern = r"```(?:mermaid)?\n?(.*?)\n?```"
        match = re.search(code_block_pattern, response, re.DOTALL)

        if match:
            return match.group(1).strip()

        # If no code block, return the whole response
        return response.strip()

    def _detect_diagram_type(self, diagram_code: str) -> DiagramType:
        """Detect diagram type from code."""
        first_line = diagram_code.split("\n")[0].strip().lower()

        if first_line.startswith("flowchart") or first_line.startswith("graph"):
            return DiagramType.FLOWCHART
        elif first_line.startswith("sequencediagram"):
            return DiagramType.SEQUENCE
        elif first_line.startswith("classdiagram"):
            return DiagramType.CLASS
        elif first_line.startswith("statediagram"):
            return DiagramType.STATE
        elif first_line.startswith("erdiagram"):
            return DiagramType.ER
        elif first_line.startswith("journey"):
            return DiagramType.JOURNEY
        elif first_line.startswith("gantt"):
            return DiagramType.GANTT
        elif first_line.startswith("pie"):
            return DiagramType.PIE
        else:
            return DiagramType.FLOWCHART

    def _load_generation_templates(self) -> Dict[str, str]:
        """Load generation templates."""
        return {
            "flowchart": "Generate a flowchart diagram",
            "sequence": "Generate a sequence diagram",
            "class": "Generate a class diagram",
            "default": "Generate an appropriate diagram",
        }

    def _load_generation_prompts(self) -> Dict[str, str]:
        """Load generation prompts."""
        return {
            "flowchart": """
You are an expert at creating Mermaid flowchart diagrams. Create a clear, well-structured flowchart that represents the described process or system.

Use appropriate node shapes:
- Rectangles [text] for processes
- Diamonds {text} for decisions
- Circles ((text)) for start/end points
- Rounded rectangles (text) for sub-processes

Connect nodes with arrows and include descriptive labels where helpful.
""",
            "sequence": """
You are an expert at creating Mermaid sequence diagrams. Create a clear sequence diagram showing the interactions between participants.

Use proper sequence diagram syntax:
- participant A as Actor
- A->>B: Message
- B-->>A: Response
- Note over A: Comment

Show the flow of messages and interactions clearly.
""",
            "default": """
You are an expert at creating Mermaid diagrams. Analyze the input and create the most appropriate type of diagram to represent the described system, process, or concept.

Choose the best diagram type and create clear, well-structured output.
""",
        }

    def _data_to_description(self, data: Dict[str, Any], data_type: str) -> str:
        """Convert structured data to natural language description."""
        # Simplified implementation
        return f"Create a diagram representing the {data_type} data structure with the following elements: {list(data.keys())}"

    def _analyze_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code structure."""
        # Simplified implementation
        return {
            "language": language,
            "functions": [],
            "classes": [],
            "imports": [],
        }

    def _code_to_description(self, analysis: Dict[str, Any], language: str) -> str:
        """Convert code analysis to description."""
        # Simplified implementation
        return f"Create a diagram showing the structure of this {language} code"

    def _create_improvement_prompt(
        self,
        existing_diagram: str,
        improvement_request: str,
        config: GenerationConfig,
    ) -> str:
        """Create prompt for diagram improvement."""
        return f"""
Improve the following Mermaid diagram based on the improvement request:

Current Diagram:
{existing_diagram}

Improvement Request: {improvement_request}

Please provide an improved version of the diagram that addresses the request while maintaining the core structure and functionality.
"""

    def _calculate_improvement_confidence(
        self,
        original: str,
        improved: str,
        request: str,
    ) -> float:
        """Calculate confidence for improvement."""
        # Simplified implementation
        return 0.8
