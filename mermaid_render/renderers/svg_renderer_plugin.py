"""
SVG renderer plugin adapter for the plugin-based architecture.

This module wraps the existing SVGRenderer to work with the new
plugin-based rendering system.
"""

import time
from typing import Any, Dict, Optional, Set

from ..exceptions import UnsupportedFormatError, RenderingError
from .base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
)
from .svg_renderer import SVGRenderer


class SVGRendererPlugin(BaseRenderer):
    """
    Plugin adapter for the existing SVGRenderer.

    This class wraps the existing SVGRenderer to work with the new
    plugin-based architecture while maintaining all existing functionality.
    """

    def __init__(self, **config: Any) -> None:
        """
        Initialize the SVG renderer plugin.

        Args:
            **config: Configuration options passed to SVGRenderer
        """
        super().__init__(**config)

        # Extract SVGRenderer-specific config
        svg_config = {
            "server_url": config.get("server_url", "https://mermaid.ink"),
            "timeout": config.get("timeout", 30.0),
            "use_local": config.get("use_local", True),
            "max_retries": config.get("max_retries", 3),
            "backoff_factor": config.get("backoff_factor", 0.3),
            "cache_enabled": config.get("cache_enabled", True),
            "cache_dir": config.get("cache_dir"),
            "cache_ttl": config.get("cache_ttl", 3600),
        }

        # Remove None values
        svg_config = {k: v for k, v in svg_config.items() if v is not None}

        # Create the underlying SVGRenderer
        self._svg_renderer = SVGRenderer(**svg_config)

    def get_info(self) -> RendererInfo:
        """
        Get renderer information and capabilities.

        Returns:
            RendererInfo object describing the SVG renderer
        """
        return RendererInfo(
            name="svg",
            description="SVG renderer using mermaid-py and mermaid.ink service",
            supported_formats={"svg"},
            capabilities={
                RendererCapability.CACHING,
                RendererCapability.VALIDATION,
                RendererCapability.BATCH_PROCESSING,
                RendererCapability.THEME_SUPPORT,
                RendererCapability.CUSTOM_CONFIG,
                RendererCapability.PERFORMANCE_METRICS,
                RendererCapability.FALLBACK_SUPPORT,
                RendererCapability.LOCAL_RENDERING,
                RendererCapability.REMOTE_RENDERING,
            },
            priority=RendererPriority.HIGH,
            version="1.0.0",
            author="Mermaid Render Team",
            dependencies=["mermaid-py", "requests"],
            config_schema={
                "type": "object",
                "properties": {
                    "server_url": {"type": "string", "default": "https://mermaid.ink"},
                    "timeout": {"type": "number", "default": 30.0},
                    "use_local": {"type": "boolean", "default": True},
                    "max_retries": {"type": "integer", "default": 3},
                    "cache_enabled": {"type": "boolean", "default": True},
                    "cache_ttl": {"type": "integer", "default": 3600},
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
        Render Mermaid code to SVG format.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format (must be 'svg')
            theme: Optional theme name
            config: Optional configuration dictionary
            **options: Additional rendering options

        Returns:
            RenderResult containing the SVG content and metadata

        Raises:
            UnsupportedFormatError: If format is not 'svg'
            RenderingError: If rendering fails
        """
        if format.lower() != "svg":
            raise UnsupportedFormatError(
                f"SVG renderer only supports 'svg' format, got '{format}'")

        start_time = time.time()

        try:
            # Extract SVGRenderer-specific options
            validate = options.get("validate", True)
            sanitize = options.get("sanitize", True)
            optimize = options.get("optimize", False)

            # Render using the underlying SVGRenderer
            svg_content = self._svg_renderer.render(
                mermaid_code=mermaid_code,
                theme=theme,
                config=config,
                validate=validate,
                sanitize=sanitize,
                optimize=optimize,
            )

            render_time = time.time() - start_time

            # Get performance metrics if available
            metadata = {}
            if hasattr(self._svg_renderer, "get_performance_metrics"):
                try:
                    metrics = self._svg_renderer.get_performance_metrics()
                    metadata["performance_metrics"] = metrics
                except Exception:
                    pass

            # Get cache stats if available
            if hasattr(self._svg_renderer, "get_cache_stats"):
                try:
                    cache_stats = self._svg_renderer.get_cache_stats()
                    metadata["cache_stats"] = cache_stats
                except Exception:
                    pass

            return RenderResult(
                content=svg_content,
                format="svg",
                renderer_name="svg",
                render_time=render_time,
                success=True,
                metadata=metadata,
            )

        except Exception as e:
            render_time = time.time() - start_time

            return RenderResult(
                content="",
                format="svg",
                renderer_name="svg",
                render_time=render_time,
                success=False,
                error=str(e),
            )

    def is_available(self) -> bool:
        """
        Check if SVG renderer is available.

        Returns:
            True if renderer is available, False otherwise
        """
        try:
            # Check if underlying renderer can get server status
            if hasattr(self._svg_renderer, "get_server_status"):
                status = self._svg_renderer.get_server_status()
                if isinstance(status, dict):
                    return bool(status.get("available", False))
            return True
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get detailed health status of the SVG renderer.

        Returns:
            Dictionary with health status information
        """
        base_status = super().get_health_status()

        # Add SVG-specific health information
        try:
            if hasattr(self._svg_renderer, "get_server_status"):
                server_status = self._svg_renderer.get_server_status()
                base_status["server_status"] = server_status

            if hasattr(self._svg_renderer, "get_cache_stats"):
                cache_stats = self._svg_renderer.get_cache_stats()
                base_status["cache_stats"] = cache_stats

        except Exception as e:
            base_status["health_check_error"] = str(e)

        return base_status

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate SVG renderer configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Basic validation for SVG renderer config
        valid_keys = {
            "server_url", "timeout", "use_local", "max_retries",
            "backoff_factor", "cache_enabled", "cache_dir", "cache_ttl"
        }

        # Check for unknown keys
        unknown_keys = set(config.keys()) - valid_keys
        if unknown_keys:
            self.logger.warning(f"Unknown config keys for SVG renderer: {unknown_keys}")

        # Validate specific values
        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
                return False

        if "max_retries" in config:
            if not isinstance(config["max_retries"], int) or config["max_retries"] < 0:
                return False

        if "cache_ttl" in config:
            if not isinstance(config["cache_ttl"], int) or config["cache_ttl"] < 0:
                return False

        return True

    def cleanup(self) -> None:
        """
        Clean up SVG renderer resources.
        """
        try:
            if hasattr(self._svg_renderer, "close"):
                self._svg_renderer.close()
        except Exception as e:
            self.logger.warning(f"Error during SVG renderer cleanup: {e}")

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get cache statistics from the underlying renderer.

        Returns:
            Cache statistics or None if not available
        """
        if hasattr(self._svg_renderer, "get_cache_stats"):
            try:
                return self._svg_renderer.get_cache_stats()
            except Exception:
                pass
        return None

    def clear_cache(self) -> int:
        """
        Clear renderer cache.

        Returns:
            Number of cache entries cleared
        """
        if hasattr(self._svg_renderer, "clear_cache"):
            try:
                return self._svg_renderer.clear_cache()
            except Exception:
                pass
        return 0
