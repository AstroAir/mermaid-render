"""
Class diagram model for the Mermaid Render library.

This module provides an object-oriented interface for creating UML class diagrams
with support for classes, interfaces, relationships, and methods.
"""

from typing import Dict, List, Optional

from ..core import MermaidDiagram
from ..exceptions import DiagramError


class ClassMethod:
    """Represents a method belonging to a class in a class diagram.

    Attributes:
        name: Method name.
        visibility: UML-style visibility ('public', 'private', 'protected', 'package').
        return_type: Optional return type string.
        parameters: Optional list of parameter strings (e.g., 'x: int').
        is_static: Whether the method is static.
        is_abstract: Whether the method is abstract.
    """

    def __init__(
        self,
        name: str,
        visibility: str = "public",
        return_type: Optional[str] = None,
        parameters: Optional[List[str]] = None,
        is_static: bool = False,
        is_abstract: bool = False,
    ) -> None:
        """Initialize a ClassMethod with optional metadata."""
        self.name = name
        self.visibility = visibility
        self.return_type = return_type
        self.parameters = parameters or []
        self.is_static = is_static
        self.is_abstract = is_abstract

    def to_mermaid(self) -> str:
        """Return the Mermaid syntax fragment for this method."""
        visibility_map = {
            "public": "+",
            "private": "-",
            "protected": "#",
            "package": "~",
        }
        vis_symbol = visibility_map.get(self.visibility, "+")

        params_str = ", ".join(self.parameters)
        method_str = f"{vis_symbol}{self.name}({params_str})"

        if self.return_type:
            method_str += f" {self.return_type}"

        if self.is_static:
            method_str += "$"
        if self.is_abstract:
            method_str += "*"

        return method_str


class ClassAttribute:
    """Represents a class attribute (field) in a class diagram.

    Attributes:
        name: Attribute name.
        type: Optional type annotation.
        visibility: UML-style visibility specifier.
        is_static: Whether the attribute is static.
    """

    def __init__(
        self,
        name: str,
        type: Optional[str] = None,
        visibility: str = "public",
        is_static: bool = False,
    ) -> None:
        """Initialize a ClassAttribute with metadata."""
        self.name = name
        self.type = type
        self.visibility = visibility
        self.is_static = is_static

    def to_mermaid(self) -> str:
        """Return the Mermaid syntax fragment for this attribute."""
        visibility_map = {
            "public": "+",
            "private": "-",
            "protected": "#",
            "package": "~",
        }
        vis_symbol = visibility_map.get(self.visibility, "+")

        attr_str = f"{vis_symbol}{self.name}"
        if self.type:
            attr_str += f" {self.type}"
        if self.is_static:
            attr_str += "$"

        return attr_str


class ClassDefinition:
    """Represents a class/interface definition in a class diagram.

    Attributes:
        name: Class name.
        is_abstract: Marks the class as abstract.
        is_interface: Marks the class as an interface.
        stereotype: Optional stereotype label.
        attributes: Collected attributes defined on this class.
        methods: Collected methods defined on this class.
    """

    def __init__(
        self,
        name: str,
        is_abstract: bool = False,
        is_interface: bool = False,
        stereotype: Optional[str] = None,
    ) -> None:
        """Create a new ClassDefinition with optional flags and stereotype."""
        self.name = name
        self.is_abstract = is_abstract
        self.is_interface = is_interface
        self.stereotype = stereotype
        self.attributes: List[ClassAttribute] = []
        self.methods: List[ClassMethod] = []

    def add_attribute(self, attribute: ClassAttribute) -> None:
        """Append an attribute to this class definition."""
        self.attributes.append(attribute)

    def add_method(self, method: ClassMethod) -> None:
        """Append a method to this class definition."""
        self.methods.append(method)

    def to_mermaid(self) -> List[str]:
        """Build and return the Mermaid class block as a list of lines."""
        lines = []

        # Class declaration
        if self.is_interface:
            lines.append(f"class {self.name} {{")
            lines.append("    <<interface>>")
        elif self.is_abstract:
            lines.append(f"class {self.name} {{")
            lines.append("    <<abstract>>")
        else:
            lines.append(f"class {self.name} {{")

        # Add stereotype if present
        if self.stereotype:
            lines.append(f"    <<{self.stereotype}>>")

        # Add attributes
        for attr in self.attributes:
            lines.append(f"    {attr.to_mermaid()}")

        # Add methods
        for method in self.methods:
            lines.append(f"    {method.to_mermaid()}")

        lines.append("}")
        return lines


class ClassRelationship:
    """Represents a relationship (edge) between two classes.

    Supported relationship types map to Mermaid arrows:
        inheritance  -> '<|--'
        composition  -> '*--'
        aggregation  -> 'o--'
        association  -> '-->'
        dependency   -> '..>'
        realization  -> '..|>'

    Attributes:
        from_class: Source class name.
        to_class: Target class name.
        relationship_type: One of the supported relationship keys.
        label: Optional relationship label.
        from_cardinality: Optional source-side cardinality.
        to_cardinality: Optional target-side cardinality.
    """

    RELATIONSHIP_TYPES = {
        "inheritance": "<|--",
        "composition": "*--",
        "aggregation": "o--",
        "association": "-->",
        "dependency": "..>",
        "realization": "..|>",
    }

    def __init__(
        self,
        from_class: str,
        to_class: str,
        relationship_type: str,
        label: Optional[str] = None,
        from_cardinality: Optional[str] = None,
        to_cardinality: Optional[str] = None,
    ) -> None:
        """Initialize a ClassRelationship and validate the relationship type."""
        self.from_class = from_class
        self.to_class = to_class
        self.relationship_type = relationship_type
        self.label = label
        self.from_cardinality = from_cardinality
        self.to_cardinality = to_cardinality

        if relationship_type not in self.RELATIONSHIP_TYPES:
            raise DiagramError(f"Unknown relationship type: {relationship_type}")

    def to_mermaid(self) -> str:
        """Return the Mermaid syntax line for this relationship."""
        arrow = self.RELATIONSHIP_TYPES[self.relationship_type]

        # Build relationship string
        parts = [self.from_class]

        if self.from_cardinality:
            parts.append(f'"{self.from_cardinality}"')

        parts.append(arrow)

        if self.to_cardinality:
            parts.append(f'"{self.to_cardinality}"')

        parts.append(self.to_class)

        if self.label:
            parts.append(f": {self.label}")

        return " ".join(parts)


class ClassDiagram(MermaidDiagram):
    """High-level class diagram container that emits Mermaid classDiagram.

    Provides APIs to register classes, attributes, methods, and relationships and
    to generate the final Mermaid diagram text.
    """

    def __init__(self, title: Optional[str] = None) -> None:
        """Initialize an empty class diagram with an optional title."""
        super().__init__(title)
        self.classes: Dict[str, ClassDefinition] = {}
        self.relationships: List[ClassRelationship] = []

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram header keyword ('classDiagram')."""
        return "classDiagram"

    def add_class(
        self,
        name: str,
        is_abstract: bool = False,
        is_interface: bool = False,
        stereotype: Optional[str] = None,
    ) -> ClassDefinition:
        """Create and register a new class; raises if the name already exists."""
        if name in self.classes:
            raise DiagramError(f"Class '{name}' already exists")

        class_def = ClassDefinition(name, is_abstract, is_interface, stereotype)
        self.classes[name] = class_def
        return class_def

    def add_relationship(
        self,
        from_class: str,
        to_class: str,
        relationship_type: str,
        label: Optional[str] = None,
        from_cardinality: Optional[str] = None,
        to_cardinality: Optional[str] = None,
    ) -> ClassRelationship:
        """Create and register a new relationship; raises if classes are missing."""
        if from_class not in self.classes:
            raise DiagramError(f"Class '{from_class}' does not exist")
        if to_class not in self.classes:
            raise DiagramError(f"Class '{to_class}' does not exist")

        relationship = ClassRelationship(
            from_class,
            to_class,
            relationship_type,
            label,
            from_cardinality,
            to_cardinality,
        )
        self.relationships.append(relationship)
        return relationship

    def _generate_mermaid(self) -> str:
        """Generate and return the full Mermaid text for the diagram."""
        lines = ["classDiagram"]

        # Add title if present
        if self.title:
            lines.append(f"    title: {self.title}")

        # Add classes
        for class_def in self.classes.values():
            class_lines = class_def.to_mermaid()
            for line in class_lines:
                lines.append(f"    {line}")

        # Add relationships
        for relationship in self.relationships:
            lines.append(f"    {relationship.to_mermaid()}")

        return "\n".join(lines)
