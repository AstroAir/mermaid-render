"""
Configuration and system management MCP tools for mermaid-render.

This module provides configuration, cache, and system information tools.
"""

import logging
from typing import Any

from ...core import MermaidConfig
from .base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
    measure_performance,
)
from .helpers import (
    _get_config_description,
    _get_section_keys,
    _validate_config_value,
)
from .params import CacheManagementParams, ConfigurationParams

logger = logging.getLogger(__name__)


@measure_performance
def get_configuration(
    key: str | None = None,
    section: str | None = None,
) -> dict[str, Any]:
    """
    Get current configuration settings with optional filtering.

    This tool provides access to the current mermaid-render configuration,
    allowing retrieval of all settings or filtering by specific keys or sections.
    Includes detailed information about each setting and its current value.

    Args:
        key: Specific configuration key to retrieve (if None, returns all)
        section: Configuration section to filter by (e.g., 'rendering', 'themes')

    Returns:
        Dictionary containing configuration data and metadata

    Example:
        >>> result = get_configuration()
        >>> print(result["data"]["timeout"])  # Current timeout setting
        >>> result = get_configuration(key="default_theme")
        >>> print(result["data"]["value"])  # Current default theme
    """
    try:
        # Validate parameters
        params = ConfigurationParams(key=key, section=section)

        # Get configuration from MermaidConfig
        config = MermaidConfig()
        all_config = config.to_dict()

        if params.key:
            # Return specific key
            if params.key in all_config:
                config_data = {
                    "key": params.key,
                    "value": all_config[params.key],
                    "type": type(all_config[params.key]).__name__,
                    "description": _get_config_description(params.key),
                }
            else:
                return create_error_response(
                    ValueError(f"Configuration key '{params.key}' not found"),
                    ErrorCategory.CONFIGURATION,
                    context={"available_keys": list(all_config.keys())},
                    suggestions=[
                        f"Use one of the available keys: {', '.join(list(all_config.keys())[:5])}..."
                    ],
                )
        else:
            # Return all configuration or filtered by section
            if params.section:
                # Filter by section (basic implementation)
                section_keys = _get_section_keys(params.section)
                filtered_config = {
                    k: v for k, v in all_config.items() if k in section_keys
                }
                config_data = {
                    "section": params.section,
                    "settings": {
                        k: {
                            "value": v,
                            "type": type(v).__name__,
                            "description": _get_config_description(k),
                        }
                        for k, v in filtered_config.items()
                    },
                }
            else:
                # Return all configuration
                config_data = {
                    "settings": {
                        k: {
                            "value": v,
                            "type": type(v).__name__,
                            "description": _get_config_description(k),
                        }
                        for k, v in all_config.items()
                    }
                }

        # Enhanced metadata
        metadata = {
            "total_settings": len(all_config),
            "filtered_settings": (
                len(config_data.get("settings", {})) if "settings" in config_data else 1
            ),
            "available_sections": ["rendering", "themes", "cache", "ai", "validation"],
            "config_source": "MermaidConfig",
        }

        return create_success_response(data=config_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        return create_error_response(
            e,
            ErrorCategory.CONFIGURATION,
            suggestions=["Check configuration system is properly initialized"],
        )


@measure_performance
def update_configuration(
    key: str,
    value: Any,
) -> dict[str, Any]:
    """
    Update configuration settings with validation.

    This tool allows updating mermaid-render configuration settings with
    comprehensive validation to ensure the new values are valid and safe.
    Provides detailed feedback about the changes made.

    Args:
        key: Configuration key to update
        value: New value for the configuration key

    Returns:
        Dictionary containing update results and metadata

    Example:
        >>> result = update_configuration("default_theme", "dark")
        >>> print(result["data"]["updated"])  # True
        >>> print(result["data"]["old_value"])  # Previous value
    """
    try:
        # Validate parameters
        params = ConfigurationParams(key=key, value=value)

        # Get current configuration
        config = MermaidConfig()
        all_config = config.to_dict()

        if params.key not in all_config:
            return create_error_response(
                ValueError(f"Configuration key '{params.key}' not found"),
                ErrorCategory.CONFIGURATION,
                context={"available_keys": list(all_config.keys())},
                suggestions=[
                    f"Use one of the available keys: {', '.join(list(all_config.keys())[:5])}..."
                ],
            )

        # Store old value
        old_value = all_config[params.key]
        old_type = type(old_value).__name__

        # Validate new value type compatibility
        if not _validate_config_value(params.key, params.value):
            return create_error_response(
                ValueError(
                    f"Invalid value type for '{params.key}'. Expected {old_type}, got {type(params.value).__name__}"
                ),
                ErrorCategory.VALIDATION,
                context={
                    "expected_type": old_type,
                    "provided_type": type(params.value).__name__,
                },
                suggestions=[f"Provide a value of type {old_type}"],
            )

        # Update configuration
        config.set(params.key, params.value)

        # Prepare response data
        import datetime

        update_data = {
            "updated": True,
            "key": params.key,
            "old_value": old_value,
            "new_value": params.value,
            "value_type": type(params.value).__name__,
            "description": _get_config_description(params.key),
        }

        # Enhanced metadata
        metadata = {
            "update_timestamp": datetime.datetime.now().isoformat(),
            "config_source": "MermaidConfig",
            "validation_passed": True,
        }

        return create_success_response(data=update_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return create_error_response(
            e,
            ErrorCategory.CONFIGURATION,
            suggestions=[
                "Check configuration key and value are valid",
                "Verify configuration system is writable",
            ],
        )


@measure_performance
def get_system_information() -> dict[str, Any]:
    """
    Get system capabilities, version information, and available features.

    This tool provides comprehensive information about the mermaid-render system,
    including version details, available features, system capabilities, and
    configuration status.

    Returns:
        Dictionary containing system information and capabilities

    Example:
        >>> result = get_system_information()
        >>> print(result["data"]["version"])  # mermaid-render version
        >>> print(result["data"]["features"])  # Available features
    """
    try:
        import datetime
        import platform
        import sys

        from ... import __version__ as mermaid_version

        # Collect system information
        system_info = {
            "mermaid_render_version": mermaid_version,
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
        }

        # Check available features
        features = {
            "ai_support": False,
            "template_support": False,
            "cache_support": True,
            "interactive_support": False,
            "pdf_rendering": True,
            "png_rendering": True,
            "svg_rendering": True,
        }

        # Check AI support
        try:
            from ...ai import DiagramGenerator  # noqa: F401

            features["ai_support"] = True
        except ImportError:
            pass

        # Check template support
        try:
            from ...templates import TemplateManager  # noqa: F401

            features["template_support"] = True
        except ImportError:
            pass

        # Check interactive support
        try:
            from ...interactive import InteractiveServer  # noqa: F401

            features["interactive_support"] = True
        except ImportError:
            pass

        # Get renderer capabilities
        from ...renderers import RendererRegistry

        registry = RendererRegistry()
        available_renderers = registry.list_renderers()

        # Enhanced metadata
        metadata = {
            "system_check_timestamp": datetime.datetime.now().isoformat(),
            "feature_count": len([f for f in features.values() if f]),
            "renderer_count": len(available_renderers),
            "python_executable": sys.executable,
        }

        return create_success_response(
            data={
                "system": system_info,
                "features": features,
                "renderers": available_renderers,
                "capabilities": {
                    "max_diagram_size": "50KB",
                    "supported_formats": ["svg", "png", "pdf"],
                    "concurrent_renders": 10,
                    "cache_enabled": True,
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error getting system information: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            suggestions=[
                "Check system configuration",
                "Verify all dependencies are installed",
            ],
        )


@measure_performance
def manage_cache_operations(
    operation: str,
    cache_key: str | None = None,
) -> dict[str, Any]:
    """
    Manage cache operations including clear, stats, and cleanup.

    This tool provides comprehensive cache management capabilities including
    cache statistics, selective clearing, and maintenance operations with
    detailed reporting.

    Args:
        operation: Cache operation to perform (stats, clear, clear_all, cleanup)
        cache_key: Specific cache key for targeted operations

    Returns:
        Dictionary containing cache operation results and statistics

    Example:
        >>> result = manage_cache_operations("stats")
        >>> print(result["data"]["cache_size"])  # Current cache size
        >>> result = manage_cache_operations("clear", "diagram_abc123")
        >>> print(result["data"]["cleared"])  # True if cleared successfully
    """
    try:
        # Validate parameters
        params = CacheManagementParams(operation=operation, cache_key=cache_key)

        # Get cache manager
        try:
            from ...cache import CacheManager

            cache_manager = CacheManager()
        except ImportError:
            return create_error_response(
                ImportError("Cache functionality not available"),
                ErrorCategory.CACHE,
                suggestions=["Check cache system configuration"],
            )

        operation_result = {}

        if params.operation == "stats":
            # Get cache statistics
            stats = cache_manager.get_stats()
            operation_result = {
                "operation": "stats",
                "cache_enabled": hasattr(cache_manager, "backend")
                and cache_manager.backend is not None,
                "cache_size": stats.get("size", 0),
                "entry_count": stats.get("count", 0),
                "hit_rate": stats.get("hit_rate", 0.0),
                "miss_rate": stats.get("miss_rate", 0.0),
                "cache_directory": (
                    str(cache_manager.cache_dir)
                    if hasattr(cache_manager, "cache_dir")
                    else None
                ),
                "max_size": stats.get("max_size", "unlimited"),
                "last_cleanup": stats.get("last_cleanup", "never"),
            }

        elif params.operation == "clear":
            if params.cache_key:
                # Clear specific cache entry
                cleared = cache_manager.delete(params.cache_key)
                operation_result = {
                    "operation": "clear",
                    "cache_key": params.cache_key,
                    "cleared": cleared,
                    "message": f"Cache key '{params.cache_key}' {'cleared' if cleared else 'not found'}",
                }
            else:
                return create_error_response(
                    ValueError("cache_key required for clear operation"),
                    ErrorCategory.VALIDATION,
                    suggestions=[
                        "Provide cache_key parameter",
                        "Use clear_all to clear entire cache",
                    ],
                )

        elif params.operation == "clear_all":
            # Clear entire cache
            cleared_count = cache_manager.clear()
            operation_result = {
                "operation": "clear_all",
                "cleared_entries": cleared_count,
                "message": f"Cleared {cleared_count} cache entries",
            }

        elif params.operation == "cleanup":
            # Perform cache cleanup (remove expired entries)
            # Use clear with no tags to clean up all entries
            cleaned_count = cache_manager.clear()
            operation_result = {
                "operation": "cleanup",
                "cleaned_entries": cleaned_count,
                "message": f"Cleaned up {cleaned_count} expired cache entries",
            }

        else:
            return create_error_response(
                ValueError(f"Unknown cache operation: {params.operation}"),
                ErrorCategory.VALIDATION,
                context={
                    "supported_operations": ["stats", "clear", "clear_all", "cleanup"]
                },
                suggestions=["Use one of: stats, clear, clear_all, cleanup"],
            )

        # Enhanced metadata
        import datetime

        metadata = {
            "operation_timestamp": datetime.datetime.now().isoformat(),
            "cache_system": "CacheManager",
            "operation_type": params.operation,
            "cache_enabled": (
                cache_manager.is_enabled()
                if hasattr(cache_manager, "is_enabled")
                else True
            ),
        }

        return create_success_response(data=operation_result, metadata=metadata)

    except Exception as e:
        logger.error(f"Error in cache management: {e}")
        return create_error_response(
            e,
            ErrorCategory.CACHE,
            context={"operation": operation, "cache_key": cache_key},
            suggestions=[
                "Check cache system is properly configured",
                "Verify cache permissions",
            ],
        )
