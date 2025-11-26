"""Generate the code reference pages and navigation."""

import importlib
import pkgutil
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()


def is_module_available(module_name: str) -> bool:
    """Check if a module is available for import."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def get_submodules(package_name: str) -> list[str]:
    """Get all submodules of a package."""
    try:
        package = importlib.import_module(package_name)
        if hasattr(package, "__path__"):
            submodules = []
            for _, name, ispkg in pkgutil.iter_modules(
                package.__path__, package_name + "."
            ):
                if not name.startswith("_"):
                    submodules.append(name)
            return submodules
        return []
    except ImportError:
        return []


# Define the core modules to document
core_modules = [
    "mermaid_render",
    "mermaid_render.core",
    "mermaid_render.exceptions",
    "mermaid_render.plugin_renderer",
    "mermaid_render.convenience",
]

# Define optional feature modules
optional_modules = [
    "mermaid_render.config",
    "mermaid_render.ai",
    "mermaid_render.collaboration",
    "mermaid_render.interactive",
    "mermaid_render.templates",
    "mermaid_render.cache",
]

# Define modules with submodules that need individual pages
submodule_groups: dict[str, list[str]] = {
    "mermaid_render.models": [],
    "mermaid_render.renderers": [],
    "mermaid_render.utils": [],
    "mermaid_render.validators": [],
}

# Discover available modules
available_modules = []
for module in core_modules:
    if is_module_available(module):
        available_modules.append(module)

for module in optional_modules:
    if is_module_available(module):
        available_modules.append(module)

# Discover submodules
for parent_module in submodule_groups:
    if is_module_available(parent_module):
        available_modules.append(parent_module)
        submodules = get_submodules(parent_module)
        submodule_groups[parent_module] = submodules

# Generate main module reference pages
for module in available_modules:
    if module in submodule_groups:
        # Skip modules that will have individual submodule pages
        continue

    module_path = Path(module.replace(".", "/"))
    doc_path = Path("api-reference") / f"{module_path.name}.md"

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        # Write the module header
        module_name = module.split(".")[-1].replace("_", " ").title()
        fd.write(f"# {module_name}\n\n")

        # Add module description
        if module == "mermaid_render":
            fd.write("Main package module with core functionality and public API.\n\n")
        elif module == "mermaid_render.core":
            fd.write("Core rendering classes and base functionality.\n\n")
        elif module == "mermaid_render.ai":
            fd.write("AI-powered features for diagram generation and optimization.\n\n")
        elif module == "mermaid_render.cache":
            fd.write(
                "Caching system with multiple backends and performance monitoring.\n\n"
            )
        elif module == "mermaid_render.collaboration":
            fd.write(
                "Collaboration features for multi-user editing and version control.\n\n"
            )
        elif module == "mermaid_render.interactive":
            fd.write("Interactive web interface and diagram builder.\n\n")
        elif module == "mermaid_render.templates":
            fd.write(
                "Template system for generating diagrams from structured data.\n\n"
            )
        elif module == "mermaid_render.config":
            fd.write("Configuration management and theme system.\n\n")
        elif module == "mermaid_render.exceptions":
            fd.write("Exception classes for error handling.\n\n")
        elif module == "mermaid_render.plugin_renderer":
            fd.write("Plugin-based renderer with advanced features.\n\n")
        elif module == "mermaid_render.convenience":
            fd.write("Convenience functions for quick diagram rendering.\n\n")

        # Add module docstring
        fd.write(f"::: {module}\n")
        fd.write("    options:\n")
        fd.write("      show_root_heading: false\n")
        fd.write("      show_source: true\n")
        fd.write("      heading_level: 2\n")
        fd.write("      show_submodules: false\n")
        fd.write("      members_order: source\n")
        fd.write("      group_by_category: true\n")
        fd.write("      show_category_heading: true\n")
        fd.write("      filters: ['!^_', '!^__']\n")

    # Set edit path for the generated file
    mkdocs_gen_files.set_edit_path(doc_path, Path("../") / module_path)

# Generate submodule pages (individual pages only to avoid duplicate URLs)
for parent_module, submodules in submodule_groups.items():
    if not submodules:
        continue

    parent_name = parent_module.split(".")[-1]

    # Create main parent module page with overview only (no detailed API docs)
    parent_doc_path = Path("api-reference") / f"{parent_name}.md"
    with mkdocs_gen_files.open(parent_doc_path, "w") as fd:
        parent_title = parent_name.replace("_", " ").title()
        fd.write(f"# {parent_title} Overview\n\n")

        # Add parent module description
        if parent_name == "models":
            fd.write(
                "Diagram model classes providing object-oriented interfaces for creating different types of Mermaid diagrams.\n\n"
            )
            fd.write(
                "Each model class provides a clean, type-safe interface for building specific diagram types with validation and Mermaid syntax generation.\n\n"
            )
        elif parent_name == "renderers":
            fd.write(
                "Rendering engines for converting Mermaid diagrams to different output formats.\n\n"
            )
            fd.write(
                "The renderer system supports multiple backends and output formats with extensible plugin architecture.\n\n"
            )
        elif parent_name == "utils":
            fd.write(
                "Utility functions for validation, export, and helper operations.\n\n"
            )
            fd.write(
                "Common utility functions used throughout the library for various operations.\n\n"
            )
        elif parent_name == "validators":
            fd.write("Validation system for Mermaid diagram syntax and structure.\n\n")
            fd.write(
                "Comprehensive validation with detailed error reporting and suggestions.\n\n"
            )

        # Add overview of submodules
        fd.write("## Available Modules\n\n")
        for submodule in submodules:
            if not is_module_available(submodule):
                continue
            submodule_name = submodule.split(".")[-1]
            submodule_title = submodule_name.replace("_", " ").title()
            fd.write(f"- **[{submodule_title}]({parent_name}/{submodule_name}.md)**: ")

            # Add brief description for each submodule
            if parent_name == "models":
                if "flowchart" in submodule_name:
                    fd.write("Flowchart and process diagram models")
                elif "sequence" in submodule_name:
                    fd.write("Sequence diagram models for interaction flows")
                elif "class" in submodule_name:
                    fd.write("UML class diagram models")
                elif "state" in submodule_name:
                    fd.write("State machine diagram models")
                elif "er" in submodule_name:
                    fd.write("Entity-relationship diagram models")
                elif "user_journey" in submodule_name:
                    fd.write("User journey mapping models")
                elif "gantt" in submodule_name:
                    fd.write("Gantt chart and timeline models")
                elif "pie" in submodule_name:
                    fd.write("Pie chart models for data visualization")
                elif "git" in submodule_name:
                    fd.write("Git workflow and branching models")
                elif "mindmap" in submodule_name:
                    fd.write("Mind map and hierarchical structure models")
                elif "timeline" in submodule_name:
                    fd.write("Timeline diagram models")
                else:
                    fd.write(f"{submodule_title} diagram models")
            elif parent_name == "renderers":
                if "svg" in submodule_name:
                    fd.write("SVG format renderer with caching and optimization")
                elif "png" in submodule_name:
                    fd.write("PNG format renderer with dimension control")
                elif "pdf" in submodule_name:
                    fd.write("PDF format renderer with page layout options")
                else:
                    fd.write(f"{submodule_title} format renderer")
            elif parent_name == "utils":
                if "validation" in submodule_name:
                    fd.write("Diagram validation utilities")
                elif "export" in submodule_name:
                    fd.write("Export and file handling utilities")
                elif "helpers" in submodule_name:
                    fd.write("General helper functions")
                else:
                    fd.write(f"{submodule_title} utilities")
            elif parent_name == "validators":
                fd.write(f"{submodule_title} validation components")

            fd.write("\n")
        fd.write("\n")

    # Create individual submodule pages with full API documentation
    for submodule in submodules:
        if not is_module_available(submodule):
            continue

        submodule_name = submodule.split(".")[-1]
        submodule_doc_path = (
            Path("api-reference") / parent_name / f"{submodule_name}.md"
        )

        with mkdocs_gen_files.open(submodule_doc_path, "w") as fd:
            submodule_title = submodule_name.replace("_", " ").title()
            fd.write(f"# {submodule_title}\n\n")

            # Add submodule-specific descriptions
            if parent_name == "models":
                fd.write(
                    f"Model classes for creating {submodule_title.lower()} diagrams with object-oriented interface.\n\n"
                )
            elif parent_name == "renderers":
                fd.write(
                    f"Renderer implementation for {submodule_title.lower()} format output.\n\n"
                )
            elif parent_name == "utils":
                fd.write(
                    f"Utility functions for {submodule_title.lower()} operations.\n\n"
                )
            elif parent_name == "validators":
                fd.write(f"Validation components for {submodule_title.lower()}.\n\n")

            # Add submodule docstring with unique configuration to avoid conflicts
            fd.write(f"::: {submodule}\n")
            fd.write("    options:\n")
            fd.write("      show_root_heading: false\n")
            fd.write("      show_source: true\n")
            fd.write("      heading_level: 2\n")
            fd.write("      show_bases: true\n")
            fd.write("      show_inheritance_diagram: false\n")
            fd.write("      members_order: source\n")
            fd.write("      group_by_category: true\n")
            fd.write("      show_category_heading: true\n")
            fd.write("      filters: ['!^_', '!^__']\n")
            # Prevent duplicate URLs by not showing submodules in individual pages
            fd.write("      show_submodules: false\n")

        # Set edit path for submodule
        mkdocs_gen_files.set_edit_path(
            submodule_doc_path, Path("../../") / Path(submodule.replace(".", "/"))
        )

# Build navigation structure
nav_items = []

# Add main modules to navigation
for module in available_modules:
    if module in submodule_groups:
        continue
    module_name = module.split(".")[-1]
    module_title = module_name.replace("_", " ").title()
    nav_items.append(f"* [{module_title}]({module_name}.md)")

# Add submodule groups to navigation
for parent_module, submodules in submodule_groups.items():
    if not submodules:
        continue
    parent_name = parent_module.split(".")[-1]
    parent_title = parent_name.replace("_", " ").title()
    nav_items.append(f"* [{parent_title}]({parent_name}.md)")

    # Add submodule navigation items
    for submodule in submodules:
        if not is_module_available(submodule):
            continue
        submodule_name = submodule.split(".")[-1]
        submodule_title = submodule_name.replace("_", " ").title()
        nav_items.append(
            f"    * [{submodule_title}]({parent_name}/{submodule_name}.md)"
        )

# Write the navigation file
with mkdocs_gen_files.open("api-reference/SUMMARY.md", "w") as nav_file:
    nav_file.write("# API Reference\n\n")
    nav_file.write(
        "This section contains the complete API reference for all modules.\n\n"
    )
    for item in nav_items:
        nav_file.write(f"{item}\n")

print(f"Generated documentation for {len(available_modules)} modules")
print(f"Available modules: {', '.join(available_modules)}")
for parent, subs in submodule_groups.items():
    if subs:
        print(f"{parent}: {len(subs)} submodules")
