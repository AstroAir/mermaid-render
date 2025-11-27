"""
Page routes for the interactive diagram builder.

This module provides HTML page routes for the web interface.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..models import DiagramType


def setup_page_routes(app: FastAPI, templates_dir: Path) -> None:
    """
    Setup HTML page routes.

    Args:
        app: FastAPI application
        templates_dir: Directory containing Jinja2 templates
    """
    templates = Jinja2Templates(directory=str(templates_dir))

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
