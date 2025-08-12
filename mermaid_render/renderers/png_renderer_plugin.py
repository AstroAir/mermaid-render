"""
PNG renderer plugin adapter for the plugin-based architecture.

This module wraps the existing PNGRenderer to work with the new
plugin-based rendering system.
"""

import time
from typing import Any, Dict, Optional, Set

from .base import (
    BaseRenderer,
    RendererCapability,
    RendererInfo,
    RendererPriority,
    RenderResult,
)
from .png_renderer import PNGRenderer


class PNGRendererPlugin(BaseRenderer):
    """
    Plugin adapter for the existing PNGRenderer.
    
    This class wraps the existing PNGRenderer to work with the new
    plugin-based architecture while maintaining all existing functionality.
    """
    
    def __init__(self, **config: Any) -> None:
        """
        Initialize the PNG renderer plugin.
        
        Args:
            **config: Configuration options passed to PNGRenderer
        """
        super().__init__(**config)
        
        # Extract PNGRenderer-specific config
        png_config = {
            "server_url": config.get("server_url", "https://mermaid.ink"),
            "timeout": config.get("timeout", 30.0),
            "width": config.get("width", 800),
            "height": config.get("height", 600),
        }
        
        # Create the underlying PNGRenderer
        self._png_renderer = PNGRenderer(**png_config)
    
    def get_info(self) -> RendererInfo:
        """
        Get renderer information and capabilities.
        
        Returns:
            RendererInfo object describing the PNG renderer
        """
        return RendererInfo(
            name="png",
            description="PNG renderer using mermaid.ink service",
            supported_formats={"png"},
            capabilities={
                RendererCapability.THEME_SUPPORT,
                RendererCapability.CUSTOM_CONFIG,
                RendererCapability.REMOTE_RENDERING,
            },
            priority=RendererPriority.NORMAL,
            version="1.0.0",
            author="Mermaid Render Team",
            dependencies=["requests"],
            config_schema={
                "type": "object",
                "properties": {
                    "server_url": {"type": "string", "default": "https://mermaid.ink"},
                    "timeout": {"type": "number", "default": 30.0},
                    "width": {"type": "integer", "default": 800},
                    "height": {"type": "integer", "default": 600},
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
        Render Mermaid code to PNG format.
        
        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format (must be 'png')
            theme: Optional theme name
            config: Optional configuration dictionary
            **options: Additional rendering options
            
        Returns:
            RenderResult containing the PNG content and metadata
            
        Raises:
            UnsupportedFormatError: If format is not 'png'
            RenderingError: If rendering fails
        """
        from ..exceptions import UnsupportedFormatError
        
        if format.lower() != "png":
            raise UnsupportedFormatError(f"PNG renderer only supports 'png' format, got '{format}'")
        
        start_time = time.time()
        
        try:
            # Extract PNG-specific options
            width = options.get("width")
            height = options.get("height")
            
            # Render using the underlying PNGRenderer
            png_data = self._png_renderer.render(
                mermaid_code=mermaid_code,
                theme=theme,
                config=config,
                width=width,
                height=height,
            )
            
            render_time = time.time() - start_time
            
            # Create metadata
            metadata = {
                "image_size": len(png_data),
                "width": width or self._png_renderer.default_width,
                "height": height or self._png_renderer.default_height,
            }
            
            return RenderResult(
                content=png_data,
                format="png",
                renderer_name="png",
                render_time=render_time,
                success=True,
                metadata=metadata,
            )
            
        except Exception as e:
            render_time = time.time() - start_time
            
            return RenderResult(
                content=b"",
                format="png",
                renderer_name="png",
                render_time=render_time,
                success=False,
                error=str(e),
            )
    
    def is_available(self) -> bool:
        """
        Check if PNG renderer is available.
        
        Returns:
            True if renderer is available, False otherwise
        """
        try:
            # Test connectivity to mermaid.ink service
            import requests
            
            response = requests.get(
                f"{self._png_renderer.server_url}/",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get detailed health status of the PNG renderer.
        
        Returns:
            Dictionary with health status information
        """
        base_status = super().get_health_status()
        
        # Add PNG-specific health information
        try:
            import requests
            
            response = requests.get(
                f"{self._png_renderer.server_url}/",
                timeout=5,
            )
            
            base_status["server_status"] = {
                "available": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "server_url": self._png_renderer.server_url,
            }
            
        except Exception as e:
            base_status["server_status"] = {
                "available": False,
                "error": str(e),
                "server_url": self._png_renderer.server_url,
            }
        
        return base_status
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate PNG renderer configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        # Basic validation for PNG renderer config
        valid_keys = {"server_url", "timeout", "width", "height"}
        
        # Check for unknown keys
        unknown_keys = set(config.keys()) - valid_keys
        if unknown_keys:
            self.logger.warning(f"Unknown config keys for PNG renderer: {unknown_keys}")
        
        # Validate specific values
        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
                return False
        
        if "width" in config:
            if not isinstance(config["width"], int) or config["width"] <= 0:
                return False
        
        if "height" in config:
            if not isinstance(config["height"], int) or config["height"] <= 0:
                return False
        
        if "server_url" in config:
            if not isinstance(config["server_url"], str) or not config["server_url"].strip():
                return False
        
        return True
    
    def cleanup(self) -> None:
        """
        Clean up PNG renderer resources.
        """
        # PNG renderer doesn't have explicit cleanup, but we can log
        self.logger.debug("PNG renderer cleanup completed")
    
    def render_to_file(
        self,
        mermaid_code: str,
        output_path: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """
        Render Mermaid code directly to PNG file.
        
        This method provides direct access to the underlying renderer's
        file output functionality for backward compatibility.
        
        Args:
            mermaid_code: Raw Mermaid diagram syntax
            output_path: Output file path
            theme: Optional theme name
            config: Optional configuration
            width: Image width
            height: Image height
        """
        self._png_renderer.render_to_file(
            mermaid_code=mermaid_code,
            output_path=output_path,
            theme=theme,
            config=config,
            width=width,
            height=height,
        )
    
    def get_supported_themes(self) -> List[str]:
        """
        Get list of supported themes.
        
        Returns:
            List of supported theme names
        """
        if hasattr(self._png_renderer, "get_supported_themes"):
            return self._png_renderer.get_supported_themes()
        return ["default", "dark", "forest", "neutral", "base"]
