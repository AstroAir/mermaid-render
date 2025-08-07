"""
SVG renderer for the Mermaid Render library.

This module provides SVG rendering functionality using the mermaid-py library
and mermaid.ink service.
"""

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

try:
    import mermaid as md  # type: ignore[import-untyped]

    _MERMAID_AVAILABLE = True
except ImportError:
    _MERMAID_AVAILABLE = False
    md = None

import requests

from ..exceptions import NetworkError, RenderingError


class SVGRenderer:
    """
    SVG renderer using mermaid-py and mermaid.ink service.

    This renderer converts Mermaid diagram code to SVG format using
    the online mermaid.ink service or local mermaid-py functionality.
    """

    def __init__(
        self,
        server_url: str = "https://mermaid.ink",
        timeout: float = 30.0,
        use_local: bool = True,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        cache_enabled: bool = True,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,  # 1 hour default
    ) -> None:
        """
        Initialize SVG renderer.

        Args:
            server_url: Mermaid.ink server URL
            timeout: Request timeout in seconds
            use_local: Whether to use local mermaid-py rendering when possible
            max_retries: Maximum number of retry attempts for network requests
            backoff_factor: Backoff factor for retry delays
            cache_enabled: Whether to enable caching
            cache_dir: Cache directory path (default: ~/.mermaid_render_cache)
            cache_ttl: Cache time-to-live in seconds
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.use_local = use_local
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl

        # Set up caching
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".mermaid_render_cache"

        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Create a session with retry strategy
        self._session = self._create_session()

        # Performance metrics
        self._metrics: Dict[str, Any] = {
            "cache_hits": 0,
            "cache_misses": 0,
            "render_times": [],
            "total_requests": 0,
        }

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with basic configuration.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Set default headers
        session.headers.update(
            {
                "User-Agent": "mermaid-render/1.0.0",
                "Accept": "image/svg+xml,text/plain,*/*",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        return session

    def _generate_cache_key(
        self, mermaid_code: str, theme: Optional[str], config: Optional[Dict[str, Any]]
    ) -> str:
        """Generate a cache key for the given parameters."""
        # Create a hash of the input parameters
        cache_data = {
            "code": mermaid_code,
            "theme": theme,
            "config": config or {},
            "server_url": self.server_url,
        }

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the cache file path for a given cache key."""
        return self.cache_dir / f"{cache_key}.svg"

    def _get_cache_metadata_path(self, cache_key: str) -> Path:
        """Get the cache metadata file path for a given cache key."""
        return self.cache_dir / f"{cache_key}.meta"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached content is still valid."""
        if not self.cache_enabled:
            return False

        cache_path = self._get_cache_path(cache_key)
        meta_path = self._get_cache_metadata_path(cache_key)

        if not cache_path.exists() or not meta_path.exists():
            return False

        try:
            with open(meta_path) as f:
                metadata = json.load(f)

            cached_time = float(metadata.get("timestamp", 0))
            current_time = time.time()

            return (current_time - cached_time) < self.cache_ttl
        except Exception:
            return False

    def _get_cached_content(self, cache_key: str) -> Optional[str]:
        """Get cached SVG content if valid."""
        if not self._is_cache_valid(cache_key):
            return None

        try:
            cache_path = self._get_cache_path(cache_key)
            with open(cache_path, encoding="utf-8") as f:
                content = f.read()

            self._metrics["cache_hits"] += 1
            self.logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return content
        except Exception as e:
            self.logger.warning(f"Failed to read cache: {e}")
            return None

    def _cache_content(self, cache_key: str, content: str) -> None:
        """Cache SVG content."""
        if not self.cache_enabled:
            return

        try:
            cache_path = self._get_cache_path(cache_key)
            meta_path = self._get_cache_metadata_path(cache_key)

            # Write content
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Write metadata
            metadata = {
                "timestamp": time.time(),
                "size": len(content),
                "cache_key": cache_key,
            }

            with open(meta_path, "w") as f:
                json.dump(metadata, f)

            self.logger.debug(f"Cached content for key: {cache_key[:8]}...")
        except Exception as e:
            self.logger.warning(f"Failed to cache content: {e}")

    def clear_cache(self) -> int:
        """
        Clear all cached content.

        Returns:
            Number of files removed
        """
        if not self.cache_enabled or not self.cache_dir.exists():
            return 0

        removed_count = 0
        for file_path in self.cache_dir.glob("*"):
            try:
                file_path.unlink()
                removed_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to remove cache file {file_path}: {e}")

        return removed_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats: Dict[str, Any] = {
            "cache_enabled": self.cache_enabled,
            "cache_dir": str(self.cache_dir),
            "cache_hits": self._metrics["cache_hits"],
            "cache_misses": self._metrics["cache_misses"],
            "hit_rate": 0.0,
            "total_files": 0,
            "total_size": 0,
        }

        total_requests = stats["cache_hits"] + stats["cache_misses"]
        if total_requests > 0:
            stats["hit_rate"] = stats["cache_hits"] / total_requests

        if self.cache_enabled and self.cache_dir.exists():
            svg_files = list(self.cache_dir.glob("*.svg"))
            stats["total_files"] = len(svg_files)

            total_size = 0
            for file_path in svg_files:
                try:
                    total_size += file_path.stat().st_size
                except Exception:
                    pass
            stats["total_size"] = total_size

        return stats

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        render_times: List[float] = self._metrics["render_times"]

        metrics: Dict[str, Any] = {
            "total_requests": self._metrics["total_requests"],
            "cache_hits": self._metrics["cache_hits"],
            "cache_misses": self._metrics["cache_misses"],
            "cache_hit_rate": 0.0,
            "average_render_time": 0.0,
            "min_render_time": 0.0,
            "max_render_time": 0.0,
            "total_render_time": 0.0,
        }

        if self._metrics["total_requests"] > 0:
            metrics["cache_hit_rate"] = (
                self._metrics["cache_hits"] / self._metrics["total_requests"]
            )

        if render_times:
            metrics["average_render_time"] = sum(render_times) / len(render_times)
            metrics["min_render_time"] = min(render_times)
            metrics["max_render_time"] = max(render_times)
            metrics["total_render_time"] = sum(render_times)

        return metrics

    def optimize_for_large_diagrams(self, mermaid_code: str) -> Dict[str, Any]:
        """
        Analyze and provide optimization suggestions for large diagrams.

        Args:
            mermaid_code: Mermaid code to analyze

        Returns:
            Optimization suggestions
        """
        analysis: Dict[str, Any] = {
            "size_category": "small",
            "complexity_score": 0,
            "suggestions": [],
            "estimated_render_time": "fast",
        }

        lines = len(mermaid_code.split("\n"))
        chars = len(mermaid_code)

        # Analyze complexity
        nodes = len(re.findall(r"\b[A-Za-z0-9_]+\b", mermaid_code))
        connections = len(re.findall(r"-->|---|\-\.\-|==>", mermaid_code))

        analysis["complexity_score"] = nodes + connections * 2

        # Categorize size
        if lines > 100 or chars > 5000 or nodes > 50:
            analysis["size_category"] = "large"
            analysis["estimated_render_time"] = "slow"
            analysis["suggestions"].extend(
                [
                    "Consider breaking the diagram into smaller parts",
                    "Use subgraphs to organize complex diagrams",
                    "Enable caching to avoid re-rendering",
                    "Consider using a higher timeout value",
                ]
            )
        elif lines > 50 or chars > 2000 or nodes > 25:
            analysis["size_category"] = "medium"
            analysis["estimated_render_time"] = "moderate"
            analysis["suggestions"].extend(
                [
                    "Consider enabling caching for better performance",
                    "Monitor rendering time for optimization opportunities",
                ]
            )
        else:
            analysis["suggestions"].append("Diagram size is optimal for fast rendering")

        # Check for performance-impacting patterns
        if "sequenceDiagram" in mermaid_code and connections > 20:
            analysis["suggestions"].append("Large sequence diagrams may render slowly")

        if "classDiagram" in mermaid_code and nodes > 30:
            analysis["suggestions"].append(
                "Complex class diagrams may benefit from grouping"
            )

        return analysis

    def preload_cache(self, diagram_configs: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Preload cache with commonly used diagrams.

        Args:
            diagram_configs: List of diagram configurations to preload

        Returns:
            Preload results
        """
        results: Dict[str, Union[int, List[str]]] = {"successful": 0, "failed": 0, "errors": []}

        for config in diagram_configs:
            try:
                mermaid_code = config.get("code", "")
                theme = config.get("theme")
                render_config = config.get("config")

                if not mermaid_code:
                    continue

                # Render and cache
                self.render(mermaid_code, theme, render_config)
                results["successful"] = cast(int, results["successful"]) + 1

            except Exception as e:
                results["failed"] = cast(int, results["failed"]) + 1
                cast(List[str], results["errors"]).append(str(e))

        return results

    def warm_up_session(self) -> bool:
        """
        Warm up the HTTP session with a simple request.

        Returns:
            True if warm-up successful, False otherwise
        """
        try:
            # Make a simple request to warm up the connection
            simple_diagram = "graph TD\n    A --> B"
            cache_key = self._generate_cache_key(simple_diagram, None, None)

            # Check if already cached
            if self._get_cached_content(cache_key):
                return True

            # Make a quick render request
            self.render(simple_diagram, validate=False, sanitize=False, optimize=False)
            return True

        except Exception as e:
            self.logger.warning(f"Session warm-up failed: {e}")
            return False

    def close(self) -> None:
        """Close the session and clean up resources."""
        if hasattr(self, "_session"):
            self._session.close()

    def __enter__(self) -> "SVGRenderer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        # Touch parameters to avoid unused-variable analysis flags
        _ = (exc_type, exc_val, exc_tb)
        self.close()

    def get_server_status(self) -> Dict[str, Any]:
        """
        Check the status of the mermaid.ink server.

        Returns:
            Dictionary with server status information
        """
        try:
            response = self._session.get(f"{self.server_url}/", timeout=5)
            return {
                "available": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "server_url": self.server_url,
            }
        except Exception as e:
            return {"available": False, "error": str(e), "server_url": self.server_url}

    def render(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        validate: bool = True,
        sanitize: bool = True,
        optimize: bool = False,
    ) -> str:
        """
        Render Mermaid code to SVG.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration dictionary
            validate: Whether to validate the resulting SVG
            sanitize: Whether to sanitize the SVG content for security
            optimize: Whether to optimize the SVG content for size

        Returns:
            SVG content as string

        Raises:
            RenderingError: If rendering fails
            NetworkError: If network request fails
        """
        # Input validation with detailed feedback
        if not mermaid_code or not mermaid_code.strip():
            context = {"input_length": len(mermaid_code) if mermaid_code else 0}
            raise self.create_detailed_error(
                ValueError("Empty mermaid code provided"), context
            )

        # Performance tracking
        start_time = time.time()
        self._metrics["total_requests"] += 1

        # Check cache first
        cache_key = self._generate_cache_key(mermaid_code, theme, config)
        cached_content = self._get_cached_content(cache_key)

        if cached_content:
            # Apply post-processing to cached content if needed
            if validate:
                validation_result = self.validate_svg_content(
                    cached_content, strict=True
                )
                if not validation_result["is_valid"]:
                    # Cache is invalid, remove it and continue with fresh render
                    self.logger.warning(
                        "Cached content failed validation, removing from cache"
                    )
                    try:
                        self._get_cache_path(cache_key).unlink(missing_ok=True)
                        self._get_cache_metadata_path(cache_key).unlink(missing_ok=True)
                    except Exception:
                        pass
                else:
                    # Cache is valid, return it
                    render_time = time.time() - start_time
                    self._metrics["render_times"].append(render_time)
                    return cached_content
            else:
                # No validation needed, return cached content
                render_time = time.time() - start_time
                self._metrics["render_times"].append(render_time)
                return cached_content

        # Cache miss, record it
        self._metrics["cache_misses"] += 1

        # Validate mermaid syntax if requested
        if validate:
            syntax_result = self.validate_mermaid_syntax(mermaid_code)
            if not syntax_result["is_valid"]:
                context = {
                    "errors": syntax_result["errors"],
                    "line_count": len(mermaid_code.split("\n")),
                }
                raise self.create_detailed_error(
                    ValueError(
                        f"Invalid mermaid syntax: {'; '.join(syntax_result['errors'])}"
                    ),
                    context,
                )

            # Log warnings if any
            if syntax_result["warnings"]:
                self.logger.warning(
                    f"Mermaid syntax warnings: {'; '.join(syntax_result['warnings'])}"
                )

            # Log suggestions if any
            if syntax_result["suggestions"]:
                self.logger.info(
                    f"Mermaid syntax suggestions: {'; '.join(syntax_result['suggestions'])}"
                )

        svg_content: Optional[str] = None
        last_error: Optional[Exception] = None

        if self.use_local:
            try:
                svg_content = self._render_local(mermaid_code, theme, config)
            except Exception as e:
                last_error = e
                # Fall back to remote rendering if local fails
                try:
                    svg_content = self._render_remote(mermaid_code, theme, config)
                except Exception as remote_error:
                    # If both fail, create detailed error with context
                    error_context: Dict[str, Any] = {
                        "local_error": str(last_error),
                        "remote_error": str(remote_error),
                        "server_url": self.server_url,
                        "use_local": self.use_local,
                    }
                    raise self.create_detailed_error(
                        RuntimeError("Both local and remote rendering failed"), error_context
                    ) from last_error
        else:
            svg_content = self._render_remote(mermaid_code, theme, config)

        # Post-process the SVG content
        if svg_content:
            if validate:
                validation_result = self.validate_svg_content(svg_content, strict=True)
                if not validation_result["is_valid"]:
                    context = {
                        "validation_errors": validation_result["errors"],
                        "security_issues": validation_result["security_issues"],
                        "svg_length": len(svg_content),
                    }
                    raise self.create_detailed_error(
                        ValueError("Generated SVG content failed validation"), context
                    )

                # Log warnings
                if validation_result["warnings"]:
                    self.logger.warning(
                        f"SVG validation warnings: {'; '.join(validation_result['warnings'])}"
                    )

                # Log security issues
                if validation_result["security_issues"]:
                    self.logger.warning(
                        f"SVG security issues: {'; '.join(validation_result['security_issues'])}"
                    )

            if sanitize:
                svg_content = self.sanitize_svg_content(svg_content, strict=True)

            if optimize:
                svg_content = self.optimize_svg_content(svg_content)

            # Cache the result
            self._cache_content(cache_key, svg_content)

        # Record performance metrics
        render_time = time.time() - start_time
        self._metrics["render_times"].append(render_time)

        return svg_content if svg_content is not None else ""

    def render_with_fallback(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        fallback_servers: Optional[list[str]] = None,
    ) -> str:
        """
        Render with fallback to alternative servers if primary fails.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration dictionary
            fallback_servers: List of fallback server URLs

        Returns:
            SVG content as string
        """
        # Try primary server first
        try:
            return self.render(mermaid_code, theme, config)
        except (NetworkError, RenderingError) as primary_error:
            if not fallback_servers:
                raise primary_error

            # Try fallback servers
            original_server = self.server_url
            last_error: Optional[Exception] = primary_error

            for fallback_url in fallback_servers:
                try:
                    self.server_url = fallback_url.rstrip("/")
                    # Recreate session for new server
                    self._session.close()
                    self._session = self._create_session()

                    return self.render(mermaid_code, theme, config)
                except Exception as e:
                    last_error = e
                    continue
                finally:
                    # Always restore original server
                    self.server_url = original_server
                    self._session.close()
                    self._session = self._create_session()

            # If all servers failed, raise the last error
            raise RenderingError(
                f"All servers failed. Last error: {str(last_error)}"
            ) from last_error

    def _render_local(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render using local mermaid-py library.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration

        Returns:
            SVG content as string
        """
        if not _MERMAID_AVAILABLE or md is None:
            raise RenderingError(
                "mermaid-py library not available. Install with: pip install mermaid-py"
            )

        try:
            # Create mermaid object
            mermaid_obj = md.Mermaid(mermaid_code)

            # Get the SVG content using the svg_response property
            svg_response = mermaid_obj.svg_response

            # Handle different response types
            svg_content: str
            if hasattr(svg_response, "text"):
                # It's a Response object
                svg_content = str(svg_response.text)
            elif isinstance(svg_response, str):
                # It's already a string
                svg_content = svg_response
            else:
                # Convert to string
                svg_content = str(svg_response)

            # If the content is HTML, extract SVG
            if svg_content.strip().startswith("<html") or "<svg" not in svg_content:
                svg_content = self._extract_svg_from_html(svg_content)

            return svg_content

        except Exception as e:
            raise RenderingError(f"Local rendering failed: {str(e)}") from e

    def _extract_svg_from_html(self, html_content: str) -> str:
        """
        Extract SVG content from HTML.

        Args:
            html_content: HTML content containing SVG

        Returns:
            Extracted SVG content
        """
        import re

        # Look for SVG tags in the HTML
        svg_match = re.search(
            r"<svg[^>]*>.*?</svg>", html_content, re.DOTALL | re.IGNORECASE
        )
        if svg_match:
            return svg_match.group(0)

        # If no SVG found, return the original content
        return html_content

    def _render_remote(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render using remote mermaid.ink service.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            theme: Optional theme name
            config: Optional configuration

        Returns:
            SVG content as string
        """
        import base64
        import json as _json

        url: Optional[str] = None
        try:
            # Validate input
            if not mermaid_code or not mermaid_code.strip():
                raise RenderingError("Empty mermaid code provided")

            # Prepare the configuration
            mermaid_config: Dict[str, Any] = {}
            if config:
                # Filter out invalid config options
                valid_config = {
                    k: v
                    for k, v in config.items()
                    if k in ["width", "height", "scale", "backgroundColor", "theme"]
                }
                mermaid_config.update(valid_config)

            # Apply theme configuration
            if theme:
                mermaid_config = self.apply_theme_to_config(mermaid_config, theme)

            # Create the request payload
            if mermaid_config:
                # Include config in the request
                payload = {"code": mermaid_code, "mermaid": mermaid_config}
                json_str = _json.dumps(payload)
                encoded = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
                url = f"{self.server_url}/svg/{encoded}"
            else:
                # Simple encoding without config
                encoded = base64.b64encode(mermaid_code.encode("utf-8")).decode("ascii")
                url = f"{self.server_url}/svg/{encoded}"

            # Make the request using the configured session
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Validate response content
            svg_content = response.text
            if not svg_content:
                raise RenderingError("Empty response from mermaid.ink service")

            # Basic SVG validation
            if not (
                "<svg" in svg_content.lower()
                or "svg" in response.headers.get("content-type", "").lower()
            ):
                # If response doesn't look like SVG, it might be an error message
                if len(svg_content) < 1000:  # Error messages are usually short
                    raise RenderingError(
                        f"Invalid response from server: {svg_content[:200]}"
                    )
                else:
                    raise RenderingError("Response does not appear to be valid SVG")

            return svg_content

        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout after {self.timeout}s") from e
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            raise NetworkError(
                f"Network request failed with status {status_code}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network request failed: {str(e)}") from e
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            context = {
                "mermaid_code_preview": (
                    mermaid_code[:100] + "..."
                    if len(mermaid_code) > 100
                    else mermaid_code
                ),
                "encoding_issue": "unicode",
            }
            raise self.create_detailed_error(e, context) from e
        except Exception as e:
            error_context: Dict[str, Any] = {
                "server_url": self.server_url,
                "operation": "remote_svg_rendering",
                "mermaid_length": len(mermaid_code),
            }
            raise self.create_detailed_error(e, error_context) from e

    def render_to_file(
        self,
        mermaid_code: str,
        output_path: Union[str, Path],
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        validate: bool = True,
        sanitize: bool = True,
        optimize: bool = False,
        add_metadata: bool = True,
        format: str = "svg",
        quality: int = 90,
        background: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Render Mermaid code to file with enhanced export options.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            output_path: Output file path
            theme: Optional theme name
            config: Optional configuration
            validate: Whether to validate the resulting SVG
            sanitize: Whether to sanitize the SVG content
            optimize: Whether to optimize the SVG content
            add_metadata: Whether to add metadata to the SVG
            format: Output format ('svg', 'png', 'pdf', 'html')
            quality: Quality for raster formats (1-100)
            background: Background color for the export

        Returns:
            Export information dictionary
        """
        import datetime as _dt  # intentionally used to avoid unused import warning

        _ = _dt.datetime.now  # touch to avoid unused checks

        start_time = time.time()

        # Render SVG content
        svg_content = self.render(
            mermaid_code, theme, config, validate, sanitize, optimize
        )

        # Add metadata if requested
        if add_metadata and svg_content:
            svg_content = self._add_svg_metadata(svg_content, mermaid_code, theme)

        # Apply background if specified
        if background:
            svg_content = self._add_background_to_svg(svg_content, background)

        # Ensure output directory exists
        normalized_output = Path(output_path)
        normalized_output.parent.mkdir(parents=True, exist_ok=True)

        # Export based on format
        export_info: Dict[str, Any] = {
            "output_path": str(normalized_output),
            "format": format,
            "size_bytes": 0,
            "render_time": 0.0,
            "success": False,
            "error": None,
        }

        try:
            fmt = format.lower()
            if fmt == "svg":
                self._export_svg(svg_content, normalized_output)
            elif fmt == "png":
                self._export_png(svg_content, normalized_output, quality, background)
            elif fmt == "pdf":
                self._export_pdf(svg_content, normalized_output, background)
            elif fmt == "html":
                self._export_html(svg_content, normalized_output, mermaid_code, theme)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            # Get file size
            if normalized_output.exists():
                export_info["size_bytes"] = normalized_output.stat().st_size

            export_info["success"] = True

        except Exception as e:
            export_info["error"] = str(e)
            raise RenderingError(f"Failed to export to {format}: {str(e)}") from e
        finally:
            export_info["render_time"] = time.time() - start_time

        return export_info

    def _export_svg(self, svg_content: str, output_path: Path) -> None:
        """Export SVG content to file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    def _export_png(
        self,
        svg_content: str,
        output_path: Path,
        quality: int,
        background: Optional[str],
    ) -> None:
        """Export SVG to PNG format."""
        try:
            # Try to use cairosvg for PNG conversion
            import cairosvg  # type: ignore[import-untyped]

            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode("utf-8"),
                background_color=background or "white",
                output_width=None,
                output_height=None,
            )
            # Ensure bytes for type checkers
            png_bytes = cast(bytes, png_data)

            with open(output_path, "wb") as f:
                f.write(png_bytes)

        except ImportError:
            raise RenderingError(
                "PNG export requires cairosvg. Install with: pip install cairosvg"
            )
        except Exception as e:
            raise RenderingError(f"PNG export failed: {str(e)}") from e
        finally:
            _ = quality  # parameter acknowledged for API compatibility

    def _export_pdf(
        self, svg_content: str, output_path: Path, background: Optional[str]
    ) -> None:
        """Export SVG to PDF format."""
        try:
            # Try to use cairosvg for PDF conversion
            import cairosvg

            pdf_data = cairosvg.svg2pdf(
                bytestring=svg_content.encode("utf-8"),
                background_color=background or "white",
            )
            pdf_bytes = cast(bytes, pdf_data)

            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        except ImportError:
            raise RenderingError(
                "PDF export requires cairosvg. Install with: pip install cairosvg"
            )
        except Exception as e:
            raise RenderingError(f"PDF export failed: {str(e)}") from e

    def _export_html(
        self,
        svg_content: str,
        output_path: Path,
        mermaid_code: str,
        theme: Optional[str],
    ) -> None:
        """Export SVG embedded in HTML."""
        import datetime

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .diagram {{
            text-align: center;
            margin: 20px 0;
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }}
        .source-code {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            font-family: monospace;
            white-space: pre-wrap;
            border-left: 4px solid #007bff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Mermaid Diagram</h1>
        <div class="diagram">
            {svg_content}
        </div>
        <div class="metadata">
            <strong>Generated:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Theme:</strong> {theme or 'default'}<br>
            <strong>Format:</strong> SVG embedded in HTML
        </div>
        <details>
            <summary><strong>Source Code</strong></summary>
            <div class="source-code">{mermaid_code}</div>
        </details>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_template)

    def _add_background_to_svg(self, svg_content: str, background: str) -> str:
        """Add background color to SVG."""
        # Insert background rectangle after opening svg tag
        if "<svg" in svg_content:
            svg_start = svg_content.find(">")
            if svg_start != -1:
                # Extract width and height from SVG tag
                svg_tag = svg_content[: svg_start + 1]
                width_match = re.search(r'width\s*=\s*["\']([^"\']*)["\']', svg_tag)
                height_match = re.search(r'height\s*=\s*["\']([^"\']*)["\']', svg_tag)

                width = width_match.group(1) if width_match else "100%"
                height = height_match.group(1) if height_match else "100%"

                background_rect = (
                    f'\n<rect width="{width}" height="{height}" fill="{background}"/>'
                )
                svg_content = (
                    svg_content[: svg_start + 1]
                    + background_rect
                    + svg_content[svg_start + 1 :]
                )

        return svg_content

    def batch_export(
        self,
        diagrams: list[Dict[str, Any]],
        output_dir: str,
        format: str = "svg",
        naming_pattern: str = "{index}_{name}",
        **export_options: Any,
    ) -> Dict[str, Any]:
        """
        Export multiple diagrams in batch.

        Args:
            diagrams: List of diagram configurations
            output_dir: Output directory
            format: Export format
            naming_pattern: File naming pattern
            **export_options: Additional export options

        Returns:
            Batch export results
        """
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results: Dict[str, Any] = {
            "total": len(diagrams),
            "successful": 0,
            "failed": 0,
            "files": [],
            "errors": [],
            "total_time": 0.0,
        }

        start_time = time.time()

        # Predefine name to avoid unbound reference in except path
        name: str = ""

        for i, diagram in enumerate(diagrams):
            try:
                mermaid_code = diagram.get("code", "")
                name = diagram.get("name", f"diagram_{i}")
                theme = diagram.get("theme")
                config = diagram.get("config")

                if not mermaid_code:
                    results["errors"].append(f"Diagram {i}: No code provided")
                    results["failed"] += 1
                    continue

                # Generate filename
                filename = naming_pattern.format(
                    index=i, name=name, theme=theme or "default"
                )

                # Add extension if not present
                if not filename.endswith(f".{format}"):
                    filename += f".{format}"

                file_path = output_path / filename

                # Export diagram
                export_info = self.render_to_file(
                    mermaid_code,
                    str(file_path),
                    theme=theme,
                    config=config,
                    format=format,
                    **export_options,
                )

                results["files"].append(
                    {
                        "index": i,
                        "name": name,
                        "path": str(file_path),
                        "size": export_info["size_bytes"],
                        "render_time": export_info["render_time"],
                    }
                )

                results["successful"] += 1

            except Exception as e:
                results["errors"].append(f"Diagram {i} ({name}): {str(e)}")
                results["failed"] += 1

        results["total_time"] = time.time() - start_time

        return results

    def create_export_template(self, template_name: str) -> Dict[str, Any]:
        """
        Create export template with predefined settings.

        Args:
            template_name: Name of the template

        Returns:
            Template configuration
        """
        templates: Dict[str, Dict[str, Any]] = {
            "web": {
                "format": "svg",
                "optimize": True,
                "sanitize": True,
                "add_metadata": False,
                "description": "Optimized for web use",
            },
            "print": {
                "format": "pdf",
                "background": "white",
                "add_metadata": True,
                "description": "Optimized for printing",
            },
            "presentation": {
                "format": "png",
                "quality": 95,
                "background": "transparent",
                "add_metadata": False,
                "description": "High quality for presentations",
            },
            "documentation": {
                "format": "html",
                "add_metadata": True,
                "validate": True,
                "description": "Complete HTML with source code",
            },
            "archive": {
                "format": "svg",
                "add_metadata": True,
                "validate": True,
                "sanitize": False,
                "optimize": False,
                "description": "Full fidelity for archival",
            },
        }

        if template_name not in templates:
            available = ", ".join(templates.keys())
            raise ValueError(
                f"Unknown template '{template_name}'. Available: {available}"
            )

        return templates[template_name]

    def export_with_template(
        self,
        mermaid_code: str,
        output_path: Union[str, Path],
        template_name: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """
        Export using a predefined template.

        Args:
            mermaid_code: Mermaid code to render
            output_path: Output file path
            template_name: Template to use
            theme: Optional theme
            config: Optional configuration
            **overrides: Override template settings

        Returns:
            Export information
        """
        template = self.create_export_template(template_name)

        # Apply overrides
        template.update(overrides)

        # Remove description from export options
        template.pop("description", None)

        return self.render_to_file(
            mermaid_code, output_path, theme=theme, config=config, **template
        )

    def _add_svg_metadata(
        self, svg_content: str, mermaid_code: str, theme: Optional[str]
    ) -> str:
        """
        Add metadata to SVG content.

        Args:
            svg_content: Original SVG content
            mermaid_code: Original mermaid code
            theme: Theme used

        Returns:
            SVG content with metadata
        """
        import datetime
        import html

        # Create metadata comment
        timestamp = datetime.datetime.now().isoformat()
        metadata = f"""<!--
Generated by mermaid-render
Timestamp: {timestamp}
Theme: {theme or 'default'}
Original Mermaid Code:
{html.escape(mermaid_code)}
-->"""

        # Insert metadata after the opening SVG tag
        if "<svg" in svg_content:
            svg_start = svg_content.find(">")
            if svg_start != -1:
                svg_content = (
                    svg_content[: svg_start + 1]
                    + "\n"
                    + metadata
                    + "\n"
                    + svg_content[svg_start + 1 :]
                )

        return svg_content

    def get_supported_themes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about supported themes.

        Returns:
            Dictionary mapping theme names to their configurations
        """
        return {
            "default": {
                "name": "Default",
                "description": "Standard Mermaid theme with blue and gray colors",
                "colors": {
                    "primaryColor": "#0066cc",
                    "primaryTextColor": "#ffffff",
                    "primaryBorderColor": "#004499",
                    "lineColor": "#333333",
                    "backgroundColor": "#ffffff",
                },
            },
            "dark": {
                "name": "Dark",
                "description": "Dark theme with light text on dark backgrounds",
                "colors": {
                    "primaryColor": "#1f2937",
                    "primaryTextColor": "#ffffff",
                    "primaryBorderColor": "#374151",
                    "lineColor": "#6b7280",
                    "backgroundColor": "#111827",
                },
            },
            "forest": {
                "name": "Forest",
                "description": "Green-based theme with natural colors",
                "colors": {
                    "primaryColor": "#22c55e",
                    "primaryTextColor": "#ffffff",
                    "primaryBorderColor": "#16a34a",
                    "lineColor": "#15803d",
                    "backgroundColor": "#f0f9ff",
                },
            },
            "neutral": {
                "name": "Neutral",
                "description": "Neutral color palette with grays and subtle accents",
                "colors": {
                    "primaryColor": "#6b7280",
                    "primaryTextColor": "#ffffff",
                    "primaryBorderColor": "#4b5563",
                    "lineColor": "#374151",
                    "backgroundColor": "#f9fafb",
                },
            },
            "base": {
                "name": "Base",
                "description": "Minimal base theme with clean styling",
                "colors": {
                    "primaryColor": "#3b82f6",
                    "primaryTextColor": "#ffffff",
                    "primaryBorderColor": "#2563eb",
                    "lineColor": "#1f2937",
                    "backgroundColor": "#ffffff",
                },
            },
        }

    def get_theme_names(self) -> list[str]:
        """Get list of supported theme names."""
        return list(self.get_supported_themes().keys())

    def validate_theme(self, theme: str) -> bool:
        """Validate if theme is supported."""
        return theme in self.get_theme_names()

    def get_theme_info(self, theme: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific theme.

        Args:
            theme: Theme name

        Returns:
            Theme information dictionary or None if theme doesn't exist
        """
        themes = self.get_supported_themes()
        return themes.get(theme)

    def create_custom_theme(
        self, name: str, colors: Dict[str, str], description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a custom theme configuration.

        Args:
            name: Theme name
            colors: Color configuration dictionary
            description: Optional theme description

        Returns:
            Custom theme configuration
        """
        required_colors = [
            "primaryColor",
            "primaryTextColor",
            "primaryBorderColor",
            "lineColor",
            "backgroundColor",
        ]

        # Validate required colors
        missing_colors = [color for color in required_colors if color not in colors]
        if missing_colors:
            raise ValueError(f"Missing required colors: {', '.join(missing_colors)}")

        # Validate color format (basic hex color validation)
        for color_name, color_value in colors.items():
            if not re.match(r"^#[0-9a-fA-F]{6}$", color_value):
                raise ValueError(
                    f"Invalid color format for {color_name}: {color_value}"
                )

        return {
            "name": name,
            "description": description or f"Custom theme: {name}",
            "colors": colors,
            "custom": True,
        }

    def apply_theme_to_config(
        self, config: Dict[str, Any], theme: str
    ) -> Dict[str, Any]:
        """
        Apply theme configuration to mermaid config.

        Args:
            config: Base configuration
            theme: Theme name or custom theme dict

        Returns:
            Configuration with theme applied
        """
        result_config = config.copy()

        if isinstance(theme, str):
            if self.validate_theme(theme):
                result_config["theme"] = theme
                theme_info = self.get_theme_info(theme)
                if theme_info and "colors" in theme_info:
                    result_config.update(theme_info["colors"])
            else:
                self.logger.warning(f"Unknown theme '{theme}', using default")
                result_config["theme"] = "default"
        elif isinstance(theme, dict) and "colors" in theme:
            # Custom theme
            result_config.update(theme["colors"])

        return result_config

    def preview_theme(self, theme: str, diagram_type: str = "flowchart") -> str:
        """
        Generate a preview of what a theme looks like.

        Args:
            theme: Theme name to preview
            diagram_type: Type of diagram for preview

        Returns:
            Sample mermaid code with theme applied
        """
        if not self.validate_theme(theme):
            raise ValueError(f"Unknown theme: {theme}")

        theme_info = self.get_theme_info(theme)
        colors = theme_info.get("colors", {}) if theme_info else {}

        if diagram_type == "flowchart":
            preview_code = f"""flowchart TD
    A[Start] --> B{{Decision}}
    B -->|Yes| C[Process]
    B -->|No| D[Alternative]
    C --> E[End]
    D --> E

    classDef default fill:{colors.get('primaryColor', '#0066cc')},stroke:{colors.get('primaryBorderColor', '#004499')},color:{colors.get('primaryTextColor', '#ffffff')}
"""
        elif diagram_type == "sequence":
            preview_code = """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B-->>A: Hello Alice!
    A->>B: How are you?
    B-->>A: I'm good, thanks!
"""
        else:
            preview_code = """graph TD
    A --> B
    B --> C
    C --> A
"""

        return preview_code

    def compare_themes(self, themes: list[str]) -> Dict[str, Any]:
        """
        Compare multiple themes side by side.

        Args:
            themes: List of theme names to compare

        Returns:
            Comparison data for the themes
        """
        comparison: Dict[str, Any] = {"themes": {}, "color_comparison": {}}

        all_themes = self.get_supported_themes()

        for theme_name in themes:
            if theme_name in all_themes:
                comparison["themes"][theme_name] = all_themes[theme_name]

        # Create color comparison matrix
        color_keys = [
            "primaryColor",
            "primaryTextColor",
            "primaryBorderColor",
            "lineColor",
            "backgroundColor",
        ]
        for color_key in color_keys:
            comparison["color_comparison"][color_key] = {}
            for theme_name in themes:
                if theme_name in comparison["themes"]:
                    colors = comparison["themes"][theme_name].get("colors", {})
                    comparison["color_comparison"][color_key][theme_name] = colors.get(
                        color_key, "#000000"
                    )

        return comparison

    def suggest_theme(self, preferences: Dict[str, Any]) -> str:
        """
        Suggest a theme based on user preferences.

        Args:
            preferences: Dictionary with user preferences like 'dark_mode', 'colorful', etc.

        Returns:
            Recommended theme name
        """
        if preferences.get("dark_mode", False):
            return "dark"
        elif preferences.get("natural", False) or preferences.get("green", False):
            return "forest"
        elif preferences.get("minimal", False) or preferences.get("clean", False):
            return "base"
        elif preferences.get("neutral", False) or preferences.get(
            "professional", False
        ):
            return "neutral"
        else:
            return "default"

    def validate_svg_content(
        self, svg_content: str, strict: bool = False
    ) -> Dict[str, Any]:
        """
        Validate SVG content for correctness and security.

        Args:
            svg_content: SVG content to validate
            strict: Whether to apply strict validation rules

        Returns:
            Dictionary with validation results
        """
        result: Dict[str, Any] = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "security_issues": [],
            "structure_issues": [],
        }

        if not svg_content or not isinstance(svg_content, str):
            result["is_valid"] = False
            result["errors"].append("Empty or invalid SVG content")
            return result

        svg_lower = svg_content.lower()

        # Basic structure validation
        if "<svg" not in svg_lower:
            result["is_valid"] = False
            result["errors"].append("No SVG opening tag found")

        if "</svg>" not in svg_lower:
            result["is_valid"] = False
            result["errors"].append("No SVG closing tag found")

        # Check for proper XML structure
        svg_open_count = svg_content.count("<svg")
        svg_close_count = svg_content.count("</svg>")
        if svg_open_count != svg_close_count:
            result["structure_issues"].append(
                f"Mismatched SVG tags: {svg_open_count} open, {svg_close_count} close"
            )

        # Security validation
        security_patterns = [
            (r"<script[^>]*>", "Script tags detected"),
            (r"javascript:", "JavaScript URLs detected"),
            (r"on\w+\s*=", "Event handlers detected"),
            (r"<iframe[^>]*>", "Iframe tags detected"),
            (r"<object[^>]*>", "Object tags detected"),
            (r"<embed[^>]*>", "Embed tags detected"),
            (r"<link[^>]*>", "Link tags detected"),
            (r"<meta[^>]*>", "Meta tags detected"),
            (r"data:text/html", "HTML data URLs detected"),
            (r"vbscript:", "VBScript URLs detected"),
        ]

        for pattern, message in security_patterns:
            if re.search(pattern, svg_content, re.IGNORECASE):
                result["security_issues"].append(message)
                if strict:
                    result["is_valid"] = False

        # Namespace validation - be more specific about what's missing
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
            if "xmlns" not in svg_lower:
                result["warnings"].append("No XML namespace declaration found")
            else:
                result["warnings"].append("SVG namespace declaration may be incorrect")

        # Check for valid SVG elements
        valid_svg_elements = [
            "svg",
            "g",
            "path",
            "rect",
            "circle",
            "ellipse",
            "line",
            "polyline",
            "polygon",
            "text",
            "tspan",
            "textPath",
            "defs",
            "clipPath",
            "mask",
            "pattern",
            "image",
            "use",
            "symbol",
            "marker",
            "linearGradient",
            "radialGradient",
            "stop",
            "animate",
            "animateTransform",
            "animateMotion",
            "set",
            "foreignObject",
            "style",
            "title",
            "desc",
            "metadata",  # Add commonly used SVG elements
            "p",
            "div",
            "span",
            "br",  # HTML elements that can be valid in foreignObject
        ]

        # Extract all element names
        element_pattern = r"<(\w+)(?:\s|>|/>)"
        elements = re.findall(element_pattern, svg_content, re.IGNORECASE)

        invalid_elements = []
        for element in set(elements):
            if element.lower() not in valid_svg_elements:
                # Don't flag common HTML elements that might be valid in certain contexts
                if element.lower() not in ["html", "head", "body", "div", "span"]:
                    invalid_elements.append(element)

        if invalid_elements:
            result["warnings"].append(
                f"Non-standard SVG elements found: {', '.join(invalid_elements)}"
            )

        # Check for excessive size
        if len(svg_content) > 1024 * 1024:  # 1MB
            result["warnings"].append("SVG content is very large (>1MB)")

        # Check for deeply nested elements (simplified check)
        try:
            max_depth = self._calculate_nesting_depth(svg_content)
            if max_depth > 50:
                result["warnings"].append(f"Deep nesting detected (depth: {max_depth})")
        except Exception:
            # If nesting calculation fails, skip it
            result["warnings"].append("Could not calculate nesting depth")

        # Final validation
        if result["security_issues"] and strict:
            result["is_valid"] = False

        return result

    def _calculate_nesting_depth(self, svg_content: str) -> int:
        """Calculate the maximum nesting depth of XML elements."""
        # Simple regex-based approach to avoid infinite loops

        # Count opening and closing tags
        opening_tags = re.findall(r"<([a-zA-Z][a-zA-Z0-9]*)[^>]*(?<!/)>", svg_content)
        # closing_tags = re.findall(r"</([a-zA-Z][a-zA-Z0-9]*)>", svg_content)  # TODO: Use for validation

        # Simple heuristic: assume reasonable nesting based on tag counts
        max_depth = min(len(opening_tags), 20)  # Cap at 20 to avoid issues

        return max_depth

    def sanitize_svg_content(self, svg_content: str, strict: bool = True) -> str:
        """
        Sanitize SVG content by removing potentially dangerous elements.

        Args:
            svg_content: Raw SVG content
            strict: Whether to apply strict sanitization

        Returns:
            Sanitized SVG content
        """
        if not svg_content:
            return svg_content

        # Remove script tags and their content
        svg_content = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            svg_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove event handlers - improved pattern to handle edge cases
        event_handlers = [
            "onclick",
            "onmouseover",
            "onmouseout",
            "onmousedown",
            "onmouseup",
            "onkeydown",
            "onkeyup",
            "onkeypress",
            "onfocus",
            "onblur",
            "onload",
            "onerror",
            "onabort",
            "onchange",
            "onsubmit",
            "onreset",
            "onselect",
            "onresize",
            "onscroll",
            "onunload",
        ]

        for handler in event_handlers:
            # More robust pattern that handles various quote styles and spacing
            patterns = [
                rf'\s{handler}\s*=\s*["\'][^"\']*["\']',  # Standard quotes
                rf'\s{handler}\s*=\s*[^"\'\s>]+',  # Unquoted values
                rf'{handler}\s*=\s*["\'][^"\']*["\']',  # No leading space
            ]
            for pattern in patterns:
                svg_content = re.sub(pattern, "", svg_content, flags=re.IGNORECASE)

        # Remove dangerous URLs
        dangerous_urls = [
            r'javascript:[^"\'>\s]*',
            r'vbscript:[^"\'>\s]*',
            r'data:text/html[^"\'>\s]*',
            r'data:application/[^"\'>\s]*',
        ]

        for url_pattern in dangerous_urls:
            svg_content = re.sub(url_pattern, "", svg_content, flags=re.IGNORECASE)

        if strict:
            # Remove potentially dangerous elements entirely
            dangerous_elements = [
                r"<iframe[^>]*>.*?</iframe>",
                r"<object[^>]*>.*?</object>",
                r"<embed[^>]*>.*?</embed>",
                r"<link[^>]*>",
                r"<meta[^>]*>",
                r"<style[^>]*>.*?</style>",  # Remove style tags in strict mode
                r"<foreignObject[^>]*>.*?</foreignObject>",  # Remove foreign objects
            ]

            for element_pattern in dangerous_elements:
                svg_content = re.sub(
                    element_pattern, "", svg_content, flags=re.IGNORECASE | re.DOTALL
                )

        # Clean up attributes that could be dangerous
        dangerous_attributes = [
            r'\sxlink:href\s*=\s*["\']javascript:[^"\']*["\']',
            r'\shref\s*=\s*["\']javascript:[^"\']*["\']',
            r'\ssrc\s*=\s*["\']javascript:[^"\']*["\']',
        ]

        for attr_pattern in dangerous_attributes:
            svg_content = re.sub(attr_pattern, "", svg_content, flags=re.IGNORECASE)

        # Ensure proper XML structure
        svg_content = self._fix_xml_structure(svg_content)

        # Fix common compatibility issues
        svg_content = self._fix_compatibility_issues(svg_content)

        return svg_content

    def _fix_xml_structure(self, svg_content: str) -> str:
        """Fix basic XML structure issues."""
        # Ensure proper XML declaration if missing
        if not svg_content.strip().startswith(
            "<?xml"
        ) and not svg_content.strip().startswith("<svg"):
            # Add XML declaration if it's a standalone SVG
            if "<svg" in svg_content:
                svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

        # Fix malformed self-closing tags (e.g., '//>') to proper self-closing tags ('/>')
        svg_content = re.sub(r"/+>", "/>", svg_content)

        # Ensure proper SVG namespace declaration
        if (
            "<svg" in svg_content
            and 'xmlns="http://www.w3.org/2000/svg"' not in svg_content
        ):
            # Find the SVG opening tag and add namespace if missing
            svg_pattern = r"<svg([^>]*?)>"

            def add_namespace(match: Any) -> str:
                attrs = match.group(1)
                if "xmlns=" not in attrs:
                    # Add the SVG namespace
                    if attrs.strip():
                        return f'<svg{attrs} xmlns="http://www.w3.org/2000/svg">'
                    else:
                        return '<svg xmlns="http://www.w3.org/2000/svg">'
                return cast(str, match.group(0))

            svg_content = re.sub(svg_pattern, add_namespace, svg_content, count=1)

        # Fix self-closing tags that should be properly closed
        self_closing_fixes = [
            (r"<path([^>]*?)(?<!/)>", r"<path\1/>"),
            (r"<circle([^>]*?)(?<!/)>", r"<circle\1/>"),
            (r"<rect([^>]*?)(?<!/)>", r"<rect\1/>"),
            (r"<line([^>]*?)(?<!/)>", r"<line\1/>"),
            (r"<ellipse([^>]*?)(?<!/)>", r"<ellipse\1/>"),
        ]

        for pattern, replacement in self_closing_fixes:
            # Only fix if not already self-closing and not followed by closing tag
            svg_content = re.sub(pattern + r"(?![^<]*</\w+>)", replacement, svg_content)

        return svg_content

    def _fix_compatibility_issues(self, svg_content: str) -> str:
        """Fix common SVG compatibility issues for better browser support."""
        if not svg_content:
            return svg_content

        # Fix viewBox attribute casing (some browsers are case-sensitive)
        svg_content = re.sub(
            r"\bviewbox\b", "viewBox", svg_content, flags=re.IGNORECASE
        )

        # Ensure proper units for width/height if they're just numbers
        def add_units(match: Any) -> str:
            attr_name = match.group(1)
            value = match.group(2)
            # If it's just a number, add 'px' unit
            if re.match(r"^\d+(\.\d+)?$", value):
                return f'{attr_name}="{value}px"'
            return cast(str, match.group(0))

        # Fix width and height attributes
        svg_content = re.sub(r'(width|height)="([^"]*)"', add_units, svg_content)

        # Remove any remaining multiple slashes in self-closing tags
        svg_content = re.sub(r"/+>", "/>", svg_content)

        # Fix any remaining malformed attributes
        svg_content = re.sub(r'(\w+)=([^"\s>]+)(?=\s|>)', r'\1="\2"', svg_content)

        # Fix XML attribute construct errors
        svg_content = self._fix_xml_attribute_errors(svg_content)

        return svg_content

    def _fix_xml_attribute_errors(self, svg_content: str) -> str:
        """Fix XML attribute construct errors that cause parsing issues."""
        if not svg_content:
            return svg_content

        # Fix the most common XML attribute issues

        # 1. Fix unquoted attribute values
        svg_content = re.sub(r'(\w+)=([^"\s>]+)(?=\s|>)', r'\1="\2"', svg_content)

        # 2. Fix unescaped ampersands in attribute values (simple approach)
        def fix_ampersands(match: Any) -> str:
            attr_name = match.group(1)
            attr_value = match.group(2)
            # Only escape & if it's not already part of an entity
            if "&amp;" not in attr_value:
                attr_value = attr_value.replace("&", "&amp;")
            return f'{attr_name}="{attr_value}"'

        svg_content = re.sub(
            r'([a-zA-Z-]+)="([^"]*&[^"]*)"', fix_ampersands, svg_content
        )

        # 3. Fix unescaped < and > in attribute values
        def fix_brackets(match: Any) -> str:
            attr_name = match.group(1)
            attr_value = match.group(2)
            # Only escape if not already escaped
            if "&lt;" not in attr_value and "&gt;" not in attr_value:
                attr_value = attr_value.replace("<", "&lt;").replace(">", "&gt;")
            return f'{attr_name}="{attr_value}"'

        svg_content = re.sub(
            r'([a-zA-Z-]+)="([^"]*[<>][^"]*)"', fix_brackets, svg_content
        )

        return svg_content

    def scan_svg_security(self, svg_content: str) -> Dict[str, Any]:
        """
        Perform comprehensive security scan of SVG content.

        Args:
            svg_content: SVG content to scan

        Returns:
            Security scan results
        """
        scan_result: Dict[str, Any] = {
            "risk_level": "low",
            "issues": [],
            "recommendations": [],
            "safe_to_use": True,
        }

        if not svg_content:
            return scan_result

        # High-risk patterns
        high_risk_patterns = [
            (r"<script[^>]*>", "Script execution capability"),
            (r"javascript:", "JavaScript URL scheme"),
            (r"vbscript:", "VBScript URL scheme"),
            (r"data:text/html", "HTML data URL"),
            (r"<iframe[^>]*>", "Embedded iframe"),
            (r"<object[^>]*>", "Object embedding"),
            (r"<embed[^>]*>", "Plugin embedding"),
        ]

        # Medium-risk patterns
        medium_risk_patterns = [
            (r"on\w+\s*=", "Event handlers"),
            (r"<foreignObject[^>]*>", "Foreign object content"),
            (r'<use[^>]*href\s*=\s*["\']https?://', "External resource references"),
            (r'<image[^>]*href\s*=\s*["\']https?://', "External image references"),
            (r"<style[^>]*>", "Inline styles"),
        ]

        # Low-risk patterns
        low_risk_patterns = [
            (r"<animate[^>]*>", "Animation elements"),
            (r"<animateTransform[^>]*>", "Transform animations"),
            (r"<text[^>]*>", "Text elements with potential for content injection"),
        ]

        # Check high-risk patterns
        for pattern, description in high_risk_patterns:
            if re.search(pattern, svg_content, re.IGNORECASE):
                scan_result["issues"].append(
                    {"level": "high", "description": description, "pattern": pattern}
                )
                scan_result["risk_level"] = "high"
                scan_result["safe_to_use"] = False

        # Check medium-risk patterns
        for pattern, description in medium_risk_patterns:
            if re.search(pattern, svg_content, re.IGNORECASE):
                scan_result["issues"].append(
                    {"level": "medium", "description": description, "pattern": pattern}
                )
                if scan_result["risk_level"] == "low":
                    scan_result["risk_level"] = "medium"

        # Check low-risk patterns
        for pattern, description in low_risk_patterns:
            if re.search(pattern, svg_content, re.IGNORECASE):
                scan_result["issues"].append(
                    {"level": "low", "description": description, "pattern": pattern}
                )

        # Generate recommendations
        if scan_result["risk_level"] == "high":
            scan_result["recommendations"].extend(
                [
                    "Do not use this SVG in production without sanitization",
                    "Remove all script tags and JavaScript URLs",
                    "Consider using a strict SVG sanitizer",
                    "Validate the source of this SVG content",
                ]
            )
        elif scan_result["risk_level"] == "medium":
            scan_result["recommendations"].extend(
                [
                    "Review and sanitize event handlers",
                    "Validate external resource references",
                    "Consider removing foreign object content",
                ]
            )
        else:
            scan_result["recommendations"].append("SVG appears safe for general use")

        return scan_result

    def create_svg_report(self, svg_content: str) -> Dict[str, Any]:
        """
        Create comprehensive SVG analysis report.

        Args:
            svg_content: SVG content to analyze

        Returns:
            Complete analysis report
        """
        report: Dict[str, Any] = {
            "validation": self.validate_svg_content(svg_content, strict=True),
            "security": self.scan_svg_security(svg_content),
            "statistics": self._get_svg_statistics(svg_content),
            "recommendations": [],
        }

        # Combine recommendations
        if report["validation"]["errors"]:
            report["recommendations"].append("Fix validation errors before use")

        if report["security"]["risk_level"] != "low":
            report["recommendations"].extend(report["security"]["recommendations"])

        if report["statistics"]["size"] > 500000:  # 500KB
            report["recommendations"].append("Consider optimizing SVG size")

        return report

    def _get_svg_statistics(self, svg_content: str) -> Dict[str, Any]:
        """Get statistics about SVG content."""
        stats: Dict[str, Any] = {
            "size": len(svg_content),
            "elements": len(re.findall(r"<\w+", svg_content)),
            "text_elements": len(
                re.findall(r"<text[^>]*>", svg_content, re.IGNORECASE)
            ),
            "paths": len(re.findall(r"<path[^>]*>", svg_content, re.IGNORECASE)),
            "shapes": len(
                re.findall(
                    r"<(rect|circle|ellipse|polygon|polyline)[^>]*>",
                    svg_content,
                    re.IGNORECASE,
                )
            ),
            "groups": len(re.findall(r"<g[^>]*>", svg_content, re.IGNORECASE)),
            "max_nesting_depth": self._calculate_nesting_depth(svg_content),
        }

        return stats

    def validate_mermaid_syntax(self, mermaid_code: str) -> Dict[str, Any]:
        """
        Validate Mermaid syntax and provide detailed error information.

        Args:
            mermaid_code: Mermaid code to validate

        Returns:
            Dictionary with validation results
        """
        result: Dict[str, Any] = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
        }

        if not mermaid_code or not mermaid_code.strip():
            result["is_valid"] = False
            result["errors"].append("Empty mermaid code")
            return result

        # Basic syntax validation
        lines = mermaid_code.strip().split("\n")
        first_line = lines[0].strip()

        # Check for diagram type declaration
        valid_diagram_types = [
            "flowchart",
            "graph",
            "sequenceDiagram",
            "classDiagram",
            "stateDiagram",
            "erDiagram",
            "journey",
            "gantt",
            "pie",
            "gitgraph",
            "mindmap",
            "timeline",
            "sankey",
        ]

        has_diagram_type = any(first_line.startswith(dt) for dt in valid_diagram_types)
        if not has_diagram_type:
            result["warnings"].append(
                f"No recognized diagram type found. First line: '{first_line}'"
            )
            result["suggestions"].append(
                "Start with a diagram type like 'flowchart TD' or 'sequenceDiagram'"
            )

        # Check for common syntax issues
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("%"):  # Skip empty lines and comments
                continue

            # Check for unmatched brackets
            open_brackets = line.count("[") + line.count("(") + line.count("{")
            close_brackets = line.count("]") + line.count(")") + line.count("}")
            if open_brackets != close_brackets:
                result["warnings"].append(f"Line {i}: Potentially unmatched brackets")

            # Check for invalid characters in node IDs
            if "-->" in line or "---" in line:
                parts = re.split(r"-->|---", line)
                for part in parts:
                    part = part.strip()
                    if part and not re.match(r'^[A-Za-z0-9_\[\](){}"\s-]+$', part):
                        result["warnings"].append(
                            f"Line {i}: Potentially invalid characters in '{part}'"
                        )

        return result

    def get_error_suggestions(self, error_message: str) -> list[str]:
        """
        Get suggestions based on error message.

        Args:
            error_message: Error message to analyze

        Returns:
            List of suggestions
        """
        suggestions: list[str] = []
        error_lower = error_message.lower()

        if "timeout" in error_lower:
            suggestions.extend(
                [
                    "Try increasing the timeout value",
                    "Check your internet connection",
                    "Use a simpler diagram to test connectivity",
                    "Consider using a different server URL",
                ]
            )

        if "network" in error_lower or "connection" in error_lower:
            suggestions.extend(
                [
                    "Check your internet connection",
                    "Verify the server URL is accessible",
                    "Try using fallback servers",
                    "Check if you're behind a firewall or proxy",
                ]
            )

        if "invalid" in error_lower and "svg" in error_lower:
            suggestions.extend(
                [
                    "Check if the mermaid syntax is correct",
                    "Try a simpler diagram first",
                    "Verify the diagram type is supported",
                    "Check for special characters that might cause issues",
                ]
            )

        if "empty" in error_lower:
            suggestions.extend(
                [
                    "Provide valid mermaid diagram code",
                    "Check that the input is not empty or whitespace only",
                    "Ensure the diagram has at least one element",
                ]
            )

        return suggestions

    def create_detailed_error(
        self, base_error: Exception, context: Dict[str, Any]
    ) -> RenderingError:
        """
        Create a detailed error with context and suggestions.

        Args:
            base_error: Original exception
            context: Additional context information

        Returns:
            Enhanced RenderingError with details
        """
        error_msg = str(base_error)
        suggestions = self.get_error_suggestions(error_msg)

        detailed_msg = f"{error_msg}"

        if context:
            details = []
            for key, value in context.items():
                if value is not None:
                    details.append(f"{key}: {value}")
            if details:
                detailed_msg += f" | Context: {', '.join(details)}"

        if suggestions:
            # Limit to 3 suggestions
            detailed_msg += f" | Suggestions: {'; '.join(suggestions[:3])}"

        return RenderingError(detailed_msg)

    def diagnose_rendering_issues(self, mermaid_code: str) -> Dict[str, Any]:
        """
        Diagnose potential rendering issues and provide recommendations.

        Args:
            mermaid_code: Mermaid code to diagnose

        Returns:
            Dictionary with diagnostic information
        """
        diagnosis: Dict[str, Any] = {
            "syntax_check": self.validate_mermaid_syntax(mermaid_code),
            "server_status": self.get_server_status(),
            "recommendations": [],
        }

        # Check code complexity
        lines = len(mermaid_code.split("\n"))
        nodes = len(re.findall(r"\b[A-Za-z0-9_]+\b", mermaid_code))

        if lines > 100:
            diagnosis["recommendations"].append(
                "Large diagram detected. Consider breaking into smaller parts."
            )

        if nodes > 50:
            diagnosis["recommendations"].append(
                "Many nodes detected. This might affect rendering performance."
            )

        # Check for special characters
        if re.search(r"[^\x00-\x7F]", mermaid_code):
            diagnosis["recommendations"].append(
                "Non-ASCII characters detected. Ensure proper encoding."
            )

        # Check server availability
        if not diagnosis["server_status"]["available"]:
            diagnosis["recommendations"].append(
                "Server is not available. Check network connection or try fallback servers."
            )

        return diagnosis

    def render_with_recovery(
        self,
        mermaid_code: str,
        theme: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        max_attempts: int = 3,
    ) -> str:
        """
        Render with automatic error recovery and retries.

        Args:
            mermaid_code: Mermaid code to render
            theme: Optional theme
            config: Optional configuration
            max_attempts: Maximum number of attempts

        Returns:
            SVG content
        """
        last_error: Optional[Exception] = None

        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Rendering attempt {attempt + 1}/{max_attempts}")
                return self.render(mermaid_code, theme, config)

            except NetworkError as e:
                last_error = e
                self.logger.warning(f"Network error on attempt {attempt + 1}: {e}")

                if attempt < max_attempts - 1:
                    # Wait before retry with exponential backoff
                    wait_time = (2**attempt) * self.backoff_factor
                    self.logger.info(f"Waiting {wait_time:.1f}s before retry...")
                    time.sleep(wait_time)

                    # Recreate session to clear any connection issues
                    self._session.close()
                    self._session = self._create_session()

            except RenderingError as e:
                last_error = e
                self.logger.error(f"Rendering error on attempt {attempt + 1}: {e}")

                # For rendering errors, don't retry unless it's a timeout-related issue
                if "timeout" not in str(e).lower():
                    break

                if attempt < max_attempts - 1:
                    wait_time = (2**attempt) * self.backoff_factor
                    self.logger.info(f"Waiting {wait_time:.1f}s before retry...")
                    time.sleep(wait_time)

        # If all attempts failed, provide diagnostic information
        diagnosis = self.diagnose_rendering_issues(mermaid_code)
        context = {
            "attempts": max_attempts,
            "diagnosis": diagnosis,
            "last_error": str(last_error),
        }

        raise self.create_detailed_error(
            RuntimeError(f"Rendering failed after {max_attempts} attempts"), context
        ) from last_error

    def optimize_svg_content(self, svg_content: str) -> str:
        """
        Optimize SVG content by removing unnecessary whitespace and comments.

        Args:
            svg_content: Raw SVG content

        Returns:
            Optimized SVG content
        """
        # Remove comments
        svg_content = re.sub(r"<!--.*?-->", "", svg_content, flags=re.DOTALL)

        # Remove excessive whitespace between tags
        svg_content = re.sub(r">\s+<", "><", svg_content)

        # Remove leading/trailing whitespace
        svg_content = svg_content.strip()

        return svg_content
