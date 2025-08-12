"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

# Define the modules to document (core modules only)
modules = [
    "mermaid_render",
    "mermaid_render.core",
    "mermaid_render.models",
    "mermaid_render.renderers",
    "mermaid_render.utils",
    "mermaid_render.validators",
    "mermaid_render.exceptions",
]

# Optional modules that may not be available
optional_modules = [
    "mermaid_render.config",
    "mermaid_render.ai",
    "mermaid_render.collaboration",
    "mermaid_render.interactive",
    "mermaid_render.templates",
    "mermaid_render.cache",
]

# Check which optional modules are available
available_optional_modules = []
for module in optional_modules:
    try:
        __import__(module)
        available_optional_modules.append(module)
    except ImportError:
        pass

# Combine core and available optional modules
all_modules = modules + available_optional_modules

# Generate reference pages for each module
for module in all_modules:
    module_path = Path(module.replace(".", "/"))
    doc_path = Path("api-reference") / f"{module_path.name}.md"
    full_doc_path = Path("api-reference", module_path.name + ".md")

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        # Write the module header
        module_name = module.split(".")[-1].replace("_", " ").title()
        fd.write(f"# {module_name}\n\n")

        # Add module docstring
        fd.write(f"::: {module}\n")

        # Configure mkdocstrings options for this module
        fd.write("    options:\n")
        fd.write("      show_root_heading: true\n")
        fd.write("      show_source: true\n")
        fd.write("      heading_level: 2\n")

        # Special handling for models module to show submodules
        if module == "mermaid_render.models":
            fd.write("      show_submodules: true\n")
        else:
            fd.write("      show_submodules: false\n")

    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / module_path)

# Generate individual model pages
model_modules = [
    "mermaid_render.models.flowchart",
    "mermaid_render.models.sequence",
    "mermaid_render.models.class_diagram",
    "mermaid_render.models.state",
    "mermaid_render.models.er_diagram",
    "mermaid_render.models.user_journey",
    "mermaid_render.models.gantt",
    "mermaid_render.models.pie_chart",
    "mermaid_render.models.git_graph",
    "mermaid_render.models.mindmap",
    "mermaid_render.models.timeline",
]

for model_module in model_modules:
    model_name = model_module.split(".")[-1]
    doc_path = Path("api-reference") / "models" / f"{model_name}.md"

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        # Write the model header
        model_title = model_name.replace("_", " ").title()
        fd.write(f"# {model_title}\n\n")

        # Add model docstring
        fd.write(f"::: {model_module}\n")
        fd.write("    options:\n")
        fd.write("      show_root_heading: true\n")
        fd.write("      show_source: true\n")
        fd.write("      heading_level: 2\n")
        fd.write("      show_bases: true\n")
        fd.write("      show_inheritance_diagram: true\n")

# Generate renderer pages
renderer_modules = [
    "mermaid_render.renderers.svg_renderer",
    "mermaid_render.renderers.png_renderer",
    "mermaid_render.renderers.pdf_renderer",
]

for renderer_module in renderer_modules:
    renderer_name = renderer_module.split(".")[-1]
    doc_path = Path("api-reference") / "renderers" / f"{renderer_name}.md"

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        # Write the renderer header
        renderer_title = renderer_name.replace("_", " ").title()
        fd.write(f"# {renderer_title}\n\n")

        # Add renderer docstring
        fd.write(f"::: {renderer_module}\n")
        fd.write("    options:\n")
        fd.write("      show_root_heading: true\n")
        fd.write("      show_source: true\n")
        fd.write("      heading_level: 2\n")

# Generate utility pages
utility_modules = [
    "mermaid_render.utils.validation",
    "mermaid_render.utils.export",
    "mermaid_render.utils.helpers",
]

for util_module in utility_modules:
    util_name = util_module.split(".")[-1]
    doc_path = Path("api-reference") / "utilities" / f"{util_name}.md"

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        # Write the utility header
        util_title = util_name.replace("_", " ").title()
        fd.write(f"# {util_title}\n\n")

        # Add utility docstring
        fd.write(f"::: {util_module}\n")
        fd.write("    options:\n")
        fd.write("      show_root_heading: true\n")
        fd.write("      show_source: true\n")
        fd.write("      heading_level: 2\n")

# Write the navigation file
with mkdocs_gen_files.open("api-reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
