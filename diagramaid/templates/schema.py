"""
Template schema validation for Mermaid diagram templates.

This module provides schema definitions and validation functions for
template structure, parameters, and content validation.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..exceptions import ValidationError


class ParameterType(Enum):
    """Supported parameter types for templates."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    OBJECT = "object"


@dataclass
class ParameterSchema:
    """
    Schema definition for a template parameter.

    Defines the structure, validation rules, and metadata for
    template parameters.
    """

    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Any = None
    validation: dict[str, Any] | None = None
    examples: list[Any] | None = None

    def validate_value(self, value: Any) -> bool:
        """
        Validate a parameter value against this schema.

        Args:
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        # Type validation
        if not self._validate_type(value):
            return False

        # Custom validation rules
        if self.validation:
            return self._validate_rules(value)

        return True

    def _validate_type(self, value: Any) -> bool:
        """Validate parameter type."""
        if self.type == ParameterType.STRING:
            return isinstance(value, str)
        elif self.type == ParameterType.INTEGER:
            return isinstance(value, int)
        elif self.type == ParameterType.FLOAT:
            return isinstance(value, (int, float))
        elif self.type == ParameterType.BOOLEAN:
            return isinstance(value, bool)
        elif self.type == ParameterType.LIST:
            return isinstance(value, list)
        elif self.type == ParameterType.DICT:
            return isinstance(value, dict)
        elif self.type == ParameterType.OBJECT:
            return True  # Accept any object

    def _validate_rules(self, value: Any) -> bool:
        """Validate against custom validation rules."""
        if not self.validation:
            return True

        # String validation
        if self.type == ParameterType.STRING:
            if "min_length" in self.validation:
                if len(value) < self.validation["min_length"]:
                    return False

            if "max_length" in self.validation:
                if len(value) > self.validation["max_length"]:
                    return False

            if "pattern" in self.validation:
                if not re.match(self.validation["pattern"], value):
                    return False

            if "enum" in self.validation:
                if value not in self.validation["enum"]:
                    return False

        # Numeric validation
        elif self.type in [ParameterType.INTEGER, ParameterType.FLOAT]:
            if "min" in self.validation:
                if value < self.validation["min"]:
                    return False

            if "max" in self.validation:
                if value > self.validation["max"]:
                    return False

        # List validation
        elif self.type == ParameterType.LIST:
            if "min_items" in self.validation:
                if len(value) < self.validation["min_items"]:
                    return False

            if "max_items" in self.validation:
                if len(value) > self.validation["max_items"]:
                    return False

            if "item_type" in self.validation:
                item_type = self.validation["item_type"]
                for item in value:
                    if not self._validate_item_type(item, item_type):
                        return False

        return True

    def _validate_item_type(self, item: Any, expected_type: str) -> bool:
        """Validate list item type."""
        type_map: dict[str, type[Any] | tuple[type[Any], ...]] = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "list": list,
            "dict": dict,
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(item, expected_python_type)

        return True


@dataclass
class TemplateSchema:
    """
    Complete schema definition for a Mermaid diagram template.

    Defines the structure, parameters, validation rules, and metadata
    for template validation and generation.
    """

    name: str
    version: str
    diagram_type: str
    description: str
    parameters: list[ParameterSchema]
    template_content: str
    metadata: dict[str, Any] | None = None

    def validate(self) -> list[str]:
        """
        Validate the template schema.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Basic field validation
        if not self.name or not self.name.strip():
            errors.append("Template name is required")

        if not self.version or not self.version.strip():
            errors.append("Template version is required")

        if not self.diagram_type or not self.diagram_type.strip():
            errors.append("Diagram type is required")

        if not self.template_content or not self.template_content.strip():
            errors.append("Template content is required")

        # Validate diagram type
        valid_types = [
            "flowchart",
            "sequence",
            "class",
            "state",
            "er",
            "journey",
            "gantt",
            "pie",
            "gitgraph",
            "mindmap",
        ]
        if self.diagram_type not in valid_types:
            errors.append(f"Invalid diagram type: {self.diagram_type}")

        # Validate parameters
        parameter_names = set()
        for param in self.parameters:
            if param.name in parameter_names:
                errors.append(f"Duplicate parameter name: {param.name}")
            parameter_names.add(param.name)

            # Validate parameter name format
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", param.name):
                errors.append(f"Invalid parameter name format: {param.name}")

        # Validate template content syntax (basic check)
        if "{{" in self.template_content or "{%" in self.template_content:
            # Contains Jinja2 syntax - validate basic structure
            if not self._validate_jinja_syntax():
                errors.append("Invalid Jinja2 template syntax")

        return errors

    def _validate_jinja_syntax(self) -> bool:
        """Basic Jinja2 syntax validation."""
        try:
            from jinja2 import BaseLoader, Environment

            env = Environment(loader=BaseLoader())
            env.from_string(self.template_content)
            return True
        except Exception:
            return False


def validate_template(template_data: dict[str, Any]) -> None:
    """
    Validate template data against schema.

    Args:
        template_data: Template data dictionary

    Raises:
        ValidationError: If validation fails
    """
    required_fields = ["name", "diagram_type", "template_content", "parameters"]

    # Check required fields
    for field in required_fields:
        if field not in template_data:
            raise ValidationError(f"Missing required field: {field}")

    # Validate diagram type
    valid_types = [
        "flowchart",
        "sequence",
        "class",
        "state",
        "er",
        "journey",
        "gantt",
        "pie",
        "gitgraph",
        "mindmap",
    ]

    if template_data["diagram_type"] not in valid_types:
        raise ValidationError(f"Invalid diagram type: {template_data['diagram_type']}")

    # Validate parameters structure
    if not isinstance(template_data["parameters"], dict):
        raise ValidationError("Parameters must be a dictionary")

    # Validate template content is not empty
    if not template_data["template_content"].strip():
        raise ValidationError("Template content cannot be empty")


def validate_template_parameters(
    template_parameters: dict[str, Any], provided_parameters: dict[str, Any]
) -> list[str]:
    """
    Validate provided parameters against template parameter schema.

    Args:
        template_parameters: Template parameter definitions
        provided_parameters: Parameters provided for generation

    Returns:
        List of validation errors
    """
    errors = []

    # Check required parameters
    required = template_parameters.get("required", [])
    for param_name in required:
        if param_name not in provided_parameters:
            errors.append(f"Missing required parameter: {param_name}")

    # Validate parameter types and values
    properties = template_parameters.get("properties", {})
    for param_name, param_value in provided_parameters.items():
        if param_name in properties:
            param_schema = properties[param_name]

            # Type validation
            expected_type = param_schema.get("type")
            if expected_type and not _validate_parameter_type(
                param_value, expected_type
            ):
                errors.append(
                    f"Invalid type for parameter {param_name}: expected {expected_type}"
                )

            # Additional validation rules
            validation_rules = param_schema.get("validation", {})
            param_errors = _validate_parameter_rules(
                param_name, param_value, validation_rules
            )
            errors.extend(param_errors)

            # Also check for JSON Schema-style validation rules directly in param_schema
            json_schema_errors = _validate_json_schema_rules(
                param_name, param_value, param_schema
            )
            errors.extend(json_schema_errors)

    return errors


def _validate_parameter_type(value: Any, expected_type: str) -> bool:
    """Validate parameter type."""
    type_map: dict[str, type[Any] | tuple[type[Any], ...]] = {
        "string": str,
        "integer": int,
        "float": (int, float),
        "boolean": bool,
        "list": list,
        "dict": dict,
        "object": object,
    }

    expected_python_type = type_map.get(expected_type)
    if expected_python_type:
        return isinstance(value, expected_python_type)

    return True


def _validate_parameter_rules(
    param_name: str, value: Any, rules: dict[str, Any]
) -> list[str]:
    """Validate parameter against custom rules."""
    errors = []

    # String validation
    if isinstance(value, str):
        if "min_length" in rules and len(value) < rules["min_length"]:
            errors.append(
                f"Parameter {param_name} too short (min: {rules['min_length']})"
            )

        if "max_length" in rules and len(value) > rules["max_length"]:
            errors.append(
                f"Parameter {param_name} too long (max: {rules['max_length']})"
            )

        if "pattern" in rules and not re.match(rules["pattern"], value):
            errors.append(f"Parameter {param_name} doesn't match required pattern")

    # Numeric validation
    elif isinstance(value, (int, float)):
        if "min" in rules and value < rules["min"]:
            errors.append(f"Parameter {param_name} too small (min: {rules['min']})")

        if "max" in rules and value > rules["max"]:
            errors.append(f"Parameter {param_name} too large (max: {rules['max']})")

    # List validation
    elif isinstance(value, list):
        if "min_items" in rules and len(value) < rules["min_items"]:
            errors.append(
                f"Parameter {param_name} has too few items (min: {rules['min_items']})"
            )

        if "max_items" in rules and len(value) > rules["max_items"]:
            errors.append(
                f"Parameter {param_name} has too many items (max: {rules['max_items']})"
            )

    return errors


def _validate_json_schema_rules(
    param_name: str, value: Any, schema: dict[str, Any]
) -> list[str]:
    """Validate parameter against JSON Schema-style rules."""
    errors = []

    # String validation
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(
                f"Parameter {param_name} too short (min: {schema['minLength']})"
            )

        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(
                f"Parameter {param_name} too long (max: {schema['maxLength']})"
            )

        if "pattern" in schema and not re.match(schema["pattern"], value):
            errors.append(f"Parameter {param_name} doesn't match required pattern")

    # Numeric validation
    elif isinstance(value, (int, float)):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(
                f"Parameter {param_name} too small (min: {schema['minimum']})"
            )

        if "maximum" in schema and value > schema["maximum"]:
            errors.append(
                f"Parameter {param_name} too large (max: {schema['maximum']})"
            )

    # Array validation
    elif isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(
                f"Parameter {param_name} has too few items (min: {schema['minItems']})"
            )

        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(
                f"Parameter {param_name} has too many items (max: {schema['maxItems']})"
            )

    return errors
