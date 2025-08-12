"""
Renderer registry for the Mermaid Render library.

This module provides a registry system for managing and discovering
available renderers in the plugin-based architecture.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Type

from .base import BaseRenderer, RendererCapability, RendererInfo, RendererPriority


class RendererRegistry:
    """
    Registry for managing available renderers.
    
    This class provides a centralized way to register, discover, and manage
    renderer plugins. It supports automatic discovery, priority-based ordering,
    and capability-based filtering.
    """
    
    def __init__(self) -> None:
        """Initialize the renderer registry."""
        self.logger = logging.getLogger(__name__)
        self._renderers: Dict[str, Type[BaseRenderer]] = {}
        self._renderer_info: Dict[str, RendererInfo] = {}
        self._initialized = False
    
    def register(
        self,
        renderer_class: Type[BaseRenderer],
        name: Optional[str] = None,
        override: bool = False,
    ) -> None:
        """
        Register a renderer class.
        
        Args:
            renderer_class: Renderer class to register
            name: Optional custom name (defaults to class name)
            override: Whether to override existing registration
            
        Raises:
            ValueError: If renderer is already registered and override is False
        """
        # Get renderer name
        if name is None:
            name = renderer_class.__name__.lower().replace("renderer", "")
        
        # Check for existing registration
        if name in self._renderers and not override:
            raise ValueError(f"Renderer '{name}' is already registered")
        
        # Create temporary instance to get info
        try:
            temp_instance = renderer_class()
            info = temp_instance.get_info()
            temp_instance.cleanup()
        except Exception as e:
            self.logger.warning(f"Failed to get info for renderer '{name}': {e}")
            # Create minimal info
            info = RendererInfo(
                name=name,
                description=f"Renderer: {renderer_class.__name__}",
                supported_formats=set(),
                capabilities=set(),
            )
        
        # Register the renderer
        self._renderers[name] = renderer_class
        self._renderer_info[name] = info
        
        self.logger.info(f"Registered renderer: {name}")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a renderer.
        
        Args:
            name: Name of renderer to unregister
            
        Returns:
            True if renderer was unregistered, False if not found
        """
        if name in self._renderers:
            del self._renderers[name]
            del self._renderer_info[name]
            self.logger.info(f"Unregistered renderer: {name}")
            return True
        return False
    
    def get_renderer_class(self, name: str) -> Optional[Type[BaseRenderer]]:
        """
        Get renderer class by name.
        
        Args:
            name: Renderer name
            
        Returns:
            Renderer class or None if not found
        """
        return self._renderers.get(name)
    
    def get_renderer_info(self, name: str) -> Optional[RendererInfo]:
        """
        Get renderer information by name.
        
        Args:
            name: Renderer name
            
        Returns:
            RendererInfo or None if not found
        """
        return self._renderer_info.get(name)
    
    def list_renderers(
        self,
        format_filter: Optional[str] = None,
        capability_filter: Optional[Set[RendererCapability]] = None,
        available_only: bool = False,
    ) -> List[str]:
        """
        List available renderers with optional filtering.
        
        Args:
            format_filter: Only include renderers supporting this format
            capability_filter: Only include renderers with these capabilities
            available_only: Only include renderers that are currently available
            
        Returns:
            List of renderer names matching the criteria
        """
        results = []
        
        for name, renderer_class in self._renderers.items():
            info = self._renderer_info[name]
            
            # Apply format filter
            if format_filter and format_filter.lower() not in info.supported_formats:
                continue
            
            # Apply capability filter
            if capability_filter and not capability_filter.issubset(info.capabilities):
                continue
            
            # Apply availability filter
            if available_only:
                try:
                    temp_instance = renderer_class()
                    is_available = temp_instance.is_available()
                    temp_instance.cleanup()
                    if not is_available:
                        continue
                except Exception:
                    continue
            
            results.append(name)
        
        # Sort by priority
        results.sort(key=lambda name: self._renderer_info[name].priority.value)
        
        return results
    
    def get_best_renderer(
        self,
        format: str,
        required_capabilities: Optional[Set[RendererCapability]] = None,
    ) -> Optional[str]:
        """
        Get the best available renderer for a format and capabilities.
        
        Args:
            format: Required output format
            required_capabilities: Required capabilities
            
        Returns:
            Name of best renderer or None if none available
        """
        candidates = self.list_renderers(
            format_filter=format,
            capability_filter=required_capabilities,
            available_only=True,
        )
        
        return candidates[0] if candidates else None
    
    def get_fallback_chain(
        self,
        format: str,
        primary_renderer: Optional[str] = None,
        max_fallbacks: int = 3,
    ) -> List[str]:
        """
        Get ordered list of renderers for fallback chain.
        
        Args:
            format: Required output format
            primary_renderer: Preferred primary renderer
            max_fallbacks: Maximum number of fallback renderers
            
        Returns:
            Ordered list of renderer names for fallback chain
        """
        all_candidates = self.list_renderers(
            format_filter=format,
            available_only=True,
        )
        
        # Build fallback chain
        chain = []
        
        # Add primary renderer first if specified and available
        if primary_renderer and primary_renderer in all_candidates:
            chain.append(primary_renderer)
            all_candidates.remove(primary_renderer)
        
        # Add remaining candidates up to max_fallbacks
        remaining_slots = max_fallbacks - len(chain)
        chain.extend(all_candidates[:remaining_slots])
        
        return chain
    
    def create_renderer(
        self,
        name: str,
        **config: Any,
    ) -> Optional[BaseRenderer]:
        """
        Create a renderer instance by name.
        
        Args:
            name: Renderer name
            **config: Configuration options for the renderer
            
        Returns:
            Renderer instance or None if not found
        """
        renderer_class = self.get_renderer_class(name)
        if renderer_class is None:
            return None
        
        try:
            return renderer_class(**config)
        except Exception as e:
            self.logger.error(f"Failed to create renderer '{name}': {e}")
            return None
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry statistics
        """
        total_renderers = len(self._renderers)
        available_renderers = 0
        format_support: Dict[str, int] = {}
        capability_support: Dict[str, int] = {}
        
        for name, renderer_class in self._renderers.items():
            info = self._renderer_info[name]
            
            # Check availability
            try:
                temp_instance = renderer_class()
                if temp_instance.is_available():
                    available_renderers += 1
                temp_instance.cleanup()
            except Exception:
                pass
            
            # Count format support
            for fmt in info.supported_formats:
                format_support[fmt] = format_support.get(fmt, 0) + 1
            
            # Count capability support
            for cap in info.capabilities:
                cap_name = cap.value
                capability_support[cap_name] = capability_support.get(cap_name, 0) + 1
        
        return {
            "total_renderers": total_renderers,
            "available_renderers": available_renderers,
            "format_support": format_support,
            "capability_support": capability_support,
        }
    
    def auto_discover(self) -> None:
        """
        Automatically discover and register built-in renderers.
        
        This method scans for known renderer classes and registers them
        automatically. It's called during initialization.
        """
        if self._initialized:
            return
        
        # Import and register built-in renderers
        try:
            from .svg_renderer_plugin import SVGRendererPlugin
            self.register(SVGRendererPlugin, "svg")
        except ImportError:
            self.logger.debug("SVG renderer plugin not available")
        
        try:
            from .png_renderer_plugin import PNGRendererPlugin
            self.register(PNGRendererPlugin, "png")
        except ImportError:
            self.logger.debug("PNG renderer plugin not available")
        
        try:
            from .pdf_renderer_plugin import PDFRendererPlugin
            self.register(PDFRendererPlugin, "pdf")
        except ImportError:
            self.logger.debug("PDF renderer plugin not available")
        
        # Register new renderers
        try:
            from .playwright_renderer import PlaywrightRenderer
            self.register(PlaywrightRenderer, "playwright")
        except ImportError:
            self.logger.debug("Playwright renderer not available")
        
        try:
            from .nodejs_renderer import NodeJSRenderer
            self.register(NodeJSRenderer, "nodejs")
        except ImportError:
            self.logger.debug("Node.js renderer not available")
        
        try:
            from .graphviz_renderer import GraphvizRenderer
            self.register(GraphvizRenderer, "graphviz")
        except ImportError:
            self.logger.debug("Graphviz renderer not available")
        
        self._initialized = True
        self.logger.info(f"Auto-discovery complete. Registered {len(self._renderers)} renderers.")


# Global registry instance
_global_registry: Optional[RendererRegistry] = None


def get_global_registry() -> RendererRegistry:
    """
    Get the global renderer registry instance.
    
    Returns:
        Global RendererRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = RendererRegistry()
        _global_registry.auto_discover()
    return _global_registry


def register_renderer(
    renderer_class: Type[BaseRenderer],
    name: Optional[str] = None,
    override: bool = False,
) -> None:
    """
    Register a renderer in the global registry.
    
    Args:
        renderer_class: Renderer class to register
        name: Optional custom name
        override: Whether to override existing registration
    """
    registry = get_global_registry()
    registry.register(renderer_class, name, override)
