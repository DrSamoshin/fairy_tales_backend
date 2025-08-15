import logging
import time
from typing import Callable
from collections import defaultdict, deque
from datetime import datetime, timezone
from threading import Lock

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.db_sessions import _get_users_db_engine


class DatabaseMetrics:
    """Thread-safe database metrics collector"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.lock = Lock()
        
        # Metrics storage
        self.query_times = deque(maxlen=max_history)
        self.query_counts = defaultdict(int)
        self.slow_queries = deque(maxlen=100)  # Keep last 100 slow queries
        self.error_counts = defaultdict(int)
        
        # Thresholds
        self.slow_query_threshold = 1000  # ms
        
        self.logger = logging.getLogger(__name__)
    
    def record_query(self, query_time_ms: float, endpoint: str, method: str, status_code: int):
        """Record a database query execution"""
        with self.lock:
            timestamp = datetime.now(timezone.utc)
            
            # Record query time
            self.query_times.append({
                'time_ms': query_time_ms,
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'timestamp': timestamp
            })
            
            # Count queries per endpoint
            self.query_counts[f"{method} {endpoint}"] += 1
            
            # Track slow queries
            if query_time_ms > self.slow_query_threshold:
                self.slow_queries.append({
                    'time_ms': query_time_ms,
                    'endpoint': endpoint,
                    'method': method,
                    'timestamp': timestamp
                })
                self.logger.warning(f"Slow query detected: {query_time_ms:.2f}ms on {method} {endpoint}")
            
            # Count errors
            if status_code >= 500:
                self.error_counts[f"{method} {endpoint}"] += 1
    
    def get_metrics(self) -> dict:
        """Get current database metrics"""
        with self.lock:
            if not self.query_times:
                return {
                    "total_queries": 0,
                    "average_response_time_ms": 0,
                    "slow_queries_count": 0,
                    "error_rate": 0
                }
            
            # Calculate metrics
            total_queries = len(self.query_times)
            total_time = sum(q['time_ms'] for q in self.query_times)
            avg_time = total_time / total_queries if total_queries > 0 else 0
            
            slow_queries_count = len([q for q in self.query_times if q['time_ms'] > self.slow_query_threshold])
            error_count = sum(self.error_counts.values())
            error_rate = (error_count / total_queries) * 100 if total_queries > 0 else 0
            
            # Recent performance (last 100 queries)
            recent_queries = list(self.query_times)[-100:]
            recent_avg = sum(q['time_ms'] for q in recent_queries) / len(recent_queries) if recent_queries else 0
            
            return {
                "total_queries": total_queries,
                "average_response_time_ms": round(avg_time, 2),
                "recent_average_response_time_ms": round(recent_avg, 2),
                "slow_queries_count": slow_queries_count,
                "slow_query_threshold_ms": self.slow_query_threshold,
                "error_rate_percent": round(error_rate, 2),
                "query_counts_by_endpoint": dict(self.query_counts),
                "recent_slow_queries": list(self.slow_queries)[-10:],  # Last 10 slow queries
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_connection_pool_metrics(self) -> dict:
        """Get connection pool metrics"""
        try:
            engine = _get_users_db_engine()
            pool = engine.pool
            
            total_connections = pool.size() + pool.overflow()
            used_connections = pool.checkedout()
            usage_percent = (used_connections / total_connections * 100) if total_connections > 0 else 0
            
            return {
                "pool_size": pool.size(),
                "max_overflow": engine.pool._max_overflow,
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "total_connections": total_connections,
                "usage_percent": round(usage_percent, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get connection pool metrics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Global metrics instance
db_metrics = DatabaseMetrics()


class DatabaseMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor database performance for API requests"""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/health/app"]
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip monitoring for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Skip if not a database-related endpoint
        if not self._is_database_endpoint(request.url.path):
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            db_metrics.record_query(
                query_time_ms=response_time_ms,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code
            )
            
            # Add performance headers
            response.headers["X-DB-Response-Time"] = f"{response_time_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            # Record error
            response_time_ms = (time.time() - start_time) * 1000
            db_metrics.record_query(
                query_time_ms=response_time_ms,
                endpoint=request.url.path,
                method=request.method,
                status_code=500
            )
            
            self.logger.error(f"Database error on {request.method} {request.url.path}: {str(e)}")
            raise
    
    def _is_database_endpoint(self, path: str) -> bool:
        """Check if the endpoint likely uses database"""
        database_endpoints = [
            "/api/v1/auth",
            "/api/v1/user",
            "/api/v1/stories",
            "/api/v1/admin",
            "/api/v1/health/db"
        ]
        
        return any(path.startswith(endpoint) for endpoint in database_endpoints)


# Service for exposing metrics
class DatabaseMonitoringService:
    """Service to expose database monitoring metrics"""
    
    def get_performance_metrics(self) -> dict:
        """Get comprehensive database performance metrics"""
        return {
            "query_metrics": db_metrics.get_metrics(),
            "connection_pool": db_metrics.get_connection_pool_metrics(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_query_statistics(self) -> dict:
        """Get detailed query statistics"""
        metrics = db_metrics.get_metrics()
        
        return {
            "summary": {
                "total_queries": metrics["total_queries"],
                "average_response_time_ms": metrics["average_response_time_ms"],
                "recent_average_response_time_ms": metrics["recent_average_response_time_ms"],
                "slow_queries_count": metrics["slow_queries_count"],
                "error_rate_percent": metrics["error_rate_percent"]
            },
            "by_endpoint": metrics["query_counts_by_endpoint"],
            "slow_queries": metrics["recent_slow_queries"],
            "threshold_ms": metrics["slow_query_threshold_ms"],
            "timestamp": metrics["timestamp"]
        }


# Service instance
db_monitoring_service = DatabaseMonitoringService()
