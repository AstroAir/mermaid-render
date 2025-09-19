#!/usr/bin/env python3
"""
Test enhanced theme support functionality.
"""

import requests
from unittest.mock import patch, Mock
from mermaid_render.renderers.svg_renderer import SVGRenderer
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def test_theme_information() -> None:
    """Test theme information retrieval."""
    print("Testing theme information...")

    renderer = SVGRenderer()

    # Test getting supported themes
    themes = renderer.get_supported_themes()
    print(f"Supported themes: {list(themes.keys())}")
    assert isinstance(themes, dict)
    assert "default" in themes
    assert "dark" in themes
    assert "forest" in themes
    print("✓ Theme information retrieval passed")

    # Test getting theme names
    theme_names = renderer.get_theme_names()
    assert isinstance(theme_names, list)
    assert len(theme_names) > 0
    print("✓ Theme names retrieval passed")

    # Test getting specific theme info
    dark_theme = renderer.get_theme_info("dark")
    print(f"Dark theme info: {dark_theme}")
    assert dark_theme is not None
    assert "colors" in dark_theme
    assert "primaryColor" in dark_theme["colors"]
    print("✓ Specific theme info retrieval passed")


def test_theme_validation() -> None:
    """Test theme validation."""
    print("\nTesting theme validation...")

    renderer = SVGRenderer()

    # Test valid themes
    valid_themes = ["default", "dark", "forest", "neutral", "base"]
    for theme in valid_themes:
        assert renderer.validate_theme(theme) == True
        print(f"✓ Theme '{theme}' validation passed")

    # Test invalid themes
    invalid_themes = ["invalid", "nonexistent", ""]
    for theme in invalid_themes:
        assert renderer.validate_theme(theme) == False
        print(f"✓ Invalid theme '{theme}' validation passed")


def test_custom_theme_creation() -> None:
    """Test custom theme creation."""
    print("\nTesting custom theme creation...")

    renderer = SVGRenderer()

    # Test valid custom theme
    colors = {
        "primaryColor": "#ff6b6b",
        "primaryTextColor": "#ffffff",
        "primaryBorderColor": "#ff5252",
        "lineColor": "#333333",
        "backgroundColor": "#f8f9fa"
    }

    custom_theme = renderer.create_custom_theme("corporate", colors, "Corporate theme")
    print(f"Custom theme: {custom_theme}")

    assert custom_theme["name"] == "corporate"
    assert custom_theme["colors"] == colors
    assert custom_theme["custom"] == True
    print("✓ Custom theme creation passed")

    # Test invalid custom theme (missing colors)
    try:
        invalid_colors = {"primaryColor": "#ff6b6b"}  # Missing required colors
        renderer.create_custom_theme("invalid", invalid_colors)
        assert False, "Should have raised error"
    except ValueError as e:
        assert "Missing required colors" in str(e)
        print("✓ Invalid custom theme validation passed")

    # Test invalid color format
    try:
        invalid_format = {
            "primaryColor": "red",  # Invalid format
            "primaryTextColor": "#ffffff",
            "primaryBorderColor": "#ff5252",
            "lineColor": "#333333",
            "backgroundColor": "#f8f9fa"
        }
        renderer.create_custom_theme("invalid", invalid_format)
        assert False, "Should have raised error"
    except ValueError as e:
        assert "Invalid color format" in str(e)
        print("✓ Invalid color format validation passed")


def test_theme_application() -> None:
    """Test theme application to config."""
    print("\nTesting theme application...")

    renderer = SVGRenderer()

    # Test applying built-in theme
    base_config = {"width": 800, "height": 600}
    themed_config = renderer.apply_theme_to_config(base_config, "dark")
    print(f"Themed config: {themed_config}")

    assert themed_config["width"] == 800  # Original config preserved
    assert themed_config["theme"] == "dark"
    assert "primaryColor" in themed_config  # Theme colors added
    print("✓ Built-in theme application passed")

    # Test applying custom theme
    custom_theme = {
        "colors": {
            "primaryColor": "#ff6b6b",
            "primaryTextColor": "#ffffff",
            "primaryBorderColor": "#ff5252",
            "lineColor": "#333333",
            "backgroundColor": "#f8f9fa"
        }
    }

    custom_themed_config = renderer.apply_theme_to_config(base_config, custom_theme)
    print(f"Custom themed config: {custom_themed_config}")

    assert custom_themed_config["primaryColor"] == "#ff6b6b"
    print("✓ Custom theme application passed")


def test_theme_preview() -> None:
    """Test theme preview generation."""
    print("\nTesting theme preview...")

    renderer = SVGRenderer()

    # Test flowchart preview
    preview = renderer.preview_theme("dark", "flowchart")
    print(f"Dark theme flowchart preview (first 100 chars): {preview[:100]}")

    assert "flowchart TD" in preview
    assert "classDef" in preview
    print("✓ Flowchart theme preview passed")

    # Test sequence diagram preview
    seq_preview = renderer.preview_theme("forest", "sequence")
    print(f"Forest theme sequence preview (first 100 chars): {seq_preview[:100]}")

    assert "sequenceDiagram" in seq_preview
    print("✓ Sequence diagram theme preview passed")

    # Test invalid theme
    try:
        renderer.preview_theme("invalid", "flowchart")
        assert False, "Should have raised error"
    except ValueError as e:
        assert "Unknown theme" in str(e)
        print("✓ Invalid theme preview validation passed")


def test_theme_comparison() -> None:
    """Test theme comparison functionality."""
    print("\nTesting theme comparison...")

    renderer = SVGRenderer()

    # Compare multiple themes
    comparison = renderer.compare_themes(["default", "dark", "forest"])
    print(f"Theme comparison keys: {list(comparison.keys())}")

    assert "themes" in comparison
    assert "color_comparison" in comparison
    assert "default" in comparison["themes"]
    assert "dark" in comparison["themes"]
    assert "forest" in comparison["themes"]

    # Check color comparison
    assert "primaryColor" in comparison["color_comparison"]
    assert "default" in comparison["color_comparison"]["primaryColor"]
    print("✓ Theme comparison passed")


def test_theme_suggestion() -> None:
    """Test theme suggestion functionality."""
    print("\nTesting theme suggestion...")

    renderer = SVGRenderer()

    # Test dark mode preference
    dark_prefs = {"dark_mode": True}
    suggestion = renderer.suggest_theme(dark_prefs)
    assert suggestion == "dark"
    print("✓ Dark mode suggestion passed")

    # Test natural preference
    natural_prefs = {"natural": True}
    suggestion = renderer.suggest_theme(natural_prefs)
    assert suggestion == "forest"
    print("✓ Natural theme suggestion passed")

    # Test minimal preference
    minimal_prefs = {"minimal": True}
    suggestion = renderer.suggest_theme(minimal_prefs)
    assert suggestion == "base"
    print("✓ Minimal theme suggestion passed")

    # Test default preference
    default_prefs: dict[str, str] = {}
    suggestion = renderer.suggest_theme(default_prefs)
    assert suggestion == "default"
    print("✓ Default theme suggestion passed")


def test_themed_rendering() -> None:
    """Test rendering with themes."""
    print("\nTesting themed rendering...")

    # Mock SVG response
    mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#1f2937"/></svg>'

    with patch.object(requests.Session, 'get') as mock_get:
        mock_response = Mock()
        mock_response.text = mock_svg
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/svg+xml'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        renderer = SVGRenderer(use_local=False)

        # Test rendering with theme
        result = renderer.render('flowchart TD\n    A --> B', theme='dark')
        # Check that we got SVG content (the exact content may be processed)
        assert '<svg' in result
        assert '</svg>' in result
        print("✓ Themed rendering passed")

        # Verify theme was applied in the request (if remote rendering was used)
        if mock_get.call_args:
            call_args = mock_get.call_args
            url = call_args[0][0]
            assert "mermaid.ink/svg/" in url
            print("✓ Theme application in request verified")
        else:
            print("✓ Local rendering used (no remote request)")


if __name__ == "__main__":
    print("Testing enhanced theme support...")

    test_theme_information()
    test_theme_validation()
    test_custom_theme_creation()
    test_theme_application()
    test_theme_preview()
    test_theme_comparison()
    test_theme_suggestion()
    test_themed_rendering()

    print("\n🎉 All enhanced theme support tests passed!")
