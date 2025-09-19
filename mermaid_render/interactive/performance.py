"""Performance optimization utilities for the interactive module."""

import asyncio
import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union
from dataclasses import dataclass
from functools import wraps

T = TypeVar('T')


@dataclass
class DebounceConfig:
    """Configuration for debouncing operations."""
    
    delay: float = 0.3  # Delay in seconds
    max_delay: float = 2.0  # Maximum delay before forcing execution
    immediate: bool = False  # Execute immediately on first call


class Debouncer:
    """Debounces function calls to reduce excessive operations."""
    
    def __init__(self, config: DebounceConfig):
        self.config = config
        self._pending_tasks: Dict[str, asyncio.Task] = {}
        self._first_call_times: Dict[str, float] = {}
    
    async def debounce(self, key: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Debounce a function call.
        
        Args:
            key: Unique key for this debounced operation
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Result of the function call (when executed)
        """
        now = time.time()
        
        # Cancel existing pending task for this key
        if key in self._pending_tasks:
            self._pending_tasks[key].cancel()
        
        # Track first call time for max delay enforcement
        if key not in self._first_call_times:
            self._first_call_times[key] = now
            
            # Execute immediately if configured
            if self.config.immediate:
                result = await self._execute_func(func, *args, **kwargs)
                del self._first_call_times[key]
                return result
        
        # Check if max delay has been reached
        time_since_first = now - self._first_call_times[key]
        if time_since_first >= self.config.max_delay:
            result = await self._execute_func(func, *args, **kwargs)
            del self._first_call_times[key]
            return result
        
        # Create new debounced task
        async def delayed_execution() -> Any:
            await asyncio.sleep(self.config.delay)
            try:
                result = await self._execute_func(func, *args, **kwargs)
                if key in self._first_call_times:
                    del self._first_call_times[key]
                if key in self._pending_tasks:
                    del self._pending_tasks[key]
                return result
            except asyncio.CancelledError:
                # Task was cancelled, clean up
                if key in self._first_call_times:
                    del self._first_call_times[key]
                if key in self._pending_tasks:
                    del self._pending_tasks[key]
                raise
        
        task = asyncio.create_task(delayed_execution())
        self._pending_tasks[key] = task
        
        try:
            return await task
        except asyncio.CancelledError:
            # Task was cancelled by a newer call
            return None
    
    async def _execute_func(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    def cancel_all(self) -> None:
        """Cancel all pending debounced operations."""
        for task in self._pending_tasks.values():
            task.cancel()
        self._pending_tasks.clear()
        self._first_call_times.clear()


class ConnectionPool:
    """Manages WebSocket connections efficiently."""
    
    def __init__(self, max_connections_per_session: int = 10):
        self.max_connections_per_session = max_connections_per_session
        self.session_connections: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_connections_per_session))
        self.connection_metadata: Dict[Any, Dict[str, Any]] = {}
    
    def add_connection(self, session_id: str, connection: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add connection to pool.
        
        Args:
            session_id: Session identifier
            connection: WebSocket connection
            metadata: Optional connection metadata
            
        Returns:
            True if connection was added, False if pool is full
        """
        connections = self.session_connections[session_id]
        
        # Remove oldest connection if at capacity
        if len(connections) >= self.max_connections_per_session:
            oldest = connections.popleft()
            if oldest in self.connection_metadata:
                del self.connection_metadata[oldest]
        
        connections.append(connection)
        if metadata:
            self.connection_metadata[connection] = metadata
        
        return True
    
    def remove_connection(self, session_id: str, connection: Any) -> bool:
        """
        Remove connection from pool.
        
        Args:
            session_id: Session identifier
            connection: WebSocket connection
            
        Returns:
            True if connection was removed, False if not found
        """
        connections = self.session_connections[session_id]
        try:
            connections.remove(connection)
            if connection in self.connection_metadata:
                del self.connection_metadata[connection]
            
            # Clean up empty session
            if not connections:
                del self.session_connections[session_id]
            
            return True
        except ValueError:
            return False
    
    def get_connections(self, session_id: str) -> list:
        """Get all connections for a session."""
        return list(self.session_connections.get(session_id, []))
    
    def get_connection_count(self, session_id: str) -> int:
        """Get connection count for a session."""
        return len(self.session_connections.get(session_id, []))
    
    def get_total_connections(self) -> int:
        """Get total number of connections across all sessions."""
        return sum(len(connections) for connections in self.session_connections.values())


class PerformanceMonitor:
    """Monitors performance metrics for the interactive module."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.operation_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
    
    def record_operation(self, operation: str, duration: float) -> None:
        """Record operation timing."""
        self.operation_times[operation].append(duration)
        self.operation_counts[operation] += 1
    
    def record_error(self, operation: str) -> None:
        """Record operation error."""
        self.error_counts[operation] += 1
    
    def get_average_time(self, operation: str) -> float:
        """Get average operation time."""
        times = self.operation_times[operation]
        return sum(times) / len(times) if times else 0.0
    
    def get_operation_stats(self, operation: str) -> Dict[str, Union[float, int]]:
        """Get comprehensive stats for an operation."""
        times = self.operation_times[operation]
        if not times:
            return {
                "count": 0,
                "errors": self.error_counts[operation],
                "avg_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0
            }
        
        return {
            "count": self.operation_counts[operation],
            "errors": self.error_counts[operation],
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Union[float, int]]]:
        """Get stats for all operations."""
        all_operations = set(self.operation_times.keys()) | set(self.error_counts.keys())
        return {op: self.get_operation_stats(op) for op in all_operations}


def performance_monitor(operation_name: str, monitor: PerformanceMonitor) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to monitor function performance."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_operation(operation_name, duration)
                return result
            except Exception as e:
                monitor.record_error(operation_name)
                raise
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_operation(operation_name, duration)
                return result
            except Exception as e:
                monitor.record_error(operation_name)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class ResourceManager:
    """Manages system resources and cleanup."""
    
    def __init__(self) -> None:
        self.cleanup_tasks: list[Callable] = []
        self.resource_limits = {
            "max_sessions": 1000,
            "max_elements_per_session": 500,
            "max_connections_per_session": 10,
            "session_timeout": 3600  # 1 hour
        }
    
    def register_cleanup(self, cleanup_func: Callable) -> None:
        """Register a cleanup function."""
        self.cleanup_tasks.append(cleanup_func)
    
    async def cleanup_all(self) -> None:
        """Execute all cleanup tasks."""
        for cleanup_func in self.cleanup_tasks:
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()
            except Exception as e:
                # Log error but continue cleanup
                print(f"Error during cleanup: {e}")
    
    def check_resource_limits(self, resource: str, current_value: int) -> bool:
        """Check if resource usage is within limits."""
        limit = self.resource_limits.get(resource)
        return limit is None or current_value < limit
    
    def set_resource_limit(self, resource: str, limit: int) -> None:
        """Set resource limit."""
        self.resource_limits[resource] = limit


# Global instances
default_debouncer = Debouncer(DebounceConfig())
default_connection_pool = ConnectionPool()
default_performance_monitor = PerformanceMonitor()
default_resource_manager = ResourceManager()
