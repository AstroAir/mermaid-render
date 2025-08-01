#!/usr/bin/env python3
"""
Template system showcase for Mermaid Render.

This script demonstrates the template system including built-in templates,
custom template creation, and diagram generators for common patterns.
"""

from pathlib import Path
from mermaid_render import MermaidRenderer

# Template system (optional imports with fallbacks)
try:
    from mermaid_render.templates import (
        TemplateManager,
        FlowchartGenerator,
        SequenceGenerator,
        ClassDiagramGenerator,
        ArchitectureGenerator,
        ProcessFlowGenerator,
        generate_from_template,
        list_available_templates,
        get_template_info,
    )
    TEMPLATES_AVAILABLE = True
except ImportError:
    TEMPLATES_AVAILABLE = False
    print("⚠️  Template system not available. Install with: pip install mermaid-render[templates]")


def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/templates")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def built_in_templates_example(output_dir: Path):
    """Demonstrate using built-in templates."""
    if not TEMPLATES_AVAILABLE:
        print("Skipping built-in templates (templates not available)")
        return
        
    print("Built-in templates example...")
    
    try:
        # List available templates
        templates = list_available_templates()
        print(f"📋 Available templates: {len(templates)}")
        
        for template_name in templates[:5]:  # Show first 5
            info = get_template_info(template_name)
            print(f"   - {template_name}: {info.get('description', 'No description')}")
        
        # Use a built-in template
        if "basic_flowchart" in templates:
            diagram_code = generate_from_template(
                "basic_flowchart",
                {
                    "title": "User Registration Process",
                    "steps": [
                        {"id": "start", "label": "Start", "type": "start"},
                        {"id": "form", "label": "Fill Registration Form", "type": "process"},
                        {"id": "validate", "label": "Validate Input", "type": "decision"},
                        {"id": "save", "label": "Save User", "type": "process"},
                        {"id": "email", "label": "Send Welcome Email", "type": "process"},
                        {"id": "end", "label": "Complete", "type": "end"}
                    ],
                    "connections": [
                        {"from": "start", "to": "form"},
                        {"from": "form", "to": "validate"},
                        {"from": "validate", "to": "save", "label": "Valid"},
                        {"from": "validate", "to": "form", "label": "Invalid"},
                        {"from": "save", "to": "email"},
                        {"from": "email", "to": "end"}
                    ]
                }
            )
            
            # Save the generated diagram
            renderer = MermaidRenderer()
            output_path = output_dir / "template_flowchart.svg"
            renderer.save_raw(diagram_code, output_path)
            print(f"✅ Generated flowchart from template")
            print(f"📁 Saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Error with built-in templates: {e}")


def custom_template_creation_example(output_dir: Path):
    """Demonstrate creating custom templates."""
    if not TEMPLATES_AVAILABLE:
        print("Skipping custom template creation (templates not available)")
        return
        
    print("Custom template creation example...")
    
    try:
        # Create template manager
        template_manager = TemplateManager()
        
        # Define a custom API documentation template
        api_template_content = """
sequenceDiagram
    title: {{ title }}
    autonumber
    
    {% for participant in participants %}
    participant {{ participant.id }} as {{ participant.name }}
    {% endfor %}
    
    {% for endpoint in endpoints %}
    Note over {{ endpoint.client }}, {{ endpoint.server }}: {{ endpoint.name }}
    {{ endpoint.client }}->>{{ endpoint.server }}: {{ endpoint.method }} {{ endpoint.path }}
    {% if endpoint.auth_required %}
    {{ endpoint.server }}->>{{ endpoint.server }}: Validate Authentication
    {% endif %}
    {% if endpoint.validation %}
    {{ endpoint.server }}->>{{ endpoint.server }}: Validate Request
    {% endif %}
    {{ endpoint.server }}->>{{ endpoint.database }}: Query/Update Data
    {{ endpoint.database }}-->>{{ endpoint.server }}: Result
    {{ endpoint.server }}-->>{{ endpoint.client }}: {{ endpoint.response_code }} Response
    {% endfor %}
"""
        
        # Create the template
        template = template_manager.create_template(
            name="api_documentation",
            diagram_type="sequence",
            template_content=api_template_content,
            parameters={
                "title": {"type": "string", "required": True, "description": "API documentation title"},
                "participants": {"type": "array", "required": True, "description": "List of participants"},
                "endpoints": {"type": "array", "required": True, "description": "List of API endpoints"}
            },
            description="Template for generating API documentation sequence diagrams",
            author="Example Author",
            tags=["api", "documentation", "sequence"]
        )
        
        print(f"✅ Created custom template: {template.name}")
        
        # Use the custom template
        diagram_code = template_manager.generate(
            template.id,
            {
                "title": "User Management API",
                "participants": [
                    {"id": "client", "name": "Client App"},
                    {"id": "api", "name": "API Server"},
                    {"id": "db", "name": "Database"}
                ],
                "endpoints": [
                    {
                        "name": "Create User",
                        "client": "client",
                        "server": "api",
                        "database": "db",
                        "method": "POST",
                        "path": "/users",
                        "auth_required": True,
                        "validation": True,
                        "response_code": "201"
                    },
                    {
                        "name": "Get User",
                        "client": "client",
                        "server": "api",
                        "database": "db",
                        "method": "GET",
                        "path": "/users/{id}",
                        "auth_required": True,
                        "validation": False,
                        "response_code": "200"
                    }
                ]
            }
        )
        
        # Save the generated diagram
        renderer = MermaidRenderer()
        output_path = output_dir / "custom_template_api.svg"
        renderer.save_raw(diagram_code, output_path)
        print(f"📁 Generated API documentation saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Error with custom template: {e}")


def flowchart_generator_example(output_dir: Path):
    """Demonstrate the FlowchartGenerator."""
    if not TEMPLATES_AVAILABLE:
        print("Skipping flowchart generator (templates not available)")
        return
        
    print("FlowchartGenerator example...")
    
    try:
        generator = FlowchartGenerator()
        
        # Generate from process steps
        process_steps = [
            {"id": "start", "label": "Receive Order", "type": "start"},
            {"id": "validate", "label": "Validate Order", "type": "decision"},
            {"id": "inventory", "label": "Check Inventory", "type": "process"},
            {"id": "payment", "label": "Process Payment", "type": "process"},
            {"id": "ship", "label": "Ship Order", "type": "process"},
            {"id": "notify", "label": "Send Confirmation", "type": "process"},
            {"id": "end", "label": "Order Complete", "type": "end"},
            {"id": "reject", "label": "Reject Order", "type": "end"}
        ]
        
        flowchart = generator.from_steps(
            steps=process_steps,
            title="Order Processing Workflow",
            direction="TD"
        )
        
        # Add custom connections for decision logic
        flowchart.add_edge("validate", "inventory", label="Valid")
        flowchart.add_edge("validate", "reject", label="Invalid")
        
        # Save the generated flowchart
        renderer = MermaidRenderer()
        output_path = output_dir / "generated_flowchart.svg"
        renderer.save(flowchart, output_path)
        print(f"✅ Generated flowchart from steps")
        print(f"📁 Saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Error with flowchart generator: {e}")


def sequence_generator_example(output_dir: Path):
    """Demonstrate the SequenceGenerator."""
    if not TEMPLATES_AVAILABLE:
        print("Skipping sequence generator (templates not available)")
        return
        
    print("SequenceGenerator example...")
    
    try:
        generator = SequenceGenerator()
        
        # Generate from interaction data
        interactions = [
            {
                "from": "user",
                "to": "frontend",
                "message": "Click Login Button",
                "type": "sync"
            },
            {
                "from": "frontend",
                "to": "backend",
                "message": "POST /auth/login",
                "type": "sync"
            },
            {
                "from": "backend",
                "to": "database",
                "message": "SELECT user WHERE email = ?",
                "type": "sync"
            },
            {
                "from": "database",
                "to": "backend",
                "message": "User data",
                "type": "return"
            },
            {
                "from": "backend",
                "to": "backend",
                "message": "Verify password",
                "type": "self"
            },
            {
                "from": "backend",
                "to": "frontend",
                "message": "JWT token",
                "type": "return"
            },
            {
                "from": "frontend",
                "to": "user",
                "message": "Redirect to dashboard",
                "type": "return"
            }
        ]
        
        sequence = generator.from_interactions(
            interactions=interactions,
            title="User Login Sequence",
            participants={
                "user": "User",
                "frontend": "Frontend App",
                "backend": "Backend API",
                "database": "Database"
            }
        )
        
        # Save the generated sequence diagram
        renderer = MermaidRenderer()
        output_path = output_dir / "generated_sequence.svg"
        renderer.save(sequence, output_path)
        print(f"✅ Generated sequence diagram from interactions")
        print(f"📁 Saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Error with sequence generator: {e}")


def architecture_generator_example(output_dir: Path):
    """Demonstrate the ArchitectureGenerator."""
    if not TEMPLATES_AVAILABLE:
        print("Skipping architecture generator (templates not available)")
        return
        
    print("ArchitectureGenerator example...")
    
    try:
        generator = ArchitectureGenerator()
        
        # Define system components
        components = {
            "frontend": {
                "name": "React Frontend",
                "type": "client",
                "technologies": ["React", "TypeScript", "Tailwind"]
            },
            "api_gateway": {
                "name": "API Gateway",
                "type": "gateway",
                "technologies": ["Kong", "Rate Limiting"]
            },
            "auth_service": {
                "name": "Authentication Service",
                "type": "service",
                "technologies": ["Node.js", "JWT"]
            },
            "user_service": {
                "name": "User Service",
                "type": "service",
                "technologies": ["Python", "FastAPI"]
            },
            "database": {
                "name": "PostgreSQL",
                "type": "database",
                "technologies": ["PostgreSQL", "Connection Pool"]
            },
            "cache": {
                "name": "Redis Cache",
                "type": "cache",
                "technologies": ["Redis", "Clustering"]
            }
        }
        
        connections = [
            {"from": "frontend", "to": "api_gateway", "label": "HTTPS"},
            {"from": "api_gateway", "to": "auth_service", "label": "Auth"},
            {"from": "api_gateway", "to": "user_service", "label": "API Calls"},
            {"from": "auth_service", "to": "cache", "label": "Session Store"},
            {"from": "user_service", "to": "database", "label": "SQL"},
            {"from": "user_service", "to": "cache", "label": "Caching"}
        ]
        
        architecture = generator.from_components(
            components=components,
            connections=connections,
            title="Microservices Architecture"
        )
        
        # Save the generated architecture diagram
        renderer = MermaidRenderer()
        output_path = output_dir / "generated_architecture.svg"
        renderer.save(architecture, output_path)
        print(f"✅ Generated architecture diagram")
        print(f"📁 Saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Error with architecture generator: {e}")


def main():
    """Run all template system examples."""
    print("=== Mermaid Render Template System Showcase ===\n")
    
    if not TEMPLATES_AVAILABLE:
        print("⚠️  Template system requires additional dependencies.")
        print("Install with: pip install mermaid-render[templates]\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Run examples
    try:
        built_in_templates_example(output_dir)
        print()
        
        custom_template_creation_example(output_dir)
        print()
        
        flowchart_generator_example(output_dir)
        print()
        
        sequence_generator_example(output_dir)
        print()
        
        architecture_generator_example(output_dir)
        print()
        
        if TEMPLATES_AVAILABLE:
            print("✅ All template system examples completed successfully!")
        else:
            print("ℹ️  Template examples skipped (dependencies not available)")
        print(f"Check the {output_dir} directory for generated diagrams.")
        
    except Exception as e:
        print(f"❌ Error running template examples: {e}")
        raise


if __name__ == "__main__":
    main()
