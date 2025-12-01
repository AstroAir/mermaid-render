"""
Operation MCP tools for diagramaid.

This module provides batch operations, file operations, and format conversion tools.
"""

import logging
from pathlib import Path
from typing import Any

from .base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
    measure_performance,
)
from .core import render_diagram
from .helpers import (
    _detect_diagram_type,
    _extract_nodes_from_code,
    _get_common_patterns,
    _get_diagram_best_practices,
    _get_diagram_example,
    _get_quick_reference_guide,
    _get_syntax_guide,
    _prefix_nodes,
)
from .params import BatchRenderParams, DiagramTypeParams, FileOperationParams

logger = logging.getLogger(__name__)


async def convert_diagram_format(
    diagram_code: str,
    source_format: str = "svg",
    target_format: str = "png",
    theme: str | None = None,
    width: int | None = None,
    height: int | None = None,
) -> dict[str, Any]:
    """
    Convert a diagram between different output formats.

    This tool renders a diagram in one format and converts it to another,
    supporting SVG, PNG, and PDF formats with optional theme and size settings.

    Args:
        diagram_code: Mermaid diagram code to convert
        source_format: Source format (svg, png, pdf) - mainly for reference
        target_format: Target format to convert to (svg, png, pdf)
        theme: Theme to apply during conversion
        width: Output width in pixels
        height: Output height in pixels

    Returns:
        Dictionary containing converted diagram data and metadata

    Example:
        >>> result = convert_diagram_format(
        ...     "flowchart TD\\n    A --> B",
        ...     target_format="png"
        ... )
        >>> print(result["data"]["format"])  # "png"
    """
    try:
        import datetime

        # Validate target format
        valid_formats = ["svg", "png", "pdf"]
        if target_format.lower() not in valid_formats:
            return create_error_response(
                ValueError(f"Invalid target format: {target_format}"),
                ErrorCategory.VALIDATION,
                context={"valid_formats": valid_formats},
                suggestions=[f"Use one of: {', '.join(valid_formats)}"],
            )

        # Render in target format
        render_result = await render_diagram(
            diagram_code=diagram_code,
            output_format=target_format.lower(),
            theme=theme,
            width=width,
            height=height,
        )

        if not render_result.get("success"):
            return render_result

        # Enhanced metadata
        metadata = {
            "source_format": source_format,
            "target_format": target_format,
            "conversion_timestamp": datetime.datetime.now().isoformat(),
            "diagram_type": _detect_diagram_type(diagram_code),
            "theme_applied": theme or "default",
            "dimensions": {"width": width, "height": height},
        }

        return create_success_response(
            data={
                "format": target_format,
                "content": render_result["data"]["content"],
                "is_binary": render_result["data"]["is_binary"],
                "conversion_successful": True,
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error converting diagram format: {e}")
        return create_error_response(
            e,
            ErrorCategory.RENDERING,
            context={
                "source_format": source_format,
                "target_format": target_format,
            },
            suggestions=[
                "Check diagram syntax",
                "Verify format is supported",
            ],
        )


@measure_performance
def merge_diagrams(
    diagrams: list[dict[str, Any]],
    merge_strategy: str = "subgraph",
    title: str | None = None,
    direction: str = "TD",
) -> dict[str, Any]:
    """
    Merge multiple diagrams into a single diagram.

    This tool combines multiple Mermaid diagrams into one, using various
    merge strategies like subgraphs, sequential flow, or parallel layout.

    Args:
        diagrams: List of diagram specifications with 'code' and optional 'name'
        merge_strategy: How to merge diagrams (subgraph, sequential, parallel)
        title: Optional title for the merged diagram
        direction: Flow direction for merged diagram (TD, LR, BT, RL)

    Returns:
        Dictionary containing merged diagram code and metadata

    Example:
        >>> diagrams = [
        ...     {"code": "flowchart TD\\n    A --> B", "name": "Process 1"},
        ...     {"code": "flowchart TD\\n    C --> D", "name": "Process 2"}
        ... ]
        >>> result = merge_diagrams(diagrams, merge_strategy="subgraph")
        >>> print(result["data"]["merged_code"])
    """
    try:
        import datetime

        if not diagrams or len(diagrams) < 2:
            return create_error_response(
                ValueError("At least 2 diagrams required for merging"),
                ErrorCategory.VALIDATION,
                suggestions=["Provide at least 2 diagram specifications"],
            )

        valid_strategies = ["subgraph", "sequential", "parallel"]
        if merge_strategy not in valid_strategies:
            return create_error_response(
                ValueError(f"Invalid merge strategy: {merge_strategy}"),
                ErrorCategory.VALIDATION,
                context={"valid_strategies": valid_strategies},
                suggestions=[f"Use one of: {', '.join(valid_strategies)}"],
            )

        merged_code = ""
        diagram_types = []

        if merge_strategy == "subgraph":
            # Merge using subgraphs
            merged_code = f"flowchart {direction}\n"
            if title:
                merged_code = f"---\ntitle: {title}\n---\nflowchart {direction}\n"

            for i, diagram in enumerate(diagrams):
                code = diagram.get("code", "")
                name = diagram.get("name", f"Diagram_{i+1}")
                diagram_types.append(_detect_diagram_type(code))

                # Extract content (remove flowchart/graph declaration)
                content_lines = []
                for line in code.splitlines():
                    stripped = line.strip().lower()
                    if not (
                        stripped.startswith("flowchart")
                        or stripped.startswith("graph")
                    ):
                        content_lines.append(line)

                # Add as subgraph
                merged_code += f"    subgraph {name.replace(' ', '_')}[{name}]\n"
                for line in content_lines:
                    if line.strip():
                        merged_code += f"        {line.strip()}\n"
                merged_code += "    end\n"

        elif merge_strategy == "sequential":
            # Merge sequentially with connections
            merged_code = f"flowchart {direction}\n"
            if title:
                merged_code = f"---\ntitle: {title}\n---\nflowchart {direction}\n"

            last_node = None
            for i, diagram in enumerate(diagrams):
                code = diagram.get("code", "")
                name = diagram.get("name", f"Diagram_{i+1}")
                diagram_types.append(_detect_diagram_type(code))

                # Extract nodes and find first/last
                nodes = _extract_nodes_from_code(code)
                if nodes:
                    first_node = f"D{i}_{nodes[0]}"
                    current_last = f"D{i}_{nodes[-1]}"

                    # Add prefix to avoid node conflicts
                    for line in code.splitlines():
                        stripped = line.strip().lower()
                        if not (
                            stripped.startswith("flowchart")
                            or stripped.startswith("graph")
                        ):
                            # Prefix node names
                            prefixed_line = _prefix_nodes(line, f"D{i}_")
                            if prefixed_line.strip():
                                merged_code += f"    {prefixed_line.strip()}\n"

                    # Connect to previous diagram
                    if last_node:
                        merged_code += f"    {last_node} --> {first_node}\n"

                    last_node = current_last

        elif merge_strategy == "parallel":
            # Merge in parallel (side by side conceptually)
            merged_code = f"flowchart {direction}\n"
            if title:
                merged_code = f"---\ntitle: {title}\n---\nflowchart {direction}\n"

            for i, diagram in enumerate(diagrams):
                code = diagram.get("code", "")
                diagram_types.append(_detect_diagram_type(code))

                # Add prefix to avoid node conflicts
                for line in code.splitlines():
                    stripped = line.strip().lower()
                    if not (
                        stripped.startswith("flowchart")
                        or stripped.startswith("graph")
                    ):
                        prefixed_line = _prefix_nodes(line, f"P{i}_")
                        if prefixed_line.strip():
                            merged_code += f"    {prefixed_line.strip()}\n"

        # Enhanced metadata
        metadata = {
            "merge_timestamp": datetime.datetime.now().isoformat(),
            "diagram_count": len(diagrams),
            "merge_strategy": merge_strategy,
            "direction": direction,
            "source_types": diagram_types,
            "result_type": "flowchart",
            "line_count": len(merged_code.splitlines()),
        }

        return create_success_response(
            data={
                "merged_code": merged_code,
                "diagram_count": len(diagrams),
                "strategy_used": merge_strategy,
                "title": title,
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error merging diagrams: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            context={"diagram_count": len(diagrams) if diagrams else 0},
            suggestions=[
                "Check diagram syntax",
                "Ensure all diagrams are flowcharts for best results",
            ],
        )


async def export_to_markdown(
    diagram_code: str,
    title: str = "Diagram",
    description: str = "",
    include_code: bool = True,
    include_preview: bool = True,
    include_elements: bool = False,
    output_format: str = "svg",
) -> dict[str, Any]:
    """
    Export a diagram with documentation to Markdown format.

    This tool creates a comprehensive Markdown document containing the diagram,
    its code, description, and optionally extracted elements.

    Args:
        diagram_code: Mermaid diagram code to export
        title: Title for the document
        description: Description of the diagram
        include_code: Include the Mermaid code block
        include_preview: Include rendered preview (as base64 image)
        include_elements: Include extracted elements table
        output_format: Format for preview image (svg, png)

    Returns:
        Dictionary containing Markdown content and metadata

    Example:
        >>> result = export_to_markdown(
        ...     "flowchart TD\\n    A --> B",
        ...     title="My Process Flow",
        ...     description="This diagram shows..."
        ... )
        >>> print(result["data"]["markdown"])
    """
    try:
        import datetime

        from .analytics import extract_diagram_elements

        diagram_type = _detect_diagram_type(diagram_code)
        markdown_parts = []

        # Title
        markdown_parts.append(f"# {title}\n")

        # Description
        if description:
            markdown_parts.append(f"{description}\n")

        # Diagram type info
        markdown_parts.append(f"**Diagram Type:** {diagram_type or 'Unknown'}\n")

        # Mermaid code block
        if include_code:
            markdown_parts.append("## Diagram Code\n")
            markdown_parts.append(f"```mermaid\n{diagram_code}\n```\n")

        # Preview
        if include_preview:
            render_result = await render_diagram(
                diagram_code=diagram_code,
                output_format=output_format,
            )
            if render_result.get("success"):
                markdown_parts.append("## Preview\n")
                if render_result["data"]["is_binary"]:
                    # Base64 encoded image
                    content = render_result["data"]["content"]
                    markdown_parts.append(
                        f"![{title}](data:image/{output_format};base64,{content})\n"
                    )
                else:
                    # SVG can be embedded directly
                    markdown_parts.append("<!-- SVG Preview -->\n")
                    markdown_parts.append(
                        f"<details>\n<summary>Click to view SVG</summary>\n\n{render_result['data']['content']}\n\n</details>\n"
                    )

        # Elements table
        if include_elements:
            elements = await extract_diagram_elements(diagram_code)
            if elements.get("success"):
                data = elements["data"]["elements"]

                # Nodes table
                if data.get("nodes"):
                    markdown_parts.append("## Nodes\n")
                    markdown_parts.append("| ID | Label | Type |\n")
                    markdown_parts.append("|-----|-------|------|\n")
                    for node in data["nodes"]:
                        markdown_parts.append(
                            f"| {node.get('id', '-')} | {node.get('label', '-')} | {node.get('type', '-')} |\n"
                        )
                    markdown_parts.append("\n")

                # Edges table
                if data.get("edges"):
                    markdown_parts.append("## Connections\n")
                    markdown_parts.append("| From | To | Label |\n")
                    markdown_parts.append("|------|-----|-------|\n")
                    for edge in data["edges"]:
                        markdown_parts.append(
                            f"| {edge.get('from', '-')} | {edge.get('to', '-')} | {edge.get('label', '-')} |\n"
                        )
                    markdown_parts.append("\n")

        # Footer
        markdown_parts.append("---\n")
        markdown_parts.append(
            f"*Generated by diagramaid on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        )

        markdown_content = "\n".join(markdown_parts)

        # Enhanced metadata
        metadata = {
            "export_timestamp": datetime.datetime.now().isoformat(),
            "diagram_type": diagram_type,
            "export_options": {
                "include_code": include_code,
                "include_preview": include_preview,
                "include_elements": include_elements,
                "output_format": output_format,
            },
            "content_length": len(markdown_content),
            "line_count": len(markdown_content.splitlines()),
        }

        return create_success_response(
            data={
                "markdown": markdown_content,
                "title": title,
                "diagram_type": diagram_type,
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error exporting to markdown: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            suggestions=[
                "Check diagram syntax",
                "Verify export options",
            ],
        )


async def save_diagram_to_file(
    diagram_code: str,
    file_path: str,
    output_format: str = "svg",
    theme: str | None = None,
    create_directories: bool = True,
    overwrite: bool = False,
) -> dict[str, Any]:
    """
    Save rendered diagram content to a file with path validation.

    This tool renders a diagram and saves it directly to a file with comprehensive
    path validation, directory creation, and error handling.

    Args:
        diagram_code: Mermaid diagram code to render and save
        file_path: File path where to save the diagram
        output_format: Output format (svg, png, pdf)
        theme: Theme to apply to the diagram
        create_directories: Create parent directories if they don't exist
        overwrite: Overwrite existing files

    Returns:
        Dictionary containing save operation results

    Example:
        >>> result = save_diagram_to_file(
        ...     "flowchart TD\\n    A[Start] --> B[End]",
        ...     "/path/to/diagram.svg",
        ...     "svg"
        ... )
        >>> print(result["data"]["saved"])  # True
        >>> print(result["data"]["file_size"])  # File size in bytes
    """
    try:
        import base64
        import datetime

        # Validate parameters
        params = FileOperationParams(
            file_path=file_path,
            create_directories=create_directories,
            overwrite=overwrite,
        )

        # Validate file path
        file_path_obj = Path(params.file_path)

        # Check if file exists and overwrite is not allowed
        if file_path_obj.exists() and not params.overwrite:
            return create_error_response(
                FileExistsError(f"File already exists: {params.file_path}"),
                ErrorCategory.FILE_OPERATION,
                context={"file_path": params.file_path, "exists": True},
                suggestions=[
                    "Use overwrite=True to replace existing file",
                    "Choose a different file path",
                ],
            )

        # Create directories if needed
        if params.create_directories:
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Render the diagram first
        render_result = await render_diagram(
            diagram_code=diagram_code, output_format=output_format, theme=theme
        )

        if not render_result.get("success"):
            return create_error_response(
                RuntimeError("Failed to render diagram"),
                ErrorCategory.RENDERING,
                context={"render_error": render_result.get("error")},
                suggestions=["Check diagram syntax", "Verify rendering parameters"],
            )

        # Get rendered content
        content = render_result["data"]["content"]
        is_binary = render_result["data"]["is_binary"]

        # Save to file
        if is_binary:
            with open(file_path_obj, "wb") as f:
                f.write(base64.b64decode(content))
        else:
            with open(file_path_obj, "w", encoding="utf-8") as f:
                f.write(content)

        # Get file info
        file_size = file_path_obj.stat().st_size

        # Enhanced metadata
        metadata = {
            "save_timestamp": datetime.datetime.now().isoformat(),
            "file_path": str(file_path_obj.absolute()),
            "file_size_bytes": file_size,
            "output_format": output_format,
            "theme_used": theme or "default",
            "directories_created": params.create_directories,
        }

        return create_success_response(
            data={
                "saved": True,
                "file_path": str(file_path_obj.absolute()),
                "file_size": file_size,
                "format": output_format,
                "encoding": "binary" if is_binary else "utf-8",
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error saving diagram to file: {e}")
        return create_error_response(
            e,
            ErrorCategory.FILE_OPERATION,
            context={"file_path": file_path, "format": output_format},
            suggestions=[
                "Check file path permissions",
                "Verify directory exists",
                "Check disk space",
            ],
        )


async def batch_render_diagrams(
    diagrams: list[dict[str, Any]],
    parallel: bool = True,
    max_workers: int = 4,
) -> dict[str, Any]:
    """
    Render multiple diagrams efficiently with concurrent processing.

    This tool renders multiple diagrams in batch with optional concurrent processing
    for improved performance. Uses asyncio.gather for parallel async operations.
    Provides detailed progress tracking and error handling for individual diagrams.

    Args:
        diagrams: List of diagram specifications with code, format, theme, etc.
        parallel: Enable concurrent processing for better performance
        max_workers: Maximum number of concurrent tasks (used for semaphore)

    Returns:
        Dictionary containing batch render results and statistics

    Example:
        >>> diagrams = [
        ...     {"code": "flowchart TD\\n    A --> B", "format": "svg"},
        ...     {"code": "sequenceDiagram\\n    A->>B: Hello", "format": "png"}
        ... ]
        >>> result = await batch_render_diagrams(diagrams)
        >>> print(result["data"]["success_count"])  # Number of successful renders
    """
    try:
        import asyncio
        import datetime
        import time

        # Validate parameters
        params = BatchRenderParams(
            diagrams=diagrams, parallel=parallel, max_workers=max_workers
        )

        if not params.diagrams:
            return create_error_response(
                ValueError("No diagrams provided for batch rendering"),
                ErrorCategory.VALIDATION,
                suggestions=["Provide at least one diagram specification"],
            )

        results: list[dict[str, Any]] = []
        success_count = 0
        error_count = 0
        start_time = time.time()

        async def render_single(index: int, diagram: dict[str, Any]) -> dict[str, Any]:
            """Render a single diagram and return result with index."""
            try:
                result = await render_diagram(
                    diagram_code=diagram.get("code", ""),
                    output_format=diagram.get("format", "svg"),
                    theme=diagram.get("theme"),
                )
                return {
                    "index": index,
                    "success": result.get("success", False),
                    "result": result,
                    "diagram_spec": diagram,
                }
            except Exception as e:
                return {
                    "index": index,
                    "success": False,
                    "error": str(e),
                    "diagram_spec": diagram,
                }

        if params.parallel and len(params.diagrams) > 1:
            # Concurrent processing using asyncio.gather
            # Use semaphore to limit concurrent tasks
            semaphore = asyncio.Semaphore(params.max_workers)

            async def render_with_semaphore(index: int, diagram: dict[str, Any]) -> dict[str, Any]:
                async with semaphore:
                    return await render_single(index, diagram)

            tasks = [
                render_with_semaphore(i, diagram)
                for i, diagram in enumerate(params.diagrams)
            ]
            results = await asyncio.gather(*tasks)
        else:
            # Sequential processing
            for i, diagram in enumerate(params.diagrams):
                result = await render_single(i, diagram)
                results.append(result)

        # Count successes and errors
        for result in results:
            if result.get("success"):
                success_count += 1
            else:
                error_count += 1

        # Sort results by index to maintain order
        results.sort(key=lambda x: x["index"])

        end_time = time.time()
        total_time = end_time - start_time

        # Enhanced metadata
        metadata = {
            "batch_timestamp": datetime.datetime.now().isoformat(),
            "total_diagrams": len(params.diagrams),
            "processing_mode": "concurrent" if params.parallel else "sequential",
            "max_workers": params.max_workers if params.parallel else 1,
            "total_time_seconds": total_time,
            "average_time_per_diagram": (
                total_time / len(params.diagrams) if params.diagrams else 0
            ),
        }

        return create_success_response(
            data={
                "results": results,
                "summary": {
                    "total": len(params.diagrams),
                    "success_count": success_count,
                    "error_count": error_count,
                    "success_rate": (
                        success_count / len(params.diagrams) if params.diagrams else 0
                    ),
                    "total_time": total_time,
                    "processing_mode": "concurrent" if params.parallel else "sequential",
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error in batch rendering: {e}")
        return create_error_response(
            e,
            ErrorCategory.RENDERING,
            context={"diagram_count": len(diagrams) if diagrams else 0},
            suggestions=[
                "Check diagram specifications",
                "Reduce batch size",
                "Try sequential processing",
            ],
        )


@measure_performance
def list_diagram_types(
    diagram_type: str | None = None,
    include_examples: bool = True,
) -> dict[str, Any]:
    """
    List all supported diagram types with descriptions and capabilities.

    This tool provides comprehensive information about all supported Mermaid
    diagram types, including their capabilities, syntax patterns, and use cases.

    Args:
        diagram_type: Specific diagram type to get information for
        include_examples: Include example code for each diagram type

    Returns:
        Dictionary containing diagram type information and metadata

    Example:
        >>> result = list_diagram_types()
        >>> print(result["data"]["types"]["flowchart"]["description"])
        >>> result = list_diagram_types(diagram_type="sequence")
        >>> print(result["data"]["example_code"])  # Sequence diagram example
    """
    try:
        # Validate parameters
        params = DiagramTypeParams(
            diagram_type=diagram_type, include_examples=include_examples
        )

        # Define comprehensive diagram type information
        diagram_types = {
            "flowchart": {
                "name": "Flowchart",
                "description": "Process flow diagrams showing steps, decisions, and connections",
                "syntax_start": [
                    "flowchart TD",
                    "flowchart LR",
                    "graph TD",
                    "graph LR",
                ],
                "use_cases": [
                    "Process documentation",
                    "Decision trees",
                    "Workflow visualization",
                ],
                "complexity": "simple",
                "node_types": [
                    "rectangles",
                    "diamonds",
                    "circles",
                    "rounded rectangles",
                ],
                "supports_subgraphs": True,
                "supports_styling": True,
            },
            "sequence": {
                "name": "Sequence Diagram",
                "description": "Interaction diagrams showing message exchanges between participants",
                "syntax_start": ["sequenceDiagram"],
                "use_cases": [
                    "API interactions",
                    "System communications",
                    "Protocol documentation",
                ],
                "complexity": "medium",
                "features": [
                    "participants",
                    "messages",
                    "activation boxes",
                    "notes",
                    "loops",
                ],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "class": {
                "name": "Class Diagram",
                "description": "UML class diagrams showing classes, attributes, methods, and relationships",
                "syntax_start": ["classDiagram"],
                "use_cases": [
                    "Software architecture",
                    "Object modeling",
                    "System design",
                ],
                "complexity": "complex",
                "features": [
                    "classes",
                    "attributes",
                    "methods",
                    "relationships",
                    "interfaces",
                ],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "state": {
                "name": "State Diagram",
                "description": "State machine diagrams showing states and transitions",
                "syntax_start": ["stateDiagram", "stateDiagram-v2"],
                "use_cases": ["State machines", "Workflow states", "System behavior"],
                "complexity": "medium",
                "features": [
                    "states",
                    "transitions",
                    "composite states",
                    "choice points",
                ],
                "supports_subgraphs": True,
                "supports_styling": True,
            },
            "er": {
                "name": "Entity Relationship Diagram",
                "description": "Database entity relationship diagrams",
                "syntax_start": ["erDiagram"],
                "use_cases": [
                    "Database design",
                    "Data modeling",
                    "Schema documentation",
                ],
                "complexity": "medium",
                "features": ["entities", "attributes", "relationships", "cardinality"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "journey": {
                "name": "User Journey",
                "description": "User journey mapping diagrams",
                "syntax_start": ["journey"],
                "use_cases": [
                    "User experience design",
                    "Customer journey mapping",
                    "Process analysis",
                ],
                "complexity": "simple",
                "features": ["sections", "tasks", "actors", "satisfaction scores"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "gantt": {
                "name": "Gantt Chart",
                "description": "Project timeline and task scheduling diagrams",
                "syntax_start": ["gantt"],
                "use_cases": [
                    "Project management",
                    "Timeline visualization",
                    "Task scheduling",
                ],
                "complexity": "medium",
                "features": ["tasks", "dependencies", "milestones", "sections"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "pie": {
                "name": "Pie Chart",
                "description": "Pie charts for data visualization",
                "syntax_start": ["pie"],
                "use_cases": ["Data visualization", "Proportion display", "Statistics"],
                "complexity": "simple",
                "features": ["data values", "labels", "percentages"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "gitgraph": {
                "name": "Git Graph",
                "description": "Git branching and merging visualization",
                "syntax_start": ["gitgraph"],
                "use_cases": [
                    "Git workflow documentation",
                    "Branch visualization",
                    "Version control",
                ],
                "complexity": "medium",
                "features": ["branches", "commits", "merges", "tags"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "mindmap": {
                "name": "Mind Map",
                "description": "Hierarchical mind maps for idea organization",
                "syntax_start": ["mindmap"],
                "use_cases": [
                    "Brainstorming",
                    "Idea organization",
                    "Knowledge mapping",
                ],
                "complexity": "simple",
                "features": ["root node", "branches", "sub-branches", "icons"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
            "timeline": {
                "name": "Timeline",
                "description": "Timeline diagrams for chronological events",
                "syntax_start": ["timeline"],
                "use_cases": [
                    "Historical timelines",
                    "Project milestones",
                    "Event sequences",
                ],
                "complexity": "simple",
                "features": ["periods", "events", "sections"],
                "supports_subgraphs": False,
                "supports_styling": True,
            },
        }

        # Filter by specific diagram type if requested
        if params.diagram_type:
            if params.diagram_type.value in diagram_types:
                filtered_types = {
                    params.diagram_type.value: diagram_types[params.diagram_type.value]
                }
            else:
                return create_error_response(
                    ValueError(
                        f"Diagram type '{params.diagram_type.value}' not supported"
                    ),
                    ErrorCategory.VALIDATION,
                    context={"supported_types": list(diagram_types.keys())},
                    suggestions=[f"Use one of: {', '.join(diagram_types.keys())}"],
                )
        else:
            filtered_types = diagram_types

        # Add examples if requested
        if params.include_examples:
            for type_name, type_info in filtered_types.items():
                type_info["example_code"] = _get_diagram_example(type_name)

        # Enhanced metadata
        metadata = {
            "total_types": len(diagram_types),
            "filtered_count": len(filtered_types),
            "complexity_distribution": {
                "simple": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("complexity") == "simple"
                    ]
                ),
                "medium": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("complexity") == "medium"
                    ]
                ),
                "complex": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("complexity") == "complex"
                    ]
                ),
            },
            "features_summary": {
                "supports_subgraphs": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("supports_subgraphs", False)
                    ]
                ),
                "supports_styling": len(
                    [
                        t
                        for t in diagram_types.values()
                        if t.get("supports_styling", False)
                    ]
                ),
            },
        }

        return create_success_response(
            data={
                "types": filtered_types,
                "summary": {
                    "total_supported": len(filtered_types),
                    "by_complexity": {
                        complexity: [
                            name
                            for name, info in filtered_types.items()
                            if info.get("complexity") == complexity
                        ]
                        for complexity in ["simple", "medium", "complex"]
                    },
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error listing diagram types: {e}")
        return create_error_response(
            e, ErrorCategory.SYSTEM, suggestions=["Check system configuration"]
        )


@measure_performance
def get_diagram_examples(
    diagram_type: str | None = None,
) -> dict[str, Any]:
    """
    Get example code and documentation for specific diagram types.

    This tool provides detailed examples and documentation for Mermaid diagram
    types, including syntax patterns, best practices, and common use cases.

    Args:
        diagram_type: Specific diagram type to get examples for

    Returns:
        Dictionary containing examples and documentation

    Example:
        >>> result = get_diagram_examples(diagram_type="flowchart")
        >>> print(result["data"]["example_code"])  # Flowchart example
        >>> print(result["data"]["best_practices"])  # Best practices
    """
    try:
        # Validate parameters
        params = DiagramTypeParams(diagram_type=diagram_type, include_examples=True)

        if params.diagram_type:
            # Get specific diagram type example
            example_code = _get_diagram_example(params.diagram_type.value)
            best_practices = _get_diagram_best_practices(params.diagram_type.value)

            example_data = {
                "diagram_type": params.diagram_type.value,
                "example_code": example_code,
                "best_practices": best_practices,
                "syntax_guide": _get_syntax_guide(params.diagram_type.value),
                "common_patterns": _get_common_patterns(params.diagram_type.value),
            }
        else:
            # Get examples for all diagram types
            all_examples: dict[str, dict[str, str]] = {}
            for dtype in [
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
                "timeline",
            ]:
                all_examples[dtype] = {
                    "example_code": _get_diagram_example(dtype),
                    "description": f"Example {dtype} diagram",
                }

            example_data = {
                "all_examples": all_examples,  # type: ignore[dict-item]
                "quick_reference": _get_quick_reference_guide(),
            }

        # Enhanced metadata
        metadata = {
            "examples_provided": (
                1
                if params.diagram_type
                else len(all_examples)
                if "all_examples" in locals()
                else 0
            ),
            "includes_best_practices": bool(params.diagram_type),
            "includes_syntax_guide": bool(params.diagram_type),
            "last_updated": "2024-01-01",  # Would be dynamic in real implementation
        }

        return create_success_response(data=example_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error getting diagram examples: {e}")
        return create_error_response(
            e, ErrorCategory.SYSTEM, suggestions=["Check diagram type is valid"]
        )
