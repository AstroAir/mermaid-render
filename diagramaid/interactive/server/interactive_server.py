"""
Interactive server for the diagram builder.

This module provides the main InteractiveServer class and convenience functions.
"""

import logging
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI

from ...core import MermaidRenderer
from ...validators.validator import MermaidValidator
from ..websocket import DiagramSession, WebSocketHandler
from .app_factory import create_fastapi_app
from .middleware import setup_exception_handler, setup_security_middleware
from .page_routes import setup_page_routes
from .router_registration import register_api_routers
from .websocket_endpoint import setup_websocket_endpoint


class InteractiveServer:
    """
    Interactive diagram builder server.

    Provides a web-based interface for building Mermaid diagrams
    with real-time updates and live preview capabilities.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        static_dir: Path | None = None,
        templates_dir: Path | None = None,
    ) -> None:
        """
        Initialize interactive server.

        Args:
            host: Server host
            port: Server port
            static_dir: Directory for static files
            templates_dir: Directory for templates
        """
        self.host = host
        self.port = port

        # Setup directories
        self.static_dir = static_dir or Path(__file__).parent.parent / "static"
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"

        # Create FastAPI app
        self.app = self._create_app()

        # WebSocket handler for real-time updates
        self.websocket_handler = WebSocketHandler()

        # Active diagram sessions
        self.sessions: dict[str, DiagramSession] = {}

        # Renderer for preview generation
        self.renderer = MermaidRenderer()

        # Validator for live validation
        self.validator = MermaidValidator()

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Complete app setup
        self._setup_app()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""
        return create_fastapi_app(static_dir=self.static_dir)

    def _setup_app(self) -> None:
        """Setup all application components."""
        # Add security middleware
        setup_security_middleware(self.app)

        # Add global exception handler
        setup_exception_handler(self.app)

        # Setup templates and page routes
        setup_page_routes(self.app, self.templates_dir)

        # Register API routers
        register_api_routers(
            app=self.app,
            sessions=self.sessions,
            websocket_handler=self.websocket_handler,
            renderer=self.renderer,
            validator=self.validator,
            max_sessions=100,
        )

        # Setup WebSocket endpoint
        setup_websocket_endpoint(self.app, self.websocket_handler)

    def run(self, **kwargs: Any) -> None:
        """
        Run the server.

        Notes:
            - uvicorn.run has many optional keyword parameters.
              We accept arbitrary keyword args and forward them using **kwargs.
        """
        uvicorn.run(app=self.app, host=self.host, port=self.port, **kwargs)


def create_app(
    static_dir: Path | None = None,
    templates_dir: Path | None = None,
) -> FastAPI:
    """
    Create FastAPI application for interactive builder.

    Args:
        static_dir: Directory for static files
        templates_dir: Directory for templates

    Returns:
        Configured FastAPI application
    """
    server = InteractiveServer(
        static_dir=static_dir,
        templates_dir=templates_dir,
    )
    return server.app


def start_server(
    host: str = "localhost",
    port: int = 8080,
    static_dir: Path | None = None,
    templates_dir: Path | None = None,
    **kwargs: Any,
) -> None:
    """
    Start the interactive diagram builder server.

    Args:
        host: Server host
        port: Server port
        static_dir: Directory for static files
        templates_dir: Directory for templates
        **kwargs: Additional uvicorn options

    Example:
        >>> from diagramaid.interactive import start_server
        >>> start_server(host="0.0.0.0", port=8080)
        >>> # Access at http://localhost:8080
    """
    server = InteractiveServer(
        host=host,
        port=port,
        static_dir=static_dir,
        templates_dir=templates_dir,
    )

    server.run(**kwargs)
