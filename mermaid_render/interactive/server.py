"""
Web server for the interactive diagram builder.

This module provides the FastAPI-based web server with WebSocket support
for real-time updates and live preview.
"""

import json
import logging
import traceback
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from ..core import MermaidRenderer
from .builder import DiagramBuilder, DiagramType, ElementType, Position, Size
from .validation import LiveValidator
from .websocket_handler import DiagramSession, WebSocketHandler
from .security import InputSanitizer, SecurityValidator, api_rate_limiter
from .performance import (
    default_debouncer,
    default_performance_monitor,
    default_resource_manager,
    performance_monitor
)


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
        static_dir: Optional[Path] = None,
        templates_dir: Optional[Path] = None,
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
        self.sessions: Dict[str, DiagramSession] = {}

        # Renderer for preview generation
        self.renderer = MermaidRenderer()

        # Validator for live validation
        self.validator = LiveValidator()

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
        @app.middleware("http")  # type: ignore[misc]
        async def security_middleware(request: Request, call_next: Callable) -> Any:
            """Security middleware for rate limiting and origin validation."""
            # Get client IP for rate limiting
            client_ip = request.client.host if request.client else "unknown"

            # Check rate limit for API endpoints
            if request.url.path.startswith("/api/"):
                if not api_rate_limiter.is_allowed(client_ip):
                    return JSONResponse(
                        status_code=429,
                        content={"error": "Rate limit exceeded", "message": "Too many requests"}
                    )

            # Validate origin for sensitive endpoints
            origin = request.headers.get("origin")
            if request.method in ["POST", "PUT", "DELETE"] and not SecurityValidator.validate_origin(origin):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Forbidden", "message": "Invalid origin"}
                )

            response = await call_next(request)

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            return response

        # Add global exception handler
        @app.exception_handler(Exception)  # type: ignore[misc]
        async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
            """Global exception handler for better error reporting."""
            logging.error(f"Unhandled exception: {exc}")
            logging.error(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(exc),
                    "type": type(exc).__name__
                }
            )

        # Setup templates
        templates = Jinja2Templates(directory=str(self.templates_dir))

        # Routes
        @app.get("/", response_class=HTMLResponse)  # type: ignore
        async def index(request: Request) -> HTMLResponse:
            """Main builder interface."""
            return templates.TemplateResponse("index.html", {"request": request})

        @app.get("/builder/{diagram_type}", response_class=HTMLResponse)  # type: ignore
        async def builder(
            request: Request, diagram_type: str
        ) -> HTMLResponse:
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

        @app.post("/api/sessions")  # type: ignore
        @performance_monitor("create_session", default_performance_monitor)
        async def create_session(diagram_type: str = "flowchart") -> Dict[str, Any]:
            """Create new diagram session."""
            try:
                # Check resource limits
                if not default_resource_manager.check_resource_limits("max_sessions", len(self.sessions)):
                    raise HTTPException(
                        status_code=503,
                        detail="Maximum number of sessions reached"
                    )

                session_id = str(uuid.uuid4())
                builder_obj = DiagramBuilder(DiagramType(diagram_type))
                session = DiagramSession(session_id, builder_obj)

                self.sessions[session_id] = session

                return {
                    "session_id": session_id,
                    "diagram_type": diagram_type,
                    "created_at": session.created_at.isoformat(),
                }
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid diagram type '{diagram_type}': {str(e)}"
                )
            except Exception as e:
                logging.error(f"Failed to create session: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create session"
                )

        @app.get("/api/sessions/{session_id}")  # type: ignore
        async def get_session(session_id: str) -> Dict[str, Any]:
            """Get session information."""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.sessions[session_id]
            builder_state = session.builder.to_dict()
            return {
                "session_id": session_id,
                "diagram_type": session.builder.diagram_type.value,
                "elements": builder_state["elements"],
                "connections": builder_state["connections"],
                "metadata": session.builder.metadata,
            }

        @app.post("/api/sessions/{session_id}/elements")  # type: ignore
        async def add_element(session_id: str, element_data: dict) -> Dict[str, Any]:
            """Add element to diagram."""
            try:
                # Sanitize session ID
                session_id = InputSanitizer.sanitize_session_id(session_id)

                if session_id not in self.sessions:
                    raise HTTPException(status_code=404, detail="Session not found")

                session = self.sessions[session_id]

                # Sanitize and validate element data
                sanitized_data = InputSanitizer.sanitize_element_data(element_data)

                element = session.builder.add_element(
                    element_type=ElementType(sanitized_data["element_type"]),
                    label=sanitized_data["label"],
                    position=Position.from_dict(sanitized_data["position"]),
                    size=Size.from_dict(
                        sanitized_data.get("size", {"width": 120, "height": 60})
                    ),
                    properties=sanitized_data.get("properties", {}),
                    style=sanitized_data.get("style", {}),
                )

                # Broadcast update to connected clients
                await self.websocket_handler.broadcast_to_session(
                    session_id,
                    {
                        "type": "element_added",
                        "element": element.to_dict(),
                    },
                )

                return element.to_dict()

            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid element data: {str(e)}"
                )
            except KeyError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {str(e)}"
                )
            except Exception as e:
                logging.error(f"Failed to add element: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to add element"
                )

        @app.put("/api/sessions/{session_id}/elements/{element_id}")  # type: ignore
        async def update_element(
            session_id: str, element_id: str, element_data: dict
        ) -> Dict[str, Any]:
            """Update element in diagram."""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.sessions[session_id]

            # Extract update parameters
            update_params: Dict[str, Any] = {}
            if "label" in element_data:
                update_params["label"] = element_data["label"]
            if "position" in element_data:
                update_params["position"] = Position.from_dict(element_data["position"])
            if "size" in element_data:
                update_params["size"] = Size.from_dict(element_data["size"])
            if "properties" in element_data:
                update_params["properties"] = element_data["properties"]
            if "style" in element_data:
                update_params["style"] = element_data["style"]

            success = session.builder.update_element(element_id, **update_params)

            if not success:
                raise HTTPException(status_code=404, detail="Element not found")

            # Broadcast update to connected clients
            await self.websocket_handler.broadcast_to_session(
                session_id,
                {
                    "type": "element_updated",
                    "element_id": element_id,
                    "updates": element_data,
                },
            )

            return {"success": True}

        @app.delete("/api/sessions/{session_id}/elements/{element_id}")  # type: ignore
        async def remove_element(session_id: str, element_id: str) -> Dict[str, Any]:
            """Remove element from diagram."""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.sessions[session_id]
            success = session.builder.remove_element(element_id)

            if not success:
                raise HTTPException(status_code=404, detail="Element not found")

            # Broadcast update to connected clients
            await self.websocket_handler.broadcast_to_session(
                session_id,
                {
                    "type": "element_removed",
                    "element_id": element_id,
                },
            )

            return {"success": True}

        @app.post("/api/sessions/{session_id}/connections")  # type: ignore
        async def add_connection(
            session_id: str, connection_data: dict
        ) -> Dict[str, Any]:
            """Add connection to diagram."""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.sessions[session_id]

            connection = session.builder.add_connection(
                source_id=connection_data["source_id"],
                target_id=connection_data["target_id"],
                label=connection_data.get("label", ""),
                connection_type=connection_data.get("connection_type", "default"),
                style=connection_data.get("style", {}),
                properties=connection_data.get("properties", {}),
            )

            if not connection:
                raise HTTPException(status_code=400, detail="Invalid connection")

            # Broadcast update to connected clients
            await self.websocket_handler.broadcast_to_session(
                session_id,
                {
                    "type": "connection_added",
                    "connection": connection.to_dict(),
                },
            )

            return connection.to_dict()

        @app.get("/api/sessions/{session_id}/code")  # type: ignore
        async def get_mermaid_code(session_id: str) -> Dict[str, Any]:
            """Get generated Mermaid code for session."""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.sessions[session_id]

            try:
                code = session.builder.generate_mermaid_code()
                validation_result = self.validator.validate(code)

                return {
                    "code": code,
                    "validation": {
                        "is_valid": validation_result.is_valid,
                        "errors": validation_result.errors,
                        "warnings": validation_result.warnings,
                    },
                }
            except Exception as e:
                return {
                    "code": "",
                    "validation": {
                        "is_valid": False,
                        "errors": [str(e)],
                        "warnings": [],
                    },
                }

        @app.get("/api/sessions/{session_id}/preview")  # type: ignore
        async def get_preview(session_id: str, format: str = "svg") -> Dict[str, Any]:
            """Get rendered preview of diagram."""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.sessions[session_id]

            try:
                code = session.builder.generate_mermaid_code()
                rendered_content = self.renderer.render_raw(code, format)

                return {
                    "format": format,
                    "content": rendered_content,
                    "generated_at": session.updated_at.isoformat(),
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Rendering failed: {str(e)}"
                )

        # WebSocket endpoint for real-time updates
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

        # Assign to variables to ensure the functions are referenced (for strict linters)
        _ = (
            index,
            builder,
            create_session,
            get_session,
            add_element,
            update_element,
            remove_element,
            add_connection,
            get_mermaid_code,
            get_preview,
            websocket_endpoint,
        )

        return app

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
    static_dir: Optional[Path] = None,
    templates_dir: Optional[Path] = None,
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
    static_dir: Optional[Path] = None,
    templates_dir: Optional[Path] = None,
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
        >>> from mermaid_render.interactive import start_server
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
