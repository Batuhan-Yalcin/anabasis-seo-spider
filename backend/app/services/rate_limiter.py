import asyncio
from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)


class GeminiRateLimiter:
    """
    Async rate limiter for Gemini API calls
    
    Rules:
    - Max 3 concurrent requests
    - Implements backpressure (queue waits if limit reached)
    - Tracks metrics for monitoring
    """
    
    MAX_CONCURRENT_REQUESTS = 3
    
    def __init__(self):
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self.active_requests = 0
        self.total_requests = 0
        self.total_wait_time = 0.0
        self.queue_size = 0
        
        logger.info(
            f"GeminiRateLimiter initialized: "
            f"max_concurrent={self.MAX_CONCURRENT_REQUESTS}"
        )
    
    async def acquire(self) -> None:
        """
        Acquire slot for Gemini request
        
        Blocks if max concurrent requests reached (backpressure)
        """
        start_time = time.time()
        self.queue_size += 1
        
        logger.debug(
            f"Acquiring rate limiter slot... "
            f"(active={self.active_requests}, queue={self.queue_size})"
        )
        
        await self.semaphore.acquire()
        
        wait_time = time.time() - start_time
        self.total_wait_time += wait_time
        self.queue_size -= 1
        self.active_requests += 1
        self.total_requests += 1
        
        if wait_time > 0.1:
            logger.warning(
                f"⏱️ Backpressure: waited {wait_time:.2f}s for rate limiter slot"
            )
        
        logger.debug(
            f"✅ Rate limiter slot acquired (active={self.active_requests})"
        )
    
    def release(self) -> None:
        """Release slot after Gemini request completes"""
        self.active_requests -= 1
        self.semaphore.release()
        
        logger.debug(
            f"Released rate limiter slot (active={self.active_requests})"
        )
    
    async def __aenter__(self):
        """Context manager support"""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.release()
    
    def get_metrics(self) -> dict:
        """Get rate limiter metrics for monitoring"""
        avg_wait_time = (
            self.total_wait_time / self.total_requests
            if self.total_requests > 0
            else 0.0
        )
        
        return {
            "max_concurrent": self.MAX_CONCURRENT_REQUESTS,
            "active_requests": self.active_requests,
            "queue_size": self.queue_size,
            "total_requests": self.total_requests,
            "total_wait_time_seconds": round(self.total_wait_time, 2),
            "average_wait_time_seconds": round(avg_wait_time, 3),
            "utilization_percent": round(
                (self.active_requests / self.MAX_CONCURRENT_REQUESTS) * 100, 1
            )
        }
    
    def reset_metrics(self):
        """Reset metrics (for testing/debugging)"""
        self.total_requests = 0
        self.total_wait_time = 0.0
        logger.info("Rate limiter metrics reset")


# Singleton instance
rate_limiter = GeminiRateLimiter()
