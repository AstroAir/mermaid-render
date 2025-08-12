# Diagram Types

Mermaid Render supports all major Mermaid diagram types with comprehensive Python APIs. This guide covers each diagram type with practical examples and best practices.

## Overview

| Diagram Type     | Use Case                         | Complexity | Python Class         |
| ---------------- | -------------------------------- | ---------- | -------------------- |
| **Flowchart**    | Process flows, workflows         | ⭐⭐       | `FlowchartDiagram`   |
| **Sequence**     | API interactions, communications | ⭐⭐⭐     | `SequenceDiagram`    |
| **Class**        | System architecture, OOP design  | ⭐⭐⭐⭐   | `ClassDiagram`       |
| **State**        | State machines, lifecycles       | ⭐⭐⭐     | `StateDiagram`       |
| **ER**           | Database design, relationships   | ⭐⭐⭐     | `ERDiagram`          |
| **User Journey** | UX flows, customer journeys      | ⭐⭐       | `UserJourneyDiagram` |
| **Gantt**        | Project timelines, scheduling    | ⭐⭐       | `GanttDiagram`       |
| **Pie Chart**    | Data visualization               | ⭐         | `PieChartDiagram`    |
| **Git Graph**    | Version control flows            | ⭐⭐       | `GitGraphDiagram`    |
| **Mindmap**      | Hierarchical information         | ⭐⭐       | `MindmapDiagram`     |

## Flowchart Diagrams

Perfect for visualizing processes, decision trees, and workflows.

```python
from mermaid_render import FlowchartDiagram, MermaidRenderer

# Create a business process flow
process = FlowchartDiagram(title="Order Processing", direction="TD")

# Add process steps
process.add_node("start", "Order Received", shape="circle")
process.add_node("validate", "Validate Order", shape="rectangle")
process.add_node("check_stock", "Stock Available?", shape="diamond")
process.add_node("fulfill", "Fulfill Order", shape="rectangle")
process.add_node("backorder", "Create Backorder", shape="rectangle")
process.add_node("notify", "Notify Customer", shape="rectangle")
process.add_node("end", "Complete", shape="circle")

# Connect the flow
process.add_edge("start", "validate")
process.add_edge("validate", "check_stock")
process.add_edge("check_stock", "fulfill", label="Yes")
process.add_edge("check_stock", "backorder", label="No")
process.add_edge("fulfill", "notify")
process.add_edge("backorder", "notify")
process.add_edge("notify", "end")

# Render
renderer = MermaidRenderer(theme="neutral")
renderer.save(process, "order_process.svg")
```

**Best Practices:**

- Use descriptive node labels
- Choose appropriate shapes (diamond for decisions, circle for start/end)
- Keep flows top-to-bottom or left-to-right for readability
- Group related processes in subgraphs

## Sequence Diagrams

Ideal for documenting API interactions, system communications, and time-based processes.

```python
from mermaid_render import SequenceDiagram

# Create an authentication flow
auth_flow = SequenceDiagram(title="OAuth 2.0 Flow", autonumber=True)

# Add participants
auth_flow.add_participant("user", "User")
auth_flow.add_participant("client", "Client App")
auth_flow.add_participant("auth", "Auth Server")
auth_flow.add_participant("resource", "Resource Server")

# Document the flow
auth_flow.add_message("user", "client", "Request protected resource")
auth_flow.add_message("client", "auth", "Redirect to authorization")
auth_flow.add_message("user", "auth", "Login credentials")
auth_flow.add_message("auth", "client", "Authorization code")
auth_flow.add_message("client", "auth", "Exchange code for token")
auth_flow.add_message("auth", "client", "Access token", message_type="return")
auth_flow.add_message("client", "resource", "API request + token")
auth_flow.add_message("resource", "client", "Protected data", message_type="return")

renderer = MermaidRenderer(theme="dark")
renderer.save(auth_flow, "oauth_flow.png", format="png")
```

**Best Practices:**

- Use clear, descriptive message names
- Include return messages for completeness
- Use activation boxes for long-running processes
- Number messages for complex flows

## Class Diagrams

Essential for documenting system architecture and object-oriented designs.

```python
from mermaid_render import ClassDiagram
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute

# Create a system architecture diagram
system = ClassDiagram(title="E-commerce System")

# Define User class
user = system.add_class("User")
user.add_attribute(ClassAttribute("id", "UUID", "private"))
user.add_attribute(ClassAttribute("email", "String", "private"))
user.add_method(ClassMethod("authenticate", "public", "boolean"))
user.add_method(ClassMethod("getProfile", "public", "UserProfile"))

# Define Order class
order = system.add_class("Order")
order.add_attribute(ClassAttribute("id", "UUID", "private"))
order.add_attribute(ClassAttribute("items", "List<OrderItem>", "private"))
order.add_method(ClassMethod("calculateTotal", "public", "Money"))
order.add_method(ClassMethod("addItem", "public", "void"))

# Define relationships
system.add_relationship("User", "Order", "one_to_many")

renderer = MermaidRenderer(theme="forest")
renderer.save(system, "system_architecture.pdf", format="pdf")
```

**Best Practices:**

- Include key attributes and methods only
- Use appropriate visibility modifiers
- Show important relationships clearly
- Group related classes together

## State Diagrams

Perfect for modeling state machines, user interface states, and business process states.

```python
from mermaid_render import StateDiagram

# Model user session states
session = StateDiagram(title="User Session Lifecycle")

# Define states
session.add_state("idle", "Idle")
session.add_state("authenticating", "Authenticating")
session.add_state("active", "Active Session")
session.add_state("expired", "Session Expired")
session.add_state("locked", "Account Locked")

# Define transitions
session.add_transition("idle", "authenticating", "login_attempt")
session.add_transition("authenticating", "active", "success")
session.add_transition("authenticating", "locked", "too_many_failures")
session.add_transition("active", "expired", "timeout")
session.add_transition("active", "idle", "logout")
session.add_transition("expired", "idle", "cleanup")
session.add_transition("locked", "idle", "unlock")

# Set initial state
session.set_initial_state("idle")

renderer = MermaidRenderer()
renderer.save(session, "session_states.svg")
```

**Best Practices:**

- Use clear state names
- Include all important transitions
- Consider error and edge cases
- Document trigger conditions

## Choosing the Right Diagram Type

### Decision Matrix

| Need to Show        | Best Diagram Type | Alternative  |
| ------------------- | ----------------- | ------------ |
| Process flow        | Flowchart         | User Journey |
| System interactions | Sequence          | Class        |
| Data relationships  | ER                | Class        |
| State changes       | State             | Flowchart    |
| System architecture | Class             | Flowchart    |
| Project timeline    | Gantt             | User Journey |
| Hierarchical data   | Mindmap           | Flowchart    |
| Version control     | Git Graph         | Flowchart    |

### Common Patterns

**Documentation Workflow:**

1. Start with Flowchart for overall process
2. Use Sequence for detailed interactions
3. Add Class diagrams for system structure
4. Include State diagrams for complex logic

**System Design:**

1. Class diagrams for architecture
2. Sequence diagrams for key scenarios
3. State diagrams for complex components
4. ER diagrams for data models

## Advanced Features

### Subgraphs and Grouping

```python
# Group related nodes in flowcharts
flowchart.add_subgraph("validation", "Input Validation", [
    "check_format", "validate_data", "sanitize_input"
])
```

### Styling and Themes

```python
# Apply custom styling
custom_style = {
    "fill": "#e1f5fe",
    "stroke": "#01579b",
    "stroke-width": "2px"
}
flowchart.add_node("important", "Critical Step", style=custom_style)
```

### Complex Relationships

```python
# Multiple relationship types in class diagrams
system.add_relationship("Order", "Customer", "belongs_to")
system.add_relationship("Order", "OrderItem", "has_many")
system.add_relationship("OrderItem", "Product", "references")
```

## Next Steps

- Explore [Examples](../examples/) for real-world usage patterns
- Learn about [Themes](themes.md) for consistent styling
- Check [Rendering](rendering.md) for output options
- Review [API Reference](../api-reference/) for complete documentation
