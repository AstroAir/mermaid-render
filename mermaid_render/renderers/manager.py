"""
Renderer manager for the Mermaid Render library.

This module provides the RendererManager class that orchestrates the
plugin-based rendering system, including renderer selection, fallback
handling, and error recovery.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set, Union

from ..exceptions import RenderingError, UnsupportedFormatError
from .base import BaseRenderer, RendererCapability, RenderResult
from .registry import RendererRegistry, get_global_registry
from .error_handler import ErrorContext, get_global_error_handler
from .validation import get_global_validator
from .logging_config import PerformanceLogger, LoggingContext


class RendererManager:
    """
    Manager for orchestrating the plugin-based rendering system.

    This class handles renderer selection, fallback chains, error recovery,
    and provides a unified interface for rendering operations across
    multiple renderer backends.
    """

    def __init__(
        self,
        registry: Optional[RendererRegistry] = None,
        default_fallback_enabled: bool = True,
        max_fallback_attempts: int = 3,
        fallback_timeout: float = 30.0,
    ) -> None:
        """
        Initialize the renderer manager.

        Args:
            registry: Optional renderer registry (uses global if not provided)
            default_fallback_enabled: Whether to enable fallback by default
            max_fallback_attempts: Maximum number of fallback attempts
            fallback_timeout: Timeout for each fallback attempt
        """
        self.logger = logging.getLogger(__name__)
        self.registry = registry or get_global_registry()
        self.default_fallback_enabled = default_fallback_enabled
        self.max_fallback_attempts = max_fallback_attempts
        self.fallback_timeout = fallback_timeout

        # Active renderer instances (for cleanup)
        self._active_renderers: Dict[str, BaseRenderer] = {}

        # Performance tracking
        self._stats: Dict[str, Any] = {
            "total_renders": 0,
            "successful_renders": 0,
            "failed_renders": 0,
            "fallback_uses": 0,
            "renderer_usage": {},
        }

    def render(
        self,
        mermaid_code: str,
        format: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        preferred_renderer: Optional[str] = None,
        fallback_enabled: Optional[bool] = None,
        required_capabilities: Optional[Set[RendererCapability]] = None,
        **options: Any,
    ) -> RenderResult:
        """
        Render Mermaid code using the best available renderer.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format
            theme: Optional theme name
            config: Optional configuration dictionary
            preferred_renderer: Preferred renderer name
            fallback_enabled: Whether to enable fallback (overrides default)
            required_capabilities: Required renderer capabilities
            **options: Additional rendering options

        Returns:
            RenderResult with rendered content and metadata

        Raises:
            UnsupportedFormatError: If no renderer supports the format
            RenderingError: If all renderers fail
        """
        self._stats["total_renders"] += 1
        start_time = time.time()

        # Create error context
        error_context = ErrorContext(
            format=format,
            config=config,
            input_size=len(mermaid_code),
        )

        # Validate input
        validator = get_global_validator()
        validation_result = validator.validate(
            mermaid_code=mermaid_code,
            format=format,
            renderer_name=preferred_renderer,
            strict=False,  # Use warnings instead of errors for flexibility
        )

        if not validation_result.is_valid:
            error_handler = get_global_error_handler()
            validation_error = RenderingError(f"Validation failed: {validation_result.errors}")
            error_details = error_handler.handle_error(validation_error, error_context)
            raise validation_error

        # Use sanitized input if available
        if validation_result.sanitized_input:
            mermaid_code = validation_result.sanitized_input

        # Log validation warnings
        if validation_result.warnings:
            self.logger.warning(f"Validation warnings: {validation_result.warnings}")

        # Determine fallback setting
        use_fallback = (
            fallback_enabled
            if fallback_enabled is not None
            else self.default_fallback_enabled
        )

        # Get renderer chain
        if use_fallback:
            renderer_chain = self.registry.get_fallback_chain(
                format=format,
                primary_renderer=preferred_renderer,
                max_fallbacks=self.max_fallback_attempts,
            )
        else:
            # Single renderer only
            if preferred_renderer:
                renderer_chain = [preferred_renderer]
            else:
                best_renderer = self.registry.get_best_renderer(
                    format=format,
                    required_capabilities=required_capabilities,
                )
                if best_renderer:
                    renderer_chain = [best_renderer]
                else:
                    renderer_chain = []

        if not renderer_chain:
            raise UnsupportedFormatError(
                f"No available renderer supports format '{format}'"
            )

        # Try each renderer in the chain
        last_error: Optional[Exception] = None
        attempts: List[Dict[str, Any]] = []

        for i, renderer_name in enumerate(renderer_chain):
            # Update error context for this attempt
            error_context.renderer_name = renderer_name
            error_context.attempt_number = i + 1
            error_context.total_attempts = len(renderer_chain)

            with LoggingContext(self.logger, renderer_name=renderer_name, format=format):
                try:
                    # Get or create renderer instance
                    renderer = self._get_renderer_instance(renderer_name, config or {})
                    if renderer is None:
                        self.logger.warning(f"Could not create renderer instance: {renderer_name}")
                        continue

                    # Check capabilities if required
                    if required_capabilities:
                        missing_caps = required_capabilities - renderer.get_capabilities()
                        if missing_caps:
                            self.logger.debug(
                                f"Renderer '{renderer_name}' missing required capabilities: {missing_caps}"
                            )
                            continue

                    # Attempt rendering with performance tracking
                    self.logger.debug(f"Attempting render with '{renderer_name}' (attempt {i+1})")

                    render_start = time.time()
                    result = renderer.render(
                        mermaid_code=mermaid_code,
                        format=format,
                        theme=theme,
                        config=config,
                        **options,
                    )
                    render_time = time.time() - render_start

                    # Track success
                    self._stats["successful_renders"] += 1
                    self._stats["renderer_usage"][renderer_name] = (
                        self._stats["renderer_usage"].get(renderer_name, 0) + 1
                    )

                    if i > 0:
                        self._stats["fallback_uses"] += 1

                    # Add timing information
                    result.metadata["total_render_time"] = time.time() - start_time
                    result.metadata["attempts"] = attempts + [{"renderer": renderer_name, "success": True}]

                    self.logger.info(
                        f"Successfully rendered with '{renderer_name}' "
                        f"(format: {format}, time: {result.render_time:.3f}s)"
                    )

                    return result

                except Exception as e:
                    # Handle error with enhanced error handling
                    error_context.elapsed_time = time.time() - render_start
                    error_handler = get_global_error_handler()
                    error_details = error_handler.handle_error(e, error_context)

                    last_error = e
                    attempts.append({
                        "renderer": renderer_name,
                        "success": False,
                        "error": str(e),
                        "error_code": error_details.error_code,
                        "category": error_details.category.value,
                        "severity": error_details.severity.value,
                    })

                    self.logger.warning(
                        f"Renderer '{renderer_name}' failed: {e} [{error_details.error_code}]"
                    )

                    # Continue to next renderer in fallback chain
                    continue

        # All renderers failed
        self._stats["failed_renders"] += 1

        error_msg = f"All renderers failed for format '{format}'"
        if last_error:
            error_msg += f". Last error: {last_error}"

        # Create detailed error result
        failed_result = RenderResult(
            content="",
            format=format,
            renderer_name="none",
            render_time=time.time() - start_time,
            success=False,
            error=error_msg,
            metadata={"attempts": attempts},
        )

        raise RenderingError(error_msg)

    def _get_renderer_instance(
        self,
        name: str,
        config: Dict[str, Any],
    ) -> Optional[BaseRenderer]:
        """
        Get or create a renderer instance.

        Args:
            name: Renderer name
            config: Configuration for the renderer

        Returns:
            Renderer instance or None if creation fails
        """
        # Check if we already have an active instance
        if name in self._active_renderers:
            return self._active_renderers[name]

        # Create new instance
        renderer = self.registry.create_renderer(name, **config)
        if renderer is not None:
            self._active_renderers[name] = renderer

        return renderer

    def get_available_formats(self) -> Set[str]:
        """
        Get all formats supported by available renderers.

        Returns:
            Set of supported format strings
        """
        formats: Set[str] = set()

        for name in self.registry.list_renderers(available_only=True):
            info = self.registry.get_renderer_info(name)
            if info:
                formats.update(info.supported_formats)

        return formats

    def get_renderer_status(self) -> Dict[str, Any]:
        """
        Get status of all registered renderers.

        Returns:
            Dictionary with renderer status information
        """
        status = {}

        for name in self.registry.list_renderers():
            renderer_class = self.registry.get_renderer_class(name)
            info = self.registry.get_renderer_info(name)

            if renderer_class and info:
                try:
                    temp_instance = renderer_class()
                    health = temp_instance.get_health_status()
                    temp_instance.cleanup()
                except Exception as e:
                    health = {"available": False, "error": str(e)}

                status[name] = {
                    "info": {
                        "description": info.description,
                        "supported_formats": list(info.supported_formats),
                        "capabilities": [cap.value for cap in info.capabilities],
                        "priority": info.priority.value,
                    },
                    "health": health,
                }

        return status

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance statistics
        """
        return self._stats.copy()

    def cleanup(self) -> None:
        """
        Clean up all active renderer instances.
        """
        for renderer in self._active_renderers.values():
            try:
                renderer.cleanup()
            except Exception as e:
                self.logger.warning(f"Error cleaning up renderer: {e}")

        self._active_renderers.clear()

    def __enter__(self) -> "RendererManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.cleanup()
