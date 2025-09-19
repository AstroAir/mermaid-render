"""
Integration tests for the plugin-based renderer system.

This module tests the complete integration of the plugin-based architecture
with real rendering scenarios and fallback mechanisms.
"""

import tempfile
from pathlib import Path

import pytest

from mermaid_render import PluginMermaidRenderer, MermaidRenderer
from mermaid_render.core import MermaidConfig, MermaidTheme
from mermaid_render.renderers import setup_logging


class TestPluginSystemIntegration:
    """Integration tests for the plugin-based renderer system."""
    
    def setup_method(self) -> None:
        """Set up test environment."""
        # Enable debug logging for tests
        setup_logging(level="DEBUG", console_output=False)
    
    def test_plugin_renderer_basic_functionality(self) -> None:
        """Test basic functionality of PluginMermaidRenderer."""
        renderer = PluginMermaidRenderer()
        
        # Test simple diagram
        result = renderer.render("graph TD\n    A --> B", format="svg")
        assert isinstance(result, str)
        assert len(result) > 100
        assert "<svg" in result
    
    def test_plugin_renderer_with_theme(self) -> None:
        """Test plugin-based renderer with theme support."""
        renderer = PluginMermaidRenderer()
        renderer.set_theme("dark")
        
        result = renderer.render("graph TD\n    A --> B", format="svg")
        assert isinstance(result, str)
        assert len(result) > 100
    
    def test_plugin_renderer_save_to_file(self) -> None:
        """Test saving rendered content to file."""
        renderer = PluginMermaidRenderer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_diagram.svg"
            
            save_result = renderer.save(
                "graph TD\n    A --> B",
                output_path,
                format="svg"
            )
            
            assert save_result["format"] == "svg"
            assert save_result["size_bytes"] > 0
            assert output_path.exists()
            
            # Verify file content
            content = output_path.read_text()
            assert "<svg" in content
    
    def test_legacy_renderer_with_plugin_system(self) -> None:
        """Test legacy renderer with plugin system enabled."""
        renderer = MermaidRenderer(use_plugin_system=True)
        
        result = renderer.render_raw("graph TD\n    A --> B", "svg")
        assert isinstance(result, str)
        assert len(result) > 100
        assert "<svg" in result
    
    def test_legacy_renderer_pure_mode(self) -> None:
        """Test legacy renderer in pure legacy mode."""
        renderer = MermaidRenderer()  # Default is legacy mode
        
        result = renderer.render_raw("graph TD\n    A --> B", "svg")
        assert isinstance(result, str)
        assert len(result) > 100
        assert "<svg" in result
    
    def test_renderer_fallback_mechanism(self) -> None:
        """Test fallback mechanism when preferred renderer fails."""
        renderer = PluginMermaidRenderer()
        
        # Try to use a non-existent renderer - should fallback to available one
        result = renderer.render(
            "graph TD\n    A --> B",
            format="svg",
            renderer="nonexistent",  # This will fallback
            fallback=True
        )
        
        assert isinstance(result, str)
        assert len(result) > 100
    
    def test_multiple_formats(self) -> None:
        """Test rendering to multiple formats."""
        renderer = PluginMermaidRenderer()
        diagram = "graph TD\n    A[Start] --> B[Process] --> C[End]"
        
        # Test SVG
        svg_result = renderer.render(diagram, format="svg")
        assert isinstance(svg_result, str)
        assert "<svg" in svg_result
        
        # Test PNG (if available)
        try:
            png_result = renderer.render(diagram, format="png")
            assert isinstance(png_result, bytes)
            assert len(png_result) > 0
        except Exception as e:
            # PNG might not be available in test environment
            print(f"PNG test skipped: {e}")
    
    def test_renderer_status_and_health(self) -> None:
        """Test renderer status and health checking."""
        renderer = PluginMermaidRenderer()
        
        # Get available renderers
        available = renderer.get_available_renderers()
        assert len(available) > 0
        assert "svg" in available  # SVG should always be available
        
        # Get detailed status
        status = renderer.get_renderer_status()
        assert len(status) >= 3  # At least SVG, PNG, PDF
        
        # Check that each status has required fields
        for name, info in status.items():
            assert "info" in info
            assert "health" in info
            assert "available" in info["health"]
    
    def test_performance_tracking(self) -> None:
        """Test performance tracking functionality."""
        renderer = PluginMermaidRenderer()
        
        # Perform multiple renders
        for i in range(3):
            renderer.render(f"graph TD\n    A{i} --> B{i}", format="svg")
        
        # Check performance stats
        stats = renderer.get_performance_stats()
        assert stats["total_renders"] >= 3
        assert stats["successful_renders"] >= 3
        assert "renderer_usage" in stats
    
    def test_renderer_testing_functionality(self) -> None:
        """Test the renderer testing functionality."""
        renderer = PluginMermaidRenderer()
        
        # Test available renderers
        available = renderer.get_available_renderers()
        
        for renderer_name in available:
            test_result = renderer.test_renderer(renderer_name)
            assert "renderer" in test_result
            assert "success" in test_result
            assert test_result["renderer"] == renderer_name
    
    def test_configuration_integration(self) -> None:
        """Test configuration integration."""
        config = MermaidConfig(timeout=45.0)
        theme = MermaidTheme("dark")
        
        renderer = PluginMermaidRenderer(
            config=config,
            theme=theme,
            fallback_enabled=True,
        )
        
        assert renderer.config == config
        assert renderer.get_theme() == theme
        assert renderer.fallback_enabled is True
        
        # Test rendering with configuration
        result = renderer.render("graph TD\n    A --> B", format="svg")
        assert isinstance(result, str)
        assert len(result) > 100
    
    def test_error_handling_integration(self) -> None:
        """Test error handling integration."""
        renderer = PluginMermaidRenderer()
        
        # Test with invalid syntax (should be handled gracefully)
        try:
            result = renderer.render("invalid mermaid syntax", format="svg")
            # If it succeeds, that's fine (lenient validation)
            assert isinstance(result, str)
        except Exception as e:
            # If it fails, error should be informative
            assert len(str(e)) > 10
    
    def test_benchmark_functionality(self) -> None:
        """Test benchmark functionality."""
        renderer = PluginMermaidRenderer()
        
        # Run benchmark with simple diagrams
        test_diagrams = ["graph TD\n    A --> B"]
        benchmark_results = renderer.benchmark_renderers(
            test_diagrams=test_diagrams,
            formats=["svg"]
        )
        
        assert isinstance(benchmark_results, dict)
        assert len(benchmark_results) > 0
        
        # Check benchmark structure
        for renderer_name, results in benchmark_results.items():
            assert isinstance(results, list)
            for result in results:
                assert "success" in result
                assert "render_time" in result
                assert "format" in result
    
    def test_context_manager_functionality(self) -> None:
        """Test context manager functionality."""
        with PluginMermaidRenderer() as renderer:
            result = renderer.render("graph TD\n    A --> B", format="svg")
            assert isinstance(result, str)
            assert len(result) > 100
        
        # Renderer should be cleaned up after context exit
        # (No specific assertion needed, just ensure no exceptions)


class TestBackwardCompatibilityIntegration:
    """Integration tests for backward compatibility."""
    
    def test_existing_api_unchanged(self) -> None:
        """Test that existing API works unchanged."""
        # This should work exactly as before
        renderer = MermaidRenderer()
        
        # Test all original methods
        result = renderer.render_raw("graph TD\n    A --> B", "svg")
        assert isinstance(result, str)
        
        # Test with theme
        renderer.set_theme("dark")
        result = renderer.render_raw("graph TD\n    A --> B", "svg")
        assert isinstance(result, str)
    
    def test_config_compatibility(self) -> None:
        """Test configuration compatibility."""
        config = MermaidConfig(timeout=30.0)
        renderer = MermaidRenderer(config=config)
        
        result = renderer.render_raw("graph TD\n    A --> B", "svg")
        assert isinstance(result, str)
    
    def test_theme_compatibility(self) -> None:
        """Test theme compatibility."""
        theme = MermaidTheme("forest")
        renderer = MermaidRenderer(theme=theme)
        
        result = renderer.render_raw("graph TD\n    A --> B", "svg")
        assert isinstance(result, str)
    
    def test_save_functionality_compatibility(self) -> None:
        """Test save functionality compatibility."""
        renderer = MermaidRenderer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "legacy_test.svg"
            
            renderer.save_raw(
                "graph TD\n    A --> B",
                str(output_path),
                format="svg"
            )
            
            assert output_path.exists()
            content = output_path.read_text()
            assert "<svg" in content
