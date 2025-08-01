"""
Specialized diagram generators for common patterns.

This module provides high-level generators that create diagrams
from structured data without requiring template knowledge.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class DiagramGenerator(ABC):
    """Base class for diagram generators."""

    @abstractmethod
    def generate(self, data: Dict[str, Any], **options) -> str:
        """Generate diagram from structured data."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get data schema for this generator."""
        pass


class FlowchartGenerator(DiagramGenerator):
    """
    Generator for flowchart diagrams from structured data.

    Creates flowcharts from node and edge definitions with
    automatic styling and layout optimization.
    """

    def generate(self, data: Dict[str, Any], **options) -> str:
        """
        Generate flowchart from structured data.

        Args:
            data: Flowchart data with nodes and edges
            **options: Additional generation options

        Returns:
            Generated Mermaid flowchart code
        """
        direction = data.get("direction", "TD")
        title = data.get("title", "")
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        styling = data.get("styling", {})

        # Start building the flowchart
        lines = [f"flowchart {direction}"]

        if title:
            lines.append(f"    %% {title}")
            lines.append("")

        # Add nodes
        for node in nodes:
            node_id = node["id"]
            label = node.get("label", node_id)
            shape = node.get("shape", "rectangle")

            # Map shape to Mermaid syntax
            shape_map = {
                "rectangle": f"{node_id}[{label}]",
                "rounded": f"{node_id}({label})",
                "circle": f"{node_id}(({label}))",
                "diamond": f"{node_id}{{{label}}}",
                "hexagon": f"{node_id}{{{{{label}}}}}",
                "stadium": f"{node_id}([{label}])",
                "subroutine": f"{node_id}[[{label}]]",
                "cylinder": f"{node_id}[({label})]",
            }

            node_syntax = shape_map.get(shape, f"{node_id}[{label}]")
            lines.append(f"    {node_syntax}")

        lines.append("")

        # Add edges
        for edge in edges:
            from_node = edge["from"]
            to_node = edge["to"]
            label = edge.get("label", "")
            style = edge.get("style", "solid")

            # Map style to Mermaid syntax
            style_map = {
                "solid": "-->",
                "dotted": "-.-",
                "thick": "==>",
                "invisible": "~~~",
            }

            arrow = style_map.get(style, "-->")

            if label:
                lines.append(f"    {from_node} {arrow}|{label}| {to_node}")
            else:
                lines.append(f"    {from_node} {arrow} {to_node}")

        # Add styling
        if styling:
            lines.append("")
            lines.append("    %% Styling")

            # Class definitions
            for class_name, class_style in styling.get("classes", {}).items():
                style_parts = []
                if "fill" in class_style:
                    style_parts.append(f"fill:{class_style['fill']}")
                if "stroke" in class_style:
                    style_parts.append(f"stroke:{class_style['stroke']}")
                if "stroke_width" in class_style:
                    style_parts.append(f"stroke-width:{class_style['stroke_width']}")

                if style_parts:
                    style_str = ",".join(style_parts)
                    lines.append(f"    classDef {class_name} {style_str}")

            # Apply classes to nodes
            for node_id, class_name in styling.get("node_classes", {}).items():
                lines.append(f"    class {node_id} {class_name}")

        return "\n".join(lines)

    def get_schema(self) -> Dict[str, Any]:
        """Get data schema for flowchart generation."""
        return {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["TD", "TB", "BT", "RL", "LR"],
                    "default": "TD",
                    "description": "Flowchart direction",
                },
                "title": {"type": "string", "description": "Optional flowchart title"},
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Node identifier"},
                            "label": {"type": "string", "description": "Node label"},
                            "shape": {
                                "type": "string",
                                "enum": [
                                    "rectangle",
                                    "rounded",
                                    "circle",
                                    "diamond",
                                    "hexagon",
                                    "stadium",
                                    "subroutine",
                                    "cylinder",
                                ],
                                "default": "rectangle",
                            },
                        },
                        "required": ["id"],
                    },
                    "minItems": 1,
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string", "description": "Source node ID"},
                            "to": {"type": "string", "description": "Target node ID"},
                            "label": {"type": "string", "description": "Edge label"},
                            "style": {
                                "type": "string",
                                "enum": ["solid", "dotted", "thick", "invisible"],
                                "default": "solid",
                            },
                        },
                        "required": ["from", "to"],
                    },
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "classes": {
                            "type": "object",
                            "description": "CSS class definitions",
                        },
                        "node_classes": {
                            "type": "object",
                            "description": "Node to class mappings",
                        },
                    },
                },
            },
            "required": ["nodes"],
        }


class SequenceGenerator(DiagramGenerator):
    """
    Generator for sequence diagrams from interaction data.

    Creates sequence diagrams from participant and message definitions
    with automatic lifeline management.
    """

    def generate(self, data: Dict[str, Any], **options) -> str:
        """
        Generate sequence diagram from structured data.

        Args:
            data: Sequence data with participants and messages
            **options: Additional generation options

        Returns:
            Generated Mermaid sequence diagram code
        """
        title = data.get("title", "")
        participants = data.get("participants", [])
        messages = data.get("messages", [])
        notes = data.get("notes", [])

        lines = ["sequenceDiagram"]

        if title:
            lines.append(f"    title {title}")
            lines.append("")

        # Add participants
        for participant in participants:
            if isinstance(participant, dict):
                pid = participant["id"]
                name = participant.get("name", pid)
                lines.append(f"    participant {pid} as {name}")
            else:
                lines.append(f"    participant {participant}")

        lines.append("")

        # Add messages and notes
        for item in messages:
            if item.get("type") == "note":
                participant = item["participant"]
                message = item["message"]
                lines.append(f"    Note over {participant}: {message}")
            elif item.get("type") == "activate":
                participant = item["participant"]
                lines.append(f"    activate {participant}")
            elif item.get("type") == "deactivate":
                participant = item["participant"]
                lines.append(f"    deactivate {participant}")
            else:
                from_p = item["from"]
                to_p = item["to"]
                message = item["message"]
                msg_type = item.get("type", "sync")

                # Map message types to arrows
                arrow_map = {
                    "sync": "->>",
                    "async": "->",
                    "return": "-->>",
                    "callback": "-->",
                }

                arrow = arrow_map.get(msg_type, "->>")
                lines.append(f"    {from_p}{arrow}{to_p}: {message}")

        return "\n".join(lines)

    def get_schema(self) -> Dict[str, Any]:
        """Get data schema for sequence generation."""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Sequence diagram title"},
                "participants": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                },
                                "required": ["id"],
                            },
                        ]
                    },
                    "minItems": 2,
                },
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "message": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "sync",
                                    "async",
                                    "return",
                                    "callback",
                                    "note",
                                    "activate",
                                    "deactivate",
                                ],
                                "default": "sync",
                            },
                            "participant": {
                                "type": "string",
                                "description": "For note, activate, deactivate types",
                            },
                        },
                    },
                },
            },
            "required": ["participants", "messages"],
        }


class ClassDiagramGenerator(DiagramGenerator):
    """
    Generator for class diagrams from object-oriented design data.

    Creates UML class diagrams from class definitions with
    attributes, methods, and relationships.
    """

    def generate(self, data: Dict[str, Any], **options) -> str:
        """
        Generate class diagram from structured data.

        Args:
            data: Class diagram data with classes and relationships
            **options: Additional generation options

        Returns:
            Generated Mermaid class diagram code
        """
        title = data.get("title", "")
        classes = data.get("classes", [])
        relationships = data.get("relationships", [])

        lines = ["classDiagram"]

        if title:
            lines.append(f"    %% {title}")
            lines.append("")

        # Add classes
        for cls in classes:
            class_name = cls["name"]
            lines.append(f"    class {class_name} {{")

            # Add attributes
            for attr in cls.get("attributes", []):
                visibility = attr.get("visibility", "+")
                name = attr["name"]
                attr_type = attr.get("type", "")

                if attr_type:
                    lines.append(f"        {visibility}{name}: {attr_type}")
                else:
                    lines.append(f"        {visibility}{name}")

            # Add methods
            for method in cls.get("methods", []):
                visibility = method.get("visibility", "+")
                name = method["name"]
                params = method.get("parameters", [])
                return_type = method.get("return_type", "")

                param_str = ", ".join(params) if params else ""

                if return_type:
                    lines.append(
                        f"        {visibility}{name}({param_str}): {return_type}"
                    )
                else:
                    lines.append(f"        {visibility}{name}({param_str})")

            lines.append("    }")

            # Add stereotypes
            if cls.get("abstract"):
                lines.append(f"    <<abstract>> {class_name}")
            if cls.get("interface"):
                lines.append(f"    <<interface>> {class_name}")

            lines.append("")

        # Add relationships
        for rel in relationships:
            from_class = rel["from"]
            to_class = rel["to"]
            rel_type = rel.get("type", "association")
            label = rel.get("label", "")

            # Map relationship types to Mermaid syntax
            rel_map = {
                "inheritance": "--|>",
                "composition": "*--",
                "aggregation": "o--",
                "association": "--",
                "dependency": "..>",
                "realization": "..|>",
            }

            arrow = rel_map.get(rel_type, "--")

            if label:
                lines.append(f"    {from_class} {arrow} {to_class} : {label}")
            else:
                lines.append(f"    {from_class} {arrow} {to_class}")

        return "\n".join(lines)

    def get_schema(self) -> Dict[str, Any]:
        """Get data schema for class diagram generation."""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Class diagram title"},
                "classes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Class name"},
                            "abstract": {"type": "boolean", "default": False},
                            "interface": {"type": "boolean", "default": False},
                            "attributes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "visibility": {
                                            "type": "string",
                                            "enum": ["+", "-", "#", "~"],
                                            "default": "+",
                                        },
                                    },
                                    "required": ["name"],
                                },
                            },
                            "methods": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "parameters": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                        "return_type": {"type": "string"},
                                        "visibility": {
                                            "type": "string",
                                            "enum": ["+", "-", "#", "~"],
                                            "default": "+",
                                        },
                                    },
                                    "required": ["name"],
                                },
                            },
                        },
                        "required": ["name"],
                    },
                    "minItems": 1,
                },
                "relationships": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "inheritance",
                                    "composition",
                                    "aggregation",
                                    "association",
                                    "dependency",
                                    "realization",
                                ],
                                "default": "association",
                            },
                            "label": {"type": "string"},
                        },
                        "required": ["from", "to"],
                    },
                },
            },
            "required": ["classes"],
        }


class ArchitectureGenerator(DiagramGenerator):
    """
    Generator for software architecture diagrams.

    Creates high-level architecture diagrams showing
    system components and their interactions.
    """

    def generate(self, data: Dict[str, Any], **options) -> str:
        """Generate architecture diagram from structured data."""
        # Use flowchart generator with architecture-specific styling
        flowchart_data = {
            "direction": data.get("direction", "TD"),
            "title": data.get("title", ""),
            "nodes": [],
            "edges": data.get("connections", []),
            "styling": {
                "classes": {
                    "service": {
                        "fill": "#e1f5fe",
                        "stroke": "#01579b",
                        "stroke_width": "2px",
                    },
                    "database": {
                        "fill": "#f3e5f5",
                        "stroke": "#4a148c",
                        "stroke_width": "2px",
                    },
                    "external": {
                        "fill": "#fff3e0",
                        "stroke": "#ef6c00",
                        "stroke_width": "2px",
                    },
                },
                "node_classes": {},
            },
        }

        # Process components
        for component in data.get("components", []):
            comp_type = component.get("type", "service")
            shape = "cylinder" if comp_type == "database" else "rectangle"

            node = {"id": component["id"], "label": component["name"], "shape": shape}

            flowchart_data["nodes"].append(node)
            flowchart_data["styling"]["node_classes"][component["id"]] = comp_type

        generator = FlowchartGenerator()
        return generator.generate(flowchart_data)

    def get_schema(self) -> Dict[str, Any]:
        """Get data schema for architecture generation."""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Architecture diagram title",
                },
                "direction": {
                    "type": "string",
                    "enum": ["TD", "TB", "BT", "RL", "LR"],
                    "default": "TD",
                },
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": ["service", "database", "external"],
                                "default": "service",
                            },
                        },
                        "required": ["id", "name"],
                    },
                    "minItems": 1,
                },
                "connections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "label": {"type": "string"},
                        },
                        "required": ["from", "to"],
                    },
                },
            },
            "required": ["components"],
        }


class ProcessFlowGenerator(DiagramGenerator):
    """
    Generator for business process flow diagrams.

    Creates process flow diagrams with decision points,
    parallel processes, and standard business symbols.
    """

    def generate(self, data: Dict[str, Any], **options) -> str:
        """Generate process flow diagram from structured data."""
        # Implementation similar to FlowchartGenerator but with
        # business process specific shapes and styling
        direction = data.get("direction", "TD")
        title = data.get("title", "")
        processes = data.get("processes", [])
        flows = data.get("flows", [])

        lines = [f"flowchart {direction}"]

        if title:
            lines.append(f"    %% {title}")
            lines.append("")

        # Add start/end nodes
        lines.append("    Start([Start])")
        lines.append("    End([End])")
        lines.append("")

        # Add process nodes
        for process in processes:
            proc_id = process["id"]
            label = process["label"]
            proc_type = process.get("type", "process")

            if proc_type == "decision":
                lines.append(f"    {proc_id}{{{label}}}")
            elif proc_type == "subprocess":
                lines.append(f"    {proc_id}[[{label}]]")
            elif proc_type == "data":
                lines.append(f"    {proc_id}[/{label}/]")
            else:
                lines.append(f"    {proc_id}[{label}]")

        lines.append("")

        # Add flows
        for flow in flows:
            from_node = flow["from"]
            to_node = flow["to"]
            condition = flow.get("condition", "")

            if condition:
                lines.append(f"    {from_node} -->|{condition}| {to_node}")
            else:
                lines.append(f"    {from_node} --> {to_node}")

        return "\n".join(lines)

    def get_schema(self) -> Dict[str, Any]:
        """Get data schema for process flow generation."""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Process flow title"},
                "direction": {
                    "type": "string",
                    "enum": ["TD", "TB", "BT", "RL", "LR"],
                    "default": "TD",
                },
                "processes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": ["process", "decision", "subprocess", "data"],
                                "default": "process",
                            },
                        },
                        "required": ["id", "label"],
                    },
                    "minItems": 1,
                },
                "flows": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "condition": {"type": "string"},
                        },
                        "required": ["from", "to"],
                    },
                },
            },
            "required": ["processes", "flows"],
        }
