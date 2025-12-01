"""
Web server for the interactive diagram builder.

This module provides the FastAPI-based web server with WebSocket support
for real-time updates and live preview.
"""

import json
import logging
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..core import MermaidRenderer
from ..validators.validator import MermaidValidator
from .models import DiagramType
from .routes import (
    create_elements_router,
    create_preview_router,
    create_sessions_router,
)
from .security import SecurityValidator, api_rate_limiter
from .websocket_handler import DiagramSession, WebSocketHandler


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
        self.static_dir = static_dir or Path(__file__).parent / "static"
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"

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

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="Mermaid Interactive Builder",
            description="Interactive web-based Mermaid diagram builder",
            version="1.0.0",
        )

        # Setup static files
        if self.static_dir.exists():
            app.mount(
                "/static", StaticFiles(directory=str(self.static_dir)), name="static"
            )

        # Configure CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add security middleware
        self._setup_security_middleware(app)

        # Add global exception handler
        self._setup_exception_handler(app)

        # Setup templates and page routes
        self._setup_page_routes(app)

        # Register API routers
        self._register_api_routers(app)

        # Setup WebSocket endpoint
        self._setup_websocket_endpoint(app)

        return app

    def _setup_security_middleware(self, app: FastAPI) -> None:
        """Setup security middleware for rate limiting and origin validation."""

        @app.middleware("http")  # type: ignore[misc]
        async def security_middleware(
            request: Request, call_next: Callable[..., Any]
        ) -> Any:
            """Security middleware for rate limiting and origin validation."""
            # Get client IP for rate limiting
            client_ip = request.client.host if request.client else "unknown"

            # Check rate limit for API endpoints
            if request.url.path.startswith("/api/"):
                if not api_rate_limiter.is_allowed(client_ip):
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": "Too many requests",
                        },
                    )

            # Validate origin for sensitive endpoints
            origin = request.headers.get("origin")
            if request.method in [
                "POST",
                "PUT",
                "DELETE",
            ] and not SecurityValidator.validate_origin(origin):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Forbidden", "message": "Invalid origin"},
                )

            response = await call_next(request)

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            return response

        # Reference the middleware to avoid linter warnings
        _ = security_middleware

    def _setup_exception_handler(self, app: FastAPI) -> None:
        """Setup global exception handler."""

        @app.exception_handler(Exception)  # type: ignore[misc]
        async def global_exception_handler(
            request: Request, exc: Exception
        ) -> JSONResponse:
            """Global exception handler for better error reporting."""
            logging.error(f"Unhandled exception: {exc}")
            logging.error(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(exc),
                    "type": type(exc).__name__,
                },
            )

        # Reference the handler to avoid linter warnings
        _ = global_exception_handler

    def _setup_page_routes(self, app: FastAPI) -> None:
        """Setup HTML page routes."""
        from fastapi import HTTPException

        templates = Jinja2Templates(directory=str(self.templates_dir))

        @app.get("/", response_class=HTMLResponse)  # type: ignore
        async def index(request: Request) -> HTMLResponse:
            """Main builder interface."""
            return templates.TemplateResponse("index.html", {"request": request})

        @app.get("/builder/{diagram_type}", response_class=HTMLResponse)  # type: ignore
        async def builder(request: Request, diagram_type: str) -> HTMLResponse:
            """Diagram builder for specific type."""
            try:
                DiagramType(diagram_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid diagram type")

            return templates.TemplateResponse(
                "builder.html",
                {
                    "request": request,
                    "diagram_type": diagram_type,
                },
            )

        # Reference the routes to avoid linter warnings
        _ = (index, builder)

    def _register_api_routers(self, app: FastAPI) -> None:
        """Register API routers."""
        # Create and register session routes
        sessions_router = create_sessions_router(
            sessions=self.sessions,
            websocket_handler=self.websocket_handler,
            max_sessions=100,
        )
        app.include_router(sessions_router)

        # Create and register element routes
        elements_router = create_elements_router(
            sessions=self.sessions,
            websocket_handler=self.websocket_handler,
        )
        app.include_router(elements_router)

        # Create and register preview routes
        preview_router = create_preview_router(
            sessions=self.sessions,
            renderer=self.renderer,
            validator=self.validator,
        )
        app.include_router(preview_router)

    def _setup_websocket_endpoint(self, app: FastAPI) -> None:
        """Setup WebSocket endpoint for real-time updates."""

        @app.websocket("/ws/{session_id}")  # type: ignore
        async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
            """WebSocket endpoint for real-time updates."""
            await self.websocket_handler.connect(websocket, session_id)

            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)

                    # Handle different message types
                    await self.websocket_handler.handle_message(session_id, message)

            except WebSocketDisconnect:
                self.websocket_handler.disconnect(websocket, session_id)

        # Reference the endpoint to avoid linter warnings
        _ = websocket_endpoint

    def run(self, **kwargs: Any) -> None:
        """Run the server.

        Notes:
            - uvicorn.run has many optional keyword parameters (e.g., reload, workers, log_level, etc.).
              We accept arbitrary keyword args and forward them using **kwargs.
            - Important: Always pass host/port as keyword arguments to avoid mypy/pylance mis-inferring
              **kwargs as positional args for unrelated parameters in uvicorn.run overloads.
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
