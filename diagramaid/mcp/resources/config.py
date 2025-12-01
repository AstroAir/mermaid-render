"""
Configuration resources for MCP.

This module provides configuration-related resource implementations.
"""

import json

from .base import Context, ResourceError, logger


async def get_config_schema(ctx: Context) -> str:
    """
    Get configuration schema resource.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing configuration schema
    """
    try:
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Mermaid Render Configuration",
            "type": "object",
            "properties": {
                "server_url": {
                    "type": "string",
                    "description": "Mermaid.ink server URL",
                    "default": "https://mermaid.ink",
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds",
                    "default": 30.0,
                    "minimum": 1,
                    "maximum": 300,
                },
                "retries": {
                    "type": "integer",
                    "description": "Number of retry attempts",
                    "default": 3,
                    "minimum": 0,
                    "maximum": 10,
                },
                "default_theme": {
                    "type": "string",
                    "description": "Default theme name",
                    "default": "default",
                    "enum": ["default", "dark", "forest", "neutral", "base"],
                },
                "default_format": {
                    "type": "string",
                    "description": "Default output format",
                    "default": "svg",
                    "enum": ["svg", "png", "pdf"],
                },
                "validate_syntax": {
                    "type": "boolean",
                    "description": "Enable syntax validation",
                    "default": True,
                },
                "cache_enabled": {
                    "type": "boolean",
                    "description": "Enable caching",
                    "default": True,
                },
                "cache_dir": {
                    "type": "string",
                    "description": "Cache directory path",
                    "default": "~/.diagramaid_cache",
                },
                "max_cache_size": {
                    "type": "integer",
                    "description": "Maximum cache size in MB",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 10000,
                },
                "cache_ttl": {
                    "type": "integer",
                    "description": "Cache TTL in seconds",
                    "default": 3600,
                    "minimum": 60,
                    "maximum": 86400,
                },
                "default_width": {
                    "type": "integer",
                    "description": "Default output width in pixels",
                    "default": 800,
                    "minimum": 100,
                    "maximum": 4000,
                },
                "default_height": {
                    "type": "integer",
                    "description": "Default output height in pixels",
                    "default": 600,
                    "minimum": 100,
                    "maximum": 4000,
                },
                "use_local_rendering": {
                    "type": "boolean",
                    "description": "Use local rendering when available",
                    "default": True,
                },
                "log_level": {
                    "type": "string",
                    "description": "Logging level",
                    "default": "INFO",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                },
            },
        }

        return json.dumps(schema, indent=2)

    except Exception as e:
        logger.error(f"Error getting config schema: {e}")
        raise ResourceError(f"Failed to get config schema: {e}")


async def get_default_config(ctx: Context) -> str:
    """
    Get default configuration resource.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing default configuration
    """
    try:
        from ...core import MermaidConfig

        config = MermaidConfig()
        default_config = config.to_dict()

        return json.dumps(default_config, indent=2)

    except Exception as e:
        logger.error(f"Error getting default config: {e}")
        raise ResourceError(f"Failed to get default config: {e}")
