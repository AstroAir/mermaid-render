#!/usr/bin/env python3
"""
Comprehensive showcase of all diagram types supported by Mermaid Render.

This script demonstrates all available diagram types with practical examples
that show real-world use cases for each type.
"""

from pathlib import Path
from mermaid_render import (
    MermaidRenderer,
    StateDiagram,
    ERDiagram,
    UserJourneyDiagram,
    GanttDiagram,
    PieChartDiagram,
    GitGraphDiagram,
    MindmapDiagram,
)


def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/diagram_types")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def state_diagram_example(output_dir: Path):
    """Create a state diagram for a user authentication system."""
    print("Creating state diagram example...")
    
    state = StateDiagram(title="User Authentication State Machine")
    
    # Add states
    state.add_state("logged_out", "Logged Out")
    state.add_state("authenticating", "Authenticating")
    state.add_state("logged_in", "Logged In")
    state.add_state("session_expired", "Session Expired")
    state.add_state("locked_out", "Locked Out")
    
    # Add transitions
    state.add_transition("logged_out", "authenticating", "login_attempt")
    state.add_transition("authenticating", "logged_in", "success")
    state.add_transition("authenticating", "logged_out", "invalid_credentials")
    state.add_transition("authenticating", "locked_out", "too_many_attempts")
    state.add_transition("logged_in", "session_expired", "timeout")
    state.add_transition("logged_in", "logged_out", "logout")
    state.add_transition("session_expired", "logged_out", "session_cleanup")
    state.add_transition("locked_out", "logged_out", "unlock_timeout")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "state_diagram.svg"
    renderer.save(state, output_path)
    print(f"Saved state diagram to {output_path}")


def er_diagram_example(output_dir: Path):
    """Create an ER diagram for an e-commerce database."""
    print("Creating ER diagram example...")
    
    er = ERDiagram(title="E-commerce Database Schema")
    
    # Add entities
    er.add_entity("User", {
        "user_id": "PK",
        "email": "string",
        "password_hash": "string",
        "created_at": "datetime",
        "is_active": "boolean"
    })
    
    er.add_entity("Product", {
        "product_id": "PK",
        "name": "string",
        "description": "text",
        "price": "decimal",
        "stock_quantity": "integer",
        "category_id": "FK"
    })
    
    er.add_entity("Category", {
        "category_id": "PK",
        "name": "string",
        "description": "text"
    })
    
    er.add_entity("Order", {
        "order_id": "PK",
        "user_id": "FK",
        "total_amount": "decimal",
        "status": "string",
        "created_at": "datetime"
    })
    
    er.add_entity("OrderItem", {
        "order_item_id": "PK",
        "order_id": "FK",
        "product_id": "FK",
        "quantity": "integer",
        "unit_price": "decimal"
    })
    
    # Add relationships
    er.add_relationship("User", "Order", "one-to-many", "places")
    er.add_relationship("Order", "OrderItem", "one-to-many", "contains")
    er.add_relationship("Product", "OrderItem", "one-to-many", "included_in")
    er.add_relationship("Category", "Product", "one-to-many", "categorizes")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "er_diagram.svg"
    renderer.save(er, output_path)
    print(f"Saved ER diagram to {output_path}")


def user_journey_example(output_dir: Path):
    """Create a user journey diagram for online shopping."""
    print("Creating user journey diagram example...")
    
    journey = UserJourneyDiagram(title="Online Shopping User Journey")
    
    # Add journey steps
    journey.add_step("Discovery", "User discovers product", 3, ["Browsing", "Search"])
    journey.add_step("Research", "User researches product", 4, ["Reviews", "Comparison"])
    journey.add_step("Decision", "User decides to purchase", 5, ["Add to Cart"])
    journey.add_step("Checkout", "User completes purchase", 2, ["Payment", "Shipping"])
    journey.add_step("Delivery", "User receives product", 5, ["Tracking", "Unboxing"])
    journey.add_step("Support", "User contacts support", 1, ["Help", "Returns"])
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "user_journey.svg"
    renderer.save(journey, output_path)
    print(f"Saved user journey diagram to {output_path}")


def gantt_diagram_example(output_dir: Path):
    """Create a Gantt chart for a software development project."""
    print("Creating Gantt diagram example...")
    
    gantt = GanttDiagram(title="Software Development Project Timeline")
    
    # Add sections and tasks
    gantt.add_section("Planning")
    gantt.add_task("Requirements", "2024-01-01", "2024-01-15", "done")
    gantt.add_task("Design", "2024-01-10", "2024-01-25", "done")
    gantt.add_task("Architecture", "2024-01-20", "2024-02-05", "active")
    
    gantt.add_section("Development")
    gantt.add_task("Backend API", "2024-02-01", "2024-03-15", "")
    gantt.add_task("Frontend UI", "2024-02-15", "2024-03-30", "")
    gantt.add_task("Database", "2024-02-01", "2024-02-20", "")
    
    gantt.add_section("Testing")
    gantt.add_task("Unit Tests", "2024-03-01", "2024-03-20", "")
    gantt.add_task("Integration Tests", "2024-03-15", "2024-04-05", "")
    gantt.add_task("User Testing", "2024-03-25", "2024-04-10", "")
    
    gantt.add_section("Deployment")
    gantt.add_task("Staging Deploy", "2024-04-01", "2024-04-05", "")
    gantt.add_task("Production Deploy", "2024-04-08", "2024-04-12", "")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "gantt_diagram.svg"
    renderer.save(gantt, output_path)
    print(f"Saved Gantt diagram to {output_path}")


def pie_chart_example(output_dir: Path):
    """Create a pie chart showing technology stack usage."""
    print("Creating pie chart example...")
    
    pie = PieChartDiagram(title="Technology Stack Distribution")
    
    # Add data segments
    pie.add_segment("Python", 35.5)
    pie.add_segment("JavaScript", 28.2)
    pie.add_segment("TypeScript", 15.8)
    pie.add_segment("Java", 12.1)
    pie.add_segment("Go", 5.4)
    pie.add_segment("Rust", 3.0)
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "pie_chart.svg"
    renderer.save(pie, output_path)
    print(f"Saved pie chart to {output_path}")


def git_graph_example(output_dir: Path):
    """Create a Git graph showing branching strategy."""
    print("Creating Git graph example...")
    
    git = GitGraphDiagram(title="Feature Development Git Flow")
    
    # Add commits and branches
    git.add_commit("main", "Initial commit")
    git.add_commit("main", "Add basic structure")
    
    git.create_branch("feature/auth", "main")
    git.add_commit("feature/auth", "Add authentication")
    git.add_commit("feature/auth", "Add user management")
    
    git.create_branch("feature/api", "main")
    git.add_commit("feature/api", "Add REST API")
    git.add_commit("feature/api", "Add validation")
    
    git.merge_branch("feature/auth", "main", "Merge auth feature")
    git.add_commit("main", "Update documentation")
    git.merge_branch("feature/api", "main", "Merge API feature")
    
    git.add_commit("main", "Release v1.0.0")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "git_graph.svg"
    renderer.save(git, output_path)
    print(f"Saved Git graph to {output_path}")


def mindmap_example(output_dir: Path):
    """Create a mindmap for project planning."""
    print("Creating mindmap example...")
    
    mindmap = MindmapDiagram(title="Project Planning Mindmap")
    
    # Add root and branches
    root = mindmap.add_root("Web Application")
    
    # Frontend branch
    frontend = mindmap.add_child(root, "Frontend")
    mindmap.add_child(frontend, "React")
    mindmap.add_child(frontend, "TypeScript")
    mindmap.add_child(frontend, "Tailwind CSS")
    
    # Backend branch
    backend = mindmap.add_child(root, "Backend")
    mindmap.add_child(backend, "Python")
    mindmap.add_child(backend, "FastAPI")
    mindmap.add_child(backend, "PostgreSQL")
    
    # DevOps branch
    devops = mindmap.add_child(root, "DevOps")
    mindmap.add_child(devops, "Docker")
    mindmap.add_child(devops, "Kubernetes")
    mindmap.add_child(devops, "CI/CD")
    
    # Testing branch
    testing = mindmap.add_child(root, "Testing")
    mindmap.add_child(testing, "Unit Tests")
    mindmap.add_child(testing, "Integration Tests")
    mindmap.add_child(testing, "E2E Tests")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "mindmap.svg"
    renderer.save(mindmap, output_path)
    print(f"Saved mindmap to {output_path}")


def main():
    """Run all diagram type examples."""
    print("=== Mermaid Render Diagram Types Showcase ===\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Run examples
    try:
        state_diagram_example(output_dir)
        print()
        
        er_diagram_example(output_dir)
        print()
        
        user_journey_example(output_dir)
        print()
        
        gantt_diagram_example(output_dir)
        print()
        
        pie_chart_example(output_dir)
        print()
        
        git_graph_example(output_dir)
        print()
        
        mindmap_example(output_dir)
        print()
        
        print("✅ All diagram type examples completed successfully!")
        print(f"Check the {output_dir} directory for generated diagrams.")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    main()
