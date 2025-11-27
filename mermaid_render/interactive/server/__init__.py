"""
Server package for the interactive diagram builder.

This package provides the FastAPI-based web server with WebSocket support
for real-time updates and live preview.
"""

from .app_factory import create_fastapi_app
from .interactive_server import InteractiveServer, create_app, start_server
from .middleware import setup_exception_handler, setup_security_middleware
from .page_routes import setup_page_routes
from .router_registration import register_api_routers
from .websocket_endpoint import setup_websocket_endpoint

__all__ = [
    "InteractiveServer",
    "create_app",
    "start_server",
    "create_fastapi_app",
    "setup_security_middleware",
    "setup_exception_handler",
    "setup_page_routes",
    "register_api_routers",
    "setup_websocket_endpoint",
]
