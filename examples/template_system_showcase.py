#!/usr/bin/env python3
"""
Template system showcase for Mermaid Render.

This script demonstrates the template system including built-in templates,
custom template creation, and diagram generators for common patterns.
"""

from pathlib import Path
from typing import Any, cast

from diagramaid import MermaidRenderer

# Template system (optional imports with fallbacks)
TEMPLATES_AVAILABLE = False


# Define safe shims with correct types to avoid "possibly unbound"
class _Template:
    def __init__(
        self,
        name: str,
        diagram_type: str,
        template_content: str,
        parameters: dict[str, Any],
        description: str,
        author: str,
        tags: list[str],
    ):
        self.id = f"{name}"
        self.name = name
        self.diagram_type = diagram_type
        self.template_content = template_content
        self.parameters = parameters
        self.description = description
        self.author = author
        self.tags = tags


class _TemplateManagerShim:
    def create_template(
        self,
        name: str,
        diagram_type: str,
        template_content: str,
        parameters: dict[str, Any],
        description: str = "",
        author: str = "",
        tags: list[str] | None = None,
    ) -> _Template:
        return _Template(
            name=name,
            diagram_type=diagram_type,
            template_content=template_content,
            parameters=parameters,
            description=description,
            author=author,
            tags=tags or [],
        )

    def generate(self, template_id: str, params: dict[str, Any]) -> str:
        # Minimal Jinja-like replace for the demo; just return a basic sequenceDiagram using provided params
        title = params.get("title", "Untitled")
        participants = params.get("participants", [])
        endpoints = params.get("endpoints", [])
        lines = ["sequenceDiagram", f"    %% {title}", "    autonumber"]
        for p in participants:
            lines.append(f"    participant {p['id']} as {p['name']}")
        for e in endpoints:
            lines.append(f"    Note over {e['client']}, {e['server']}: {e['name']}")
            lines.append(
                f"    {e['client']}->>{e['server']}: {e['method']} {e['path']}"
            )
            if e.get("auth_required"):
                lines.append(
                    f"    {e['server']}->>{e['server']}: Validate Authentication"
                )
            if e.get("validation"):
                lines.append(f"    {e['server']}->>{e['server']}: Validate Request")
            lines.append(f"    {e['server']}->>{e['database']}: Query/Update Data")
            lines.append(f"    {e['database']}-->>{e['server']}: Result")
            lines.append(
                f"    {e['server']}-->>{e['client']}: {e['response_code']} Response"
            )
        return "\n".join(lines)


class _FlowchartGeneratorShim:
    def from_steps(
        self,
        steps: list[dict[str, Any]],
        title: str | None = None,
        direction: str = "TD",
    ) -> None:
        # Return a lightweight object with to_mermaid and add_edge
        class _Flow:
            def __init__(
                self, steps: list[dict[str, Any]], title: str | None, direction: str
            ):
                self.steps = steps
                self.title = title
                self.direction = direction
                self.edges: list[dict[str, str]] = []

            def add_edge(self, src: str, dst: str, label: str | None = None) -> None:
                self.edges.append({"from": src, "to": dst, "label": label or ""})

            def to_mermaid(self) -> str:
                lines = [f"flowchart {self.direction}"]
                if self.title:
                    lines.append(f"    %% {self.title}")
                for s in self.steps:
                    nid = s["id"]
                    lbl = s["label"]
                    typ = s.get("type", "process")
                    if typ in ("start", "end"):
                        lines.append(f"    {nid}(({lbl}))")
                    elif typ == "decision":
                        lines.append(f"    {nid}{{{lbl}}}")
                    else:
                        lines.append(f"    {nid}[{lbl}]")
                # default linear edges
                for i in range(len(self.steps) - 1):
                    lines.append(
                        f"    {self.steps[i]['id']} --> {self.steps[i+1]['id']}"
                    )
                # custom edges
                for e in self.edges:
                    if e["label"]:
                        lines.append(f"    {e['from']} -- {e['label']} --> {e['to']}")
                    else:
                        lines.append(f"    {e['from']} --> {e['to']}")
                return "\n".join(lines)

        return _Flow(steps, title, direction)


class _SequenceGeneratorShim:
    def from_interactions(
        self,
        interactions: list[dict[str, Any]],
        title: str | None = None,
        participants: dict[str, str] | None = None,
    ) -> None:
        lines = ["sequenceDiagram", "    autonumber"]
        if title:
            lines.append(f"    %% {title}")
        if participants:
            for pid, name in participants.items():
                lines.append(f"    participant {pid} as {name}")
        for it in interactions:
            t = it.get("type", "sync")
            if t == "return":
                lines.append(f"    {it['from']}-->>{it['to']}: {it['message']}")
            elif t == "self":
                lines.append(f"    {it['from']}->>{it['to']}: {it['message']}")
            else:
                lines.append(f"    {it['from']}->>{it['to']}: {it['message']}")
        return "\n".join(lines)


class _ArchitectureGeneratorShim:
    def from_components(
        self,
        components: dict[str, dict[str, Any]],
        connections: list[dict[str, str]],
        title: str | None = None,
    ) -> None:
        lines = ["flowchart TD"]
        if title:
            lines.append(f"    %% {title}")
        for cid, meta in components.items():
            label = meta.get("name", cid)
            lines.append(f"    {cid}[{label}]")
        for c in connections:
            lbl = f' -- {c["label"]} --> ' if c.get("label") else " --> "
            lines.append(f"    {c['from']}{lbl}{c['to']}")
        return "\n".join(lines)


# Try to import real modules
try:
    from diagramaid.templates import (
        ArchitectureGenerator as _ArchitectureGenerator,
    )
    from diagramaid.templates import (
        ClassDiagramGenerator as _ClassDiagramGenerator,  # noqa: F401
    )
    from diagramaid.templates import (
        FlowchartGenerator as _FlowchartGenerator,
    )
    from diagramaid.templates import (
        ProcessFlowGenerator as _ProcessFlowGenerator,  # noqa: F401
    )
    from diagramaid.templates import (
        SequenceGenerator as _SequenceGenerator,
    )
    from diagramaid.templates import (
        TemplateManager as _TemplateManager,
    )
    from diagramaid.templates import (
        generate_from_template as _generate_from_template,
    )
    from diagramaid.templates import (
        get_template_info as _get_template_info,
    )
    from diagramaid.templates import (
        list_available_templates as _list_available_templates,
    )

    TemplateManager = _TemplateManager
    FlowchartGenerator = _FlowchartGenerator
    SequenceGenerator = _SequenceGenerator
    ArchitectureGenerator = _ArchitectureGenerator
    generate_from_template = _generate_from_template

    # Normalize list_available_templates to return List[str] for this showcase
    def list_available_templates(
        template_manager: Any | None = None,
        diagram_type: str | None = None,
        tags: list[str] | None = None,
    ) -> list[str]:
        try:
            res: Any = _list_available_templates(
                template_manager=template_manager,
                diagram_type=diagram_type,
                tags=tags,
            )
        except TypeError:
            res = _list_available_templates()

        # If already a list of strings, cast for type checkers
        if isinstance(res, list) and all(isinstance(x, str) for x in res):
            return cast(list[str], res)

        names: list[str] = []
        if isinstance(res, list):
            for item in res:
                if isinstance(item, dict):
                    val = item.get("name") or item.get("id")
                    if isinstance(val, str):
                        names.append(val)
                        continue
                name_val = getattr(item, "name", None)
                if isinstance(name_val, str):
                    names.append(name_val)
                    continue
                id_val = getattr(item, "id", None)
                if isinstance(id_val, str):
                    names.append(id_val)
                    continue
                names.append(str(item))
        return names

    # Normalize get_template_info to a stable signature: (template_name: str) -> Dict[str, Any]
    def get_template_info(template_name: str) -> dict[str, Any]:
        try:
            info: Any = _get_template_info(template_name)
        except TypeError:
            info = _get_template_info(template_name)
        if isinstance(info, dict):
            return info
        # Fallback to minimal dict if underlying returns None or unexpected type
        return {"name": template_name}

    TEMPLATES_AVAILABLE = True
except ImportError:
    # Bind shims to avoid "possibly unbound"
    TemplateManager = _TemplateManagerShim
    FlowchartGenerator = _FlowchartGeneratorShim
    SequenceGenerator = _SequenceGeneratorShim
    ArchitectureGenerator = _ArchitectureGeneratorShim

    # Provide stubbed template listing APIs
    def _shim_list_available_templates(
        template_manager: Any | None = None,
        diagram_type: str | None = None,
        tags: list[str] | None = None,
    ) -> list[str]:
        # Shim ignores filters but keeps the same signature for type compatibility
        return ["basic_flowchart"]

    def _shim_get_template_info(template_name: str) -> dict[str, Any]:
        return {"name": template_name, "description": "Basic flowchart template (shim)"}

    def _shim_generate_from_template(
        template_name: str,
        parameters: dict[str, Any],
        template_manager: Any | None = None,
        validate_params: bool = True,
    ) -> str:
        if template_name != "basic_flowchart":
            raise ValueError("Unknown template in shim")
        # Very simple generator using parameters
        title = parameters.get("title", "Flowchart")
        steps = parameters.get("steps", [])
        conns = parameters.get("connections", [])
        lines = ["flowchart TD", f"    %% {title}"]
        for s in steps:
            typ = s.get("type", "process")
            nid = s["id"]
            lbl = s["label"]
            if typ in ("start", "end"):
                lines.append(f"    {nid}(({lbl}))")
            elif typ == "decision":
                lines.append(f"    {nid}{{{lbl}}}")
            else:
                lines.append(f"    {nid}[{lbl}]")
        for c in conns:
            if "label" in c and c["label"]:
                lines.append(f"    {c['from']} -- {c['label']} --> {c['to']}")
            else:
                lines.append(f"    {c['from']} --> {c['to']}")
        return "\n".join(lines)

    # Assign public API names from shims (avoid duplicate def names for type checkers)
    def list_available_templates(
        template_manager: Any | None = None,
        diagram_type: str | None = None,
        tags: list[str] | None = None,
    ) -> list[str]:
        # Pass-through; shim ignores filters but signature matches
        return _shim_list_available_templates(template_manager, diagram_type, tags)

    def get_template_info(template_name: str) -> dict[str, Any]:
        return _shim_get_template_info(template_name)

    def generate_from_template(
        template_name: str,
        parameters: dict[str, Any],
        template_manager: Any | None = None,
        validate_params: bool = True,
    ) -> str:
        return _shim_generate_from_template(
            template_name=template_name,
            parameters=parameters,
            template_manager=template_manager,
            validate_params=validate_params,
        )

    print(
        "⚠️  Template system not available. Install with: pip install diagramaid[templates]"
    )


def create_output_dir() -> Path:
    """Create output directory for examples."""
    output_dir = Path("output/templates")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _save_mermaid_code(renderer: MermaidRenderer, code: str, output_path: Path) -> None:
    """
    Save Mermaid code to file using available renderer API.
    Some versions expose save(diagram_obj, path) and render_raw(code, format),
    but not save_raw. Implement a safe saver for strings.
    """
    # Prefer render_raw + write to file
    fmt = output_path.suffix.lstrip(".").lower() or "svg"
    content = renderer.render_raw(code, format=fmt)
    # If bytes, write binary; else write text
    if isinstance(content, bytes):
        output_path.write_bytes(content)
    else:
        # Ensure content is a string for write_text
        output_path.write_text(str(content))


def built_in_templates_example(output_dir: Path) -> None:
    """Demonstrate using built-in templates."""
    if not TEMPLATES_AVAILABLE:
        print("Skipping built-in templates (templates not available)")
        return

    print("Built-in templates example...")

    try:
        # List available templates
        templates: list[str] = list_available_templates()
        print(f"📋 Available templates: {len(templates)}")

        for template_name in templates[:5]:  # Show first 5
            # Ensure we pass a str and handle missing info safely
            info = get_template_info(str(template_name))
            desc = info.get("description") if isinstance(info, dict) else None
            print(f"   - {template_name}: {desc or 'No description'}")

        # Use a built-in template
        if "basic_flowchart" in templates:
            diagram_code = generate_from_template(
                "basic_flowchart",
                {
                    "title": "User Registration Process",
                    "steps": [
                        {"id": "start", "label": "Start", "type": "start"},
                        {
                            "id": "form",
                            "label": "Fill Registration Form",
                            "type": "process",
                        },
                        {
                            "id": "validate",
                            "label": "Validate Input",
                            "type": "decision",
                        },
                        {"id": "save", "label": "Save User", "type": "process"},
                        {
                            "id": "email",
                            "label": "Send Welcome Email",
                            "type": "process",
                        },
                        {"id": "end", "label": "Complete", "type": "end"},
                    ],
                    "connections": [
                        {"from": "start", "to": "form"},
                        {"from": "form", "to": "validate"},
                        {"from": "validate", "to": "save", "label": "Valid"},
                        {"from": "validate", "to": "form", "label": "Invalid"},
                        {"from": "save", "to": "email"},
                        {"from": "email", "to": "end"},
                    ],
                },
            )

            # Save the generated diagram
            renderer = MermaidRenderer()
            output_path = output_dir / "template_flowchart.svg"
            _save_mermaid_code(renderer, diagram_code, output_path)
            print("✅ Generated flowchart from template")
            print(f"📁 Saved to {output_path}")

    except Exception as e:
        print(f"❌ Error with built-in templates: {e}")


def custom_template_creation_example(output_dir: Path) -> None:
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
                "title": {
                    "type": "string",
                    "required": True,
                    "description": "API documentation title",
                },
                "participants": {
                    "type": "array",
                    "required": True,
                    "description": "List of participants",
                },
                "endpoints": {
                    "type": "array",
                    "required": True,
                    "description": "List of API endpoints",
                },
            },
            description="Template for generating API documentation sequence diagrams",
            author="Example Author",
            tags=["api", "documentation", "sequence"],
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
                    {"id": "db", "name": "Database"},
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
                        "response_code": "201",
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
                        "response_code": "200",
                    },
                ],
            },
        )

        # Save the generated diagram
        renderer = MermaidRenderer()
        output_path = output_dir / "custom_template_api.svg"
        _save_mermaid_code(renderer, diagram_code, output_path)
        print(f"📁 Generated API documentation saved to {output_path}")

    except Exception as e:
        print(f"❌ Error with custom template: {e}")


def flowchart_generator_example(output_dir: Path) -> None:
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
            {"id": "reject", "label": "Reject Order", "type": "end"},
        ]

        # Convert steps to the format expected by FlowchartGenerator.generate()
        nodes = []
        for step in process_steps:
            step_type = step.get("type", "process")
            if step_type in ("start", "end"):
                shape = "circle"
            elif step_type == "decision":
                shape = "diamond"
            else:
                shape = "rectangle"

            nodes.append({"id": step["id"], "label": step["label"], "shape": shape})

        # Create edges for linear flow and decision branches
        edges = []
        for i in range(len(process_steps) - 1):
            from_id = process_steps[i]["id"]
            to_id = process_steps[i + 1]["id"]
            # Skip the default edge from validate to inventory since we'll add custom ones
            if from_id == "validate" and to_id == "inventory":
                continue
            edges.append({"from": from_id, "to": to_id})

        # Add decision edges
        edges.extend(
            [
                {"from": "validate", "to": "inventory", "label": "Valid"},
                {"from": "validate", "to": "reject", "label": "Invalid"},
            ]
        )

        flowchart_data = {
            "title": "Order Processing Workflow",
            "direction": "TD",
            "nodes": nodes,
            "edges": edges,
        }

        # Use the appropriate method based on what's available
        if TEMPLATES_AVAILABLE:
            # Real FlowchartGenerator with generate method
            diagram_code = generator.generate(flowchart_data)
        else:
            # Shim with from_steps method - fallback to manual generation
            lines = [f"flowchart {flowchart_data['direction']}"]
            if flowchart_data.get("title"):
                lines.append(f"    %% {flowchart_data['title']}")

            # Add nodes
            for node in nodes:
                node_id = node["id"]
                label = node["label"]
                shape = node["shape"]
                if shape == "circle":
                    lines.append(f"    {node_id}(({label}))")
                elif shape == "diamond":
                    lines.append(f"    {node_id}{{{label}}}")
                else:
                    lines.append(f"    {node_id}[{label}]")

            # Add edges
            for edge in edges:
                if edge.get("label"):
                    lines.append(
                        f"    {edge['from']} -- {edge['label']} --> {edge['to']}"
                    )
                else:
                    lines.append(f"    {edge['from']} --> {edge['to']}")

            diagram_code = "\n".join(lines)

        # Save the generated flowchart
        renderer = MermaidRenderer()
        output_path = output_dir / "generated_flowchart.svg"
        _save_mermaid_code(renderer, diagram_code, output_path)
        print("✅ Generated flowchart from steps")
        print(f"📁 Saved to {output_path}")

    except Exception as e:
        print(f"❌ Error with flowchart generator: {e}")


def sequence_generator_example(output_dir: Path) -> None:
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
                "type": "sync",
            },
            {
                "from": "frontend",
                "to": "backend",
                "message": "POST /auth/login",
                "type": "sync",
            },
            {
                "from": "backend",
                "to": "database",
                "message": "SELECT user WHERE email = ?",
                "type": "sync",
            },
            {
                "from": "database",
                "to": "backend",
                "message": "User data",
                "type": "return",
            },
            {
                "from": "backend",
                "to": "backend",
                "message": "Verify password",
                "type": "self",
            },
            {
                "from": "backend",
                "to": "frontend",
                "message": "JWT token",
                "type": "return",
            },
            {
                "from": "frontend",
                "to": "user",
                "message": "Redirect to dashboard",
                "type": "return",
            },
        ]

        # Convert interactions to the format expected by SequenceGenerator.generate()
        participants = [
            {"id": "user", "name": "User"},
            {"id": "frontend", "name": "Frontend App"},
            {"id": "backend", "name": "Backend API"},
            {"id": "database", "name": "Database"},
        ]

        messages = []
        for interaction in interactions:
            msg_type = interaction.get("type", "sync")
            if msg_type == "return":
                arrow_type = "return"
            elif msg_type == "self":
                arrow_type = "sync"  # Self messages use sync arrows
            else:
                arrow_type = "sync"

            messages.append(
                {
                    "from": interaction["from"],
                    "to": interaction["to"],
                    "message": interaction["message"],
                    "type": arrow_type,
                }
            )

        sequence_data = {
            "title": "User Login Sequence",
            "participants": participants,
            "messages": messages,
        }

        # Use the appropriate method based on what's available
        if TEMPLATES_AVAILABLE:
            # Real SequenceGenerator with generate method
            diagram_code = generator.generate(sequence_data)
        else:
            # Shim with from_interactions method - fallback to manual generation
            lines = ["sequenceDiagram", "    autonumber"]
            lines.append(f"    %% {sequence_data['title']}")

            # Add participants
            for participant in participants:
                lines.append(
                    f"    participant {participant['id']} as {participant['name']}"
                )

            # Add messages
            for msg in messages:
                if msg["type"] == "return":
                    lines.append(f"    {msg['from']}-->>{msg['to']}: {msg['message']}")
                elif msg["from"] == msg["to"]:  # Self message
                    lines.append(f"    {msg['from']}->>{msg['to']}: {msg['message']}")
                else:
                    lines.append(f"    {msg['from']}->>{msg['to']}: {msg['message']}")

            diagram_code = "\n".join(lines)

        # Save the generated sequence diagram
        renderer = MermaidRenderer()
        output_path = output_dir / "generated_sequence.svg"
        _save_mermaid_code(renderer, diagram_code, output_path)
        print("✅ Generated sequence diagram from interactions")
        print(f"📁 Saved to {output_path}")

    except Exception as e:
        print(f"❌ Error with sequence generator: {e}")


def architecture_generator_example(output_dir: Path) -> None:
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
                "technologies": ["React", "TypeScript", "Tailwind"],
            },
            "api_gateway": {
                "name": "API Gateway",
                "type": "gateway",
                "technologies": ["Kong", "Rate Limiting"],
            },
            "auth_service": {
                "name": "Authentication Service",
                "type": "service",
                "technologies": ["Node.js", "JWT"],
            },
            "user_service": {
                "name": "User Service",
                "type": "service",
                "technologies": ["Python", "FastAPI"],
            },
            "database": {
                "name": "PostgreSQL",
                "type": "database",
                "technologies": ["PostgreSQL", "Connection Pool"],
            },
            "cache": {
                "name": "Redis Cache",
                "type": "cache",
                "technologies": ["Redis", "Clustering"],
            },
        }

        connections = [
            {"from": "frontend", "to": "api_gateway", "label": "HTTPS"},
            {"from": "api_gateway", "to": "auth_service", "label": "Auth"},
            {"from": "api_gateway", "to": "user_service", "label": "API Calls"},
            {"from": "auth_service", "to": "cache", "label": "Session Store"},
            {"from": "user_service", "to": "database", "label": "SQL"},
            {"from": "user_service", "to": "cache", "label": "Caching"},
        ]

        # Convert components dict to the format expected by ArchitectureGenerator.generate()
        components_array = []
        for comp_id, comp_data in components.items():
            comp_type = comp_data.get("type", "service")
            # Map component types to the expected values
            if comp_type in ("client", "gateway"):
                comp_type = "external"
            elif comp_type == "cache":
                comp_type = "database"  # Treat cache as database type

            components_array.append(
                {"id": comp_id, "name": comp_data["name"], "type": comp_type}
            )

        architecture_data = {
            "title": "Microservices Architecture",
            "direction": "TD",
            "components": components_array,
            "connections": connections,
        }

        # Use the appropriate method based on what's available
        if TEMPLATES_AVAILABLE:
            # Real ArchitectureGenerator with generate method
            diagram_code = generator.generate(architecture_data)
        else:
            # Shim with from_components method - fallback to manual generation
            lines = ["flowchart TD"]
            lines.append(f"    %% {architecture_data['title']}")

            # Add components
            for comp in components_array:
                comp_id = comp["id"]
                comp_name = comp["name"]
                lines.append(f"    {comp_id}[{comp_name}]")

            # Add connections
            for conn in connections:
                if conn.get("label"):
                    lines.append(
                        f"    {conn['from']} -- {conn['label']} --> {conn['to']}"
                    )
                else:
                    lines.append(f"    {conn['from']} --> {conn['to']}")

            diagram_code = "\n".join(lines)

        # Save the generated architecture diagram
        renderer = MermaidRenderer()
        output_path = output_dir / "generated_architecture.svg"
        _save_mermaid_code(renderer, diagram_code, output_path)
        print("✅ Generated architecture diagram")
        print(f"📁 Saved to {output_path}")

    except Exception as e:
        print(f"❌ Error with architecture generator: {e}")


def main() -> None:
    """Run all template system examples."""
    print("=== Mermaid Render Template System Showcase ===\n")

    if not TEMPLATES_AVAILABLE:
        print("⚠️  Template system requires additional dependencies.")
        print("Install with: pip install diagramaid[templates]\n")

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
            print(
                "ℹ️  Template examples ran with local shims (install extras for full features)."
            )
        print(f"Check the {output_dir} directory for generated diagrams.")

    except Exception as e:
        print(f"❌ Error running template examples: {e}")
        raise


if __name__ == "__main__":
    main()
