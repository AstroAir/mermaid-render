#!/usr/bin/env python3
"""
Comprehensive showcase of all diagram types supported by Mermaid Render.

This script demonstrates all available diagram types with practical examples
that show real-world use cases for each type.
"""

from pathlib import Path
from typing import List
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


def create_output_dir() -> Path:
    """Create output directory for examples."""
    output_dir = Path("output/diagram_types")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def state_diagram_example(output_dir: Path) -> None:
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


def er_diagram_example(output_dir: Path) -> None:
    """Create an ER diagram for an e-commerce database."""
    print("Creating ER diagram example...")

    er = ERDiagram()  # ER diagrams don't support titles in Mermaid
    
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
    er.add_relationship("User", "Order", "||--o{")
    er.add_relationship("Order", "OrderItem", "||--o{")
    er.add_relationship("Product", "OrderItem", "||--o{")
    er.add_relationship("Category", "Product", "||--o{")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "er_diagram.svg"
    renderer.save(er, output_path)
    print(f"Saved ER diagram to {output_path}")


def user_journey_example(output_dir: Path) -> None:
    """Create a user journey diagram for online shopping."""
    print("Creating user journey diagram example...")
    
    journey = UserJourneyDiagram(title="Online Shopping User Journey")
    
    # Add journey sections and tasks
    journey.add_section("Discovery")
    journey.add_task("User discovers product", ["Browsing", "Search"], 3)

    journey.add_section("Research")
    journey.add_task("User researches product", ["Reviews", "Comparison"], 4)

    journey.add_section("Decision")
    journey.add_task("User decides to purchase", ["Add to Cart"], 5)

    journey.add_section("Checkout")
    journey.add_task("User completes purchase", ["Payment", "Shipping"], 2)

    journey.add_section("Delivery")
    journey.add_task("User receives product", ["Tracking", "Unboxing"], 5)

    journey.add_section("Support")
    journey.add_task("User contacts support", ["Help", "Returns"], 1)
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "user_journey.svg"
    renderer.save(journey, output_path)
    print(f"Saved user journey diagram to {output_path}")


def gantt_diagram_example(output_dir: Path) -> None:
    """Create a Gantt chart for a software development project."""
    print("Creating Gantt diagram example...")
    
    gantt = GanttDiagram(title="Software Development Project Timeline")
    
    # Add sections and tasks
    gantt.add_section("Planning")
    gantt.add_task("Requirements", "2024-01-01", "15d", "done")
    gantt.add_task("Design", "2024-01-10", "15d", "done")
    gantt.add_task("Architecture", "2024-01-20", "16d", "active")

    gantt.add_section("Development")
    gantt.add_task("Backend API", "2024-02-01", "43d", "")
    gantt.add_task("Frontend UI", "2024-02-15", "43d", "")
    gantt.add_task("Database", "2024-02-01", "19d", "")

    gantt.add_section("Testing")
    gantt.add_task("Unit Tests", "2024-03-01", "19d", "")
    gantt.add_task("Integration Tests", "2024-03-15", "21d", "")
    gantt.add_task("User Testing", "2024-03-25", "16d", "")

    gantt.add_section("Deployment")
    gantt.add_task("Staging Deploy", "2024-04-01", "4d", "")
    gantt.add_task("Production Deploy", "2024-04-08", "4d", "")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "gantt_diagram.svg"
    renderer.save(gantt, output_path)
    print(f"Saved Gantt diagram to {output_path}")


def pie_chart_example(output_dir: Path) -> None:
    """Create a pie chart showing technology stack usage."""
    print("Creating pie chart example...")
    
    pie = PieChartDiagram(title="Technology Stack Distribution")
    
    # Add data slices
    pie.add_slice("Python", 35.5)
    pie.add_slice("JavaScript", 28.2)
    pie.add_slice("TypeScript", 15.8)
    pie.add_slice("Java", 12.1)
    pie.add_slice("Go", 5.4)
    pie.add_slice("Rust", 3.0)
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "pie_chart.svg"
    renderer.save(pie, output_path)
    print(f"Saved pie chart to {output_path}")


def git_graph_example(output_dir: Path) -> None:
    """Create a Git graph showing branching strategy."""
    print("Creating Git graph example...")
    
    git = GitGraphDiagram(title="Feature Development Git Flow")
    
    # Add commits and branches
    git.add_commit("Initial commit", "main")
    git.add_commit("Add basic structure", "main")

    git.add_branch("feature/auth")
    git.add_commit("Add authentication", "feature/auth")
    git.add_commit("Add user management", "feature/auth")

    git.add_branch("feature/api")
    git.add_commit("Add REST API", "feature/api")
    git.add_commit("Add validation", "feature/api")

    git.add_merge("feature/auth", "main")
    git.add_commit("Update documentation", "main")
    git.add_merge("feature/api", "main")

    git.add_commit("Release v1.0.0", "main")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "git_graph.svg"
    renderer.save(git, output_path)
    print(f"Saved Git graph to {output_path}")


def mindmap_example(output_dir: Path) -> None:
    """Create a mindmap for project planning."""
    print("Creating mindmap example...")
    
    mindmap = MindmapDiagram(title="Project Planning Mindmap", root_text="Web Application")

    # Add main branches
    mindmap.add_node("root", "frontend", "Frontend")
    mindmap.add_node("root", "backend", "Backend")
    mindmap.add_node("root", "devops", "DevOps")
    mindmap.add_node("root", "testing", "Testing")

    # Frontend technologies
    mindmap.add_node("frontend", "react", "React")
    mindmap.add_node("frontend", "typescript", "TypeScript")
    mindmap.add_node("frontend", "tailwind", "Tailwind CSS")

    # Backend technologies
    mindmap.add_node("backend", "python", "Python")
    mindmap.add_node("backend", "fastapi", "FastAPI")
    mindmap.add_node("backend", "postgresql", "PostgreSQL")

    # DevOps tools
    mindmap.add_node("devops", "docker", "Docker")
    mindmap.add_node("devops", "kubernetes", "Kubernetes")
    mindmap.add_node("devops", "cicd", "CI/CD")

    # Testing types
    mindmap.add_node("testing", "unit", "Unit Tests")
    mindmap.add_node("testing", "integration", "Integration Tests")
    mindmap.add_node("testing", "e2e", "E2E Tests")
    
    # Render and save
    renderer = MermaidRenderer()
    output_path = output_dir / "mindmap.svg"
    renderer.save(mindmap, output_path)
    print(f"Saved mindmap to {output_path}")


def main() -> None:
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
