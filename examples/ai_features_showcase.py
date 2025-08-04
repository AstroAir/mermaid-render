#!/usr/bin/env python3
"""
AI-powered features showcase for Mermaid Render.

This script demonstrates the AI capabilities including natural language
diagram generation, code analysis, optimization, and intelligent suggestions.
"""

from pathlib import Path

from mermaid_render import (
    FlowchartDiagram,
    MermaidRenderer,
    SequenceDiagram,
)

# AI features (optional imports with fallbacks)
try:
    from mermaid_render.ai import (
        DiagramAnalyzer,
        DiagramGenerator,
        DiagramOptimizer,
        NLProcessor,
        SuggestionEngine,
        analyze_diagram,
        generate_from_text,
        get_suggestions,
        optimize_diagram,
    )

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  AI features not available. Install with: pip install mermaid-render[ai]")


def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/ai_features")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def natural_language_generation_example(output_dir: Path):
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

    generator = DiagramGenerator()

    for i, description in enumerate(descriptions):
        try:
            print(f"Generating diagram from: '{description}'")

            # Generate diagram from natural language
            result = generate_from_text(description)

            if result.confidence_score > 0.7:
                # Save the generated diagram
                output_path = output_dir / f"ai_generated_{i + 1}.svg"

                # Render the generated Mermaid code
                renderer = MermaidRenderer()
                renderer.save_raw(result.diagram_code, output_path)

                print(f"  ✅ Generated with {result.confidence_score:.2f} confidence")
                print(f"  📁 Saved to {output_path}")

                # Show suggestions if available
                if result.suggestions:
                    print(f"  💡 Suggestions: {len(result.suggestions)} available")
                    for suggestion in result.suggestions[:2]:  # Show first 2
                        print(f"     - {suggestion.description}")
            else:
                print(f"  ⚠️  Low confidence ({result.confidence_score:.2f}), skipping")

        except Exception as e:
            print(f"  ❌ Error generating diagram: {e}")

        print()


def code_analysis_generation_example(output_dir: Path):
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
        generator = DiagramGenerator()

        # Generate class diagram from code
        result = generator.from_code(sample_code, "python")

        if result.confidence_score > 0.6:
            output_path = output_dir / "code_analysis_diagram.svg"

            renderer = MermaidRenderer()
            renderer.save_raw(result.diagram_code, output_path)

            print(f"✅ Generated class diagram from code analysis")
            print(f"📁 Saved to {output_path}")
            print(f"🎯 Confidence: {result.confidence_score:.2f}")

            # Show metadata
            if result.metadata:
                print("📊 Analysis metadata:")
                for key, value in result.metadata.items():
                    if isinstance(value, dict) and len(str(value)) < 100:
                        print(f"   {key}: {value}")
        else:
            print(f"⚠️  Low confidence in code analysis ({result.confidence_score:.2f})")

    except Exception as e:
        print(f"❌ Error in code analysis: {e}")


def diagram_optimization_example(output_dir: Path):
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
        optimizer = DiagramOptimizer()
        optimized_result = optimize_diagram(flowchart)

        if optimized_result.improvements:
            # Save optimized version
            optimized_path = output_dir / "optimized_diagram.svg"
            renderer.save_raw(optimized_result.optimized_code, optimized_path)

            print(f"✅ Diagram optimized successfully")
            print(f"📁 Optimized diagram saved to {optimized_path}")
            print(f"🔧 Improvements applied: {len(optimized_result.improvements)}")

            for improvement in optimized_result.improvements:
                print(f"   - {improvement.description}")

        else:
            print("ℹ️  No optimizations suggested for this diagram")

    except Exception as e:
        print(f"❌ Error in diagram optimization: {e}")


def diagram_analysis_example(output_dir: Path):
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
        analyzer = DiagramAnalyzer()
        analysis_result = analyze_diagram(sequence)

        # Save the diagram
        renderer = MermaidRenderer()
        diagram_path = output_dir / "analyzed_diagram.svg"
        renderer.save(sequence, diagram_path)
        print(f"📁 Analyzed diagram saved to {diagram_path}")

        # Display analysis results
        print(f"📊 Diagram Analysis Results:")
        print(
            f"   Complexity: {analysis_result.complexity_analysis.overall_score:.2f}/10"
        )
        print(
            f"   Quality Score: {analysis_result.quality_metrics.overall_score:.2f}/10"
        )
        print(f"   Readability: {analysis_result.quality_metrics.readability:.2f}/10")
        print(
            f"   Maintainability: {analysis_result.quality_metrics.maintainability:.2f}/10"
        )

        # Show recommendations
        if analysis_result.recommendations:
            print(f"💡 Recommendations ({len(analysis_result.recommendations)}):")
            for rec in analysis_result.recommendations[:3]:  # Show top 3
                print(f"   - {rec.description} (Priority: {rec.priority.value})")

    except Exception as e:
        print(f"❌ Error in diagram analysis: {e}")


def suggestion_engine_example(output_dir: Path):
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
        suggestion_engine = SuggestionEngine()
        suggestions = get_suggestions(flowchart)

        # Save original diagram
        renderer = MermaidRenderer()
        original_path = output_dir / "basic_flow.svg"
        renderer.save(flowchart, original_path)
        print(f"📁 Basic diagram saved to {original_path}")

        # Display suggestions
        if suggestions:
            print(f"💡 AI Suggestions ({len(suggestions)}):")

            for i, suggestion in enumerate(suggestions[:5], 1):  # Show top 5
                print(f"   {i}. {suggestion.description}")
                print(f"      Type: {suggestion.suggestion_type.value}")
                print(f"      Priority: {suggestion.priority.value}")
                if suggestion.implementation_hint:
                    print(f"      Hint: {suggestion.implementation_hint}")
                print()

        else:
            print("ℹ️  No suggestions available for this diagram")

    except Exception as e:
        print(f"❌ Error getting suggestions: {e}")


def main():
    """Run all AI feature examples."""
    print("=== Mermaid Render AI Features Showcase ===\n")

    if not AI_AVAILABLE:
        print("⚠️  AI features require additional dependencies.")
        print("Install with: pip install mermaid-render[ai]\n")

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
