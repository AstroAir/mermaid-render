"""
Node.js renderer for the Mermaid Render library.

This module provides rendering functionality using the Mermaid CLI
via Node.js subprocess for local, high-quality diagram rendering.
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from .base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
)


class NodeJSRenderer(BaseRenderer):
    """
    Renderer using Node.js and Mermaid CLI for local rendering.

    This renderer uses the official Mermaid CLI (@mermaid-js/mermaid-cli)
    to render diagrams locally via Node.js subprocess. It provides
    high-quality rendering without network dependencies.
    """

    def __init__(self, **config: Any) -> None:
        """
        Initialize the Node.js renderer.

        Args:
            **config: Configuration options
        """
        super().__init__(**config)

        self.mmdc_path = config.get("mmdc_path", "mmdc")
        self.node_path = config.get("node_path", "node")
        self.timeout = config.get("timeout", 30.0)
        self.puppeteer_config = config.get("puppeteer_config", {})
        self.temp_dir = config.get("temp_dir")

        # Validate Node.js and mmdc availability
        self._validate_dependencies()

    def get_info(self) -> RendererInfo:
        """
        Get renderer information and capabilities.

        Returns:
            RendererInfo object describing the Node.js renderer
        """
        return RendererInfo(
            name="nodejs",
            description="Local renderer using Node.js and Mermaid CLI",
            supported_formats={"svg", "png", "pdf"},
            capabilities={
                RendererCapability.VALIDATION,
                RendererCapability.THEME_SUPPORT,
                RendererCapability.CUSTOM_CONFIG,
                RendererCapability.LOCAL_RENDERING,
            },
            priority=RendererPriority.HIGH,
            version="1.0.0",
            author="Mermaid Render Team",
            dependencies=["nodejs", "@mermaid-js/mermaid-cli"],
            config_schema={
                "type": "object",
                "properties": {
                    "mmdc_path": {"type": "string", "default": "mmdc"},
                    "node_path": {"type": "string", "default": "node"},
                    "timeout": {"type": "number", "default": 30.0},
                    "puppeteer_config": {"type": "object", "default": {}},
                    "temp_dir": {"type": "string"},
                },
            },
        )

    def render(
        self,
        mermaid_code: str,
        format: str,
        theme: str | None = None,
        config: dict[str, Any] | None = None,
        **options: Any,
    ) -> RenderResult:
        """
        Render Mermaid code using Node.js CLI.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format (svg, png, pdf)
            theme: Optional theme name
            config: Optional configuration dictionary
            **options: Additional rendering options

        Returns:
            RenderResult containing the rendered content and metadata
        """
        from ..exceptions import RenderingError, UnsupportedFormatError

        if format.lower() not in {"svg", "png", "pdf"}:
            raise UnsupportedFormatError(
                f"Node.js renderer doesn't support format '{format}'"
            )

        start_time = time.time()

        try:
            # Create temporary files
            with tempfile.TemporaryDirectory(dir=self.temp_dir) as temp_dir:
                temp_path = Path(temp_dir)
                input_file = temp_path / "diagram.mmd"
                output_file = temp_path / f"diagram.{format.lower()}"
                config_file = temp_path / "config.json"

                # Write Mermaid code to input file
                input_file.write_text(mermaid_code, encoding="utf-8")

                # Create configuration file if needed
                mermaid_config = self._create_mermaid_config(theme, config, options)
                if mermaid_config:
                    config_file.write_text(json.dumps(mermaid_config), encoding="utf-8")

                # Build mmdc command
                cmd = [
                    self.mmdc_path,
                    "-i",
                    str(input_file),
                    "-o",
                    str(output_file),
                    "-t",
                    theme or "default",
                ]

                # Add configuration file if created
                if mermaid_config:
                    cmd.extend(["-c", str(config_file)])

                # Add format-specific options
                if format.lower() == "png":
                    if "width" in options:
                        cmd.extend(["-w", str(options["width"])])
                    if "height" in options:
                        cmd.extend(["-H", str(options["height"])])
                    if "background" in options:
                        cmd.extend(["-b", options["background"]])

                elif format.lower() == "pdf":
                    if "page_size" in options:
                        cmd.extend(["--pdfFit"])

                # Execute mmdc command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir,
                )

                if result.returncode != 0:
                    error_msg = f"mmdc command failed: {result.stderr}"
                    raise RenderingError(error_msg)

                # Read the output file
                if not output_file.exists():
                    raise RenderingError(f"Output file not created: {output_file}")

                if format.lower() == "svg":
                    content: str | bytes = output_file.read_text(encoding="utf-8")
                else:
                    content = output_file.read_bytes()

                render_time = time.time() - start_time

                # Create metadata
                metadata = {
                    "mmdc_version": self._get_mmdc_version(),
                    "command": " ".join(cmd),
                    "output_size": len(content),
                }

                if result.stdout:
                    metadata["stdout"] = result.stdout

                return RenderResult(
                    content=content,
                    format=format.lower(),
                    renderer_name="nodejs",
                    render_time=render_time,
                    success=True,
                    metadata=metadata,
                )

        except subprocess.TimeoutExpired:
            render_time = time.time() - start_time
            return RenderResult(
                content="" if format.lower() == "svg" else b"",
                format=format.lower(),
                renderer_name="nodejs",
                render_time=render_time,
                success=False,
                error=f"Rendering timeout after {self.timeout}s",
            )
        except Exception as e:
            render_time = time.time() - start_time
            return RenderResult(
                content="" if format.lower() == "svg" else b"",
                format=format.lower(),
                renderer_name="nodejs",
                render_time=render_time,
                success=False,
                error=str(e),
            )

    def _create_mermaid_config(
        self,
        theme: str | None,
        config: dict[str, Any] | None,
        options: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Create Mermaid configuration for CLI."""
        mermaid_config = {}

        # Add theme configuration
        if theme and theme != "default":
            mermaid_config["theme"] = theme

        # Add custom configuration
        if config:
            mermaid_config.update(config)

        # Add puppeteer configuration
        if self.puppeteer_config:
            mermaid_config["puppeteerConfig"] = self.puppeteer_config

        return mermaid_config if mermaid_config else None

    def _validate_dependencies(self) -> None:
        """Validate that Node.js and mmdc are available."""
        # Check Node.js
        try:
            subprocess.run(
                [self.node_path, "--version"], capture_output=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("Node.js not found or not working")

        # Check mmdc
        try:
            subprocess.run(
                [self.mmdc_path, "--version"], capture_output=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("mmdc (Mermaid CLI) not found or not working")

    def _get_mmdc_version(self) -> str:
        """Get mmdc version."""
        try:
            result = subprocess.run(
                [self.mmdc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def is_available(self) -> bool:
        """
        Check if Node.js renderer is available.

        Returns:
            True if Node.js and mmdc are available
        """
        try:
            # Check Node.js
            node_result = subprocess.run(
                [self.node_path, "--version"],
                capture_output=True,
                timeout=5,
            )

            # Check mmdc
            mmdc_result = subprocess.run(
                [self.mmdc_path, "--version"],
                capture_output=True,
                timeout=5,
            )

            return node_result.returncode == 0 and mmdc_result.returncode == 0

        except Exception:
            return False

    def validate_config(self, config: dict[str, Any]) -> bool:
        """
        Validate Node.js renderer configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Basic validation for Node.js renderer config
        valid_keys = {
            "mmdc_path",
            "node_path",
            "timeout",
            "puppeteer_config",
            "temp_dir",
        }

        # Check for unknown keys
        unknown_keys = set(config.keys()) - valid_keys
        if unknown_keys:
            self.logger.warning(
                f"Unknown config keys for Node.js renderer: {unknown_keys}"
            )

        # Validate specific values
        if "timeout" in config:
            if (
                not isinstance(config["timeout"], (int, float))
                or config["timeout"] <= 0
            ):
                return False

        if "mmdc_path" in config:
            if (
                not isinstance(config["mmdc_path"], str)
                or not config["mmdc_path"].strip()
            ):
                return False

        if "node_path" in config:
            if (
                not isinstance(config["node_path"], str)
                or not config["node_path"].strip()
            ):
                return False

        if "puppeteer_config" in config:
            if not isinstance(config["puppeteer_config"], dict):
                return False

        if "temp_dir" in config:
            if not isinstance(config["temp_dir"], str):
                return False

        return True

    def cleanup(self) -> None:
        """Clean up Node.js renderer resources."""
        # No persistent resources to clean up for subprocess-based renderer
        self.logger.debug("Node.js renderer cleanup completed")
