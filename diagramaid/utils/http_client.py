"""
Shared HTTP client utilities for making requests to rendering services.

This module provides a centralized HTTP client with session pooling, retry logic,
and consistent error handling for all renderers.
"""

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import NetworkError, RenderingError

logger = logging.getLogger(__name__)


class MermaidHTTPClient:
    """
    HTTP client with connection pooling and retry logic for Mermaid services.

    This client provides consistent HTTP request handling across all renderers,
    including automatic retries, connection pooling, and error handling.
    """

    def __init__(
        self,
        server_url: str = "https://mermaid.ink",
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ) -> None:
        """
        Initialize HTTP client.

        Args:
            server_url: Base URL for the Mermaid service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for exponential retry delays
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to save in the pool
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        # Create session with retry strategy and connection pooling
        self._session = self._create_session(pool_connections, pool_maxsize)

    def _create_session(
        self, pool_connections: int, pool_maxsize: int
    ) -> requests.Session:
        """
        Create a requests session with retry strategy and connection pooling.

        Args:
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to save in the pool

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            ],
        )

        # Mount adapters with retry strategy and connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(
            {
                "User-Agent": "diagramaid/1.0.0",
                "Accept": "image/svg+xml,image/png,application/pdf,text/plain,*/*",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        return session

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Make a GET request.

        Args:
            path: URL path (relative to server_url)
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Raises:
            NetworkError: If request fails after retries
            RenderingError: If server returns error response
        """
        url = f"{self.server_url}/{path.lstrip('/')}" if path else self.server_url

        try:
            response = self._session.get(
                url, params=params, headers=headers, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            raise NetworkError(
                f"Request timed out after {self.timeout}s: {url}", url=url
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {url}", url=url) from e
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            raise RenderingError(
                f"HTTP {status_code} error for {url}: {str(e)}", status_code=status_code
            ) from e
        except Exception as e:
            raise RenderingError(f"Unexpected error during request: {str(e)}") from e

    def post(
        self,
        path: str,
        data: Any | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Make a POST request.

        Args:
            path: URL path (relative to server_url)
            data: Request body data
            json: JSON data to send
            headers: Additional headers
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Raises:
            NetworkError: If request fails after retries
            RenderingError: If server returns error response
        """
        url = f"{self.server_url}/{path.lstrip('/')}"

        try:
            response = self._session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            raise NetworkError(
                f"Request timed out after {self.timeout}s: {url}", url=url
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {url}", url=url) from e
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            raise RenderingError(
                f"HTTP {status_code} error for {url}: {str(e)}", status_code=status_code
            ) from e
        except Exception as e:
            raise RenderingError(f"Unexpected error during request: {str(e)}") from e

    def close(self) -> None:
        """Close the session and release resources."""
        if self._session:
            self._session.close()

    def __enter__(self) -> "MermaidHTTPClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
