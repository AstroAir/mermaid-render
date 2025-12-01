#!/usr/bin/env python3
"""
AI-powered features showcase for Mermaid Render.

This script demonstrates the AI capabilities including natural language
diagram generation, code analysis, optimization, and intelligent suggestions.
"""

from pathlib import Path
from typing import Any, TypedDict

from diagramaid import (
    FlowchartDiagram,
    MermaidRenderer,
    SequenceDiagram,
)

# AI features (optional imports with fallbacks)
AI_AVAILABLE = False


# Minimal type shims to satisfy static analysis about returned attributes
class GenerationSuggestion(TypedDict, total=False):
    description: str


class GenerationResult(TypedDict, total=False):
    confidence_score: float
    diagram_code: str
    suggestions: list[GenerationSuggestion]
    metadata: dict[str, Any]


class OptimizationItem(TypedDict, total=False):
    description: str


class OptimizationResult(TypedDict, total=False):
    optimized_code: str
    improvements: list[OptimizationItem]


class ScoreInfo(TypedDict, total=False):
    overall_score: float
    readability: float
    maintainability: float


class RecommendationItem(TypedDict, total=False):
    description: str
    priority: Any  # could be Enum


class AnalysisResult(TypedDict, total=False):
    complexity_analysis: ScoreInfo
    quality_metrics: ScoreInfo
    recommendations: list[RecommendationItem]


# Optional AI symbols
DiagramAnalyzer: Any | None = None
DiagramGenerator: Any | None = None
DiagramOptimizer: Any | None = None
NLProcessor: Any | None = None
SuggestionEngine: Any | None = None
analyze_diagram: Any | None = None
generate_from_text: Any | None = None
get_suggestions: Any | None = None
optimize_diagram: Any | None = None

try:
    from diagramaid.ai import (
        DiagramAnalyzer as _DiagramAnalyzer,
    )
    from diagramaid.ai import (
        DiagramGenerator as _DiagramGenerator,
    )
    from diagramaid.ai import (
        DiagramOptimizer as _DiagramOptimizer,
    )
    from diagramaid.ai import (
        NLProcessor as _NLProcessor,
    )
    from diagramaid.ai import (
        SuggestionEngine as _SuggestionEngine,
    )
    from diagramaid.ai import (
        analyze_diagram as _analyze_diagram,
    )
    from diagramaid.ai import (
        generate_from_text as _generate_from_text,
    )
    from diagramaid.ai import (
        get_suggestions as _get_suggestions,
    )
    from diagramaid.ai import (
        optimize_diagram as _optimize_diagram,
    )

    DiagramAnalyzer = _DiagramAnalyzer
    DiagramGenerator = _DiagramGenerator
    DiagramOptimizer = _DiagramOptimizer
    NLProcessor = _NLProcessor
    SuggestionEngine = _SuggestionEngine
    analyze_diagram = _analyze_diagram
    generate_from_text = _generate_from_text
    get_suggestions = _get_suggestions
    optimize_diagram = _optimize_diagram

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  AI features not available. Install with: pip install diagramaid[ai]")


def create_output_dir() -> Path:
    """Create output directory for examples."""
    output_dir = Path("output/ai_features")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _save_mermaid_code(
    renderer: MermaidRenderer, mermaid_code: str, path: Path
) -> None:
    """
    Helper to save raw Mermaid code when renderer has no save_raw().
    Use MermaidRenderer.save on a minimal diagram wrapper if needed.
    """
    # Try renderer.save_raw if available
    save_raw = getattr(renderer, "save_raw", None)
    if callable(save_raw):
        save_raw(mermaid_code, path)
        return

    # Fallback: create a generic diagram wrapper if renderer supports rendering code strings
    # Some MermaidRenderer implementations accept raw code via a dedicated method.
    render_method = getattr(renderer, "render_to_file", None)
    if callable(render_method):
        render_method(mermaid_code, path)
        return

    # Last resort: attempt to wrap as Flowchart if it starts with flowchart or graph, else as Sequence
    code = mermaid_code.strip()
    if code.startswith("sequenceDiagram"):
        # Wrap in SequenceDiagram raw setter if available
        seq = SequenceDiagram(title="Generated")
        # Assuming SequenceDiagram has a way to set raw content is not guaranteed;
        # in absence, write via renderer if it accepts code
        if callable(render_method):
            render_method(code, path)
        else:
            # If no viable method, raise a clear error
            raise RuntimeError(
                "Renderer cannot save raw Mermaid code on this platform."
            )
    else:
        # Attempt Flowchart save as a diagram if renderer can only save diagram objects
        # This still won't help without parsing; thus rely on render_to_file above.
        if callable(render_method):
            render_method(code, path)
        else:
            raise RuntimeError(
                "Renderer cannot save raw Mermaid code on this platform."
            )


def natural_language_generation_example(output_dir: Path) -> None:
    """Demonstrate generating diagrams from natural language descriptions."""
    if not AI_AVAILABLE:
        print("Skipping natural language generation (AI not available)")
        return

    print("Natural language diagram generation example...")

    # Example descriptions for different diagram types
    descriptions = [
        "Create a flowchart showing the user registration process with email verification",
        "Generate a sequence diagram for a REST API authentication flow with JWT tokens",
        "Make a state diagram for an order processing system with pending, confirmed, shipped, and delivered states",
        "Design a class diagram for a simple blog system with users, posts, and comments",
    ]

    for i, description in enumerate(descriptions):
        try:
            print(f"Generating diagram from: '{description}'")

            # Generate diagram from natural language
            assert generate_from_text is not None
            result: GenerationResult = generate_from_text(description)

            confidence = float(result.get("confidence_score", 0.0))
            if confidence > 0.7:
                # Save the generated diagram
                output_path = output_dir / f"ai_generated_{i + 1}.svg"

                # Render the generated Mermaid code
                renderer = MermaidRenderer()
                code = str(result.get("diagram_code", "")).strip()
                if not code:
                    raise ValueError("No diagram code returned by generator.")
                _save_mermaid_code(renderer, code, output_path)

                print(f"  ✅ Generated with {confidence:.2f} confidence")
                print(f"  📁 Saved to {output_path}")

                # Show suggestions if available
                suggestions = result.get("suggestions") or []
                if suggestions:
                    print(f"  💡 Suggestions: {len(suggestions)} available")
                    for suggestion in suggestions[:2]:  # Show first 2
                        desc = suggestion.get("description", "")
                        print(f"     - {desc}")
            else:
                print(f"  ⚠️  Low confidence ({confidence:.2f}), skipping")

        except Exception as e:
            print(f"  ❌ Error generating diagram: {e}")

        print()


def code_analysis_generation_example(output_dir: Path) -> None:
    """Demonstrate generating diagrams from source code analysis."""
    if not AI_AVAILABLE:
        print("Skipping code analysis generation (AI not available)")
        return

    print("Code analysis diagram generation example...")

    # Example Python code to analyze
    sample_code = """
class UserService:
    def __init__(self, database):
        self.db = database

    def create_user(self, email, password):
        user = User(email, password)
        self.db.save(user)
        self.send_welcome_email(user)
        return user

    def authenticate(self, email, password):
        user = self.db.find_by_email(email)
        if user and user.check_password(password):
            return self.generate_token(user)
        raise AuthenticationError("Invalid credentials")

    def send_welcome_email(self, user):
        EmailService.send(user.email, "Welcome!")

    def generate_token(self, user):
        return JWTService.create_token(user.id)

class EmailService:
    @staticmethod
    def send(email, message):
        # Send email implementation
        pass

class JWTService:
    @staticmethod
    def create_token(user_id):
        # Create JWT token
        return f"token_{user_id}"
"""

    try:
        assert DiagramGenerator is not None
        generator = DiagramGenerator()

        # Generate class diagram from code
        result: GenerationResult = generator.from_code(sample_code, "python")

        confidence = float(result.get("confidence_score", 0.0))
        if confidence > 0.6:
            output_path = output_dir / "code_analysis_diagram.svg"

            renderer = MermaidRenderer()
            code = str(result.get("diagram_code", "")).strip()
            if not code:
                raise ValueError("No diagram code returned by code analysis.")
            _save_mermaid_code(renderer, code, output_path)

            print("✅ Generated class diagram from code analysis")
            print(f"📁 Saved to {output_path}")
            print(f"🎯 Confidence: {confidence:.2f}")

            # Show metadata
            metadata = result.get("metadata") or {}
            if metadata:
                print("📊 Analysis metadata:")
                for key, value in metadata.items():
                    if isinstance(value, dict) and len(str(value)) < 100:
                        print(f"   {key}: {value}")
        else:
            print(f"⚠️  Low confidence in code analysis ({confidence:.2f})")

    except Exception as e:
        print(f"❌ Error in code analysis: {e}")


def diagram_optimization_example(output_dir: Path) -> None:
    """Demonstrate diagram optimization capabilities."""
    if not AI_AVAILABLE:
        print("Skipping diagram optimization (AI not available)")
        return

    print("Diagram optimization example...")

    # Create a suboptimal flowchart
    flowchart = FlowchartDiagram(direction="TD", title="Unoptimized Process")

    # Add nodes in a way that could be improved
    flowchart.add_node("start", "Start Process", shape="circle")
    flowchart.add_node(
        "step1", "Very Long Step Name That Could Be Shortened", shape="rectangle"
    )
    flowchart.add_node(
        "decision1", "Is this condition met and verified?", shape="rhombus"
    )
    flowchart.add_node("step2", "Another Long Process Step", shape="rectangle")
    flowchart.add_node("step3", "Final Step", shape="rectangle")
    flowchart.add_node("end", "End", shape="circle")

    # Add edges
    flowchart.add_edge("start", "step1")
    flowchart.add_edge("step1", "decision1")
    flowchart.add_edge("decision1", "step2", label="Yes")
    flowchart.add_edge("decision1", "step3", label="No")
    flowchart.add_edge("step2", "end")
    flowchart.add_edge("step3", "end")

    try:
        # Save original
        renderer = MermaidRenderer()
        original_path = output_dir / "original_diagram.svg"
        renderer.save(flowchart, original_path)
        print(f"📁 Original diagram saved to {original_path}")

        # Optimize the diagram
        assert DiagramOptimizer is not None
        optimizer = DiagramOptimizer()

        # Prefer module-level function if available; else use optimizer instance
        optimized: OptimizationResult
        if callable(optimize_diagram):
            optimized = optimize_diagram(flowchart)
        elif hasattr(optimizer, "optimize"):
            optimized = optimizer.optimize(flowchart)
        else:
            raise RuntimeError("No optimization function available.")

        improvements = optimized.get("improvements") or []
        if improvements:
            # Save optimized version
            optimized_path = output_dir / "optimized_diagram.svg"
            code = str(optimized.get("optimized_code", "")).strip()
            if not code:
                raise ValueError("No optimized code returned by optimizer.")
            _save_mermaid_code(renderer, code, optimized_path)

            print("✅ Diagram optimized successfully")
            print(f"📁 Optimized diagram saved to {optimized_path}")
            print(f"🔧 Improvements applied: {len(improvements)}")

            for improvement in improvements:
                desc = improvement.get("description", "")
                print(f"   - {desc}")

        else:
            print("ℹ️  No optimizations suggested for this diagram")

    except Exception as e:
        print(f"❌ Error in diagram optimization: {e}")


def diagram_analysis_example(output_dir: Path) -> None:
    """Demonstrate diagram analysis and quality assessment."""
    if not AI_AVAILABLE:
        print("Skipping diagram analysis (AI not available)")
        return

    print("Diagram analysis example...")

    # Create a complex sequence diagram for analysis
    sequence = SequenceDiagram(title="Complex API Interaction", autonumber=True)

    # Add participants
    sequence.add_participant("client", "Client App")
    sequence.add_participant("gateway", "API Gateway")
    sequence.add_participant("auth", "Auth Service")
    sequence.add_participant("user_service", "User Service")
    sequence.add_participant("db", "Database")
    sequence.add_participant("cache", "Redis Cache")

    # Add complex interaction flow
    sequence.add_message("client", "gateway", "POST /api/users")
    sequence.add_message("gateway", "auth", "validate_token()")
    sequence.add_message("auth", "cache", "get_token_info()")
    sequence.add_message("cache", "auth", "token_data", message_type="return")
    sequence.add_message("auth", "gateway", "validation_result", message_type="return")
    sequence.add_message("gateway", "user_service", "create_user()")
    sequence.add_message("user_service", "db", "INSERT user")
    sequence.add_message("db", "user_service", "user_id", message_type="return")
    sequence.add_message("user_service", "cache", "cache_user()")
    sequence.add_message(
        "user_service", "gateway", "user_created", message_type="return"
    )
    sequence.add_message("gateway", "client", "201 Created", message_type="return")

    try:
        # Analyze the diagram
        assert DiagramAnalyzer is not None
        analyzer = DiagramAnalyzer()

        analysis: AnalysisResult
        if callable(analyze_diagram):
            analysis = analyze_diagram(sequence)
        elif hasattr(analyzer, "analyze"):
            analysis = analyzer.analyze(sequence)
        else:
            raise RuntimeError("No analysis function available.")

        # Save the diagram
        renderer = MermaidRenderer()
        diagram_path = output_dir / "analyzed_diagram.svg"
        renderer.save(sequence, diagram_path)
        print(f"📁 Analyzed diagram saved to {diagram_path}")

        # Display analysis results
        print("📊 Diagram Analysis Results:")

        complexity = analysis.get("complexity_analysis", {}) or {}
        quality = analysis.get("quality_metrics", {}) or {}

        complexity_score = float(complexity.get("overall_score", 0.0))
        quality_score = float(quality.get("overall_score", 0.0))
        readability = float(quality.get("readability", 0.0))
        maintainability = float(quality.get("maintainability", 0.0))

        print(f"   Complexity: {complexity_score:.2f}/10")
        print(f"   Quality Score: {quality_score:.2f}/10")
        print(f"   Readability: {readability:.2f}/10")
        print(f"   Maintainability: {maintainability:.2f}/10")

        # Show recommendations
        recs = analysis.get("recommendations") or []
        if recs:
            print(f"💡 Recommendations ({len(recs)}):")
            for rec in recs[:3]:  # Show top 3
                desc = rec.get("description", "")
                pr = rec.get("priority")
                pr_val = getattr(pr, "value", pr)
                print(f"   - {desc} (Priority: {pr_val})")

    except Exception as e:
        print(f"❌ Error in diagram analysis: {e}")


def suggestion_engine_example(output_dir: Path) -> None:
    """Demonstrate the AI suggestion engine."""
    if not AI_AVAILABLE:
        print("Skipping suggestion engine (AI not available)")
        return

    print("AI suggestion engine example...")

    # Create a basic flowchart that could be enhanced
    flowchart = FlowchartDiagram(title="Basic Login Flow")
    flowchart.add_node("start", "User Login", shape="circle")
    flowchart.add_node("check", "Check Credentials", shape="rectangle")
    flowchart.add_node("success", "Login Success", shape="rectangle")
    flowchart.add_node("fail", "Login Failed", shape="rectangle")

    flowchart.add_edge("start", "check")
    flowchart.add_edge("check", "success")
    flowchart.add_edge("check", "fail")

    try:
        # Get AI suggestions
        assert SuggestionEngine is not None
        engine = SuggestionEngine()

        if callable(get_suggestions):
            suggestions: list[dict[str, Any]] = get_suggestions(flowchart)
        elif hasattr(engine, "suggest"):
            suggestions = engine.suggest(flowchart)
        else:
            suggestions = []

        # Save original diagram
        renderer = MermaidRenderer()
        original_path = output_dir / "basic_flow.svg"
        renderer.save(flowchart, original_path)
        print(f"📁 Basic diagram saved to {original_path}")

        # Display suggestions
        if suggestions:
            print(f"💡 AI Suggestions ({len(suggestions)}):")

            for i, suggestion in enumerate(suggestions[:5], 1):  # Show top 5
                desc = getattr(suggestion, "description", None) or suggestion.get(
                    "description", ""
                )
                st = getattr(suggestion, "suggestion_type", None) or suggestion.get(
                    "suggestion_type"
                )
                pr = getattr(suggestion, "priority", None) or suggestion.get("priority")
                hint = getattr(
                    suggestion, "implementation_hint", None
                ) or suggestion.get("implementation_hint")

                st_val = getattr(st, "value", st)
                pr_val = getattr(pr, "value", pr)

                print(f"   {i}. {desc}")
                print(f"      Type: {st_val}")
                print(f"      Priority: {pr_val}")
                if hint:
                    print(f"      Hint: {hint}")
                print()

        else:
            print("ℹ️  No suggestions available for this diagram")

    except Exception as e:
        print(f"❌ Error getting suggestions: {e}")


def main() -> None:
    """Run all AI feature examples."""
    print("=== Mermaid Render AI Features Showcase ===\n")

    if not AI_AVAILABLE:
        print("⚠️  AI features require additional dependencies.")
        print("Install with: pip install diagramaid[ai]\n")

    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")

    # Run examples
    try:
        natural_language_generation_example(output_dir)
        print()

        code_analysis_generation_example(output_dir)
        print()

        diagram_optimization_example(output_dir)
        print()

        diagram_analysis_example(output_dir)
        print()

        suggestion_engine_example(output_dir)
        print()

        if AI_AVAILABLE:
            print("✅ All AI feature examples completed successfully!")
        else:
            print("ℹ️  AI examples skipped (dependencies not available)")
        print(f"Check the {output_dir} directory for generated diagrams.")

    except Exception as e:
        print(f"❌ Error running AI examples: {e}")
        raise


if __name__ == "__main__":
    main()
