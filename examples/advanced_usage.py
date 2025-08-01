#!/usr/bin/env python3
"""
Advanced usage examples for the Mermaid Render library.

This script demonstrates advanced features including custom themes,
configuration management, batch processing, and error handling.
"""

from pathlib import Path
from typing import Dict, Any
from mermaid_render import (
    MermaidRenderer,
    MermaidConfig,
    MermaidTheme,
    FlowchartDiagram,
    SequenceDiagram,
    ClassDiagram,
)
from mermaid_render.config import ThemeManager, ConfigManager
from mermaid_render.utils import export_multiple_formats, batch_export
from mermaid_render.exceptions import ValidationError, RenderingError
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute


def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/advanced")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def custom_theme_example(output_dir: Path):
    """Demonstrate custom theme creation and usage."""
    print("Custom theme example...")
    
    # Create custom theme
    custom_theme = MermaidTheme("custom",
        primaryColor="#e74c3c",
        primaryTextColor="#ffffff",
        primaryBorderColor="#c0392b",
        lineColor="#2c3e50",
        secondaryColor="#f39c12",
        tertiaryColor="#e67e22"
    )
    
    # Create diagram
    flowchart = FlowchartDiagram()
    flowchart.add_node("A", "Custom Theme", shape="rectangle")
    flowchart.add_node("B", "Beautiful Colors", shape="circle")
    flowchart.add_node("C", "Professional Look", shape="rhombus")
    flowchart.add_edge("A", "B")
    flowchart.add_edge("B", "C")
    
    # Render with custom theme
    renderer = MermaidRenderer(theme=custom_theme)
    output_path = output_dir / "custom_theme.svg"
    renderer.save(flowchart, output_path)
    
    print(f"Saved custom theme example to {output_path}")


def theme_manager_example(output_dir: Path):
    """Demonstrate theme management capabilities."""
    print("Theme manager example...")
    
    # Create theme manager with custom directory
    themes_dir = output_dir / "themes"
    theme_manager = ThemeManager(custom_themes_dir=themes_dir)
    
    # Create and save custom themes
    corporate_theme = {
        "theme": "corporate",
        "primaryColor": "#2c3e50",
        "primaryTextColor": "#ffffff",
        "primaryBorderColor": "#34495e",
        "lineColor": "#7f8c8d",
        "secondaryColor": "#3498db",
        "tertiaryColor": "#2980b9"
    }
    
    theme_manager.add_custom_theme("corporate", corporate_theme, save_to_file=True)
    
    # Create variant theme
    theme_manager.create_theme_variant(
        "corporate", 
        "corporate_green",
        {"primaryColor": "#27ae60", "secondaryColor": "#2ecc71"}
    )
    
    # List available themes
    available = theme_manager.get_available_themes()
    print(f"Available themes: {', '.join(available)}")
    
    # Use custom theme
    flowchart = FlowchartDiagram()
    flowchart.add_node("A", "Corporate")
    flowchart.add_node("B", "Professional")
    flowchart.add_edge("A", "B")
    
    corporate_config = theme_manager.get_theme("corporate")
    theme = MermaidTheme("custom", **corporate_config)
    
    renderer = MermaidRenderer(theme=theme)
    output_path = output_dir / "corporate_theme.svg"
    renderer.save(flowchart, output_path)
    
    print(f"Saved corporate theme example to {output_path}")


def configuration_example(output_dir: Path):
    """Demonstrate configuration management."""
    print("Configuration example...")
    
    # Create custom configuration
    config = MermaidConfig(
        timeout=60,
        default_theme="dark",
        validate_syntax=True,
        cache_enabled=False,
        custom_setting="example_value"
    )
    
    # Create config manager
    config_manager = ConfigManager(load_env=False)
    config_manager.update({
        "timeout": 45,
        "default_format": "svg",
        "max_width": 1200,
        "max_height": 800
    })
    
    # Save configuration to file
    config_file = output_dir / "config.json"
    config_manager.save_to_file(config_file)
    
    # Use configuration with renderer
    renderer = MermaidRenderer(config=config)
    
    # Create simple diagram
    flowchart = FlowchartDiagram()
    flowchart.add_node("A", "Configured")
    flowchart.add_node("B", "Rendering")
    flowchart.add_edge("A", "B")
    
    output_path = output_dir / "configured.svg"
    renderer.save(flowchart, output_path)
    
    print(f"Saved configured example to {output_path}")
    print(f"Configuration saved to {config_file}")


def batch_processing_example(output_dir: Path):
    """Demonstrate batch processing capabilities."""
    print("Batch processing example...")
    
    # Create multiple diagrams
    diagrams = {}
    
    # Flowchart
    flowchart = FlowchartDiagram()
    flowchart.add_node("A", "Start")
    flowchart.add_node("B", "Process")
    flowchart.add_node("C", "End")
    flowchart.add_edge("A", "B")
    flowchart.add_edge("B", "C")
    diagrams["process_flow"] = flowchart
    
    # Sequence diagram
    sequence = SequenceDiagram()
    sequence.add_participant("User")
    sequence.add_participant("System")
    sequence.add_message("User", "System", "Request")
    sequence.add_message("System", "User", "Response", message_type="return")
    diagrams["user_interaction"] = sequence
    
    # Class diagram
    class_diagram = ClassDiagram()
    base_class = class_diagram.add_class("BaseClass", is_abstract=True)
    base_class.add_method(ClassMethod("abstract_method", "public", "void", is_abstract=True))
    
    derived_class = class_diagram.add_class("DerivedClass")
    derived_class.add_method(ClassMethod("concrete_method", "public", "void"))
    
    class_diagram.add_relationship("DerivedClass", "BaseClass", "inheritance")
    diagrams["class_hierarchy"] = class_diagram
    
    # Batch export to single format
    batch_dir = output_dir / "batch"
    paths = batch_export(diagrams, batch_dir, format="svg", theme="forest")
    
    print("Batch exported diagrams:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    
    # Export single diagram to multiple formats
    multi_paths = export_multiple_formats(
        flowchart,
        output_dir / "multi_format",
        ["svg"]  # Only SVG for this example
    )
    
    print("Multi-format export:")
    for format, path in multi_paths.items():
        print(f"  {format}: {path}")


def error_handling_example():
    """Demonstrate error handling patterns."""
    print("Error handling example...")
    
    from mermaid_render.exceptions import (
        ValidationError,
        RenderingError,
        UnsupportedFormatError,
        DiagramError,
        ThemeError
    )
    
    # Diagram creation errors
    try:
        flowchart = FlowchartDiagram()
        flowchart.add_edge("A", "B")  # Nodes don't exist
    except DiagramError as e:
        print(f"✅ Caught diagram error: {e}")
    
    # Theme errors
    try:
        from mermaid_render.config import ThemeManager
        theme_manager = ThemeManager()
        theme_manager.get_theme("nonexistent_theme")
    except ThemeError as e:
        print(f"✅ Caught theme error: {e}")
    
    # Validation errors
    try:
        from mermaid_render.utils import validate_mermaid_syntax
        result = validate_mermaid_syntax("invalid diagram")
        if not result.is_valid:
            print(f"✅ Validation failed as expected: {result.errors}")
    except Exception as e:
        print(f"✅ Caught validation error: {e}")
    
    # Unsupported format
    try:
        renderer = MermaidRenderer()
        renderer.render("flowchart TD\n    A --> B", format="gif")
    except UnsupportedFormatError as e:
        print(f"✅ Caught unsupported format error: {e}")


def complex_diagram_example(output_dir: Path):
    """Create a complex diagram with multiple features."""
    print("Complex diagram example...")
    
    # Create complex flowchart with subgraphs
    flowchart = FlowchartDiagram(direction="TD", title="Complex Business Process")
    
    # Main process nodes
    flowchart.add_node("start", "Start Process", shape="circle")
    flowchart.add_node("input", "Collect Input", shape="rectangle")
    flowchart.add_node("validate", "Validate Data", shape="rhombus")
    flowchart.add_node("process", "Process Request", shape="rectangle")
    flowchart.add_node("approve", "Needs Approval?", shape="rhombus")
    flowchart.add_node("auto_approve", "Auto Approve", shape="rectangle")
    flowchart.add_node("manual_review", "Manual Review", shape="rectangle")
    flowchart.add_node("approved", "Approved?", shape="rhombus")
    flowchart.add_node("execute", "Execute Action", shape="rectangle")
    flowchart.add_node("notify", "Send Notification", shape="rectangle")
    flowchart.add_node("end", "End Process", shape="circle")
    flowchart.add_node("error", "Handle Error", shape="rectangle")
    
    # Add subgraph for approval process
    approval_subgraph = flowchart.add_subgraph("approval", "Approval Process")
    flowchart.add_node_to_subgraph("manual_review", "approval")
    flowchart.add_node_to_subgraph("approved", "approval")
    
    # Main flow
    flowchart.add_edge("start", "input")
    flowchart.add_edge("input", "validate")
    flowchart.add_edge("validate", "process", label="Valid")
    flowchart.add_edge("validate", "error", label="Invalid")
    flowchart.add_edge("process", "approve")
    flowchart.add_edge("approve", "auto_approve", label="No")
    flowchart.add_edge("approve", "manual_review", label="Yes")
    flowchart.add_edge("auto_approve", "execute")
    flowchart.add_edge("manual_review", "approved")
    flowchart.add_edge("approved", "execute", label="Yes")
    flowchart.add_edge("approved", "error", label="No")
    flowchart.add_edge("execute", "notify")
    flowchart.add_edge("notify", "end")
    flowchart.add_edge("error", "end")
    
    # Add styling
    flowchart.add_style("start", {"fill": "#90EE90"})
    flowchart.add_style("end", {"fill": "#FFB6C1"})
    flowchart.add_style("error", {"fill": "#FFA07A"})
    
    # Render with custom theme
    renderer = MermaidRenderer(theme="neutral")
    output_path = output_dir / "complex_process.svg"
    renderer.save(flowchart, output_path)
    
    print(f"Saved complex diagram to {output_path}")


def main():
    """Run all advanced examples."""
    print("=== Mermaid Render Advanced Examples ===\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Run examples
    try:
        custom_theme_example(output_dir)
        print()
        
        theme_manager_example(output_dir)
        print()
        
        configuration_example(output_dir)
        print()
        
        batch_processing_example(output_dir)
        print()
        
        error_handling_example()
        print()
        
        complex_diagram_example(output_dir)
        print()
        
        print("✅ All advanced examples completed successfully!")
        print(f"Check the {output_dir} directory for generated diagrams.")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    main()
