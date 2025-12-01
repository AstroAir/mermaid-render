"""
FastAPI application factory for the interactive diagram builder.

This module provides functions to create and configure the FastAPI application.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


def create_fastapi_app(
    title: str = "Mermaid Interactive Builder",
    description: str = "Interactive web-based Mermaid diagram builder",
    version: str = "1.0.0",
    static_dir: Path | None = None,
) -> FastAPI:
    """
    Create and configure a FastAPI application.

    Args:
        title: Application title
        description: Application description
        version: Application version
        static_dir: Directory for static files

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=title,
        description=description,
        version=version,
    )

    # Setup static files if directory exists
    if static_dir and static_dir.exists():
        app.mount(
            "/static",
            StaticFiles(directory=str(static_dir)),
            name="static",
        )

    # Configure CORS
    configure_cors(app)

    return app


def configure_cors(
    app: FastAPI,
    allow_origins: list[str] | None = None,
    allow_credentials: bool = True,
    allow_methods: list[str] | None = None,
    allow_headers: list[str] | None = None,
) -> None:
    """
    Configure CORS middleware for the application.

    Args:
        app: FastAPI application
        allow_origins: Allowed origins (default: all)
        allow_credentials: Allow credentials
        allow_methods: Allowed methods (default: all)
        allow_headers: Allowed headers (default: all)
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ["*"],
        allow_credentials=allow_credentials,
        allow_methods=allow_methods or ["*"],
        allow_headers=allow_headers or ["*"],
    )
