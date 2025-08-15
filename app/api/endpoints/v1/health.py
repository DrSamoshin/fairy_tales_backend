import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import response
from app.schemas.response import BaseResponse
from app.services.database_health import db_health_service
from app.services.openai_health import openai_health_service
from app.middleware.database_monitoring import db_monitoring_service
from app.db.db_sessions import get_users_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=BaseResponse)
async def comprehensive_health_check(db: Session = Depends(get_users_db)):
    """Comprehensive health check for all services"""
    logging.info("Performing comprehensive health check")
    
    health_results = {
        "overall_status": "healthy",
        "timestamp": __import__('time').time(),
        "services": {}
    }
    
    # Check application
    health_results["services"]["application"] = {
        "status": "healthy",
        "message": "Application is running"
    }
    
    # Check database
    try:
        db_health = db_health_service.check_basic_connectivity(db)
        health_results["services"]["database"] = db_health
    except Exception as e:
        health_results["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check OpenAI
    try:
        openai_healthy = await openai_health_service.quick_check()
        health_results["services"]["openai"] = {
            "status": "healthy" if openai_healthy else "unhealthy",
            "check_type": "quick"
        }
    except Exception as e:
        health_results["services"]["openai"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Determine overall status
    unhealthy_services = [
        service for service, details in health_results["services"].items()
        if details.get("status") != "healthy"
    ]
    
    if unhealthy_services:
        health_results["overall_status"] = "unhealthy"
        health_results["unhealthy_services"] = unhealthy_services
    
    # Set response
    status_code = 200 if health_results["overall_status"] == "healthy" else 503
    success = health_results["overall_status"] == "healthy"
    
    return response(
        message=f"System status: {health_results['overall_status']}",
        status_code=status_code,
        success=success,
        data=health_results
    )


@router.get("/app/", response_model=BaseResponse)
async def get_health_check():
    """Basic application health check"""
    msg = "Application is running"
    logging.info(msg)
    return response(
        message=msg,
        data={"status": "healthy", "service": "fairy_tales_backend"}
    )


@router.get("/db/", response_model=BaseResponse)
def database_health_check(db: Session = Depends(get_users_db)):
    """Basic database connectivity check"""
    health_result = db_health_service.check_basic_connectivity(db)
    
    if health_result["status"] == "healthy":
        return response(
            message="Database is healthy",
            data=health_result
        )
    else:
        return response(
            message="Database health check failed",
            status_code=503,
            success=False,
            data=health_result
        )


@router.get("/db/comprehensive/", response_model=BaseResponse)
def comprehensive_database_health_check():
    """Comprehensive database health check including performance tests"""
    health_result = db_health_service.comprehensive_health_check()
    
    status_code_map = {
        "healthy": 200,
        "warning": 200,
        "degraded": 200,
        "slow": 200,
        "unhealthy": 503
    }
    
    status_code = status_code_map.get(health_result["overall_status"], 503)
    success = health_result["overall_status"] not in ["unhealthy"]
    
    return response(
        message=f"Database status: {health_result['overall_status']}",
        status_code=status_code,
        success=success,
        data=health_result
    )


@router.get("/db/pool/", response_model=BaseResponse)
def connection_pool_status():
    """Check database connection pool status"""
    pool_status = db_health_service.check_connection_pool_status()
    
    if pool_status["status"] == "healthy":
        return response(
            message="Connection pool is healthy",
            data=pool_status
        )
    else:
        return response(
            message="Connection pool issues detected",
            status_code=503,
            success=False,
            data=pool_status
        )


@router.get("/db/metrics/", response_model=BaseResponse)
def database_performance_metrics():
    """Get database performance metrics and monitoring data"""
    metrics = db_monitoring_service.get_performance_metrics()
    
    return response(
        message="Database performance metrics retrieved",
        data=metrics
    )


@router.get("/db/queries/", response_model=BaseResponse)
def database_query_statistics():
    """Get detailed database query statistics"""
    stats = db_monitoring_service.get_query_statistics()
    
    return response(
        message="Database query statistics retrieved",
        data=stats
    )


@router.get("/openai/", response_model=BaseResponse)
async def openai_health_check():
    """Comprehensive OpenAI API health check"""
    logging.info("Performing OpenAI health check")
    
    try:
        health_result = await openai_health_service.check_health()
        
        status_code = 200 if health_result["status"] == "healthy" else 503
        success = health_result["status"] == "healthy"
        
        return response(
            message=f"OpenAI API status: {health_result['status']}",
            status_code=status_code,
            success=success,
            data=health_result
        )
    
    except Exception as e:
        logging.error(f"OpenAI health check failed: {e}")
        return response(
            message="OpenAI health check failed",
            status_code=503,
            success=False,
            data={
                "service": "openai",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": __import__('time').time()
            }
        )


@router.get("/openai/quick/", response_model=BaseResponse)
async def openai_quick_check():
    """Quick OpenAI API connectivity check"""
    logging.info("Performing quick OpenAI check")
    
    try:
        is_healthy = await openai_health_service.quick_check()
        
        if is_healthy:
            return response(
                message="OpenAI API is responsive",
                data={
                    "service": "openai",
                    "status": "healthy",
                    "check_type": "quick",
                    "timestamp": __import__('time').time()
                }
            )
        else:
            return response(
                message="OpenAI API is not responsive",
                status_code=503,
                success=False,
                data={
                    "service": "openai",
                    "status": "unhealthy",
                    "check_type": "quick",
                    "timestamp": __import__('time').time()
                }
            )
    
    except Exception as e:
        logging.error(f"Quick OpenAI check failed: {e}")
        return response(
            message="Quick OpenAI check failed",
            status_code=503,
            success=False,
            data={
                "service": "openai",
                "status": "error",
                "error": str(e),
                "timestamp": __import__('time').time()
            }
        )
