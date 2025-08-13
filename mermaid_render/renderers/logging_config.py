"""
Enhanced logging configuration for the Mermaid Render library.

This module provides structured logging and debugging capabilities
for the plugin-based rendering system.
"""

import json
import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union


class RendererLogFormatter(logging.Formatter):
    """Custom log formatter for renderer operations."""

    def __init__(self, include_context: bool = True):
        """
        Initialize the formatter.

        Args:
            include_context: Whether to include renderer context in logs
        """
        self.include_context = include_context

        # Color codes for different log levels
        self.colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m',  # Magenta
            'RESET': '\033[0m',     # Reset
        }

        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record."""
        # Add timestamp
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))

        # Add color for console output
        color = self.colors.get(record.levelname, '')
        reset = self.colors['RESET'] if color else ''

        # Build base message
        parts = [
            f"{timestamp}",
            f"{color}{record.levelname:8}{reset}",
            f"{record.name}",
        ]

        # Add renderer context if available
        if self.include_context and hasattr(record, 'renderer_name'):
            parts.append(f"[{record.renderer_name}]")

        if self.include_context and hasattr(record, 'format'):
            parts.append(f"({record.format})")

        # Add the message
        parts.append(f"- {record.getMessage()}")

        # Add exception info if present
        formatted = " ".join(parts)
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


class PerformanceLogger:
    """Logger for performance metrics and timing information."""

    def __init__(self, logger_name: str = "mermaid_render.performance"):
        """
        Initialize the performance logger.

        Args:
            logger_name: Name of the logger
        """
        self.logger = logging.getLogger(logger_name)
        self._timers: Dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self._timers[operation] = time.time()

    def end_timer(
        self,
        operation: str,
        renderer_name: Optional[str] = None,
        format: Optional[str] = None,
        **metadata: Any,
    ) -> float:
        """
        End timing an operation and log the result.

        Args:
            operation: Operation name
            renderer_name: Renderer name
            format: Output format
            **metadata: Additional metadata to log

        Returns:
            Elapsed time in seconds
        """
        if operation not in self._timers:
            self.logger.warning(f"Timer '{operation}' was not started")
            return 0.0

        elapsed = time.time() - self._timers[operation]
        del self._timers[operation]

        # Create log record with extra context
        extra = {
            'renderer_name': renderer_name,
            'format': format,
            'elapsed_time': elapsed,
            'operation': operation,
        }
        extra.update(metadata)

        self.logger.info(
            f"Operation '{operation}' completed in {elapsed:.3f}s",
            extra=extra,
        )

        return elapsed

    def log_metrics(
        self,
        metrics: Dict[str, Any],
        renderer_name: Optional[str] = None,
    ) -> None:
        """
        Log performance metrics.

        Args:
            metrics: Performance metrics dictionary
            renderer_name: Renderer name
        """
        extra = {'renderer_name': renderer_name}

        self.logger.info(
            f"Performance metrics: {json.dumps(metrics, indent=2)}",
            extra=extra,
        )


def setup_logging(
    level: Union[str, int] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    console_output: bool = True,
    include_context: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Set up enhanced logging for the Mermaid Render library.

    Args:
        level: Logging level
        log_file: Optional log file path
        console_output: Whether to output to console
        include_context: Whether to include renderer context in logs
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    # Get root logger for mermaid_render
    logger = logging.getLogger("mermaid_render")
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = RendererLogFormatter(include_context=include_context)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info("Enhanced logging configured")


def get_renderer_logger(renderer_name: str) -> logging.Logger:
    """
    Get a logger for a specific renderer.

    Args:
        renderer_name: Name of the renderer

    Returns:
        Logger instance for the renderer
    """
    return logging.getLogger(f"mermaid_render.renderers.{renderer_name}")


class LoggingContext:
    """Context manager for adding renderer context to log records."""

    def __init__(
        self,
        logger: logging.Logger,
        renderer_name: Optional[str] = None,
        format: Optional[str] = None,
        **context: Any,
    ):
        """
        Initialize the logging context.

        Args:
            logger: Logger to add context to
            renderer_name: Renderer name
            format: Output format
            **context: Additional context information
        """
        self.logger = logger
        self.old_factory = logging.getLogRecordFactory()
        self.context = {
            'renderer_name': renderer_name,
            'format': format,
        }
        self.context.update(context)

    def __enter__(self) -> logging.Logger:
        """Enter the logging context."""
        def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                if value is not None:
                    setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self.logger

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the logging context."""
        logging.setLogRecordFactory(self.old_factory)


def create_debug_session(
    session_name: str,
    log_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Create a debug session with detailed logging.

    Args:
        session_name: Name of the debug session
        log_dir: Directory for debug logs

    Returns:
        Debug session configuration
    """
    if log_dir is None:
        log_dir = Path.home() / ".mermaid_render" / "debug"

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create session-specific log file
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"{session_name}_{timestamp}.log"

    # Set up detailed logging
    setup_logging(
        level=logging.DEBUG,
        log_file=log_file,
        console_output=True,
        include_context=True,
    )

    session_config = {
        "session_name": session_name,
        "log_file": str(log_file),
        "start_time": time.time(),
        "log_level": "DEBUG",
    }

    logger = logging.getLogger("mermaid_render")
    logger.info(f"Debug session '{session_name}' started", extra=session_config)

    return session_config


def log_renderer_operation(
    operation: str,
    renderer_name: str,
    format: str,
    success: bool,
    duration: float,
    **metadata: Any,
) -> None:
    """
    Log a renderer operation with structured data.

    Args:
        operation: Operation name (e.g., 'render', 'validate')
        renderer_name: Name of the renderer
        format: Output format
        success: Whether operation succeeded
        duration: Operation duration in seconds
        **metadata: Additional metadata
    """
    logger = get_renderer_logger(renderer_name)

    extra = {
        'renderer_name': renderer_name,
        'format': format,
        'operation': operation,
        'success': success,
        'duration': duration,
    }
    extra.update(metadata)

    level = logging.INFO if success else logging.ERROR
    status = "succeeded" if success else "failed"

    logger.log(
        level,
        f"Operation '{operation}' {status} in {duration:.3f}s",
        extra=extra,
    )
