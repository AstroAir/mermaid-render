"""
Data source integrations for template parameter generation.

This module provides integrations with various data sources to automatically
populate template parameters from external data.
"""

import csv
import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from ..exceptions import DataSourceError


class DataSource(ABC):
    """Base class for data sources."""

    @abstractmethod
    def load_data(self, source: str, **options) -> Dict[str, Any]:
        """Load data from source and return as dictionary."""
        pass

    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """Validate if source is accessible and valid."""
        pass


class JSONDataSource(DataSource):
    """
    JSON file data source.

    Loads template parameters from JSON files with support for
    nested data structures and parameter mapping.
    """

    def load_data(self, source: str, **options) -> Dict[str, Any]:
        """
        Load data from JSON file.

        Args:
            source: Path to JSON file
            **options: Additional options (mapping, filters, etc.)

        Returns:
            Dictionary with loaded data

        Raises:
            DataSourceError: If loading fails
        """
        try:
            source_path = Path(source)

            if not source_path.exists():
                raise DataSourceError(f"JSON file not found: {source}")

            with open(source_path, encoding="utf-8") as f:
                data = json.load(f)

            # Apply mapping if provided
            mapping = options.get("mapping")
            if mapping:
                data = self._apply_mapping(data, mapping)

            # Apply filters if provided
            filters = options.get("filters")
            if filters:
                data = self._apply_filters(data, filters)

            return data

        except (OSError, json.JSONDecodeError) as e:
            raise DataSourceError(f"Failed to load JSON data: {str(e)}") from e

    def validate_source(self, source: str) -> bool:
        """Validate JSON file exists and is valid."""
        try:
            source_path = Path(source)
            if not source_path.exists():
                return False

            with open(source_path, encoding="utf-8") as f:
                json.load(f)

            return True
        except (OSError, json.JSONDecodeError):
            return False

    def _apply_mapping(
        self, data: Dict[str, Any], mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply field mapping to transform data structure."""
        mapped_data = {}

        for target_field, source_field in mapping.items():
            # Support nested field access with dot notation
            value = self._get_nested_value(data, source_field)
            if value is not None:
                mapped_data[target_field] = value

        return mapped_data

    def _apply_filters(
        self, data: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply filters to data."""
        filtered_data = data.copy()

        # Simple filtering implementation
        for field, filter_value in filters.items():
            if field in filtered_data:
                if isinstance(filtered_data[field], list):
                    # Filter list items
                    if isinstance(filter_value, dict):
                        filtered_data[field] = [
                            item
                            for item in filtered_data[field]
                            if self._matches_filter(item, filter_value)
                        ]

        return filtered_data

    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = field_path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def _matches_filter(self, item: Any, filter_criteria: Dict[str, Any]) -> bool:
        """Check if item matches filter criteria."""
        if not isinstance(item, dict):
            return True

        for field, expected_value in filter_criteria.items():
            if field in item:
                if item[field] != expected_value:
                    return False
            else:
                return False

        return True


class CSVDataSource(DataSource):
    """
    CSV file data source.

    Loads template parameters from CSV files with support for
    column mapping and data transformation.
    """

    def load_data(self, source: str, **options) -> Dict[str, Any]:
        """
        Load data from CSV file.

        Args:
            source: Path to CSV file
            **options: Additional options (delimiter, mapping, etc.)

        Returns:
            Dictionary with loaded data

        Raises:
            DataSourceError: If loading fails
        """
        try:
            source_path = Path(source)

            if not source_path.exists():
                raise DataSourceError(f"CSV file not found: {source}")

            delimiter = options.get("delimiter", ",")
            encoding = options.get("encoding", "utf-8")

            rows = []
            with open(source_path, encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)

            # Apply column mapping if provided
            mapping = options.get("mapping")
            if mapping:
                rows = [self._apply_row_mapping(row, mapping) for row in rows]

            # Structure data based on options
            structure = options.get("structure", "rows")

            if structure == "rows":
                return {"data": rows}
            elif structure == "columns":
                return self._rows_to_columns(rows)
            elif structure == "grouped":
                group_by = options.get("group_by")
                if group_by:
                    return self._group_rows(rows, group_by)

            return {"data": rows}

        except (OSError, csv.Error) as e:
            raise DataSourceError(f"Failed to load CSV data: {str(e)}") from e

    def validate_source(self, source: str) -> bool:
        """Validate CSV file exists and is readable."""
        try:
            source_path = Path(source)
            if not source_path.exists():
                return False

            with open(source_path, encoding="utf-8") as f:
                csv.reader(f)

            return True
        except (OSError, csv.Error):
            return False

    def _apply_row_mapping(
        self, row: Dict[str, str], mapping: Dict[str, str]
    ) -> Dict[str, str]:
        """Apply column mapping to a single row."""
        mapped_row = {}

        for target_col, source_col in mapping.items():
            if source_col in row:
                mapped_row[target_col] = row[source_col]

        return mapped_row

    def _rows_to_columns(self, rows: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """Convert row-based data to column-based data."""
        if not rows:
            return {}

        columns = {}
        for column_name in rows[0].keys():
            columns[column_name] = [row.get(column_name, "") for row in rows]

        return columns

    def _group_rows(
        self, rows: List[Dict[str, str]], group_by: str
    ) -> Dict[str, List[Dict[str, str]]]:
        """Group rows by a specific column."""
        groups = {}

        for row in rows:
            group_value = row.get(group_by, "unknown")
            if group_value not in groups:
                groups[group_value] = []
            groups[group_value].append(row)

        return groups


class DatabaseDataSource(DataSource):
    """
    Database data source.

    Loads template parameters from SQL databases with support for
    custom queries and result transformation.
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database data source.

        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string

    def load_data(self, source: str, **options) -> Dict[str, Any]:
        """
        Load data from database query.

        Args:
            source: SQL query or table name
            **options: Additional options (connection, parameters, etc.)

        Returns:
            Dictionary with loaded data

        Raises:
            DataSourceError: If loading fails
        """
        try:
            connection_string = options.get("connection", self.connection_string)

            if not connection_string:
                raise DataSourceError("Database connection string required")

            # For simplicity, this implementation uses SQLite
            # In a full implementation, you'd support multiple database types
            conn = sqlite3.connect(connection_string)
            conn.row_factory = sqlite3.Row  # Enable column access by name

            cursor = conn.cursor()

            # Determine if source is a query or table name
            if source.strip().upper().startswith("SELECT"):
                query = source
            else:
                # Treat as table name
                query = f"SELECT * FROM {source}"

            # Execute query with parameters if provided
            parameters = options.get("parameters", ())
            cursor.execute(query, parameters)

            rows = cursor.fetchall()
            conn.close()

            # Convert to list of dictionaries
            data = [dict(row) for row in rows]

            # Apply transformations if provided
            transform = options.get("transform")
            if transform:
                data = self._apply_transform(data, transform)

            return {"data": data}

        except (sqlite3.Error, Exception) as e:
            raise DataSourceError(f"Failed to load database data: {str(e)}") from e

    def validate_source(self, source: str) -> bool:
        """Validate database connection and query/table."""
        try:
            if not self.connection_string:
                return False

            conn = sqlite3.connect(self.connection_string)
            cursor = conn.cursor()

            # Test query
            if source.strip().upper().startswith("SELECT"):
                cursor.execute(f"EXPLAIN QUERY PLAN {source}")
            else:
                cursor.execute(f"SELECT 1 FROM {source} LIMIT 1")

            conn.close()
            return True
        except sqlite3.Error:
            return False

    def _apply_transform(
        self, data: List[Dict[str, Any]], transform: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply data transformations."""
        # Simple transformation implementation
        # In a full implementation, you'd support more complex transformations

        if "rename_columns" in transform:
            mapping = transform["rename_columns"]
            data = [{mapping.get(k, k): v for k, v in row.items()} for row in data]

        if "filter" in transform:
            filter_criteria = transform["filter"]
            data = [
                row
                for row in data
                if all(row.get(k) == v for k, v in filter_criteria.items())
            ]

        return data


class APIDataSource(DataSource):
    """
    REST API data source.

    Loads template parameters from REST APIs with support for
    authentication, pagination, and response transformation.
    """

    def __init__(
        self, base_url: Optional[str] = None, headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize API data source.

        Args:
            base_url: Base URL for API requests
            headers: Default headers for requests
        """
        self.base_url = base_url
        self.default_headers = headers or {}

    def load_data(self, source: str, **options) -> Dict[str, Any]:
        """
        Load data from API endpoint.

        Args:
            source: API endpoint path or full URL
            **options: Additional options (method, params, headers, etc.)

        Returns:
            Dictionary with loaded data

        Raises:
            DataSourceError: If loading fails
        """
        try:
            # Build URL
            if source.startswith("http"):
                url = source
            elif self.base_url:
                url = urljoin(self.base_url, source)
            else:
                raise DataSourceError("Base URL required for relative endpoints")

            # Prepare request
            method = options.get("method", "GET").upper()
            params = options.get("params", {})
            headers = {**self.default_headers, **options.get("headers", {})}
            timeout = options.get("timeout", 30)

            # Make request
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=timeout,
                json=options.get("json"),
                data=options.get("data"),
            )

            response.raise_for_status()

            # Parse response
            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:
                data = response.json()
            else:
                data = {"content": response.text}

            # Apply data extraction if provided
            extract_path = options.get("extract_path")
            if extract_path:
                data = self._extract_data(data, extract_path)

            # Apply transformation if provided
            transform = options.get("transform")
            if transform:
                data = self._apply_api_transform(data, transform)

            return data

        except (requests.RequestException, ValueError) as e:
            raise DataSourceError(f"Failed to load API data: {str(e)}") from e

    def validate_source(self, source: str) -> bool:
        """Validate API endpoint is accessible."""
        try:
            # Build URL
            if source.startswith("http"):
                url = source
            elif self.base_url:
                url = urljoin(self.base_url, source)
            else:
                return False

            # Test with HEAD request
            response = requests.head(url, headers=self.default_headers, timeout=10)
            return response.status_code < 400

        except requests.RequestException:
            return False

    def _extract_data(self, data: Dict[str, Any], extract_path: str) -> Any:
        """Extract data from nested response using dot notation."""
        keys = extract_path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    return None
            else:
                return None

        return value

    def _apply_api_transform(self, data: Any, transform: Dict[str, Any]) -> Any:
        """Apply transformations to API response data."""
        # Simple transformation implementation
        if isinstance(data, list) and "map" in transform:
            mapping = transform["map"]
            return [
                {target: item.get(source) for target, source in mapping.items()}
                for item in data
                if isinstance(item, dict)
            ]

        return data


def create_data_source(source_type: str, **config) -> DataSource:
    """
    Factory function to create data source instances.

    Args:
        source_type: Type of data source (json, csv, database, api)
        **config: Configuration for the data source

    Returns:
        Data source instance

    Raises:
        DataSourceError: If source type is not supported

    Example:
        >>> json_source = create_data_source('json')
        >>> api_source = create_data_source('api', base_url='https://api.example.com')
    """
    source_map = {
        "json": JSONDataSource,
        "csv": CSVDataSource,
        "database": DatabaseDataSource,
        "api": APIDataSource,
    }

    if source_type not in source_map:
        raise DataSourceError(f"Unsupported data source type: {source_type}")

    source_class = source_map[source_type]

    # Pass relevant config to constructor
    if source_type == "database":
        return source_class(config.get("connection_string"))
    elif source_type == "api":
        return source_class(config.get("base_url"), config.get("headers"))
    else:
        return source_class()


def load_template_data(
    source_type: str,
    source: str,
    template_mapping: Optional[Dict[str, str]] = None,
    **options,
) -> Dict[str, Any]:
    """
    Convenience function to load and map data for template parameters.

    Args:
        source_type: Type of data source
        source: Data source location/query
        template_mapping: Mapping from data fields to template parameters
        **options: Additional options for data source

    Returns:
        Dictionary ready for template parameter use

    Example:
        >>> data = load_template_data(
        ...     'json',
        ...     'services.json',
        ...     template_mapping={'services': 'components', 'connections': 'links'}
        ... )
        >>> diagram = generate_from_template('software_architecture', data)
    """
    data_source = create_data_source(source_type, **options)
    data = data_source.load_data(source, **options)

    if template_mapping:
        mapped_data = {}
        for template_param, data_field in template_mapping.items():
            if data_field in data:
                mapped_data[template_param] = data[data_field]
        return mapped_data

    return data
