"""
Graphviz renderer for the Mermaid Render library.

This module provides rendering functionality by converting compatible
Mermaid diagrams to Graphviz DOT format for alternative rendering.
"""

import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from ..exceptions import RenderingError, UnsupportedFormatError
from .base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
)


class GraphvizRenderer(BaseRenderer):
    """
    Renderer that converts Mermaid diagrams to Graphviz DOT format.

    This renderer provides an alternative rendering backend by converting
    compatible Mermaid diagram types (primarily flowcharts) to Graphviz
    DOT format and using Graphviz for rendering.
    """

    def __init__(self, **config: Any) -> None:
        """
        Initialize the Graphviz renderer.

        Args:
            **config: Configuration options
        """
        super().__init__(**config)

        self.engine = config.get("engine", "dot")
        self.dpi = config.get("dpi", 96)
        self.rankdir = config.get("rankdir", "TB")
        self.node_shape = config.get("node_shape", "box")
        self.edge_style = config.get("edge_style", "solid")

    def get_info(self) -> RendererInfo:
        """
        Get renderer information and capabilities.

        Returns:
            RendererInfo object describing the Graphviz renderer
        """
        return RendererInfo(
            name="graphviz",
            description="Alternative renderer using Graphviz for compatible diagram types",
            supported_formats={"svg", "png", "pdf"},
            capabilities={
                RendererCapability.CUSTOM_CONFIG,
                RendererCapability.LOCAL_RENDERING,
                RendererCapability.PERFORMANCE_METRICS,
            },
            priority=RendererPriority.LOW,  # Lower priority as it's limited in diagram type support
            version="1.0.0",
            author="Mermaid Render Team",
            dependencies=["graphviz"],
            config_schema={
                "type": "object",
                "properties": {
                    "engine": {"type": "string", "enum": ["dot", "neato", "fdp", "sfdp", "circo"], "default": "dot"},
                    "dpi": {"type": "integer", "default": 96},
                    "rankdir": {"type": "string", "enum": ["TB", "BT", "LR", "RL"], "default": "TB"},
                    "node_shape": {"type": "string", "default": "box"},
                    "edge_style": {"type": "string", "default": "solid"},
                },
            },
        )

    def render(
        self,
        mermaid_code: str,
        format: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **options: Any,
    ) -> RenderResult:
        """
        Render Mermaid code using Graphviz.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format (svg, png, pdf)
            theme: Optional theme name (limited support)
            config: Optional configuration dictionary
            **options: Additional rendering options

        Returns:
            RenderResult containing the rendered content and metadata
        """
        if format.lower() not in {"svg", "png", "pdf"}:
            raise UnsupportedFormatError(
                f"Graphviz renderer doesn't support format '{format}'")

        start_time = time.time()

        try:
            # Check if diagram type is supported
            if not self._is_diagram_supported(mermaid_code):
                raise RenderingError("Diagram type not supported by Graphviz renderer")

            # Convert Mermaid to DOT format
            dot_code = self._convert_to_dot(mermaid_code, theme, config)

            # Render using Graphviz
            content = self._render_with_graphviz(dot_code, format.lower(), options)

            render_time = time.time() - start_time

            return RenderResult(
                content=content,
                format=format.lower(),
                renderer_name="graphviz",
                render_time=render_time,
                success=True,
                metadata={
                    "engine": self.engine,
                    "dot_lines": len(dot_code.split("\n")),
                    "conversion_method": "mermaid_to_dot",
                },
            )

        except Exception as e:
            render_time = time.time() - start_time

            return RenderResult(
                content="" if format.lower() == "svg" else b"",
                format=format.lower(),
                renderer_name="graphviz",
                render_time=render_time,
                success=False,
                error=str(e),
            )

    def _is_diagram_supported(self, mermaid_code: str) -> bool:
        """Check if the diagram type is supported by Graphviz renderer."""
        # Currently only support flowcharts
        return (
            "flowchart" in mermaid_code.lower() or
            "graph" in mermaid_code.lower()
        )

    def _convert_to_dot(
        self,
        mermaid_code: str,
        theme: Optional[str],
        config: Optional[Dict[str, Any]],
    ) -> str:
        """Convert Mermaid flowchart to Graphviz DOT format."""
        lines = mermaid_code.strip().split("\n")

        # Parse the diagram
        nodes = {}
        edges = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("%%"):
                continue

            # Skip diagram type declaration
            if line.startswith(("flowchart", "graph")):
                continue

            # Parse node definitions and edges
            if "-->" in line or "---" in line:
                # Edge definition
                edge_match = re.match(
                    r"(\w+)\s*(-->|---)\s*(\w+)(?:\s*\|\s*(.+?)\s*\|)?", line)
                if edge_match:
                    from_node, edge_type, to_node, label = edge_match.groups()
                    edges.append((from_node, to_node, label))
            else:
                # Node definition
                node_match = re.match(r"(\w+)\[(.+?)\]", line)
                if node_match:
                    node_id, node_label = node_match.groups()
                    nodes[node_id] = node_label

        # Generate DOT code
        dot_lines = [
            f"digraph G {{",
            f"    rankdir={self.rankdir};",
            f"    node [shape={self.node_shape}];",
        ]

        # Add theme-based styling
        if theme == "dark":
            dot_lines.extend([
                "    bgcolor=\"#1f2937\";",
                "    node [style=filled, fillcolor=\"#374151\", fontcolor=white];",
                "    edge [color=white];",
            ])
        elif theme == "forest":
            dot_lines.extend([
                "    node [style=filled, fillcolor=\"#22c55e\", fontcolor=white];",
                "    edge [color=\"#15803d\"];",
            ])

        # Add nodes
        for node_id, label in nodes.items():
            dot_lines.append(f'    {node_id} [label="{label}"];')

        # Add edges
        for from_node, to_node, label in edges:
            if label:
                dot_lines.append(f'    {from_node} -> {to_node} [label="{label}"];')
            else:
                dot_lines.append(f'    {from_node} -> {to_node};')

        dot_lines.append("}")

        return "\n".join(dot_lines)

    def _render_with_graphviz(
        self,
        dot_code: str,
        format: str,
        options: Dict[str, Any],
    ) -> Any:
        """Render DOT code using Graphviz."""
        try:
            import graphviz  # type: ignore[import-untyped]

            # Create Graphviz source
            source = graphviz.Source(dot_code)

            # Set format and engine
            source.format = format
            source.engine = self.engine

            # Render to string/bytes
            if format == "svg":
                return source.pipe(format="svg", encoding="utf-8")
            else:
                return source.pipe(format=format)

        except ImportError:
            raise RenderingError(
                "Graphviz renderer requires graphviz package. Install with: pip install graphviz"
            )

    def is_available(self) -> bool:
        """
        Check if Graphviz renderer is available.

        Returns:
            True if Graphviz is installed and working
        """
        try:
            import graphviz

            # Test with simple graph
            test_dot = "digraph { A -> B; }"
            source = graphviz.Source(test_dot)
            source.pipe(format="svg")
            return True

        except ImportError:
            return False
        except Exception:
            return False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Graphviz renderer configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        valid_engines = {"dot", "neato", "fdp", "sfdp", "circo"}
        valid_rankdirs = {"TB", "BT", "LR", "RL"}

        if "engine" in config and config["engine"] not in valid_engines:
            return False

        if "rankdir" in config and config["rankdir"] not in valid_rankdirs:
            return False

        if "dpi" in config:
            if not isinstance(config["dpi"], int) or config["dpi"] <= 0:
                return False

        return True

    def cleanup(self) -> None:
        """Clean up Graphviz renderer resources."""
        # No persistent resources to clean up
        self.logger.debug("Graphviz renderer cleanup completed")
