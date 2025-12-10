from fastapi import APIRouter
import logging

from app.services.rate_limiter import rate_limiter
from app.services.circuit_breaker import circuit_breaker
from app.services.memory_guard import memory_guard

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """
    Health check endpoint with full monitoring data
    """
    # Get all circuit breaker statuses
    circuit_breakers_list = []
    # Iterate through all tracked job_ids in failures dict
    for job_id in circuit_breaker.failures.keys():
        status = circuit_breaker.get_status(job_id)
        circuit_breakers_list.append(status)
    
    return {
        "status": "healthy",
        "service": "AI Anabasis SEO Spider",
        "rate_limiter": rate_limiter.get_metrics(),
        "circuit_breakers": circuit_breakers_list,
        "memory_limits": {
            "max_extracted_size_mb": memory_guard.MAX_EXTRACTED_SIZE_BYTES / (1024 * 1024),
            "current_jobs": []  # TODO: Track active jobs if needed
        }
    }


@router.get("/rate-limiter")
async def get_rate_limiter_metrics():
    """
    Get Gemini rate limiter metrics
    """
    return rate_limiter.get_metrics()


@router.get("/circuit-breaker/{job_id}")
async def get_circuit_breaker_status(job_id: str):
    """
    Get circuit breaker status for a job
    """
    return circuit_breaker.get_status(job_id)


@router.post("/circuit-breaker/{job_id}/reset")
async def reset_circuit_breaker(job_id: str):
    """
    Reset circuit breaker for a job (admin only)
    """
    circuit_breaker.reset(job_id)
    return {
        "job_id": job_id,
        "status": "reset",
        "message": "Circuit breaker reset successfully"
    }


@router.get("/memory-limits")
async def get_memory_limits():
    """
    Get memory guard configuration
    """
    return {
        "max_extracted_size_bytes": memory_guard.MAX_EXTRACTED_SIZE_BYTES,
        "max_extracted_size_mb": memory_guard.MAX_EXTRACTED_SIZE_BYTES / (1024 * 1024),
        "format_example": memory_guard.format_size(memory_guard.MAX_EXTRACTED_SIZE_BYTES)
    }

