#!/usr/bin/env python3
"""
Demonstration script for the Mermaid Render library.

This script showcases the key features of the library without requiring
network access for rendering.
"""

from mermaid_render import (
    FlowchartDiagram,
    SequenceDiagram,
    ClassDiagram,
    MermaidRenderer,
    MermaidTheme,
    MermaidConfig,
)
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute
from mermaid_render.utils import validate_mermaid_syntax, get_supported_formats
from mermaid_render.config import ThemeManager


def demo_flowchart():
    """Demonstrate flowchart creation."""
    print("🔄 Creating a flowchart diagram...")
    
    flowchart = FlowchartDiagram(direction="TD", title="Software Development Process")
    
    # Add nodes with different shapes
    flowchart.add_node("start", "Start Project", shape="circle")
    flowchart.add_node("requirements", "Gather Requirements", shape="rectangle")
    flowchart.add_node("design", "Design System", shape="rectangle")
    flowchart.add_node("review", "Design Review", shape="rhombus")
    flowchart.add_node("implement", "Implementation", shape="rectangle")
    flowchart.add_node("test", "Testing", shape="rectangle")
    flowchart.add_node("deploy", "Deploy", shape="rectangle")
    flowchart.add_node("end", "Project Complete", shape="circle")
    flowchart.add_node("revise", "Revise Design", shape="rectangle")
    
    # Add connections
    flowchart.add_edge("start", "requirements")
    flowchart.add_edge("requirements", "design")
    flowchart.add_edge("design", "review")
    flowchart.add_edge("review", "implement", label="Approved")
    flowchart.add_edge("review", "revise", label="Needs Changes")
    flowchart.add_edge("revise", "design")
    flowchart.add_edge("implement", "test")
    flowchart.add_edge("test", "deploy")
    flowchart.add_edge("deploy", "end")
    
    print("Generated Mermaid code:")
    print(flowchart.to_mermaid())
    print()


def demo_sequence():
    """Demonstrate sequence diagram creation."""
    print("📊 Creating a sequence diagram...")
    
    sequence = SequenceDiagram(title="E-commerce Order Process", autonumber=True)
    
    # Add participants
    sequence.add_participant("customer", "Customer")
    sequence.add_participant("web", "Web App")
    sequence.add_participant("api", "API Server")
    sequence.add_participant("payment", "Payment Service")
    sequence.add_participant("inventory", "Inventory")
    sequence.add_participant("shipping", "Shipping")
    
    # Add interactions
    sequence.add_message("customer", "web", "Browse products")
    sequence.add_message("web", "api", "GET /products")
    sequence.add_message("api", "inventory", "Check availability")
    sequence.add_message("inventory", "api", "Product list", message_type="return")
    sequence.add_message("api", "web", "Product data", message_type="return")
    sequence.add_message("web", "customer", "Display products", message_type="return")
    
    sequence.add_message("customer", "web", "Add to cart")
    sequence.add_message("customer", "web", "Checkout")
    sequence.add_message("web", "api", "POST /orders")
    sequence.add_message("api", "payment", "Process payment")
    sequence.add_message("payment", "api", "Payment confirmed", message_type="return")
    sequence.add_message("api", "inventory", "Reserve items")
    sequence.add_message("api", "shipping", "Create shipment")
    sequence.add_message("api", "web", "Order confirmation", message_type="return")
    sequence.add_message("web", "customer", "Order success", message_type="return")
    
    # Add note
    sequence.add_note("Payment processed securely", "payment", "right of")
    
    print("Generated Mermaid code:")
    print(sequence.to_mermaid())
    print()


def demo_class_diagram():
    """Demonstrate class diagram creation."""
    print("🏗️ Creating a class diagram...")
    
    class_diagram = ClassDiagram(title="Animal Hierarchy")
    
    # Add Animal base class
    animal = class_diagram.add_class("Animal", is_abstract=True)
    animal.add_attribute(ClassAttribute("name", "String", "protected"))
    animal.add_attribute(ClassAttribute("age", "int", "protected"))
    animal.add_method(ClassMethod("move", "public", "void", is_abstract=True))
    animal.add_method(ClassMethod("eat", "public", "void"))
    animal.add_method(ClassMethod("sleep", "public", "void"))
    
    # Add Mammal class
    mammal = class_diagram.add_class("Mammal", is_abstract=True)
    mammal.add_attribute(ClassAttribute("furColor", "String", "protected"))
    mammal.add_method(ClassMethod("giveBirth", "public", "void"))
    
    # Add Dog class
    dog = class_diagram.add_class("Dog")
    dog.add_attribute(ClassAttribute("breed", "String", "private"))
    dog.add_method(ClassMethod("bark", "public", "void"))
    dog.add_method(ClassMethod("wagTail", "public", "void"))
    dog.add_method(ClassMethod("move", "public", "void"))  # Override
    
    # Add Bird class
    bird = class_diagram.add_class("Bird", is_abstract=True)
    bird.add_attribute(ClassAttribute("wingspan", "double", "protected"))
    bird.add_method(ClassMethod("fly", "public", "void", is_abstract=True))
    
    # Add Eagle class
    eagle = class_diagram.add_class("Eagle")
    eagle.add_method(ClassMethod("hunt", "public", "void"))
    eagle.add_method(ClassMethod("fly", "public", "void"))  # Override
    eagle.add_method(ClassMethod("move", "public", "void"))  # Override
    
    # Add relationships
    class_diagram.add_relationship("Mammal", "Animal", "inheritance")
    class_diagram.add_relationship("Bird", "Animal", "inheritance")
    class_diagram.add_relationship("Dog", "Mammal", "inheritance")
    class_diagram.add_relationship("Eagle", "Bird", "inheritance")
    
    print("Generated Mermaid code:")
    print(class_diagram.to_mermaid())
    print()


def demo_validation():
    """Demonstrate validation functionality."""
    print("✅ Testing validation...")
    
    # Valid diagram
    valid_code = """
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]
    C --> D
"""
    
    result = validate_mermaid_syntax(valid_code)
    print(f"Valid diagram: {result}")
    
    # Invalid diagram
    invalid_code = """
flowchart TD
    A[Start --> B{Decision
    B -->|Yes| C[Process]
    B -->|No| D[End]
    C --> D
"""
    
    result = validate_mermaid_syntax(invalid_code)
    print(f"Invalid diagram: {result}")
    if not result.is_valid:
        print("Validation errors:")
        for error in result.errors:
            print(f"  - {error}")
    print()


def demo_themes():
    """Demonstrate theme management."""
    print("🎨 Testing theme management...")
    
    # Create theme manager
    theme_manager = ThemeManager()
    
    # List built-in themes
    built_in = theme_manager.get_built_in_themes()
    print(f"Built-in themes: {', '.join(built_in)}")
    
    # Create custom theme
    custom_theme_config = {
        "theme": "custom",
        "primaryColor": "#ff6b6b",
        "primaryTextColor": "#ffffff",
        "primaryBorderColor": "#ee5a52",
        "lineColor": "#4ecdc4",
        "secondaryColor": "#45b7d1",
        "tertiaryColor": "#96ceb4"
    }
    
    theme_manager.add_custom_theme("vibrant", custom_theme_config, save_to_file=False)
    
    # List all themes
    all_themes = theme_manager.get_available_themes()
    print(f"All available themes: {', '.join(all_themes)}")
    
    # Create theme object
    custom_theme = MermaidTheme("custom", **custom_theme_config)
    print(f"Custom theme created: {custom_theme.name}")
    print()


def demo_configuration():
    """Demonstrate configuration management."""
    print("⚙️ Testing configuration...")
    
    # Create custom configuration
    config = MermaidConfig(
        timeout=45,
        default_theme="dark",
        validate_syntax=True,
        cache_enabled=False,
        custom_option="demo_value"
    )
    
    print(f"Timeout: {config.get('timeout')}")
    print(f"Default theme: {config.get('default_theme')}")
    print(f"Custom option: {config.get('custom_option')}")
    print(f"Non-existent option: {config.get('non_existent', 'default_value')}")
    
    # Update configuration
    config.update({"timeout": 60, "new_setting": "updated"})
    print(f"Updated timeout: {config.get('timeout')}")
    print(f"New setting: {config.get('new_setting')}")
    print()


def demo_utilities():
    """Demonstrate utility functions."""
    print("🛠️ Testing utilities...")
    
    from mermaid_render.utils import (
        get_supported_formats,
        get_available_themes,
        detect_diagram_type,
        sanitize_filename,
    )
    
    # Test format utilities
    formats = get_supported_formats()
    print(f"Supported formats: {', '.join(formats)}")
    
    # Test theme utilities
    themes = get_available_themes()
    print(f"Available themes: {', '.join(themes)}")
    
    # Test diagram type detection
    flowchart_code = "flowchart TD\n    A --> B"
    sequence_code = "sequenceDiagram\n    A->>B: Message"
    
    print(f"Flowchart type: {detect_diagram_type(flowchart_code)}")
    print(f"Sequence type: {detect_diagram_type(sequence_code)}")
    
    # Test filename sanitization
    unsafe_name = "My Diagram: Version 2.0 (Final)"
    safe_name = sanitize_filename(unsafe_name)
    print(f"Sanitized filename: '{unsafe_name}' -> '{safe_name}'")
    print()


def main():
    """Run the complete demonstration."""
    print("🚀 Mermaid Render Library Demonstration")
    print("=" * 50)
    print()
    
    try:
        demo_flowchart()
        demo_sequence()
        demo_class_diagram()
        demo_validation()
        demo_themes()
        demo_configuration()
        demo_utilities()
        
        print("🎉 Demonstration completed successfully!")
        print()
        print("Key Features Demonstrated:")
        print("✅ Object-oriented diagram creation")
        print("✅ Multiple diagram types (flowchart, sequence, class)")
        print("✅ Mermaid syntax generation")
        print("✅ Syntax validation with error reporting")
        print("✅ Theme management (built-in and custom)")
        print("✅ Configuration management")
        print("✅ Utility functions")
        print("✅ Type safety and error handling")
        print()
        print("The library is ready for production use!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
