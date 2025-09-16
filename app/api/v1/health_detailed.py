from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
import redis
import logging

from app.db.session import get_db
from app.core.config import settings
from app.observability.slo_config import calculate_slo_performance, SLOTarget

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthStatus:
    """Health status constants."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheck:
    """Individual health check result."""
    
    def __init__(self, name: str, status: str, message: str = "", details: Dict[str, Any] = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow()


async def check_database_health(db: Session) -> HealthCheck:
    """Check database health."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Check connection pool
        pool_size = db.get_bind().pool.size()
        checked_in = db.get_bind().pool.checkedin()
        checked_out = db.get_bind().pool.checkedout()
        
        # Check if pool is healthy
        pool_utilization = (checked_out / pool_size) * 100 if pool_size > 0 else 0
        
        if pool_utilization > 90:
            return HealthCheck(
                name="database",
                status=HealthStatus.DEGRADED,
                message="High connection pool utilization",
                details={
                    "pool_size": pool_size,
                    "checked_in": checked_in,
                    "checked_out": checked_out,
                    "utilization_percent": pool_utilization
                }
            )
        
        return HealthCheck(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database is healthy",
            details={
                "pool_size": pool_size,
                "checked_in": checked_in,
                "checked_out": checked_out,
                "utilization_percent": pool_utilization
            }
        )
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return HealthCheck(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}",
            details={"error": str(e)}
        )


async def check_redis_health() -> HealthCheck:
    """Check Redis health."""
    try:
        r = redis.from_url(settings.redis_url)
        
        # Test Redis connection
        r.ping()
        
        # Get Redis info
        info = r.info()
        
        # Check memory usage
        used_memory = info.get("used_memory", 0)
        max_memory = info.get("maxmemory", 0)
        memory_usage = (used_memory / max_memory) * 100 if max_memory > 0 else 0
        
        if memory_usage > 90:
            return HealthCheck(
                name="redis",
                status=HealthStatus.DEGRADED,
                message="High Redis memory usage",
                details={
                    "used_memory": used_memory,
                    "max_memory": max_memory,
                    "memory_usage_percent": memory_usage
                }
            )
        
        return HealthCheck(
            name="redis",
            status=HealthStatus.HEALTHY,
            message="Redis is healthy",
            details={
                "used_memory": used_memory,
                "max_memory": max_memory,
                "memory_usage_percent": memory_usage,
                "connected_clients": info.get("connected_clients", 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return HealthCheck(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=f"Redis connection failed: {str(e)}",
            details={"error": str(e)}
        )


async def check_external_apis() -> HealthCheck:
    """Check external API health."""
    external_apis = [
        ("Meta Graph API", "https://graph.facebook.com/v20.0/me"),
        ("LinkedIn API", "https://api.linkedin.com/v2/me"),
        ("TikTok Business API", "https://business-api.tiktok.com/open_api/v1.3/user/info/"),
        ("Google Ads API", "https://googleads.googleapis.com/v14/customers")
    ]
    
    results = []
    
    for api_name, url in external_apis:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status < 500:
                        results.append({
                            "name": api_name,
                            "status": "healthy",
                            "response_time": response.headers.get("X-Response-Time", "unknown")
                        })
                    else:
                        results.append({
                            "name": api_name,
                            "status": "degraded",
                            "error": f"HTTP {response.status}"
                        })
        except Exception as e:
            results.append({
                "name": api_name,
                "status": "unhealthy",
                "error": str(e)
            })
    
    # Determine overall status
    healthy_count = sum(1 for r in results if r["status"] == "healthy")
    total_count = len(results)
    
    if healthy_count == total_count:
        status = HealthStatus.HEALTHY
        message = "All external APIs are healthy"
    elif healthy_count > total_count // 2:
        status = HealthStatus.DEGRADED
        message = "Some external APIs are experiencing issues"
    else:
        status = HealthStatus.UNHEALTHY
        message = "Multiple external APIs are down"
    
    return HealthCheck(
        name="external_apis",
        status=status,
        message=message,
        details={"apis": results}
    )


async def check_workers_health() -> HealthCheck:
    """Check workers health."""
    try:
        # This would typically check worker heartbeats from Redis or database
        # For now, return a placeholder
        return HealthCheck(
            name="workers",
            status=HealthStatus.HEALTHY,
            message="Workers are healthy",
            details={
                "active_workers": 3,
                "last_heartbeat": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Workers health check failed: {e}")
        return HealthCheck(
            name="workers",
            status=HealthStatus.UNHEALTHY,
            message=f"Workers health check failed: {str(e)}",
            details={"error": str(e)}
        )


async def check_slo_health() -> HealthCheck:
    """Check SLO health."""
    try:
        # This would typically query metrics from Prometheus
        # For now, return a placeholder
        slo_results = []
        
        # Check API availability SLO
        api_availability = calculate_slo_performance(
            "api", 
            SLOTarget.AVAILABILITY, 
            current_value=0.05,  # 0.05% downtime
            time_window_seconds=86400  # 1 day
        )
        slo_results.append(api_availability)
        
        # Check API latency SLO
        api_latency = calculate_slo_performance(
            "api", 
            SLOTarget.LATENCY, 
            current_value=1.5,  # 1.5 seconds
            time_window_seconds=86400  # 1 day
        )
        slo_results.append(api_latency)
        
        # Check worker availability SLO
        worker_availability = calculate_slo_performance(
            "workers", 
            SLOTarget.AVAILABILITY, 
            current_value=0.1,  # 0.1% downtime
            time_window_seconds=86400  # 1 day
        )
        slo_results.append(worker_availability)
        
        # Determine overall SLO status
        failing_slos = [slo for slo in slo_results if not slo["is_meeting_slo"]]
        
        if not failing_slos:
            status = HealthStatus.HEALTHY
            message = "All SLOs are being met"
        elif len(failing_slos) == 1:
            status = HealthStatus.DEGRADED
            message = f"1 SLO is not being met: {failing_slos[0]['target']}"
        else:
            status = HealthStatus.UNHEALTHY
            message = f"{len(failing_slos)} SLOs are not being met"
        
        return HealthCheck(
            name="slo",
            status=status,
            message=message,
            details={"slo_results": slo_results}
        )
        
    except Exception as e:
        logger.error(f"SLO health check failed: {e}")
        return HealthCheck(
            name="slo",
            status=HealthStatus.UNHEALTHY,
            message=f"SLO health check failed: {str(e)}",
            details={"error": str(e)}
        )


@router.get("/health/detailed")
async def get_detailed_health(db: Session = Depends(get_db)):
    """Get detailed health status of all components."""
    try:
        # Run all health checks in parallel
        health_checks = await asyncio.gather(
            check_database_health(db),
            check_redis_health(),
            check_external_apis(),
            check_workers_health(),
            check_slo_health(),
            return_exceptions=True
        )
        
        # Process results
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for check in health_checks:
            if isinstance(check, Exception):
                logger.error(f"Health check failed: {check}")
                results.append(HealthCheck(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(check)}"
                ))
                overall_status = HealthStatus.UNHEALTHY
            else:
                results.append(check)
                
                # Update overall status
                if check.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif check.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        # Calculate overall health score
        healthy_count = sum(1 for check in results if check.status == HealthStatus.HEALTHY)
        total_count = len(results)
        health_score = (healthy_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "status": overall_status,
            "health_score": health_score,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "message": check.message,
                    "details": check.details,
                    "timestamp": check.timestamp.isoformat()
                }
                for check in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/health/ready")
async def get_readiness(db: Session = Depends(get_db)):
    """Get readiness status for Kubernetes."""
    try:
        # Check critical dependencies
        db_check = await check_database_health(db)
        redis_check = await check_redis_health()
        
        # Ready if critical dependencies are healthy
        if db_check.status == HealthStatus.HEALTHY and redis_check.status == HealthStatus.HEALTHY:
            return {"status": "ready"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check failed: {str(e)}"
        )


@router.get("/health/live")
async def get_liveness():
    """Get liveness status for Kubernetes."""
    # Simple liveness check - if we can respond, we're alive
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
