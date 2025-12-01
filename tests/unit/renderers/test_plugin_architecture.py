"""
Tests for the plugin-based renderer architecture.

This module tests the base renderer interface, registry system,
and renderer manager functionality.
"""

import pytest
from typing import Any, Optional, Union
from unittest.mock import Mock, patch

from diagramaid.renderers.base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
    RendererError,
)
from diagramaid.renderers.registry import RendererRegistry
from diagramaid.renderers.manager import RendererManager
from diagramaid.exceptions import RenderingError, UnsupportedFormatError


class MockRenderer(BaseRenderer):
    """Mock renderer for testing."""
    
    def __init__(self, name: str = "mock", formats: Optional[set] = None, capabilities: Optional[set] = None, **config: Any) -> None:
        super().__init__(**config)
        self._name = name
        self._formats = formats or {"svg"}
        self._capabilities = capabilities or {RendererCapability.THEME_SUPPORT}
        self._available = config.get("available", True)
        self._should_fail = config.get("should_fail", False)
    
    def get_info(self) -> RendererInfo:
        return RendererInfo(
            name=self._name,
            description=f"Mock renderer: {self._name}",
            supported_formats=self._formats,
            capabilities=self._capabilities,
            priority=RendererPriority.NORMAL,
        )
    
    def render(self, mermaid_code: str, format: str, theme: Optional[str] = None, config: Optional[dict] = None, **options: Any) -> RenderResult:
        if self._should_fail:
            raise RenderingError("Mock renderer failure")
        
        svg_content = f"<svg>Mock {format} content for {self._name}</svg>"
        if format != "svg":
            content: Union[str, bytes] = svg_content.encode()
        else:
            content = svg_content
        
        return RenderResult(
            content=content,
            format=format,
            renderer_name=self._name,
            render_time=0.1,
            success=True,
        )
    
    def is_available(self) -> bool:
        return bool(self._available)


class TestBaseRenderer:
    """Test the BaseRenderer abstract class."""
    
    def test_abstract_methods(self) -> None:
        """Test that BaseRenderer cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseRenderer()  # type: ignore[abstract]
    
    def test_mock_renderer_creation(self) -> None:
        """Test creating a mock renderer."""
        renderer = MockRenderer()
        assert renderer.get_info().name == "mock"
        assert "svg" in renderer.get_supported_formats()
        assert renderer.has_capability(RendererCapability.THEME_SUPPORT)
    
    def test_supports_format(self) -> None:
        """Test format support checking."""
        renderer = MockRenderer(formats={"svg", "png"})
        assert renderer.supports_format("svg")
        assert renderer.supports_format("png")
        assert not renderer.supports_format("pdf")
    
    def test_has_capability(self) -> None:
        """Test capability checking."""
        capabilities = {RendererCapability.CACHING, RendererCapability.VALIDATION}
        renderer = MockRenderer(capabilities=capabilities)
        assert renderer.has_capability(RendererCapability.CACHING)
        assert renderer.has_capability(RendererCapability.VALIDATION)
        assert not renderer.has_capability(RendererCapability.BATCH_PROCESSING)
    
    def test_context_manager(self) -> None:
        """Test context manager functionality."""
        with MockRenderer() as renderer:
            assert isinstance(renderer, MockRenderer)


class TestRendererRegistry:
    """Test the RendererRegistry class."""
    
    def test_registry_creation(self) -> None:
        """Test creating a registry."""
        registry = RendererRegistry()
        assert len(registry._renderers) == 0
    
    def test_register_renderer(self) -> None:
        """Test registering a renderer."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "test_mock")
        
        assert "test_mock" in registry._renderers
        assert registry.get_renderer_class("test_mock") == MockRenderer
    
    def test_register_duplicate_error(self) -> None:
        """Test error when registering duplicate renderer."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "test_mock")
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(MockRenderer, "test_mock")
    
    def test_register_with_override(self) -> None:
        """Test registering with override."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "test_mock")
        
        # Should not raise error with override=True
        registry.register(MockRenderer, "test_mock", override=True)
    
    def test_unregister_renderer(self) -> None:
        """Test unregistering a renderer."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "test_mock")
        
        assert registry.unregister("test_mock")
        assert "test_mock" not in registry._renderers
        assert not registry.unregister("nonexistent")
    
    def test_list_renderers(self) -> None:
        """Test listing renderers with filters."""
        registry = RendererRegistry()
        
        # Register different renderers
        registry.register(
            MockRenderer,
            "svg_only",
            override=True,
        )
        
        # Create a mock class for PNG renderer
        class MockPNGRenderer(MockRenderer):
            def __init__(self, **config: Any) -> None:
                super().__init__(name="png_only", formats={"png"}, **config)
        
        registry.register(MockPNGRenderer, "png_only")
        
        # Test listing all
        all_renderers = registry.list_renderers()
        assert "svg_only" in all_renderers
        assert "png_only" in all_renderers
        
        # Test format filter
        svg_renderers = registry.list_renderers(format_filter="svg")
        assert "svg_only" in svg_renderers
        assert "png_only" not in svg_renderers
    
    def test_get_best_renderer(self) -> None:
        """Test getting the best renderer for a format."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "test_renderer")
        
        best = registry.get_best_renderer("svg")
        assert best == "test_renderer"
        
        # Test with unsupported format
        best = registry.get_best_renderer("unsupported")
        assert best is None
    
    def test_create_renderer(self) -> None:
        """Test creating renderer instances."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "test_renderer")
        
        renderer = registry.create_renderer("test_renderer")
        assert isinstance(renderer, MockRenderer)
        
        # Test with nonexistent renderer
        renderer = registry.create_renderer("nonexistent")
        assert renderer is None


class TestRendererManager:
    """Test the RendererManager class."""
    
    def test_manager_creation(self) -> None:
        """Test creating a renderer manager."""
        registry = RendererRegistry()
        manager = RendererManager(registry=registry)
        assert manager.registry == registry
    
    def test_render_success(self) -> None:
        """Test successful rendering."""
        registry = RendererRegistry()
        
        # Create a custom renderer class that uses the correct name
        class TestRenderer(MockRenderer):
            def __init__(self, **config: Any) -> None:
                super().__init__(name="test_renderer", **config)
        
        registry.register(TestRenderer, "test_renderer")
        
        manager = RendererManager(registry=registry)
        
        result = manager.render(
            mermaid_code="graph TD\n    A --> B",
            format="svg",
        )
        
        assert result.success
        assert result.format == "svg"
        assert result.renderer_name == "test_renderer"
        assert "Mock svg content" in result.content
    
    def test_render_fallback(self) -> None:
        """Test fallback rendering."""
        registry = RendererRegistry()
        
        # Register failing renderer with higher priority
        class FailingRenderer(MockRenderer):
            def __init__(self, **config: Any) -> None:
                super().__init__(name="failing", should_fail=True, **config)
            
            def get_info(self) -> RendererInfo:
                info = super().get_info()
                info.priority = RendererPriority.HIGHEST
                return info
        
        # Create a working renderer with correct name
        class WorkingRenderer(MockRenderer):
            def __init__(self, **config: Any) -> None:
                super().__init__(name="working", **config)
        
        registry.register(FailingRenderer, "failing")
        registry.register(WorkingRenderer, "working")
        
        manager = RendererManager(registry=registry)
        
        result = manager.render(
            mermaid_code="graph TD\n    A --> B",
            format="svg",
        )
        
        assert result.success
        assert result.renderer_name == "working"
    
    def test_render_all_fail(self) -> None:
        """Test when all renderers fail."""
        registry = RendererRegistry()
        registry.register(
            MockRenderer,
            "failing",
            override=True,
        )
        
        # Make the mock renderer fail
        with patch.object(MockRenderer, 'render', side_effect=RenderingError("Test failure")):
            manager = RendererManager(registry=registry)
            
            with pytest.raises(RenderingError, match="All renderers failed"):
                manager.render(
                    mermaid_code="graph TD\n    A --> B",
                    format="svg",
                )
    
    def test_unsupported_format(self) -> None:
        """Test unsupported format error."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "svg_only")  # Only supports SVG
        
        manager = RendererManager(registry=registry)
        
        with pytest.raises(UnsupportedFormatError):
            manager.render(
                mermaid_code="graph TD\n    A --> B",
                format="unsupported",
            )
    
    def test_get_available_formats(self) -> None:
        """Test getting available formats."""
        registry = RendererRegistry()
        registry.register(MockRenderer, "svg_renderer")
        
        class MockPNGRenderer(MockRenderer):
            def __init__(self, **config: Any) -> None:
                super().__init__(name="png", formats={"png"}, **config)
        
        registry.register(MockPNGRenderer, "png_renderer")
        
        manager = RendererManager(registry=registry)
        formats = manager.get_available_formats()
        
        assert "svg" in formats
        assert "png" in formats
    
    def test_context_manager(self) -> None:
        """Test context manager functionality."""
        registry = RendererRegistry()
        
        with RendererManager(registry=registry) as manager:
            assert isinstance(manager, RendererManager)
