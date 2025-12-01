"""
Theme resources for MCP.

This module provides theme-related resource implementations.
"""

import json

from .base import Context, ResourceError, logger


async def get_themes_resource(ctx: Context) -> str:
    """
    Get all available themes resource.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing themes data
    """
    try:
        themes_data = {
            "themes": {
                "default": {
                    "name": "default",
                    "description": "Default theme with light background",
                    "colors": {
                        "primary": "#0066cc",
                        "secondary": "#ffffff",
                        "background": "#ffffff",
                    },
                },
                "dark": {
                    "name": "dark",
                    "description": "Dark theme with dark background",
                    "colors": {
                        "primary": "#58a6ff",
                        "secondary": "#f0f6fc",
                        "background": "#0d1117",
                    },
                },
                "forest": {
                    "name": "forest",
                    "description": "Forest theme with green colors",
                    "colors": {
                        "primary": "#1f7a1f",
                        "secondary": "#ffffff",
                        "background": "#f0fff0",
                    },
                },
                "neutral": {
                    "name": "neutral",
                    "description": "Neutral theme with gray colors",
                    "colors": {
                        "primary": "#666666",
                        "secondary": "#ffffff",
                        "background": "#f8f9fa",
                    },
                },
                "base": {
                    "name": "base",
                    "description": "Base theme with minimal styling",
                    "colors": {
                        "primary": "#000000",
                        "secondary": "#ffffff",
                        "background": "#ffffff",
                    },
                },
            },
            "default_theme": "default",
            "total_count": 5,
            "custom_themes_supported": True,
        }

        return json.dumps(themes_data, indent=2)

    except Exception as e:
        logger.error(f"Error getting themes resource: {e}")
        raise ResourceError(f"Failed to get themes: {e}")


async def get_theme_details(ctx: Context, theme_name: str) -> str:
    """
    Get details for a specific theme.

    Args:
        ctx: MCP context
        theme_name: Name of the theme

    Returns:
        JSON string containing theme details
    """
    try:
        theme_details = {
            "default": {
                "name": "default",
                "description": "Default theme with light background and blue accents",
                "colors": {
                    "primary": "#0066cc",
                    "secondary": "#ffffff",
                    "background": "#ffffff",
                    "text": "#000000",
                    "border": "#cccccc",
                },
                "usage": "Best for general purpose diagrams and documentation",
                "compatibility": "All diagram types",
            },
            "dark": {
                "name": "dark",
                "description": "Dark theme optimized for dark mode interfaces",
                "colors": {
                    "primary": "#58a6ff",
                    "secondary": "#f0f6fc",
                    "background": "#0d1117",
                    "text": "#f0f6fc",
                    "border": "#30363d",
                },
                "usage": "Ideal for dark mode applications and presentations",
                "compatibility": "All diagram types",
            },
            "forest": {
                "name": "forest",
                "description": "Nature-inspired theme with green color palette",
                "colors": {
                    "primary": "#1f7a1f",
                    "secondary": "#ffffff",
                    "background": "#f0fff0",
                    "text": "#000000",
                    "border": "#90ee90",
                },
                "usage": "Great for environmental, growth, or nature-related diagrams",
                "compatibility": "All diagram types",
            },
            "neutral": {
                "name": "neutral",
                "description": "Professional neutral theme with gray tones",
                "colors": {
                    "primary": "#666666",
                    "secondary": "#ffffff",
                    "background": "#f8f9fa",
                    "text": "#000000",
                    "border": "#dee2e6",
                },
                "usage": "Perfect for business and professional documentation",
                "compatibility": "All diagram types",
            },
            "base": {
                "name": "base",
                "description": "Minimal base theme with basic styling",
                "colors": {
                    "primary": "#000000",
                    "secondary": "#ffffff",
                    "background": "#ffffff",
                    "text": "#000000",
                    "border": "#000000",
                },
                "usage": "Minimal styling for custom theme development",
                "compatibility": "All diagram types",
            },
        }

        if theme_name not in theme_details:
            raise ResourceError(f"Theme '{theme_name}' not found")

        return json.dumps(theme_details[theme_name], indent=2)

    except Exception as e:
        logger.error(f"Error getting theme details for {theme_name}: {e}")
        raise ResourceError(f"Failed to get theme details: {e}")
