import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from app.db.db_sessions import get_users_db, _get_users_db_engine
from app.db.models.user import User
from app.db.models.story import Story


class DatabaseHealthService:
    """Service for comprehensive database health monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_basic_connectivity(self, db: Session) -> Dict[str, Any]:
        """Basic database connectivity check"""
        try:
            start_time = time.time()
            result = db.execute(text("SELECT 1")).scalar()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "status": "healthy" if result == 1 else "unhealthy",
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": "Database connection successful"
            }
        except Exception as e:
            self.logger.error(f"Database connectivity check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": f"Connection failed: {str(e)}"
            }
    
    def check_connection_pool_status(self) -> Dict[str, Any]:
        """Check connection pool health"""
        try:
            engine = _get_users_db_engine()
            pool = engine.pool
            
            return {
                "status": "healthy",
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "max_overflow": engine.pool._max_overflow,
                "pool_usage_percent": round((pool.checkedout() / (pool.size() + pool.overflow())) * 100, 2) if (pool.size() + pool.overflow()) > 0 else 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Connection pool check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "details": f"Pool check failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def check_table_accessibility(self, db: Session) -> Dict[str, Any]:
        """Check if main tables are accessible"""
        tables_status = {}
        overall_status = "healthy"
        
        # Test main tables
        test_queries = {
            "users": "SELECT COUNT(*) FROM users LIMIT 1",
            "stories": "SELECT COUNT(*) FROM stories LIMIT 1"
        }
        
        for table_name, query in test_queries.items():
            try:
                start_time = time.time()
                count = db.execute(text(query)).scalar()
                response_time = (time.time() - start_time) * 1000
                
                tables_status[table_name] = {
                    "status": "healthy",
                    "record_count": count,
                    "response_time_ms": round(response_time, 2)
                }
            except Exception as e:
                self.logger.error(f"Table {table_name} check failed: {str(e)}")
                tables_status[table_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "tables": tables_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def check_query_performance(self, db: Session) -> Dict[str, Any]:
        """Test common query performance"""
        performance_tests = {}
        
        test_queries = {
            "user_lookup": {
                "description": "User lookup by email",
                "query": lambda: db.query(User).filter(User.email.isnot(None)).first(),
                "threshold_ms": 100
            },
            "story_count": {
                "description": "Count active stories",
                "query": lambda: db.query(func.count(Story.id)).filter(Story.is_deleted == False).scalar(),
                "threshold_ms": 200
            },
            "recent_stories": {
                "description": "Recent stories with user",
                "query": lambda: db.query(Story).filter(Story.is_deleted == False).order_by(Story.created_at.desc()).limit(5).all(),
                "threshold_ms": 150
            }
        }
        
        overall_status = "healthy"
        
        for test_name, test_config in test_queries.items():
            try:
                start_time = time.time()
                result = test_config["query"]()
                response_time = (time.time() - start_time) * 1000
                
                status = "healthy" if response_time <= test_config["threshold_ms"] else "slow"
                if status == "slow":
                    overall_status = "degraded"
                
                performance_tests[test_name] = {
                    "status": status,
                    "description": test_config["description"],
                    "response_time_ms": round(response_time, 2),
                    "threshold_ms": test_config["threshold_ms"],
                    "result_count": len(result) if isinstance(result, list) else (1 if result else 0)
                }
            except Exception as e:
                self.logger.error(f"Performance test {test_name} failed: {str(e)}")
                performance_tests[test_name] = {
                    "status": "unhealthy",
                    "description": test_config["description"],
                    "error": str(e)
                }
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "tests": performance_tests,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def check_database_locks(self, db: Session) -> Dict[str, Any]:
        """Check for database locks (PostgreSQL specific)"""
        try:
            lock_query = text("""
                SELECT 
                    blocked_locks.pid AS blocked_pid,
                    blocked_activity.usename AS blocked_user,
                    blocking_locks.pid AS blocking_pid,
                    blocking_activity.usename AS blocking_user,
                    blocked_activity.query AS blocked_statement,
                    blocking_activity.query AS current_statement_in_blocking_process
                FROM pg_catalog.pg_locks blocked_locks
                JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
                JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
                    AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
                    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                    AND blocking_locks.pid != blocked_locks.pid
                JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
                WHERE NOT blocked_locks.GRANTED;
            """)
            
            locks = db.execute(lock_query).fetchall()
            
            return {
                "status": "healthy" if len(locks) == 0 else "warning",
                "blocked_queries_count": len(locks),
                "locks": [dict(lock._mapping) for lock in locks] if locks else [],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            # If we can't check locks (maybe not PostgreSQL), just return unknown
            return {
                "status": "unknown",
                "details": f"Lock check not available: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks and provide comprehensive status"""
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {}
        }
        
        try:
            # Get database session for testing
            db_gen = get_users_db()
            db = next(db_gen)
            
            try:
                # Run all health checks
                health_status["checks"]["connectivity"] = self.check_basic_connectivity(db)
                health_status["checks"]["connection_pool"] = self.check_connection_pool_status()
                health_status["checks"]["table_accessibility"] = self.check_table_accessibility(db)
                health_status["checks"]["query_performance"] = self.check_query_performance(db)
                health_status["checks"]["database_locks"] = self.check_database_locks(db)
                
                # Determine overall status
                statuses = []
                for check_name, check_result in health_status["checks"].items():
                    statuses.append(check_result.get("status", "unknown"))
                
                if "unhealthy" in statuses:
                    health_status["overall_status"] = "unhealthy"
                elif "degraded" in statuses or "slow" in statuses:
                    health_status["overall_status"] = "degraded"
                elif "warning" in statuses:
                    health_status["overall_status"] = "warning"
                else:
                    health_status["overall_status"] = "healthy"
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"Comprehensive health check failed: {str(e)}")
            health_status["overall_status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status


# Create service instance
db_health_service = DatabaseHealthService()
