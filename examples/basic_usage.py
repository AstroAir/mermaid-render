#!/usr/bin/env python3
"""
Basic usage examples for the Mermaid Render library.

This script demonstrates the fundamental features of the library including
diagram creation, rendering, and saving to files.
"""

from pathlib import Path

from mermaid_render import (
    FlowchartDiagram,
    MermaidRenderer,
    SequenceDiagram,
    export_to_file,
    quick_render,
)


def create_output_dir() -> Path:
    """Create output directory for examples."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def basic_flowchart_example(output_dir: Path) -> None:
    """Create and render a basic flowchart."""
    print("Creating basic flowchart...")

    # Create flowchart
    flowchart = FlowchartDiagram(direction="TD", title="Basic Process")
    flowchart.add_node("start", "Start", shape="circle")
    flowchart.add_node("input", "Get Input", shape="rectangle")
    flowchart.add_node("process", "Process Data", shape="rectangle")
    flowchart.add_node("decision", "Valid?", shape="rhombus")
    flowchart.add_node("output", "Show Result", shape="rectangle")
    flowchart.add_node("error", "Show Error", shape="rectangle")
    flowchart.add_node("end", "End", shape="circle")

    # Add connections
    flowchart.add_edge("start", "input")
    flowchart.add_edge("input", "process")
    flowchart.add_edge("process", "decision")
    flowchart.add_edge("decision", "output", label="Yes")
    flowchart.add_edge("decision", "error", label="No")
    flowchart.add_edge("output", "end")
    flowchart.add_edge("error", "end")

    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "basic_flowchart.svg"
    renderer.save(flowchart, output_path)
    print(f"Saved flowchart to {output_path}")


def basic_sequence_example(output_dir: Path) -> None:
    """Create and render a basic sequence diagram."""
    print("Creating basic sequence diagram...")

    # Create sequence diagram
    sequence = SequenceDiagram(title="User Login Process", autonumber=True)
    sequence.add_participant("user", "User")
    sequence.add_participant("frontend", "Frontend")
    sequence.add_participant("backend", "Backend")
    sequence.add_participant("database", "Database")

    # Add interactions
    sequence.add_message("user", "frontend", "Enter credentials")
    sequence.add_message("frontend", "backend", "POST /login")
    sequence.add_message("backend", "database", "SELECT user")
    sequence.add_message("database", "backend", "User data", message_type="return")
    sequence.add_message("backend", "frontend", "JWT token", message_type="return")
    sequence.add_message("frontend", "user", "Login success", message_type="return")

    # Add note
    sequence.add_note("Token expires in 24 hours", "backend", "right of")

    # Render with theme
    renderer = MermaidRenderer(theme="dark")
    output_path = output_dir / "basic_sequence.svg"
    renderer.save(sequence, output_path)
    print(f"Saved sequence diagram to {output_path}")


def quick_render_example(output_dir: Path) -> None:
    """Demonstrate quick rendering from raw Mermaid code."""
    print("Quick rendering example...")

    diagram_code = """
flowchart LR
    A[Client] --> B[Load Balancer]
    B --> C[Server 1]
    B --> D[Server 2]
    B --> E[Server 3]
    C --> F[Database]
    D --> F
    E --> F
"""

    # Quick render to SVG
    svg_content = quick_render(diagram_code, format="svg", theme="forest")

    # Ensure svg_content is a string before writing
    if isinstance(svg_content, bytes):
        svg_content = svg_content.decode("utf-8")

    # Save to file
    output_path = output_dir / "quick_render.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Quick rendered diagram to {output_path}")


def export_utility_example(output_dir: Path) -> None:
    """Demonstrate export utility functions."""
    print("Export utility example...")

    # Create a simple diagram
    flowchart = FlowchartDiagram()
    flowchart.add_node("A", "Input")
    flowchart.add_node("B", "Transform")
    flowchart.add_node("C", "Output")
    flowchart.add_edge("A", "B")
    flowchart.add_edge("B", "C")

    # Export using utility function
    output_path = output_dir / "export_utility.svg"
    export_to_file(flowchart, output_path, theme="neutral")

    print(f"Exported diagram using utility to {output_path}")


def theme_example(output_dir: Path) -> None:
    """Demonstrate different themes."""
    print("Theme example...")

    # Create a simple diagram
    flowchart = FlowchartDiagram()
    flowchart.add_node("A", "Start")
    flowchart.add_node("B", "Middle")
    flowchart.add_node("C", "End")
    flowchart.add_edge("A", "B")
    flowchart.add_edge("B", "C")

    # Render with different themes
    themes = ["default", "dark", "forest", "neutral"]

    for theme in themes:
        renderer = MermaidRenderer(theme=theme)
        output_path = output_dir / f"theme_{theme}.svg"
        renderer.save(flowchart, output_path)
        print(f"Saved {theme} theme to {output_path}")


def validation_example() -> None:
    """Demonstrate diagram validation."""
    print("Validation example...")

    from mermaid_render.utils import validate_mermaid_syntax

    # Valid diagram
    valid_code = """
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
"""

    result = validate_mermaid_syntax(valid_code)
    print(f"Valid diagram validation: {result}")

    # Invalid diagram
    invalid_code = """
flowchart TD
    A[Start --> B[Process
    B --> C[End]
"""

    result = validate_mermaid_syntax(invalid_code)
    print(f"Invalid diagram validation: {result}")
    if not result.is_valid:
        print("Errors found:")
        for error in result.errors:
            print(f"  - {error}")


def main() -> None:
    """Run all basic examples."""
    print("=== Mermaid Render Basic Examples ===\n")

    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")

    # Run examples
    try:
        basic_flowchart_example(output_dir)
        print()

        basic_sequence_example(output_dir)
        print()

        quick_render_example(output_dir)
        print()

        export_utility_example(output_dir)
        print()

        theme_example(output_dir)
        print()

        validation_example()
        print()

        print("✅ All examples completed successfully!")
        print(f"Check the {output_dir} directory for generated diagrams.")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    main()
