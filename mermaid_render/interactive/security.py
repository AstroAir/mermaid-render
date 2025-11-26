"""Security utilities for the interactive module."""

import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    max_requests: int = 100  # Maximum requests per window
    window_seconds: int = 60  # Time window in seconds
    burst_limit: int = 10  # Maximum burst requests


@dataclass
class ClientInfo:
    """Information about a client for rate limiting."""

    requests: list[float] = field(default_factory=list)
    blocked_until: float = 0.0


class RateLimiter:
    """Rate limiter for API endpoints and WebSocket connections."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.clients: dict[str, ClientInfo] = defaultdict(ClientInfo)

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = time.time()
        client = self.clients[client_id]

        # Check if client is currently blocked
        if client.blocked_until > now:
            return False

        # Clean old requests outside the window
        cutoff = now - self.config.window_seconds
        client.requests = [
            req_time for req_time in client.requests if req_time > cutoff
        ]

        # Check rate limit
        if len(client.requests) >= self.config.max_requests:
            # Block client for the window duration
            client.blocked_until = now + self.config.window_seconds
            return False

        # Check burst limit
        recent_cutoff = now - 1.0  # Last second
        recent_requests = [
            req_time for req_time in client.requests if req_time > recent_cutoff
        ]
        if len(recent_requests) >= self.config.burst_limit:
            return False

        # Allow request and record it
        client.requests.append(now)
        return True

    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client in current window."""
        now = time.time()
        client = self.clients[client_id]

        cutoff = now - self.config.window_seconds
        client.requests = [
            req_time for req_time in client.requests if req_time > cutoff
        ]

        return max(0, self.config.max_requests - len(client.requests))


class InputSanitizer:
    """Sanitizes user inputs to prevent security issues."""

    # Maximum lengths for various input types
    MAX_LABEL_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_CODE_LENGTH = 50000
    MAX_SESSION_ID_LENGTH = 100

    # Allowed characters for different input types
    LABEL_PATTERN = re.compile(r"^[a-zA-Z0-9\s\-_.,!?()[\]{}]+$")
    SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_]+$")

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        re.compile(r"data:text/html", re.IGNORECASE),
        re.compile(r"vbscript:", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_label(cls, label: str) -> str:
        """Sanitize element labels."""
        if not isinstance(label, str):
            raise ValueError("Label must be a string")

        if len(label) > cls.MAX_LABEL_LENGTH:
            raise ValueError(f"Label too long (max {cls.MAX_LABEL_LENGTH} characters)")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(label):
                raise ValueError("Label contains potentially dangerous content")

        # Basic sanitization
        label = label.strip()
        if not label:
            raise ValueError("Label cannot be empty")

        return label

    @classmethod
    def sanitize_description(cls, description: str) -> str:
        """Sanitize descriptions."""
        if not isinstance(description, str):
            raise ValueError("Description must be a string")

        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Description too long (max {cls.MAX_DESCRIPTION_LENGTH} characters)"
            )

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(description):
                raise ValueError("Description contains potentially dangerous content")

        return description.strip()

    @classmethod
    def sanitize_mermaid_code(cls, code: str) -> str:
        """Sanitize Mermaid diagram code."""
        if not isinstance(code, str):
            raise ValueError("Code must be a string")

        if len(code) > cls.MAX_CODE_LENGTH:
            raise ValueError(f"Code too long (max {cls.MAX_CODE_LENGTH} characters)")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(code):
                raise ValueError("Code contains potentially dangerous content")

        return code.strip()

    @classmethod
    def sanitize_session_id(cls, session_id: str) -> str:
        """Sanitize session IDs."""
        if not isinstance(session_id, str):
            raise ValueError("Session ID must be a string")

        if len(session_id) > cls.MAX_SESSION_ID_LENGTH:
            raise ValueError(
                f"Session ID too long (max {cls.MAX_SESSION_ID_LENGTH} characters)"
            )

        if not cls.SESSION_ID_PATTERN.match(session_id):
            raise ValueError("Session ID contains invalid characters")

        return session_id

    @classmethod
    def sanitize_element_data(cls, element_data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize element data dictionary."""
        if not isinstance(element_data, dict):
            raise ValueError("Element data must be a dictionary")

        sanitized: dict[str, Any] = {}

        # Sanitize label
        if "label" in element_data:
            sanitized["label"] = cls.sanitize_label(element_data["label"])

        # Sanitize element type
        if "element_type" in element_data:
            element_type = element_data["element_type"]
            if not isinstance(element_type, str) or element_type not in [
                "node",
                "connection",
            ]:
                raise ValueError("Invalid element type")
            sanitized["element_type"] = element_type

        # Sanitize position
        if "position" in element_data:
            position = element_data["position"]
            if not isinstance(position, dict):
                raise ValueError("Position must be a dictionary")

            for coord in ["x", "y"]:
                if coord in position:
                    try:
                        value = float(position[coord])
                        if not (-10000 <= value <= 10000):
                            raise ValueError(f"Position {coord} out of bounds")
                        if "position" not in sanitized:
                            sanitized["position"] = {}
                        sanitized["position"][coord] = value
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid position {coord}")

        # Sanitize size
        if "size" in element_data:
            size = element_data["size"]
            if not isinstance(size, dict):
                raise ValueError("Size must be a dictionary")

            for dim in ["width", "height"]:
                if dim in size:
                    try:
                        value = float(size[dim])
                        if not (1 <= value <= 2000):
                            raise ValueError(f"Size {dim} out of bounds")
                        if "size" not in sanitized:
                            sanitized["size"] = {}
                        sanitized["size"][dim] = value
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid size {dim}")

        # Copy other safe fields
        safe_fields = ["properties", "style"]
        for field_name in safe_fields:
            if field_name in element_data and isinstance(
                element_data[field_name], dict
            ):
                sanitized[field_name] = element_data[field_name]

        return sanitized


class SecurityValidator:
    """Validates security aspects of requests."""

    ALLOWED_ORIGINS: set[str] = {
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://localhost:8000",
        "https://127.0.0.1:8000",
    }

    @classmethod
    def validate_origin(cls, origin: str | None) -> bool:
        """Validate request origin."""
        if not origin:
            return True  # Allow requests without origin (e.g., direct API calls)

        return origin in cls.ALLOWED_ORIGINS

    @classmethod
    def validate_websocket_origin(cls, origin: str | None) -> bool:
        """Validate WebSocket connection origin."""
        return cls.validate_origin(origin)

    @classmethod
    def add_allowed_origin(cls, origin: str) -> None:
        """Add an allowed origin."""
        cls.ALLOWED_ORIGINS.add(origin)

    @classmethod
    def remove_allowed_origin(cls, origin: str) -> None:
        """Remove an allowed origin."""
        cls.ALLOWED_ORIGINS.discard(origin)


# Global rate limiter instances
api_rate_limiter = RateLimiter(RateLimitConfig(max_requests=100, window_seconds=60))
websocket_rate_limiter = RateLimiter(
    RateLimitConfig(max_requests=200, window_seconds=60)
)
