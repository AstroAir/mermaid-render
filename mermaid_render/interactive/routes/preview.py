"""
Preview and code generation routes for the interactive diagram builder.

This module provides API endpoints for generating Mermaid code
and rendering diagram previews.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from ...core import MermaidRenderer
from ...validators.validator import MermaidValidator
from ..security import InputSanitizer
from ..websocket import DiagramSession


def create_preview_router(
    sessions: dict[str, DiagramSession],
    renderer: MermaidRenderer,
    validator: MermaidValidator,
) -> APIRouter:
    """
    Create the preview router with the given dependencies.

    Args:
        sessions: Dictionary of active sessions
        renderer: MermaidRenderer instance for rendering diagrams
        validator: MermaidValidator instance for code validation

    Returns:
        Configured APIRouter for preview endpoints
    """
    router = APIRouter(prefix="/api/sessions", tags=["preview"])

    @router.get("/{session_id}/code")
    async def get_mermaid_code(session_id: str) -> dict[str, Any]:
        """Get generated Mermaid code for session."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        try:
            code = session.builder.generate_mermaid_code()
            validation_result = validator.validate(code)

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

    @router.get("/{session_id}/preview")
    async def get_preview(session_id: str, format: str = "svg") -> dict[str, Any]:
        """Get rendered preview of diagram."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        try:
            code = session.builder.generate_mermaid_code()
            rendered_content = renderer.render_raw(code, format)

            return {
                "format": format,
                "content": rendered_content,
                "generated_at": session.updated_at.isoformat(),
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Rendering failed: {str(e)}"
            )

    @router.post("/{session_id}/validate")
    async def validate_code(
        session_id: str, code_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Validate Mermaid code for session."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        # Use provided code or generate from session
        if code_data and "code" in code_data:
            code = code_data["code"]
        else:
            code = session.builder.generate_mermaid_code()

        try:
            validation_result = validator.validate(code)

            return {
                "is_valid": validation_result.is_valid,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
            }
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [str(e)],
                "warnings": [],
            }

    return router
